"""按词面检索能力目录。不按语意扩展，没有匹配就不拿别的能力顶上。"""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

FIND_LIMIT = 10
QUERY_MAX = 200

# 暂时不对外提供。目录文件仍保留，恢复时从这里删掉即可。
DISABLED_PLATFORMS = frozenset({"ai_gen", "tools"})

# 长的别名放前面，避免「微信视频号」被截成公众号。
PLATFORM_ALIASES: list[tuple[str, list[str]]] = [
    ("wechat_channels", ["wechat_channels", "wechat-channels", "微信视频号", "视频号"]),
    ("xiaohongshu", ["xiaohongshu", "小红书", "红书", "xhs"]),
    ("wechat", ["wechat", "微信公众号", "公众号"]),
    ("bilibili", ["bilibili", "哔哩哔哩", "b站"]),
    ("kuaishou", ["kuaishou", "快手"]),
    ("toutiao", ["toutiao", "今日头条", "头条"]),
    ("douyin", ["douyin", "抖音"]),
    ("tiktok", ["tiktok"]),
    ("instagram", ["instagram", "ins"]),
    ("twitter", ["twitter", "推特"]),
    ("youtube", ["youtube", "油管"]),
    ("ai_search", ["ai_search", "ai搜索", "联网搜索"]),
    ("ai_gen", ["ai_gen", "ai生成", "文生图"]),
    ("auto", ["懂车帝", "汽车之家", "易车", "汽车", "auto"]),
    ("tools", ["下载", "上传", "tools"]),
]

SYNONYMS = {
    "video": ["视频", "作品"],
    "videos": ["视频", "作品"],
    "work": ["作品"],
    "works": ["作品"],
    "article": ["文章", "作品"],
    "articles": ["文章", "作品"],
    "note": ["笔记"],
    "notes": ["笔记"],
    "comment": ["评论"],
    "comments": ["评论"],
    "user": ["用户", "账号"],
    "users": ["用户", "账号"],
    "account": ["账号", "用户"],
    "accounts": ["账号"],
    "search": ["搜索"],
    "hot": ["热门"],
    "rank": ["榜"],
    "transcript": ["文案"],
    "download": ["下载"],
    "upload": ["上传"],
    "image": ["图片"],
    "generate": ["生成"],
    "keyword": ["关键词"],
}

STOP = {
    "的", "了", "和", "与", "或", "在", "把", "被", "吗", "呢", "吧", "请", "帮",
    "我", "一下", "一个", "什么", "哪些", "怎么", "如何", "这个", "那个",
    "the", "a", "an", "of", "on", "for", "to", "and", "in", "with",
}

_CJK = re.compile(r"[\u4e00-\u9fff]+")
_LATIN = re.compile(r"[a-z0-9_]+")


def load_catalog() -> list[dict[str, Any]]:
    path = Path(__file__).with_name("catalog.json")
    items = json.loads(path.read_text())
    return [item for item in items if item["platform"] not in DISABLED_PLATFORMS]


@lru_cache(maxsize=1)
def by_id() -> dict[str, dict[str, Any]]:
    return {item["id"]: item for item in load_catalog()}


def _hay(item: dict[str, Any]) -> str:
    parts = [
        item["id"],
        item["legacy_tool"],
        item["name_zh"],
        item["name_en"],
        item["summary_zh"],
        item["source"],
        " ".join(p["name"] for p in item["params"]),
    ]
    return "\n".join(parts)


def _latin_tokens(text: str) -> list[str]:
    return [tok for tok in _LATIN.findall(text.lower()) if tok not in STOP and len(tok) >= 3]


def _cjk_segments(text: str) -> list[str]:
    return [seg for seg in _CJK.findall(text) if seg not in STOP and len(seg) >= 2]


def _platforms_in(text: str) -> list[str]:
    found: list[str] = []
    remaining = text.lower()
    raw = text
    for platform, aliases in PLATFORM_ALIASES:
        if platform in DISABLED_PLATFORMS:
            continue
        for alias in aliases:
            if alias.isascii():
                if re.search(rf"(?<![a-z0-9]){re.escape(alias.lower())}(?![a-z0-9])", remaining):
                    found.append(platform)
                    break
            elif alias in raw:
                found.append(platform)
                break
    # 保持顺序、去重
    seen: list[str] = []
    for name in found:
        if name not in seen:
            seen.append(name)
    return seen


def _known(token: str, catalogs: list[dict[str, Any]]) -> bool:
    probes = [token, *SYNONYMS.get(token, [])]
    for item in catalogs:
        hay = _hay(item)
        hay_low = hay.lower()
        for probe in probes:
            if probe.isascii():
                if probe.lower() in hay_low:
                    return True
            elif probe in hay:
                return True
    return False


def _score(query_latin: list[str], query_cjk: list[str], item: dict[str, Any]) -> int:
    hay = _hay(item)
    hay_low = hay.lower()
    score = 0
    for token in query_latin:
        probes = [token, *SYNONYMS.get(token, [])]
        if any((p.lower() in hay_low) if p.isascii() else (p in hay) for p in probes):
            score += 4
            if token in item["id"].lower() or token in item["legacy_tool"]:
                score += 3
    for seg in query_cjk:
        if seg in hay:
            score += 6 + len(seg)
        else:
            hits = 0
            for i in range(len(seg) - 1):
                if seg[i:i + 2] in hay:
                    hits += 1
            score += hits * 2
    return score


def example_call(item: dict[str, Any]) -> dict[str, Any]:
    placeholders = {
        "keyword": "咖啡",
        "inquiry_text": "露营咖啡",
        "prompt": "一只狐狸",
        "url": "https://example.com/video",
        "file": "/path/to/file",
    }
    names = [p["name"] for p in item["params"] if p.get("required") and p["name"] != "timeout_seconds"]
    if item.get("one_of"):
        names = [item["one_of"][0]]
    arguments = {name: placeholders.get(name, f"<{name}>") for name in names}
    return {"capability": item["id"], "arguments": arguments}


def _card(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": item["id"],
        "name": {"zh": item["name_zh"], "en": item["name_en"]},
        "summary": item["summary_zh"],
        "platform": item["platform"],
        "category": item["category"],
        "kind": item["kind"],
        "required": [p["name"] for p in item["params"] if p.get("required")],
        "one_of": item.get("one_of") or [],
        "legacy_tool": item["legacy_tool"],
        "example": example_call(item),
    }


def resolve_platform(value: str) -> str | None:
    text = value.strip()
    if not text:
        return None
    for platform, aliases in PLATFORM_ALIASES:
        if platform in DISABLED_PLATFORMS:
            continue
        if text == platform or text.lower() in {a.lower() for a in aliases}:
            return platform
    return None


def find(query: str = "", platform: str = "", category: str = "") -> dict[str, Any]:
    query = (query or "").strip()
    if len(query) > QUERY_MAX:
        return {"error": "invalid_argument", "message": f"query 最长 {QUERY_MAX} 个字符"}
    catalog = load_catalog()
    explicit = resolve_platform(platform) if platform else None
    if platform and explicit is None:
        return {
            "error": "invalid_argument",
            "message": f"不认识的平台 {platform}",
            "platforms": [name for name, _ in PLATFORM_ALIASES if name not in DISABLED_PLATFORMS],
        }
    if category and category not in {"social", "auto", "ai", "tools"}:
        return {"error": "invalid_argument", "message": "category 只能是 social、auto、ai、tools"}
    if not query and not explicit and not category:
        return {"error": "invalid_argument", "message": "至少给 query 或 platform"}

    detected = _platforms_in(query) if query else []
    chosen = explicit
    if chosen is None and len(detected) == 1:
        chosen = detected[0]

    pool = catalog
    if chosen:
        pool = [item for item in pool if item["platform"] == chosen]
    if category:
        pool = [item for item in pool if item["category"] == category]

    scored_query = query
    if chosen:
        aliases = next(items for name, items in PLATFORM_ALIASES if name == chosen)
        for alias in sorted(aliases, key=len, reverse=True):
            scored_query = re.sub(re.escape(alias), " ", scored_query, flags=re.IGNORECASE)
    latin = [tok for tok in _latin_tokens(scored_query) if resolve_platform(tok) is None]
    cjk = _cjk_segments(scored_query)

    ranked: list[tuple[int, dict[str, Any]]] = []
    if latin or cjk:
        for item in pool:
            score = _score(latin, cjk, item)
            if score > 0:
                ranked.append((score, item))
        ranked.sort(key=lambda pair: (-pair[0], pair[1]["id"]))

    matches = [_card(item) for _, item in ranked[:FIND_LIMIT]]
    unknown = []
    for token in latin + cjk:
        if token in unknown or token in STOP:
            continue
        if not _known(token, catalog):
            unknown.append(token)

    nearest: list[dict[str, Any]] = []
    if not matches and chosen:
        nearest = [
            {
                "id": item["id"],
                "name": {"zh": item["name_zh"], "en": item["name_en"]},
                "summary": item["summary_zh"],
            }
            for item in catalog
            if item["platform"] == chosen
        ]

    return {
        "matches": matches,
        "platforms": [chosen] if chosen else detected,
        "unknown": unknown,
        "nearest": nearest,
    }


def describe(ids: list[str]) -> dict[str, Any]:
    if not ids or len(ids) > FIND_LIMIT:
        return {"error": "invalid_argument", "message": f"ids 需要 1 到 {FIND_LIMIT} 个能力编号"}
    found = []
    missing = []
    for cap_id in ids:
        item = by_id().get(cap_id)
        if item is None:
            missing.append(cap_id)
            continue
        found.append({
            "id": item["id"],
            "platform": item["platform"],
            "category": item["category"],
            "kind": item["kind"],
            "name": {"zh": item["name_zh"], "en": item["name_en"]},
            "summary": item["summary_zh"],
            "legacy_tool": item["legacy_tool"],
            "params": item["params"],
            "one_of": item.get("one_of") or [],
            "async": item["kind"] == "async",
            "result": "超时返回 taskId 后，用 result 工具按这个能力编号查询" if item["kind"] == "async" else None,
            "example": example_call(item),
        })
    return {"capabilities": found, "missing": missing}
