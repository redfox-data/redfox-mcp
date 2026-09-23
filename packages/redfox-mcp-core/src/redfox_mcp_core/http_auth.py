"""HTTP 建连鉴权：无 API Key 不进入 MCP session；并记录 mcp_connect 日志。"""

from __future__ import annotations

from typing import Callable, Optional

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from redfox_mcp_core.runtime import (
    API_KEY_GUIDE_HTTP,
    api_key_from_headers,
    emit_mcp_connect,
    require_api_key_enabled,
)


def _is_health(path: str) -> bool:
    p = path.rstrip("/") or "/"
    return p == "/health" or p.endswith("/health")


def _session_id(headers) -> str:
    return (
        headers.get("mcp-session-id")
        or headers.get("Mcp-Session-Id")
        or ""
    )


class RequireApiKeyMiddleware(BaseHTTPMiddleware):
    """拦截 /mcp：无 Key 返回 401；新 session 打 mcp_connect。

    /health 放行。可用环境变量 REDFOX_MCP_REQUIRE_API_KEY=0 只记日志不拦截。
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if _is_health(request.url.path):
            return await call_next(request)

        key: Optional[str] = api_key_from_headers(request.headers)
        session_id = _session_id(request.headers)
        is_new_session = not session_id

        if not key:
            if require_api_key_enabled():
                emit_mcp_connect(
                    has_api_key=False,
                    api_key=None,
                    session_id=session_id or None,
                    rejected=True,
                    http_method=request.method,
                    path=request.url.path,
                )
                return JSONResponse(
                    {"error": "auth_failed", "message": API_KEY_GUIDE_HTTP},
                    status_code=401,
                )
            if is_new_session:
                emit_mcp_connect(
                    has_api_key=False,
                    api_key=None,
                    session_id=None,
                    rejected=False,
                    http_method=request.method,
                    path=request.url.path,
                )
            return await call_next(request)

        if is_new_session:
            emit_mcp_connect(
                has_api_key=True,
                api_key=key,
                session_id=None,
                rejected=False,
                http_method=request.method,
                path=request.url.path,
            )
        return await call_next(request)
