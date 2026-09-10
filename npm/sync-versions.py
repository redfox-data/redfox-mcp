#!/usr/bin/env python3
"""Sync version numbers from Python pyproject.toml to npm package.json.

Usage:
    python npm/sync-versions.py
"""

import json
import os
import re

ROOT = os.path.dirname(os.path.abspath(__file__))

PACKAGES = [
    ("redfox-douyin-mcp", "redfox-douyin-mcp"),
    ("redfox-xiaohongshu-mcp", "redfox-xiaohongshu-mcp"),
    ("redfox-wechat-mcp", "redfox-wechat-mcp"),
    ("redfox-bilibili-mcp", "redfox-bilibili-mcp"),
    ("redfox-toutiao-mcp", "redfox-toutiao-mcp"),
    ("redfox-tiktok-mcp", "redfox-tiktok-mcp"),
    ("redfox-ai-search-mcp", "redfox-ai-search-mcp"),
    ("redfox-ai-gen-mcp", "redfox-ai-gen-mcp"),
    ("redfox-twitter-mcp", "redfox-twitter-mcp"),
    ("redfox-youtube-mcp", "redfox-youtube-mcp"),
    ("redfox-instagram-mcp", "redfox-instagram-mcp"),
    ("redfox-kuaishou-mcp", "redfox-kuaishou-mcp"),
    ("redfox-auto-mcp", "redfox-auto-mcp"),
    ("redfox-wechat-channels-mcp", "redfox-wechat-channels-mcp"),
    ("redfox-tools-mcp", "redfox-tools-mcp"),
    ("redfox-mcp", "redfox-mcp"),
]


def read_py_version(pyproject_path):
    with open(pyproject_path) as f:
        for line in f:
            m = re.match(r'^version\s*=\s*"([^"]+)"', line.strip())
            if m:
                return m.group(1)
    return None


def sync():
    print("Syncing versions: pyproject.toml → package.json\n")
    for pypi_name, npm_name in PACKAGES:
        pyproject = os.path.join(ROOT, "..", "packages", pypi_name, "pyproject.toml")
        pkg_json_path = os.path.join(ROOT, npm_name, "package.json")

        pyproject = os.path.normpath(pyproject)

        if not os.path.exists(pyproject):
            print(f"  SKIP {npm_name} (no pyproject.toml)")
            continue
        if not os.path.exists(pkg_json_path):
            print(f"  SKIP {npm_name} (no package.json)")
            continue

        py_ver = read_py_version(pyproject)
        if not py_ver:
            print(f"  SKIP {npm_name} (version not found in pyproject.toml)")
            continue

        with open(pkg_json_path) as f:
            data = json.load(f)

        old_ver = data.get("version")
        if old_ver == py_ver:
            print(f"  OK   {npm_name}: {py_ver} (already synced)")
            continue

        data["version"] = py_ver
        with open(pkg_json_path, "w") as f:
            json.dump(data, f, indent=2)
            f.write("\n")

        print(f"  SYNC {npm_name}: {old_ver} → {py_ver}")

    print("\nDone!")


if __name__ == "__main__":
    sync()
