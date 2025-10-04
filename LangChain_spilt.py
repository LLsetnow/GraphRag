from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
import pandas as pd

csv_file = 'output/text_reply.csv'

# 读取txt文件内容
file_path = "input//textbook.txt"
with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
    long_text = file.read()

# 使用 LangChain 提供的文本分割工具
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=100,   # 每个文本块的字符数
    chunk_overlap=10  # 文本块之间的重叠字符数
)

# 对长文段进行分割
split_texts = text_splitter.split_text(long_text)

# 将分割后的文段保存为 DataFrame
df = pd.DataFrame(split_texts, columns=['replay'])

# 将 DataFrame 保存为 CSV 文件
df.to_csv(csv_file, index=False, encoding='utf-8')

print("文段分割完成并保存为 text_reply.csv 文件")

# !cp {csv_file} ../ErnieRag
# print(f"复制{csv_file}至../ErnieRag")