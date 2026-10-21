"""RedFox 数据 MCP：find、describe、call、result。

能力执行沿用各平台 server 里同一条 SDK 调用。本服务不注册那 100 多个工具。
模型看到的服务说明、能力编号枚举和参数名从目录生成，和线上 tools/list 一致。
鉴权和业务日志走 redfox-mcp-core。
"""

from __future__ import annotations

import argparse
import inspect
import os
from typing import Annotated, Any, Literal, Optional

from pydantic import Field
from redfox_mcp_core import create_server, serve
from redfox_mcp_core.runtime import _emit

from redfox_data_mcp import __version__
from redfox_data_mcp.dispatch import invoke, query_result
from redfox_data_mcp.schema import async_ids, capability_ids, find_param_descriptions, find_tool_description, instructions, param_specs
from redfox_data_mcp.search import DESCRIBE_LIMIT, describe as describe_catalog
from redfox_data_mcp.search import find as find_catalog

mcp = create_server("红狐数据", __version__)
mcp.instructions = instructions()


def _literal(values: list[str]):
    return Literal.__getitem__(tuple(values))


Capability = _literal(capability_ids())
AsyncCapability = _literal(async_ids())


def _optional(json_type: str | list[str]):
    if json_type == "integer":
        return Optional[int]
    if json_type == "boolean":
        return Optional[bool]
    if json_type == "array":
        return Optional[list[Any]]
    if json_type == "string":
        return Optional[str]
    return Optional[Any]


def _bind(fn, parameters: list[inspect.Parameter]) -> None:
    fn.__signature__ = inspect.Signature(parameters)
    fn.__annotations__ = {param.name: param.annotation for param in parameters}
    fn.__annotations__["return"] = dict[str, Any]


_FIND = find_param_descriptions()


def find(
    query: Annotated[str, Field(description=_FIND["query"])] = "",
    platform: Annotated[str, Field(description=_FIND["platform"])] = "",
    category: Annotated[str, Field(description=_FIND["category"])] = "",
) -> dict[str, Any]:
    result = find_catalog(query=query, platform=platform, category=category)
    _emit(
        "mcp_call",
        tool="find",
        arguments={"query": query, "platform": platform, "category": category},
        ok="error" not in result,
        result={"matches": [m["id"] for m in result.get("matches") or []], "unknown": result.get("unknown"), "error": result.get("error")},
    )
    return result


find.__doc__ = find_tool_description()
mcp.tool()(find)


def describe(ids: list[str]) -> dict[str, Any]:
    """读取 1 到 10 个已开放能力的参数、必填项、是否异步，以及一条示例调用。

    ids 只能用 call 列出的编号。参数名能从 call 上看懂时可以不调用；取值、多选一或是否异步不确定时再调用。
    """
    if not isinstance(ids, list) or any(not isinstance(item, str) for item in ids):
        result = {"error": "invalid_argument", "message": "ids 必须是字符串数组"}
    elif len(ids) > DESCRIBE_LIMIT:
        result = {"error": "invalid_argument", "message": f"一次最多描述 {DESCRIBE_LIMIT} 个能力"}
    else:
        result = describe_catalog(ids)
    _emit(
        "mcp_call",
        tool="describe",
        arguments={"ids": ids},
        ok="error" not in result,
        result={"ids": [item.get("id") for item in result.get("capabilities") or []], "missing": result.get("missing"), "error": result.get("error")},
    )
    return result


describe.__annotations__["ids"] = Annotated[
    list[Capability],
    Field(description="能力编号，1 到 10 个，取 call 的 capability 列表里的值"),
]
mcp.tool()(describe)


def call(capability: str, **kwargs: Any) -> dict[str, Any]:
    """调用一个已开放的能力。capability 用列表中的编号；列表里有就直接调用，不要先 find。

    只填这个能力自己的参数，参数名和含义写在下面。取值或是否必填不确定时先 describe。编号不存在或参数不合法时不会请求上游。
    异步能力超时返回 taskId，再用 result 查询。榜单分类（体育、美食等）填 type。
    """
    arguments = {key: value for key, value in kwargs.items() if value is not None}
    return invoke(capability, arguments)


_call_params = [
    inspect.Parameter(
        "capability",
        inspect.Parameter.POSITIONAL_OR_KEYWORD,
        annotation=Annotated[Capability, Field(description="能力编号。列表里有就直接用；对不上再 find")],
    )
]
for _spec in param_specs():
    _call_params.append(
        inspect.Parameter(
            _spec["name"],
            inspect.Parameter.KEYWORD_ONLY,
            default=None,
            annotation=Annotated[
                _optional(_spec["json_type"]),
                Field(description=_spec["description"]),
            ],
        )
    )
_bind(call, _call_params)
mcp.tool()(call)


def result(capability: str, task_id: str) -> dict[str, Any]:
    """查询异步任务。capability 用当时 call 的同一个编号，task_id 用返回里的 taskId。

    当前会超时并返回 taskId 的是各平台视频文案提取，以及小红书笔记评论。
    """
    return query_result(capability, task_id)


_bind(result, [
    inspect.Parameter(
        "capability",
        inspect.Parameter.POSITIONAL_OR_KEYWORD,
        annotation=Annotated[AsyncCapability, Field(description="异步能力编号，与当时的 call 相同")],
    ),
    inspect.Parameter(
        "task_id",
        inspect.Parameter.POSITIONAL_OR_KEYWORD,
        annotation=Annotated[str, Field(description="call 超时返回的 taskId")],
    ),
])
mcp.tool()(result)


def main() -> None:
    mode = os.getenv("REDFOX_MCP_AUTH_MODE", "apikey").strip().lower()
    if mode in {"oauth", "multi"}:
        from redfox_data_mcp.oauth_http import serve as serve_oauth

        serve_oauth(mcp)
        return
    serve(mcp, prog="redfox-data-mcp", description="RedFox 数据 MCP：find / describe / call / result")


if __name__ == "__main__":
    main()
