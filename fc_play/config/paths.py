"""FC-Play path utilities — data dirs, config paths, and helpers."""

from __future__ import annotations

from pathlib import Path


def _home() -> Path:
    return Path.home()


def data_dir() -> Path:
    """~/.fc-play/ — the root data directory."""
    d = _home() / ".fc-play"
    d.mkdir(parents=True, exist_ok=True)
    return d


def env_file() -> Path:
    """~/.fc-play/.env."""
    return data_dir() / ".env"


def config_file() -> Path:
    """~/.fc-play/config.json — JSON-persisted runtime config."""
    return data_dir() / "config.json"


def logs_dir() -> Path:
    """~/.fc-play/logs/."""
    d = data_dir() / "logs"
    d.mkdir(parents=True, exist_ok=True)
    return d


def sessions_dir() -> Path:
    """~/.fc-play/sessions/."""
    d = data_dir() / "sessions"
    d.mkdir(parents=True, exist_ok=True)
    return d
