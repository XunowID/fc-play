"""FC-Play server entry point — starts the proxy ASGI application."""

from __future__ import annotations

from fc_play.api.app import create_app, create_asgi_app

__all__ = ["app", "create_app"]

app = create_asgi_app()


def main() -> None:
    """Run the server via uvicorn."""
    import uvicorn

    from fc_play.config.settings import get_settings

    settings = get_settings()

    uvicorn.run(
        "server:app",
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level.lower(),
        timeout_graceful_shutdown=5,
        reload=False,
    )


if __name__ == "__main__":
    main()
