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


import erniebot
from neo4j import GraphDatabase

# ========== ERNIE 配置 ==========
erniebot.api_type = 'aistudio'
erniebot.access_token = '66f2cca42998fba19928022ac4829155eb17b312'
model = 'ernie-4.0-turbo-8k'

# ========== Neo4j 配置 ==========
uri = "neo4j+s://4b4caece.databases.neo4j.io:7687"
user = "neo4j"
password = "uKmBry2hbtVuYriIKM-8Ob-PK86S0nRff9VKCN6KCDk"

# 创建 Neo4j 驱动
driver = GraphDatabase.driver(uri, auth=(user, password))


# ========== 功能函数定义 ==========
def chat(text, temperature=0.9, top_p=0.9):
    """与 ERNIE 交互生成回答"""
    response = erniebot.ChatCompletion.create(
        model=model,
        messages=[{"role": "user", "content": text}],
        temperature=temperature,
        top_p=top_p)
    return response.get_result()


def extract_entities(content, messages):
    """调用 ERNIE 提取实体"""
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

    response = erniebot.ChatCompletion.create(model=model, messages=messages)
    messages.append(response.to_message())

    result = response.get_result()
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
    """处理问题：提取实体 -> 查询数据库 -> 调用 ERNIE"""
    # 提取实体
    entities = extract_entities(content, messages)
    print(f"所提取的实体为: {entities}")
    if not entities:
        print("未能从问题中提取出有效实体，请尝试重新提问。")
        return ""

    # 查询数据库
    results = []
    entity_description = ""

    for entity in entities:
        print(f"查找‘{subject}’学科下的‘{entity}’节点")
        query_results = query_neo4j_single(entity, subject)
        if query_results:
            results.extend(query_results)
            for result in query_results:
                node, neighbor, relation_description = result
                entity_description += node.get('description', '')  # 累积描述信息
                break
        else:
            print(f"未找到‘{entity}’相关的节点或关系，跳过。")

    if not results:
        print("未在数据库中找到匹配的节点。")
        return ""

    print(f"参考文档为：\n{entity_description}")

    # 使用 ERNIE 生成最终答案
    prompt = (
        f"使用以下文段来回答最后的问题。请根据给定的文段生成答案。"
        f"如果你在给定的文段中没有找到任何与问题相关的信息，请用自身知识回答，并且告诉用户该信息不是来自文档。"
        f"保持你的答案丰富且富有表现力。用户最后的问题是：{content}。给定的文段是：{entity_description}"
    )
    return chat(prompt)


# ========== 主交互逻辑 ==========
if __name__ == "__main__":
    messages = []  # 初始化对话消息列表
    question = "法国和中国是什么关系"
    subject = "近代史"

    # 处理用户问题并获取答案
    answer = process_question(question, messages, subject)
    if answer:
        print(f"由 ErnieBot 生成的回答为:\n{answer}")
