"""RedFox AI 搜索 MCP Server

将 RedFoxHub（红狐数据平台）的 AI 搜索能力（Kimi/豆包/Deepseek）暴露为 MCP 工具，
提交后自动轮询等待结果，超时返回 taskId 供 result 工具补查。

认证：stdio 模式读环境变量 REDFOX_API_KEY；HTTP 模式从请求头
X-API-Key（或 Authorization: Bearer <key>）取 key。
获取地址 https://redfox.hk/settings/api-keys?source=mcp
"""

from typing import Any, Dict

from redfox_mcp_core import call, create_server, get_client, run_task, serve

from redfox_ai_search_mcp import __version__

mcp = create_server("redfox-ai-search", __version__)


@mcp.tool()
def ai_search_kimi(inquiry_text: str, timeout_seconds: int = 240) -> Dict[str, Any]:
    """Kimi 联网 AI 搜索，提交后自动等待并返回完整结果（含 content/webPages）。
    inquiry_text 为搜索提问文本；超时未完成时返回 taskId，可用 ai_search_kimi_result 再查。"""
    return run_task(lambda: get_client().ai_search.kimi_submit,
                    lambda: get_client().ai_search.kimi_result,
                    timeout_seconds, inquiry_text=inquiry_text)


@mcp.tool()
def ai_search_doubao(inquiry_text: str, timeout_seconds: int = 240) -> Dict[str, Any]:
    """豆包联网 AI 搜索，提交后自动等待并返回完整结果。
    inquiry_text 为搜索提问文本；超时未完成时返回 taskId，可用 ai_search_doubao_result 再查。"""
    return run_task(lambda: get_client().ai_search.doubao_submit,
                    lambda: get_client().ai_search.doubao_result,
                    timeout_seconds, inquiry_text=inquiry_text)


@mcp.tool()
def ai_search_deepseek(inquiry_text: str, timeout_seconds: int = 240) -> Dict[str, Any]:
    """Deepseek 联网 AI 搜索，提交后自动等待并返回完整结果。
    inquiry_text 为搜索提问文本；超时未完成时返回 taskId，可用 ai_search_deepseek_result 再查。"""
    return run_task(lambda: get_client().ai_search.deepseek_submit,
                    lambda: get_client().ai_search.deepseek_result,
                    timeout_seconds, inquiry_text=inquiry_text)


@mcp.tool()
def ai_search_kimi_result(task_id: str) -> Dict[str, Any]:
    """查询 Kimi 搜索任务结果。仅在 ai_search_kimi 超时返回 taskId 后使用。"""
    return call(lambda: get_client().ai_search.kimi_result, task_id=task_id)


@mcp.tool()
def ai_search_doubao_result(task_id: str) -> Dict[str, Any]:
    """查询豆包搜索任务结果。仅在 ai_search_doubao 超时返回 taskId 后使用。"""
    return call(lambda: get_client().ai_search.doubao_result, task_id=task_id)


@mcp.tool()
def ai_search_deepseek_result(task_id: str) -> Dict[str, Any]:
    """查询 Deepseek 搜索任务结果。仅在 ai_search_deepseek 超时返回 taskId 后使用。"""
    return call(lambda: get_client().ai_search.deepseek_result, task_id=task_id)


def main() -> None:
    serve(mcp, prog="redfox-ai-search-mcp", description="RedFox AI 搜索 MCP server")


if __name__ == "__main__":
    main()
