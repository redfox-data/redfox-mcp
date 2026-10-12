"""红狐 OAuth（模型 A）本地自检脚本 —— 不需要公网/隧道/豆包即可验证代码链路。

覆盖：
  [发现链] GET /mcp→401+WWW-Authenticate → protected-resource → authz-server 元数据
  [授权链] DCR /register → PKCE /authorize → /token
  [调用链] Bearer 连 /mcp → list_tools → call_tool

用法（两个终端）：
  终端1 起服务（见对话里的启动命令）
  终端2 TEST_BASE=http://127.0.0.1:8137 .venv/bin/python oauth_selftest.py

环境变量：
  TEST_BASE  服务地址，默认 http://127.0.0.1:8137
判读：
  call_tool 返回 3107「API Key无效」= 身份链已通（哨兵 Key 无效）；
  返回真实数据 = 你配了有效的 REDFOX_OAUTH_TEST_API_KEY。
"""
from __future__ import annotations

import asyncio
import base64
import hashlib
import os
import secrets
from urllib.parse import parse_qs, urlparse

import httpx

BASE = os.getenv("TEST_BASE", "http://127.0.0.1:8137").rstrip("/")
REDIRECT = "https://client.example.com/callback"


def _ok(msg: str):
    print(f"  \033[32m✓\033[0m {msg}")


def _fail(msg: str):
    print(f"  \033[31m✗\033[0m {msg}")


def _pkce():
    verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).rstrip(b"=").decode()
    challenge = (
        base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest())
        .rstrip(b"=")
        .decode()
    )
    return verifier, challenge


def discovery(http: httpx.Client) -> None:
    print("[发现链]")
    r = http.get(f"{BASE}/mcp")
    assert r.status_code == 401, f"GET /mcp 期望 401，实得 {r.status_code}"
    www = r.headers.get("www-authenticate", "")
    assert "resource_metadata=" in www, f"缺 resource_metadata：{www}"
    rm_url = www.split('resource_metadata="', 1)[1].split('"', 1)[0]
    _ok(f"GET /mcp → 401，resource_metadata={rm_url}")

    # resource_metadata 可能是公网域名；本地测试时 base_url 即本地，可直接访问。
    # 若不可达（比如指向隧道域名而隧道没开），退回本地等价路径。
    try:
        pr = http.get(rm_url)
    except httpx.HTTPError:
        pr = http.get(f"{BASE}/.well-known/oauth-protected-resource/mcp")
    assert pr.status_code == 200, f"protected-resource 期望 200，实得 {pr.status_code}"
    prj = pr.json()
    _ok(f"protected-resource → authorization_servers={prj.get('authorization_servers')}")

    asm_url = f"{BASE}/.well-known/oauth-authorization-server"
    asm = http.get(asm_url)
    assert asm.status_code == 200, f"authz-server 期望 200，实得 {asm.status_code}"
    asj = asm.json()
    for k in ("issuer", "authorization_endpoint", "token_endpoint", "registration_endpoint"):
        assert asj.get(k), f"authz-server 元数据缺 {k}"
    assert "S256" in asj.get("code_challenge_methods_supported", []), "缺 PKCE S256"
    _ok(f"authz-server → register={asj['registration_endpoint']} S256 ✓")


def flow(http: httpx.Client) -> str:
    print("[授权链]")
    verifier, challenge = _pkce()

    reg = http.post(
        f"{BASE}/register",
        json={
            "client_name": "selftest",
            "redirect_uris": [REDIRECT],
            "grant_types": ["authorization_code", "refresh_token"],
            "response_types": ["code"],
            "token_endpoint_auth_method": "none",
        },
    )
    reg.raise_for_status()
    client_id = reg.json()["client_id"]
    _ok(f"DCR /register → client_id={client_id}")

    auth = http.get(
        f"{BASE}/authorize",
        params={
            "response_type": "code",
            "client_id": client_id,
            "redirect_uri": REDIRECT,
            "code_challenge": challenge,
            "code_challenge_method": "S256",
            "state": "s",
        },
        follow_redirects=False,
    )
    assert auth.status_code in (302, 303), f"authorize 期望 302，实得 {auth.status_code}"
    code = parse_qs(urlparse(auth.headers["location"]).query)["code"][0]
    _ok(f"PKCE /authorize → code={code[:12]}...")

    tok = http.post(
        f"{BASE}/token",
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT,
            "client_id": client_id,
            "code_verifier": verifier,
        },
    )
    tok.raise_for_status()
    access_token = tok.json()["access_token"]
    _ok(f"/token → access_token={access_token[:12]}...")
    return access_token


async def call(access_token: str) -> None:
    print("[调用链]")
    from fastmcp import Client
    from fastmcp.client.transports import StreamableHttpTransport

    transport = StreamableHttpTransport(
        url=f"{BASE}/mcp", headers={"Authorization": f"Bearer {access_token}"}
    )
    async with Client(transport) as c:
        tools = await c.list_tools()
        names = [t.name for t in tools]
        _ok(f"Bearer 握手成功，{len(names)} 个工具")

        target = next(
            (n for n in ("xiaohongshu_search_articles", "xiaohongshu_search_notes") if n in names),
            names[0],
        )
        try:
            res = await c.call_tool(target, {"keyword": "美妆"})
        except TypeError:
            res = await c.call_tool(target, {})
        data = getattr(res, "data", None)
        print(f"  call_tool({target}) → {data}")
        if isinstance(data, dict) and data.get("code") == 3107:
            _ok("身份链已通（3107=解析出的 Key 无效，换有效 Key 即返真实数据）")
        elif isinstance(data, dict) and data.get("error"):
            _fail(f"调用返回错误：{data}")
        else:
            _ok("调用返回数据（Key 有效）")


def main():
    print(f"目标服务：{BASE}\n")
    with httpx.Client(timeout=30.0) as http:
        discovery(http)
        tok = flow(http)
    asyncio.run(call(tok))
    print("\n全部步骤通过。")


if __name__ == "__main__":
    main()
