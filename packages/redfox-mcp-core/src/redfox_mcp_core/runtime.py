"""RedFox MCP 共享运行时

为各平台 MCP server 提供统一的基础设施：
- RedFoxClient 管理（stdio 单例 / HTTP 多租户按 key 缓存）
- 统一异常转结构化结果（agent 可直接读取出错引导）
- 异步任务提交 + 自动轮询

认证：stdio 模式读环境变量 REDFOX_API_KEY；
HTTP 模式从请求头 X-API-Key（或 Authorization: Bearer <key>）取 key。
获取地址 https://redfox.hk/settings/api-keys?source=mcp
"""

import threading
import time
from collections import OrderedDict
from typing import Any, Callable, Dict, Optional

from redfox import RedFoxClient
from redfox.exceptions import RedFoxAPIError, RedFoxAuthError, RedFoxRateLimitError

try:
    from fastmcp.server.dependencies import get_http_request
except ImportError:  # 老版本 fastmcp 无此接口
    get_http_request = None

API_KEY_GUIDE = (
    "REDFOX_API_KEY 未配置或无效。请前往 "
    "https://redfox.hk/settings/api-keys?source=mcp 注册并获取 API Key，"
    "然后设置环境变量 REDFOX_API_KEY 后重启本服务。"
)

API_KEY_GUIDE_HTTP = (
    "未在请求头中检测到 API Key。请前往 "
    "https://redfox.hk/settings/api-keys?source=mcp 注册并获取 API Key，"
    "然后在 MCP 客户端的请求头中配置 X-API-Key（或 Authorization: Bearer <key>）。"
)

TASK_PENDING_MSG = (
    "任务仍在进行中，已超过本次等待时间。"
    "请稍后使用对应的 result 工具并传入此 taskId 查询结果。"
)

TERMINAL_STATUSES = {
    "succeeded", "success", "completed", "complete", "done",
    "failed", "error", "cancelled", "canceled",
}

_TRANSPORT = "stdio"  # serve() 启动时按实际 transport 设置

_client: Optional[RedFoxClient] = None  # stdio 模式：全局单例
_tenants: "OrderedDict[str, RedFoxClient]" = OrderedDict()  # http 模式：按 key 缓存
_tenants_lock = threading.Lock()
_TENANT_MAX = 1000


def set_transport(transport: str) -> None:
    """由 serve() 在启动时调用，按实际 transport 设置全局模式"""
    global _TRANSPORT
    _TRANSPORT = transport


def _auth_guide() -> str:
    return API_KEY_GUIDE if _TRANSPORT == "stdio" else API_KEY_GUIDE_HTTP


def _request_key() -> Optional[str]:
    """HTTP 模式下从当前请求头取 key：X-API-Key 优先，Authorization: Bearer 回退"""
    if get_http_request is None:
        return None
    try:
        req = get_http_request()
    except Exception:  # 非 HTTP 上下文
        return None
    key = req.headers.get("x-api-key")
    if key and key.strip():
        return key.strip()
    auth = req.headers.get("authorization", "")
    if auth.lower().startswith("bearer "):
        return auth[7:].strip() or None
    return None


def get_client() -> RedFoxClient:
    global _client
    if _TRANSPORT == "stdio":
        if _client is None:
            _client = RedFoxClient()  # 零配置：自动读环境变量 REDFOX_API_KEY
        return _client
    # HTTP 多租户：按请求头中的 key 建独立 client，互不共享额度
    key = _request_key()
    if not key:
        raise ValueError("missing API key in request header")
    with _tenants_lock:
        cli = _tenants.get(key)
        if cli is None:
            cli = RedFoxClient(api_key=key)
            _tenants[key] = cli
            if len(_tenants) > _TENANT_MAX:
                _tenants.popitem(last=False)  # 淘汰最久未使用的租户
        else:
            _tenants.move_to_end(key)
    return cli


def call(fn_factory: Callable[[], Callable], **kwargs) -> Dict[str, Any]:
    """统一调用 SDK 方法并把异常转为结构化结果，agent 可直接读取出错引导"""
    try:
        return fn_factory()(**{k: v for k, v in kwargs.items() if v is not None})
    except (RedFoxAuthError, ValueError):
        return {"error": "auth_failed", "message": _auth_guide()}
    except RedFoxRateLimitError:
        return {"error": "rate_limited", "message": "请求频率超限，请稍后重试"}
    except RedFoxAPIError as e:
        return {"error": "api_error", "code": e.code, "message": e.message}


def is_done(res: Any) -> bool:
    """判断异步任务是否到达终态（兼容各品类不同的响应结构）"""
    if not isinstance(res, dict):
        return True
    if res.get("error"):
        return True
    if res.get("completed") is True:
        return True
    status = res.get("status")
    if isinstance(status, str) and status.lower() in TERMINAL_STATUSES:
        return True
    for field in ("content", "imagePaths", "images", "videoUrl", "videoUrls", "video"):
        if res.get(field):
            return True
    return False


def poll(result_fn: Callable[[], Callable], task_id: str,
         timeout_seconds: int, interval: float = 3.0) -> Dict[str, Any]:
    deadline = time.monotonic() + timeout_seconds
    while True:
        res = call(result_fn, task_id=task_id)
        if is_done(res):
            return res
        if time.monotonic() >= deadline:
            return {"completed": False, "taskId": task_id, "message": TASK_PENDING_MSG}
        time.sleep(interval)


def run_task(submit_fn: Callable[[], Callable], result_fn: Callable[[], Callable],
             timeout_seconds: int, **kwargs) -> Dict[str, Any]:
    """提交异步任务并自动轮询至完成；超时则返回 taskId 供 result 工具后续查询"""
    submitted = call(submit_fn, **kwargs)
    if not isinstance(submitted, dict) or submitted.get("error"):
        return submitted
    task_id = submitted.get("taskId") or submitted.get("task_id")
    if not task_id:
        return submitted
    return poll(result_fn, task_id, timeout_seconds)
