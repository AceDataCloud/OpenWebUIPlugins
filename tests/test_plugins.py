from __future__ import annotations

import importlib.util
import inspect
import json
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

    async def test_unfinished_task_hides_preview_and_intermediate_error(self):
        module = load(ROOT / "tools" / "gpt_image.py")
        result = module.Tools()._result({
            "finished_at": None,
            "response": {"status": "running", "success": False, "error": "private", "data": {"image_url": "https://example.com/preview.png"}},
        }, "same-task")
        self.assertEqual(result["status"], "pending")
        self.assertFalse(result["success"])
        self.assertEqual(result["media_urls"], [])
        self.assertNotIn("private", json.dumps(result))

    async def test_string_response_is_parsed_before_redaction(self):
        module = load(ROOT / "tools" / "gpt_image.py")
        result = module.Tools()._result({
            "finished_at": "2026-10-12T00:00:00Z",
            "response": json.dumps({
                "status": "succeeded",
                "data": {"image_url": "https://example.com/final.png", "supplier_name": "private", "authorization": "private"},
            }),
        }, "same-task")
        self.assertEqual(result["status"], "succeeded")
        self.assertTrue(result["success"])
        self.assertEqual(result["media_urls"], ["https://example.com/final.png"])
        self.assertNotIn("private", json.dumps(result))

    async def test_terminal_failure_never_returns_media_url(self):
        module = load(ROOT / "tools" / "gpt_image.py")
        result = module.Tools()._result({
            "finished_at": "2026-10-12T00:00:00Z",
            "response": {"status": "failed", "error": "private", "data": {"image_url": "https://example.com/preview.png"}},
        }, "same-task")
        self.assertEqual(result["status"], "failed")
        self.assertFalse(result["success"])
        self.assertEqual(result["media_urls"], [])
        self.assertNotIn("private", json.dumps(result))

    async def test_mixed_completed_and_running_items_stay_pending(self):
        module = load(ROOT / "tools" / "suno.py")
        result = module.Tools()._result({
            "response": {"data": [
                {"status": "succeeded", "audio_url": "https://example.com/first.mp3"},
                {"status": "running", "audio_url": "https://example.com/preview.mp3"},
            ]},
        }, "same-task")
        self.assertEqual(result["status"], "pending")
        self.assertFalse(result["success"])
        self.assertEqual(result["media_urls"], [])

    async def test_grok_video_default_matches_published_dify_contract(self):
        module = load(ROOT / "tools" / "grok.py")
        tool = module.Tools()
        captured = []

        async def fake_post(path, payload, key, task_id="", extra_headers=None):
            captured.append((path, payload))
            return {"status": "pending", "task_id": "test-task"}

        tool._post = fake_post
        await tool.generate_video("A quiet landscape", __user__={"valves": tool.UserValves(API_KEY="test-key", ALLOW_BILLABLE_CALLS=True)})
        self.assertEqual(captured, [("/grok/videos", {"prompt": "A quiet landscape", "model": "grok-imagine-video-1.5-fast:reverse", "duration": 6, "resolution": "480p", "async": True})])

    async def test_google_search_scrubs_private_metadata(self):
        module = load(ROOT / "tools" / "google_search.py")
        result = module.Tools()._clean({"items": [{"title": "Public", "supplier_name": "private"}], "error": "private"})
        self.assertEqual(result["items"], [{"title": "Public"}])
        self.assertNotIn("private", json.dumps(result))

    async def test_tool_rejects_redirect_without_leaking_response(self):
        module = load(ROOT / "tools" / "gpt_image.py")
        real_client = httpx.AsyncClient
        transport = httpx.MockTransport(lambda request: httpx.Response(302, text="private", headers={"Location": "https://example.com"}))
        with patch.object(module.httpx, "AsyncClient", side_effect=lambda **kwargs: real_client(transport=transport, **kwargs)):
            with self.assertRaisesRegex(RuntimeError, "HTTP 302") as raised:
                await module.Tools().retrieve_task("same-task", __user__={"valves": module.Tools.UserValves(API_KEY="test-key")})
        self.assertNotIn("private", str(raised.exception))


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

    async def test_pipe_rejects_redirect(self):
        module = load(ROOT / "functions" / "acedatacloud_pipe.py")
        real_client = httpx.AsyncClient
        transport = httpx.MockTransport(lambda request: httpx.Response(302, text="private"))
        with patch.object(module.httpx, "AsyncClient", side_effect=lambda **kwargs: real_client(transport=transport, **kwargs)):
            with self.assertRaisesRegex(RuntimeError, "HTTP 302") as raised:
                await module.Pipe().pipe({"model": "acedatacloud_models.gpt-5.6-luna", "messages": [{"role": "user", "content": "Hi"}]}, __user__={"valves": module.Pipe.UserValves(API_KEY="test-key")})
        self.assertNotIn("private", str(raised.exception))


if __name__ == "__main__":
    unittest.main()
