# Development and verification

## Source layout

Open WebUI's native OpenAI-compatible Connection is the default chat-model integration and needs no custom code. The Pipe is an optional personal-key model path. Open WebUI Community imports one Python file per post: <code>functions/acedatacloud_pipe.py</code> is the optional Pipe; each file under <code>tools/</code> is an independent service Tool. One source repository with 17 self-contained Tool files matches that install boundary. Splitting the source into 17 repositories would not change Community imports or user permissions, and would make coordinated security fixes harder. <code>scripts/generate_service_tools.py</code> is the reviewed source for 16 service files; <code>tools/google_search.py</code> is small enough to maintain directly. Regenerate after editing a service action:

~~~bash
python3 scripts/generate_service_tools.py
python3 scripts/generate_service_tools.py --check
python3 scripts/build_community_materials.py --check
python3 -m compileall -q functions tools scripts
python3 -m unittest discover -s tests -v
~~~

The public API payloads were compared with the existing Ace Data Cloud Dify integration's published contract snapshots using:

~~~bash
python3 scripts/audit_dify_contracts.py /path/to/AceDataCloud/.worktrees
~~~

That optional audit needs <code>jsonschema</code> and the 17 local Dify source checkouts. It makes no Ace Data Cloud API calls. On 2026-10-12, 25 exposed primary action payloads passed their service schemas, including Google Search's intercepted HTTP payload; the Nano Banana check uses the v0.0.3 contract when that checkout is present. Fish Audio's selected model is an HTTP header, so the focused unit test checks that detail separately. This audit validates payload shape, not the full Dify action surface or live service behavior; see the [per-service comparison](SERVICES.md#dify-scope-comparison).

The current result tests also cover pending tasks with preview URLs, intermediate errors, completed JSON-string responses with private metadata, terminal failures, and Grok's public first-run model. A pending or failed task exposes no final <code>media_urls</code>. HTTP redirects are rejected as non-success responses; billable calls are never retried automatically.

## Service discovery material, 2026-10-18

Tool frontmatter now uses service-first titles such as **Suno by Ace Data Cloud**, action-specific descriptions and relevant tag hints. Tool versions are **0.1.1**; Pipe remains **0.1.0**. The generation payloads, fixed API host, keys, opt-in switches and task semantics are unchanged. Old acceptance screenshots use earlier names; no current-title Community or host/UI execution is inferred from them.

`scripts/build_community_materials.py` generates five distinct local drafts, ten bilingual service walkthroughs and a catalog of exact Tool SHA-256 hashes. Its `--check` mode detects source/material drift. It makes no API call, website search or publication. The catalog's official listing fields stay null until a real public post/Get URL is verified. Categories/tags are suggestions for the actual form, not a claimed official schema or ranking.

The two Key reference images are byte-preserved, redacted Ace Console screenshots from a pinned SunoDify commit; [_assets/tutorial/key-images-source.json](../_assets/tutorial/key-images-source.json) records provenance. The create dialog says `Dify tutorial`; the Open WebUI guides explicitly instruct an Open WebUI-specific name. Existing Open WebUI screenshot scope and dates remain unchanged.

## Open WebUI v0.12.0 current-source acceptance

On 2026-10-12, the current plugin files at code commit `d209255` were imported into a separate disposable instance of the official **v0.12.0-slim** image. Its build commit was `15818d88fd7bde1b73de33590f50d15d21e8d7c1`; the linux/amd64 registry manifest was `sha256:e244f99ece7e9e2f40ee75a26ae0014a0fd74c2ee404059501a15edef7c3ad93`. The [redacted acceptance record](evidence/openwebui-v0120-20261012.json) distinguishes these checks:

- The administrator imported **17/17 Tools** and the Pipe. Open WebUI generated all **40 action schemas** without exposing `__user__` as a model parameter.
- With Tool creation/import disabled for ordinary users, their create requests returned **401**. Before each Read grant, the intended user’s User Valve schema request returned **401**; afterward it returned **200**, the key input was masked, and **Allow Billable Calls** defaulted off. A second ordinary user without grants still saw no Tools and received **401** on each User Valve schema. The intended user saw all 17 Tools without receiving code creation permission.
- The Pipe’s two models were absent before model Read grants and visible afterward; the ungranted user still saw none. No new Pipe model chat was made.
- Open WebUI’s own native **Verify Connection** against `https://api.acedata.cloud/v1` returned **200** and **108 models**. The intended ordinary user saw `gpt-5.6-luna` only after its separate model Read grant. This proves native discovery and access, not a new paid Ace model chat or browser-chat acceptance.
- A deterministic **localhost model fixture** exercised the authenticated Socket.IO/native chat workflow and called the installed GPT Image `retrieve_task` exactly once in the recorded run, with the user’s billable switch off. The real Ace lookup returned `succeeded`, `success: true`, the existing task `7893131f-77d0-4f93-b779-d192a74dd3e8`, and one media URL; the host emitted a completed chat event. Separately, the same task’s PNG passed an HTTP 200 HEAD check. The model fixture made two local completion requests; **no new Ace model completion, search or media generation was submitted**. This is current-host read-only Tool evidence, not paid-model or new-generation evidence.

All of these are **D0 local acceptance**. Community Get/Import, public search, paid native-model/browser first calls, the other current-host service actions, and new billing checks remain separate gates. The README API-key link now uses the platform’s `opensource / referral / evergreen` attribution convention with `utm_content=openwebui_readme_api_key`; this records a shared distribution source group, not Community installs or historical conversion.

## Open WebUI v0.11.4 earlier local acceptance

The local test used a fresh Open WebUI v0.11.4 container, one admin and one ordinary user. The admin installed the Pipe and 17 Tool files, then granted read access to the two Pipe model IDs and each Tool. The ordinary user saw two Ace models in the model picker and 17 independent Tools in Integrations. Before the read grants, the ordinary user's API model and Tool lists were empty. The native Connection instructions follow [Open WebUI's official OpenAI-compatible guide](https://docs.openwebui.com/getting-started/quick-start/connect-a-provider/starting-with-openai-compatible/) and Ace Data Cloud's existing [Open WebUI customer guide](https://platform.acedata.cloud/documents); the local browser calls below exercised the optional Pipe path. Do not infer a new native Connection live-call proof from this table.

After the 2026-10-12 result-handling revision, a separate disposable v0.11.4 instance accepted all **17 revised Tool files** through its administrator create API and returned all 17 IDs in the Tool list. It also accepted the revised model Function and listed its type as <code>pipe</code>. No Ace Data Cloud key was entered and no generation/search call was made in that import check. The disposable instance was removed. The ordinary-user read grants and browser calls below were on the earlier revision; current-revision installation and current-revision real calls remain distinct evidence.

| Path | Observed result |
| --- | --- |
| Pipe non-streaming chat | <code>gpt-5.6-luna</code> returned <code>OK</code> to a minimal real prompt. |
| Pipe in browser chat | Native tool calls worked with the selected model. |
| Google Search Tool in browser chat | One <code>search</code> call returned the official Open WebUI Tools documentation title and URL. One same-key usage row <code>07363829-bbe1-4f72-aaa0-01c041cb4e52</code> had HTTP 200 and deducted 0.009 Credits under the test account's discount. |
| GPT Image Tool in browser chat | One <code>generate_image</code> call returned task <code>7893131f-77d0-4f93-b779-d192a74dd3e8</code>. |
| GPT Image read-only follow-up | <code>retrieve_task</code> on that same ID returned <code>succeeded</code>, one PNG URL, and a 200 image readback. |
| GPT Image billing | Exactly one matching <code>ApiUsage</code> row, ID <code>8bf937aa-c8cb-48e5-ac75-a9312318af9f</code>, HTTP 200, deducted 0.099 Credits with the test account's discount. |

A browser reload did not keep the Tool enabled for a later chat turn in the tested session. The tutorial instructs the user to open a new chat and explicitly enable the same Tool before read-only retrieval. It does not interpret an accepted task as a completed result.

The existing Dify E2E records provided task IDs for the other 14 async media services. The matching new Open WebUI Tool's <code>retrieve_task</code> successfully read a terminal task and at least one media URL for each without submitting new paid generation. Face Transform has no async task endpoint; its Tool loaded and its payload passed the published schema, but this Open WebUI instance did not make a new Face Transform call. Google Search was tested through the browser. These read-only checks do not prove that every new submit method has been run through this Open WebUI instance.

## Security boundary

Every import is arbitrary Python executed with the Open WebUI server's permissions. The checked-in code imports only <code>httpx</code>, <code>pydantic</code> and Python standard library modules. It has no subprocess use, local file read, arbitrary destination URL, logging of keys, or automatic retry of paid submits. API destinations are fixed under <code>https://api.acedata.cloud</code>. User keys are masked User Valves; database encryption requires the administrator's Open WebUI setting. Billable methods require a separate per-user switch that defaults off. Query methods work with that switch off.

Open WebUI Community highlighting and GitHub availability are not security reviews. Administrators should inspect source before importing and restrict Tool creation or import to trusted users. A user granted Tool read access can invoke it with their own Key but cannot edit its source through that grant.

## Source references

- [Open WebUI Pipe API](https://docs.openwebui.com/features/extensibility/plugin/functions/pipe/)
- [Open WebUI native OpenAI-compatible Connection](https://docs.openwebui.com/getting-started/quick-start/connect-a-provider/starting-with-openai-compatible/)
- [Open WebUI Tool development](https://docs.openwebui.com/features/extensibility/plugin/tools/development/)
- [Open WebUI Community share and import](https://docs.openwebui.com/ecosystem/community/)
- [Open WebUI Valve storage and encryption](https://docs.openwebui.com/features/extensibility/plugin/development/valves/)
- [Ace Data Cloud API documentation](https://platform.acedata.cloud/documents)

## Release build

`python3 scripts/build_release.py --tag v0.1.1 --output-dir /tmp/openwebui-release-v0.1.1` builds separate Python/JSON/ZIP files, a pinned manifest, optional complete bundle and SHA256SUMS without network calls. The release tests discover all 18 forms, exact source bytes, empty Read grants/no credentials, disabled Function imports, deterministic archives and complete checksums. Community publication and current-title browser use remain separate gates.
