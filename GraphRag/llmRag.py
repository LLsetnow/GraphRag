from pydantic import BaseModel, Field
from typing import List
import erniebot

# 配置 ERNIE API
erniebot.api_type = 'aistudio'  # 根据实际情况选择类型
erniebot.access_token = '66f2cca42998fba19928022ac4829155eb17b312'

# 定义 ERNIE 模型
model = "ernie-4.0-turbo-8k"


# 定义实体提取的结构化模型
class Entities(BaseModel):
    """识别实体相关信息。"""
    names: List[str] = Field(
        ...,
        description="文本中提取的所有人物、组织或商业实体的名称",
    )
    places: List[str] = Field(
        default=[],
        description="文本中提取的所有地名",
    )
    dates: List[str] = Field(
        default=[],
        description="文本中提取的所有时间",
    )


# 定义 Prompt
Prompt = """
您是一个 NLP 模型，任务是从文本中提取特定的实体。
请按照以下格式返回提取结果：
{{
    "names": ["所有的人物名称"],
    "places": ["所有的地名"],
    "dates": ["所有的时间"]
}}
文本：{input_text}
"""

# 定义调用 ERNIE 模型的函数
def extract_entities(input_text: str) -> Entities:
    # 构建消息
    messages = [
        {"role": "user", "content": Prompt.format(input_text=input_text)},
    ]

    # 调用 ERNIE API
    response = erniebot.ChatCompletion.create(
        model=model,
        messages=messages,
    )

    # 提取结果并结构化
    result = response.get_result()
    structured_output = Entities.parse_raw(result)

    return structured_output


# 测试提取实体功能
if __name__ == "__main__":
    text = "阿梅莉亚·埃尔哈特于1937年在太平洋上空失踪,她出生于堪萨斯州阿奇森."

    entities = extract_entities(text)
    print("提取结果:")
    print(f"人物: {entities.names}")
    print(f"地名: {entities.places}")
    print(f"时间: {entities.dates}")
