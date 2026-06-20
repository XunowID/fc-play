"""Admin UI configuration manifest and managed env persistence."""

from __future__ import annotations

import os
from dataclasses import dataclass
from io import StringIO
from pathlib import Path
from typing import Any, Literal

from dotenv import dotenv_values
from pydantic import ValidationError

from fc_play.config.paths import data_dir
from fc_play.config.settings import Settings

FieldType = Literal["text", "secret", "number", "boolean", "select", "textarea"]
SourceType = Literal["default", "template", "repo_env", "managed_env", "explicit_env_file", "process"]

MASKED_SECRET = "********"


@dataclass(frozen=True)
class ConfigSectionSpec:
    section_id: str
    label: str
    description: str
    advanced: bool = False


@dataclass(frozen=True)
class ConfigFieldSpec:
    key: str
    label: str
    section_id: str
    field_type: FieldType = "text"
    default: str = ""
    options: tuple[str, ...] = ()
    secret: bool = False
    advanced: bool = False
    restart_required: bool = False
    description: str = ""


SECTIONS: tuple[ConfigSectionSpec, ...] = (
    ConfigSectionSpec("api", "API Keys", "Provider API keys for routing."),
    ConfigSectionSpec("providers", "Local Providers", "Base URLs for self-hosted providers."),
    ConfigSectionSpec("models", "Model Routing", "Provider-prefixed models for Claude model tiers."),
    ConfigSectionSpec("thinking", "Extended Thinking", "Global and tier-specific thinking."),
    ConfigSectionSpec("general", "General", "Server host, port, and log level.", advanced=False),
    ConfigSectionSpec("rate_limiting", "Rate Limiting", "Request limits and concurrency."),
    ConfigSectionSpec("advanced", "Advanced", "Timeouts, retries, and web tools.", advanced=True),
)

FIELDS: tuple[ConfigFieldSpec, ...] = (
    # ── API Keys ──────────────────────────────────────────────────────────
    ConfigFieldSpec("ANTHROPIC_API_KEY", "Anthropic Key", "api", "secret", secret=True, description="sk-ant-..."),
    ConfigFieldSpec("OPENAI_API_KEY", "OpenAI Key", "api", "secret", secret=True, description="sk-..."),
    ConfigFieldSpec("OPENROUTER_API_KEY", "OpenRouter Key", "api", "secret", secret=True, description="sk-or-..."),
    ConfigFieldSpec("GEMINI_API_KEY", "Gemini Key", "api", "secret", secret=True, description="AIza..."),
    ConfigFieldSpec("DEEPSEEK_API_KEY", "DeepSeek Key", "api", "secret", secret=True, description="sk-..."),
    ConfigFieldSpec("MISTRAL_API_KEY", "Mistral Key", "api", "secret", secret=True),
    ConfigFieldSpec("CODESTRAL_API_KEY", "Codestral Key", "api", "secret", secret=True),
    ConfigFieldSpec("GROQ_API_KEY", "Groq Key", "api", "secret", secret=True, description="gsk_..."),
    ConfigFieldSpec("FIREWORKS_API_KEY", "Fireworks Key", "api", "secret", secret=True, description="fw_..."),
    ConfigFieldSpec("TOGETHER_API_KEY", "Together Key", "api", "secret", secret=True),
    ConfigFieldSpec("NVIDIA_NIM_API_KEY", "NVIDIA NIM Key", "api", "secret", secret=True),
    ConfigFieldSpec("CEREBRAS_API_KEY", "Cerebras Key", "api", "secret", secret=True),
    ConfigFieldSpec("KIMI_API_KEY", "Kimi Key", "api", "secret", secret=True),
    ConfigFieldSpec("WAFER_API_KEY", "Wafer Key", "api", "secret", secret=True),
    ConfigFieldSpec("OPENCODE_API_KEY", "OpenCode Key", "api", "secret", secret=True),
    ConfigFieldSpec("ZAI_API_KEY", "Z.ai Key", "api", "secret", secret=True),
    # ── Local Providers ───────────────────────────────────────────────────
    ConfigFieldSpec("OLLAMA_BASE_URL", "Ollama URL", "providers", description="http://localhost:11434"),
    ConfigFieldSpec("LMSTUDIO_BASE_URL", "LM Studio URL", "providers", description="http://localhost:1234/v1"),
    ConfigFieldSpec("LLAMACPP_BASE_URL", "llama.cpp URL", "providers", description="http://localhost:8080/v1"),
    ConfigFieldSpec("NVIDIA_NIM_BASE_URL", "NVIDIA NIM URL", "providers", description="https://integrate.api.nvidia.com/v1"),
    # ── Model Routing ─────────────────────────────────────────────────────
    ConfigFieldSpec("MODEL", "Default Model", "models", "select",
                    default="custom/claude-sonnet-4-20250514", options=(
                        "custom/claude-opus-4-20250514", "custom/claude-sonnet-4-20250514",
                        "custom/claude-haiku-4-20250514", "custom/claude-opus-4-8",
                        "custom/claude-sonnet-4-6", "custom/claude-haiku-4-5",
                        "openrouter/anthropic/claude-sonnet-4", "openai/gpt-4o",
                        "gemini/gemini-2.0-flash", "deepseek/deepseek-chat",
                        "mistral/mistral-large-latest", "groq/llama-3.3-70b-versatile",
                    )),
    ConfigFieldSpec("MODEL_OPUS", "Opus Override", "models", "select", options=(
        "custom/claude-opus-4-20250514", "custom/claude-opus-4-8",
        "openrouter/anthropic/claude-opus-4", "")),
    ConfigFieldSpec("MODEL_SONNET", "Sonnet Override", "models", "select", options=(
        "custom/claude-sonnet-4-20250514", "custom/claude-sonnet-4-6",
        "openrouter/anthropic/claude-sonnet-4", "")),
    ConfigFieldSpec("MODEL_HAIKU", "Haiku Override", "models", "select", options=(
        "custom/claude-haiku-4-20250514", "custom/claude-haiku-4-5",
        "openrouter/anthropic/claude-haiku-4", "")),
    # ── Extended Thinking ─────────────────────────────────────────────────
    ConfigFieldSpec("ENABLE_THINKING", "Enable Thinking", "thinking", "boolean"),
    ConfigFieldSpec("ENABLE_OPUS_THINKING", "Opus Thinking", "thinking", "boolean"),
    ConfigFieldSpec("ENABLE_SONNET_THINKING", "Sonnet Thinking", "thinking", "boolean"),
    ConfigFieldSpec("ENABLE_HAIKU_THINKING", "Haiku Thinking", "thinking", "boolean"),
    # ── General ───────────────────────────────────────────────────────────
    ConfigFieldSpec("HOST", "Host", "general", default="0.0.0.0", restart_required=True),
    ConfigFieldSpec("PORT", "Port", "general", "number", default="3010", restart_required=True),
    ConfigFieldSpec("LOG_LEVEL", "Log Level", "general", "select", default="INFO", options=("DEBUG", "INFO", "WARNING", "ERROR")),
    # ── Rate Limiting ─────────────────────────────────────────────────────
    ConfigFieldSpec("RATE_LIMIT_REQUESTS", "Max Requests", "rate_limiting", "number", default="60"),
    ConfigFieldSpec("RATE_LIMIT_WINDOW", "Window (s)", "rate_limiting", "number", default="60"),
    ConfigFieldSpec("RATE_LIMIT_MAX_CONCURRENT", "Max Concurrent", "rate_limiting", "number", default="10"),
    # ── Advanced ──────────────────────────────────────────────────────────
    ConfigFieldSpec("MAX_RETRIES", "Max Retries", "advanced", "number", default="3"),
    ConfigFieldSpec("TIMEOUT_READ", "Read Timeout (s)", "advanced", "number", default="120"),
    ConfigFieldSpec("TIMEOUT_WRITE", "Write Timeout (s)", "advanced", "number", default="10"),
    ConfigFieldSpec("TIMEOUT_CONNECT", "Connect Timeout (s)", "advanced", "number", default="30"),
    ConfigFieldSpec("ENABLE_WEB_SERVER_TOOLS", "Web Server Tools", "advanced", "boolean"),
    ConfigFieldSpec("BLOCK_PRIVATE_NETWORKS", "Block Private Networks", "advanced", "boolean"),
)

FIELD_BY_KEY = {f.key: f for f in FIELDS}


def managed_env_path() -> Path:
    return data_dir() / ".env"


def repo_env_path() -> Path:
    return Path(__file__).resolve().parent.parent.parent / ".env"


def _dotenv_values_from_file(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {}
    values = dotenv_values(path)
    return {key: "" if value is None else value for key, value in values.items()}


def _dotenv_values_from_text(text: str) -> dict[str, str]:
    values = dotenv_values(stream=StringIO(text))
    return {key: "" if value is None else value for key, value in values.items()}


def _is_locked_source(source: SourceType) -> bool:
    return source in ("process", "explicit_env_file")


def _normalize_for_env(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def _display_value(field: ConfigFieldSpec, value: str) -> str:
    if field.secret and value:
        return MASKED_SECRET
    return value


def template_values() -> dict[str, str]:
    """Return default values for all known fields."""
    values: dict[str, str] = {}
    for field in FIELDS:
        values[field.key] = field.default
    return values


def _load_value_state() -> dict[str, dict[str, Any]]:
    values = template_values()
    sources: dict[str, SourceType] = {key: "template" for key in FIELD_BY_KEY}

    # Read from repo .env
    repo_values = _dotenv_values_from_file(repo_env_path())
    for key, value in repo_values.items():
        if key in FIELD_BY_KEY:
            values[key] = value
            sources[key] = "repo_env"

    # Read from managed ~/.fc-play/.env (highest precedence among files)
    managed_values = _dotenv_values_from_file(managed_env_path())
    for key, value in managed_values.items():
        if key in FIELD_BY_KEY:
            values[key] = value
            sources[key] = "managed_env"

    # Process env vars override everything
    for key in FIELD_BY_KEY:
        if key in os.environ:
            values[key] = os.environ[key]
            sources[key] = "process"

    return {
        key: {
            "value": values.get(key, ""),
            "source": sources.get(key, "default"),
        }
        for key in FIELD_BY_KEY
    }


def load_config_response() -> dict[str, Any]:
    """Return manifest and current config values for the admin UI."""
    state = _load_value_state()
    fields: list[dict[str, Any]] = []
    for field in FIELDS:
        entry = state[field.key]
        source = entry["source"]
        raw_value = entry["value"]
        fields.append({
            "key": field.key,
            "label": field.label,
            "section": field.section_id,
            "type": field.field_type,
            "value": _display_value(field, raw_value),
            "configured": bool(str(raw_value).strip()),
            "source": source,
            "locked": _is_locked_source(source),
            "secret": field.secret,
            "advanced": field.advanced,
            "restart_required": field.restart_required,
            "options": list(field.options),
            "description": field.description,
        })

    # Build provider status
    provider_status = _provider_status(state)

    return {
        "sections": [
            {
                "id": s.section_id,
                "label": s.label,
                "description": s.description,
                "advanced": s.advanced,
            }
            for s in SECTIONS
        ],
        "fields": fields,
        "provider_status": provider_status,
    }


def _provider_status(state: dict[str, dict[str, Any]]) -> dict[str, dict]:
    """Build provider status from current config values."""
    from fc_play.config.constants import PROVIDERS

    status = {}
    for pid, display in PROVIDERS.items():
        if pid in ("ollama", "lmstudio", "llamacpp"):
            url_key = f"{pid.upper()}_BASE_URL"
            url_val = state.get(url_key, {}).get("value", "")
            status[pid] = {
                "status": "on" if url_val.strip() else "warn",
                "label": display,
                "keys": [{"index": 1, "masked": url_val or "—", "has_value": bool(url_val)}],
            }
        else:
            key_env = f"{pid.upper()}_API_KEY"
            entry = state.get(key_env, {})
            raw = entry.get("value", "")
            has_key = bool(str(raw).strip())
            # Show masked or raw key
            masked = _display_value(FIELD_BY_KEY.get(key_env), str(raw)) if FIELD_BY_KEY.get(key_env) else ("••••" if has_key else "")
            status[pid] = {
                "status": "on" if has_key else "warn",
                "label": display,
                "keys": [{"index": 1, "masked": masked, "has_value": has_key}],
            }
    return status


def _target_values_with_updates(updates: dict[str, Any]) -> dict[str, str]:
    state = _load_value_state()
    values = template_values()

    # Preserve existing managed values
    managed_values = _dotenv_values_from_file(managed_env_path())
    if managed_values:
        values.update({key: val for key, val in managed_values.items() if key in values})
    else:
        for key, entry in state.items():
            if entry["source"] in ("repo_env", "template", "default"):
                values[key] = str(entry["value"])

    # Apply updates
    for key, value in updates.items():
        field = FIELD_BY_KEY.get(key)
        if field is None:
            continue
        if _is_locked_source(state[key]["source"]):
            continue
        if field.secret and value == MASKED_SECRET:
            continue
        values[key] = _normalize_for_env(value)

    # Ensure defaults for missing fields
    for field in FIELDS:
        values.setdefault(field.key, field.default)

    return values


def _effective_values_for_validation(target_values: dict[str, str]) -> dict[str, str]:
    values = dict(target_values)
    for key, entry in _load_value_state().items():
        if _is_locked_source(entry["source"]):
            values[key] = str(entry["value"])
    return values


def validate_values(values: dict[str, str]) -> tuple[bool, list[str]]:
    """Validate proposed env values against the Settings model."""
    kwargs: dict[str, Any] = {"_env_file": None}
    for field in FIELDS:
        raw = values.get(field.key, "")
        if field.field_type == "boolean":
            kwargs[field.key.lower()] = raw.lower() in ("true", "1", "yes") if raw else False
        elif field.field_type == "number":
            try:
                kwargs[field.key.lower()] = int(raw) if raw else 0
            except ValueError:
                kwargs[field.key.lower()] = 0
        else:
            kwargs[field.key.lower()] = raw
    try:
        Settings(**kwargs)
    except ValidationError as exc:
        errors = []
        for error in exc.errors():
            loc = ".".join(str(p) for p in error.get("loc", ()))
            msg = str(error.get("msg", "Invalid"))
            errors.append(f"{loc}: {msg}" if loc else msg)
        return False, errors
    return True, []


def validate_updates(updates: dict[str, Any]) -> dict[str, Any]:
    """Validate partial admin updates."""
    target_values = _target_values_with_updates(updates)
    effective_values = _effective_values_for_validation(target_values)
    valid, errors = validate_values(effective_values)
    return {"valid": valid, "errors": errors}


def write_managed_env(updates: dict[str, Any]) -> dict[str, Any]:
    """Validate and atomically write the admin-managed env file."""
    validation = validate_updates(updates)
    if not validation["valid"]:
        return validation | {"applied": False, "pending_fields": []}

    target_values = _target_values_with_updates(updates)
    pending_fields = [k for k in updates if FIELD_BY_KEY.get(k, None) and FIELD_BY_KEY[k].restart_required]

    path = managed_env_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_suffix(path.suffix + ".tmp")
    temp_path.write_text(render_env_file(target_values), encoding="utf-8")
    os.replace(temp_path, path)

    return {
        "applied": True,
        "valid": True,
        "errors": [],
        "path": str(path),
        "pending_fields": pending_fields,
    }


def _quote_env_value(value: str) -> str:
    if value == "":
        return ""
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    if any(char.isspace() for char in value) or any(char in value for char in ('"', "#", "=", "$")):
        return f'"{escaped}"'
    return value


def render_env_file(values: dict[str, str], *, mask_secrets: bool = False) -> str:
    """Render a complete grouped env file."""
    lines: list[str] = [
        "# Managed by FC-Play Admin Console.",
        "# Edit via the admin UI when possible.",
        "",
    ]
    for section in SECTIONS:
        section_fields = [f for f in FIELDS if f.section_id == section.section_id]
        if not section_fields:
            continue
        lines.append(f"# {section.label}")
        for field in section_fields:
            value = values.get(field.key, field.default)
            if mask_secrets and field.secret and value:
                value = MASKED_SECRET
            lines.append(f"{field.key}={_quote_env_value(value)}")
        lines.append("")
    return "\n".join(lines) + "\n"
