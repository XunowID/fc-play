"""FC-Play CLI — typer-based command interface with server/tui/admin/status."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from fc_play.config.constants import APP_DISPLAY, APP_TAGLINE

cli = typer.Typer(
    name="fc-play",
    help=f"{APP_DISPLAY} — {APP_TAGLINE}",
    no_args_is_help=True,
    rich_markup_mode="rich",
)
console = Console()

# ─── Banner ────────────────────────────────────────────────────────────────

def _banner():
    console.print(f"""
[bold #f97316]┌────────────────────────────────────────────┐
│         FC-PLAY  v1.0.0                     │
│   Multi-provider model gateway              │
│   Fast. Flexible. Fabulous.                 │
└────────────────────────────────────────────┘[/]""")


# ─── Server ────────────────────────────────────────────────────────────────

@cli.command()
def server(
    host: str = typer.Option("0.0.0.0", "--host", help="Bind address"),
    port: int = typer.Option(3010, "--port", "-p", help="Port"),
    env: Optional[Path] = typer.Option(None, "--env", "-e", help=".env path"),
    log_level: str = typer.Option("INFO", "--log-level", "-l"),
):
    """Start the FC-Play proxy server."""
    _banner()
    if env:
        from dotenv import load_dotenv
        load_dotenv(env)
    import uvicorn
    console.print(f"[dim]Starting server on [bold]{host}:{port}[/][/]")
    uvicorn.run("server:app", host=host, port=port,
                log_level=log_level.lower(), timeout_graceful_shutdown=5)


# ─── TUI ───────────────────────────────────────────────────────────────────

@cli.command()
def tui(
    theme: str = typer.Option("midnight", "--theme", "-t",
                              help="midnight | emerald | ruby"),
):
    """Launch the terminal dashboard."""
    from fc_play.tui.app import run_tui
    run_tui(theme=theme)


# ─── Admin ─────────────────────────────────────────────────────────────────

@cli.command()
def admin(
    port: int = typer.Option(3010, "--port", "-p", help="Server port"),
    open: bool = typer.Option(False, "--open", "-o", help="Open browser"),
):
    """Start server with admin UI."""
    import webbrowser
    url = f"http://127.0.0.1:{port}/admin"
    console.print(f"[bold #f97316]✦[/] Admin UI: [bold]{url}[/]")
    if open:
        webbrowser.open(url)
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=port, log_level="info",
                timeout_graceful_shutdown=5)


# ─── Status ────────────────────────────────────────────────────────────────

@cli.command()
def status():
    """Show current configuration status."""
    _banner()
    try:
        from fc_play.config.settings import get_settings
        settings = get_settings()
    except Exception as e:
        console.print(f"[red]Failed: {e}[/]")
        return

    t = Table(show_header=False, box=None, padding=(0, 2))
    t.add_column("Key", style="bold #78716c", no_wrap=True)
    t.add_column("Value", style="#f5f5f4")

    t.add_row("Server", f"{settings.host}:{settings.port}")
    t.add_row("Model", settings.model)
    t.add_row("Opus-tier", settings.model_opus or "—")
    t.add_row("Sonnet-tier", settings.model_sonnet or "—")
    t.add_row("Haiku-tier", settings.model_haiku or "—")

    providers = settings.configured_providers()
    active = [k for k, v in providers.items() if v]
    t.add_row("Active Providers", ", ".join(active) if active else "none")

    t.add_row("Rate Limit", f"{settings.rate_limit_requests}/{settings.rate_limit_window}s")
    t.add_row("Thinking", "Enabled" if settings.enable_thinking else "Disabled")
    t.add_row("Log Level", settings.log_level)
    console.print(t)
    console.print()
    console.print("[bold #f97316]Commands:[/]")
    console.print("  fc-play server  —  Start proxy")
    console.print("  fc-play tui     —  Dashboard")
    console.print("  fc-play admin   —  Admin UI")


# ─── Version ───────────────────────────────────────────────────────────────

@cli.command()
def version():
    """Show version."""
    console.print(f"[bold #f97316]{APP_DISPLAY}[/] v1.0.0")
    console.print(f"[dim]{APP_TAGLINE}[/]")


@cli.callback()
def main_callback():
    pass


# ─── Entry points ─────────────────────────────────────────────────────────

def server_main():
    """Entry point for fc-play-server."""
    sys.argv = ["fc-play", "server"]
    cli()

def admin_main():
    """Entry point for fc-play-admin."""
    sys.argv = ["fc-play", "admin"]
    cli()

def tui_main():
    """Entry point for fc-play-tui."""
    sys.argv = ["fc-play", "tui"]
    cli()


if __name__ == "__main__":
    cli()
