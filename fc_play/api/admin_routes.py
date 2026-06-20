"""FC-Play admin API — configuration endpoints using managed env persistence."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
from loguru import logger

from fc_play.api.admin_config import (
    FIELD_BY_KEY,
    load_config_response,
    validate_updates,
    write_managed_env,
)
from fc_play.config.settings import invalidate_settings_cache
from fc_play.providers.router import provider_health

router = APIRouter()


# ---------------------------------------------------------------------------
# Admin page
# ---------------------------------------------------------------------------

@router.get("", response_class=HTMLResponse, include_in_schema=False)
async def admin_page():
    """Serve the admin dashboard HTML."""
    html_path = Path(__file__).resolve().parent / "admin_static" / "index.html"
    if html_path.exists():
        return HTMLResponse(content=html_path.read_text(encoding="utf-8"))
    return HTMLResponse(content="<h1>Admin UI not found</h1>", status_code=404)


# ---------------------------------------------------------------------------
# Config API
# ---------------------------------------------------------------------------

@router.get("/api/config")
async def get_config():
    """Get the full configuration specification."""
    return load_config_response()


@router.post("/api/config/validate")
async def validate_config(request: Request):
    """Validate proposed changes against the Settings model."""
    try:
        changes = await request.json()
        filtered = {k: v for k, v in changes.items() if k in FIELD_BY_KEY}
        result = validate_updates(filtered)
        if result["valid"]:
            return JSONResponse(content={"valid": True})
        return JSONResponse(content={"valid": False, "errors": result["errors"]}, status_code=422)
    except Exception as e:
        logger.error("Validate failed: {}", e)
        return JSONResponse(content={"valid": False, "errors": [str(e)]}, status_code=422)


@router.post("/api/config/apply")
async def apply_config(request: Request):
    """Validate and atomically write managed env file, then invalidate cache."""
    try:
        payload = await request.json()
        filtered = {k: v for k, v in payload.items() if k in FIELD_BY_KEY}
        if not filtered:
            return JSONResponse(content={"saved": False, "error": "No valid fields to save"}, status_code=422)

        result = write_managed_env(filtered)
        if not result["applied"]:
            return JSONResponse(
                content={"saved": False, "errors": result.get("errors", [])},
                status_code=422,
            )

        # Invalidate settings cache so next request picks up changes
        invalidate_settings_cache()

        pending = result.get("pending_fields", [])
        needs_restart = bool(pending)
        logger.info("Config applied: {} fields ({} pending restart)", len(filtered), len(pending))

        return JSONResponse(content={
            "saved": True,
            "restart_required": needs_restart,
            "pending_fields": pending,
        })
    except Exception as e:
        logger.error("Apply failed: {}", e)
        return JSONResponse(content={"saved": False, "error": str(e)}, status_code=422)


# ---------------------------------------------------------------------------
# Key health
# ---------------------------------------------------------------------------

@router.get("/api/keys")
async def get_key_health():
    """Get key pool health for admin UI."""
    return JSONResponse(content={"providers": provider_health()})
