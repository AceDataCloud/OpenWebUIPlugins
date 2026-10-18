from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest
import zipfile
import io


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("release_builder", ROOT / "scripts/build_release.py")
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


class ReleaseTests(unittest.TestCase):
    def test_private_separate_imports_match_reviewed_source_bytes(self):
        assets = module.build_assets("a" * 40)
        manifest = json.loads(assets["manifest.json"])
        self.assertEqual(len(manifest["entries"]), 18)
        self.assertEqual(sum(entry["kind"] == "tool" for entry in manifest["entries"]), 17)
        for entry in manifest["entries"]:
            with self.subTest(entry=entry["id"]):
                form, = json.loads(assets[entry["import_asset"]["name"]])
                self.assertEqual(form["content"].encode(), (ROOT / entry["source_path"]).read_bytes())
                self.assertNotIn("valves", form)
                self.assertNotIn("user_id", form)
                self.assertNotIn("is_active", form)
                self.assertEqual(form.get("access_grants", []), [])
                self.assertIsNone(entry["official_community_url"])
                with zipfile.ZipFile(io.BytesIO(assets[entry["zip_asset"]["name"]])) as archive:
                    self.assertEqual(archive.read(entry["python_asset"]["name"]), form["content"].encode())
                    self.assertEqual(archive.read(entry["import_asset"]["name"]), assets[entry["import_asset"]["name"]])

    def test_deterministic_assets_and_complete_checksums(self):
        first = module.build_assets("b" * 40)
        self.assertEqual(first, module.build_assets("b" * 40))
        sums = dict(line.split("  ", 1)[::-1] for line in first["SHA256SUMS"].decode().splitlines())
        self.assertEqual(set(sums), set(first) - {"SHA256SUMS"})
        for name, checksum in sums.items():
            self.assertEqual(checksum, module.digest(first[name]))
        with zipfile.ZipFile(io.BytesIO(first["acedatacloud-openwebui-0.1.1.zip"])) as archive:
            self.assertEqual(archive.read("tools/suno.py"), (ROOT / "tools/suno.py").read_bytes())
            self.assertEqual(archive.read("functions/acedatacloud_pipe.py"), (ROOT / "functions/acedatacloud_pipe.py").read_bytes())
            self.assertIn("readme/services/suno.md", archive.namelist())
            self.assertIn("_assets/tutorial/get-api-key-en.png", archive.namelist())

    def test_rejects_unpinned_source_or_unsafe_tag(self):
        with self.assertRaises(ValueError):
            module.build_assets("main")
        with self.assertRaises(ValueError):
            module.build_assets("b" * 40, "../../bad")
