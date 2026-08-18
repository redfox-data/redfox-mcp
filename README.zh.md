<p align="center">
  <a href="https://redfox.hk/?source=github"><img src="https://lyy.redfox.hk/page/logo-redfox-name.png" alt="RedFox Logo" width="200"></a>
</p>

<p align="right">
  中文
  <a href="https://github.com/redfox-data/redfox-mcp/blob/main/README.md">English</a>
</p>

# redfox-mcp

<p align="center">
  <a href="https://pypi.org/project/redfox-mcp/"><img src="https://img.shields.io/pypi/v/redfox-mcp" alt="PyPI Version"></a>
</p>

RedFoxHub（红狐数据平台）MCP Server — 将 6 大内容平台数据 API 与 AI 搜索/生成能力封装为 40 个 MCP 工具，可被 dsh、Claude Code、Cursor 等任意 MCP 客户端直接调用。

## 工具清单（40 个）

| 类别 | 工具 | 说明 |
|---|---|---|
| 抖音 | `douyin_search_articles` / `douyin_search_users` / `douyin_get_user` / `douyin_get_user_works` / `douyin_get_work` / `douyin_search_ai_articles` | 作品搜索、账号搜索、账号信息、作品列表、作品详情、AI 作品 |
| 小红书 | `xiaohongshu_search_articles` / `xiaohongshu_search_users` / `xiaohongshu_get_account` / `xiaohongshu_get_work` / `xiaohongshu_search_ai_articles` | 笔记搜索、博主搜索、账号信息、笔记详情、AI 笔记 |
| 公众号 | `wechat_search_articles` / `wechat_search_users` / `wechat_get_account` / `wechat_get_user_works` / `wechat_get_work` / `wechat_get_article_detail` / `wechat_search_ai_articles` | 文章搜索（支持全文详情）、账号搜索、文章列表、AI 文章 |
| B 站 | `bilibili_search_articles` / `bilibili_search_users` / `bilibili_get_account` / `bilibili_get_user_works` / `bilibili_get_work` | 视频搜索、UP 主搜索/信息/视频列表、视频详情 |
| 今日头条 | `toutiao_search_works` / `toutiao_get_work` | 内容搜索、作品详情（实时） |
| TikTok | `tiktok_search_users` | 账号搜索 |
| AI 搜索 | `ai_search_kimi` / `ai_search_doubao` / `ai_search_deepseek` | 联网 AI 搜索，单次调用自动等待结果 |
| AI 生成 | `gpt_image_generate` / `doubao_image_pro_generate` / `doubao_image_lite_generate` / `doubao_video_generate` | 文生图/图生图/组图/文生视频，单次调用自动等待结果 |
| 任务查询 | `ai_search_*_result` / `gpt_image_result` / `doubao_image_*_result` / `doubao_video_result`（共 7 个） | 异步任务超时返回 taskId 后，凭 taskId 补查结果 |

异步工具（AI 搜索/生成）内部自动轮询：提交任务 → 等待完成 → 返回完整结果，无需手动管理 taskId。超过 `timeout_seconds`（默认 240 秒，视频 480 秒）仍未完成时返回 `taskId`，可用对应 result 工具补查。

## 认证

所有接口需要 RedFoxHub API Key：

1. 前往 [红狐Hub](https://redfox.hk/settings/api-keys?source=mcp) 注册并复制 API Key
2. 设置环境变量：

```bash
export REDFOX_API_KEY="YOUR_API_KEY"
```

未配置时，工具会返回结构化的获取引导信息。

## 安装与运行

要求 Python ≥ 3.10，推荐用 [uv](https://docs.astral.sh/uv/) 运行：

```bash
uvx redfox-mcp
```

或：

```bash
pip install redfox-mcp
redfox-mcp
```

server 以 stdio transport 运行。

## 客户端配置

### dsh（DeepSeek Harness）

安装官方 bundle 插件 [redfox-community-dsh](https://github.com/redfox-data/redfox-community-dsh)，其中已内置本 MCP server 的注册，装好后工具以 `mcp__redfox__*` 命名直接可用：

```bash
dsh plugin --profile web add -w github:redfox-data/redfox-community-dsh
```

### Claude Code

```bash
claude mcp add redfox --env REDFOX_API_KEY=YOUR_API_KEY -- uvx redfox-mcp
```

### Cursor / 其他 MCP 客户端

在 MCP 配置中加入：

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

## 底层依赖

基于官方 SDK [redfox-python-sdk](https://github.com/redfox-data/redfox-python-sdk)（`pip install redfox-python-sdk`），API 文档见 [红狐Hub API文档](https://redfox.hk/apis/?source=mcp)。

## License

MIT
