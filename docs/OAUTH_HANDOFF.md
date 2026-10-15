# OAuth DCR 试点接手任务书：红狐前端登录/同意页 + MCP 协议 + 豆包接入

> 本文件面向**接手此任务的同事 / AI Agent**。读完即可自主完成「登录/同意页（红狐前端 JS）+ MCP OAuth 协议接线 + 部署联调」。
> 凡 `<...>` 均为占位符，需向人类索取真实值；**缺任一项就停下来问，不要假设**。
> 协议层（DCR / PKCE / token / 发现链）已在 `feat/oauth-dcr` 分支实现并本地验证，**不要改协议逻辑**；本任务书聚焦「登录/同意页接线 + 部署联调」。

## 0. 架构分工（四方）

| 角色                | 技术栈                          | 职责                                                                      |
| ------------------- | ------------------------------- | ------------------------------------------------------------------------- |
| 豆包 OAuth 客户端   | 第三方                          | 发起 DCR / PKCE / 换 token / 带 Bearer 调 MCP                             |
| 红狐前端            | **JS**（redfox.hk）             | 登录页 + 同意页 + 调红狐后端验登录 + 点同意拿 ticket 跳回 MCP             |
| 红狐后端            | 账号系统                        | 登录 API / session 验证 / ticket 签发与验证 / `GET /story/web/apiKey/queryKey?uuid={ticket}` |
| MCP 资源+授权服务器 | Python/fastmcp（mcp.redfox.hk） | OAuth 协议端点 + `/oauth/resume` 回调（验 ticket + 发 code + 302 回豆包） |

**关键约定**：登录页/同意页在**红狐前端 JS**（redfox.hk 域名，天然读红狐 cookie），**不在 MCP**；MCP 不碰账号密码，只接收红狐前端回调传过来的一次性 ticket 换 user_id。

## 1. 完整流程（每一步 URL）

1. 豆包 → `GET https://mcp.redfox.hk/authorize?response_type=code&client_id={cid}&redirect_uri={cb}&state={S}&code_challenge={CC}&code_challenge_method=S256&scope={scope}`
2. MCP：生成 `txn_id` 暂存原始参数 → `302` 到红狐前端 → `GET https://redfox.hk/oauth/consent?txn_id={T}`
3. 红狐前端（JS）读红狐 cookie：已登录 → 渲染同意页（只有授权按钮）；未登录 → 渲染登录页 → 调红狐后端登录 API → 成功后渲染同意页
4. 用户点[同意授权] → 红狐前端调红狐后端拿一次性 ticket → 浏览器跳回 MCP → `GET https://mcp.redfox.hk/oauth/resume?txn_id={T}&ticket={ticket}`（点[拒绝] → `.../oauth/resume?txn_id={T}&consent=deny`）
5. MCP `/oauth/resume`：验 ticket 换 user_id → 发 code（含 code_challenge）→ `302` 回豆包 → `GET {cb}?code={code}&state={S}`
6. 浏览器跟随 302 → 豆包回调端点收 code+state（**豆包自己实现，我们不做**）
7. 豆包 → `POST https://mcp.redfox.hk/token`（code+client_id+redirect_uri+code_verifier）→ access_token+refresh_token（已实现）
8. 豆包 → `https://mcp.redfox.hk/mcp` 带 `Authorization: Bearer access_token` → MCP 验 token → `claims.redfox_user_id`（即 ticket）→ `GET https://redfox.hk/story/web/apiKey/queryKey?uuid={ticket}` → 调数据（已实现）

## 2. 红狐前端（JS）要做的

新增页面 `https://redfox.hk/oauth/consent`（读 query 的 `txn_id`）。示例为框架无关原生 JS，按你们前端框架（React/Vue）改造：

```html
<!-- https://redfox.hk/oauth/consent?txn_id={T} -->
<form id="loginForm" hidden>
  <input name="username" placeholder="红狐账号" />
  <input type="password" name="password" placeholder="密码" />
  <button type="submit">登录</button>
</form>
<div id="consentBox" hidden>
  <p>红狐账号 <span id="uname"></span> 授权豆包访问你的小红书数据</p>
  <button id="approve">同意授权</button>
  <button id="deny">拒绝</button>
</div>
<script>
  const txn = new URLSearchParams(location.search).get("txn_id");
  const MCP_RESUME = "https://mcp.redfox.hk/oauth/resume";

  // 1) 读红狐登录态（同域 cookie 自动带上）；未登录则显示登录表单
  fetch("/api/session", { credentials: "include" })
    .then((r) => (r.ok ? r.json() : Promise.reject()))
    .then(({ user_id, username }) => showConsent(user_id, username))
    .catch(() => {
      document.getElementById("loginForm").hidden = false;
    });

  function showConsent(uid, name) {
    document.getElementById("uname").textContent = name;
    document.getElementById("consentBox").hidden = false;
  }

  // 2) 未登录：密码只发给红狐后端 /api/login（绝不发给 MCP）
  document.getElementById("loginForm").onsubmit = async (e) => {
    e.preventDefault();
    const r = await fetch("/api/login", {
      method: "POST",
      credentials: "include",
      body: new FormData(e.target),
    });
    if (!r.ok) return alert("账号或密码错误");
    const { user_id, username } = await r.json();
    showConsent(user_id, username);
  };

  // 3) 点同意：拿一次性 ticket，跳回 MCP 回调
  document.getElementById("approve").onclick = async () => {
    const r = await fetch("/api/oauth/ticket", {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ txn_id: txn }),
    });
    const { ticket } = await r.json();
    location.href = `${MCP_RESUME}?txn_id=${txn}&ticket=${ticket}`;
  };
  document.getElementById("deny").onclick = () => {
    location.href = `${MCP_RESUME}?txn_id=${txn}&consent=deny`;
  };
</script>
```

要点：登录态用 `GET /api/session`（credentials:include）；登录用 `POST /api/login`（种 cookie）；同意用 `POST /api/oauth/ticket` 拿一次性 ticket 后 `location.href` 跳回 MCP。**密码只到红狐后端，不过 MCP。**

## 3. MCP（Python）要做的

- `/authorize` 改造：`RedFoxOAuthProvider.authorize()` 不再直接 `super().authorize()` 发码；改为生成 `txn_id` 暂存原始参数后，返回红狐前端 URL（fastmcp 会 302 到它）。
- 新增 `/oauth/resume` 回调端点（验 ticket + 发 code + 302 回豆包）：

```python
# oauth_resume.py —— 挂到 fastmcp HTTP app 的自定义路由
import secrets, time
from mcp.server.auth.provider import AuthorizationCode

_TXN: dict = {}  # txn_id -> 原始 authorize params（生产落持久化）
REDFOX_TICKET_VERIFY = "<红狐后端验ticket接口>"  # 占位，等红狐后端文档

async def redfox_verify_ticket(ticket: str):
    """调红狐后端验一次性 ticket 换 user_id（占位，等接口文档）。"""
    ...

async def oauth_resume(request, provider):
    q = request.query_params
    p = _TXN.get(q.get("txn_id", ""), {})
    if q.get("consent") == "deny" or not p:
        return Redirect(f"{p.get('redirect_uri')}?error=access_denied&state={p.get('state')}")
    uid = await redfox_verify_ticket(q.get("ticket", ""))
    if not uid:
        return Redirect(f"{p['redirect_uri']}?error=access_denied&state={p['state']}")
    code = f"code_{secrets.token_hex(16)}"
    # 手动构造 AuthorizationCode（含 code_challenge），复用 fastmcp /token 的 PKCE 校验
    provider.auth_codes[code] = AuthorizationCode(
        code=code, client_id=p["client_id"], redirect_uri=p["redirect_uri"],
        scopes=p.get("scopes", []), expires_at=time.time() + 300,
        code_challenge=p["code_challenge"])
    provider._code_to_user[code] = uid   # 复用现有身份绑定（claims.redfox_user_id）
    return Redirect(f"{p['redirect_uri']}?code={code}&state={p['state']}")
```

## 4. 红狐后端要做的（接口清单，等文档）

- `POST /api/login`：账号密码 → user_id，种红狐 cookie
- `GET /api/session`：cookie → user_id（前端读登录态）
- `POST /api/oauth/ticket`：session + txn_id → 一次性 ticket（前端点同意时调）
- ticket 验证接口：ticket → user_id（MCP `/oauth/resume` 调用）
- `GET https://redfox.hk/story/web/apiKey/queryKey?uuid={ticket}` → 红狐 API Key（MCP 调数据用；`uuid` 用同意回调里的 ticket）

## 5. FC 部署（同事）

- 镜像含 `feat/oauth-dcr` 代码：发 PyPI 测试版（Dockerfile 现成 pip install）或本地 build 推 ACR，二选一
- 新建**独立测试函数**（不动生产），环境变量：`REDFOX_MCP_AUTH_MODE=oauth`、`REDFOX_MCP_OAUTH_BASE_URL=https://<测试子域名>`、`REDFOX_OAUTH_STUB_USER_ID=<测试用户>`、`REDFOX_OAUTH_TEST_API_KEY=<有效Key>`
- **预留实例=1 + 单实例**（InMemory 调试期保持状态；生产必须持久化，见§6）
- 域名：FC 自定义域名加独立测试子域名（如 `oauth-test.redfox.hk`）走根路径 `/mcp`，避开 path prefix 的 well-known 坑
- SSE/超时：复用现有 streamable-http 触发器配置（FC 3.0 已验证稳定）

## 6. 持久化（生产前置，FC 架构必需）

`_TXN`、`auth_codes`、`clients`、`access_tokens`、`refresh_tokens` 落跨实例共享存储（Tablestore / 云数据库 Redis / RDS）。FC 默认按量实例多实例+冷启动，InMemory 跨请求必丢状态（register 在实例 A、token 在实例 B 即失败）。调试期用预留实例=1 临时规避，生产必须落库。

## 7. 已知坑（勿踩）

1. cloudflared quick tunnel 对 GET SSE 不实时流（#1449），别用；FC 自身 SSE 已验证可用。
2. `claims` 承载 user_id（fastmcp `get_access_token()` 丢 subject），别改。
3. `ClientRegistrationOptions(enabled=True)` 别去掉，否则 /register 不挂载。
4. MCP 不读红狐 cookie（跨域），靠红狐前端回调的一次性 ticket 传身份。
5. 密码只到红狐后端 `/api/login`，绝不过 MCP。
6. FC 预留实例/持久化见 §5/§6。

## 8. 后续准备清单（向人类索取）

- [ ] 红狐后端 5 个接口（§4）的地址/文档/凭证
- [ ] 持久化存储选型（Tablestore / Redis / RDS）+ 连接信息
- [ ] FC 部署信息：s.yaml / ACR 地址 / 测试子域名 / 预留实例配置
- [ ] PyPI 版本号 + 发布权限（若走发版路线）
- [ ] 一个有效红狐 API Key（stub 测试用）

## 9. 完成判据

- 红狐前端同意页/登录页跑通（已登录直接出授权按钮；未登录登录后出授权按钮）
- 点同意 → MCP `/oauth/resume` 发 code → 302 回豆包
- `TEST_BASE=https://<测试子域名> python oauth_selftest.py` 全绿
- 豆包工作真实完成 OAuth 授权 + 调用工具返回数据
