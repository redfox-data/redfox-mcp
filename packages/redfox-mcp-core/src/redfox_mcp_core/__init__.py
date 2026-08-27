"""RedFox MCP 共享基础设施 — 各平台 MCP server 的统一运行时与启动入口"""

from redfox_mcp_core.runtime import (
    API_KEY_GUIDE,
    API_KEY_GUIDE_HTTP,
    TASK_PENDING_MSG,
    call,
    get_client,
    is_done,
    poll,
    run_task,
    set_transport,
)
from redfox_mcp_core.server import create_server, serve

__all__ = [
    "API_KEY_GUIDE",
    "API_KEY_GUIDE_HTTP",
    "TASK_PENDING_MSG",
    "call",
    "get_client",
    "is_done",
    "poll",
    "run_task",
    "set_transport",
    "create_server",
    "serve",
]
