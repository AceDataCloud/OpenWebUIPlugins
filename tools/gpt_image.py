"""
title: Ace Data Cloud GPT Image
author: Ace Data Cloud
author_url: https://platform.acedata.cloud
git_url: https://github.com/AceDataCloud/OpenWebUIPlugins
description: GPT Image service actions through Ace Data Cloud using a personal API key.
required_open_webui_version: 0.11.4
requirements: httpx
version: 0.1.0
licence: MIT
"""

from __future__ import annotations

import json
import httpx
from pydantic import BaseModel, Field


class Tools:
    class Valves(BaseModel):
        pass

    class UserValves(BaseModel):
        API_KEY: str = Field(
            default="",
            description="Ace Data Cloud application API key for GPT Image (token only).",
            json_schema_extra={"input": {"type": "password"}},
        )
        ALLOW_BILLABLE_CALLS: bool = Field(
            default=False,
            description="Permit billable GPT Image calls. Turn off when finished.",
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
            return {key: ({"message": "Operation failed; inspect the task ID."} if key == "error" else self._clean(item)) for key, item in value.items() if str(key).lower() not in hidden and not str(key).lower().startswith("internal_")}
        if isinstance(value, list):
            return [self._clean(item) for item in value]
        return value

    def _media_urls(self, value) -> list[str]:
        urls = []
        if isinstance(value, dict):
            for key, item in value.items():
                if key in {"url", "image_url", "video_url", "audio_url", "file_url"} and isinstance(item, str) and item.startswith("https://"):
                    urls.append(item)
                elif isinstance(item, (dict, list)):
                    urls.extend(self._media_urls(item))
        elif isinstance(value, list):
            for item in value:
                urls.extend(self._media_urls(item))
        return list(dict.fromkeys(urls))

    def _result(self, value, fallback_task_id: str = "") -> dict:
        clean = self._clean(value)
        if not isinstance(clean, dict):
            return {"status": "returned", "task_id": fallback_task_id, "media_urls": self._media_urls(clean), "result": clean}
        task = clean.get("task") if isinstance(clean.get("task"), dict) else {}
        task_id = str(clean.get("task_id") or task.get("id") or fallback_task_id or "")
        response = clean.get("response", clean)
        if isinstance(response, str):
            try:
                response = json.loads(response)
            except ValueError:
                response = {}
        state = ""
        if isinstance(response, dict):
            state = str(response.get("status") or response.get("state") or "").lower()
            if not state and isinstance(response.get("data"), dict):
                state = str(response["data"].get("status") or response["data"].get("state") or "").lower()
        if not state and task:
            state = str(task.get("status") or task.get("state") or "").lower()
        urls = self._media_urls(response)
        if clean.get("success") is False or state in {"failed", "error", "cancelled", "canceled", "rejected"}:
            status = "failed"
        elif "finished_at" in clean and clean["finished_at"] is None:
            status = "pending"
        elif state in {"complete", "completed", "succeeded", "succeed", "success", "finished"} or (clean.get("finished_at") and response):
            status = "succeeded"
        elif task_id:
            status = "pending"
        else:
            status = "returned"
        return {"status": status, "task_id": task_id, "media_urls": urls, "result": clean}

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
        if response.status_code >= 400:
            raise RuntimeError(f"Ace Data Cloud HTTP {response.status_code}; check key, access, balance or request history.")
        try:
            value = response.json()
        except ValueError:
            raise RuntimeError("Ace Data Cloud returned invalid JSON.") from None
        if not isinstance(value, (dict, list)):
            raise RuntimeError("Ace Data Cloud returned an invalid result.")
        return self._result(value, task_id)

    async def retrieve_task(self, task_id: str, __user__: dict | None = None) -> dict:
        """Read the status and result of an existing task without submitting a new generation.

        :param task_id: Task ID returned by the first submission.
        """
        if not task_id.strip(): raise ValueError('Task ID is required.')
        return await self._post('/openai/tasks', {'action': 'retrieve', 'id': task_id}, self._key(__user__, billable=False), task_id)


    async def generate_image(self, prompt: str, model: str = 'gpt-image-2', size: str = '1024x1024', quality: str = 'low', __user__: dict | None = None) -> dict:
        """Generate one image from a text prompt. One invocation may be billable. Use retrieve_task with the returned task ID; never repeat this call to poll.

        :param prompt: Text instruction. One call may incur service charges.
        :param model: Public Ace Data Cloud model ID available to your key.
        :param size: Requested output size supported by this model.
        :param quality: Requested output quality; low is the inexpensive first run.
        """
        if not prompt.strip(): raise ValueError('Prompt is required.')
        payload = {'prompt': prompt, 'model': model, 'size': size, 'quality': quality, 'n': 1, 'response_format': 'url', 'async': True}
        return await self._post('/openai/images/generations', payload, self._key(__user__, billable=True))


    async def edit_image(self, prompt: str, image_url: str, model: str = 'gpt-image-2', size: str = '1024x1024', quality: str = 'low', __user__: dict | None = None) -> dict:
        """Edit one image from a public HTTPS reference and prompt. One invocation may be billable. Use retrieve_task with the returned task ID; never repeat this call to poll.

        :param prompt: Text instruction. One call may incur service charges.
        :param image_url: Public HTTPS image URL that you are allowed to process.
        :param model: Public Ace Data Cloud model ID available to your key.
        :param size: Requested output size supported by this model.
        :param quality: Requested output quality; low is the inexpensive first run.
        """
        if not prompt.strip() or not image_url.startswith('https://'): raise ValueError('Prompt and HTTPS image URL are required.')
        payload = {'prompt': prompt, 'image': image_url, 'model': model, 'size': size, 'quality': quality, 'n': 1, 'response_format': 'url', 'async': True}
        return await self._post('/openai/images/edits', payload, self._key(__user__, billable=True))
