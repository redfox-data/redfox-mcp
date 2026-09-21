#!/usr/bin/env python3
"""防漏守卫：代码改了但版本没 bump 的包，给告警（只告警，不阻断）。

增量发布以"版本号 bump"为变更信号，于是出现一种静默漏发：
某个包改了代码却忘记 bump 版本 -> 过滤器认为它"无新版本"而跳过 -> 改动永远上不了 PyPI。
本脚本用纯 git 分析揪出这种情况：

  changed = 自上一个发布 tag 以来 packages/<dir>/ 下有任何文件改动的包
  bumped  = 其中 pyproject.toml 的 version 行相对上一个 tag 有变化的包
  missed  = changed - bumped  -> ::warning:: 注解 + GITHUB_STEP_SUMMARY

基线 tag 取法：tag 触发时取当前 tag 的前一个 v* tag；workflow_dispatch 时取最新 v* tag。
"""
import os
import re
import subprocess
import sys


def sh(*args):
    return subprocess.run(args, capture_output=True, text=True, check=True).stdout


def version_at(ref, pkg_dir):
    try:
        txt = sh("git", "show", f"{ref}:packages/{pkg_dir}/pyproject.toml")
    except subprocess.CalledProcessError:
        return None  # 该 ref 下包还不存在
    m = re.search(r'^version\s*=\s*"([^"]+)"', txt, re.M)
    return m.group(1) if m else None


def main():
    ref = os.environ.get("GITHUB_REF_NAME", "")
    tags = [t for t in sh("git", "tag", "--sort=v:refname").split() if t.startswith("v")]
    if not tags:
        print("guard: 仓库还没有发布 tag，跳过")
        return
    if ref in tags:
        idx = tags.index(ref)
        prev = tags[idx - 1] if idx > 0 else None
    else:
        prev = tags[-1]  # workflow_dispatch：以最新 tag 为基线
    if prev is None:
        print("guard: 只有一个是 tag，无基线，跳过")
        return
    print(f"guard: 基线 {prev} .. HEAD ({ref or 'dispatch'})")

    changed = set()
    for path in sh("git", "diff", "--name-only", f"{prev}..HEAD").split():
        m = re.match(r"packages/([^/]+)/", path)
        if m:
            changed.add(m.group(1))
    bumped = {p for p in changed if version_at(prev, p) != version_at("HEAD", p)}
    missed = sorted(changed - bumped)

    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    for pkg in missed:
        msg = (f"{pkg}: 自 {prev} 以来有代码改动但 pyproject 版本未 bump，"
               f"本次不会发布到 PyPI，改动将静默漏发")
        print(f"::warning file=packages/{pkg}/pyproject.toml::{msg}")
        if summary:
            with open(summary, "a", encoding="utf-8") as fh:
                fh.write(f"- :warning: {msg}\n")
    if not missed:
        print(f"guard: {len(changed)} 个改动包全部已 bump: {sorted(changed) or '-'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
