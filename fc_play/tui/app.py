"""FC-Play TUI application — interactive terminal dashboard."""

from __future__ import annotations

import signal
import sys
from datetime import datetime
from typing import Any

from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.text import Text

from fc_play.config.constants import APP_DISPLAY, APP_TAGLINE
from fc_play.config.settings import get_settings
from fc_play.tui.panels import (make_dashboard, make_header, make_help_panel,
                                 make_model_table, make_progress_bar,
                                 make_request_log, make_status_table)
from fc_play.tui.themes import DEFAULT_THEME, get_theme


class TUIApp:
    """Interactive terminal dashboard for FC-Play."""

    def __init__(self, theme_name: str = "midnight"):
        self.console = Console()
        self.theme = get_theme(theme_name)
        self.settings = get_settings()
        self.running = False
        self.start_time = datetime.now()

        # Data
        self.request_log: list[dict[str, Any]] = []
        self.models: list[dict[str, Any]] = []

        # Signal handling
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)

    def _handle_signal(self, sig, frame):
        """Handle shutdown signals gracefully."""
        self.running = False

    def _format_uptime(self) -> str:
        """Calculate and format uptime string."""
        delta = datetime.now() - self.start_time
        total_seconds = int(delta.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        if hours > 0:
            return f"{hours}h {minutes}m"
        if minutes > 0:
            return f"{minutes}m {seconds}s"
        return f"{seconds}s"

    def _build_layout(self) -> Layout:
        """Build the current layout state."""
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=5),
            Layout(name="body"),
        )
        layout["header"].update(make_header(self.theme))

        layout["body"].split_row(
            Layout(name="left", ratio=2),
            Layout(name="right", ratio=1),
        )
        layout["body"]["left"].split_column(
            Layout(name="status", size=8),
            Layout(name="models"),
        )
        layout["body"]["right"].split_column(
            Layout(name="log"),
            Layout(name="help", size=8),
        )

        # Populate panels
        layout["body"]["left"]["status"].update(
            make_status_table(
                server_status="Running",
                active_provider="Custom API (Anthropic)",
                model=self.settings.custom_api_model or "claude-sonnet-4",
                uptime=self._format_uptime(),
                theme=self.theme,
            )
        )

        model_list = [
            {"id": self.settings.custom_api_model, "provider": "Custom API"},
            {"id": self.settings.model, "provider": "Fallback"},
        ]
        if self.settings.model_opus:
            model_list.insert(0, {"id": self.settings.model_opus, "provider": "Opus"})
        if self.settings.model_sonnet:
            model_list.insert(1, {"id": self.settings.model_sonnet, "provider": "Sonnet"})
        if self.settings.model_haiku:
            model_list.append({"id": self.settings.model_haiku, "provider": "Haiku"})

        layout["body"]["left"]["models"].update(
            make_model_table(model_list, theme=self.theme)
        )

        layout["body"]["right"]["log"].update(
            make_request_log(self.request_log, theme=self.theme)
        )

        layout["body"]["right"]["help"].update(
            make_help_panel(theme=self.theme)
        )

        return layout

    def run(self):
        """Run the TUI dashboard."""
        self.running = True

        with Live(
            self._build_layout(),
            console=self.console,
            refresh_per_second=4,
            screen=True,
        ) as live:
            while self.running:
                try:
                    live.update(self._build_layout())
                    import time
                    time.sleep(0.25)
                except KeyboardInterrupt:
                    break

    def stop(self):
        """Stop the TUI dashboard."""
        self.running = False


def run_tui(theme: str = "midnight"):
    """Launch the TUI dashboard."""
    app = TUIApp(theme_name=theme)
    try:
        app.run()
    except KeyboardInterrupt:
        pass
    finally:
        console = Console()
        console.print()
        console.print(f"[bold {app.theme.primary}]FC-Play[/] dashboard closed.")
        console.print(f"[{app.theme.text_dim}]Uptime: {app._format_uptime()}[/]")
