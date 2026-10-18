# Download and import a released Tool or Function

The source [PR #1](https://github.com/AceDataCloud/OpenWebUIPlugins/pull/1) merged on **2026-10-19**. The first source/download release is **v0.1.1**: it contains 17 Tool files at version **0.1.1** and the optional model Pipe at **0.1.0**. This mixed source release is a first-party GitHub distribution, not a Community listing, official default or recommendation.

## Independent downloads

Use the [release page](https://github.com/AceDataCloud/OpenWebUIPlugins/releases/tag/v0.1.1), `manifest.json` and `SHA256SUMS`. Every service has its own Python file, JSON import and small ZIP. For example, Suno uses `suno.py`, `suno.tool.json`, or `acedatacloud-suno-openwebui-tool-0.1.1.zip`. The optional model Function uses `acedatacloud_pipe.function.json`. The complete ZIP is optional; it is not a requirement to use one Tool.

Before importing, compare the asset's SHA-256 with `SHA256SUMS` and read the complete Python code. Imports run code inside Open WebUI. Nothing in these assets contains a Key, a User Valve value, a user ID or a Read grant.

1. For a **Tool**, open **Workspace → Tools → Create → Import**, select its `*.tool.json`, review, and confirm. This is an array containing one ToolForm object, following the [v0.12.3 import handler](https://github.com/open-webui/open-webui/blob/v0.12.3/src/lib/components/workspace/Tools.svelte). An administrator deliberately grants the intended user or group **Read** after import.
2. For the optional model **Pipe**, open **Admin Panel → Functions → Import**, select `acedatacloud_pipe.function.json`, and review. It imports disabled with no global activation or model Read grants. Enable intentionally, choose public model IDs and grant model Read only to the intended users.
3. If the ID already exists, update that existing item's source. Do not repeatedly import duplicate entries. Each user configures their own application Key in that item's **User Valves**; the model Connection's shared Key does not fill Tool keys. Tool billable switches stay off until the user explicitly enables an intended submit.

The import format was checked against official v0.12.3 frontend handlers and backend forms. This does not claim a new v0.12.3 browser import or current-title paid call. Prior v0.12.0 host/permission and earlier v0.11.4 real browser evidence remain dated in [development notes](DEVELOPMENT.md). Queries use the original task ID and do not generate new work; new paid calls need an intended current charge.

## Publication boundaries

Community posts still need the existing Ace account's manual duplicate check and **Share** workflow. A GitHub release download, a source merge or an import JSON is not proof that searching Suno/Seedance/HappyHorse/GPT Image/Nano Banana in Community finds an Ace entry. Only add exact post/Get URLs after verifying them.

The [manifest builder](../scripts/build_release.py) creates a pinned source commit, exact hashes and deterministic ZIPs:

```bash
python3 scripts/build_release.py --tag v0.1.1 --output-dir /tmp/openwebui-release-v0.1.1
```

Use a clean reviewed commit and a new empty directory. Read back the public assets and their hashes after release publication. This script neither publishes nor sends any network/API request.
