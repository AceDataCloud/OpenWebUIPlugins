"""Compare first-run Tool payloads with the published Dify API schemas.

Run with a checkout directory containing the 17 Ace *Dify repositories:
    python scripts/audit_dify_contracts.py /path/to/AceDataCloud/.worktrees
This read-only audit makes no Ace Data Cloud API calls.
"""

from __future__ import annotations

import ast
import asyncio
import importlib.util
import inspect
import json
from pathlib import Path
import sys
from unittest.mock import patch

import httpx
from jsonschema import Draft202012Validator

from generate_service_tools import ROOT, SERVICES


REPOS = {
    "gpt_image": "GPTImage", "suno": "Suno", "seedance": "Seedance",
    "fish_audio": "FishAudio", "seedream": "Seedream", "happy_horse": "HappyHorse",
    "qwen_image": "QwenImage", "veo": "Veo", "grok": "Grok",
    "face_transform": "Face", "midjourney": "Midjourney", "flux": "Flux",
    "minimax_h3": "MiniMax", "wan": "Wan", "kling": "Kling",
    "nano_banana": "NanoBanana",
}


def contracts(path: Path) -> dict:
    tree = ast.parse(path.read_text())
    return next(
        ast.literal_eval(node.value)
        for node in tree.body
        if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == "ENDPOINTS" for target in node.targets)
    )


async def audit(dify_root: Path) -> int:
    failures = []
    checked = 0
    for service in SERVICES:
        module_path = ROOT / "tools" / f"{service.slug}.py"
        spec = importlib.util.spec_from_file_location("audit_" + service.slug, module_path)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        tool = module.Tools()
        user_valves = tool.UserValves(API_KEY="example-test-key", ALLOW_BILLABLE_CALLS=True)

        async def capture(path, payload, key, task_id="", extra_headers=None):
            return path, payload

        tool._post = capture
        checkout = f"{REPOS[service.slug]}Dify-provider-onboarding"
        if service.slug == "nano_banana" and (dify_root / "NanoBananaDify-marketplace-003/tools/api_contracts.py").exists():
            checkout = "NanoBananaDify-marketplace-003"  # Dify v0.0.3 includes nano-banana-2.1.
        source = dify_root / checkout / "tools/api_contracts.py"
        endpoints = contracts(source)
        for action in service.actions:
            method = getattr(tool, action.name)
            kwargs = {}
            for name, param in inspect.signature(method).parameters.items():
                if name == "__user__":
                    kwargs[name] = {"valves": user_valves}
                elif param.default is inspect.Parameter.empty:
                    kwargs[name] = {
                        "prompt": "a blue cube", "image_url": "https://example.com/a.png",
                        "text": "Hello", "video_id": "video123",
                        "model": "grok-imagine-video-1.5-fast",
                    }.get(name, "example")
            path, payload = await method(**kwargs)
            candidates = [
                (name, endpoint) for name, endpoint in endpoints.items()
                if endpoint.get("path") == path and endpoint.get("operation") not in {"task", "batch"}
            ]
            valid = any(
                not list(Draft202012Validator(endpoint["schema"]).iter_errors(payload))
                for _, endpoint in candidates
            )
            checked += 1
            if not valid:
                first = []
                for name, endpoint in candidates:
                    errors = list(Draft202012Validator(endpoint["schema"]).iter_errors(payload))
                    first.append(f"{name}: {errors[0].message if errors else 'no schema error'}")
                failures.append(f"{service.slug}.{action.name}: {'; '.join(first) or 'no endpoint'}")
    search_spec = importlib.util.spec_from_file_location("audit_google_search", ROOT / "tools/google_search.py")
    assert search_spec and search_spec.loader
    search_module = importlib.util.module_from_spec(search_spec)
    search_spec.loader.exec_module(search_module)
    search_tool = search_module.Tools()
    captured = []

    def search_handler(request: httpx.Request):
        captured.append((request.url.path, json.loads(request.content)))
        return httpx.Response(200, json={"items": []})

    real_client = httpx.AsyncClient
    with patch.object(search_module.httpx, "AsyncClient", side_effect=lambda **kwargs: real_client(transport=httpx.MockTransport(search_handler), **kwargs)):
        await search_tool.search("Open WebUI", __user__={"valves": search_tool.UserValves(API_KEY="example-test-key", ALLOW_BILLABLE_CALLS=True)})
    search_endpoint = contracts(dify_root / "GoogleSearchDify-provider-onboarding/tools/api_contracts.py")["serp_google"]
    checked += 1
    path, payload = captured[0]
    errors = list(Draft202012Validator(search_endpoint["schema"]).iter_errors(payload))
    if path != search_endpoint["path"] or errors:
        failures.append(f"google_search.search: {errors[0].message if errors else 'wrong endpoint'}")
    print(f"Checked {checked} actions against Dify API schemas; failures: {len(failures)}")
    for item in failures:
        print(item)
    return 1 if failures else 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: audit_dify_contracts.py <AceDataCloud .worktrees path>")
    raise SystemExit(asyncio.run(audit(Path(sys.argv[1]))))
