# LLM 技术学习与实践项目

> 涵盖 GraphRAG、知识图谱问答、LangChain 文本处理等多个方向的 LLM 应用实践项目集

---

## 📋 项目概述

本项目集是关于大语言模型（LLM）及相关技术的学习与实践，主要探索 GraphRAG、知识图谱问答、文本处理等应用场景。

---

## 📁 主要模块

### 1. QASystemOnMedicalKG - 医疗知识图谱问答系统

从零构建以疾病为中心的医疗知识图谱，并实现自动问答服务。

**项目规模**
- 实体：7类约 4.4 万个（疾病、症状、药品、食物等）
- 关系：11类约 30 万条

**技术栈**
- Neo4j 图数据库 + 规则匹配 + Cypher 查询

**支持问答类型（18种）**
| 类型 | 说明 | 示例 |
|------|------|------|
| disease_symptom | 疾病症状 | 乳腺癌的症状有哪些？ |
| symptom_disease | 症状找疾病 | 最近老流鼻涕怎么办？ |
| disease_cause | 疾病病因 | 为什么有的人会失眠？ |
| disease_drug | 疾病用药 | 肝病要吃啥药？ |
| disease_check | 检查项目 | 脑膜炎怎么才能查出来？ |
| ... | 更多 | ... |

**核心文件**
- `build_medicalgraph.py` - 知识图谱构建与入库
- `chatbot_graph.py` - 问答程序主入口
- `question_classifier.py` - 问句类型分类
- `question_parser.py` - 问句解析

**运行方式**
```bash
# 1. 导入知识图谱数据（需要几小时）
python build_medicalgraph.py

# 2. 启动问答系统
python chatbot_graph.py
```

---

### 2. GraphRag - 图检索增强生成

结合知识图谱的 RAG 实现，用于特定领域知识问答。

**技术特点**
- LLM 实体提取 + Neo4j 知识检索
- 支持多轮对话上下文管理
- 应用场景：近代史知识问答

**核心文件**
- `GraphRag.py` - GraphRAG 主程序
- `main.py` - 主逻辑与交互
- `graph2neo4j.py` - 图数据导入 Neo4j
- `neo4j2json*.py` - 数据导出工具

---

### 3. LangChain 文本处理

使用 LangChain 框架进行文本分割与处理。

**功能**
- 长文本切分为小块（chunk_size=100, chunk_overlap=10）
- 支持递归字符分割器
- 输出 CSV 格式分割结果

**核心文件**
- `LangChain_spilt.py` - 文本分割工具
- `LangChain_test.py` - 测试脚本

---

### 4. ChatGLM - 智谱AI对话

基于智谱AI的对话功能实现。

**核心文件**
- `chat_ZhipuAi.py` - 智谱AI API 调用

---

### 5. Neo4j 集成

Neo4j 图数据库的连接与操作。

**核心文件**
- `ernie&neo4j.py` - 文心一言 + Neo4j 知识问答
- `neo4j_link.py` - 数据库连接管理
- `clear_neo4j.py` - 数据清理工具

---

### 6. 数据库

存放原始文本数据，用于知识图谱构建。

**文件**
- `近代史.txt` - 近代史知识文本
- `data_jindaishi.txt` - 结构化数据

---

## 🔧 技术栈

| 技术 | 用途 |
|------|------|
| **LangChain** | 文本处理、分割、链式调用 |
| **Neo4j** | 图数据库存储知识图谱 |
| **erniebot** | 百度文心一言 API |
| **zhipuai** | 智谱AI API |
| **tiktoken** | Token 分词与计数 |
| **networkx** | 图数据结构处理 |
| **pdfplumber** | PDF 文件解析 |
| **milvus** | 向量数据库 |
| **pandas** | 数据处理 |

---

## 💡 学习要点

1. **知识图谱构建流程**
   ```
   数据采集 → 实体/关系抽取 → Schema 设计 → Neo4j 存储 → 应用查询
   ```

2. **RAG 实现模式**
   - 向量检索 + LLM 生成（传统 RAG）
   - 图检索 + LLM 生成（GraphRAG）
   - 混合检索模式

3. **问答系统架构**
   ```
   用户提问 → 实体提取 → 图谱查询 → 答案生成 → 润色输出
   ```

4. **文本处理最佳实践**
   - 合理设置 chunk_size 与 overlap
   - 保留上下文语义完整性

---

## 📦 依赖安装

```bash
pip install -r requirements.txt
```

主要依赖：
```
tiktoken          # Token 分词
networkx          # 图处理
erniebot          # 百度文心一言
langchain         # LangChain 框架
pandas            # 数据处理
neo4j             # Neo4j 驱动
tqdm              # 进度条
zhipuai           # 智谱AI
pdfplumber        # PDF 解析
milvus[client]    # 向量数据库
```

---

## 🚀 快速开始

### 医疗问答系统

```bash
cd QASystemOnMedicalKG-master
python build_medicalgraph.py  # 构建图谱
python chatbot_graph.py       # 启动问答
```

### GraphRag

```bash
cd GraphRag
python GraphRag.py            # 运行 GraphRag
```

### 文本分割

```bash
python LangChain_spilt.py     # 处理 input/textbook.txt
```

---

## 📄 许可证

本项目数据仅供学习交流使用，请勿商用。医疗问答系统数据来源自垂直医药网站，如涉及版权问题请联系删除。

---

## 🔗 参考资源

- [QASystemOnMedicalKG 原项目](https://github.com/liuhuanyong/QABasedOnMedicalKnowledgeGraph)
- [LangChain 官方文档](https://python.langchain.com/)
- [Neo4j 文档](https://neo4j.com/docs/)

