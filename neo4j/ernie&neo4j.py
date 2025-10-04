import erniebot
import os
os.environ['LANGCHAIN_API_BASE'] = 'http://api.wlai.vip'
from langchain_community.document_loaders import WikipediaLoader
from langchain.text_splitter import TokenTextSplitter
from neo4j import GraphDatabase

# 设置 `erniebot` 的 API 类型和 Access Token
erniebot.api_type = "aistudio"  # 设置为 'aistudio' 或其他类型
erniebot.access_token = "66f2cca42998fba19928022ac4829155eb17b312"  # 用你的 API Token

# 读取维基百科文章
raw_documents = WikipediaLoader(query="Elizabeth I").load()
# with open("wiki.txt", 'w') as f:
#     f.write(raw_documents)

# 定义分块策略
# text_splitter = TokenTextSplitter(chunk_size=512, chunk_overlap=24)
# documents = text_splitter.split_documents(raw_documents[:3])
# print(documents)

# # 创建与 Ernie 交互的函数
# def call_erniebot(texts):
#     responses = []
#     for text in texts:
#         response = erniebot.chat(text)
#         responses.append(response)
#     return responses
#
# # 获取 Ernie 模型转换后的文档内容
# ernie_responses = call_erniebot([doc.page_content for doc in documents])
#
# # 连接到 Neo4j
# uri = "neo4j+s://4b4caece.databases.neo4j.io:7687"
# username = "neo4j"
# password = "uKmBry2hbtVuYriIKM-8Ob-PK86S0nRff9VKCN6KCDk"
# graph = GraphDatabase.driver(uri, auth=(username, password))
#
# # 存储数据到 Neo4j
# def store_to_neo4j(responses):
#     with graph.session() as session:
#         for idx, response in enumerate(responses):
#             session.run("CREATE (n:Document {content: $content})", content=response)
#
# # 将处理后的 Ernie 响应存储到 Neo4j
# store_to_neo4j(ernie_responses)
