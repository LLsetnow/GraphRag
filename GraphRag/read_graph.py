import networkx as nx

# 读取 .gexf 文件
graph = nx.read_gexf("D:\github\LLM\GraphRag\graph.gexf")

# 打印图的基本信息
print(f"图的基本信息:")
print(f"节点数: {graph.number_of_nodes()}")
print(f"边数: {graph.number_of_edges()}")
print(f"是否为有向图: {graph.is_directed()}")

# 获取所有节点及其属性
print("\n节点及其属性:")
for node, attrs in graph.nodes(data=True):
    print(f"节点: {node}, 属性: {attrs}")

# 获取所有边及其属性
print("\n边及其属性:")
for source, target, attrs in graph.edges(data=True):
    print(f"边: ({source}, {target}), 属性: {attrs}")

# 查看图的全局属性
print("\n图的全局属性:")
print(graph.graph)
