# redfox-xiaohongshu-mcp

RedFoxHub 小红书数据 MCP Server — 将小红书数据 API 封装为 15 个 MCP 工具，适用于 dsh、Claude Code、Cursor 等任意 MCP 客户端。

## 工具（15）

| 工具 | 说明 |
|---|---|
| `xiaohongshu_search_articles` | 搜索小红书笔记（优质库） |
| `xiaohongshu_search_users` | 搜索小红书博主账号（优质库） |
| `xiaohongshu_get_account` | 获取小红书账号信息 |
| `xiaohongshu_get_work` | 获取小红书笔记详情 |
| `xiaohongshu_search_ai_articles` | 搜索小红书 AI 创作相关笔记 |
| `xiaohongshu_get_user_works` | 查询小红书账号作品列表 |
| `xiaohongshu_get_daily_hot_rank` | 小红书每日爆款笔记榜单 |
| `xiaohongshu_get_weekly_hot_rank` | 小红书七日爆款笔记 |
| `xiaohongshu_get_hot_accounts` | 小红书热门账号推荐（日/周/月榜） |
| `xiaohongshu_search_hot_notes` | 小红书爆款笔记洞察 |
| `xiaohongshu_get_dark_horse_notes` | 小红书黑马爆文榜（低粉爆款） |
| `xiaohongshu_get_comments` | 获取笔记一级评论（提交后自动等待结果） |
| `xiaohongshu_get_comments_result` | 查询评论任务结果（超时返回 taskId 后补查） |
| `xiaohongshu_transcript` | 小红书视频提文案（提交后自动等待结果） |
| `xiaohongshu_transcript_result` | 查询视频提文案任务结果（超时返回 taskId 后补查） |

异步工具（评论、提文案）内部自动轮询：提交 → 等待 → 返回完整结果。若等待超过 `timeout_seconds`（默认 240 秒），返回 `taskId`，可用对应的 result 工具补查。

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
uvx redfox-xiaohongshu-mcp
```

或：

```bash
pip install redfox-xiaohongshu-mcp
redfox-xiaohongshu-mcp
```

## 客户端配置

Claude Code：

```bash
claude mcp add redfox-xiaohongshu --env REDFOX_API_KEY=YOUR_API_KEY -- uvx redfox-xiaohongshu-mcp
```

Cursor / 其他 MCP 客户端：

```json
{
  "mcpServers": {
    "redfox-xiaohongshu": {
      "command": "uvx",
      "args": ["redfox-xiaohongshu-mcp"],
      "env": { "REDFOX_API_KEY": "YOUR_API_KEY" }
    }
  }
}
```

## 远程 HTTP 模式（多租户）

适用于 MCP 市场与托管场景，每个用户携带自己的 API Key：

```bash
redfox-xiaohongshu-mcp --transport http --host 0.0.0.0 --port 8000
# 或环境变量：REDFOX_MCP_TRANSPORT=http REDFOX_MCP_HOST=0.0.0.0 REDFOX_MCP_PORT=8000
```

- MCP 端点：`http://<host>:8000/mcp`（Streamable HTTP）；健康检查：`GET /health`
- 每个请求通过请求头 `X-API-Key: <key>`（或 `Authorization: Bearer <key>`）携带自己的 key，按 key 建独立客户端缓存，额度互不共享

客户端配置（远程 URL + 请求头）：

```json
{
  "mcpServers": {
    "redfox-xiaohongshu": {
      "url": "http://<host>:8000/mcp",
      "headers": { "X-API-Key": "ak_your_key" }
    }
  }
}
```

## Docker 部署

本包目录自带 Dockerfile，可独立构建部署：

```bash
cd packages/redfox-xiaohongshu-mcp
docker build -t redfox-xiaohongshu-mcp .
docker run -d -p 8000:8000 redfox-xiaohongshu-mcp
```

镜像不内置任何 API Key，调用方通过请求头携带自己的 key。

## 底层实现

基于官方 SDK [redfox-python-sdk](https://github.com/redfox-data/redfox-python-sdk)。API 文档：<https://redfox.hk/?source=mcp>。

## License

MIT
