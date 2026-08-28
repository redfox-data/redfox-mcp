# redfox-wechat-mcp

RedFoxHub 公众号数据 MCP Server — 将公众号数据 API 封装为 16 个 MCP 工具，适用于 dsh、Claude Code、Cursor 等任意 MCP 客户端。

## 工具（16）

| 工具 | 说明 |
|---|---|
| `wechat_search_articles` | 搜索公众号文章（优质库） |
| `wechat_search_users` | 搜索公众号账号（优质库） |
| `wechat_get_account` | 获取公众号账号信息 |
| `wechat_get_user_works` | 获取公众号文章列表 |
| `wechat_get_work` | 根据作品 UUID 获取文章元数据 |
| `wechat_get_article_detail` | 根据文章链接获取全文详情 |
| `wechat_search_ai_articles` | 搜索公众号 AI 创作相关文章 |
| `wechat_search_articles_wide` | 搜索公众号作品（广域库，覆盖更大） |
| `wechat_search_users_wide` | 搜索公众号账号（广域库） |
| `wechat_get_work_wide` | 根据作品 UUID 获取作品含正文全文（广域库） |
| `wechat_get_user_works_wide` | 获取公众号账号作品列表（广域库） |
| `wechat_get_account_wide` | 获取公众号账号信息（广域库） |
| `wechat_get_ten_w_rank` | 公众号 10W+ 阅读文章推荐 |
| `wechat_get_original_rank` | 公众号原创爆款文章推荐 |
| `wechat_get_strength_rank` | 公众号综合实力榜（日/周/月） |
| `wechat_get_reading_growth_rank` | 公众号阅读增长榜单 |

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
uvx redfox-wechat-mcp
```

或：

```bash
pip install redfox-wechat-mcp
redfox-wechat-mcp
```

## 客户端配置

Claude Code：

```bash
claude mcp add redfox-wechat --env REDFOX_API_KEY=YOUR_API_KEY -- uvx redfox-wechat-mcp
```

Cursor / 其他 MCP 客户端：

```json
{
  "mcpServers": {
    "redfox-wechat": {
      "command": "uvx",
      "args": ["redfox-wechat-mcp"],
      "env": { "REDFOX_API_KEY": "YOUR_API_KEY" }
    }
  }
}
```

## 远程 HTTP 模式（多租户）

适用于 MCP 市场与托管场景，每个用户携带自己的 API Key：

```bash
redfox-wechat-mcp --transport http --host 0.0.0.0 --port 8000
# 或环境变量：REDFOX_MCP_TRANSPORT=http REDFOX_MCP_HOST=0.0.0.0 REDFOX_MCP_PORT=8000
```

- MCP 端点：`http://<host>:8000/mcp`（Streamable HTTP）；健康检查：`GET /health`
- 每个请求通过请求头 `X-API-Key: <key>`（或 `Authorization: Bearer <key>`）携带自己的 key，按 key 建独立客户端缓存，额度互不共享

客户端配置（远程 URL + 请求头）：

```json
{
  "mcpServers": {
    "redfox-wechat": {
      "url": "http://<host>:8000/mcp",
      "headers": { "X-API-Key": "ak_your_key" }
    }
  }
}
```

## Docker 部署

本包目录自带 Dockerfile，可独立构建部署：

```bash
cd packages/redfox-wechat-mcp
docker build -t redfox-wechat-mcp .
docker run -d -p 8000:8000 redfox-wechat-mcp
```

镜像不内置任何 API Key，调用方通过请求头携带自己的 key。

## 底层实现

基于官方 SDK [redfox-python-sdk](https://github.com/redfox-data/redfox-python-sdk)。API 文档：<https://redfox.hk/?source=mcp>。

## License

MIT
