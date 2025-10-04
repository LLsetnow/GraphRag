import tiktoken
from abc import ABC, abstractmethod
import pandas as pd
from typing import Any, Literal, cast
from dataclasses import dataclass
from collections.abc import Callable, Collection, Iterable

EncodedText = list[int]
DecodeFn = Callable[[EncodedText], str]
EncodeFn = Callable[[str], EncodedText]
LengthFn = Callable[[str], int]


@dataclass(frozen=True)
class Tokenizer:
    """Tokenizer data class."""

    chunk_overlap: int
    """Overlap in tokens between chunks"""
    tokens_per_chunk: int
    """Maximum number of tokens per chunk"""
    decode: DecodeFn
    """ Function to decode a list of token ids to a string"""
    encode: EncodeFn
    """ Function to encode a string to a list of token ids"""


class TextSplitter(ABC):
    """Text splitter class definition."""

    _chunk_size: int
    _chunk_overlap: int
    _length_function: LengthFn
    _keep_separator: bool
    _add_start_index: bool
    _strip_whitespace: bool

    def __init__(
            self,
            # based on text-ada-002-embedding max input buffer length
            # https://platform.openai.com/docs/guides/embeddings/second-generation-models
            chunk_size: int = 8191,
            chunk_overlap: int = 100,
            length_function: LengthFn = len,
            keep_separator: bool = False,
            add_start_index: bool = False,
            strip_whitespace: bool = True,
    ):
        """Init method definition."""
        self._chunk_size = chunk_size
        self._chunk_overlap = chunk_overlap
        self._length_function = length_function
        self._keep_separator = keep_separator
        self._add_start_index = add_start_index
        self._strip_whitespace = strip_whitespace

    @abstractmethod
    def split_text(self, text: str | list[str]) -> Iterable[str]:
        """Split text method definition."""


class TokenTextSplitter(TextSplitter):
    """Token text splitter class definition."""

    _allowed_special: Literal["all"] | set[str]
    _disallowed_special: Literal["all"] | Collection[str]

    def __init__(
            self,
            encoding_name: str = "cl100k_base",
            model_name: str | None = None,
            allowed_special: Literal["all"] | set[str] | None = None,
            disallowed_special: Literal["all"] | Collection[str] = "all",
            **kwargs: Any,
    ):
        """Init method definition."""
        super().__init__(**kwargs)
        if model_name is not None:
            try:
                enc = tiktoken.encoding_for_model(model_name)
            except KeyError:
                print("Model %s not found, using %s", model_name, encoding_name)
                enc = tiktoken.get_encoding(encoding_name)
        else:
            enc = tiktoken.get_encoding(encoding_name)
        self._tokenizer = enc
        self._allowed_special = allowed_special or set()
        self._disallowed_special = disallowed_special

    def encode(self, text: str) -> list[int]:
        """Encode the given text into an int-vector."""
        return self._tokenizer.encode(
            text,
            allowed_special=self._allowed_special,
            disallowed_special=self._disallowed_special,
        )

    def num_tokens(self, text: str) -> int:
        """Return the number of tokens in a string."""
        return len(self.encode(text))

    def split_text(self, text: str | list[str]) -> list[str]:
        """Split text method."""
        if cast(bool, pd.isna(text)) or text == "":
            return []
        if isinstance(text, list):
            text = " ".join(text)
        if not isinstance(text, str):
            msg = f"Attempting to split a non-string value, actual is {type(text)}"
            raise TypeError(msg)

        tokenizer = Tokenizer(
            chunk_overlap=self._chunk_overlap,
            tokens_per_chunk=self._chunk_size,
            decode=self._tokenizer.decode,
            encode=lambda text: self.encode(text),
        )

        return split_text_on_tokens(text=text, tokenizer=tokenizer)


def split_text_on_tokens(*, text: str, tokenizer: Tokenizer) -> list[str]:
    """Split incoming text and return chunks using tokenizer."""
    splits: list[str] = []
    input_ids = tokenizer.encode(text)
    start_idx = 0
    cur_idx = min(start_idx + tokenizer.tokens_per_chunk, len(input_ids))
    chunk_ids = input_ids[start_idx:cur_idx]
    while start_idx < len(input_ids):
        splits.append(tokenizer.decode(chunk_ids))
        start_idx += tokenizer.tokens_per_chunk - tokenizer.chunk_overlap
        cur_idx = min(start_idx + tokenizer.tokens_per_chunk, len(input_ids))
        chunk_ids = input_ids[start_idx:cur_idx]
    return splits


def create_text_splitter(chunk_size: int,
                         chunk_overlap: int,
                         encoding_name: str):
    """Create a text splitter for the extraction chain.

    Args:
        - chunk_size - The size of each chunk
        - chunk_overlap - The overlap between chunks
        - encoding_name - The name of the encoding to use
    Returns:
        - output - A text splitter
    """

    return TokenTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        encoding_name=encoding_name,
    )


# LLM模块
import erniebot
from dataclasses import dataclass, field
from typing import Generic, TypeVar, Any

erniebot.api_type = "aistudio"
# 替换成自己的token
erniebot.access_token = "66f2cca42998fba19928022ac4829155eb17b312"

######################我是分割线############################
T = TypeVar("T")


@dataclass
class LLMOutput(Generic[T]):
    """The output of an LLM invocation."""

    output: T | None
    """The output of the LLM invocation."""

    json: dict | None = field(default=None)
    """The JSON output from the LLM, if available."""

    history: list[dict] | None = field(default=None)
    """The history of the LLM invocation, if available (e.g. chat mode)"""


class ErnieExecutor:
    def __init__(self, model):
        self.model = model

    async def __call__(self,
                       input,
                       **kwargs):

        is_json = kwargs.get("is_json", False)
        if is_json:
            return await self._invoke_json(input, **kwargs)
        return self._invoke(input, **kwargs)

    def _execute_llm(self, input, **kwargs):
        history = kwargs.get("history", [])
        variables = kwargs.get("variables", {})
        if variables:
            input = input.format(**variables)

        messages = [
            *history,
            {"role": "user", "content": input},
        ]

        response = erniebot.ChatCompletion.create(
            model=self.model,
            messages=messages,
        )
        return LLMOutput(
            output=response.get_result(),
            history=[{"role": "user", "content": input},
                     {"role": "assistant", "content": response.get_result()}],
        )

    def _invoke(self, input, **kwargs):
        response = self._execute_llm(input, **kwargs)
        return response


# Prompt设计
GRAPH_EXTRACTION_PROMPT = """

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

CONTINUE_PROMPT = "在上次提取中遗漏了许多实体和关系。请记住，只输出与先前提取的任何类型相匹配的实体。请使用相同的格式在下方添加它们：\n"
LOOP_PROMPT = "看起来可能仍然遗漏了一些实体和关系。如果还有需要添加的实体或关系，请回答<是> 或者 <否>。"


import re
import html
import tiktoken
import logging
import traceback
import numbers
from collections.abc import Mapping
import networkx as nx
from tqdm import tqdm

from typing import Any
from dataclasses import dataclass
from collections.abc import Callable

ENTITY_EXTRACTION_MAX_GLEANINGS = 1
DEFAULT_TUPLE_DELIMITER = "<|>"
DEFAULT_RECORD_DELIMITER = "##"
DEFAULT_COMPLETION_DELIMITER = "<|COMPLETE|>"
DEFAULT_ENTITY_TYPES = ["organization", "person", "geo", "event"]


ErrorHandlerFn = Callable[[BaseException | None, str | None, dict | None], None]

@dataclass
class GraphExtractionResult:
    """Unipartite graph extraction result class definition."""

    output: nx.Graph
    source_docs: dict[Any, Any]

class GraphExtractor:
    """Unipartite graph extractor class definition."""

    _join_descriptions: bool
    _tuple_delimiter_key: str
    _record_delimiter_key: str
    _entity_types_key: str
    _input_text_key: str
    _completion_delimiter_key: str
    _entity_name_key: str
    _input_descriptions_key: str
    _extraction_prompt: str
    _summarization_prompt: str
    _loop_args: dict[str, Any]
    _max_gleanings: int
    _on_error: ErrorHandlerFn

    def __init__(
        self,
        llm_invoker,
        tuple_delimiter_key: str | None = None,
        record_delimiter_key: str | None = None,
        input_text_key: str | None = None,
        entity_types_key: str | None = None,
        completion_delimiter_key: str | None = None,
        prompt: str | None = None,
        join_descriptions=True,
        encoding_model: str | None = None,
        max_gleanings: int | None = None,
        on_error: ErrorHandlerFn | None = None,
    ):
        """Init method definition."""
        # TODO: streamline construction
        self._llm = llm_invoker
        self._join_descriptions = join_descriptions
        self._input_text_key = input_text_key or "input_text"
        self._tuple_delimiter_key = tuple_delimiter_key or "tuple_delimiter"
        self._record_delimiter_key = record_delimiter_key or "record_delimiter"
        self._completion_delimiter_key = (
            completion_delimiter_key or "completion_delimiter"
        )
        self._entity_types_key = entity_types_key or "entity_types"
        self._extraction_prompt = prompt or GRAPH_EXTRACTION_PROMPT
        self._max_gleanings = (
            max_gleanings
            if max_gleanings is not None
            else ENTITY_EXTRACTION_MAX_GLEANINGS
        )
        self._on_error = on_error or (lambda _e, _s, _d: None)

        # Construct the looping arguments
        encoding = tiktoken.get_encoding(encoding_model or "cl100k_base")
        yes = encoding.encode("是")
        no = encoding.encode("否")
        self._loop_args = {"logit_bias": {yes[0]: 100, no[0]: 100}, "max_tokens": 1}

    async def __call__(
        self,
        texts: list[str],
        prompt_variables: dict[str, Any] | None = None
    ) -> GraphExtractionResult:
        """Call method definition."""
        if prompt_variables is None:
            prompt_variables = {}
        all_records: dict[int, str] = {}
        source_doc_map: dict[int, str] = {}

        # Wire defaults into the prompt variables
        prompt_variables = {
            **prompt_variables,
            self._tuple_delimiter_key: prompt_variables.get(self._tuple_delimiter_key)
            or DEFAULT_TUPLE_DELIMITER,
            self._record_delimiter_key: prompt_variables.get(self._record_delimiter_key)
            or DEFAULT_RECORD_DELIMITER,
            self._completion_delimiter_key: prompt_variables.get(
                self._completion_delimiter_key
            )
            or DEFAULT_COMPLETION_DELIMITER,
            self._entity_types_key: ",".join(
                prompt_variables[self._entity_types_key] or DEFAULT_ENTITY_TYPES
            ),
        }

        for doc_index, text in tqdm(enumerate(texts)):
            try:
                # Invoke the entity extraction
                result = await self._process_document(text, prompt_variables)
                source_doc_map[doc_index] = text
                all_records[doc_index] = result
            except Exception as e:
                logging.exception("error extracting graph")
                self._on_error(
                    e,
                    traceback.format_exc(),
                    {
                        "doc_index": doc_index,
                        "text": text,
                    },
                )

        output = await self._process_results(
            all_records,
            prompt_variables.get(self._tuple_delimiter_key, DEFAULT_TUPLE_DELIMITER),
            prompt_variables.get(self._record_delimiter_key, DEFAULT_RECORD_DELIMITER),
        )

        return GraphExtractionResult(
            output=output,
            source_docs=source_doc_map,
        )

    async def _process_document(
        self,
        text: str,
        prompt_variables: dict[str, str]
    ) -> str:
        response = await self._llm(
            self._extraction_prompt,
            variables={
                **prompt_variables,
                self._input_text_key: text,
            },
        )
        results = response.output or ""

        # Repeat to ensure we maximize entity count
        for i in range(self._max_gleanings):
            response = await self._llm(
                CONTINUE_PROMPT,
                name=f"extract-continuation-{i}",
                history=response.history,
            )
            results += response.output or ""

            # if this is the final glean, don't bother updating the continuation flag
            if i >= self._max_gleanings - 1:
                break

            response = await self._llm(
                LOOP_PROMPT,
                name=f"extract-loopcheck-{i}",
                history=response.history,
                model_parameters=self._loop_args,
            )
            if response.output != "是":
                break

        return results

    async def _process_results(
        self,
        results: dict[int, str],
        tuple_delimiter: str,
        record_delimiter: str,
    ) -> nx.Graph:
        """Parse the result string to create an undirected unipartite graph.

        Args:
            - results - dict of results from the extraction chain
            - tuple_delimiter - delimiter between tuples in an output record, default is '<|>'
            - record_delimiter - delimiter between records, default is '##'
        Returns:
            - output - unipartite graph in graphML format
        """
        graph = nx.Graph()
        for source_doc_id, extracted_data in results.items():
            records = [r.strip() for r in extracted_data.split(record_delimiter)]

            for record in records:
                record = re.sub(r"^\(|\)$", "", record.strip())
                record_attributes = record.split(tuple_delimiter)

                if record_attributes[0] == '"entity"' and len(record_attributes) >= 4:
                    # add this record as a node in the G
                    entity_name = clean_str(record_attributes[1].upper())
                    entity_type = clean_str(record_attributes[2].upper())
                    entity_description = clean_str(record_attributes[3])

                    if entity_name in graph.nodes():
                        node = graph.nodes[entity_name]
                        if self._join_descriptions:
                            node["description"] = "\n".join(
                                list({
                                    *_unpack_descriptions(node),
                                    entity_description,
                                })
                            )
                        else:
                            if len(entity_description) > len(node["description"]):
                                node["description"] = entity_description
                        node["source_id"] = ", ".join(
                            list({
                                *_unpack_source_ids(node),
                                str(source_doc_id),
                            })
                        )
                        node["entity_type"] = (
                            entity_type if entity_type != "" else node["entity_type"]
                        )
                    else:
                        graph.add_node(
                            entity_name,
                            type=entity_type,
                            description=entity_description,
                            source_id=str(source_doc_id),
                        )

                if (
                    record_attributes[0] == '"relationship"'
                    and len(record_attributes) >= 5
                ):
                    # add this record as edge
                    source = clean_str(record_attributes[1].upper())
                    target = clean_str(record_attributes[2].upper())
                    edge_description = clean_str(record_attributes[3])
                    edge_source_id = clean_str(str(source_doc_id))
                    weight = (
                        float(record_attributes[-1])
                        if isinstance(record_attributes[-1], numbers.Number)
                        else 1.0
                    )
                    if source not in graph.nodes():
                        graph.add_node(
                            source,
                            type="",
                            description="",
                            source_id=edge_source_id,
                        )
                    if target not in graph.nodes():
                        graph.add_node(
                            target,
                            type="",
                            description="",
                            source_id=edge_source_id,
                        )
                    if graph.has_edge(source, target):
                        edge_data = graph.get_edge_data(source, target)
                        if edge_data is not None:
                            weight += edge_data["weight"]
                            if self._join_descriptions:
                                edge_description = "\n".join(
                                    list({
                                        *_unpack_descriptions(edge_data),
                                        edge_description,
                                    })
                                )
                            edge_source_id = ", ".join(
                                list({
                                    *_unpack_source_ids(edge_data),
                                    str(source_doc_id),
                                })
                            )
                    graph.add_edge(
                        source,
                        target,
                        weight=weight,
                        description=edge_description,
                        source_id=edge_source_id,
                    )

        return graph


def clean_str(input: Any) -> str:
    """Clean an input string by removing HTML escapes, control characters, and other unwanted characters."""
    # If we get non-string input, just give it back
    if not isinstance(input, str):
        return input

    result = html.unescape(input.strip())
    # https://stackoverflow.com/questions/4324790/removing-control-characters-from-a-string-in-python
    return re.sub(r"[\x00-\x1f\x7f-\x9f]", "", result)

def _unpack_descriptions(data: Mapping) -> list[str]:
    value = data.get("description", None)
    return [] if value is None else value.split("\n")

def _unpack_source_ids(data: Mapping) -> list[str]:
    value = data.get("source_id", None)
    return [] if value is None else value.split(", ")


@dataclass
class EntityExtractionResult:
    """Entity extraction result class definition."""
    ExtractedEntity = dict[str, Any]

    entities: list[ExtractedEntity]
    graphml_graph: str | None

@dataclass
class Document:
    """Document class definition."""

    text: str
    id: str

import networkx as nx

async def main():
    # read the docs
    with open("..//input//test.txt", "r", encoding="utf-8") as f:
        file = f.readlines()
    docs = []
    for id, doc in enumerate(file):
        docs.append(Document(id=id, text=doc))

    text_splitter = create_text_splitter(
        chunk_size=1200,
        chunk_overlap=100,
        encoding_name="cl100k_base",
    )

    # 去除前后空白，得到文本内容的列表
    text_list = [doc.text.strip() for doc in docs]

    # 将 text_list 中的所有文本合并为一个字符串（每个文档之间用换行符 \n 连接
    text_list = text_splitter.split_text("\n".join(text_list))

    llm = ErnieExecutor(model="ernie-4.0-turbo-8k")

    extractor = GraphExtractor(
        llm_invoker=llm,
    )

    # extract the type of entities
    entity_types = ["人名", "组织", "地点"]
    results = await extractor(
        list(text_list),
        {
            "entity_types": entity_types,
            "tuple_delimiter": "<|>",
            "record_delimiter": "##",
            "completion_delimiter": "<|COMPLETE|>",
        },
    )
    graph = results.output

    # Map the "source_id" back to the "id" field
    for _, node in graph.nodes(data=True):  # type: ignore
        if node is not None:
            node["source_id"] = ",".join(
                str(docs[int(id)].id) for id in node["source_id"].split(",")
            )

    for _, _, edge in graph.edges(data=True):  # type: ignore
        if edge is not None:
            edge["source_id"] = ",".join(
                str(docs[int(id)].id) for id in edge["source_id"].split(",")
            )

    entities = [
        ({"name": item[0], **(item[1] or {})})
        for item in graph.nodes(data=True)
        if item is not None
    ]

    graph_data = "".join(nx.generate_graphml(graph))

    nx.write_gexf(graph, "graph.gexf")

    return EntityExtractionResult(entities, graph_data)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
    # await main()