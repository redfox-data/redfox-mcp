# redfox-kuaishou-mcp

RedFoxHub 快手数据 MCP Server — 将快手数据 API 封装为 6 个 MCP 工具，适用于 dsh、Claude Code、Cursor 等任意 MCP 客户端。

## 工具（6）

| 工具 | 说明 |
|---|---|
| `kuaishou_search_works` | 快手关键词搜索作品 |
| `kuaishou_get_work` | 获取快手单个作品详情 |
| `kuaishou_get_user_works` | 获取快手用户作品列表 |
| `kuaishou_search_users` | 快手关键词搜索账号 |
| `kuaishou_transcript` | 快手视频字幕/文案提取（自动等待） |
| `kuaishou_transcript_result` | 查询快手字幕提取任务结果 |

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
uvx redfox-kuaishou-mcp
```

或：

```bash
pip install redfox-kuaishou-mcp
redfox-kuaishou-mcp
```

## 客户端配置

Claude Code：

```bash
claude mcp add redfox-kuaishou --env REDFOX_API_KEY=YOUR_API_KEY -- uvx redfox-kuaishou-mcp
```

Cursor / 其他 MCP 客户端：

```json
{
  "mcpServers": {
    "redfox-kuaishou": {
      "command": "uvx",
      "args": ["redfox-kuaishou-mcp"],
      "env": { "REDFOX_API_KEY": "YOUR_API_KEY" }
    }
  }
}
```

## 远程 HTTP 模式（多租户）

适用于 MCP 市场与托管场景，每个用户携带自己的 API Key：

```bash
redfox-kuaishou-mcp --transport http --host 0.0.0.0 --port 8000
# 或环境变量：REDFOX_MCP_TRANSPORT=http REDFOX_MCP_HOST=0.0.0.0 REDFOX_MCP_PORT=8000
```

- MCP 端点：`http://<host>:8000/mcp`（Streamable HTTP）；健康检查：`GET /health`
- 每个请求通过请求头 `X-API-Key: <key>`（或 `Authorization: Bearer <key>`）携带自己的 key，按 key 建独立客户端缓存，额度互不共享

客户端配置（远程 URL + 请求头）：

```json
{
  "mcpServers": {
    "redfox-kuaishou": {
      "url": "http://<host>:8000/mcp",
      "headers": { "X-API-Key": "ak_your_key" }
    }
  }
}
```

## Docker 部署

本包目录自带 Dockerfile，可独立构建部署：

```bash
cd packages/redfox-kuaishou-mcp
docker build -t redfox-kuaishou-mcp .
docker run -d -p 8000:8000 redfox-kuaishou-mcp
```

镜像不内置任何 API Key，调用方通过请求头携带自己的 key。

## 底层实现

基于官方 SDK [redfox-python-sdk](https://github.com/redfox-data/redfox-python-sdk)。API 文档：<https://redfox.hk/?source=mcp>。

## License

MIT
