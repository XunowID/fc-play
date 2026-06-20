"""FC-Play constants."""

from __future__ import annotations

# Branding
APP_NAME = "fc-play"
APP_DISPLAY = "FC-Play"
APP_TAGLINE = "Play with Claude — Free. Fast. Fabulous."

# HTTP
HTTP_READ_TIMEOUT = 120
HTTP_WRITE_TIMEOUT = 10
HTTP_CONNECT_TIMEOUT = 30

# Model families
CLAUDE_OPUS_MODELS = [
    "claude-opus-4-20250514",
    "claude-opus-4-20250514-v1",
    "claude-opus-4-8-20250601",
    "claude-opus-4-8",
    "claude-opus-4-7",
    "claude-opus-4-6",
    "claude-opus-4-5",
    "claude-opus-4",
    "claude-opus-3-5",
    "claude-opus-3",
]

CLAUDE_SONNET_MODELS = [
    "claude-sonnet-4-20250514",
    "claude-sonnet-4-20250514-v1",
    "claude-sonnet-4-6",
    "claude-sonnet-4",
    "claude-sonnet-3-5",
    "claude-sonnet-3",
    "claude-3-5-sonnet",
    "claude-3-sonnet",
]

CLAUDE_HAIKU_MODELS = [
    "claude-haiku-4-20250514",
    "claude-haiku-4-20250514-v1",
    "claude-haiku-4-5",
    "claude-haiku-4-6",
    "claude-haiku-4",
    "claude-haiku-3-5",
    "claude-haiku-3",
]

CLAUDE_MODELS = CLAUDE_OPUS_MODELS + CLAUDE_SONNET_MODELS + CLAUDE_HAIKU_MODELS

# Provider prefixes
PROVIDER_PREFIXES = {
    "custom": "Custom API (Anthropic)",
    "openai": "OpenAI",
    "openrouter": "OpenRouter",
    "gemini": "Google Gemini",
    "deepseek": "DeepSeek",
    "mistral": "Mistral AI",
    "groq": "Groq",
    "fireworks": "Fireworks AI",
    "together": "Together AI",
}
