# OAuth DCR 试点：公网暴露与豆包接入 —— AI 执行任务书

> 本文件面向**接手此任务的 AI Agent**。读完即可自主完成「把 OAuth 模式 MCP 暴露到公网 HTTPS + 豆包工作接入验证」。
> 代码已完成并本地验证通过，**不要改代码逻辑**；你的工作是部署暴露 + 联调验证。
> 凡标注 `<...>` 的都是占位符，需向人类索取真实值；**缺任一项就停下来问，不要假设**。

## 任务目标

让豆包工作通过标准 OAuth DCR 连上 `feat/oauth-dcr` 分支的 OAuth 模式小红书 MCP（公网 HTTPS），完成授权并成功调用工具返回真实数据。

## 上下文（已验证事实，勿推翻）

- 分支 `feat/oauth-dcr`（commit `aa32a8a`）。改动：core 新增 OAuth 授权层，模型 A（OAuth token → user_id → 查用户既有红狐 API Key → 构造 RedFoxClient）。
- 环境变量 `REDFOX_MCP_AUTH_MODE` 默认 `apikey`（行为与改造前逐字节一致）；设 `oauth` 才启用新链路。
- **本地全链路已验证通过**：发现链 → DCR → PKCE → token → Bearer → call_tool。返回码判读：`3107` = 身份链通但 Key 无效；返回数据 = Key 有效。
- **cloudflared quick tunnel 不可用**：它对 `GET` 的 SSE 有已知缺陷（cloudflared issue #1449），MCP 客户端一开 SSE 就挂，豆包必然连不上（已实测踩坑）。**必须用服务器反代 + `proxy_buffering off`。**
- 测试期身份是 stub（固定 user_id + env 绑定 Key）；生产接真实登录/账号接口（见末节）。

## 第 0 步：向人类收集输入（缺任一项就停下问）

- [ ] 服务器 ssh：`<user@host>`，是否免密？（不免密则把隧道/配置命令交人类执行）
- [ ] 反代软件：nginx 还是 caddy？
- [ ] 域名 + 测试子域名（如 `<oauth-test.example.com>`）；DNS 能否加 A 记录指向服务器？
- [ ] TLS 证书：caddy 可自动签发；nginx 需已有证书或 certbot。
- [ ] 一个**有效**红狐 API Key（绑给 stub 用户）。
- [ ] OAuth 服务跑在哪：服务器本机 / 另一台 / 开发本地？（决定要不要 ssh 隧道）

## 第 1 步：起 OAuth 服务

在选定机器上（已 `git checkout feat/oauth-dcr`、依赖已装）：

```bash
REDFOX_MCP_AUTH_MODE=oauth \
REDFOX_MCP_OAUTH_BASE_URL=https://<测试子域名> \
REDFOX_OAUTH_STUB_USER_ID=u_doubao_test \
REDFOX_OAUTH_TEST_API_KEY=<有效红狐Key> \
python -m redfox_xiaohongshu_mcp --transport http --host 127.0.0.1 --port 8137 --path /mcp
```

环境变量说明：
- `REDFOX_MCP_OAUTH_BASE_URL`：**必须**是豆包能访问的公网 HTTPS，决定 well-known 发现文档里 authorize/token/register 各端点拼出的域名。填错豆包连不上。
- `REDFOX_OAUTH_STUB_USER_ID`：stub 固定用户 id。
- `REDFOX_OAUTH_TEST_API_KEY`：该用户绑定的红狐 Key（用**有效**的才能真调数据）。
- 可选：`REDFOX_MCP_OAUTH_ISSUER_URL`（默认 = base_url）、`REDFOX_MCP_OAUTH_RESOURCE_BASE_URL`、`REDFOX_OAUTH_USER_KEY_MAP`（JSON 多用户映射）。

**验证（本机）**：
```bash
curl -s http://127.0.0.1:8137/health
curl -s http://127.0.0.1:8137/.well-known/oauth-protected-resource/mcp
```
第二条应返回 JSON，其中 `resource` 字段 = 公网 base_url。

## 第 2 步：把服务暴露到公网（二选一）

### 2a. 服务跑在服务器本机（推荐，最简）
不需要隧道，反代直接 `proxy_pass http://127.0.0.1:8137`。跳到第 3 步。

### 2b. 服务跑在开发本地 / 另一台
建 ssh 反向隧道，把服务器端口映射到服务机器：
```bash
# 在「跑 OAuth 服务的机器」上执行，连到服务器：
ssh -R 18137:127.0.0.1:8137 <user@server>
# 保持此连接不断；服务器反代到 127.0.0.1:18137
```
（`ssh -R` 默认绑服务器 `127.0.0.1`，无需开 GatewayPorts。）

## 第 3 步：服务器反代配置（关键：SSE 不缓冲）

DNS：加 `<测试子域名>` 的 A 记录指向服务器公网 IP。

### nginx
```nginx
server {
  listen 443 ssl http2;
  server_name <测试子域名>;
  ssl_certificate     /path/to/cert.pem;
  ssl_certificate_key /path/to/key.pem;
  location / {
    proxy_pass http://127.0.0.1:8137;   # 2b 情况改为 18137
    proxy_http_version 1.1;
    proxy_set_header Connection "";
    proxy_buffering off;                 # 必须：SSE 不缓冲
    proxy_cache off;
    proxy_set_header X-Accel-Buffering no;
    proxy_read_timeout 3600s;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-Proto https;
  }
}
```

### caddy（自动 TLS，更省事）
```
<测试子域名> {
  reverse_proxy 127.0.0.1:8137 {   # 2b 情况改为 18137
    flush_interval -1              # 关键：SSE 不缓冲
  }
}
```

reload 反代后**验证公网发现链**：
```bash
curl -s https://<测试子域名>/.well-known/oauth-protected-resource/mcp
curl -s https://<测试子域名>/.well-known/oauth-authorization-server
```
两条都应返回 JSON，且端点域名都是公网子域名（含 `registration_endpoint`、`code_challenge_methods_supported` 带 `S256`）。

## 第 4 步：SSE 过隧道验证（避免重蹈 quick tunnel 覆辙）

```bash
TEST_BASE=https://<测试子域名> python oauth_selftest.py
```
**全绿**（发现链 / 授权链 / 调用链都 OK）才算公网链路真正可用。
若卡在 `call()` 报 `Client failed to connect`，多半是 SSE 被缓冲——回查第 3 步的 `proxy_buffering off` / `flush_interval -1`。

## 第 5 步：豆包工作接入

豆包工作 → 添加 MCP 服务：
- 类型：streamable-http（或「远程 MCP」）
- URL：`https://<测试子域名>/mcp`
- 鉴权：**选自动 OAuth 发现**（不要手动填 API Key）

添加后豆包应弹出 OAuth 授权页（stub 登录直接通过）→ 授权后加载工具列表 → 调用一个工具（如小红书搜索）。

**验证**：返回真实数据 = 全链路成功；返回 `3107` = 身份链通但 `REDFOX_OAUTH_TEST_API_KEY` 无效（换有效 Key 重启服务）。

## 已知坑（勿踩）

1. **quick tunnel SSE 缺陷**（cloudflared #1449）：别用 cloudflared quick tunnel，必须自己反代。
2. **`proxy_buffering off` / `flush_interval -1`**：SSE 必须不缓冲，否则 GET SSE 挂死。
3. **base_url 必须公网 HTTPS**：否则 well-known 发本地地址，豆包连不上。
4. **claims 承载 user_id**：fastmcp `get_access_token()` 会丢 `subject` 保 `claims`，代码已把 user_id 写进 `claims.redfox_user_id`——**别改这个逻辑**。
5. **DCR enabled**：`ClientRegistrationOptions(enabled=True)` 代码已设，别去掉，否则 `/register` 不挂载。

## 完成判据

- `oauth_selftest.py` 对公网地址全绿；
- 豆包工作能完成 OAuth 授权 + 调用工具返回真实数据。

## 后续：生产接入（非本任务范围）

`packages/redfox-mcp-core/src/redfox_mcp_core/oauth.py` 替换两处即可接真实账号，协议逻辑零改动：
- `_stub_user_id()` → 接红狐真实登录 / 用户身份；
- `EnvKeyResolver` → 接 `get_api_key_by_user`（按 user_id 查库 / 账号接口）。
