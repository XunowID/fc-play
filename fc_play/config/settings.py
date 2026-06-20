"""FC-Play settings — Pydantic-based configuration with env file support."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _home() -> Path:
    return Path.home()


def _project_root() -> Path:
    """Resolve project root from file location or CWD."""
    return Path(__file__).resolve().parent.parent.parent


def _env_files() -> list[Path]:
    """Priority-ordered list of candidate .env files."""
    files: list[Path] = []
    # 1. .env in project root
    root_env = _project_root() / ".env"
    if root_env.exists():
        files.append(root_env)
    # 2. ~/.fc-play/.env
    home_env = _home() / ".fc-play" / ".env"
    if home_env.exists():
        files.append(home_env)
    # 3. FC_ENV_FILE override
    override = os.environ.get("FC_ENV_FILE")
    if override:
        p = Path(override)
        if p.exists():
            files.append(p)
    return files


# ---------------------------------------------------------------------------
# Configured model reference
# ---------------------------------------------------------------------------

@dataclass
class ConfiguredModelRef:
    """A configured model reference and the env keys that set it."""

    model_id: str
    source_env_keys: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------

class Settings(BaseSettings):
    """Application settings loaded from env files and environment variables."""

    model_config = SettingsConfigDict(
        env_file=[str(f) for f in _env_files()],
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
        frozen=False,
    )

    # --- Server ---
    host: str = "0.0.0.0"
    port: int = 8083
    anthropic_auth_token: str | None = None

    # --- Custom API (primary Claude access) ---
    custom_api_key: str = ""
    custom_api_base: str = "https://api.anthropic.com"
    custom_api_model: str = "claude-sonnet-4-20250514"
    custom_api_timeout: int = 300

    # --- Provider Keys ---
    openai_api_key: str = ""
    openrouter_api_key: str = ""
    gemini_api_key: str = ""
    deepseek_api_key: str = ""
    mistral_api_key: str = ""
    groq_api_key: str = ""
    fireworks_api_key: str = ""
    together_api_key: str = ""

    # --- Model Selection ---
    model: str = "custom/claude-sonnet-4-20250514"
    model_opus: str | None = None
    model_sonnet: str | None = None
    model_haiku: str | None = None

    # --- Rate Limiting ---
    rate_limit_requests: int = 60
    rate_limit_window: int = 60
    rate_limit_max_concurrent: int = 10

    # --- Thinking ---
    enable_thinking: bool = True
    enable_opus_thinking: bool = True
    enable_sonnet_thinking: bool = True
    enable_haiku_thinking: bool = True

    # --- Web Tools ---
    enable_web_server_tools: bool = False
    web_fetch_allowed_schemes: str = "http,https"
    block_private_networks: bool = True

    # --- Logging ---
    log_level: str = "INFO"
    fc_log_raw_payloads: bool = False
    fc_log_sse_events: bool = False
    fc_log_tracebacks: bool = False
    fc_log_messaging_content: bool = False
    fc_log_cli_diagnostics: bool = False

    # --- Performance ---
    max_retries: int = 3
    batch_size: int = 50

    # ------------------------------------------------------------------
    # Validators
    # ------------------------------------------------------------------

    @field_validator("model", "model_opus", "model_sonnet", "model_haiku")
    @classmethod
    def _empty_to_none(cls, v: str | None) -> str | None:
        return v if v and v.strip() else None

    @field_validator("model")
    @classmethod
    def _valid_model_format(cls, v: str) -> str:
        supported = {"custom", "openai", "openrouter", "gemini", "deepseek",
                     "mistral", "groq", "fireworks", "together"}
        if "/" in v:
            prefix = v.split("/")[0]
            if prefix not in supported:
                msg = f"Unknown provider prefix '{prefix}' in model '{v}'. "
                msg += f"Supported: {', '.join(sorted(supported))}"
                raise ValueError(msg)
        return v

    @model_validator(mode="after")
    def _validate_model_refs(self) -> "Settings":
        """Ensure model_opus/sonnet/haiku inherit from model when unset."""
        if self.model_opus is None:
            self.model_opus = self.model
        if self.model_sonnet is None:
            self.model_sonnet = self.model
        if self.model_haiku is None:
            self.model_haiku = self.model
        return self

    # ------------------------------------------------------------------
    # Resolvers
    # ------------------------------------------------------------------

    def resolve_model(self, model_name: str) -> str:
        """Map a Claude model family to the configured override."""
        lower = model_name.lower()
        if "opus" in lower and self.model_opus:
            return self.model_opus
        if "sonnet" in lower and self.model_sonnet:
            return self.model_sonnet
        if "haiku" in lower and self.model_haiku:
            return self.model_haiku
        return self.model

    def resolve_thinking(self, model_name: str) -> bool:
        """Map a Claude model family to the configured thinking toggle."""
        lower = model_name.lower()
        if "opus" in lower:
            return self.enable_opus_thinking
        if "sonnet" in lower:
            return self.enable_sonnet_thinking
        if "haiku" in lower:
            return self.enable_haiku_thinking
        return self.enable_thinking

    def configured_model_refs(self) -> list[ConfiguredModelRef]:
        """Return all unique configured model refs with their env key sources."""
        seen: set[str] = set()
        refs: list[ConfiguredModelRef] = []
        for key, attr in [("MODEL", "model"), ("MODEL_OPUS", "model_opus"),
                          ("MODEL_SONNET", "model_sonnet"),
                          ("MODEL_HAIKU", "model_haiku")]:
            val = getattr(self, attr)
            if val and val not in seen:
                seen.add(val)
                refs.append(ConfiguredModelRef(val, [key]))
            elif val and val in seen:
                for r in refs:
                    if r.model_id == val:
                        r.source_env_keys.append(key)
        return refs


# ---------------------------------------------------------------------------
# Cached singleton
# ---------------------------------------------------------------------------

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Get the cached Settings singleton."""
    return Settings()
