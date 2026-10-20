"""RedFox 数据 MCP：find、describe、call、result。

能力执行沿用各平台 server 里同一条 SDK 调用。本服务不注册那 100 多个工具。
鉴权和业务日志走 redfox-mcp-core：HTTP 模式由前置 API Key 中间件拦截，
真正打到 SDK 的调用经 call() 打 mcp_call。
"""

from __future__ import annotations

import json
from typing import Any, Optional

from redfox_mcp_core import create_server, serve
from redfox_mcp_core.runtime import _emit

from redfox_data_mcp import __version__
from redfox_data_mcp.dispatch import invoke, query_result
from redfox_data_mcp.search import FIND_LIMIT, describe as describe_catalog
from redfox_data_mcp.search import find as find_catalog

INSTRUCTIONS = (
    "RedFox 公开数据与工具，只通过 4 个工具使用：find、describe、call、result。"
    "能力编号形如 douyin.search.articles。"
    "编号不确定时用 find（最多 10 条，按词匹配）。find 没有匹配就告诉用户目录里没有，不要改用别的平台。"
    "参数不确定时用 describe。call 一次只调一个能力。"
    "异步能力超时会返回 taskId，再用 result，传入同一个能力编号和 task_id。"
    "上传类能力的 file 是服务端本地路径。"
)

mcp = create_server("redfox-data", __version__)
mcp.instructions = INSTRUCTIONS


def _arguments(value: Any) -> dict[str, Any] | tuple[dict[str, Any], None]:
    if value is None or value == "":
        return {}
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except json.JSONDecodeError:
            return {"error": "invalid_argument", "message": "arguments 不是合法 JSON"}, None
    if not isinstance(value, dict):
        return {"error": "invalid_argument", "message": "arguments 必须是对象"}, None
    return value


@mcp.tool()
def find(query: str = "", platform: str = "", category: str = "") -> dict[str, Any]:
    """用一句话找能力。中英文都可以，最多返回 10 条，附带必填参数和一条示例调用。

    query 例如「抖音热门作品」「kimi 联网搜索」。platform 可写 douyin、抖音、小红书。
    category 可写 social、auto、ai、tools。没有匹配时 matches 为空；点了名的平台会在 nearest 列出它有的能力，那些不能拿来顶替调用。
    """
    result = find_catalog(query=query, platform=platform, category=category)
    _emit(
        "mcp_call",
        tool="find",
        arguments={"query": query, "platform": platform, "category": category},
        ok="error" not in result,
        result={"matches": [m["id"] for m in result.get("matches") or []], "unknown": result.get("unknown"), "error": result.get("error")},
    )
    return result


@mcp.tool()
def describe(ids: list[str]) -> dict[str, Any]:
    """读取 1 到 10 个能力的参数、必填项、是否异步，以及一条示例调用。调用前参数不清楚时用它。"""
    if not isinstance(ids, list) or any(not isinstance(item, str) for item in ids):
        result = {"error": "invalid_argument", "message": "ids 必须是字符串数组"}
    elif len(ids) > FIND_LIMIT:
        result = {"error": "invalid_argument", "message": f"一次最多描述 {FIND_LIMIT} 个能力"}
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


@mcp.tool()
def call(capability: str, arguments: Optional[dict[str, Any]] = None) -> dict[str, Any]:
    """调用一个能力。capability 是 find 或 describe 给出的编号，arguments 只放这个能力自己的参数。

    异步能力会先等待；超时返回 taskId，再用 result 查询。参数缺失或编号不存在时不会请求上游。
    """
    parsed = _arguments(arguments)
    if isinstance(parsed, tuple):
        return parsed[0]
    return invoke(capability, parsed)


@mcp.tool()
def result(capability: str, task_id: str) -> dict[str, Any]:
    """查询异步任务。capability 用当时 call 的同一个编号，task_id 用返回里的 taskId。只对会超时返回 taskId 的能力有效。"""
    return query_result(capability, task_id)


def main() -> None:
    serve(mcp, prog="redfox-data-mcp", description="RedFox 数据 MCP：find / describe / call / result")


if __name__ == "__main__":
    main()
