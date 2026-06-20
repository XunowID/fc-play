#!/bin/sh
# =============================================================================
# FC-Play Uninstaller
# =============================================================================

set -e

echo "Removing FC-Play..."

# Remove uv tool
uv tool uninstall fc-play 2>/dev/null || true

# Remove config directory
rm -rf ~/.fc-play

echo "✅ FC-Play has been uninstalled."
echo "   Config directory ~/.fc-play/ removed."
echo "   Any Claude Code installations were not modified."
