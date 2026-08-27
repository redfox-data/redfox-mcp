# redfox-mcp-core

RedFoxHub 各平台 MCP server 的共享基础包，不直接面向终端用户。

提供能力：

- RedFoxClient 管理：stdio 模式全局单例；HTTP 模式按请求头 API Key 的多租户缓存（LRU，上限 1000）
- 统一异常封装：SDK 异常转为结构化结果（auth_failed / rate_limited / api_error），agent 可直接读取出错引导
- 异步任务辅助：提交后自动轮询至完成，超时返回 taskId 供 result 工具补查
- server 工厂与启动入口：`create_server(name, version)` 注册 `/health` 路由；`serve(mcp, prog, description)` 解析 `--transport stdio|http` / `--host` / `--port` / `--path` 并启动

认证方式：

- stdio：环境变量 `REDFOX_API_KEY`
- HTTP：请求头 `X-API-Key: ak_xxx`（或 `Authorization: Bearer ak_xxx`）

API Key 获取：https://redfox.hk/settings/api-keys?source=mcp
