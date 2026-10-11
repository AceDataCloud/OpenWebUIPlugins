"""
title: Ace Data Cloud Models
author: Ace Data Cloud
author_url: https://platform.acedata.cloud
git_url: https://github.com/AceDataCloud/OpenWebUIPlugins
description: Use Ace Data Cloud chat models with a personal API key.
required_open_webui_version: 0.11.4
requirements: httpx
version: 0.1.0
licence: MIT
"""

from __future__ import annotations

import httpx
from pydantic import BaseModel, Field


API_URL = "https://api.acedata.cloud/v1/chat/completions"
ALLOWED_FIELDS = {
    "messages",
    "stream",
    "temperature",
    "top_p",
    "max_tokens",
    "max_completion_tokens",
    "frequency_penalty",
    "presence_penalty",
    "stop",
    "seed",
    "n",
    "response_format",
    "tools",
    "tool_choice",
    "parallel_tool_calls",
    "reasoning_effort",
    "stream_options",
}


class Pipe:
    name = "Ace Data Cloud/"

    class Valves(BaseModel):
        MODEL_IDS: str = Field(
            default="gpt-5.6-luna,deepseek-v4-flash",
            description="Comma-separated Ace Data Cloud chat model IDs to show in the model picker.",
        )

    class UserValves(BaseModel):
        API_KEY: str = Field(
            default="",
            description="Your Ace Data Cloud application API key (token only, without Bearer).",
            json_schema_extra={"input": {"type": "password"}},
        )

    def __init__(self):
        self.valves = self.Valves()

    def pipes(self) -> list[dict[str, str]]:
        ids = [item.strip() for item in self.valves.MODEL_IDS.split(",")]
        ids = [item for item in dict.fromkeys(ids) if item and "/" not in item]
        return [{"id": item, "name": item} for item in ids]

    async def pipe(self, body: dict, __user__: dict | None = None):
        user_valves = (__user__ or {}).get("valves")
        key = getattr(user_valves, "API_KEY", "").strip()
        if not key or key.lower().startswith("platform-"):
            raise ValueError("Set your Ace Data Cloud application API key in this model's User Valves.")

        selected = str(body.get("model", ""))
        model = selected.partition(".")[2] if "." in selected else selected
        available = {item["id"] for item in self.pipes()}
        if not model and len(available) == 1:
            model = next(iter(available))
        if model not in available:
            raise ValueError("The selected model is not configured in the Pipe's Model IDs.")
        if not isinstance(body.get("messages"), list) or not body["messages"]:
            raise ValueError("A nonempty messages list is required.")

        payload = {name: body[name] for name in ALLOWED_FIELDS if name in body}
        payload["model"] = model
        headers = {"Authorization": f"Bearer {key}", "Accept": "application/json"}
        if payload.get("stream"):

            async def events():
                try:
                    async with httpx.AsyncClient(timeout=httpx.Timeout(90, connect=10)) as client:
                        async with client.stream("POST", API_URL, json=payload, headers=headers) as response:
                            if not 200 <= response.status_code < 300:
                                raise RuntimeError(f"Ace Data Cloud HTTP {response.status_code}; check key, balance and model access.")
                            async for line in response.aiter_lines():
                                if line.startswith("data:"):
                                    yield line + "\n\n"
                except httpx.TransportError:
                    raise RuntimeError("Ace Data Cloud connection failed; check request history before retrying.") from None

            return events()

        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(90, connect=10)) as client:
                response = await client.post(API_URL, json=payload, headers=headers)
        except httpx.TransportError:
            raise RuntimeError("Ace Data Cloud connection failed; check request history before retrying.") from None
        if not 200 <= response.status_code < 300:
            raise RuntimeError(f"Ace Data Cloud HTTP {response.status_code}; check key, balance and model access.")
        try:
            result = response.json()
        except ValueError:
            raise RuntimeError("Ace Data Cloud returned invalid JSON.") from None
        if not isinstance(result, dict) or result.get("error"):
            raise RuntimeError("Ace Data Cloud returned an error; check request history before retrying.")
        return result
