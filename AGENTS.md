# FC-Play Agent Instructions

This project is **fc-play** — a next-gen proxy & CLI toolkit for AI models.
Built with ❤️ by Fable No Mercy.

## Architecture

- `server.py` — Minimal ASGI entry point
- `fc_play/api/` — FastAPI routes, admin dashboard
- `fc_play/cli/` — Typer-based CLI interface
- `fc_play/config/` — Pydantic settings with env file support
- `fc_play/tui/` — Rich-based terminal dashboard
- `fc_play/providers/` — Provider adapters and routing
- `fc_play/core/` — Protocol helpers (Anthropic, OpenAI)
- `scripts/` — Install/uninstall/CI scripts

## Key Principles

1. **Beautiful UX** — Terminal and web UI must be stunning
2. **All models** — Never restrict Claude models
3. **Zero friction** — Install in one command, configure in one file
4. **No type ignores** — Fix types, don't suppress them
5. **Perfect execution** — Every commit must pass CI
