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


def _short_name(name: str) -> str:
    head = (name or "").split("。")[0]
    return re.split(r"[，,]提交", head)[0].strip()


def _capability_groups() -> list[tuple[str, list[str]]]:
    """按用户能认出的平台列出能力，汽车拆成懂车帝、汽车之家、易车。"""
    rules = [
        ("抖音", lambda item: item["platform"] == "douyin"),
        ("快手", lambda item: item["platform"] == "kuaishou"),
        ("TikTok", lambda item: item["platform"] == "tiktok"),
        ("小红书", lambda item: item["platform"] == "xiaohongshu"),
        ("微信公众号", lambda item: item["platform"] == "wechat"),
        ("微信视频号", lambda item: item["platform"] == "wechat_channels"),
        ("B站", lambda item: item["platform"] == "bilibili"),
        ("头条", lambda item: item["platform"] == "toutiao"),
        ("Instagram", lambda item: item["platform"] == "instagram"),
        ("X（推特）", lambda item: item["platform"] == "twitter"),
        ("YouTube", lambda item: item["platform"] == "youtube"),
        ("懂车帝", lambda item: item["id"].startswith("auto.dongchedi.")),
        ("汽车之家", lambda item: item["id"].startswith("auto.autohome.")),
        ("易车", lambda item: item["id"].startswith("auto.yiche.")),
    ]
    catalog = load_catalog()
    groups = []
    for label, match in rules:
        names = [_short_name(item["name_zh"]) for item in catalog if match(item)]
        if names:
            groups.append((label, names))
    return groups


def platform_capabilities_text() -> str:
    lines = ["当前开放的平台和能力："]
    for label, names in _capability_groups():
        lines.append(f"{label}：{'、'.join(names)}")
    return "\n".join(lines)


def find_tool_description() -> str:
    return (
        "编号在 call 的 capability 列表里看不出来时，才用一句话找能力。中英文都可以，最多 10 条。\n\n"
        + platform_capabilities_text()
        + "\n没有匹配时 matches 为空；点了名的平台会在 nearest 列出它有的能力，那些不能拿来顶替调用。"
    )


def find_param_descriptions() -> dict[str, str]:
    return {
        "query": "要找的能力，中英文都可以。例如「抖音体育榜单」「快手搜索作品」。编号已经在 call 的列表里时不要调用。",
        "platform": "只查一个已开放平台，用编号或中文名。可选：" + platform_line() + "。",
        "category": "只查一个类别：social 是社媒，auto 是汽车（懂车帝、汽车之家、易车）。不传则不按类别限制。",
    }


# 目录摘要里没有写到参数名时，用这里的说明，避免模型只看到「参数 xxx」。
PARAM_TEXT = {
    "timeout_seconds": "异步能力等待上游的秒数，默认 240。到时仍未完成会返回 taskId，再用 result 查询。",
    "size": "每页条数。快手和微信视频号的搜索、用户作品列表默认 20。",
    "publish_time_end": "发布时间上限，与 publish_time_start 一起用。公众号如 2026-07-01，小红书为 yyyy-MM-dd。",
    "work_uuid": "公众号作品 UUID。wechat.get.work 和 wechat.get.work.wide 必填。",
    "country_code": "YouTube 评论的国家或地区代码，例如 US。不传则用接口默认。",
    "language_code": "YouTube 评论的语言代码，例如 zh-Hans、en。不传则用接口默认。",
    "search_id": "今日头条搜索账号的翻页标识。上一页 hasMore 为 1 时，把返回的 searchId 传到这里，并带上 offset。",
}


def instructions() -> str:
    example = "douyin.get.daily.hot.rank"
    return (
        "RedFox 提供下列平台的公开数据。一次 call 只调一个能力。\n"
        f"能力编号形如 platform.resource.action，例如 {example}。\n"
        f"{platform_capabilities_text()}\n"
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
        if notes:
            description = "；".join(notes)
            if len(owners[name]) > 1:
                description += "。不同能力的含义以 describe 为准。"
        else:
            description = PARAM_TEXT.get(name, name)
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
