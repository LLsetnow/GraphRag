import erniebot

# 设置ERNIE API的相关参数
erniebot.api_type = 'aistudio'
erniebot.access_token = '66f2cca42998fba19928022ac4829155eb17b312'
model = 'ernie-4.0-turbo-8k'

# 初始化对话消息列表
messages = [{'role': 'user', 'content': "你好"}]


# 定义一个函数进行对话
def chat_with_ernie(content, messages):
    # 添加用户输入到消息列表
    messages.append({'role': 'user', 'content': content})

    # 调用ERNIE接口生成回复
    response = erniebot.ChatCompletion.create(
        model=model,
        messages=messages,
    )

    # 将机器人的回复添加到消息列表
    messages.append(response.to_message())

    # 返回结果
    return response.get_result()


# 交互式循环，用户直接输入问题
print(f"使用文心一言{model}模型进行以下对话\n")
print("输入你想问的问题，输入 '退出' 以结束对话\n")
while True:
    # 获取用户输入
    user_input = input("你: ")

    # 检查是否需要退出
    if user_input.lower() in ['退出', 'exit', 'quit']:
        print("对话结束。")
        break

    # 获取ERNIE回复
    response = chat_with_ernie(user_input, messages)

    # 输出ERNIE的回复
    print(f"\n{model}: {response}\n")
