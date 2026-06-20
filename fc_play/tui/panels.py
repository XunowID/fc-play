"""FC-Play TUI panels — beautiful terminal layout components."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from rich.align import Align
from rich.console import Console, Group
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.progress import (BarColumn, Progress, SpinnerColumn, TextColumn,
                            TimeElapsedColumn)
from rich.rule import Rule
from rich.status import Status
from rich.table import Table
from rich.text import Text

from fc_play.config.constants import APP_DISPLAY, APP_TAGLINE
from fc_play.tui.themes import DEFAULT_THEME, Theme


def make_header(theme: Theme = DEFAULT_THEME) -> Panel:
    """Create the application header panel."""
    title = Text(APP_DISPLAY, style=f"bold {theme.primary}")
    subtitle = Text(APP_TAGLINE, style=f"dim {theme.text_muted}")

    content = Group(
        Align.center(title),
        Align.center(subtitle),
    )
    return Panel(
        content,
        style=theme.surface,
        border_style=theme.border,
        padding=(1, 2),
    )


def make_status_table(
    server_status: str = "Running",
    active_provider: str = "Custom API",
    model: str = "claude-sonnet-4",
    uptime: str = "0m",
    theme: Theme = DEFAULT_THEME,
) -> Table:
    """Create a server status table."""
    table = Table(
        show_header=False,
        box=None,
        padding=(0, 2),
        style=theme.text,
    )
    table.add_column("Key", style=f"bold {theme.text_dim}", no_wrap=True)
    table.add_column("Value", style=theme.text)

    status_color = theme.success if server_status == "Running" else theme.warning
    table.add_row("Status", f"[{status_color}]●[/] {server_status}")
    table.add_row("Provider", active_provider)
    table.add_row("Model", f"[{theme.primary}]{model}[/]")
    table.add_row("Uptime", uptime)

    return Panel(
        table,
        title="Server Status",
        title_align="left",
        border_style=theme.border,
        padding=(1, 2),
    )


def make_model_table(
    models: list[dict[str, Any]],
    theme: Theme = DEFAULT_THEME,
) -> Panel:
    """Create a model listing table."""
    table = Table(
        show_header=True,
        header_style=f"bold {theme.text_dim}",
        border_style=theme.border,
        padding=(0, 1),
    )
    table.add_column("Model ID", style=theme.text)
    table.add_column("Provider", style=theme.text_dim)
    table.add_column("Status")

    for model in models[:20]:  # Show top 20
        status = f"[{theme.success}]● Active[/]"
        if "opus" in model.get("id", "").lower():
            provider_style = theme.primary
        elif "sonnet" in model.get("id", "").lower():
            provider_style = theme.info
        else:
            provider_style = theme.text_dim

        table.add_row(
            f"[{provider_style}]{model.get('id', 'unknown')}[/]",
            model.get("provider", "custom"),
            status,
        )

    return Panel(
        table,
        title="Available Models",
        title_align="left",
        border_style=theme.border,
        padding=(1, 2),
    )


def make_request_log(
    entries: list[dict[str, Any]] | None = None,
    theme: Theme = DEFAULT_THEME,
) -> Panel:
    """Create a request activity log panel."""
    entries = entries or []

    table = Table(
        show_header=True,
        header_style=f"bold {theme.text_dim}",
        border_style=theme.border,
        padding=(0, 1),
    )
    table.add_column("Time", style=theme.text_muted, width=8)
    table.add_column("Method", width=6)
    table.add_column("Path", style=theme.text)
    table.add_column("Status", width=6)

    if not entries:
        table.add_row(
            "--:--",
            "",
            "[dim]Waiting for requests...[/]",
            "",
        )
    else:
        for entry in entries[-10:]:  # Last 10
            method = entry.get("method", "GET")
            path = entry.get("path", "/")
            status = entry.get("status", 200)
            time_str = entry.get("time", "")[-8:] if entry.get("time") else ""

            if status >= 400:
                status_str = f"[{theme.error}]{status}[/]"
            elif status >= 300:
                status_str = f"[{theme.warning}]{status}[/]"
            else:
                status_str = f"[{theme.success}]{status}[/]"

            method_color = theme.primary if method == "POST" else theme.info
            table.add_row(
                time_str,
                f"[{method_color}]{method}[/]",
                path,
                status_str,
            )

    return Panel(
        table,
        title="Request Log",
        title_align="left",
        border_style=theme.border,
        padding=(1, 2),
    )


def make_progress_bar(
    description: str = "Processing",
    theme: Theme = DEFAULT_THEME,
) -> Progress:
    """Create a styled progress bar."""
    return Progress(
        SpinnerColumn(spinner_name="dots", style=theme.primary),
        TextColumn(f"[{theme.text}]{{task.description}}[/]"),
        BarColumn(bar_width=40, style=theme.border, completed_style=theme.primary),
        TextColumn(f"[{theme.text_dim}]{{task.percentage:>3.0f}}%[/]"),
        TimeElapsedColumn(),
    )


def make_help_panel(theme: Theme = DEFAULT_THEME) -> Panel:
    """Create a help/commands panel."""
    table = Table(
        show_header=False,
        box=None,
        padding=(0, 2),
        style=theme.text,
    )
    table.add_column("Command", style=f"bold {theme.primary}", no_wrap=True)
    table.add_column("Description", style=theme.text_dim)

    table.add_row("fc-play", "Launch interactive TUI dashboard")
    table.add_row("fc-play-server", "Start the proxy server")
    table.add_row("fc-play-admin", "Open the admin web UI")
    table.add_row("fc-play --help", "Show full usage info")

    return Panel(
        table,
        title="Commands",
        title_align="left",
        border_style=theme.border,
        padding=(1, 2),
    )


def make_dashboard(theme: Theme = DEFAULT_THEME) -> Layout:
    """Create the main dashboard layout."""
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=5),
        Layout(name="body"),
    )
    layout["header"].update(make_header(theme))

    layout["body"].split_row(
        Layout(name="left"),
        Layout(name="right"),
    )
    layout["body"]["left"].split_column(
        Layout(name="status"),
        Layout(name="models"),
    )
    layout["body"]["right"].split_column(
        Layout(name="log"),
        Layout(name="help"),
    )

    return layout
