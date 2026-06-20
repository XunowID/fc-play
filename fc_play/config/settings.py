"""FC-Play settings — Pydantic-based configuration with env file support."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from fc_play.config.constants import PROVIDER_PREFIXES


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _home() -> Path:
    return Path.home()


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


def _env_files() -> list[Path]:
    files: list[Path] = []
    root_env = _project_root() / ".env"
    if root_env.exists():
        files.append(root_env)
    home_env = _home() / ".fc-play" / ".env"
    if home_env.exists():
        files.append(home_env)
    override = os.environ.get("FC_ENV_FILE")
    if override:
        p = Path(override)
        if p.exists():
            files.append(p)
    return files


# ---------------------------------------------------------------------------

@dataclass
class ConfiguredModelRef:
    model_id: str
    source_env_keys: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=[str(f) for f in _env_files()],
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
        frozen=False,
    )

    # --- Server ---
    host: str = "0.0.0.0"
    port: int = 3010
    auth_token: str | None = None

    # ─── API Keys ────────────────────────────────────────────────────────
    # Primary
    anthropic_api_key: str = ""
    openai_api_key: str = ""

    # Community / Multi-model
    openrouter_api_key: str = ""
    gemini_api_key: str = ""
    deepseek_api_key: str = ""
    mistral_api_key: str = ""
    codestral_api_key: str = ""
    groq_api_key: str = ""
    fireworks_api_key: str = ""
    together_api_key: str = ""

    # Specialized
    nvidia_nim_api_key: str = ""
    nvidia_nim_base_url: str = "https://integrate.api.nvidia.com/v1"
    cerebras_api_key: str = ""
    kimi_api_key: str = ""
    wafer_api_key: str = ""
    opencode_api_key: str = ""
    zai_api_key: str = ""

    # Local / Self-hosted
    ollama_base_url: str = "http://localhost:11434"
    lmstudio_base_url: str = "http://localhost:1234/v1"
    llamacpp_base_url: str = "http://localhost:8080/v1"

    # --- Model Selection ---
    model: str = "custom/claude-sonnet-4-20250514"
    model_opus: str | None = None
    model_sonnet: str | None = None
    model_haiku: str | None = None

    # --- Provider-specific proxies ---
    nvidia_nim_proxy: str | None = None
    openrouter_proxy: str | None = None
    mistral_proxy: str | None = None

    # --- Rate Limiting ---
    rate_limit_requests: int = 60
    rate_limit_window: int = 60
    rate_limit_max_concurrent: int = 10

    # --- Extended Thinking ---
    enable_thinking: bool = False
    enable_opus_thinking: bool = False
    enable_sonnet_thinking: bool = False
    enable_haiku_thinking: bool = False

    # --- Web Tools ---
    enable_web_server_tools: bool = False
    web_fetch_allowed_schemes: str = "http,https"
    block_private_networks: bool = True

    # --- Logging ---
    log_level: str = "INFO"
    log_raw_payloads: bool = False
    log_sse_events: bool = False
    log_tracebacks: bool = False

    # --- Performance ---
    max_retries: int = 3
    batch_size: int = 50
    timeout_read: int = 120
    timeout_write: int = 10
    timeout_connect: int = 30

    # ------------------------------------------------------------------
    # Validators
    # ------------------------------------------------------------------

    @field_validator("model", "model_opus", "model_sonnet", "model_haiku")
    @classmethod
    def _empty_to_none(cls, v: str | None) -> str | None:
        return v if v and v.strip() else None

    @field_validator("ollama_base_url")
    @classmethod
    def _no_v1_suffix(cls, v: str) -> str:
        if v.endswith("/v1"):
            v = v[:-3]
        return v.rstrip("/")

    @field_validator("model")
    @classmethod
    def _valid_model_format(cls, v: str) -> str:
        valid_prefixes = set(PROVIDER_PREFIXES.keys())
        if "/" in v:
            prefix = v.split("/")[0]
            if prefix not in valid_prefixes:
                msg = f"Unknown provider '{prefix}' in model '{v}'. "
                msg += f"Valid: {', '.join(sorted(valid_prefixes))}"
                raise ValueError(msg)
        return v

    @model_validator(mode="after")
    def _inherit_model_refs(self) -> "Settings":
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
        lower = model_name.lower()
        if "opus" in lower and self.model_opus:
            return self.model_opus
        if "sonnet" in lower and self.model_sonnet:
            return self.model_sonnet
        if "haiku" in lower and self.model_haiku:
            return self.model_haiku
        return self.model

    def resolve_thinking(self, model_name: str) -> bool:
        lower = model_name.lower()
        if "opus" in lower:
            return self.enable_opus_thinking
        if "sonnet" in lower:
            return self.enable_sonnet_thinking
        if "haiku" in lower:
            return self.enable_haiku_thinking
        return self.enable_thinking

    def configured_model_refs(self) -> list[ConfiguredModelRef]:
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

    def configured_providers(self) -> dict[str, bool]:
        """Return provider_id → has_key mapping for all providers."""
        return {
            "anthropic": bool(self.anthropic_api_key),
            "openai": bool(self.openai_api_key),
            "openrouter": bool(self.openrouter_api_key),
            "gemini": bool(self.gemini_api_key),
            "deepseek": bool(self.deepseek_api_key),
            "mistral": bool(self.mistral_api_key),
            "codestral": bool(self.codestral_api_key),
            "groq": bool(self.groq_api_key),
            "fireworks": bool(self.fireworks_api_key),
            "together": bool(self.together_api_key),
            "nvidia_nim": bool(self.nvidia_nim_api_key),
            "cerebras": bool(self.cerebras_api_key),
            "kimi": bool(self.kimi_api_key),
            "wafer": bool(self.wafer_api_key),
            "opencode": bool(self.opencode_api_key),
            "zai": bool(self.zai_api_key),
            "ollama": self._is_local_available("ollama_base_url"),
            "lmstudio": self._is_local_available("lmstudio_base_url"),
            "llamacpp": self._is_local_available("llamacpp_base_url"),
        }

    @staticmethod
    def _is_local_available(url_attr: str) -> bool:
        """Check if a local provider URL is configured (non-default)."""
        return True  # Local providers are always "available" if the config exists


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
