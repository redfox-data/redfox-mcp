"""把 call 的参数校验与组装收在本包内。参数不合法时不发起上游请求。"""

from __future__ import annotations

from typing import Any

from redfox_mcp_core.runtime import _emit

from redfox_cloud_mcp.search import by_id


def _fail(capability: str, message: str, **extra: Any) -> dict[str, Any]:
    result = {"error": "invalid_argument", "message": message, "capability": capability, **extra}
    _emit("mcp_call", tool="call", arguments={"capability": capability}, ok=False, result=result)
    return result


def prepare(capability: str, arguments: dict[str, Any] | None) -> dict[str, Any] | tuple[dict[str, Any], dict[str, Any], int | None]:
    item = by_id().get(capability)
    if item is None:
        return _fail(capability, "目录里没有这个能力编号。先用 find，不要换一个平台的能力来调用。")
    raw = arguments or {}
    if not isinstance(raw, dict):
        return _fail(capability, "arguments 必须是对象")
    known = {p["name"]: p for p in item["params"]}
    unexpected = [name for name in raw if name not in known]
    if unexpected:
        return _fail(
            capability,
            "有这个能力不接受的参数",
            unexpected=unexpected,
            accepted=list(known),
        )
    given = {key: value for key, value in raw.items() if value is not None}
    missing = [name for name, spec in known.items() if spec.get("required") and name not in given]
    if missing:
        return _fail(capability, "缺少必填参数", missing=missing)
    one_of = item.get("one_of") or []
    if one_of and not any(name in given for name in one_of):
        return _fail(capability, "这些参数里至少要给一个", one_of=one_of)
    payload = dict(given)
    timeout = payload.pop("timeout_seconds", None)
    for name, spec in known.items():
        if name == "timeout_seconds" or name in payload:
            continue
        if "default" in spec and spec["default"] is not None:
            payload[name] = spec["default"]
    if timeout is None:
        for spec in item["params"]:
            if spec["name"] == "timeout_seconds":
                timeout = spec.get("default", 240)
    return item, payload, timeout
