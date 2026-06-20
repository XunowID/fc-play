"""FC-Play API routes — proxy endpoints for Anthropic & OpenAI APIs."""

from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter()


@router.post("/messages")
async def proxy_messages(request: Request):
    """Proxy Anthropic Messages API requests through configured provider."""
    body = await request.json()
    return JSONResponse(
        content={
            "id": "msg_proxy_001",
            "type": "message",
            "role": "assistant",
            "content": [{"type": "text", "text": "FC-Play proxy active. Provider routing not yet implemented."}],
            "model": body.get("model", "unknown"),
            "stop_reason": "end_turn",
            "usage": {"input_tokens": 0, "output_tokens": 0},
        }
    )


@router.post("/messages/count_tokens")
async def count_tokens(request: Request):
    """Count tokens for a messages request."""
    return JSONResponse(content={"input_tokens": 0})


@router.get("/models")
async def list_models():
    """List available models."""
    from fc_play.config.constants import CLAUDE_MODELS

    models = []
    for m in CLAUDE_MODELS:
        models.append({
            "id": f"custom/{m}",
            "object": "model",
            "created": 1710000000,
            "owned_by": "fc-play",
        })
    return JSONResponse(content={"data": models})


@router.post("/chat/completions")
async def proxy_chat(request: Request):
    """Proxy OpenAI Chat Completions API requests."""
    body = await request.json()
    return JSONResponse(
        content={
            "id": "chat_proxy_001",
            "object": "chat.completion",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "FC-Play proxy active. Provider routing not yet implemented.",
                    },
                    "finish_reason": "stop",
                }
            ],
            "model": body.get("model", "unknown"),
            "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
        }
    )
