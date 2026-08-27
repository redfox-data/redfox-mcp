# redfox-mcp

RedFoxHub MCP Server（全量聚合版）— 将 6 大内容平台数据 API 与 AI 搜索 / 生成能力封装为 40 个 MCP 工具，适用于 dsh、Claude Code、Cursor 等任意 MCP 客户端。

本包为聚合包，组合以下 8 个独立平台包（也可按需单独安装）：

| 独立包 | 工具数 | 说明 |
|---|---|---|
| `redfox-douyin-mcp` | 6 | 抖音作品/账号搜索、账号信息、作品列表与详情、AI 作品搜索 |
| `redfox-xiaohongshu-mcp` | 5 | 小红书笔记/博主搜索、账号信息、笔记详情、AI 笔记搜索 |
| `redfox-wechat-mcp` | 7 | 公众号文章/账号搜索、账号信息、文章列表与全文详情、AI 文章搜索 |
| `redfox-bilibili-mcp` | 5 | B 站视频/UP 主搜索、UP 主信息与视频、视频详情 |
| `redfox-toutiao-mcp` | 2 | 今日头条内容搜索与作品详情（实时） |
| `redfox-tiktok-mcp` | 1 | TikTok 账号搜索 |
| `redfox-ai-search-mcp` | 6 | Kimi / 豆包 / Deepseek 联网 AI 搜索（自动轮询 + 结果补查） |
| `redfox-ai-gen-mcp` | 8 | GPT 图片 / 豆包图片 Pro / Lite / 豆包视频生成（自动轮询 + 结果补查） |

异步工具（AI 搜索 / 生成）内部自动轮询：提交 → 等待 → 返回完整结果，无需手动处理 taskId。若等待超过 `timeout_seconds`（默认 240 秒、视频 480 秒），返回 `taskId`，可用对应的 result 工具补查。

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
uvx redfox-mcp
```

或：

```bash
pip install redfox-mcp
redfox-mcp
```

## 客户端配置

Claude Code：

```bash
claude mcp add redfox --env REDFOX_API_KEY=YOUR_API_KEY -- uvx redfox-mcp
```

Cursor / 其他 MCP 客户端：

```json
{
  "mcpServers": {
    "redfox": {
      "command": "uvx",
      "args": ["redfox-mcp"],
      "env": { "REDFOX_API_KEY": "YOUR_API_KEY" }
    }
  }
}
```

## 远程 HTTP 模式（多租户）

适用于 MCP 市场与托管场景，每个用户携带自己的 API Key：

```bash
redfox-mcp --transport http --host 0.0.0.0 --port 8000
# 或环境变量：REDFOX_MCP_TRANSPORT=http REDFOX_MCP_HOST=0.0.0.0 REDFOX_MCP_PORT=8000
```

- MCP 端点：`http://<host>:8000/mcp`（Streamable HTTP）；健康检查：`GET /health`
- 每个请求通过请求头 `X-API-Key: <key>`（或 `Authorization: Bearer <key>`）携带自己的 key，按 key 建独立客户端缓存，额度互不共享

客户端配置（远程 URL + 请求头）：

```json
{
  "mcpServers": {
    "redfox": {
      "url": "http://<host>:8000/mcp",
      "headers": { "X-API-Key": "ak_your_key" }
    }
  }
}
```

## Docker 部署

本包目录自带 Dockerfile，可独立构建部署：

```bash
cd packages/redfox-mcp
docker build -t redfox-mcp .
docker run -d -p 8000:8000 redfox-mcp
```

镜像不内置任何 API Key，调用方通过请求头携带自己的 key。

## 底层实现

基于官方 SDK [redfox-python-sdk](https://github.com/redfox-data/redfox-python-sdk)。API 文档：<https://redfox.hk/?source=mcp>。

## License

MIT
