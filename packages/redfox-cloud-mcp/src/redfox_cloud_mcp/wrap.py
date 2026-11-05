"""云市场 MCP 的返回包装与上游 code 判定。

工具返回值统一包成 MCP CallToolResult 形状：
    {"isError": bool, "content": [{"type": "text", "text": "<json 字符串>"}]}
其中 text 里的 JSON：成功为 {"code", "message", "data"}，失败为 {"code", "message"}。

成功码只有上游的 2000 与 3801（两者都扣费），其余一律失败。
SDK 把非 2000 的 code 抛成 RedFoxAPIError 且 core.call 会丢掉响应体，
这里对 3801 从异常的 response 里把 data 取回来，按成功处理。
"""

from __future__ import annotations

import json
import time
from typing import Any, Callable, Dict, Optional, Tuple

from fastmcp.tools import ToolResult
from redfox.exceptions import RedFoxAPIError
from redfox_mcp_core.runtime import TASK_PENDING_MSG, _emit, is_done

# 上游成功码（均扣费）。其余 code 一律视为失败。
SUCCESS_CODES = frozenset({2000, 3801})

# 云市场渠道的调用来源标识，便于后端统计与计费归属。
CALL_SOURCE = "cloud"

_POLL_INTERVAL = 3.0


def _fn_name(fn: Callable) -> str:
    owner = getattr(fn, "__self__", None)
    name = getattr(fn, "__name__", None) or type(fn).__name__
    if owner is None:
        return name
    return f"{type(owner).__name__}.{name}"


def _normalize(result: Any) -> Dict[str, Any]:
    if isinstance(result, dict):
        return result
    if isinstance(result, list):
        return {"list": result}
    return {"data": result}


def sdk_raw(fn_factory: Callable[[], Callable], **kwargs: Any) -> Tuple[int, Dict[str, Any]]:
    """直接调 SDK 并返回 (上游 code, 结果体)，不吞掉 3801 的数据。"""
    args = {k: v for k, v in kwargs.items() if v is not None}
    tool = "unknown"
    try:
        fn = fn_factory()
        tool = _fn_name(fn)
        result = fn(**args)
        _emit("mcp_call", tool=tool, arguments=args, ok=True, result=result)
        return 2000, _normalize(result)
    except RedFoxAPIError as e:
        _emit(
            "mcp_call",
            tool=tool,
            arguments=args,
            ok=False,
            error=type(e).__name__,
            result={"code": e.code, "message": e.message},
        )
        if e.code in SUCCESS_CODES and isinstance(e.response, dict):
            return e.code, _normalize(e.response.get("data", e.response))
        return (e.code or 500), {"message": e.message}
    except ValueError as e:
        _emit("mcp_call", tool=tool, arguments=args, ok=False, error=type(e).__name__, result={"message": str(e)})
        return 401, {"message": str(e)}


def poll(
    result_fn: Callable[[], Callable],
    task_id: str,
    timeout_seconds: int,
    source: Optional[str] = None,
) -> Tuple[int, Dict[str, Any]]:
    deadline = time.monotonic() + timeout_seconds
    while True:
        kw: Dict[str, Any] = {"task_id": task_id}
        if source is not None:
            kw["source"] = source
        code, res = sdk_raw(result_fn, **kw)
        if code not in SUCCESS_CODES:
            return code, res
        if is_done(res):
            return code, res
        if time.monotonic() >= deadline:
            return code, {"completed": False, "taskId": task_id, "message": TASK_PENDING_MSG}
        time.sleep(_POLL_INTERVAL)


def run_task(
    submit_fn: Callable[[], Callable],
    result_fn: Callable[[], Callable],
    timeout_seconds: int,
    **kwargs: Any,
) -> Tuple[int, Dict[str, Any]]:
    code, submitted = sdk_raw(submit_fn, **kwargs)
    if code not in SUCCESS_CODES or submitted.get("error"):
        return code, submitted
    task_id = submitted.get("taskId") or submitted.get("task_id")
    if not task_id:
        return code, submitted
    return poll(result_fn, task_id, timeout_seconds, source=kwargs.get("source"))


def envelope(code: int, payload: Optional[Dict[str, Any]] = None, message: Optional[str] = None) -> ToolResult:
    """把 (code, 结果体) 包成云市场要求的 CallToolResult。"""
    ok = code in SUCCESS_CODES
    payload = payload or {}
    if message is None:
        message = payload.get("message") or payload.get("error") or ("success" if ok else "failed")
    if ok:
        body: Dict[str, Any] = {"code": code, "message": message, "data": payload}
    else:
        body = {"code": code, "message": message}
    text = json.dumps(body, ensure_ascii=False, default=str)
    return ToolResult(content=text, is_error=not ok)
