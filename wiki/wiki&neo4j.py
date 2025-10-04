from langchain_community.document_loaders import WikipediaLoader

# 读取维基百科文章
raw_documents = WikipediaLoader(query="Elizabeth I").load()

# 定义分块策略
text_splitter = TokenTextSplitter(chunk_size=512, chunk_overlap=24)

documents = text_splitter.split_documents(raw_documents[:3])

llm = ChatOpenAI(temperature=0, model_name="gpt-4-0125-preview")
llm_transformer = LLMGraphTransformer(llm=llm)
# 提取图数据
graph_documents = llm_transformer.convert_to_graph_documents(documents)
# 存储到 neo4j

graph.add_graph_documents(
    graph_documents,
    baseEntityLabel=True,
    include_source=True
)
