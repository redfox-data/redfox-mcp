#!/bin/zsh
# PyPI 新项目限流（429）重试脚本：剩余 5 个平台包 + 聚合包 0.3.1
# 用法：zsh .tmp-publish-retry.sh（会自动 source ~/.zshrc 加载 UV_PUBLISH_TOKEN）
set -u
source ~/.zshrc >/dev/null 2>&1
cd "$(dirname "$0")"

packages=(redfox_bilibili_mcp redfox_toutiao_mcp redfox_tiktok_mcp redfox_ai_search_mcp redfox_ai_gen_mcp)

publish_pkg() {
  local p="$1" v="$2"
  uv publish "dist/${p}-${v}.tar.gz" >/dev/null 2>&1 && \
  uv publish "dist/${p}-${v}-py3-none-any.whl" >/dev/null 2>&1
}

for round in {1..24}; do
  echo "[$(date +%H:%M:%S)] round $round start"
  remaining=()
  for p in "${packages[@]}"; do
    if publish_pkg "$p" "0.1.0"; then
      echo "[$(date +%H:%M:%S)] OK $p 0.1.0"
    else
      echo "[$(date +%H:%M:%S)] FAIL $p"
      remaining+=("$p")
    fi
    sleep 20
  done
  packages=("${remaining[@]:-}")
  packages=(${(@)packages:#})
  if [ ${#packages[@]} -eq 0 ]; then
    echo "[$(date +%H:%M:%S)] all platform packages published, publishing aggregate redfox-mcp 0.3.1"
    if publish_pkg "redfox_mcp" "0.3.1"; then
      echo "[$(date +%H:%M:%S)] OK redfox-mcp 0.3.1 — ALL DONE"
      exit 0
    else
      echo "[$(date +%H:%M:%S)] aggregate publish failed, retry next round"
      packages=(__aggregate_only__)
    fi
  fi
  if [ "${packages[1]:-}" = "__aggregate_only__" ]; then
    if publish_pkg "redfox_mcp" "0.3.1"; then
      echo "[$(date +%H:%M:%S)] OK redfox-mcp 0.3.1 — ALL DONE"
      exit 0
    fi
    echo "[$(date +%H:%M:%S)] aggregate still failing — sleep 600s"
    sleep 600
    continue
  fi
  echo "[$(date +%H:%M:%S)] round $round done, remaining: ${packages[*]} — sleep 600s"
  sleep 600
done
echo "TIMEOUT after 24 rounds"
exit 1
