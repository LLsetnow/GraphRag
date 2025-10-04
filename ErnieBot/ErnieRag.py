# 文本生成模型
def chat(text, temperature=0.9, top_p=0.9):
    response = erniebot.ChatCompletion.create(
        model=model,
        messages=[{"role": "user", "content": text}],
        temperature=temperature,
        top_p=top_p)
    return response.get_result()

# 检索问题
question = "为什么中国近代史,是指1840年以来的中国历史"
print(f"提出问题为:\n   {question}\n")
qEmbedding = embedding(question)

search_params = {
    "metric_type": "L2",
    "offset": 0,
    "ignore_growing": False,
    "params": {"nprobe": 10}
}

results = collection.search(
    data=qEmbedding,
    anns_field="answer_vector",
    param=search_params,
    limit=1,
    expr=None,
    output_fields=['answer'],
    consistency_level="Strong"
)

# 获取答案
answer = results[0][0].entity.get('answer')
print(f"从数据库获取的答案为:\n    {answer}\n")

# 使用 ErnieBot 生成最终答案
Prompt = ("使用以下文段来回答最后的问题。请根据给定的文段生成答案。"
            "如果你在给定的文段中没有找到任何与问题相关的信息，请用自身知识回答，并且告诉用户该信息不是来自文档。"
            "保持你的答案丰富且富有表现力。用户最后的问题是：" + question + "。给定的文段是：" + answer)
chatResult = chat(Prompt)

# 输出结果
print(f"由ErnieBot润色后的回答为:\n    {chatResult}")