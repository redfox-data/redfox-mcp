# redfox-ai-search-mcp

RedFoxHub AI 搜索 MCP Server — 将 Kimi / 豆包 / Deepseek / 元宝 / 千问 / 百度 联网搜索能力封装为 12 个 MCP 工具，适用于 dsh、Claude Code、Cursor 等任意 MCP 客户端。

## 工具（12）

| 工具 | 说明 |
|---|---|
| `ai_search_kimi` | Kimi 联网 AI 搜索，提交后自动等待并返回完整结果 |
| `ai_search_doubao` | 豆包联网 AI 搜索，提交后自动等待并返回完整结果 |
| `ai_search_deepseek` | Deepseek 联网 AI 搜索，提交后自动等待并返回完整结果 |
| `ai_search_kimi_result` | 查询 Kimi 搜索任务结果（超时返回 taskId 后补查） |
| `ai_search_doubao_result` | 查询豆包搜索任务结果（超时返回 taskId 后补查） |
| `ai_search_deepseek_result` | 查询 Deepseek 搜索任务结果（超时返回 taskId 后补查） |
| `ai_search_yuanbao` | 元宝联网 AI 搜索（自动等待） |
| `ai_search_yuanbao_result` | 查询元宝搜索任务结果 |
| `ai_search_qianwen` | 千问联网 AI 搜索（自动等待） |
| `ai_search_qianwen_result` | 查询千问搜索任务结果 |
| `ai_search_baidu` | 百度联网 AI 搜索（自动等待） |
| `ai_search_baidu_result` | 查询百度搜索任务结果 |

异步工具内部自动轮询：提交 → 等待 → 返回完整结果，无需手动处理 taskId。若等待超过 `timeout_seconds`（默认 240 秒），返回 `taskId`，可用对应的 result 工具补查。

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
uvx redfox-ai-search-mcp
```

或：

```bash
pip install redfox-ai-search-mcp
redfox-ai-search-mcp
```

## 客户端配置

Claude Code：

```bash
claude mcp add redfox-ai-search --env REDFOX_API_KEY=YOUR_API_KEY -- uvx redfox-ai-search-mcp
```

Cursor / 其他 MCP 客户端：

```json
{
  "mcpServers": {
    "redfox-ai-search": {
      "command": "uvx",
      "args": ["redfox-ai-search-mcp"],
      "env": { "REDFOX_API_KEY": "YOUR_API_KEY" }
    }
  }
}
```

## 远程 HTTP 模式（多租户）

适用于 MCP 市场与托管场景，每个用户携带自己的 API Key：

```bash
redfox-ai-search-mcp --transport http --host 0.0.0.0 --port 8000
# 或环境变量：REDFOX_MCP_TRANSPORT=http REDFOX_MCP_HOST=0.0.0.0 REDFOX_MCP_PORT=8000
```

- MCP 端点：`http://<host>:8000/mcp`（Streamable HTTP）；健康检查：`GET /health`
- 每个请求通过请求头 `X-API-Key: <key>`（或 `Authorization: Bearer <key>`）携带自己的 key，按 key 建独立客户端缓存，额度互不共享

客户端配置（远程 URL + 请求头）：

```json
{
  "mcpServers": {
    "redfox-ai-search": {
      "url": "http://<host>:8000/mcp",
      "headers": { "X-API-Key": "ak_your_key" }
    }
  }
}
```

## Docker 部署

本包目录自带 Dockerfile，可独立构建部署：

```bash
cd packages/redfox-ai-search-mcp
docker build -t redfox-ai-search-mcp .
docker run -d -p 8000:8000 redfox-ai-search-mcp
```

镜像不内置任何 API Key，调用方通过请求头携带自己的 key。

## 底层实现

基于官方 SDK [redfox-python-sdk](https://github.com/redfox-data/redfox-python-sdk)。API 文档：<https://redfox.hk/?source=mcp>。

## License

MIT
