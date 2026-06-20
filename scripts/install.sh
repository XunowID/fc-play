#!/bin/sh
# =============================================================================
# FC-Play Installer — One command to rule them all
# =============================================================================
# curl -fsSL https://raw.githubusercontent.com/Alishahryar1/fc-play/main/scripts/install.sh | sh
#
# Or with extras:
#   curl -fsSL https://raw.githubusercontent.com/Alishahryar1/fc-play/main/scripts/install.sh | sh -s -- --voice
# =============================================================================

set -e

# ─── Configuration ──────────────────────────────────────────────────────────
REPO="git+https://github.com/Alishahryar1/fc-play.git"
PYTHON_VERSION="3.12"
MIN_UV="0.4.0"

# ─── Helpers ────────────────────────────────────────────────────────────────
fail() { echo "❌ $*" >&2; exit 1; }
step() { echo; echo "✦ $*"; }
run() {
  echo "  → $*"
  if [ -z "$DRY_RUN" ]; then
    eval "$@" || fail "Command failed: $*"
  fi
}

version_ge() {
  # Compare semver: version_ge "1.2.3" "1.0.0" → true
  v1=$(echo "$1" | cut -d. -f1-3 | awk -F. '{printf("%d%03d%03d", $1,$2,$3)}')
  v2=$(echo "$2" | cut -d. -f1-3 | awk -F. '{printf("%d%03d%03d", $1,$2,$3)}')
  [ "$v1" -ge "$v2" ]
}

# ─── Parse args ─────────────────────────────────────────────────────────────
VOICE_NIM=""
VOICE_LOCAL=""
DRY_RUN=""
TORCH_BACKEND=""

while [ $# -gt 0 ]; do
  case "$1" in
    --voice-nim) VOICE_NIM="1" ;;
    --voice-local) VOICE_LOCAL="1" ;;
    --voice-all) VOICE_NIM="1"; VOICE_LOCAL="1" ;;
    --torch-backend) shift; TORCH_BACKEND="$1" ;;
    --dry-run) DRY_RUN="1" ;;
    --help)
      echo "Usage: install.sh [options]"
      echo "  --voice-nim      Install NVIDIA NIM voice support"
      echo "  --voice-local    Install local Whisper voice support"
      echo "  --voice-all      Install both voice backends"
      echo "  --torch-backend  PyTorch backend (cpu/cuda)"
      echo "  --dry-run        Print commands without executing"
      exit 0
      ;;
    *) fail "Unknown option: $1" ;;
  esac
  shift
done

# ─── Welcome ────────────────────────────────────────────────────────────────
echo ""
echo "╔═══════════════════════════════════════════════╗"
echo "║        FC-Play — Zero Setup Installer         ║"
echo "║  Play with Claude — Free. Fast. Fabulous.     ║"
echo "╚═══════════════════════════════════════════════╝"
echo ""

# ─── 1. Ensure uv (fast Python package manager) ──────────────────────────
step "1/5 — Setting up uv..."
if command -v uv >/dev/null 2>&1; then
  UV_VERSION=$(uv version 2>/dev/null | head -1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
  echo "  ✓ uv found: v$UV_VERSION"
  if version_ge "$UV_VERSION" "$MIN_UV"; then
    echo "  → Updating uv..."
    run "uv self update 2>/dev/null || true"
  else
    fail "uv v$MIN_UV+ required (found v$UV_VERSION). Please upgrade: curl -LsSf https://astral.sh/uv/install.sh | sh"
  fi
else
  echo "  → Installing uv..."
  run "curl -LsSf https://astral.sh/uv/install.sh | sh"
  # Source uv
  . "$HOME/.cargo/env" 2>/dev/null || true
  export PATH="$HOME/.cargo/bin:$PATH"
  command -v uv >/dev/null 2>&1 || fail "uv installation failed"
fi

# ─── 2. Install Python ────────────────────────────────────────────────────
step "2/5 — Ensuring Python $PYTHON_VERSION..."
run "uv python install $PYTHON_VERSION 2>/dev/null || true"
echo "  ✓ Python $PYTHON_VERSION ready"

# ─── 3. Install FC-Play ──────────────────────────────────────────────────
step "3/5 — Installing FC-Play..."
EXTRAS=""
if [ -n "$VOICE_NIM" ] && [ -n "$VOICE_LOCAL" ]; then
  EXTRAS="[voice,voice_local]"
elif [ -n "$VOICE_NIM" ]; then
  EXTRAS="[voice]"
elif [ -n "$VOICE_LOCAL" ]; then
  EXTRAS="[voice_local]"
fi

TORCH_FLAG=""
if [ -n "$TORCH_BACKEND" ]; then
  TORCH_FLAG="--torch-backend $TORCH_BACKEND"
fi

run "uv tool install --force '${REPO}${EXTRAS}' $TORCH_FLAG"

# ─── 4. Create config directory ──────────────────────────────────────────
step "4/5 — Creating config directory..."
run "mkdir -p ~/.fc-play"
if [ ! -f ~/.fc-play/.env ]; then
  echo "  → Creating default .env..."
  # Copy default .env from installed package
  ENV_SRC=$(uv tool show fc-play 2>/dev/null | grep -oP '(?<=Location: ).*' | head -1)
  if [ -n "$ENV_SRC" ]; then
    ENV_FILE="$ENV_SRC/.env.example"
    [ -f "$ENV_FILE" ] && run "cp '$ENV_FILE' ~/.fc-play/.env" || echo "  ⚠ No .env.example found, skipping"
  fi
  echo "  ✓ Edit ~/.fc-play/.env to add your API keys"
else
  echo "  ✓ Config directory exists"
fi

# ─── 5. Verify installation ──────────────────────────────────────────────
step "5/5 — Verifying installation..."
if command -v fc-play >/dev/null 2>&1; then
  echo "  ✓ fc-play installed successfully!"
else
  fail "fc-play not found on PATH. Try: source ~/.bashrc"
fi

# ─── Done ──────────────────────────────────────────────────────────────────
echo ""
echo "╔═══════════════════════════════════════════════╗"
echo "║         🎉 FC-Play is ready to go!            ║"
echo "╚═══════════════════════════════════════════════╝"
echo ""
echo "  📝 Edit your config: nano ~/.fc-play/.env"
echo ""
echo "  🚀 Start the server:  fc-play server"
echo "  🖥️  Launch dashboard:  fc-play tui"
echo "  🌐 Open admin UI:     fc-play admin"
echo "  ℹ️  Check status:      fc-play status"
echo ""
echo "  🔗 Add your API key to ~/.fc-play/.env:"
echo "     CUSTOM_API_KEY=sk-ant-..."
echo "     CUSTOM_API_MODEL=claude-sonnet-4-20250514"
echo ""
echo "Need help? Open an issue: https://github.com/Alishahryar1/fc-play/issues"
echo ""
