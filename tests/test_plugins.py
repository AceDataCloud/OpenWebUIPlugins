from __future__ import annotations

import importlib.util
import inspect
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

import httpx


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from generate_service_tools import SERVICES  # noqa: E402


def load(path: Path):
    spec = importlib.util.spec_from_file_location("test_" + path.stem, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ToolSafetyTests(unittest.IsolatedAsyncioTestCase):
    async def test_all_billable_actions_require_user_opt_in(self):
        required = {
            "prompt": "A blue cube",
            "text": "Hello",
            "image_url": "https://example.com/input.png",
            "video_id": "video123",
            "model": "grok-imagine-video",
        }
        for service in SERVICES:
            module = load(ROOT / "tools" / f"{service.slug}.py")
            tool = module.Tools()
            user = {"valves": tool.UserValves(API_KEY="test-key")}
            for action in service.actions:
                with self.subTest(service=service.slug, action=action.name):
                    kwargs = {
                        name: required.get(name, "example")
                        for name, parameter in inspect.signature(getattr(tool, action.name)).parameters.items()
                        if name != "__user__" and parameter.default is inspect.Parameter.empty
                    }
                    kwargs["__user__"] = user
                    with self.assertRaisesRegex(ValueError, "Allow Billable Calls"):
                        await getattr(tool, action.name)(**kwargs)

    async def test_google_search_is_opt_in(self):
        module = load(ROOT / "tools" / "google_search.py")
        tool = module.Tools()
        with self.assertRaisesRegex(ValueError, "Allow Billable Calls"):
            await tool.search("Open WebUI", __user__={"valves": tool.UserValves(API_KEY="test-key")})

    async def test_task_lookup_works_with_billable_switch_off(self):
        module = load(ROOT / "tools" / "gpt_image.py")
        tool = module.Tools()
        captured = []

        async def fake_post(path, payload, key, task_id="", extra_headers=None):
            captured.append((path, payload, task_id))
            return {"status": "pending", "task_id": task_id}

        tool._post = fake_post
        result = await tool.retrieve_task(
            "task123",
            __user__={"valves": tool.UserValves(API_KEY="test-key")},
        )
        self.assertEqual(result["status"], "pending")
        self.assertEqual(captured, [("/openai/tasks", {"action": "retrieve", "id": "task123"}, "task123")])

    async def test_fish_model_is_sent_as_header(self):
        module = load(ROOT / "tools" / "fish_audio.py")
        tool = module.Tools()
        captured = []

        async def fake_post(path, payload, key, task_id="", extra_headers=None):
            captured.append((path, payload, extra_headers))
            return {"status": "pending"}

        tool._post = fake_post
        await tool.text_to_speech(
            "Hello",
            model="s2-pro",
            __user__={"valves": tool.UserValves(API_KEY="test-key", ALLOW_BILLABLE_CALLS=True)},
        )
        self.assertEqual(captured[0][0], "/fish/tts")
        self.assertEqual(captured[0][2], {"model": "s2-pro"})
        self.assertNotIn("model", captured[0][1])

    async def test_nested_terminal_task_and_sensitive_fields(self):
        module = load(ROOT / "tools" / "minimax_h3.py")
        tool = module.Tools()
        result = tool._result({
            "task": {
                "id": "task123",
                "status": "succeeded",
                "content": {"video_url": "https://example.com/output.mp4"},
                "supplier": "private",
            },
            "authorization": "secret",
        })
        self.assertEqual(result["status"], "succeeded")
        self.assertEqual(result["task_id"], "task123")
        self.assertEqual(result["media_urls"], ["https://example.com/output.mp4"])
        self.assertNotIn("authorization", result["result"])
        self.assertNotIn("supplier", result["result"]["task"])


class PipeTests(unittest.IsolatedAsyncioTestCase):
    async def test_model_key_and_allowlist(self):
        module = load(ROOT / "functions" / "acedatacloud_pipe.py")
        pipe = module.Pipe()
        self.assertEqual([m["id"] for m in pipe.pipes()], ["gpt-5.6-luna", "deepseek-v4-flash"])
        with self.assertRaisesRegex(ValueError, "application API key"):
            await pipe.pipe({"model": "acedatacloud_models.gpt-5.6-luna", "messages": [{"role": "user", "content": "Hi"}]})
        with self.assertRaisesRegex(ValueError, "not configured"):
            await pipe.pipe(
                {"model": "acedatacloud_models.unlisted", "messages": [{"role": "user", "content": "Hi"}]},
                __user__={"valves": pipe.UserValves(API_KEY="test-key")},
            )

    async def test_proxy_uses_fixed_host_and_scrubs_non_api_fields(self):
        module = load(ROOT / "functions" / "acedatacloud_pipe.py")
        seen = []
        def handler(request: httpx.Request):
            seen.append((str(request.url), request.content))
            return httpx.Response(200, json={
                "object": "chat.completion",
                "choices": [{"message": {"role": "assistant", "content": "OK"}}],
            })
        real_client = httpx.AsyncClient
        transport = httpx.MockTransport(handler)
        with patch.object(module.httpx, "AsyncClient", side_effect=lambda **kwargs: real_client(transport=transport, **kwargs)):
            result = await module.Pipe().pipe(
                {
                    "model": "acedatacloud_models.gpt-5.6-luna",
                    "messages": [{"role": "user", "content": "Hi"}],
                    "stream": False,
                    "private_metadata": "do-not-send",
                },
                __user__={"valves": module.Pipe.UserValves(API_KEY="test-key")},
            )
        self.assertEqual(result["choices"][0]["message"]["content"], "OK")
        self.assertEqual(seen[0][0], "https://api.acedata.cloud/v1/chat/completions")
        self.assertNotIn(b"private_metadata", seen[0][1])

    async def test_http_error_does_not_echo_key(self):
        module = load(ROOT / "functions" / "acedatacloud_pipe.py")
        real_client = httpx.AsyncClient
        transport = httpx.MockTransport(lambda request: httpx.Response(401, json={"error": "secret"}))
        with patch.object(module.httpx, "AsyncClient", side_effect=lambda **kwargs: real_client(transport=transport, **kwargs)):
            with self.assertRaises(RuntimeError) as raised:
                await module.Pipe().pipe(
                    {
                        "model": "acedatacloud_models.gpt-5.6-luna",
                        "messages": [{"role": "user", "content": "Hi"}],
                        "stream": False,
                    },
                    __user__={"valves": module.Pipe.UserValves(API_KEY="test-key")},
                )
        self.assertIn("HTTP 401", str(raised.exception))
        self.assertNotIn("test-key", str(raised.exception))


if __name__ == "__main__":
    unittest.main()
