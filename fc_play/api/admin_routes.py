"""FC-Play admin API routes — configuration and status endpoints."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
from loguru import logger

from fc_play.config.paths import config_file
from fc_play.config.settings import Settings, get_settings

router = APIRouter()

# ---------------------------------------------------------------------------
# Admin page
# ---------------------------------------------------------------------------


@router.get("", response_class=HTMLResponse, include_in_schema=False)
async def admin_page():
    """Serve the admin dashboard HTML."""
    html_path = Path(__file__).resolve().parent / "admin_static" / "index.html"
    if html_path.exists():
        return HTMLResponse(content=html_path.read_text(encoding="utf-8"))
    return HTMLResponse(content="<h1>Admin UI not found</h1>", status_code=404)


# ---------------------------------------------------------------------------
# Config API
# ---------------------------------------------------------------------------


def _build_field_spec(
    key: str,
    label: str,
    value: Any,
    field_type: str = "text",
    description: str = "",
    section: str = "general",
    advanced: bool = False,
    options: list[str] | None = None,
    placeholder: str = "",
    secret: bool = False,
) -> dict[str, Any]:
    """Build a field specification for the admin UI."""
    return {
        "key": key,
        "label": label,
        "value": value if value is not None else "",
        "type": field_type,
        "description": description,
        "section": section,
        "advanced": advanced,
        "options": options or [],
        "placeholder": placeholder,
        "secret": secret,
    }


def _get_config_spec(settings: Settings) -> dict[str, Any]:
    """Build the full configuration specification for the admin UI."""

    general_fields = [
        _build_field_spec("HOST", "Host", settings.host, description="Server bind address"),
        _build_field_spec("PORT", "Port", settings.port, field_type="number", description="Server port"),
        _build_field_spec("LOG_LEVEL", "Log Level", settings.log_level, options=["DEBUG", "INFO", "WARNING", "ERROR"], description="Logging verbosity"),
    ]

    api_fields = [
        _build_field_spec("CUSTOM_API_KEY", "Custom API Key", settings.custom_api_key, secret=True, section="api", placeholder="sk-ant-...", description="Anthropic API key for direct Claude access"),
        _build_field_spec("CUSTOM_API_BASE", "Custom API Base", settings.custom_api_base, section="api", description="Custom API base URL"),
        _build_field_spec("CUSTOM_API_MODEL", "Default Model", settings.custom_api_model, section="api", options=[
            "claude-opus-4-20250514",
            "claude-sonnet-4-20250514",
            "claude-haiku-4-20250514",
            "claude-opus-4-8",
            "claude-sonnet-4-6",
            "claude-haiku-4-5",
        ], description="Default Claude model for requests"),
        _build_field_spec("CUSTOM_API_TIMEOUT", "API Timeout (s)", settings.custom_api_timeout, field_type="number", section="api", description="Request timeout in seconds"),
    ]

    model_fields = [
        _build_field_spec("MODEL", "Fallback Model", settings.model, section="models", options=[
            "custom/claude-opus-4-20250514",
            "custom/claude-sonnet-4-20250514",
            "custom/claude-haiku-4-20250514",
            "openrouter/anthropic/claude-sonnet-4",
            "openrouter/anthropic/claude-opus-4",
            "openrouter/anthropic/claude-haiku-4",
            "gemini/gemini-2.0-flash",
            "deepseek/deepseek-chat",
            "mistral/mistral-large-latest",
            "groq/llama-3.3-70b-versatile",
        ], description="Fallback model when no tier override matches"),
        _build_field_spec("MODEL_OPUS", "Opus Model Override", settings.model_opus or "", section="models", description="Override for opus-tier requests"),
        _build_field_spec("MODEL_SONNET", "Sonnet Model Override", settings.model_sonnet or "", section="models", description="Override for sonnet-tier requests"),
        _build_field_spec("MODEL_HAIKU", "Haiku Model Override", settings.model_haiku or "", section="models", description="Override for haiku-tier requests"),
    ]

    provider_fields = [
        _build_field_spec("OPENAI_API_KEY", "OpenAI Key", settings.openai_api_key, secret=True, section="providers", placeholder="sk-..."),
        _build_field_spec("OPENROUTER_API_KEY", "OpenRouter Key", settings.openrouter_api_key, secret=True, section="providers", placeholder="sk-or-..."),
        _build_field_spec("GEMINI_API_KEY", "Gemini Key", settings.gemini_api_key, secret=True, section="providers", placeholder="AIza..."),
        _build_field_spec("DEEPSEEK_API_KEY", "DeepSeek Key", settings.deepseek_api_key, secret=True, section="providers", placeholder="sk-..."),
        _build_field_spec("MISTRAL_API_KEY", "Mistral Key", settings.mistral_api_key, secret=True, section="providers", placeholder="..."),
        _build_field_spec("GROQ_API_KEY", "Groq Key", settings.groq_api_key, secret=True, section="providers", placeholder="gsk_..."),
        _build_field_spec("FIREWORKS_API_KEY", "Fireworks Key", settings.fireworks_api_key, secret=True, section="providers", placeholder="fw_..."),
        _build_field_spec("TOGETHER_API_KEY", "Together Key", settings.together_api_key, secret=True, section="providers", placeholder="..."),
    ]

    thinking_fields = [
        _build_field_spec("ENABLE_THINKING", "Enable Thinking", settings.enable_thinking, field_type="boolean", section="thinking", description="Enable extended thinking for supported models"),
        _build_field_spec("ENABLE_OPUS_THINKING", "Opus Thinking", settings.enable_opus_thinking, field_type="boolean", section="thinking"),
        _build_field_spec("ENABLE_SONNET_THINKING", "Sonnet Thinking", settings.enable_sonnet_thinking, field_type="boolean", section="thinking"),
        _build_field_spec("ENABLE_HAIKU_THINKING", "Haiku Thinking", settings.enable_haiku_thinking, field_type="boolean", section="thinking"),
    ]

    rate_limit_fields = [
        _build_field_spec("RATE_LIMIT_REQUESTS", "Max Requests", settings.rate_limit_requests, field_type="number", section="rate_limiting", description="Max requests per window"),
        _build_field_spec("RATE_LIMIT_WINDOW", "Window (s)", settings.rate_limit_window, field_type="number", section="rate_limiting"),
        _build_field_spec("RATE_LIMIT_MAX_CONCURRENT", "Max Concurrent", settings.rate_limit_max_concurrent, field_type="number", section="rate_limiting"),
    ]

    advanced_fields = [
        _build_field_spec("ENABLE_WEB_SERVER_TOOLS", "Web Search Tools", settings.enable_web_server_tools, field_type="boolean", section="advanced", advanced=True, description="Enable web search/fetch tools (SSRF risk)"),
        _build_field_spec("WEB_FETCH_ALLOWED_SCHEMES", "Allowed URL Schemes", settings.web_fetch_allowed_schemes, section="advanced", advanced=True),
        _build_field_spec("BLOCK_PRIVATE_NETWORKS", "Block Private Networks", settings.block_private_networks, field_type="boolean", section="advanced", advanced=True),
        _build_field_spec("MAX_RETRIES", "Max Retries", settings.max_retries, field_type="number", section="advanced", advanced=True, description="Maximum API retry attempts"),
        _build_field_spec("BATCH_SIZE", "Batch Size", settings.batch_size, field_type="number", section="advanced", advanced=True),
    ]

    return {
        "sections": {
            "general": {"label": "General", "fields": general_fields},
            "api": {"label": "API Configuration", "fields": api_fields},
            "models": {"label": "Model Selection", "fields": model_fields},
            "providers": {"label": "Provider Keys", "fields": provider_fields},
            "thinking": {"label": "Thinking Settings", "fields": thinking_fields},
            "rate_limiting": {"label": "Rate Limiting", "fields": rate_limit_fields},
            "advanced": {"label": "Advanced", "fields": advanced_fields},
        },
        "provider_status": {
            "custom": {"status": "ok" if settings.custom_api_key else "warn", "label": "Custom API (Anthropic)"},
            "openai": {"status": "ok" if settings.openai_api_key else "warn", "label": "OpenAI"},
            "openrouter": {"status": "ok" if settings.openrouter_api_key else "warn", "label": "OpenRouter"},
            "gemini": {"status": "ok" if settings.gemini_api_key else "warn", "label": "Google Gemini"},
            "deepseek": {"status": "ok" if settings.deepseek_api_key else "warn", "label": "DeepSeek"},
            "mistral": {"status": "ok" if settings.mistral_api_key else "warn", "label": "Mistral AI"},
            "groq": {"status": "ok" if settings.groq_api_key else "warn", "label": "Groq"},
            "fireworks": {"status": "ok" if settings.fireworks_api_key else "warn", "label": "Fireworks AI"},
            "together": {"status": "ok" if settings.together_api_key else "warn", "label": "Together AI"},
        },
    }


@router.get("/api/config")
async def get_config():
    """Get the full configuration specification."""
    settings = get_settings()
    return _get_config_spec(settings)


@router.post("/api/config/validate")
async def validate_config(request: Request):
    """Validate configuration changes."""
    try:
        changes = await request.json()
        errors = []

        # Basic validation
        for key, value in changes.items():
            if key == "PORT":
                try:
                    port = int(value)
                    if port < 1 or port > 65535:
                        errors.append(f"PORT must be between 1-65535, got {port}")
                except (ValueError, TypeError):
                    errors.append(f"PORT must be a number, got {value}")

        if errors:
            return JSONResponse(content={"valid": False, "errors": errors}, status_code=422)
        return JSONResponse(content={"valid": True})
    except Exception as e:
        return JSONResponse(content={"valid": False, "errors": [str(e)]}, status_code=422)


@router.post("/api/config/apply")
async def apply_config(request: Request):
    """Apply configuration changes."""
    try:
        changes = await request.json()

        # Persist to config file
        cfg_path = config_file()
        existing = {}
        if cfg_path.exists():
            existing = json.loads(cfg_path.read_text(encoding="utf-8"))
        existing.update(changes)
        cfg_path.write_text(json.dumps(existing, indent=2), encoding="utf-8")

        logger.info("Config saved: {} keys updated", len(changes))
        return JSONResponse(content={"saved": True, "restart_required": True})
    except Exception as e:
        logger.error("Failed to save config: {}", e)
        return JSONResponse(content={"saved": False, "error": str(e)}, status_code=422)
