"""
title: Ace Data Cloud Google Search
author: Ace Data Cloud
author_url: https://platform.acedata.cloud
git_url: https://github.com/AceDataCloud/OpenWebUIPlugins
description: Search the web, images, news, places, maps or videos using your Ace Data Cloud key.
required_open_webui_version: 0.11.4
requirements: httpx
version: 0.1.0
licence: MIT
"""

from __future__ import annotations

import httpx
from pydantic import BaseModel, Field


class Tools:
    class Valves(BaseModel):
        pass

    class UserValves(BaseModel):
        API_KEY: str = Field(
            default="",
            description="Ace Data Cloud application API key for Google Search (token only).",
            json_schema_extra={"input": {"type": "password"}},
        )
        ALLOW_BILLABLE_CALLS: bool = Field(
            default=False,
            description="Allow this Tool to make billable searches. Disable when done.",
        )

    def __init__(self):
        self.valves = self.Valves()

    async def search(
        self,
        query: str,
        search_type: str = "search",
        number: int = 3,
        page: int = 1,
        country: str = "",
        language: str = "",
        __user__: dict | None = None,
    ) -> dict:
        """Search Google through Ace Data Cloud. One invocation makes one potentially billable API call.

        :param query: Search terms, up to 2048 characters.
        :param search_type: One of search, images, news, maps, places, videos.
        :param number: Results to request, from 1 to 100; start with 3.
        :param page: Result page, from 1 to 100.
        :param country: Optional country code or name supported by the API.
        :param language: Optional language code supported by the API.
        """
        valves = (__user__ or {}).get("valves")
        key = getattr(valves, "API_KEY", "").strip()
        if not key or key.lower().startswith("platform-"):
            raise ValueError("Set your Ace Data Cloud application API key in this Tool's User Valves.")
        if not getattr(valves, "ALLOW_BILLABLE_CALLS", False):
            raise ValueError("Enable Allow Billable Calls in this Tool's User Valves before searching.")
        if not query.strip() or len(query) > 2048:
            raise ValueError("Query must contain 1 to 2048 characters.")
        if search_type not in {"search", "images", "news", "maps", "places", "videos"}:
            raise ValueError("Unsupported search type.")
        if not 1 <= number <= 100 or not 1 <= page <= 100:
            raise ValueError("Number and page must each be between 1 and 100.")
        payload = {"query": query, "type": search_type, "number": number, "page": page}
        if country:
            payload["country"] = country
        if language:
            payload["language"] = language
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(60, connect=10)) as client:
                response = await client.post(
                    "https://api.acedata.cloud/serp/google",
                    json=payload,
                    headers={"Authorization": f"Bearer {key}", "Accept": "application/json"},
                )
        except httpx.TransportError:
            raise RuntimeError("Search connection failed; check request history before retrying.") from None
        if response.status_code >= 400:
            raise RuntimeError(f"Ace Data Cloud HTTP {response.status_code}; check key, balance and service access.")
        try:
            result = response.json()
        except ValueError:
            raise RuntimeError("Search returned invalid JSON.") from None
        if not isinstance(result, (dict, list)):
            raise RuntimeError("Search returned an invalid result.")
        return self._clean(result)

    def _clean(self, value):
        hidden = {"authorization", "headers", "api_key", "access_token", "refresh_token", "supplier", "upstream", "request_body"}
        if isinstance(value, dict):
            return {key: self._clean(item) for key, item in value.items() if key.lower() not in hidden}
        if isinstance(value, list):
            return [self._clean(item) for item in value]
        return value
