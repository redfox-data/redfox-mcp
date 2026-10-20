"""从现有 redfox-*-mcp 的 server.py 抽出能力目录。只读那些文件，不修改它们。"""

from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path

SOCIAL = {
    "douyin",
    "xiaohongshu",
    "wechat",
    "wechat_channels",
    "bilibili",
    "toutiao",
    "tiktok",
    "kuaishou",
    "instagram",
    "twitter",
    "youtube",
}


def packages_root() -> Path:
    if len(sys.argv) > 1:
        return Path(sys.argv[1]).resolve()
    here = Path(__file__).resolve()
    candidates = [
        here.parents[2] / "redfox-mcp" / "packages",
        here.parents[2],
    ]
    for path in candidates:
        if (path / "redfox-douyin-mcp").is_dir():
            return path
    raise SystemExit("找不到 redfox-mcp 的 packages 目录")


def platform_of(package: str) -> str:
    name = package.removeprefix("redfox-").removesuffix("-mcp")
    return name.replace("-", "_")


def category_of(platform: str) -> str:
    if platform in SOCIAL:
        return "social"
    if platform == "auto":
        return "auto"
    if platform in {"ai_search", "ai_gen"}:
        return "ai"
    return "tools"


def ann_name(node: ast.AST | None) -> str:
    if node is None:
        return "any"
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Constant):
        return str(node.value)
    if isinstance(node, ast.Attribute):
        return node.attr
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
        return f"{ann_name(node.left)} | {ann_name(node.right)}"
    if isinstance(node, ast.Subscript):
        return f"{ann_name(node.value)}[{ann_name(node.slice)}]"
    return "any"


def literal(node: ast.AST | None):
    if node is None:
        return None
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub) and isinstance(node.operand, ast.Constant):
        return -node.operand.value
    if isinstance(node, (ast.List, ast.Tuple)):
        return [literal(elt) for elt in node.elts]
    raise ValueError(f"非常量默认值: {ast.dump(node)}")


def attr_path(node: ast.AST) -> str:
    parts: list[str] = []
    cur = node
    while isinstance(cur, ast.Attribute):
        parts.append(cur.attr)
        cur = cur.value
    if not (
        isinstance(cur, ast.Call)
        and isinstance(cur.func, ast.Name)
        and cur.func.id == "get_client"
    ):
        raise ValueError(f"不是 get_client() 调用链: {ast.dump(node)[:240]}")
    return ".".join(reversed(parts))


def lambda_path(node: ast.AST) -> str:
    if not isinstance(node, ast.Lambda):
        raise ValueError("期望 lambda")
    return attr_path(node.body)


def one_of(doc: str, params: list[str]) -> list[str]:
    for sentence in re.split(r"[。；;]", doc or ""):
        if not any(mark in sentence for mark in ("至少", "三选一", "二选一")):
            continue
        found = [name for name in params if re.search(rf"\b{re.escape(name)}\b", sentence)]
        if len(found) >= 2:
            return found
    return []


def first_sentence(doc: str) -> str:
    text = (doc or "").strip()
    if not text:
        return ""
    return re.split(r"[。\n]", text, maxsplit=1)[0].strip()


def _params(fn: ast.FunctionDef) -> list[dict]:
    params = []
    defaults = [None] * (len(fn.args.args) - len(fn.args.defaults)) + list(fn.args.defaults)
    for arg, default in zip(fn.args.args, defaults):
        item = {
            "name": arg.arg,
            "type": ann_name(arg.annotation),
            "required": default is None,
        }
        if default is not None:
            item["default"] = literal(default)
            item["required"] = False
        params.append(item)
    return params


def parse_function(fn: ast.FunctionDef) -> dict:
    doc = ast.get_docstring(fn) or ""
    body = [stmt for stmt in fn.body if not isinstance(stmt, ast.Expr)]
    if len(body) != 1 or not isinstance(body[0], ast.Return) or not isinstance(body[0].value, ast.Call):
        raise ValueError(f"{fn.name} 的函数体不是单条 return")
    call = body[0].value
    callee = call.func.id if isinstance(call.func, ast.Name) else ""
    if callee == "_upload":
        method = call.args[0]
        source_node = call.args[3]
        if not isinstance(method, ast.Constant) or not isinstance(source_node, ast.Constant):
            raise ValueError(f"{fn.name} 的 _upload 参数不是常量")
        params = _params(fn)
        return {
            "legacy_tool": fn.name,
            "summary_zh": doc.strip(),
            "name_zh": first_sentence(doc),
            "params": params,
            "one_of": one_of(doc, [p["name"] for p in params]),
            "kind": "upload",
            "sdk": f"tools.{method.value}",
            "result": None,
            "source": source_node.value,
        }
    params = _params(fn)
    keywords = {}
    for kw in call.keywords:
        if kw.arg is None:
            raise ValueError(f"{fn.name} 使用了 **kwargs")
        if isinstance(kw.value, ast.Constant):
            keywords[kw.arg] = kw.value.value
        elif isinstance(kw.value, ast.Name):
            keywords[kw.arg] = kw.value.id
        else:
            keywords[kw.arg] = None
    source = keywords.get("source")
    if not isinstance(source, str):
        raise ValueError(f"{fn.name} 没有字符串 source")
    if callee == "call":
        kind = "sync"
        sdk = lambda_path(call.args[0])
        result = None
    elif callee == "run_task":
        kind = "async"
        sdk = lambda_path(call.args[0])
        result = lambda_path(call.args[1])
    else:
        raise ValueError(f"{fn.name} 调用了 {callee}")
    return {
        "legacy_tool": fn.name,
        "summary_zh": doc.strip(),
        "name_zh": first_sentence(doc),
        "params": params,
        "one_of": one_of(doc, [p["name"] for p in params]),
        "kind": kind,
        "sdk": sdk,
        "result": result,
        "source": source,
    }


def capability_id(platform: str, legacy: str) -> str:
    prefix = platform + "_"
    rest = legacy[len(prefix):] if legacy.startswith(prefix) else legacy
    return platform + "." + rest.replace("_", ".")


def main() -> None:
    root = packages_root()
    entries = []
    for server in sorted(root.glob("redfox-*-mcp/src/*/server.py")):
        package = server.parents[2].name
        if package in {"redfox-mcp", "redfox-mcp-core"}:
            continue
        platform = platform_of(package)
        tree = ast.parse(server.read_text())
        for node in tree.body:
            if not isinstance(node, ast.FunctionDef):
                continue
            if not any(
                (isinstance(dec, ast.Call) and getattr(dec.func, "attr", None) == "tool")
                or (isinstance(dec, ast.Attribute) and dec.attr == "tool")
                for dec in node.decorator_list
            ):
                continue
            try:
                parsed = parse_function(node)
            except Exception as exc:
                raise SystemExit(f"{server}: {exc}") from exc
            parsed["platform"] = platform
            parsed["category"] = category_of(platform)
            parsed["id"] = capability_id(platform, parsed["legacy_tool"])
            parsed["name_en"] = parsed["id"].split(".", 1)[-1].replace(".", " ")
            entries.append(parsed)
    result_ids = {item["id"] for item in entries if item["legacy_tool"].endswith("_result")}
    capabilities = []
    for item in entries:
        if item["id"] in result_ids:
            continue
        item["aliases"] = {
            "zh": [],
            "en": [item["legacy_tool"], item["name_en"]],
        }
        capabilities.append(item)
    out = Path(__file__).resolve().parents[1] / "src" / "redfox_data_mcp" / "catalog.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(capabilities, ensure_ascii=False, indent=2) + "\n")
    print(f"wrote {len(capabilities)} capabilities to {out}")


if __name__ == "__main__":
    main()
