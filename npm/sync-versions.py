#!/usr/bin/env python3
"""Set a unified version across all RedFox MCP npm packages.

Usage:
    python npm/sync-versions.py 0.4.2

Updates version (and optionalDependencies ranges in main packages) in:
  - npm/redfox-*-mcp/package.json        (16 main packages)
  - npm/redfox-mcp-bin-*/package.json    (platform binary packages)
"""

import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))


def update(path, version):
    with open(path) as f:
        data = json.load(f)

    old = data.get("version")
    data["version"] = version
    for dep in data.get("optionalDependencies", {}):
        if dep.startswith("redfox-mcp-bin-"):
            data["optionalDependencies"][dep] = version

    with open(path, "w") as f:
        json.dump(data, indent=2, fp=f)
        f.write("\n")

    mark = "OK  " if old == version else "SET "
    print(f"  {mark} {data['name']}: {old} → {version}")


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    version = sys.argv[1]

    print(f"Syncing npm versions → {version}\n")
    # 注意：glob "redfox-*-mcp" 不匹配裸聚合包目录 "redfox-mcp"（* 需要
    # 两侧各有字符），必须显式列出，否则聚合包版本漏 bump 会被 CI 跳过发布。
    paths = sorted(
        glob.glob(os.path.join(ROOT, "redfox-*-mcp", "package.json"))
        + glob.glob(os.path.join(ROOT, "redfox-mcp", "package.json"))
        + glob.glob(os.path.join(ROOT, "redfox-mcp-bin-*", "package.json"))
    )
    for path in paths:
        update(path, version)
    print(f"\nDone! {len(paths)} packages.")


if __name__ == "__main__":
    main()
