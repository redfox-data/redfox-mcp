# redfox-wechat-channels-mcp

RedFoxHub 微信视频号数据 MCP Server — 将微信视频号数据 API 封装为 7 个 MCP 工具，适用于 dsh、Claude Code、Cursor 等任意 MCP 客户端。

## 工具（7）

| 工具 | 说明 |
|---|---|
| `wechat_channels_search_works` | 微信视频号关键词搜索作品 |
| `wechat_channels_get_work` | 获取微信视频号单个作品详情 |
| `wechat_channels_get_user_works` | 获取微信视频号用户作品列表 |
| `wechat_channels_get_work_by_link` | 通过链接获取微信视频号作品详情 |
| `wechat_channels_search_users` | 微信视频号关键词搜索账号 |
| `wechat_channels_transcript` | 微信视频号视频字幕/文案提取（自动等待） |
| `wechat_channels_transcript_result` | 查询微信视频号字幕提取任务结果 |

## 认证

1. 前往 <https://redfox.hk/settings/api-keys?source=mcp> 获取 API Key
2. 设置环境变量：

```bash
export REDFOX_API_KEY="YOUR_API_KEY"
```

未配置 key 时，每个工具都会返回结构化的获取引导。

## 安装与运行（本地 stdio）

需要 Python ≥ 3.10，推荐使用 [uv](https://docs.astral.sh/uv/)：

```bash
uvx redfox-wechat-channels-mcp
```

或：

```bash
pip install redfox-wechat-channels-mcp
redfox-wechat-channels-mcp
```

## 客户端配置

Claude Code：

```bash
claude mcp add redfox-wechat-channels --env REDFOX_API_KEY=YOUR_API_KEY -- uvx redfox-wechat-channels-mcp
```

Cursor / 其他 MCP 客户端：

```json
{
  "mcpServers": {
    "redfox-wechat-channels": {
      "command": "uvx",
      "args": ["redfox-wechat-channels-mcp"],
      "env": { "REDFOX_API_KEY": "YOUR_API_KEY" }
    }
  }
}
```

## 远程 HTTP 模式（多租户）

适用于 MCP 市场与托管场景，每个用户携带自己的 API Key：

```bash
redfox-wechat-channels-mcp --transport http --host 0.0.0.0 --port 8000
# 或环境变量：REDFOX_MCP_TRANSPORT=http REDFOX_MCP_HOST=0.0.0.0 REDFOX_MCP_PORT=8000
```

- MCP 端点：`http://<host>:8000/mcp`（Streamable HTTP）；健康检查：`GET /health`
- 每个请求通过请求头 `X-API-Key: <key>`（或 `Authorization: Bearer <key>`）携带自己的 key，按 key 建独立客户端缓存，额度互不共享

客户端配置（远程 URL + 请求头）：

```json
{
  "mcpServers": {
    "redfox-wechat-channels": {
      "url": "http://<host>:8000/mcp",
      "headers": { "X-API-Key": "ak_your_key" }
    }
  }
}
```

## 说明

- 本包对应 **微信视频号**（WeChat Channels）；微信公众号数据请使用 [`redfox-wechat-mcp`](../redfox-wechat-mcp)。
- `wechat_channels_transcript` 为异步任务：提交后自动轮询等待，超时未完成会返回 `taskId`，可用 `wechat_channels_transcript_result` 继续查询。

## 底层实现

基于官方 SDK [redfox-python-sdk](https://github.com/redfox-data/redfox-python-sdk)。API 文档：<https://redfox.hk/?source=mcp>。

## License

MIT
