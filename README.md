# 目录功能介绍
- 数据库制作
   读取pdf格式的原始数据，并保存为txt文件
- GraphRag
   - main.py
      功能：读取txt文件, 并生产关系图 graph.gexf
      关系图：包含主体、[主体描述]、主体间的关系
      实现原理：
         1. 文本分割
         2. LLM 实体/关系提取
         3. 图构建
   - graph2neo4j.py
      功能：读取graph.gexf，并上传neo4j数据库
   - GraphRag.py
      功能：用户提问 -> LLM 提取实体 -> Neo4j 图谱检索(主要参考[主体描述] 与 相邻节点) -> LLM 生成答案

# 关系提取 Prompt设计
- 关键设计点：

设计点	说明
两阶段提取	先提取实体，再从实体中提取关系，减少误判
结构化输出	使用分隔符便于程序解析
关系强度	权重字段，用于后续图分析
Few-shot 示例	2 个示例提高准确性


## 目标
根据给定的文档提取

## 步骤
1. 识别出所有的实体。针对每个实体，提取以下信息：
- entity_name:实体的名称，首字母大写
- entity_type:以下类型之一：[{entity_types}]
- entity_description:对实体的属性和活动进行详细的描述
将每个实体格式化为("entity"{tuple_delimiter}<entity_name>{tuple_delimiter}<entity_type>{tuple_delimiter}<entity_description>)

2.从步骤1识别的实体中，找出所有明显相关的(source_entity, target_entity)对。
对于每对相关的实体，提取以下信息：
- source_entity: 步骤1识别的源实体名称
- target_entity: 步骤1识别的目标实体名称
- relationship_description: 源实体和目标实体之间的关系
- relationship_strength: 一个数值分数，表示源实体和目标实体之间关系的强度
将每个关系对格式化为("relationship"{tuple_delimiter}<source_entity>{tuple_delimiter}<target_entity>{tuple_delimiter}<relation_description>{tuple_delimiter}<relationship_strength>)

3.返回步骤1和步骤2中识别的所有实体和关系的单个列表，使用{record_delimiter}作为列表分隔符。

4.完成后，输出{completion_delimiter}

######################
-输出示例
######################
示例1：
Entity_types: 组织，人物
Text: 联储中央机构计划于周一和周四召开会议，该机构计划于太平洋夏令时周四下午 1:30 发布其最新的政策决定，随后将举行新闻发布会，中央机构主席马丁·史密斯将回答媒体提问。投资者预计市场战略委员会将基准利率维持在3.5%-3.75%的范围内。
######################
Output:
("entity"{tuple_delimiter}联储中央机构{tuple_delimiter}组织{tuple_delimiter}联储中央机构计划于周一和周四召开会议，它将在周一和周四设定利率")
{record_delimiter}
("entity"{tuple_delimiter}马丁·史密斯{tuple_delimiter}人物{tuple_delimiter}马丁·史密斯是联储中央机构的主席")
{record_delimiter}
("relationship"{tuple_delimiter}联储中央机构{tuple_delimiter}马丁·史密斯{tuple_delimiter}主席{tuple_delimiter}1.0)
{completion_delimiter}

######################
示例2：
Entity_types: 组织，地点
Text: 
当地时间7月31日周三，由于技术故障，瑞士SIX证券交易所 SIX Swiss Exchange 两次暂停交易。
公开资料显示，SIX Swiss Exchange，总部位于瑞士，是欧洲重要的金融市场之一，以其全面的服务范围和高流动性而著称。该交易所由多个地方交易所合并而成，现已成为交易股票、债券、交易所交易基金（ETF）、结构化产品以及加密产品的重要中心。SIX Swiss Exchange拥有超过60000种证券产品，包括一些最大的欧洲蓝筹股和丰富的加密货币产品。
######################
Output:
("entity"{tuple_delimiter}SIX Swiss Exchange{tuple_delimiter}组织{tuple_delimiter}Swiss Exchange 是欧洲重要的金融市场之一，以其全面的服务范围和高流动性而著称。该交易所由多个地方交易所合并而成，现已成为交易股票、债券、交易所交易基金（ETF）、结构化产品以及加密产品的重要中心。")
{record_delimiter}
("entity"{tuple_delimiter}瑞士{tuple_delimiter}地点{tuple_delimiter}Swiss Exchange 是欧洲重要的金融市场之一，以其全面的服务范围和高流动性而著称。该交易所由多个地方交易所合并而成，现已成为交易股票、债券、交易所交易基金（ETF）、结构化产品以及加密产品的重要中心。")
{record_delimiter}
("relationship"{tuple_delimiter}SIX Swiss Exchange{tuple_delimiter}欧洲{tuple_delimiter}地址{tuple_delimiter}1.0)

######################
你需要提取的数据
######################
Entity_types: {entity_types}
Text: {input_text}
######################
Output:
"""

         