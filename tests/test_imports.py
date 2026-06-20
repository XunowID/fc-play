"""Tests for fc-play core modules."""

from __future__ import annotations


def test_import_config():
    from fc_play.config.settings import Settings, get_settings
    from fc_play.config.paths import data_dir, config_file
    from fc_play.config.constants import APP_NAME, PROVIDERS, MODELS_ALL
    assert APP_NAME == "fc-play"
    assert len(PROVIDERS) >= 18
    assert len(MODELS_ALL) > 0


def test_import_tui():
    from fc_play.tui.themes import get_theme
    t = get_theme("midnight")
    assert t.name == "midnight"


def test_import_cli():
    from fc_play.cli.entrypoints import cli
    assert cli is not None


def test_settings_defaults():
    from fc_play.config.settings import get_settings
    s = get_settings()
    assert s.port == 3010
    assert s.host == "0.0.0.0"


def test_all_model_tiers():
    from fc_play.config.constants import MODELS_OPUS, MODELS_SONNET, MODELS_HAIKU
    assert any("opus-4-8" in m for m in MODELS_OPUS)
    assert any("sonnet-4-6" in m for m in MODELS_SONNET)
    assert any("haiku-4-5" in m for m in MODELS_HAIKU)
    assert any("opus-4-20250514" in m for m in MODELS_OPUS)
    assert any("sonnet-4-20250514" in m for m in MODELS_SONNET)
    assert any("haiku-4-20250514" in m for m in MODELS_HAIKU)


def test_admin_routes_import():
    from fc_play.api.admin_routes import router
    assert router is not None


def test_app_creation():
    from fc_play.api.app import create_app
    app = create_app()
    assert app.title == "FC-Play API"


def test_all_providers():
    from fc_play.config.constants import PROVIDERS, PROVIDER_PREFIXES
    assert "anthropic" in PROVIDERS
    assert "openai" in PROVIDERS
    assert "openrouter" in PROVIDERS
    assert "gemini" in PROVIDERS
    assert "deepseek" in PROVIDERS
    assert "mistral" in PROVIDERS
    assert "groq" in PROVIDERS
    assert "fireworks" in PROVIDERS
    assert "together" in PROVIDERS
    assert "nvidia_nim" in PROVIDERS
    assert "cerebras" in PROVIDERS
    assert "kimi" in PROVIDERS
    assert "ollama" in PROVIDERS
    assert "lmstudio" in PROVIDERS
    assert "llamacpp" in PROVIDERS
    assert len(PROVIDER_PREFIXES) >= 18


def test_model_resolution():
    from fc_play.config.settings import Settings
    s = Settings(
        model="custom/claude-sonnet-4-20250514",
        model_opus="custom/claude-opus-4-20250514",
        model_sonnet="custom/claude-sonnet-4-20250514",
        model_haiku="custom/claude-haiku-4-20250514",
    )
    assert s.resolve_model("claude-opus-4") == "custom/claude-opus-4-20250514"
    assert s.resolve_model("claude-sonnet-4") == "custom/claude-sonnet-4-20250514"
    assert s.resolve_model("claude-haiku-4") == "custom/claude-haiku-4-20250514"


def test_configured_providers():
    from fc_play.config.settings import Settings
    s = Settings(anthropic_api_key="sk-test")
    prov = s.configured_providers()
    assert prov["anthropic"] is True
    assert prov["openai"] is False
    assert "ollama" in prov
    assert "lmstudio" in prov
    assert "llamacpp" in prov


def test_theme_registry():
    from fc_play.tui.themes import THEMES
    assert "midnight" in THEMES
    assert "emerald" in THEMES
    assert "ruby" in THEMES
