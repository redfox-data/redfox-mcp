# redfox-douyin-mcp

RedFoxHub 抖音数据 MCP Server — 将抖音数据 API 封装为 16 个 MCP 工具，适用于 dsh、Claude Code、Cursor 等任意 MCP 客户端。

## 工具（16）

| 工具 | 说明 |
|---|---|
| `douyin_search_articles` | 搜索抖音作品（优质库） |
| `douyin_search_users` | 搜索抖音账号（优质库） |
| `douyin_get_user` | 获取抖音账号信息 |
| `douyin_get_user_works` | 获取抖音账号作品列表 |
| `douyin_get_work` | 获取抖音作品详情 |
| `douyin_search_ai_articles` | 搜索抖音 AI 相关作品 |
| `douyin_search_works_wide` | 搜索抖音作品（广域库，覆盖更大） |
| `douyin_search_accounts_wide` | 搜索抖音账号（广域库） |
| `douyin_get_work_wide` | 获取抖音作品详情（广域库） |
| `douyin_get_user_works_wide` | 获取抖音账号作品列表（广域库） |
| `douyin_get_daily_hot_rank` | 抖音每日热门作品榜（按点赞排名） |
| `douyin_get_daily_surge_rank` | 抖音每日点赞飙升榜（单日新增点赞） |
| `douyin_get_weekly_surge_rank` | 抖音七日点赞飙升榜（七日新增点赞） |
| `douyin_get_hot_accounts` | 抖音热门账号推荐（日/周/月榜） |
| `douyin_transcript` | 抖音视频提文案（提交后自动等待结果） |
| `douyin_transcript_result` | 查询视频提文案任务结果（超时返回 taskId 后补查） |

异步工具（提文案）内部自动轮询：提交 → 等待 → 返回完整结果。若等待超过 `timeout_seconds`（默认 240 秒），返回 `taskId`，可用对应的 result 工具补查。

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
uvx redfox-douyin-mcp
```

或：

```bash
pip install redfox-douyin-mcp
redfox-douyin-mcp
```

## 客户端配置

Claude Code：

```bash
claude mcp add redfox-douyin --env REDFOX_API_KEY=YOUR_API_KEY -- uvx redfox-douyin-mcp
```

Cursor / 其他 MCP 客户端：

```json
{
  "mcpServers": {
    "redfox-douyin": {
      "command": "uvx",
      "args": ["redfox-douyin-mcp"],
      "env": { "REDFOX_API_KEY": "YOUR_API_KEY" }
    }
  }
}
```

## 远程 HTTP 模式（多租户）

适用于 MCP 市场与托管场景，每个用户携带自己的 API Key：

```bash
redfox-douyin-mcp --transport http --host 0.0.0.0 --port 8000
# 或环境变量：REDFOX_MCP_TRANSPORT=http REDFOX_MCP_HOST=0.0.0.0 REDFOX_MCP_PORT=8000
```

- MCP 端点：`http://<host>:8000/mcp`（Streamable HTTP）；健康检查：`GET /health`
- 每个请求通过请求头 `X-API-Key: <key>`（或 `Authorization: Bearer <key>`）携带自己的 key，按 key 建独立客户端缓存，额度互不共享

客户端配置（远程 URL + 请求头）：

```json
{
  "mcpServers": {
    "redfox-douyin": {
      "url": "http://<host>:8000/mcp",
      "headers": { "X-API-Key": "ak_your_key" }
    }
  }
}
```

## Docker 部署

本包目录自带 Dockerfile，可独立构建部署：

```bash
cd packages/redfox-douyin-mcp
docker build -t redfox-douyin-mcp .
docker run -d -p 8000:8000 redfox-douyin-mcp
```

镜像不内置任何 API Key，调用方通过请求头携带自己的 key。

## 底层实现

基于官方 SDK [redfox-python-sdk](https://github.com/redfox-data/redfox-python-sdk)。API 文档：<https://redfox.hk/?source=mcp>。

## License

MIT
