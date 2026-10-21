"""HTTP 调用时解析红狐 API Key。

OAuth 请求用 access token 里的 user_id 向账号侧换 Key。
没有 OAuth 身份时，沿用 core 从请求头读取 API Key 的路径。
"""

from __future__ import annotations

from typing import Any, Optional

from redfox import RedFoxClient
from redfox_mcp_core import get_client as core_get_client

try:
    from fastmcp.server.dependencies import get_access_token
except ImportError:
    get_access_token = None


def _user_id(token: Any) -> Optional[str]:
    claims = getattr(token, "claims", None)
    if isinstance(claims, dict):
        uid = claims.get("redfox_user_id")
        if uid:
            return str(uid)
    subject = getattr(token, "subject", None)
    return str(subject) if subject else None


def get_client() -> RedFoxClient:
    token = None
    if get_access_token is not None:
        try:
            token = get_access_token()
        except Exception:
            token = None
    user_id = _user_id(token)
    if user_id:
        from redfox_data_mcp.oauth import resolve_api_key

        key = resolve_api_key(user_id)
        if not key:
            raise ValueError("missing API key (OAuth subject unresolved)")
        return RedFoxClient(api_key=key)
    return core_get_client()
