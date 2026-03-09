from __future__ import annotations

import os
from typing import Any

import httpx

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODEL = "openai/gpt-oss-120b"


def get_openrouter_key() -> str:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY is not set")
    return api_key


def call_openrouter(
    messages: list[dict[str, str]],
    api_key: str,
    client: httpx.Client | None = None,
) -> str:
    payload = {
        "model": OPENROUTER_MODEL,
        "messages": messages,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    if client is None:
        with httpx.Client(timeout=20) as session:
            response = session.post(OPENROUTER_URL, json=payload, headers=headers)
    else:
        response = client.post(OPENROUTER_URL, json=payload, headers=headers)

    response.raise_for_status()
    data: dict[str, Any] = response.json()
    choices = data.get("choices")
    if not choices:
        raise ValueError("OpenRouter response missing choices")
    message = choices[0].get("message") if isinstance(choices[0], dict) else None
    content = message.get("content") if isinstance(message, dict) else None
    if not content:
        raise ValueError("OpenRouter response missing content")
    return str(content)
