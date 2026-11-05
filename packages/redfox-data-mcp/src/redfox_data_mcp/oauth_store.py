"""OAuth 状态远端存储：调 Java 后台 /story/web/mcpOauth/state/* 接口。

函数计算多实例 + 内存随时清空，动态客户端、同意页事务、授权码、令牌必须落库。
MCP 不直连数据库，由账号侧后台提供存取接口，本模块只负责调用。

五类数据共用一张表，key 由本模块加前缀：
  client:{client_id}    不过期，长期保留
  txn:{txn_id}          +10 分钟
  code:{code}           +5 分钟，取走即删（take 一次有效）
  access:{token}        +1 小时
  refresh:{token}       不过期

需要环境变量：
  REDFOX_OAUTH_STATE_SECRET      共享密钥（必填），请求头 X-Mcp-Oauth-Secret
  REDFOX_OAUTH_STATE_BASE_URL    后台地址，默认 https://redfox.hk
"""

from __future__ import annotations

import json
import os
import time
from typing import Any, Dict, Optional

import httpx

KIND_CLIENT = "client"
KIND_TXN = "txn"
KIND_CODE = "code"
KIND_ACCESS = "access"
KIND_REFRESH = "refresh"

# 与文档约定一致：None 表示不过期
_KIND_TTL_SECONDS: Dict[str, Optional[int]] = {
    KIND_CLIENT: None,
    KIND_TXN: 10 * 60,
    KIND_CODE: 5 * 60,
    KIND_ACCESS: 60 * 60,
    KIND_REFRESH: None,
}

_STATE_PATH = "/story/web/mcpOauth/state"

_DEFAULT_BASE_URL = "https://redfox.hk"

# HTTP 层成功状态码
_HTTP_OK = 200

# Java 后台 Result.success() 的信封 code 是 2000（ReturnInfoEnum.Success）
_ENVELOPE_OK_CODE = 2000


class OAuthStateStoreError(RuntimeError):
    """远端状态存储调用失败。"""


class HttpOAuthStateStore:
    """按 kind+key 在后台表里存取 JSON payload，原样写入、原样返回。"""

    def __init__(self, base_url: str, secret: str, timeout: float = 10.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._secret = secret
        self._timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None

    def _get_client(self) -> httpx.AsyncClient:
        # 惰性创建：首次调用发生在事件循环内，避免跨循环绑定问题
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self._timeout)
        return self._client

    def _url(self, op: str) -> str:
        return f"{self._base_url}{_STATE_PATH}/{op}"

    async def _call(self, op: str, body: Dict[str, Any]) -> Optional[str]:
        """调一个状态接口，成功返回 payload 字符串；记录不存在返回 None。"""
        try:
            response = await self._get_client().post(
                self._url(op),
                json=body,
                headers={"X-Mcp-Oauth-Secret": self._secret},
            )
        except Exception as exc:
            raise OAuthStateStoreError(f"状态接口 {op} 调用失败: {exc}") from exc
        if response.status_code != _HTTP_OK:
            raise OAuthStateStoreError(f"状态接口 {op} HTTP {response.status_code}")
        try:
            envelope = response.json()
        except ValueError as exc:
            raise OAuthStateStoreError(f"状态接口 {op} 响应不是 JSON") from exc
        if not isinstance(envelope, dict) or envelope.get("code") != _ENVELOPE_OK_CODE:
            raise OAuthStateStoreError(
                f"状态接口 {op} 返回 code={envelope.get('code')} msg={envelope.get('msg')}"
            )
        data = envelope.get("data")
        if data is None:
            return None
        if isinstance(data, dict):
            return data.get("payload")
        return None

    async def put(
        self, kind: str, key: str, payload: Dict[str, Any], expires_in: Optional[int] = None
    ) -> None:
        """插入或覆盖。expires_in 为 None 时不过期，否则按 kind 默认 TTL。"""
        ttl = _KIND_TTL_SECONDS[kind] if expires_in is None else expires_in
        expires_at = int(time.time()) + ttl if ttl is not None else None
        await self._call(
            "save",
            {
                "key": f"{kind}:{key}",
                "kind": kind,
                "payload": json.dumps(payload, ensure_ascii=False),
                "expiresAt": expires_at,
            },
        )

    async def _read(self, op: str, kind: str, key: str) -> Optional[Dict[str, Any]]:
        # Java 侧按键读取的请求体只认 key，kind 已编码在 key 前缀里
        raw = await self._call(op, {"key": f"{kind}:{key}"})
        if raw is None:
            return None
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise OAuthStateStoreError(f"状态接口 {op} payload 不是合法 JSON") from exc
        if not isinstance(data, dict):
            raise OAuthStateStoreError(f"状态接口 {op} payload 不是 JSON 对象")
        return data

    async def get(self, kind: str, key: str) -> Optional[Dict[str, Any]]:
        """读取，不删除。过期记录由后台删掉并返回 None。"""
        return await self._read("get", kind, key)

    async def take(self, kind: str, key: str) -> Optional[Dict[str, Any]]:
        """读出并删除，一次有效。并发第二个取到 None。"""
        return await self._read("take", kind, key)

    async def delete(self, kind: str, key: str) -> None:
        await self._call("delete", {"key": f"{kind}:{key}"})


def build_state_store() -> HttpOAuthStateStore:
    """按环境变量构造远端状态存储，密钥缺失直接失败。"""
    secret = os.getenv("REDFOX_OAUTH_STATE_SECRET", "").strip()
    if not secret:
        raise RuntimeError(
            "缺少环境变量 REDFOX_OAUTH_STATE_SECRET（OAuth 状态远端存储共享密钥）"
        )
    base_url = os.getenv("REDFOX_OAUTH_STATE_BASE_URL", "").strip() or _DEFAULT_BASE_URL
    return HttpOAuthStateStore(base_url=base_url, secret=secret)
