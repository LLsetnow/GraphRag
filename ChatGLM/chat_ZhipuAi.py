from zhipuai import ZhipuAI

# 初始化 ZhipuAI 客户端，使用你的 API key
client = ZhipuAI(api_key="8b75816c8a1a05be9cda0a419a489353.W5W94ZKPT2RfdIIO")

# 初始化对话消息列表
messages = []


# 定义一个函数进行对话
def chat_with_chatglm(content, messages):
    # 添加用户输入到消息列表
    messages.append({'role': 'user', 'content': content})

    # 调用 ZhipuAI 接口生成回复
    response = client.chat.completions.create(
        model="glm-4-plus",  # 使用 GLM-4 模型
        messages=messages,
    )

    # 获取模型的回复
    reply = response.choices[0].message.content  # 修改为使用属性访问

    # 将机器人的回复添加到消息列表
    messages.append({'role': 'assistant', 'content': reply})

    # 返回模型的回复
    return reply


# 交互式循环，用户直接输入问题
print("输入你想问的问题，输入 '退出' 以结束对话。")
while True:
    # 获取用户输入
    user_input = input("你: ")

    # 检查是否需要退出
    if user_input.lower() in ['退出', 'exit', 'quit']:
        print("对话结束")
        break

    # 获取chatGLM的回复
    response = chat_with_chatglm(user_input, messages)

    # 输出chatGLM的回复
    print(f"\nchatGLM: {response}\n")
