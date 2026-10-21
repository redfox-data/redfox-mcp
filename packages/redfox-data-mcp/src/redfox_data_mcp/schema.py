"""从目录生成模型直接看得见的服务说明和 call 参数表。"""

from __future__ import annotations

import re
from typing import Any

from redfox_data_mcp.search import load_catalog

PLATFORM_LABELS = {
    "ai_gen": "AI 生成（图片、视频）",
    "ai_search": "AI 搜索（Kimi、豆包、Deepseek、元宝、千问、百度）",
    "auto": "汽车（懂车帝、汽车之家、易车）",
    "bilibili": "B站",
    "douyin": "抖音",
    "instagram": "Instagram",
    "kuaishou": "快手",
    "tiktok": "TikTok",
    "tools": "下载与上传",
    "toutiao": "头条",
    "twitter": "X（推特）",
    "wechat_channels": "微信视频号",
    "wechat": "微信公众号",
    "xiaohongshu": "小红书",
    "youtube": "YouTube",
}


def capability_ids() -> list[str]:
    return [item["id"] for item in load_catalog()]


def async_ids() -> list[str]:
    return [item["id"] for item in load_catalog() if item["kind"] == "async"]


def platform_line() -> str:
    seen: list[str] = []
    for item in load_catalog():
        if item["platform"] not in seen:
            seen.append(item["platform"])
    return ", ".join(f"{name}（{PLATFORM_LABELS.get(name, name)}）" for name in seen)


def instructions() -> str:
    example = "douyin.get.daily.hot.rank"
    return (
        "RedFox 提供社媒和内容平台的公开数据，以及 AI 搜索。"
        "一次 call 只调一个能力。\n"
        f"能力编号形如 platform.resource.action，例如 {example}。"
        f"平台：{platform_line()}。\n"
        "编号能从 call 的 capability 列表里看出来时，直接 call；参数名或取值不确定时先 describe。"
        "只有列表里对不上任何一个编号时才 find。find 说没有匹配，就告诉用户目录里没有，不要换一个平台的能力来顶上。\n"
        "榜单里的体育、美食、二次元这类分类，填在该榜单能力的 type 或 category 参数上，不要另造编号。"
        "只传这个能力接受的参数，参数名就列在 call 上。\n"
        "异步能力超时会返回 taskId，再用 result，capability 用同一次 call 的编号，task_id 用返回的 taskId。"
    )


def _sentences(text: str) -> list[str]:
    flat = re.sub(r"\s+", " ", text or "").strip()
    return [part.strip() for part in re.split(r"[。；;]", flat) if part.strip()]


def param_specs() -> list[dict[str, Any]]:
    """按出现次数从多到少。同一参数在不同能力上的类型、说明合并成一条。"""
    order: list[str] = []
    grouped: dict[str, list[dict[str, Any]]] = {}
    owners: dict[str, list[dict[str, Any]]] = {}
    for item in load_catalog():
        for param in item["params"]:
            name = param["name"]
            if name not in grouped:
                order.append(name)
                grouped[name] = []
                owners[name] = []
            grouped[name].append(param)
            owners[name].append(item)
    ranked = sorted(order, key=lambda name: (-len(grouped[name]), name))
    specs = []
    for name in ranked:
        types = {param.get("type") or "any" for param in grouped[name]}
        notes = []
        for item in owners[name]:
            for sentence in _sentences(item["summary_zh"]):
                if name in sentence and sentence not in notes:
                    notes.append(sentence)
                    break
            if len(notes) >= 2:
                break
        description = "；".join(notes) if notes else f"参数 {name}"
        if len(owners[name]) > 1:
            description += "。不同能力的含义以 describe 为准。"
        if name == "type":
            description = "榜单或推荐的分类，例如体育、美食、二次元、全部。不传时多数榜单查全部。具体可选值以 describe 为准。"
        specs.append({
            "name": name,
            "description": description[:400],
            "types": sorted(types),
            "json_type": _json_type(types),
        })
    return specs


def _json_type(types: set[str]) -> str | list[str]:
    kinds = set()
    for raw in types:
        text = raw.lower()
        if "list" in text or "dict" in text:
            kinds.add("array")
        elif "bool" in text:
            kinds.add("boolean")
        elif text in {"int", "optional[int]"}:
            kinds.add("integer")
        elif "any" in text:
            kinds.update({"string", "integer", "boolean", "array"})
        else:
            kinds.add("string")
    if kinds == {"integer"}:
        return "integer"
    if kinds == {"boolean"}:
        return "boolean"
    if kinds == {"array"}:
        return "array"
    if kinds == {"string"}:
        return "string"
    return sorted(kinds)
