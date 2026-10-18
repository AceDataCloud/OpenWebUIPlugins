"""Build deterministic, credential-free Open WebUI import assets from this commit.

Each JSON asset is the array consumed by Open WebUI's Tools/Functions Import
button. It grants no read access, contains no Valve values, and never contacts
an API. The optional Pipe imports disabled. ZIP bundles are convenience assets,
not Community listings or a separate install dependency.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path
import re
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = "https://github.com/AceDataCloud/OpenWebUIPlugins"
DEFAULT_TAG = "v0.1.1"


def metadata(content: str) -> dict[str, str]:
    return dict(re.findall(r"^([a-z_]+): (.+)$", ast.get_docstring(ast.parse(content)) or "", re.M))


def json_bytes(value) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode()


def digest(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def zip_bytes(files: dict[str, bytes]) -> bytes:
    import io
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, content in sorted(files.items()):
            info = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
            info.external_attr = 0o100644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, content)
    return stream.getvalue()


def build_assets(source_commit: str, tag: str = DEFAULT_TAG) -> dict[str, bytes]:
    if not re.fullmatch(r"[0-9a-f]{40}", source_commit):
        raise ValueError("An exact 40-character source commit is required")
    if not re.fullmatch(r"v[0-9]+\.[0-9]+\.[0-9]+(?:-[a-z0-9.-]+)?", tag):
        raise ValueError("Use a semantic release tag, such as v0.1.1")
    download_base = REPOSITORY + "/releases/download/" + tag + "/"
    assets: dict[str, bytes] = {}
    entries = []
    top5 = json.loads((ROOT / "docs/community/catalog.json").read_text())["independent_entries"]
    guides = {entry["id"]: [entry["readme_en"], entry["readme_zh"]] for entry in top5}
    for path in [*sorted((ROOT / "tools").glob("*.py")), ROOT / "functions/acedatacloud_pipe.py"]:
        source = path.read_bytes()
        text = source.decode()
        frontmatter = metadata(text)
        kind = "tool" if path.parent.name == "tools" else "function"
        item_id = "acedatacloud_" + path.stem if kind == "tool" else "acedatacloud_models"
        form = {"id": item_id, "name": frontmatter["title"], "content": text,
                "meta": {"description": frontmatter["description"], "manifest": frontmatter}}
        if kind == "tool":
            form["access_grants"] = []
        import_name = path.stem + "." + kind + ".json"
        import_data = json_bytes([form])
        archive_name = "acedatacloud-" + path.stem.replace("_", "-") + "-openwebui-" + kind + "-" + frontmatter["version"] + ".zip"
        entry_files = {
            path.name: source, import_name: import_data,
            "LICENSE": (ROOT / "LICENSE").read_bytes(),
            "PRIVACY.md": (ROOT / "PRIVACY.md").read_bytes(),
            "INSTALL.md": (
                f"# {frontmatter['title']}\n\n"
                f"Source: {REPOSITORY}/blob/{source_commit}/{path.relative_to(ROOT).as_posix()}\n\n"
                f"Source SHA-256: `{digest(source)}`\n\n"
                f"In Open WebUI, open **{'Workspace → Tools' if kind == 'tool' else 'Admin Panel → Functions'}**, "
                f"choose **Import**, select `{import_name}`, review all Python source, and confirm. "
                "Install only this service; no other Ace Tool or Pipeline is required. "
                "If the ID already exists, update the existing item; do not create duplicate imports.\n\n"
                "Imports contain no API keys, User Valves, user IDs or read grants. Administrators intentionally "
                "grant Read to intended users/models and keep code import restricted. "
                "The optional Pipe imports disabled and must be enabled intentionally. "
                "Each user configures their own application Key in that item's User Valves. "
                "Tool billable switches default off. Never generate a task just to poll.\n\n"
                f"English/Chinese setup: {REPOSITORY}/blob/{source_commit}/README.md\n\n"
                "These are first-party GitHub download assets, not a published Open WebUI Community post.\n"
            ).encode(),
        }
        assets[path.name] = source
        assets[import_name] = import_data
        assets[archive_name] = zip_bytes(entry_files)
        entry = {
            "id": item_id, "service_id": path.stem, "kind": kind,
            "function_type": "pipe" if kind == "function" else None,
            "title": frontmatter["title"], "version": frontmatter["version"],
            "required_open_webui_version": frontmatter["required_open_webui_version"],
            "source_path": path.relative_to(ROOT).as_posix(), "source_sha256": digest(source),
            "source_url": REPOSITORY + "/blob/" + source_commit + "/" + path.relative_to(ROOT).as_posix(),
            "python_asset": {"name": path.name, "url": download_base + path.name, "sha256": digest(source)},
            "import_asset": {"name": import_name, "url": download_base + import_name, "sha256": digest(import_data)},
            "zip_asset": {"name": archive_name, "url": download_base + archive_name, "sha256": digest(assets[archive_name])},
            "guides": [REPOSITORY + "/blob/" + source_commit + "/" + guide for guide in guides.get(path.stem, [])],
            "default_access_grants": [], "contains_credentials": False,
            "auto_enabled": False, "official_community_url": None,
        }
        entries.append(entry)
    if len(entries) != 18 or len({entry["id"] for entry in entries}) != 18:
        raise RuntimeError("Expected exactly 17 independent Tools and one optional Pipe")
    manifest = {
        "schema_version": 1, "repository": REPOSITORY, "release_tag": tag,
        "source_commit": source_commit, "distribution": "first_party_github_release",
        "official_community_publication_verified": False,
        "versions": {"tools": "0.1.1", "optional_pipe": "0.1.0"},
        "count": len(entries), "entries": entries,
        "import_contract": {
            "host_reference": "Open WebUI v0.12.3",
            "tools": "Workspace Tools Import consumes JSON array of ToolForm objects",
            "functions": "Admin Functions Import consumes JSON array of FunctionForm objects",
            "no_credentials_or_grants": True,
            "ui_runtime_verified": False,
        },
    }
    assets["manifest.json"] = json_bytes(manifest)
    full_files = {name: content for name, content in assets.items() if not name.endswith((".zip", ".py"))}
    for entry in entries:
        full_files[entry["source_path"]] = (ROOT / entry["source_path"]).read_bytes()
    for name in ["README.md", "PRIVACY.md", "LICENSE"]:
        full_files[name] = (ROOT / name).read_bytes()
    for directory in ["docs", "readme", "scripts", "_assets"]:
        for path in sorted((ROOT / directory).rglob("*")):
            if path.is_file() and path.suffix in {".png", ".json", ".md", ".py"}:
                full_files[path.relative_to(ROOT).as_posix()] = path.read_bytes()
    assets["acedatacloud-openwebui-" + tag.removeprefix("v") + ".zip"] = zip_bytes(full_files)
    assets["SHA256SUMS"] = "".join(f"{digest(content)}  {name}\n" for name, content in sorted(assets.items())).encode()
    return assets


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--tag", default=DEFAULT_TAG)
    args = parser.parse_args()
    if subprocess.check_output(["git", "status", "--porcelain", "--untracked-files=normal"], cwd=ROOT, text=True).strip():
        raise RuntimeError("Build release assets only from a clean reviewed commit")
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    assets = build_assets(commit, args.tag)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for name, content in assets.items():
        path = args.output_dir / name
        if path.exists() and path.read_bytes() != content:
            raise RuntimeError(f"Refusing to overwrite a different release artifact: {path}")
        path.write_bytes(content)
    print(f"Built {len(assets)} deterministic assets from {commit}; no network, Key, access grant or API request.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
