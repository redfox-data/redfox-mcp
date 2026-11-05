"""RedFox 云市场 MCP：find、describe、call、result。

目录、检索、参数表与校验均在本包内自包含（catalog.json / search / schema / dispatch），
不依赖 redfox-data-mcp。特点：
- 鉴权走普通 apikey（HTTP 时从 Authorization: Bearer <key> 或 REDFOX_API_KEY 头读取），不接 OAuth。
- 工具返回按云市场返回规范包成 {isError, content:[{type:text,text:<json>}]}，
  成功码仅上游 2000 / 3801，其余为失败（见 wrap.py）。
"""

from __future__ import annotations

import inspect
from typing import Annotated, Any, Literal, Optional

from pydantic import Field
from fastmcp.exceptions import ValidationError as FastMCPValidationError
from fastmcp.server.middleware import Middleware
from redfox_mcp_core import create_server, get_client, serve

from redfox_cloud_mcp import __version__
from redfox_cloud_mcp.dispatch import prepare
from redfox_cloud_mcp.schema import (
    async_ids,
    capability_ids,
    find_param_descriptions,
    find_tool_description,
    instructions,
    param_specs,
)
from redfox_cloud_mcp.search import DESCRIBE_LIMIT, by_id
from redfox_cloud_mcp.search import describe as describe_catalog
from redfox_cloud_mcp.search import find as find_catalog
from redfox_cloud_mcp.wrap import CALL_SOURCE, envelope, run_task, sdk_raw

mcp = create_server("红狐数据(云市场)", __version__)
mcp.instructions = instructions()


class _WrapErrors(Middleware):
    """参数校验等异常在进工具函数前就抛出，这里兜底包成统一信封。"""

    async def on_call_tool(self, context, call_next):
        try:
            return await call_next(context)
        except FastMCPValidationError:
            return envelope(400, {"message": "参数不合法：capability 与取值必须来自 call 的列表"})
        except Exception as e:  # noqa: BLE001 - 任何未预期异常都要包成失败信封
            return envelope(500, {"message": str(e)})


mcp.add_middleware(_WrapErrors())


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
    fn.__annotations__["return"] = Any


def _method(path: str):
    def factory():
        obj = get_client()
        for part in path.split("."):
            obj = getattr(obj, part)
        return obj

    return factory


_FIND = find_param_descriptions()


def find(
    query: Annotated[str, Field(description=_FIND["query"])] = "",
    platform: Annotated[str, Field(description=_FIND["platform"])] = "",
    category: Annotated[str, Field(description=_FIND["category"])] = "",
) -> Any:
    result = find_catalog(query=query, platform=platform, category=category)
    if "error" in result:
        return envelope(400, result)
    return envelope(2000, result)


find.__doc__ = find_tool_description()
mcp.tool()(find)


def describe(ids: list[str]) -> Any:
    """读取 1 到 10 个已开放能力的参数、必填项、是否异步，以及一条示例调用。

    ids 只能用 call 列出的编号。参数名能从 call 上看懂时可以不调用；取值、多选一或是否异步不确定时再调用。
    """
    if not isinstance(ids, list) or any(not isinstance(item, str) for item in ids):
        result = {"error": "invalid_argument", "message": "ids 必须是字符串数组"}
    elif len(ids) > DESCRIBE_LIMIT:
        result = {"error": "invalid_argument", "message": f"一次最多描述 {DESCRIBE_LIMIT} 个能力"}
    else:
        result = describe_catalog(ids)
    if "error" in result:
        return envelope(400, result)
    return envelope(2000, result)


describe.__annotations__["ids"] = Annotated[
    list[Capability],
    Field(description="能力编号，1 到 10 个，取 call 的 capability 列表里的值"),
]
mcp.tool()(describe)


def call(capability: str, **kwargs: Any) -> Any:
    """调用一个已开放的能力。capability 用列表中的编号；列表里有就直接调用，不要先 find。

    只填这个能力自己的参数，参数名和含义写在下面。取值或是否必填不确定时先 describe。编号不存在或参数不合法时不会请求上游。
    异步能力超时返回 taskId，再用 result 查询。榜单分类（体育、美食等）填 type。
    """
    arguments = {key: value for key, value in kwargs.items() if value is not None}
    prepared = prepare(capability, arguments)
    if isinstance(prepared, dict):
        return envelope(400, prepared)
    item, payload, timeout = prepared
    payload["source"] = CALL_SOURCE
    if item["kind"] == "async":
        code, res = run_task(_method(item["sdk"]), _method(item["result"]), int(timeout or 240), **payload)
    elif item["kind"] == "upload":
        path = payload.pop("file", None)
        try:
            handle = open(path, "rb")
        except OSError as exc:
            return envelope(400, {"message": f"无法读取本地文件 {path}：{exc}"})
        with handle:
            payload["file"] = handle
            code, res = sdk_raw(_method(item["sdk"]), **payload)
    else:
        code, res = sdk_raw(_method(item["sdk"]), **payload)
    return envelope(code, res)


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


def result(capability: str, task_id: str) -> Any:
    """查询异步任务。capability 用当时 call 的同一个编号，task_id 用返回里的 taskId。

    当前会超时并返回 taskId 的是各平台视频文案提取。
    """
    item = by_id().get(capability)
    if item is None or item["kind"] != "async" or not item.get("result"):
        return envelope(400, {"message": "这个能力不是异步任务或编号不存在", "capability": capability})
    code, res = sdk_raw(_method(item["result"]), task_id=task_id, source=CALL_SOURCE)
    return envelope(code, res)


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
    serve(mcp, prog="redfox-cloud-mcp", description="RedFox 云市场 MCP：find / describe / call / result")


if __name__ == "__main__":
    main()
