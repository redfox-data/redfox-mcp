# redfox-wechat-mcp 多租户 HTTP 模式
# 适用于任意支持 Docker 的服务器（阿里云 ECS / 腾讯云 CVM / 本地等）
FROM python:3.12-slim

# 从 PyPI 安装已发布的 redfox-wechat-mcp（容器内无需 uvx 冷启动拉包）
RUN pip install --no-cache-dir redfox-wechat-mcp

EXPOSE 8000

# 多租户模式：镜像不内置任何 API Key
# 调用方在请求头携带自己的 key：X-API-Key: ak_xxx（或 Authorization: Bearer ak_xxx）
CMD ["redfox-wechat-mcp", "--transport", "http", "--host", "0.0.0.0", "--port", "8000"]
