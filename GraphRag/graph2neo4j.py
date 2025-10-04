import networkx as nx
from neo4j import GraphDatabase

def print_progress(current, total, block_num=50, prefix="进度", suffix="%"):
    """
    打印进度条。
    :param current: 当前完成数量
    :param total: 总数量
    :param block_num: 进度条长度（用多少个█表示）
    :param prefix: 进度条前缀文本
    :param suffix: 进度条后缀文本
    """
    progress = current / total
    completed_blocks = int(progress * block_num)
    bar = "█" * completed_blocks
    percentage = int(progress * 100)
    print(
        f"\r{prefix}{bar:{block_num}} {percentage:3d}{suffix}",
        end=""
    )

# 清除所有节点
def clear_all_nodes():
    with driver.session() as session:
        cypher_command = 'MATCH (n) DETACH DELETE n'
        session.run(cypher_command)
    print('清除所有节点')

# 清除特定条件的节点
def clear_nodes(condition=''):
    with driver.session() as session:
        cypher_command = f'MATCH (n {{{condition}}}) DETACH DELETE n'
        session.run(cypher_command)
    print(f'清除节点为{condition}的所有节点')

def count_nodes(condition=''):
    with driver.session() as session:

        result = session.run(f"MATCH (n {{{condition}}}) RETURN count(n) AS count")
        return result.single()["count"]


# 处理函数：上传节点到 Neo4j
def upload_nodes(tx, nodes, subject='general', id=0):
    index = 0
    for node, attrs in nodes:
        index += 1
        print_progress(index, len(nodes), prefix='上传节点中')
        # 提取需要的属性
        label = attrs.get('label', '未知')  # 默认值为 '未知'
        node_type = attrs.get('type', '').strip() or '其他'  # 处理 type 属性为空的情况
        description = attrs.get('description', '')

        sanitized_node_type = ''.join(
            char if char.isalnum() or char == '_' else '_' for char in node_type
        )
        # 将属性整理成符合 Neo4j 的结构
        props = {
            'name': label,         # 重命名 label 为 name
            'description': description,  # 添加 description 属性
            'subject': subject,          # 科目
            'id': id,                    # 上传批次
        }

        query = f"""
                MERGE (n:`{sanitized_node_type}` {{name: $name}})
                SET n += $props
                """
        # 执行命令
        tx.run(query, name=label, props=props)
    print('\n')
    print(f"上传共{len(nodes)}个节点 至‘{subject}’学科 id={id}")

# 处理函数：上传边到 Neo4j
def upload_edges(tx, edges, degree_map):
    index = 0
    for source, target, attrs in edges:
        index += 1
        print_progress(index, len(edges), prefix='上传关系中')
        # 获取节点的度数以确定关系方向
        source_degree = degree_map[source]
        target_degree = degree_map[target]

        direction = "OUTGOING" if source_degree >= target_degree else "INCOMING"
        description = attrs.get("description", "")
        sanitized_description = ''.join(
            char if char.isalnum() or char == '_' else '_' for char in description
        )

        # 根据方向创建关系
        if direction == "OUTGOING":
            tx.run(
                f"""
                MATCH (a {{name: $source}}), (b {{name: $target}})
                MERGE (a)-[r:{sanitized_description}]->(b)
                """,
                source=source,
                target=target,
                description=description,
            )

        else:
            tx.run(
                f"""
                MATCH (a {{name: $source}}), (b {{name: $target}})
                MERGE (b)-[r:{sanitized_description}]->(a)
                """,
                source=source,
                target=target,
                description=description,
            )


# 主函数：上传 GEXF 数据
def upload_gexf_to_neo4j(graph, subject, id):
    with driver.session() as session:
        # 获取节点和边
        nodes = graph.nodes(data=True)
        edges = graph.edges(data=True)

        # 计算每个节点的度数
        degree_map = {node: graph.degree[node] for node in graph.nodes}

        # 上传节点
        session.write_transaction(upload_nodes, nodes, subject, id)

        # 上传边
        session.write_transaction(upload_edges, edges, degree_map)


# Neo4j 连接信息
uri = "neo4j+s://4b4caece.databases.neo4j.io:7687"
user = "neo4j"
password = "uKmBry2hbtVuYriIKM-8Ob-PK86S0nRff9VKCN6KCDk"

# 创建数据库驱动器
driver = GraphDatabase.driver(uri, auth=(user, password))

# 定义 GEXF 文件路径
gexf_file_path = "graph近代史.gexf"

# 读取 GEXF 文件
graph = nx.read_gexf(gexf_file_path)

clear_all_nodes()                   # 清除所有节点
# clear_nodes("id: 2, subject: '近代史_简'")
# node_num = count_nodes("id: 2, subject: '近代史_简'")
# node_num = count_nodes("")
# print(node_num)
upload_gexf_to_neo4j(graph, '近代史', 2)         # 执行上传
driver.close()                      # 关闭驱动器
