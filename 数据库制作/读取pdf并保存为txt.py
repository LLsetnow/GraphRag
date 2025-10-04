import pdfplumber

# PDF 文件路径
pdf_path = 'output_pdf_13_35.pdf'
# 输出的 TXT 文件路径
output_txt = 'textbook.txt'

# 打开 PDF 文件
with pdfplumber.open(pdf_path) as pdf:
    # 打开一个 TXT 文件用于写入
    with open(output_txt, 'w', encoding='utf-8') as txt_file:
        # 遍历每一页
        for page_num, page in enumerate(pdf.pages):
            # 提取每一页的文本
            text = page.extract_text()
            if text:
                # 写入页码
                # txt_file.write(f"Page {page_num + 1}:\n")
                # 写入文本
                txt_file.write(text)
                txt_file.write("\n\n")  # 每页之间空一行

print(f"PDF 中的文本已成功导出到 {output_txt}")
