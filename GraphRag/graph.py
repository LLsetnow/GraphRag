import networkx as nx

# 创建一个无向图
graph = nx.Graph()

# 添加节点
graph.add_nodes_from([1, 2, 3])

# 添加边
graph.add_edges_from([(1, 2), (2, 3)])

# 为节点添加属性
graph.nodes[1]['color'] = 'red'

# 为边添加属性
graph.edges[1, 2]['weight'] = 10

# 查看节点和属性
print(graph.nodes.data())  # 输出所有节点和其属性

# 查看边和属性
print(graph.edges.data())  # 输出所有边和其属性

# 查看节点的邻居
print(list(graph.neighbors(1)))  # 输出 [2]
print(graph.output)

# 查看图的全局属性
graph.graph['name'] = 'ExampleGraph'
print(graph.graph)
