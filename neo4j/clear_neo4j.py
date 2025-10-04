from neo4j import GraphDatabase

# 设置连接信息
uri = "neo4j+s://4b4caece.databases.neo4j.io:7687"  # 连接URI
user = "neo4j"  # 用户名
password = "uKmBry2hbtVuYriIKM-8Ob-PK86S0nRff9VKCN6KCDk"  # 密码

# 创建数据库驱动器
driver = GraphDatabase.driver(uri, auth=(user, password))

def clear_all_nodes():
    with driver.session() as session:
        cypher_command = 'MATCH (n) DETACH DELETE n'
        session.run(cypher_command)

clear_all_nodes()
