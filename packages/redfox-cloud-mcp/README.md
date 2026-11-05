# redfox-cloud-mcp

面向云市场 MCP 渠道的红狐数据聚合服务：用 `find / describe / call / result` 四个工具访问红狐全部已开放接口（目录与参数逻辑复用 `redfox-data-mcp`）。

## 鉴权

普通 apikey 鉴权，不接 OAuth。HTTP 模式下从请求头读取，兼容两种写法：

- `Authorization: Bearer ak_xxx`
- `REDFOX_API_KEY: ak_xxx`（或 `X-API-KEY`）

stdio 模式读环境变量 `REDFOX_API_KEY`。

## 返回包装

工具返回统一包成 MCP `CallToolResult` 形状，`content[].text` 为 JSON 字符串：

- 成功（上游 code 为 `2000` 或 `3801`，均扣费）：`isError=false`，text = `{"code":2000,"message":"success","data":<接口全部返回>}`
- 失败（其余 code）：`isError=true`，text = `{"code":<非成功码>,"message":"<错误信息>"}`

`3801` 虽被 SDK 抛成异常，但属于扣费的成功响应，本服务会从异常响应体里取回 `data` 按成功返回。

## 运行

```bash
uv run redfox-cloud-mcp                       # stdio
uv run redfox-cloud-mcp --transport http      # HTTP 多租户
```
