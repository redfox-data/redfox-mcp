"""RedFox MCP 共享运行时

为各平台 MCP server 提供统一的基础设施：
- RedFoxClient 管理（stdio 单例 / HTTP 多租户按 key 缓存）
- 统一异常转结构化结果（agent 可直接读取出错引导）
- 异步任务提交 + 自动轮询

认证：stdio 模式读环境变量 REDFOX_API_KEY；
HTTP 模式从请求头 REDFOX_API_KEY（或 Authorization: Bearer <key>）取 key。
获取地址 https://redfox.hk/settings/api-keys?source=mcp
"""

import json
import logging
import os
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
    "然后在 MCP 客户端的请求头中配置 REDFOX_API_KEY（或 Authorization: Bearer <key>）。"
)

TASK_PENDING_MSG = (
    "任务仍在进行中，已超过本次等待时间。"
    "请稍后使用对应的 result 工具并传入此 taskId 查询结果。"
)

TERMINAL_STATUSES = {
    "succeeded", "success", "completed", "complete", "done",
    "failed", "error", "cancelled", "canceled",
}

# 非终态（仅作说明）：各品类还有 queued / in_progress / processing / running 等
# 中间态，不在上表内即视为未完成，poll() 会继续轮询。

_TRANSPORT = "stdio"  # serve() 启动时按实际 transport 设置

_log = logging.getLogger("redfox_mcp")


def _log_enabled() -> bool:
    return os.getenv("REDFOX_MCP_LOG", "").strip().lower() in {"1", "true", "yes", "on"}


def _log_max() -> int:
    try:
        return max(200, int(os.getenv("REDFOX_MCP_LOG_MAX", "4000")))
    except ValueError:
        return 4000


def _mask_key(key: Optional[str]) -> str:
    if not key:
        return ""
    if os.getenv("REDFOX_MCP_LOG_API_KEY", "mask").strip().lower() == "full":
        return key
    if len(key) <= 8:
        return "***"
    return f"{key[:4]}...{key[-4:]}"


def _clip(value: Any) -> str:
    try:
        text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, default=str)
    except Exception:
        text = str(value)
    limit = _log_max()
    if len(text) <= limit:
        return text
    return text[:limit] + f"...<truncated {len(text) - limit} chars>"


def _fn_name(fn: Callable) -> str:
    owner = getattr(fn, "__self__", None)
    name = getattr(fn, "__name__", None) or type(fn).__name__
    if owner is None:
        return name
    return f"{type(owner).__name__}.{name}"


def _request_meta() -> Dict[str, Any]:
    meta: Dict[str, Any] = {"transport": _TRANSPORT}
    key = os.getenv("REDFOX_API_KEY")
    if get_http_request is not None:
        try:
            req = get_http_request()
        except Exception:
            req = None
        if req is not None:
            header_key = _request_key()
            if header_key:
                key = header_key
            meta.update({
                "http_method": getattr(req, "method", None),
                "path": str(getattr(getattr(req, "url", None), "path", "") or ""),
                "session_id": (
                    req.headers.get("mcp-session-id")
                    or req.headers.get("Mcp-Session-Id")
                    or ""
                ),
            })
    meta["api_key"] = _mask_key(key)
    return meta


def _emit(event: str, **fields: Any) -> None:
    if not _log_enabled():
        return
    if not _log.handlers:
        logging.basicConfig(level=logging.INFO, format="%(message)s")
    payload = {"event": event, **_request_meta(), **fields}
    _log.info(_clip(payload))

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


def require_api_key_enabled() -> bool:
    """HTTP 建连是否强制要求 API Key。默认开启；REDFOX_MCP_REQUIRE_API_KEY=0 可关闭拦截。"""
    return os.getenv("REDFOX_MCP_REQUIRE_API_KEY", "1").strip().lower() in {
        "1", "true", "yes", "on",
    }


def api_key_from_headers(headers: Any) -> Optional[str]:
    """从映射式 headers 取 key：REDFOX_API_KEY / X-API-KEY 优先，Authorization: Bearer 回退。"""
    if headers is None:
        return None
    key = headers.get("REDFOX_API_KEY") or headers.get("X-API-KEY")
    if key and str(key).strip():
        return str(key).strip()
    auth = headers.get("authorization") or headers.get("Authorization") or ""
    auth = str(auth)
    if auth.lower().startswith("bearer "):
        return auth[7:].strip() or None
    return None


def _request_key() -> Optional[str]:
    """HTTP 模式下从当前请求头取 key。"""
    if get_http_request is None:
        return None
    try:
        req = get_http_request()
    except Exception:  # 非 HTTP 上下文
        return None
    if req is None:
        return None
    return api_key_from_headers(getattr(req, "headers", None))


def emit_mcp_connect(
    *,
    has_api_key: bool,
    api_key: Optional[str] = None,
    session_id: Optional[str] = None,
    rejected: bool = False,
    http_method: Optional[str] = None,
    path: Optional[str] = None,
) -> None:
    """记录建连事件（含空连 / 无 Key 拒绝）。不依赖 FastMCP 请求上下文。"""
    _emit(
        "mcp_connect",
        has_api_key=has_api_key,
        api_key=_mask_key(api_key) if api_key else "",
        session_id=session_id or "",
        rejected=rejected,
        http_method=http_method,
        path=path,
        require_api_key=require_api_key_enabled(),
    )


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
    args = {k: v for k, v in kwargs.items() if v is not None}
    tool = "unknown"
    try:
        fn = fn_factory()
        tool = _fn_name(fn)
        result = fn(**args)
        _emit("mcp_call", tool=tool, arguments=args, ok=True, result=result)
        return result
    except (RedFoxAuthError, ValueError) as e:
        result = {"error": "auth_failed", "message": _auth_guide()}
        _emit("mcp_call", tool=tool, arguments=args, ok=False, error=type(e).__name__, result=result)
        return result
    except RedFoxRateLimitError as e:
        result = {"error": "rate_limited", "message": "请求频率超限，请稍后重试"}
        _emit("mcp_call", tool=tool, arguments=args, ok=False, error=type(e).__name__, result=result)
        return result
    except RedFoxAPIError as e:
        result = {"error": "api_error", "code": e.code, "message": e.message}
        _emit("mcp_call", tool=tool, arguments=args, ok=False, error=type(e).__name__, result=result)
        return result


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
    # imageUrls: GPT-Image-2 等新图片接口的结果字段；imagePaths 为其旧版字段
    for field in ("content", "imageUrls", "imagePaths", "images",
                  "videoUrl", "videoUrls", "video"):
        if res.get(field):
            return True
    return False


def poll(result_fn: Callable[[], Callable], task_id: str,
         timeout_seconds: int, interval: float = 3.0,
         source: Optional[str] = None) -> Dict[str, Any]:
    deadline = time.monotonic() + timeout_seconds
    while True:
        kw: Dict[str, Any] = {"task_id": task_id}
        if source is not None:
            kw["source"] = source
        res = call(result_fn, **kw)
        if is_done(res):
            return res
        if time.monotonic() >= deadline:
            return {"completed": False, "taskId": task_id, "message": TASK_PENDING_MSG}
        time.sleep(interval)


def run_task(submit_fn: Callable[[], Callable], result_fn: Callable[[], Callable],
             timeout_seconds: int, **kwargs) -> Dict[str, Any]:
    """提交异步任务并自动轮询至完成；超时则返回 taskId 供 result 工具后续查询

    kwargs 中的 source（调用来源标识）会同时透传给提交与轮询两个 SDK 方法。
    """
    submitted = call(submit_fn, **kwargs)
    if not isinstance(submitted, dict) or submitted.get("error"):
        return submitted
    task_id = submitted.get("taskId") or submitted.get("task_id")
    if not task_id:
        return submitted
    return poll(result_fn, task_id, timeout_seconds, source=kwargs.get("source"))
