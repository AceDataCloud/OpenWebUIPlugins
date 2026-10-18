"""
title: Face Transform by Ace Data Cloud
author: Ace Data Cloud
author_url: https://platform.acedata.cloud
git_url: https://github.com/AceDataCloud/OpenWebUIPlugins
description: Use Face Transform through Ace Data Cloud with a personal application API key.
tags: face-transform, ace-data-cloud
required_open_webui_version: 0.11.4
requirements: httpx
version: 0.1.1
licence: MIT
"""

from __future__ import annotations

import json
import re
import httpx
from pydantic import BaseModel, Field


class Tools:
    class Valves(BaseModel):
        pass

    class UserValves(BaseModel):
        API_KEY: str = Field(
            default="",
            description="Ace Data Cloud application API key for Face Transform (token only).",
            json_schema_extra={"input": {"type": "password"}},
        )
        ALLOW_BILLABLE_CALLS: bool = Field(
            default=False,
            description="Permit billable Face Transform calls. Turn off when finished.",
        )

    def __init__(self):
        self.valves = self.Valves()

    def _key(self, user: dict | None, billable: bool) -> str:
        valves = (user or {}).get("valves")
        key = getattr(valves, "API_KEY", "").strip()
        if not key or key.lower().startswith("platform-"):
            raise ValueError("Set your Ace Data Cloud application API key in this Tool's User Valves.")
        if billable and not getattr(valves, "ALLOW_BILLABLE_CALLS", False):
            raise ValueError("Enable Allow Billable Calls in this Tool's User Valves before submitting.")
        return key

    def _clean(self, value):
        hidden = {"request", "request_body", "user_id", "actor_user_id", "credential_id", "authorization_id", "application_id", "api_key", "token", "access_token", "refresh_token", "authorization", "headers", "supplier", "supplier_id", "provider_route", "upstream", "upstream_model", "actual_model", "secret"}
        if isinstance(value, dict):
            result = {}
            for key, item in value.items():
                name = str(key).lower()
                if name in hidden or re.search(r"(^internal(?:_|$)|supplier|upstream|(?:^|_)secret(?:_|$))", name):
                    continue
                result[key] = ({"message": "Operation failed; inspect the task ID."} if name == "error" and item else self._clean(item))
            return result
        if isinstance(value, list):
            return [self._clean(item) for item in value]
        return value

    def _media_urls(self, value) -> list[str]:
        urls = []
        if isinstance(value, dict):
            for key, item in value.items():
                if key in {"url", "image_url", "video_url", "audio_url", "file_url", "raw_image_url"} and isinstance(item, str) and item.startswith("https://"):
                    urls.append(item)
                elif isinstance(item, (dict, list)):
                    urls.extend(self._media_urls(item))
        elif isinstance(value, list):
            for item in value:
                urls.extend(self._media_urls(item))
        return list(dict.fromkeys(urls))

    def _result(self, value, fallback_task_id: str = "") -> dict:
        if isinstance(value, dict) and isinstance(value.get("response"), str):
            value = dict(value)
            try:
                value["response"] = json.loads(value["response"])
            except ValueError:
                value["response"] = {}
        clean = self._clean(value)
        if not isinstance(clean, dict):
            return {"status": "returned", "success": True, "task_id": fallback_task_id, "media_urls": self._media_urls(clean), "result": clean}
        task = clean.get("task") if isinstance(clean.get("task"), dict) else {}
        task_id = str(clean.get("task_id") or task.get("id") or fallback_task_id or "")
        response = clean.get("response", clean)
        states = []
        failures = []
        def visit(node):
            if isinstance(node, dict):
                if node.get("success") is False or node.get("error"):
                    failures.append(True)
                for name, item in node.items():
                    if name in {"status", "state"} and isinstance(item, str):
                        states.append(item.lower())
                    elif name in {"data", "content", "task"} and isinstance(item, (dict, list)):
                        visit(item)
            elif isinstance(node, list):
                for item in node:
                    visit(item)
        visit(response)
        if task and response is not task:
            visit(task)
        if clean.get("success") is False or clean.get("error"):
            failures.append(True)
        failed = failures or any(state in {"failed", "error", "cancelled", "canceled", "rejected"} for state in states)
        complete = bool(states) and all(state in {"complete", "completed", "succeeded", "succeed", "success", "finished"} for state in states)
        unfinished = "finished_at" in clean and clean["finished_at"] is None
        if unfinished:
            status = "pending"
        elif failed:
            status = "failed"
        elif complete or (not states and clean.get("finished_at") and response):
            status = "succeeded"
        elif task_id:
            status = "pending"
        else:
            status = "returned"
        urls = self._media_urls(response) if status in {"succeeded", "returned"} else []
        return {"status": status, "success": status in {"succeeded", "returned"}, "task_id": task_id, "media_urls": urls, "result": clean}

    async def _post(self, path: str, payload: dict, key: str, task_id: str = "", extra_headers: dict | None = None) -> dict:
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(90, connect=10)) as client:
                response = await client.post(
                    "https://api.acedata.cloud" + path,
                    json=payload,
                    headers={"Authorization": f"Bearer {key}", "Accept": "application/json", **(extra_headers or {})},
                )
        except httpx.TransportError:
            raise RuntimeError("Connection failed; check request history before submitting again.") from None
        if not 200 <= response.status_code < 300:
            raise RuntimeError(f"Ace Data Cloud HTTP {response.status_code}; check key, access, balance or request history.")
        try:
            value = response.json()
        except ValueError:
            raise RuntimeError("Ace Data Cloud returned invalid JSON.") from None
        if not isinstance(value, (dict, list)):
            raise RuntimeError("Ace Data Cloud returned an invalid result.")
        return self._result(value, task_id)

    async def analyze_face(self, image_url: str, __user__: dict | None = None) -> dict:
        """Analyze face landmarks in a public HTTPS image. One invocation may be billable. Returns the API result directly.

        :param image_url: Public HTTPS image URL that you are allowed to process.
        """
        if not image_url.startswith('https://'): raise ValueError('HTTPS image URL is required.')
        payload = {'image_url': image_url}
        return await self._post('/face/analyze', payload, self._key(__user__, billable=True))


    async def beautify_face(self, image_url: str, smoothing: int = 0, whitening: int = 0, __user__: dict | None = None) -> dict:
        """Beautify a face in a public HTTPS image. One invocation may be billable. Returns the API result directly.

        :param image_url: Public HTTPS image URL that you are allowed to process.
        :param smoothing: Face smoothing strength supported by the API.
        :param whitening: Face whitening strength supported by the API.
        """
        if not image_url.startswith('https://'): raise ValueError('HTTPS image URL is required.')
        payload = {'image_url': image_url, 'smoothing': smoothing, 'whitening': whitening}
        return await self._post('/face/beautify', payload, self._key(__user__, billable=True))
