"""FC-Play admin API — configuration endpoints with key pool support."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
from loguru import logger

from fc_play.config.constants import PROVIDERS
from fc_play.config.paths import config_file
from fc_play.config.settings import Settings, get_settings
from fc_play.providers.router import provider_health

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


@router.get("/api/config")
async def get_config():
    """Get the full configuration specification."""
    settings = get_settings()
    prov = settings.configured_providers()

    provider_status = {}
    for pid, display in PROVIDERS.items():
        has_key = prov.get(pid, False)
        key_count = settings.provider_key_count(pid)
        key_summary = settings.provider_key_summary(pid)
        if pid in ("ollama", "lmstudio", "llamacpp"):
            provider_status[pid] = {"status": "on", "label": display, "keys": [{"index": 1, "masked": "—", "has_value": False}]}
        else:
            provider_status[pid] = {
                "status": "on" if has_key else "warn",
                "label": display,
                "keys": key_summary,
                "key_count": key_count,
            }

    model_opts = [
        "custom/claude-opus-4-20250514", "custom/claude-sonnet-4-20250514",
        "custom/claude-haiku-4-20250514", "custom/claude-opus-4-8",
        "custom/claude-sonnet-4-6", "custom/claude-haiku-4-5",
        "openrouter/anthropic/claude-sonnet-4", "openrouter/anthropic/claude-opus-4",
        "openrouter/anthropic/claude-haiku-4", "openai/gpt-4o",
        "openai/gpt-4o-mini", "gemini/gemini-2.0-flash",
        "gemini/gemini-2.0-flash-lite", "deepseek/deepseek-chat",
        "mistral/mistral-large-latest", "groq/llama-3.3-70b-versatile",
        "fireworks/llama-v3p1-405b-instruct", "together/meta-llama-3.1-405b-instruct",
        "nvidia_nim/nvidia/nemotron-4-340b-instruct", "cerebras/llama-3.3-70b",
    ]

    return {
        "sections": {
            "general": {"label": "General", "fields": [
                f_spec("HOST", "Host", settings.host, desc="Bind address"),
                f_spec("PORT", "Port", settings.port, "number", desc="Server port"),
                f_spec("LOG_LEVEL", "Log Level", settings.log_level, "select",
                       options=["DEBUG","INFO","WARNING","ERROR"], desc="Verbosity"),
            ]},
            "api": {"label": "Direct API", "fields": [
                f_spec("ANTHROPIC_API_KEY", "Anthropic Key", settings.anthropic_api_key, "secret", section="api", ph="sk-ant-..."),
                f_spec("OPENAI_API_KEY", "OpenAI Key", settings.openai_api_key, "secret", section="api", ph="sk-..."),
                f_spec("OPENROUTER_API_KEY", "OpenRouter Key", settings.openrouter_api_key, "secret", section="api", ph="sk-or-..."),
                f_spec("GEMINI_API_KEY", "Gemini Key", settings.gemini_api_key, "secret", section="api", ph="AIza..."),
                f_spec("DEEPSEEK_API_KEY", "DeepSeek Key", settings.deepseek_api_key, "secret", section="api", ph="sk-..."),
                f_spec("MISTRAL_API_KEY", "Mistral Key", settings.mistral_api_key, "secret", section="api"),
                f_spec("CODESTRAL_API_KEY", "Codestral Key", settings.codestral_api_key, "secret", section="api"),
                f_spec("GROQ_API_KEY", "Groq Key", settings.groq_api_key, "secret", section="api", ph="gsk_..."),
                f_spec("FIREWORKS_API_KEY", "Fireworks Key", settings.fireworks_api_key, "secret", section="api", ph="fw_..."),
                f_spec("TOGETHER_API_KEY", "Together Key", settings.together_api_key, "secret", section="api"),
                f_spec("NVIDIA_NIM_API_KEY", "NVIDIA NIM Key", settings.nvidia_nim_api_key, "secret", section="api"),
                f_spec("CEREBRAS_API_KEY", "Cerebras Key", settings.cerebras_api_key, "secret", section="api"),
                f_spec("KIMI_API_KEY", "Kimi Key", settings.kimi_api_key, "secret", section="api"),
                f_spec("WAFER_API_KEY", "Wafer Key", settings.wafer_api_key, "secret", section="api"),
                f_spec("OPENCODE_API_KEY", "OpenCode Key", settings.opencode_api_key, "secret", section="api"),
                f_spec("ZAI_API_KEY", "Z.ai Key", settings.zai_api_key, "secret", section="api"),
            ]},
            "providers": {"label": "Local Providers", "fields": [
                f_spec("OLLAMA_BASE_URL", "Ollama URL", settings.ollama_base_url, section="providers", desc="http://localhost:11434"),
                f_spec("LMSTUDIO_BASE_URL", "LM Studio URL", settings.lmstudio_base_url, section="providers", desc="http://localhost:1234/v1"),
                f_spec("LLAMACPP_BASE_URL", "llama.cpp URL", settings.llamacpp_base_url, section="providers", desc="http://localhost:8080/v1"),
                f_spec("NVIDIA_NIM_BASE_URL", "NVIDIA NIM URL", settings.nvidia_nim_base_url, section="providers"),
            ]},
            "models": {"label": "Model Routing", "fields": [
                f_spec("MODEL", "Fallback Model", settings.model, "select",
                       options=model_opts, section="models",
                       desc="Default when no tier matches"),
                f_spec("MODEL_OPUS", "Opus-tier Override", settings.model_opus or "", "select",
                       options=model_opts, section="models"),
                f_spec("MODEL_SONNET", "Sonnet-tier Override", settings.model_sonnet or "", "select",
                       options=model_opts, section="models"),
                f_spec("MODEL_HAIKU", "Haiku-tier Override", settings.model_haiku or "", "select",
                       options=model_opts, section="models"),
            ]},
            "thinking": {"label": "Extended Thinking", "fields": [
                f_spec("ENABLE_THINKING", "Enable Thinking", settings.enable_thinking, "boolean", section="thinking"),
                f_spec("ENABLE_OPUS_THINKING", "Opus Thinking", settings.enable_opus_thinking, "boolean", section="thinking"),
                f_spec("ENABLE_SONNET_THINKING", "Sonnet Thinking", settings.enable_sonnet_thinking, "boolean", section="thinking"),
                f_spec("ENABLE_HAIKU_THINKING", "Haiku Thinking", settings.enable_haiku_thinking, "boolean", section="thinking"),
            ]},
            "rate_limiting": {"label": "Rate Limiting", "fields": [
                f_spec("RATE_LIMIT_REQUESTS", "Max Requests", settings.rate_limit_requests, "number", section="rate_limiting"),
                f_spec("RATE_LIMIT_WINDOW", "Window (s)", settings.rate_limit_window, "number", section="rate_limiting"),
                f_spec("RATE_LIMIT_MAX_CONCURRENT", "Max Concurrent", settings.rate_limit_max_concurrent, "number", section="rate_limiting"),
            ]},
            "advanced": {"label": "Advanced", "fields": [
                f_spec("ENABLE_WEB_SERVER_TOOLS", "Web Tools", settings.enable_web_server_tools, "boolean", section="advanced", adv=True),
                f_spec("BLOCK_PRIVATE_NETWORKS", "Block Private Networks", settings.block_private_networks, "boolean", section="advanced", adv=True),
                f_spec("MAX_RETRIES", "Max Retries", settings.max_retries, "number", section="advanced", adv=True),
                f_spec("TIMEOUT_READ", "Read Timeout", settings.timeout_read, "number", section="advanced", adv=True),
                f_spec("TIMEOUT_WRITE", "Write Timeout", settings.timeout_write, "number", section="advanced", adv=True),
                f_spec("TIMEOUT_CONNECT", "Connect Timeout", settings.timeout_connect, "number", section="advanced", adv=True),
            ]},
        },
        "provider_status": provider_status,
    }


def f_spec(
    key: str, label: str, value: Any,
    ftype: str = "text",
    section: str = "general",
    adv: bool = False,
    options: list[str] | None = None,
    ph: str = "",
    desc: str = "",
    secret: bool = False,
) -> dict:
    """Build a field spec."""
    if ftype == "secret":
        secret = True
        ftype = "text"
    return {
        "key": key, "label": label,
        "value": value if value is not None else "",
        "type": ftype, "section": section,
        "advanced": adv, "options": options or [],
        "placeholder": ph, "description": desc, "secret": secret,
    }


# ---------------------------------------------------------------------------
# Validate & Apply
# ---------------------------------------------------------------------------

@router.get("/api/keys")
async def get_key_health():
    """Get key pool health for admin UI."""
    return JSONResponse(content={"providers": provider_health()})


@router.post("/api/config/validate")
async def validate_config(request: Request):
    try:
        changes = await request.json()
        errors = []
        for key, value in changes.items():
            if key == "PORT":
                try:
                    p = int(value)
                    if p < 1 or p > 65535:
                        errors.append(f"PORT must be 1-65535, got {p}")
                except (ValueError, TypeError):
                    errors.append(f"PORT must be a number, got {value}")
        if errors:
            return JSONResponse(content={"valid": False, "errors": errors}, status_code=422)
        return JSONResponse(content={"valid": True})
    except Exception as e:
        return JSONResponse(content={"valid": False, "errors": [str(e)]}, status_code=422)


@router.post("/api/config/apply")
async def apply_config(request: Request):
    try:
        changes = await request.json()
        cfg = config_file()
        existing = {}
        if cfg.exists():
            existing = json.loads(cfg.read_text(encoding="utf-8"))
        existing.update(changes)
        cfg.write_text(json.dumps(existing, indent=2), encoding="utf-8")
        logger.info("Config saved: {} keys", len(changes))
        return JSONResponse(content={"saved": True, "restart_required": True})
    except Exception as e:
        logger.error("Save failed: {}", e)
        return JSONResponse(content={"saved": False, "error": str(e)}, status_code=422)
