"""Build self-contained Open WebUI Community Tools from one reviewed source.

Community imports one Python file at a time. The generated files intentionally
contain their own small transport helper and do not import this generator.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Action:
    name: str
    path: str
    signature: str
    payload: str
    description: str
    guard: str = ""
    async_task: bool = True
    headers: str | None = None


@dataclass(frozen=True)
class Service:
    slug: str
    title: str
    task_path: str | None
    actions: tuple[Action, ...]


SERVICES = (
    Service("gpt_image", "GPT Image", "/openai/tasks", (
        Action("generate_image", "/openai/images/generations", "prompt: str, model: str = 'gpt-image-2', size: str = '1024x1024', quality: str = 'low'", "{'prompt': prompt, 'model': model, 'size': size, 'quality': quality, 'n': 1, 'response_format': 'url', 'async': True}", "Generate one image from a text prompt.", "if not prompt.strip(): raise ValueError('Prompt is required.')"),
        Action("edit_image", "/openai/images/edits", "prompt: str, image_url: str, model: str = 'gpt-image-2', size: str = '1024x1024', quality: str = 'low'", "{'prompt': prompt, 'image': image_url, 'model': model, 'size': size, 'quality': quality, 'n': 1, 'response_format': 'url', 'async': True}", "Edit one image from a public HTTPS reference and prompt.", "if not prompt.strip() or not image_url.startswith('https://'): raise ValueError('Prompt and HTTPS image URL are required.')"),
    )),
    Service("suno", "Suno", "/suno/tasks", (
        Action("generate_music", "/suno/audios", "prompt: str, model: str = 'chirp-v6', instrumental: bool = True", "{'action': 'generate', 'prompt': prompt, 'model': model, 'custom': False, 'instrumental': instrumental, 'async': True}", "Generate a music track from a prompt.", "if not prompt.strip(): raise ValueError('Prompt is required.')"),
        Action("generate_lyrics", "/suno/lyrics", "prompt: str, model: str = 'default'", "{'prompt': prompt, 'model': model}", "Generate lyrics from a prompt.", "if not prompt.strip(): raise ValueError('Prompt is required.')", False),
    )),
    Service("seedance", "Seedance", "/seedance/tasks", (
        Action("generate_video", "/seedance/videos", "prompt: str, model: str = 'doubao-seedance-2-0-mini-260615', duration: int = 4, resolution: str = '480p', ratio: str = '16:9'", "{'model': model, 'content': [{'type': 'text', 'text': prompt}], 'duration': duration, 'resolution': resolution, 'ratio': ratio, 'generate_audio': False, 'async': True}", "Generate a video from a text prompt.", "if not prompt.strip() or not 4 <= duration <= 15: raise ValueError('Prompt and a supported duration are required.')"),
    )),
    Service("fish_audio", "Fish Audio", "/fish/tasks", (
        Action("text_to_speech", "/fish/tts", "text: str, model: str = 's2-pro', audio_format: str = 'mp3', reference_id: str = ''", "{'text': text, 'format': audio_format, **({'reference_id': reference_id} if reference_id else {}), 'async': True}", "Convert text to speech with a saved voice or the default voice.", "if not text.strip(): raise ValueError('Text is required.')", headers="{'model': model}"),
    )),
    Service("seedream", "Seedream", "/seedream/tasks", (
        Action("generate_image", "/seedream/images", "prompt: str, model: str = 'doubao-seedream-5-0-lite-260128', size: str = '2K'", "{'prompt': prompt, 'model': model, 'size': size, 'response_format': 'url', 'async': True}", "Generate an image from text.", "if not prompt.strip(): raise ValueError('Prompt is required.')"),
        Action("edit_image", "/seedream/images", "prompt: str, image_url: str, model: str = 'doubao-seedream-5-0-lite-260128', size: str = '2K'", "{'prompt': prompt, 'image': image_url, 'model': model, 'size': size, 'response_format': 'url', 'async': True}", "Edit an image from a public HTTPS reference.", "if not prompt.strip() or not image_url.startswith('https://'): raise ValueError('Prompt and HTTPS image URL are required.')"),
    )),
    Service("happy_horse", "Happy Horse", "/happyhorse/tasks", (
        Action("generate_video", "/happyhorse/videos", "prompt: str, model: str = 'happyhorse-1.1-t2v', duration: int = 3, resolution: str = '720P', ratio: str = '16:9'", "{'action': 'generate', 'prompt': prompt, 'model': model, 'duration': duration, 'resolution': resolution, 'ratio': ratio, 'async': True}", "Generate a short video from text.", "if not prompt.strip(): raise ValueError('Prompt is required.')"),
    )),
    Service("qwen_image", "Qwen Image", "/qwen-image/tasks", (
        Action("generate_image", "/qwen-image/images", "prompt: str, model: str = 'qwen-image-3.0', size: str = '1024*1024'", "{'prompt': prompt, 'model': model, 'size': size, 'n': 1, 'async': True}", "Generate one image from text.", "if not prompt.strip(): raise ValueError('Prompt is required.')"),
    )),
    Service("veo", "Veo", "/veo/tasks", (
        Action("generate_video", "/veo/videos", "prompt: str, model: str = 'veo31-fast', aspect_ratio: str = '16:9'", "{'action': 'text2video', 'prompt': prompt, 'model': model, 'aspect_ratio': aspect_ratio, 'async': True}", "Generate a video from text.", "if not prompt.strip(): raise ValueError('Prompt is required.')"),
        Action("extend_video", "/veo/extend", "video_id: str, model: str = 'veo31-fast', prompt: str = ''", "{'video_id': video_id, 'model': model, **({'prompt': prompt} if prompt else {}), 'async': True}", "Extend an existing Veo video by its ID.", "if not video_id.strip(): raise ValueError('Video ID is required.')"),
    )),
    Service("grok", "Grok", "/grok/tasks", (
        Action("ask_grok", "/grok/chat/completions", "prompt: str, model: str = 'grok-4'", "{'model': model, 'messages': [{'role': 'user', 'content': prompt}], 'stream': False}", "Ask a Grok chat model one question.", "if not prompt.strip(): raise ValueError('Prompt is required.')", False),
        Action("generate_video", "/grok/videos", "prompt: str, model: str = 'grok-imagine-video'", "{'prompt': prompt, 'model': model, 'async': True}", "Generate a Grok video with a model available to your account.", "if not prompt.strip() or not model.strip(): raise ValueError('Prompt and public model ID are required.')"),
    )),
    Service("face_transform", "Face Transform", None, (
        Action("analyze_face", "/face/analyze", "image_url: str", "{'image_url': image_url}", "Analyze face landmarks in a public HTTPS image.", "if not image_url.startswith('https://'): raise ValueError('HTTPS image URL is required.')", False),
        Action("beautify_face", "/face/beautify", "image_url: str, smoothing: int = 0, whitening: int = 0", "{'image_url': image_url, 'smoothing': smoothing, 'whitening': whitening}", "Beautify a face in a public HTTPS image.", "if not image_url.startswith('https://'): raise ValueError('HTTPS image URL is required.')", False),
    )),
    Service("midjourney", "Midjourney", "/midjourney/tasks", (
        Action("imagine", "/midjourney/imagine", "prompt: str, version: str = '8.2', mode: str = 'fast'", "{'action': 'generate', 'prompt': prompt, 'version': version, 'mode': mode, 'async': True}", "Generate an image from text.", "if not prompt.strip(): raise ValueError('Prompt is required.')"),
    )),
    Service("flux", "Flux", "/flux/tasks", (
        Action("generate_image", "/flux/images", "prompt: str, model: str = 'flux-dev', size: str = '1024x1024'", "{'action': 'generate', 'prompt': prompt, 'model': model, 'size': size, 'count': 1, 'async': True}", "Generate one image from text.", "if not prompt.strip(): raise ValueError('Prompt is required.')"),
        Action("edit_image", "/flux/images", "prompt: str, image_url: str, model: str = 'flux-kontext-pro', size: str = '1:1'", "{'action': 'edit', 'prompt': prompt, 'image_url': image_url, 'model': model, 'size': size, 'count': 1, 'async': True}", "Edit an image from a public HTTPS reference.", "if not prompt.strip() or not image_url.startswith('https://'): raise ValueError('Prompt and HTTPS image URL are required.')"),
    )),
    Service("minimax_h3", "MiniMax H3", "/minimax/tasks", (
        Action("generate_video", "/minimax/videos", "prompt: str, duration: int = 4, resolution: str = '768P', ratio: str = '16:9'", "{'model': 'MiniMax-H3', 'content': [{'type': 'text', 'text': prompt}], 'duration': duration, 'resolution': resolution, 'ratio': ratio, 'async': True}", "Generate a video with MiniMax H3.", "if not prompt.strip() or not 4 <= duration <= 15: raise ValueError('Prompt and a duration from 4 to 15 seconds are required.')"),
    )),
    Service("wan", "Wan", "/wan/tasks", (
        Action("generate_video", "/wan/videos", "prompt: str, model: str = 'wan2.6-t2v', duration: int = 5, resolution: str = '720P'", "{'action': 'text2video', 'prompt': prompt, 'model': model, 'duration': duration, 'resolution': resolution, 'async': True}", "Generate a video from text.", "if not prompt.strip(): raise ValueError('Prompt is required.')"),
    )),
    Service("kling", "Kling", "/kling/tasks", (
        Action("generate_video", "/kling/videos", "prompt: str, model: str = 'kling-v3-turbo', duration: int = 5, mode: str = 'std', aspect_ratio: str = '16:9'", "{'action': 'text2video', 'prompt': prompt, 'model': model, 'duration': duration, 'mode': mode, 'aspect_ratio': aspect_ratio, 'async': True}", "Generate a video from text.", "if not prompt.strip(): raise ValueError('Prompt is required.')"),
    )),
    Service("nano_banana", "Nano Banana", "/nano-banana/tasks", (
        Action("generate_image", "/nano-banana/images", "prompt: str, model: str = 'nano-banana-2-lite', resolution: str = '1K', aspect_ratio: str = '1:1'", "{'action': 'generate', 'prompt': prompt, 'model': model, 'resolution': resolution, 'aspect_ratio': aspect_ratio, 'count': 1, 'async': True}", "Generate one image from text.", "if not prompt.strip(): raise ValueError('Prompt is required.')"),
        Action("edit_image", "/nano-banana/images", "prompt: str, image_url: str, model: str = 'nano-banana-2-lite', resolution: str = '1K', aspect_ratio: str = '1:1'", "{'action': 'edit', 'prompt': prompt, 'image_urls': [image_url], 'model': model, 'resolution': resolution, 'aspect_ratio': aspect_ratio, 'count': 1, 'async': True}", "Edit one image from a public HTTPS reference.", "if not prompt.strip() or not image_url.startswith('https://'): raise ValueError('Prompt and HTTPS image URL are required.')"),
    )),
)


PARAM_DOCS = {
    "prompt": "Text instruction. One call may incur service charges.",
    "text": "Text to synthesize.",
    "image_url": "Public HTTPS image URL that you are allowed to process.",
    "model": "Public Ace Data Cloud model ID available to your key.",
    "video_id": "Existing video ID; extending it may incur a new charge.",
    "size": "Requested output size supported by this model.",
    "quality": "Requested output quality; low is the inexpensive first run.",
    "duration": "Output duration in seconds, subject to model limits.",
    "resolution": "Requested output resolution.",
    "ratio": "Output aspect ratio.",
    "aspect_ratio": "Output aspect ratio.",
    "audio_format": "Audio encoding format.",
    "reference_id": "Optional saved voice ID.",
    "instrumental": "Whether to omit vocals.",
    "version": "Public Midjourney version.",
    "mode": "Supported mode; faster modes may cost differently.",
    "smoothing": "Face smoothing strength supported by the API.",
    "whitening": "Face whitening strength supported by the API.",
}


COMMON = '''"""
title: Ace Data Cloud {title}
author: Ace Data Cloud
author_url: https://platform.acedata.cloud
git_url: https://github.com/AceDataCloud/OpenWebUIPlugins
description: {title} service actions through Ace Data Cloud using a personal API key.
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
            description="Ace Data Cloud application API key for {title} (token only).",
            json_schema_extra={{"input": {{"type": "password"}}}},
        )
        ALLOW_BILLABLE_CALLS: bool = Field(
            default=False,
            description="Permit billable {title} calls. Turn off when finished.",
        )

    def __init__(self):
        self.valves = self.Valves()

    def _key(self, user: dict | None, billable: bool) -> str:
        valves = (user or {{}}).get("valves")
        key = getattr(valves, "API_KEY", "").strip()
        if not key or key.lower().startswith("platform-"):
            raise ValueError("Set your Ace Data Cloud application API key in this Tool's User Valves.")
        if billable and not getattr(valves, "ALLOW_BILLABLE_CALLS", False):
            raise ValueError("Enable Allow Billable Calls in this Tool's User Valves before submitting.")
        return key

    def _clean(self, value):
        hidden = {{"request", "request_body", "user_id", "actor_user_id", "credential_id", "authorization_id", "application_id", "api_key", "token", "access_token", "refresh_token", "authorization", "headers", "supplier", "supplier_id", "provider_route", "upstream", "upstream_model", "actual_model", "secret"}}
        if isinstance(value, dict):
            return {{key: ({{"message": "Operation failed; inspect the task ID."}} if key == "error" else self._clean(item)) for key, item in value.items() if str(key).lower() not in hidden and not str(key).lower().startswith("internal_")}}
        if isinstance(value, list):
            return [self._clean(item) for item in value]
        return value

    def _media_urls(self, value) -> list[str]:
        urls = []
        if isinstance(value, dict):
            for key, item in value.items():
                if key in {{"url", "image_url", "video_url", "audio_url", "file_url"}} and isinstance(item, str) and item.startswith("https://"):
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
            return {{"status": "returned", "task_id": fallback_task_id, "media_urls": self._media_urls(clean), "result": clean}}
        task = clean.get("task") if isinstance(clean.get("task"), dict) else {{}}
        task_id = str(clean.get("task_id") or task.get("id") or fallback_task_id or "")
        response = clean.get("response", clean)
        if isinstance(response, str):
            try:
                response = json.loads(response)
            except ValueError:
                response = {{}}
        state = ""
        if isinstance(response, dict):
            state = str(response.get("status") or response.get("state") or "").lower()
            if not state and isinstance(response.get("data"), dict):
                state = str(response["data"].get("status") or response["data"].get("state") or "").lower()
        if not state and task:
            state = str(task.get("status") or task.get("state") or "").lower()
        urls = self._media_urls(response)
        if clean.get("success") is False or state in {{"failed", "error", "cancelled", "canceled", "rejected"}}:
            status = "failed"
        elif "finished_at" in clean and clean["finished_at"] is None:
            status = "pending"
        elif state in {{"complete", "completed", "succeeded", "succeed", "success", "finished"}} or (clean.get("finished_at") and response):
            status = "succeeded"
        elif task_id:
            status = "pending"
        else:
            status = "returned"
        return {{"status": status, "task_id": task_id, "media_urls": urls, "result": clean}}

    async def _post(self, path: str, payload: dict, key: str, task_id: str = "", extra_headers: dict | None = None) -> dict:
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(90, connect=10)) as client:
                response = await client.post(
                    "https://api.acedata.cloud" + path,
                    json=payload,
                    headers={{"Authorization": f"Bearer {{key}}", "Accept": "application/json", **(extra_headers or {{}})}},
                )
        except httpx.TransportError:
            raise RuntimeError("Connection failed; check request history before submitting again.") from None
        if response.status_code >= 400:
            raise RuntimeError(f"Ace Data Cloud HTTP {{response.status_code}}; check key, access, balance or request history.")
        try:
            value = response.json()
        except ValueError:
            raise RuntimeError("Ace Data Cloud returned invalid JSON.") from None
        if not isinstance(value, (dict, list)):
            raise RuntimeError("Ace Data Cloud returned an invalid result.")
        return self._result(value, task_id)
'''


def render_action(action: Action) -> str:
    parsed = ast.parse(f"def f({action.signature}): pass").body[0]
    names = [arg.arg for arg in parsed.args.args]
    docs = "\n".join(f"        :param {name}: {PARAM_DOCS.get(name, 'Value supported by the service API.')}" for name in names)
    outcome = "Use retrieve_task with the returned task ID; never repeat this call to poll." if action.async_task else "Returns the API result directly."
    guard = f"        {action.guard}\n" if action.guard else ""
    headers = f", extra_headers={action.headers}" if action.headers else ""
    return (
        f"    async def {action.name}(self, {action.signature}, __user__: dict | None = None) -> dict:\n"
        f"        \"\"\"{action.description} One invocation may be billable. {outcome}\n\n{docs}\n        \"\"\"\n"
        f"{guard}"
        f"        payload = {action.payload}\n"
        f"        return await self._post({action.path!r}, payload, self._key(__user__, billable=True){headers})\n"
    )


def render_service(service: Service) -> str:
    parts = [COMMON.format(title=service.title).rstrip()]
    if service.task_path:
        parts.append(
            "    async def retrieve_task(self, task_id: str, __user__: dict | None = None) -> dict:\n"
            "        \"\"\"Read the status and result of an existing task without submitting a new generation.\n\n"
            "        :param task_id: Task ID returned by the first submission.\n"
            "        \"\"\"\n"
            "        if not task_id.strip(): raise ValueError('Task ID is required.')\n"
            f"        return await self._post({service.task_path!r}, {{'action': 'retrieve', 'id': task_id}}, self._key(__user__, billable=False), task_id)\n"
        )
    parts.extend(render_action(action) for action in service.actions)
    return "\n\n".join(parts).rstrip() + "\n"


def main(check: bool = False) -> int:
    failures = []
    for service in SERVICES:
        path = ROOT / "tools" / f"{service.slug}.py"
        content = render_service(service)
        if check:
            if not path.exists() or path.read_text() != content:
                failures.append(str(path.relative_to(ROOT)))
        else:
            path.write_text(content)
    if failures:
        print("Out-of-date generated tools:", ", ".join(failures))
        return 1
    print(f"{'Checked' if check else 'Generated'} {len(SERVICES)} standalone service Tools.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main("--check" in sys.argv))
