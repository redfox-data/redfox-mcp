"""RedFox AI 搜索 MCP Server

将 RedFoxHub（红狐数据平台）的 AI 搜索能力（Kimi/豆包/Deepseek/元宝/千问/百度）暴露为 MCP 工具，
提交即返回 taskId，结果由用户自行调用对应的 result 工具查询。

认证：stdio 模式读环境变量 REDFOX_API_KEY；HTTP 模式从请求头
REDFOX_API_KEY（或 Authorization: Bearer <key>）取 key。
获取地址 https://redfox.hk/settings/api-keys?source=mcp
"""

from typing import Any, Dict, Optional

from redfox_mcp_core import call, create_server, get_client, serve

from redfox_ai_search_mcp import __version__

mcp = create_server("redfox-ai-search", __version__)


@mcp.tool()
def ai_search_kimi(inquiry_text: str, timeout_seconds: Optional[int] = None) -> Dict[str, Any]:
    """提交 Kimi 联网 AI 搜索任务，立即返回 taskId，不自动查询结果。
    inquiry_text 为搜索提问文本。请稍后用 ai_search_kimi_result(task_id) 自行查询结果
    （含 content/webPages）。timeout_seconds 为可选参数，传与不传都不影响本调用。"""
    return call(lambda: get_client().ai_search.kimi_submit,
                inquiry_text=inquiry_text, source="Kimi 联网 AI 搜索-MCP")


@mcp.tool()
def ai_search_doubao(inquiry_text: str, timeout_seconds: Optional[int] = None) -> Dict[str, Any]:
    """提交豆包联网 AI 搜索任务，立即返回 taskId，不自动查询结果。
    inquiry_text 为搜索提问文本。请稍后用 ai_search_doubao_result(task_id) 自行查询结果。
    timeout_seconds 为可选参数，传与不传都不影响本调用。"""
    return call(lambda: get_client().ai_search.doubao_submit,
                inquiry_text=inquiry_text, source="豆包联网 AI 搜索-MCP")


@mcp.tool()
def ai_search_deepseek(inquiry_text: str, timeout_seconds: Optional[int] = None) -> Dict[str, Any]:
    """提交 Deepseek 联网 AI 搜索任务，立即返回 taskId，不自动查询结果。
    inquiry_text 为搜索提问文本。请稍后用 ai_search_deepseek_result(task_id) 自行查询结果。
    timeout_seconds 为可选参数，传与不传都不影响本调用。"""
    return call(lambda: get_client().ai_search.deepseek_submit,
                inquiry_text=inquiry_text, source="Deepseek 联网 AI 搜索-MCP")


@mcp.tool()
def ai_search_yuanbao(inquiry_text: str, timeout_seconds: Optional[int] = None) -> Dict[str, Any]:
    """提交元宝联网 AI 搜索任务，立即返回 taskId，不自动查询结果。
    inquiry_text 为搜索提问文本。请稍后用 ai_search_yuanbao_result(task_id) 自行查询结果。
    timeout_seconds 为可选参数，传与不传都不影响本调用。"""
    return call(lambda: get_client().ai_search.yuanbao_submit,
                inquiry_text=inquiry_text, source="元宝联网 AI 搜索-MCP")


@mcp.tool()
def ai_search_qianwen(inquiry_text: str, timeout_seconds: Optional[int] = None) -> Dict[str, Any]:
    """提交千问联网 AI 搜索任务，立即返回 taskId，不自动查询结果。
    inquiry_text 为搜索提问文本。请稍后用 ai_search_qianwen_result(task_id) 自行查询结果。
    timeout_seconds 为可选参数，传与不传都不影响本调用。"""
    return call(lambda: get_client().ai_search.qianwen_submit,
                inquiry_text=inquiry_text, source="千问联网 AI 搜索-MCP")


@mcp.tool()
def ai_search_baidu(inquiry_text: str, timeout_seconds: Optional[int] = None) -> Dict[str, Any]:
    """提交百度联网 AI 搜索任务，立即返回 taskId，不自动查询结果。
    inquiry_text 为搜索提问文本。请稍后用 ai_search_baidu_result(task_id) 自行查询结果。
    timeout_seconds 为可选参数，传与不传都不影响本调用。"""
    return call(lambda: get_client().ai_search.baidu_submit,
                inquiry_text=inquiry_text, source="百度联网 AI 搜索-MCP")


@mcp.tool()
def ai_search_kimi_result(task_id: str) -> Dict[str, Any]:
    """查询 Kimi 搜索任务结果（含 content/webPages）。传 ai_search_kimi 提交返回的 taskId。"""
    return call(lambda: get_client().ai_search.kimi_result, task_id=task_id, source="查询 Kimi 搜索任务结果-MCP")


@mcp.tool()
def ai_search_doubao_result(task_id: str) -> Dict[str, Any]:
    """查询豆包搜索任务结果。传 ai_search_doubao 提交返回的 taskId。"""
    return call(lambda: get_client().ai_search.doubao_result, task_id=task_id, source="查询豆包搜索任务结果-MCP")


@mcp.tool()
def ai_search_deepseek_result(task_id: str) -> Dict[str, Any]:
    """查询 Deepseek 搜索任务结果。传 ai_search_deepseek 提交返回的 taskId。"""
    return call(lambda: get_client().ai_search.deepseek_result, task_id=task_id, source="查询 Deepseek 搜索任务结果-MCP")


@mcp.tool()
def ai_search_yuanbao_result(task_id: str) -> Dict[str, Any]:
    """查询元宝搜索任务结果。传 ai_search_yuanbao 提交返回的 taskId。"""
    return call(lambda: get_client().ai_search.yuanbao_result, task_id=task_id, source="查询元宝搜索任务结果-MCP")


@mcp.tool()
def ai_search_qianwen_result(task_id: str) -> Dict[str, Any]:
    """查询千问搜索任务结果。传 ai_search_qianwen 提交返回的 taskId。"""
    return call(lambda: get_client().ai_search.qianwen_result, task_id=task_id, source="查询千问搜索任务结果-MCP")


@mcp.tool()
def ai_search_baidu_result(task_id: str) -> Dict[str, Any]:
    """查询百度搜索任务结果。传 ai_search_baidu 提交返回的 taskId。"""
    return call(lambda: get_client().ai_search.baidu_result, task_id=task_id, source="查询百度搜索任务结果-MCP")


def main() -> None:
    serve(mcp, prog="redfox-ai-search-mcp", description="RedFox AI 搜索 MCP server")


if __name__ == "__main__":
    main()
