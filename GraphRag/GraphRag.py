# import erniebot
# from neo4j import GraphDatabase
# import json
#
# # ========== ERNIE 配置 ==========
# erniebot.api_type = 'aistudio'
# erniebot.access_token = '66f2cca42998fba19928022ac4829155eb17b312'
# model = 'ernie-4.0-turbo-8k'
#
# # ========== Neo4j 配置 ==========
# uri = "neo4j+s://4b4caece.databases.neo4j.io:7687"
# user = "neo4j"
# password = "uKmBry2hbtVuYriIKM-8Ob-PK86S0nRff9VKCN6KCDk"
#
# # 创建 Neo4j 驱动
# driver = GraphDatabase.driver(uri, auth=(user, password))
#
#
# # ========== 定义功能函数 ==========
# def chat(text, temperature=0.9, top_p=0.9):
#     response = erniebot.ChatCompletion.create(
#         model=model,
#         messages=[{"role": "user", "content": text}],
#         temperature=temperature,
#         top_p=top_p)
#     return response.get_result()
#
# # 从 ERNIE 提取实体
# def extract_entities(content, messages):
#     prompt = (
#         '''
#         从我的问题中识别出所有实体
#         并以列表形式返回
#         示例：
#             张三在北京2020年发生了什么事情？
#             ['张三', '北京', '2020年']
#         '''
#     )
#     # 添加用户输入到对话中
#     messages.append({'role': 'user', 'content': prompt})
#     messages.append({'role': 'user', 'content': content})
#
#     # 调用 ERNIE 模型
#     response = erniebot.ChatCompletion.create(model=model, messages=messages)
#     messages.append(response.to_message())
#
#     # 返回提取的实体
#     result = response.get_result()
#     # 清理中文符号
#     result = result.replace('，', ',').replace('“', '"').replace('”', '"').replace('：', ':').replace('。', '.')
#
#     return eval(result)
#
#
# # 从 Neo4j 检索节点和相邻节点
# # type(r) 返回关系的类型
# # r 返回关系的所有属性
# def query_neo4j(entities, subject):
#     results = []
#     for entity in entities:
#         print(f"查找‘{subject}’学科下的‘{entity}’节点")
#         query = """
#         MATCH (n {subject: $subject, name: $entity})
#         MATCH (n)-[r]-(neighbor)
#         RETURN n, neighbor, type(r) AS relation_description
#         """
#         with driver.session() as session:
#             query_results = [
#                 (record["n"], record["neighbor"], record["relation_description"])
#                 for record in session.run(query, subject=subject, entity=entity)
#             ]
#             # 检查查询结果是否为空
#             if query_results:  # 仅当结果非空时加入列表
#                 results.append(query_results)
#             else:
#                 print(f"未找到‘{entity}’相关的节点或关系，跳过")
#     return results
#
#
# # 结合实体提取和数据库查询
# def process_question(content, messages):
#     # 提取实体
#     entities = extract_entities(content, messages)
#     print(f"所提取的实体为{entities}")
#     if not entities:
#         print("未能从问题中提取出有效实体，请尝试重新提问。")
#
#     # 查询数据库
#     subject = "近代史"  # 固定筛选的 subject
#     results = query_neo4j(entities, subject)
#     if not results:
#         print("未在数据库中找到匹配的节点。")
#
#     return results
#
#
# # ========== 主交互逻辑 ==========
# messages = []  # 初始化对话消息列表
# question = "法国和中国是什么关系"
#
# # 处理用户问题
# results = process_question(question, messages)
# entity_description = ''
# for result in results:
#     print(result[0])
#     node, neighbor, relation_description = result[0]
#     entity_description += node['description']
#
# # 主体描述
# print(f"主体描述为： \n{entity_description}")
# #
# # 使用 ErnieBot 生成最终答案
# Prompt = ("使用以下文段来回答最后的问题。请根据给定的文段生成答案。"
#             "如果你在给定的文段中没有找到任何与问题相关的信息，请用自身知识回答，并且告诉用户该信息不是来自文档。"
#             "保持你的答案丰富且富有表现力。用户最后的问题是：" + question + "。给定的文段是：" + entity_description)
# chatResult = chat(Prompt)
# # 输出结果
# print(f"由ErnieBot润色后的回答为:\n    {chatResult}")


from openai import OpenAI
from neo4j import GraphDatabase

# ========== DeepSeek 配置 ==========
client = OpenAI(
    api_key="your_api_key",
    base_url="https://api.deepseek.com"
)
model = "deepseek-v4-flash"

# ========== Neo4j 配置 ==========
uri = "neo4j+s://7655ff62.databases.neo4j.io"
user = "7655ff62"
password = "jMiQ1jwJT2C_nNjTlymSFQX8snFH6146MsGEyEJV9TA"

# 创建 Neo4j 驱动
driver = GraphDatabase.driver(uri, auth=(user, password))


# ========== 功能函数定义 ==========
def chat(text, temperature=0.9, top_p=0.9):
    """与 DeepSeek 交互生成回答"""
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": text}],
        temperature=temperature,
        top_p=top_p)
    return response.choices[0].message.content


def extract_entities(content, messages):
    """调用 DeepSeek 提取实体"""
    prompt = (
        '''
        从我的问题中识别出所有实体
        并以列表形式返回
        示例：
            张三在北京2020年发生了什么事情？
            ['张三', '北京', '2020年']
        '''
    )
    messages.append({'role': 'user', 'content': prompt})
    messages.append({'role': 'user', 'content': content})

    response = client.chat.completions.create(model=model, messages=messages)
    messages.append({'role': 'assistant', 'content': response.choices[0].message.content})

    result = response.choices[0].message.content
    result = result.replace('，', ',').replace('“', '"').replace('”', '"').replace('：', ':').replace('。', '.')

    return eval(result)


def query_neo4j_single(entity, subject):
    """查询单个实体的内容"""
    query = """
    MATCH (n {subject: $subject, name: $entity})
    MATCH (n)-[r]-(neighbor)
    RETURN n, neighbor, type(r) AS relation_description
    """
    with driver.session() as session:
        query_results = [
            (record["n"], record["neighbor"], record["relation_description"])
            for record in session.run(query, subject=subject, entity=entity)
        ]
    return query_results


def process_question(content, messages, subject):
    """处理问题：提取实体 -> 查询数据库 -> 调用 DeepSeek
    返回: {"entities": [...], "nodes": [...], "description": str, "rag_answer": str}
    """
    entities = extract_entities(content, messages)
    print(f"  → 提取的实体: {entities}")
    if not entities:
        print("  → 未能从问题中提取出有效实体")
        return {"entities": [], "nodes": [], "description": "", "rag_answer": ""}

    # 查询数据库
    results = []
    entity_description = ""
    queried_nodes = []

    for entity in entities:
        print(f"  → 查询图谱: '{entity}'")
        query_results = query_neo4j_single(entity, subject)
        if query_results:
            results.extend(query_results)
            for node, neighbor, rel_desc in query_results:
                entity_description += node.get('description', '')
            # 记录节点信息（去重）
            node_info = {
                "name": query_results[0][0].get('name', entity),
                "type": query_results[0][0].get('type', ''),
                "neighbors": [(r[1].get('name', ''), r[2]) for r in query_results]
            }
            queried_nodes.append(node_info)
        else:
            print(f"  → 未找到 '{entity}' 相关节点，跳过")

    rag_answer = ""
    if results:
        prompt = (
            f"使用以下文段来回答最后的问题。请根据给定的文段生成答案。"
            f"如果你在给定的文段中没有找到任何与问题相关的信息，请用自身知识回答，并且告诉用户该信息不是来自文档。"
            f"保持你的答案丰富且富有表现力。用户最后的问题是：{content}。给定的文段是：{entity_description}"
        )
        rag_answer = chat(prompt)

    return {
        "entities": entities,
        "nodes": queried_nodes,
        "description": entity_description,
        "rag_answer": rag_answer,
    }


def summarize(text, max_len=150):
    """截断长文本，保留首尾"""
    if len(text) <= max_len:
        return text
    half = max_len // 2 - 3
    return text[:half] + " …(中间省略)… " + text[-half:]


def chat_no_rag(question):
    """无 RAG：直接调用 LLM 回答"""
    prompt = f"请回答以下问题：{question}"
    return chat(prompt)


# ========== 主交互逻辑 ==========
if __name__ == "__main__":
    questions = [
        "法国和中国在近代史上是什么关系？",
        "中国共产党在抗日战争中发挥了什么作用？",
        "鸦片战争后中国社会发生了哪些变化？",
        "洋务运动、戊戌变法和辛亥革命之间有什么联系？",
        "五四运动爆发的原因是什么？",
        "孙中山和陈独秀对中国近代化的贡献有什么不同？",
    ]

    subject = "近代史"
    separator = "=" * 70

    for i, question in enumerate(questions, 1):
        messages = []
        print(f"\n{separator}")
        print(f"  示例 {i}")
        print(f"{separator}")

        # 1. 打印提问
        print(f"\n  📝 问题: {question}")

        # 处理 RAG 流程
        result = process_question(question, messages, subject)

        # 2. 打印查询到的节点
        print(f"\n  📊 查询到的节点:")
        if result["nodes"]:
            for node in result["nodes"]:
                print(f"     - [{node['type']}] {node['name']}")
                for neighbor_name, rel in node["neighbors"][:5]:  # 最多显示5个邻居
                    print(f"        ╰──[{rel}]──→ {neighbor_name}")
                if len(node["neighbors"]) > 5:
                    print(f"        ... 还有 {len(node['neighbors']) - 5} 个关系")
        else:
            print(f"     (未匹配到节点)")

        # 3. 打印参考文档（简洁、部分显示）
        print(f"\n  📖 参考文档 (节选):")
        if result["description"]:
            print(f"     {summarize(result['description'], 200)}")
        else:
            print(f"     (无参考文档)")

        # 4. 无 RAG 的回答
        print(f"\n  🤖 无 RAG 回答:")
        no_rag_answer = chat_no_rag(question)
        print(f"     {no_rag_answer}")

        # 5. 有 RAG 的回答
        print(f"\n  🧠 有 RAG (知识图谱增强) 回答:")
        if result["rag_answer"]:
            print(f"     {result['rag_answer']}")
        else:
            print(f"     (无法生成 RAG 回答)")
        print(f"{separator}")
