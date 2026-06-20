# FC-Play Architecture

## Overview

FC-Play is a proxy server and CLI toolkit that intercepts API calls from AI clients (Claude Code, Codex CLI, VS Code extensions) and routes them through configurable model providers. It provides a unified interface to access any AI model through a single API endpoint.

## Core Flow

```
Client (Claude Code / Codex CLI)
  │
  ▼
FC-Play Proxy (FastAPI server)
  │
  ├── Custom API (Direct Anthropic)
  ├── OpenAI API
  ├── OpenRouter
  ├── Gemini
  ├── DeepSeek
  ├── Mistral
  └── Groq / Together / etc.
```

## Key Components

### 1. API Layer (`fc_play/api/`)
- **server.py** — ASGI entry point (uvicorn)
- **app.py** — FastAPI app factory with lifespan management
- **routes.py** — Proxy endpoints for `/v1/messages`, `/v1/models`, etc.
- **admin_routes.py** — Configuration API endpoints
- **admin_static/** — Beautiful web admin dashboard

### 2. CLI Layer (`fc_play/cli/`)
- **entrypoints.py** — Typer commands: `server`, `tui`, `admin`, `status`
- **launchers/** — Process management for claude/codex launchers

### 3. TUI Layer (`fc_play/tui/`)
- **app.py** — Interactive dashboard with live refresh
- **panels.py** — Status, model table, request log components
- **themes.py** — Midnight, Emerald, Ruby design themes

### 4. Config (`fc_play/config/`)
- **settings.py** — Pydantic BaseSettings with `.env` support
- **paths.py** — Data directory management (`~/.fc-play/`)
- **constants.py** — Model lists, branding, HTTP defaults

### 5. Providers (`fc_play/providers/`)
- Provider transports for different API formats
- Rate limiting, error mapping, model listing

## Design Decisions

- **Python 3.12+** — Modern language features without 3.14 instability
- **No type: ignore** — Every type is resolved properly
- **Rich-based TUI** — Beautiful terminal dashboard with Live rendering
- **Glassmorphism admin** — Modern web UI with blur effects
- **One .env file** — All config in `~/.fc-play/.env`, no database needed
