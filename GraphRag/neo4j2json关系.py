from neo4j import GraphDatabase
import json

# 配置 Neo4j 数据库
uri = "neo4j+s://4b4caece.databases.neo4j.io:7687"
user = "neo4j"
password = "uKmBry2hbtVuYriIKM-8Ob-PK86S0nRff9VKCN6KCDk"
driver = GraphDatabase.driver(uri, auth=(user, password))


def fetch_all_relationships():
    """
    从 Neo4j 数据库读取所有节点及其关系，并生成 JSON 格式的图数据。
    """
    nodes_map = {}  # 节点映射：{node_name: node_id}
    nodes_list = []  # 节点列表
    edges_list = []  # 边列表
    node_id = 1  # 分配给每个节点的唯一 ID

    query = """
    MATCH (n)-[r]->(m)
    RETURN n.name AS start_node, type(r) AS relation, m.name AS end_node
    """

    with driver.session() as session:
        results = session.run(query)

        for record in results:
            start_node = record["start_node"]
            end_node = record["end_node"]
            relation = record["relation"]

            # 如果起始节点不在映射中，添加它
            if start_node not in nodes_map:
                nodes_map[start_node] = node_id
                nodes_list.append({
                    "data": node_id,
                    "name": start_node,
                    "position": {"x": 0, "y": 0}
                })
                node_id += 1

            # 如果结束节点不在映射中，添加它
            if end_node not in nodes_map:
                nodes_map[end_node] = node_id
                nodes_list.append({
                    "data": node_id,
                    "name": end_node,
                    "position": {"x": 0, "y": 0}
                })
                node_id += 1

            # 添加边的信息
            edges_list.append({
                "a": nodes_map[start_node],
                "b": nodes_map[end_node],
                "relation": relation
            })

    # 返回最终的图数据结构
    return {
        "nodes": nodes_list,
        "edges": edges_list,
        "nodes_map": nodes_map
    }


def save_to_json_file(data, filename):
    """
    将数据保存到 JSON 文件中。
    """
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"数据已成功保存到 {filename}")


def main():
    # 读取所有关系并保存至 JSON 文件
    graph_data = fetch_all_relationships()
    save_to_json_file(graph_data, "graph_relationships.json")


if __name__ == "__main__":
    main()
