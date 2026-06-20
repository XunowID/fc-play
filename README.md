# 🎮 FC-Play — Play with Claude. Free. Fast. Fabulous.

> **The next-gen CLI & proxy for Claude, OpenAI, and everything AI.**
> Built from the ground up with beautiful UX, all models unlocked, and zero configuration pain.

<p align="center">
  <img src="https://img.shields.io/badge/python-3.12+-blue?style=flat&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/license-MIT-green?style=flat" alt="MIT License">
  <img src="https://img.shields.io/badge/status-active-brightgreen?style=flat" alt="Status">
</p>

---

## ✨ What is FC-Play?

**FC-Play** is a beautiful terminal proxy and CLI toolkit that lets you use **Claude Code**, **OpenAI Codex**, and any AI tool — with **any model**, **any provider**, through a **single command**.

Unlike the original `free-claude-code`, FC-Play focuses on:

| Feature | FC-Play | Others |
|---------|---------|--------|
| **Terminal UI** | 🎨 Rich TUI dashboard | ❌ Raw CLI |
| **Admin UI** | 🌟 Modern glassmorphism design | ⚙️ Basic |
| **All Claude models** | ✅ Opus 4.8, Sonnet 4.6, Haiku 4.5, + more | ⚠️ Limited |
| **Custom API** | ✅ First-class Anthropic API support | ⚠️ Provider-focused |
| **Installation** | 🚀 One command, zero fuss | 📦 Multi-step |
| **Theme system** | 🎭 Midnight, Emerald, Ruby themes | ❌ None |

---

## 🚀 Quick Start

### One-Command Install

**macOS / Linux:**
```bash
curl -fsSL https://raw.githubusercontent.com/Alishahryar1/fc-play/main/scripts/install.sh | sh
```

**Windows (PowerShell):**
```powershell
Invoke-Expression (Invoke-WebRequest -Uri "https://raw.githubusercontent.com/Alishahryar1/fc-play/main/scripts/install.ps1").Content
```

### Or install from source

```bash
git clone https://github.com/Alishahryar1/fc-play.git
cd fc-play
uv sync
```

---

## 🎯 Your First 5 Minutes

### 1. Add your API key

```bash
echo "CUSTOM_API_KEY=sk-ant-your-key-here" >> ~/.fc-play/.env
echo "CUSTOM_API_MODEL=claude-sonnet-4-20250514" >> ~/.fc-play/.env
```

### 2. Start the server

```bash
fc-play server
```

### 3. Launch the beautiful TUI dashboard

```bash
fc-play tui
```

Or open the admin web UI:

```bash
fc-play admin
```

---

## 🎨 Commands at a Glance

```bash
# Start the proxy server
fc-play server

# Launch interactive terminal dashboard
fc-play tui --theme midnight

# Open admin web UI
fc-play admin

# Check configuration status
fc-play status

# Show version
fc-play version
```

---

## 🧩 Supported Models

FC-Play supports **every Claude model** — including those "hidden" by Anthropic's API versioning:

| Model Family | Models |
|---|---|
| **Claude Opus 4** | `claude-opus-4-20250514`, `claude-opus-4-8`, `claude-opus-4-7`, `claude-opus-4-6`, `claude-opus-4-5` |
| **Claude Opus 3** | `claude-opus-3-5`, `claude-opus-3` |
| **Claude Sonnet 4** | `claude-sonnet-4-20250514`, `claude-sonnet-4-6` |
| **Claude Sonnet 3** | `claude-sonnet-3-5`, `claude-sonnet-3`, `claude-3-5-sonnet` |
| **Claude Haiku 4** | `claude-haiku-4-20250514`, `claude-haiku-4-5`, `claude-haiku-4-6` |
| **Claude Haiku 3** | `claude-haiku-3-5`, `claude-haiku-3` |

Plus any model via **Custom API** or through **OpenRouter**, **Together AI**, **Groq**, **Gemini**, **DeepSeek**, and more.

---

## 🖥️ Themes

FC-Play comes with three beautiful terminal themes:

| Theme | Style |
|---|---|
| `midnight` 🌙 | Indigo primary, dark OLED, purple accents |
| `emerald` 🌿 | Green primary, dark surface, emerald accents |
| `ruby` 💎 | Crimson primary, warm dark, rose accents |

```bash
fc-play tui --theme emerald
```

---

## ⚙️ Configuration

Configuration is managed through `~/.fc-play/.env` or the admin web UI.

### Essential config

```env
# Server
PORT=8083
HOST=0.0.0.0

# Your Anthropic API key (for direct Claude access)
CUSTOM_API_KEY=sk-ant-...
CUSTOM_API_MODEL=claude-sonnet-4-20250514

# Model tier overrides
MODEL_OPUS=custom/claude-opus-4-20250514
MODEL_SONNET=custom/claude-sonnet-4-20250514
MODEL_HAIKU=custom/claude-haiku-4-20250514

# Rate limiting
RATE_LIMIT_REQUESTS=60
RATE_LIMIT_WINDOW=60

# Extended thinking
ENABLE_THINKING=true
```

### Provider API keys

```env
OPENAI_API_KEY=sk-...
OPENROUTER_API_KEY=sk-or-...
GEMINI_API_KEY=AIza...
DEEPSEEK_API_KEY=sk-...
MISTRAL_API_KEY=...
GROQ_API_KEY=gsk_...
```

---

## 🏗️ Architecture

```
fc-play/
├── server.py              # ASGI entry point
├── fc_play/               # Main package
│   ├── api/               # FastAPI routes, admin UI
│   │   └── admin_static/  # 🎨 Beautiful admin dashboard
│   ├── cli/               # CLI entrypoints (typer)
│   ├── config/            # Pydantic settings, paths
│   ├── core/              # Protocol handlers (Anthropic, OpenAI)
│   ├── providers/         # Provider transports & registry
│   └── tui/               # 🎨 Terminal UI (Rich-based)
├── scripts/               # Install/uninstall/CI scripts
└── tests/                 # Test suite
```

---

## 🛠️ Development

```bash
git clone https://github.com/Alishahryar1/fc-play.git
cd fc-play
uv sync
uv run ruff format .
uv run ruff check --fix .
uv run mypy fc_play/
uv run pytest -v
```

---

## 🔒 License

MIT — do what you want, just don't blame us.

---

## 🙏 Acknowledgements

Built with ❤️ by **Fable No Mercy** — inspired by the original `free-claude-code` project, rebuilt with better UX, more models, and zero excuses.

> *"Perfect is the way we work. Failure is not our place."*
