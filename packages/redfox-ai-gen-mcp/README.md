# redfox-ai-gen-mcp

RedFoxHub AI 生成 MCP Server — 将 GPT 图片、豆包 Seedream 图片（Pro/Lite）、豆包 Seedance 视频生成能力封装为 8 个 MCP 工具，适用于 dsh、Claude Code、Cursor 等任意 MCP 客户端。

## 工具（8）

| 工具 | 说明 |
|---|---|
| `gpt_image_generate` | GPT 图片生成（gpt-image-2），支持文生图 / 图生图 |
| `gpt_image_result` | 查询 GPT 图片生成任务结果（超时返回 taskId 后补查） |
| `doubao_image_pro_generate` | 豆包 Seedream 5.0 Pro 图片生成 |
| `doubao_image_pro_result` | 查询 Seedream 5.0 Pro 任务结果 |
| `doubao_image_lite_generate` | 豆包 Seedream 5.0 Lite 图片生成，支持组图 |
| `doubao_image_lite_result` | 查询 Seedream 5.0 Lite 任务结果 |
| `doubao_video_generate` | 豆包 Seedance 2.0 视频生成 |
| `doubao_video_result` | 查询豆包视频生成任务结果 |

异步工具内部自动轮询：提交 → 等待 → 返回完整结果，无需手动处理 taskId。若等待超过 `timeout_seconds`（图片默认 240 秒、视频默认 480 秒），返回 `taskId`，可用对应的 result 工具补查。

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
uvx redfox-ai-gen-mcp
```

或：

```bash
pip install redfox-ai-gen-mcp
redfox-ai-gen-mcp
```

## 客户端配置

Claude Code：

```bash
claude mcp add redfox-ai-gen --env REDFOX_API_KEY=YOUR_API_KEY -- uvx redfox-ai-gen-mcp
```

Cursor / 其他 MCP 客户端：

```json
{
  "mcpServers": {
    "redfox-ai-gen": {
      "command": "uvx",
      "args": ["redfox-ai-gen-mcp"],
      "env": { "REDFOX_API_KEY": "YOUR_API_KEY" }
    }
  }
}
```

## 远程 HTTP 模式（多租户）

适用于 MCP 市场与托管场景，每个用户携带自己的 API Key：

```bash
redfox-ai-gen-mcp --transport http --host 0.0.0.0 --port 8000
# 或环境变量：REDFOX_MCP_TRANSPORT=http REDFOX_MCP_HOST=0.0.0.0 REDFOX_MCP_PORT=8000
```

- MCP 端点：`http://<host>:8000/mcp`（Streamable HTTP）；健康检查：`GET /health`
- 每个请求通过请求头 `X-API-Key: <key>`（或 `Authorization: Bearer <key>`）携带自己的 key，按 key 建独立客户端缓存，额度互不共享

客户端配置（远程 URL + 请求头）：

```json
{
  "mcpServers": {
    "redfox-ai-gen": {
      "url": "http://<host>:8000/mcp",
      "headers": { "X-API-Key": "ak_your_key" }
    }
  }
}
```

## Docker 部署

本包目录自带 Dockerfile，可独立构建部署：

```bash
cd packages/redfox-ai-gen-mcp
docker build -t redfox-ai-gen-mcp .
docker run -d -p 8000:8000 redfox-ai-gen-mcp
```

镜像不内置任何 API Key，调用方通过请求头携带自己的 key。

## 底层实现

基于官方 SDK [redfox-python-sdk](https://github.com/redfox-data/redfox-python-sdk)。API 文档：<https://redfox.hk/?source=mcp>。

## License

MIT
