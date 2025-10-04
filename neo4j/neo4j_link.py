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

# 创建一个会话并运行一个查询
with driver.session() as session:

    # 创建一个新的节点
    cypher_command = "CREATE (n:Person {name: 'fufu', age: 18})"
    print(f"新建节点 执行命令{cypher_command}")
    session.run(cypher_command)

    # 创建两个节点并连接它们
    cypher_command = """
        CREATE (a:Person {name: 'Alice'}),
               (b:Person {name: 'Bob'}),
               (a)-[:KNOWS]->(b)
    """
    session.run(cypher_command)

    # 查询节点
    cypher_command = "MATCH (n:Person {name: 'Alice'}) RETURN n"
    result = session.run(cypher_command)
    print("标签：Person 且 name = Alice的有:")
    for record in result:
        print(f"    {record['n']}")
        print(f"    {record['n'].values()}")
        print(f"    {record['n'].keys()}")


    # 执行查询并返回查询结果
    cypher_command = "MATCH (n:Person) RETURN n.name, n.age"
    result = session.run(cypher_command)
    print("标签为Person的有：")
    for record in result:
        print(f"    Name: {record['n.name']}, Age: {record['n.age']}")

# 关闭连接
driver.close()
