import pdfplumber
import csv

# 打开PDF文件
pdf_path = 'output_pdf_13_35.pdf'
output_csv = 'textbook_data.csv'

# 用来存储解析后的结构化数据
data_rows = []

# 使用 pdfplumber 打开 PDF 文件
with pdfplumber.open(pdf_path) as pdf:
    for page_num, page in enumerate(pdf.pages):
        # 提取每一页的文本
        text = page.extract_text()

        if text:
            # 将每一页的文本存入到结构化数据中（此处简单示例是逐页存储）
            data_rows.append([page_num + 1, text])  # 将页码和对应文本保存到 data_rows 列表中

# 将数据写入 CSV 文件
with open(output_csv, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    # 写入表头
    writer.writerow(['Page Number', 'Text'])
    # 写入每一页的文本数据
    writer.writerows(data_rows)

print(f"PDF 中的文本已成功导出到 {output_csv}")
