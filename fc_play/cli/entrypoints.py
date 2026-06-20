"""FC-Play CLI entrypoints — typer-based command-line interface."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.text import Text

from fc_play.config.constants import APP_DISPLAY, APP_TAGLINE

cli = typer.Typer(
    name="fc-play",
    help=f"{APP_DISPLAY} — {APP_TAGLINE}",
    no_args_is_help=True,
    rich_markup_mode="rich",
)

console = Console()


def _print_banner():
    """Print the FC-Play startup banner."""
    banner = f"""
[bold #6366f1]╔════════════════════════════════════════════╗
║            FC-PLAY v1.0.0                  ║
║     Play with Claude — Free. Fast.         ║
║     Fabulous.                              ║
╚════════════════════════════════════════════╝[/]"""
    console.print(banner)


@cli.command()
def server(
    host: str = typer.Option("0.0.0.0", "--host", help="Bind address"),
    port: int = typer.Option(8083, "--port", "-p", help="Server port"),
    env: Optional[Path] = typer.Option(None, "--env", "-e", help="Path to .env file", exists=True),
    log_level: str = typer.Option("INFO", "--log-level", "-l", help="Log level"),
):
    """Start the FC-Play proxy server."""
    _print_banner()

    if env:
        from dotenv import load_dotenv
        load_dotenv(env)

    console.print(f"[dim]Starting server on [bold]{host}:{port}[/]...[/]")

    import uvicorn
    uvicorn.run(
        "server:app",
        host=host,
        port=port,
        log_level=log_level.lower(),
        timeout_graceful_shutdown=5,
        reload=False,
    )


@cli.command()
def tui(
    theme: str = typer.Option("midnight", "--theme", "-t", help="Theme: midnight, emerald, ruby"),
):
    """Launch the interactive terminal dashboard."""
    from fc_play.tui.app import run_tui
    run_tui(theme=theme)


@cli.command()
def admin(
    port: int = typer.Option(8083, "--port", "-p", help="Server port"),
):
    """Start the server and open the admin web UI."""
    import webbrowser
    url = f"http://127.0.0.1:{port}/admin"
    console.print(f"[bold #6366f1]✦[/] Opening admin UI: [bold]{url}[/]")
    webbrowser.open(url)

    import uvicorn
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=port,
        log_level="info",
        timeout_graceful_shutdown=5,
    )


@cli.command()
def status():
    """Show current server status and configuration."""
    _print_banner()

    try:
        from fc_play.config.settings import get_settings
        settings = get_settings()
    except Exception as e:
        console.print(f"[red]Failed to load settings: {e}[/]")
        return

    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Setting", style="bold #71717a", no_wrap=True)
    table.add_column("Value", style="#f4f4f5")

    table.add_row("Server", f"0.0.0.0:{settings.port}")
    table.add_row("Model", settings.model)
    table.add_row("Opus", settings.model_opus or "—")
    table.add_row("Sonnet", settings.model_sonnet or "—")
    table.add_row("Haiku", settings.model_haiku or "—")
    table.add_row("Custom API", "✓ Configured" if settings.custom_api_key else "○ No key")
    table.add_row("Thinking", "Enabled" if settings.enable_thinking else "Disabled")
    table.add_row("Rate Limit", f"{settings.rate_limit_requests}/min")
    table.add_row("Log Level", settings.log_level)

    console.print(table)

    # Key info
    console.print()
    console.print(f"[bold #6366f1]Quick Start:[/]")
    console.print(f"  fc-play server    — Start proxy server")
    console.print(f"  fc-play tui       — Launch dashboard")
    console.print(f"  fc-play admin     — Open admin UI")


@cli.command()
def version():
    """Show version information."""
    console.print(f"[bold #6366f1]{APP_DISPLAY}[/] [dim]v1.0.0[/]")
    console.print(f"[dim]{APP_TAGLINE}[/]")


@cli.callback()
def main_callback():
    """FC-Play main entry point."""
    pass


# Also export as direct functions
def server_main():
    """Entry point for fc-play-server."""
    cli(["server"])


def admin_main():
    """Entry point for fc-play-admin."""
    cli(["admin"])


def tui_main():
    """Entry point for fc-play-tui."""
    cli(["tui"])


if __name__ == "__main__":
    cli()
