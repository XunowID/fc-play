"""Test that all core modules can be imported."""

from __future__ import annotations


def test_import_config():
    from fc_play.config.settings import Settings, get_settings
    from fc_play.config.paths import data_dir, config_file, logs_dir
    from fc_play.config.constants import APP_NAME, APP_DISPLAY, CLAUDE_MODELS
    assert APP_NAME == "fc-play"
    assert len(CLAUDE_MODELS) > 0


def test_import_tui():
    from fc_play.tui.themes import Theme, MIDNIGHT, get_theme
    from fc_play.tui.panels import make_header, make_status_table, make_help_panel
    theme = get_theme("midnight")
    assert theme.name == "midnight"


def test_import_cli():
    from fc_play.cli.entrypoints import cli
    assert cli is not None


def test_settings_defaults():
    from fc_play.config.settings import get_settings
    settings = get_settings()
    assert settings.port == 8083
    assert settings.host == "0.0.0.0"


def test_all_claude_models():
    """Verify we have ALL Claude models including Opus 4.8."""
    from fc_play.config.constants import CLAUDE_OPUS_MODELS, CLAUDE_SONNET_MODELS, CLAUDE_HAIKU_MODELS
    all_models = CLAUDE_OPUS_MODELS + CLAUDE_SONNET_MODELS + CLAUDE_HAIKU_MODELS

    # Must include Opus 4.8
    assert any("opus-4-8" in m for m in all_models), "Missing Opus 4.8"

    # Must include Sonnet 4.6
    assert any("sonnet-4-6" in m for m in all_models), "Missing Sonnet 4.6"

    # Must include Haiku 4.5
    assert any("haiku-4-5" in m for m in all_models), "Missing Haiku 4.5"

    # Must include latest 2025 models
    assert any("opus-4-20250514" in m for m in all_models), "Missing Opus 4 (2025)"
    assert any("sonnet-4-20250514" in m for m in all_models), "Missing Sonnet 4 (2025)"
    assert any("haiku-4-20250514" in m for m in all_models), "Missing Haiku 4 (2025)"


def test_admin_routes_import():
    from fc_play.api.admin_routes import router
    assert router is not None


def test_api_routes_import():
    from fc_play.api.routes import router
    assert router is not None


def test_app_creation():
    from fc_play.api.app import create_app
    app = create_app()
    assert app.title == "FC-Play API"


def test_theme_registry():
    from fc_play.tui.themes import THEMES, DEFAULT_THEME
    assert "midnight" in THEMES
    assert "emerald" in THEMES
    assert "ruby" in THEMES
    assert DEFAULT_THEME.name == "midnight"


def test_provider_prefixes():
    from fc_play.config.constants import PROVIDER_PREFIXES
    assert "custom" in PROVIDER_PREFIXES
    assert "openai" in PROVIDER_PREFIXES
    assert "openrouter" in PROVIDER_PREFIXES
    assert "gemini" in PROVIDER_PREFIXES


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
