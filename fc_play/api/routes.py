"""FC-Play API routes — proxy endpoints with provider routing + key rotation."""

from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from fc_play.config.constants import MODELS_ALL
from fc_play.providers.router import provider_health, resolve_model_name, resolve_provider, route_request

router = APIRouter()


@router.post("/messages")
async def proxy_messages(request: Request):
    """Proxy Anthropic Messages API through configured provider with key rotation."""
    try:
        body = await request.json()
    except Exception:
        return JSONResponse(content={"error": "Invalid JSON body"}, status_code=400)

    model = body.get("model", "")

    # Resolve capability tier
    settings = _get_settings_cached()
    resolved_model = settings.resolve_model(model)
    actual_provider = resolve_provider(resolved_model)
    actual_model = resolve_model_name(resolved_model)

    result = await route_request(f"{actual_provider}/{actual_model}", body)

    if isinstance(result, dict) and result.get("error"):
        status = result.get("status", 502)
        return JSONResponse(
            content={
                "error": {"type": "proxy_error", "message": result["message"]},
                "model": body.get("model", ""),
            },
            status_code=status,
        )

    return JSONResponse(content=result)


@router.post("/messages/count_tokens")
async def count_tokens(request: Request):
    """Count tokens — currently returns estimate."""
    body = await request.json()
    text = ""
    if isinstance(body, dict):
        for msg in body.get("messages", []):
            if isinstance(msg, dict):
                content = msg.get("content", "")
                if isinstance(content, str):
                    text += content
    return JSONResponse(content={"input_tokens": max(1, len(text) // 4)})


@router.get("/models")
async def list_models():
    """List available models from configured providers."""
    models = []
    for model_id in MODELS_ALL:
        models.append({
            "id": f"custom/{model_id}",
            "object": "model",
            "created": 1710000000,
            "owned_by": "fc-play",
        })
    return JSONResponse(content={"data": models})


@router.post("/chat/completions")
async def proxy_chat(request: Request):
    """Proxy OpenAI Chat Completions through configured provider with key rotation."""
    try:
        body = await request.json()
    except Exception:
        return JSONResponse(content={"error": "Invalid JSON body"}, status_code=400)

    result = await route_request(body.get("model", ""), body)

    if isinstance(result, dict) and result.get("error"):
        status = result.get("status", 502)
        return JSONResponse(
            content={
                "error": {"message": result["message"]},
                "model": body.get("model", ""),
            },
            status_code=status,
        )

    return JSONResponse(content=result)


@router.get("/health/keys")
async def key_health():
    """Return health status for all provider key pools."""
    return JSONResponse(content={"providers": provider_health()})


def _get_settings_cached():
    from fc_play.config.settings import get_settings
    return get_settings()
