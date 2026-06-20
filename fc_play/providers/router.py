"""Provider router — route model requests to the right provider with key rotation."""

from __future__ import annotations

from dataclasses import dataclass

import httpx
from typing import Any

from fc_play.config.settings import Settings, get_settings
from fc_play.providers.key_pool import KeyPool


# ─── Provider registry ─────────────────────────────────────────────────────

@dataclass
class ProviderRoute:
    prefix: str
    name: str
    base_url: str
    api_type: str  # "anthropic" | "openai"
    key_env_var: str
    pool: KeyPool | None = None


def _build_routes(settings: Settings) -> list[ProviderRoute]:
    """Build provider routes from settings."""
    routes: list[ProviderRoute] = []

    for pid, display, base_url, api_type in PROVIDER_REGISTRY:
        keys = settings.get_provider_keys(pid)
        pool = KeyPool(keys) if keys else None
        routes.append(ProviderRoute(
            prefix=pid,
            name=display,
            base_url=base_url,
            api_type=api_type,
            key_env_var=_key_env(pid),
            pool=pool,
        ))

    return routes


def _key_env(provider: str) -> str:
    """Get the env var name for a provider's primary key."""
    name = provider.upper()
    if not name.endswith("_API_KEY"):
        name += "_API_KEY"
    return name


# ─── Provider metadata ─────────────────────────────────────────────────────

# (id, display_name, base_url, api_type)
PROVIDER_REGISTRY: list[tuple[str, str, str, str]] = [
    ("custom", "Direct API", "", "anthropic"),
    ("anthropic", "Anthropic", "https://api.anthropic.com", "anthropic"),
    ("openai", "OpenAI", "https://api.openai.com", "openai"),
    ("openrouter", "OpenRouter", "https://openrouter.ai", "anthropic"),
    ("gemini", "Gemini", "https://generativelanguage.googleapis.com", "openai"),
    ("deepseek", "DeepSeek", "https://api.deepseek.com", "openai"),
    ("mistral", "Mistral", "https://api.mistral.ai", "openai"),
    ("codestral", "Codestral", "https://codestral.mistral.ai", "openai"),
    ("groq", "Groq", "https://api.groq.com", "openai"),
    ("fireworks", "Fireworks", "https://api.fireworks.ai", "openai"),
    ("together", "Together", "https://api.together.ai", "openai"),
    ("nvidia_nim", "NVIDIA NIM", "", "openai"),
    ("cerebras", "Cerebras", "https://api.cerebras.ai", "openai"),
    ("kimi", "Kimi", "https://api.moonshot.cn", "openai"),
    ("wafer", "Wafer", "https://api.waferai.com", "anthropic"),
    ("opencode", "OpenCode", "", "openai"),
    ("zai", "Z.ai", "", "anthropic"),
]


def resolve_provider(model: str) -> str:
    """Extract provider prefix from model string.

    Examples:
        'anthropic/claude-sonnet-4-20250514' → 'anthropic'
        'openai/gpt-4o' → 'openai'
        'custom/claude-sonnet-4' → 'custom'
    """
    if "/" in model:
        return model.split("/")[0]
    return "custom"


def resolve_model_name(model: str) -> str:
    """Extract model name from provider/model string."""
    if "/" in model:
        return model.split("/", 1)[1]
    return model


# ─── Routing ────────────────────────────────────────────────────────────────

def _find_route(provider_id: str, settings: Settings | None = None) -> ProviderRoute | None:
    """Find a provider route by ID."""
    s = settings or get_settings()
    for r in _build_routes(s):
        if r.prefix == provider_id:
            return r
    return None


def get_client_headers(route: ProviderRoute) -> tuple[dict[str, str], str | None]:
    """Get HTTP headers for a provider request."""
    headers: dict[str, str] = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    # Get the next key from the pool
    key = route.pool.next() if route.pool else None

    if route.api_type == "anthropic":
        headers["anthropic-version"] = "2023-06-01"
        if key:
            headers["x-api-key"] = key
    else:
        if key:
            headers["Authorization"] = f"Bearer {key}"

    return headers, key


async def route_request(
    model: str,
    body: dict[str, Any],
) -> dict[str, Any]:
    """Route a request to the appropriate provider.

    Args:
        model: Full model string (e.g. 'anthropic/claude-sonnet-4')
        body: Request body

    Returns:
        Response data from the provider
    """
    provider_id = resolve_provider(model)
    model_name = resolve_model_name(model)
    route = _find_route(provider_id)

    if not route:
        return {
            "error": True,
            "message": f"Unknown provider '{provider_id}' for model '{model}'",
        }

    if not route.pool or route.pool.total_keys == 0:
        return {
            "error": True,
            "message": f"No API keys configured for provider '{route.name}' ({provider_id})",
        }

    pool = route.pool

    # Send request via appropriate API
    if route.api_type == "anthropic":
        return await _route_anthropic(route, pool, model_name, body)
    else:
        return await _route_openai(route, pool, model_name, body)


async def _route_anthropic(
    route: ProviderRoute,
    pool: KeyPool,
    model_name: str,
    body: dict[str, Any],
) -> dict[str, Any]:
    """Route via Anthropic Messages API format."""
    headers, key = get_client_headers(route)
    if not key:
        return {"error": True, "message": "No available API key"}

    payload = {**body, "model": model_name}

    try:
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                f"{route.base_url}/v1/messages",
                json=payload,
                headers=headers,
            )
            if resp.is_success:
                pool.record_success(key)
                return resp.json()
            else:
                pool.record_error(key)
                return {
                    "error": True,
                    "status": resp.status_code,
                    "message": resp.text,
                }
    except httpx.TimeoutException:
        pool.record_error(key)
        return {"error": True, "message": "Request timed out"}
    except httpx.RequestError as e:
        pool.record_error(key)
        return {"error": True, "message": str(e)}


async def _route_openai(
    route: ProviderRoute,
    pool: KeyPool,
    model_name: str,
    body: dict[str, Any],
) -> dict[str, Any]:
    """Route via OpenAI Chat Completions API format."""
    headers, key = get_client_headers(route)
    if not key:
        return {"error": True, "message": "No available API key"}

    payload = {**body, "model": model_name}

    try:
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                f"{route.base_url}/v1/chat/completions",
                json=payload,
                headers=headers,
            )
            if resp.is_success:
                pool.record_success(key)
                return resp.json()
            else:
                pool.record_error(key)
                return {
                    "error": True,
                    "status": resp.status_code,
                    "message": resp.text,
                }
    except httpx.TimeoutException:
        pool.record_error(key)
        return {"error": True, "message": "Request timed out"}
    except httpx.RequestError as e:
        pool.record_error(key)
        return {"error": True, "message": str(e)}


# ─── Health / Status ───────────────────────────────────────────────────────

def provider_health() -> list[dict]:
    """Return health status for all configured providers."""
    settings = get_settings()
    health: list[dict] = []

    for pid, display, *_ in PROVIDER_REGISTRY:
        keys = settings.get_provider_keys(pid)
        if not keys:
            continue

        pool = KeyPool(keys)
        health.append({
            "id": pid,
            "name": display,
            "total_keys": pool.total_keys,
            "available_keys": pool.available_keys,
            "keys": pool.health(),
        })

    return health
