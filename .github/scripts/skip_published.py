#!/usr/bin/env python3
"""增量发布过滤器：删掉 dist/ 中 PyPI 已存在的版本，只留下待发布的新版本。

PyPI 禁止重复上传已存在的 (包名, 版本)，因此"全量重发"本就不可能；
本脚本把这一约束变成增量语义：bump 过版本的包进入发布集，未 bump 的自动跳过，
重跑流水线也安全。

用法: python3 skip_published.py <dist-dir>
退出码: 0 正常（无论发布集是否为空）; 2 PyPI 查询遇到非 200/404（不猜测，直接失败）
"""
import glob
import os
import re
import sys
import urllib.error
import urllib.request

UA = {"User-Agent": "redfox-release-script"}


def parse(filename: str):
    """从 wheel / sdist 文件名解析 (规范化包名, 版本)。"""
    if filename.endswith(".whl"):
        stem, version = filename.split("-")[0], filename.split("-")[1]
    else:
        m = re.match(r"(.+)-(\d[^-]*?)\.tar\.gz$", filename)
        if not m:
            return None
        stem, version = m.group(1), m.group(2)
    return stem.replace("_", "-"), version


def on_pypi(name: str, version: str):
    url = f"https://pypi.org/pypi/{name}/{version}/json"
    try:
        urllib.request.urlopen(
            urllib.request.Request(url, headers=UA), timeout=20
        )
        return True
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return False
        print(f"::error::PyPI 查询 {url} 返回 HTTP {e.code}，放弃猜测")
        sys.exit(2)


def main():
    dist = sys.argv[1] if len(sys.argv) > 1 else "dist"
    files = sorted(glob.glob(os.path.join(dist, "*.whl"))) + sorted(
        glob.glob(os.path.join(dist, "*.tar.gz"))
    )
    pairs = {}
    for f in files:
        parsed = parse(os.path.basename(f))
        if parsed is None:
            print(f"::warning::无法解析文件名，跳过: {f}")
            continue
        pairs.setdefault(parsed, []).append(f)

    keep = 0
    for (name, version), fs in sorted(pairs.items()):
        if on_pypi(name, version):
            for f in fs:
                os.remove(f)
            print(f"  skip    {name} {version} (PyPI 已存在)")
        else:
            keep += 1
            print(f"  publish {name} {version}")
    print(f"增量发布集: {keep} 个新版本 / 共 {len(pairs)} 个")


if __name__ == "__main__":
    main()
