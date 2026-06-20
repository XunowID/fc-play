#!/bin/sh
# =============================================================================
# FC-Play CI — Format, Lint, Type Check, Test
# =============================================================================

set -e

echo "╔═══════════════════════════════════════════════╗"
echo "║          FC-Play CI Pipeline                   ║"
echo "╚═══════════════════════════════════════════════╝"
echo ""

# ─── Configuration ──────────────────────────────────────────────────────────
RUN_FORMAT=true
RUN_LINT=true
RUN_TYPE_CHECK=true
RUN_TESTS=true
CHECK_ONLY=false

# Parse args
for arg in "$@"; do
  case "$arg" in
    --only) RUN_FORMAT=false; RUN_LINT=false; RUN_TYPE_CHECK=false; RUN_TESTS=false ;;
    --skip-format) RUN_FORMAT=false ;;
    --skip-lint) RUN_LINT=false ;;
    --skip-type) RUN_TYPE_CHECK=false ;;
    --skip-tests) RUN_TESTS=false ;;
    --check) CHECK_ONLY=true ;;
    --help)
      echo "Usage: ci.sh [options]"
      echo "  --check       Run format check (no auto-fix)"
      echo "  --skip-format Skip formatting"
      echo "  --skip-lint   Skip linting"
      echo "  --skip-type   Skip type checking"
      echo "  --skip-tests  Skip tests"
      echo "  --only        Run only the specified checks (skip all by default)"
      echo "  --help        Show this help"
      exit 0
      ;;
  esac
done

# ─── 1. Format ──────────────────────────────────────────────────────────────
if [ "$RUN_FORMAT" = true ]; then
  echo "✦ Formatting..."
  if [ "$CHECK_ONLY" = true ]; then
    uv run ruff format --check .
  else
    uv run ruff format .
  fi
  echo "  ✓ Format $([ "$CHECK_ONLY" = true ] && echo 'check' || echo '')passed"
fi

# ─── 2. Lint ────────────────────────────────────────────────────────────────
if [ "$RUN_LINT" = true ]; then
  echo "✦ Linting..."
  uv run ruff check --fix .
  echo "  ✓ Lint passed"
fi

# ─── 3. Type Check ──────────────────────────────────────────────────────────
if [ "$RUN_TYPE_CHECK" = true ]; then
  echo "✦ Type checking..."
  uv run mypy fc_play/
  echo "  ✓ Types passed"
fi

# ─── 4. Tests ───────────────────────────────────────────────────────────────
if [ "$RUN_TESTS" = true ]; then
  echo "✦ Running tests..."
  uv run pytest -v --tb=short
  echo "  ✓ Tests passed"
fi

echo ""
echo "╔═══════════════════════════════════════════════╗"
echo "║          ✅ CI Pipeline Complete              ║"
echo "╚═══════════════════════════════════════════════╝"
