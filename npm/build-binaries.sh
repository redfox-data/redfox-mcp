#!/usr/bin/env bash
# Build PyInstaller binaries for all RedFox MCP npm packages.
# Supports parallel builds and cross-platform (macOS/Linux/Windows via Git Bash).
#
# Usage:
#   ./npm/build-binaries.sh [--platform darwin-arm64] [--jobs 4] [--packages pkg1,pkg2]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# ── Cross-platform python detection ──
if command -v python3 &>/dev/null; then
  PY=python3
elif command -v python &>/dev/null; then
  PY=python
else
  echo "Error: python3/python not found"; exit 1
fi

# ── Detect platform ──
detect_platform() {
  local os arch
  os=$(uname -s | tr '[:upper:]' '[:lower:]')
  arch=$(uname -m)
  case "$arch" in x86_64|amd64) arch="x64" ;; aarch64|arm64) arch="arm64" ;; esac
  # MSYS/MINGW/CYGWIN → win32
  case "$os" in msys*|mingw*|cygwin*) os="win32" ;; esac
  echo "${os}-${arch}"
}

PLATFORM=$(detect_platform)
JOBS=4
PACKAGES=""

while [[ $# -gt 0 ]]; do
  case $1 in
    --platform) PLATFORM="$2"; shift 2 ;;
    --jobs)     JOBS="$2"; shift 2 ;;
    --packages) PACKAGES="$2"; shift 2 ;;
    *) echo "Unknown: $1"; exit 1 ;;
  esac
done

IS_WINDOWS=false
[[ "$PLATFORM" == win32-* ]] && IS_WINDOWS=true

echo "=== RedFox MCP Binary Build ==="
echo "Platform: $PLATFORM | Python: $PY | Parallel: $JOBS"
echo ""

# ── Check PyInstaller ──
if ! $PY -c "import PyInstaller" 2>/dev/null; then
  echo "Installing PyInstaller..."
  $PY -m pip install pyinstaller
fi

# ── Build one package ──
build_one() {
  local pkg_name="$1"
  local npm_dir="$SCRIPT_DIR/$pkg_name"
  local entry="$npm_dir/_entry.py"
  local out_dir="$npm_dir/bin/$PLATFORM"

  [[ ! -f "$entry" ]] && { echo "  SKIP $pkg_name"; return; }

  mkdir -p "$out_dir"

  $PY -m PyInstaller \
    --onefile \
    --name "$pkg_name" \
    --distpath "$out_dir" \
    --workpath "/tmp/pyi-${pkg_name}" \
    --specpath "/tmp" \
    --noconfirm \
    --clean \
    --copy-metadata fastmcp \
    --copy-metadata fastmcp-slim \
    --copy-metadata redfox-python-sdk \
    --copy-metadata redfox-mcp-core \
    --copy-metadata mcp \
    --copy-metadata starlette \
    --copy-metadata httpx \
    --copy-metadata pydantic \
    --copy-metadata pydantic-core \
    --copy-metadata anyio \
    --copy-metadata httpcore \
    "$entry" > /dev/null 2>&1

  local bin_file="$out_dir/$pkg_name"
  $IS_WINDOWS && bin_file="$out_dir/$pkg_name.exe"

  if [[ -f "$bin_file" ]]; then
    local size
    size=$(du -h "$bin_file" | cut -f1)
    echo "  ✓ $pkg_name ($size)"
  else
    echo "  ✗ $pkg_name FAILED"
  fi
}

export -f build_one
export SCRIPT_DIR PLATFORM PY IS_WINDOWS

# ── Collect package list ──
if [[ -n "$PACKAGES" ]]; then
  IFS=',' read -ra PKG_LIST <<< "$PACKAGES"
else
  PKG_LIST=()
  for d in "$SCRIPT_DIR"/redfox-*-mcp; do
    [[ -d "$d" ]] && PKG_LIST+=("$(basename "$d")")
  done
fi

echo "Building ${#PKG_LIST[@]} packages..."

# ── Parallel build using background jobs ──
active=0
for pkg in "${PKG_LIST[@]}"; do
  build_one "$pkg" &
  active=$((active + 1))
  if [[ $active -ge $JOBS ]]; then
    wait -n 2>/dev/null || true
    active=$((active - 1))
  fi
done
wait

echo ""
echo "=== Done: npm/*/bin/$PLATFORM/ ==="
