"""FC-Play FastAPI application factory."""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from loguru import logger

from fc_play.api.admin_routes import router as admin_router
from fc_play.api.routes import router as api_router
from fc_play.config.settings import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan — startup/shutdown hooks."""
    settings = get_settings()
    logger.info("🚀 FC-Play server starting on {}:{}", settings.host, settings.port)
    logger.info("📡 Model: {}", settings.model)
    yield
    logger.info("👋 FC-Play server shutting down")


def create_app() -> FastAPI:
    """Create the FastAPI application with all routes."""
    app = FastAPI(
        title="FC-Play API",
        description="Play with Claude — Free, Fast, Fabulous",
        version="1.0.0",
        lifespan=lifespan,
    )

    # Mount admin static files
    static_dir = Path(__file__).resolve().parent / "admin_static"
    if static_dir.exists():
        app.mount("/admin/assets", StaticFiles(directory=str(static_dir)), name="admin_assets")

    # Include routers
    app.include_router(api_router, prefix="/v1")
    app.include_router(admin_router, prefix="/admin")

    # Health check
    @app.get("/health")
    async def health():
        return {"status": "ok", "service": "fc-play"}

    return app


def create_asgi_app() -> FastAPI:
    """Create the ASGI application (alias for create_app)."""
    return create_app()
