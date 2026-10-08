# Development and verification

## Source layout

Open WebUI Community imports one Python file per post. <code>functions/acedatacloud_pipe.py</code> is the model Pipe; each file under <code>tools/</code> is an independent Tool. <code>scripts/generate_service_tools.py</code> is the reviewed source for 16 service files; <code>tools/google_search.py</code> is small enough to maintain directly. Regenerate after editing a service action:

~~~bash
python3 scripts/generate_service_tools.py
python3 scripts/generate_service_tools.py --check
python3 -m compileall -q functions tools scripts
python3 -m unittest discover -s tests -v
~~~

The public API payloads were compared with the existing Ace Data Cloud Dify integration's published contract snapshots using:

~~~bash
python3 scripts/audit_dify_contracts.py /path/to/AceDataCloud/.worktrees
~~~

That optional audit needs <code>jsonschema</code> and the 16 local Dify source checkouts. It makes no API calls. On 2026-10-09, 24 exposed action payloads passed their service schemas. Fish Audio's selected model is an HTTP header, so the focused unit test checks that detail separately.

## Open WebUI v0.11.4 local acceptance

The local test used a fresh Open WebUI v0.11.4 container, one admin and one ordinary user. The admin installed the Pipe and 17 Tool files, then granted read access to the two Pipe model IDs and each Tool. The ordinary user saw two Ace models in the model picker and 17 independent Tools in Integrations. Before the read grants, the ordinary user's API model and Tool lists were empty.

| Path | Observed result |
| --- | --- |
| Pipe non-streaming chat | <code>gpt-5.6-luna</code> returned <code>OK</code> to a minimal real prompt. |
| Pipe in browser chat | Native tool calls worked with the selected model. |
| Google Search Tool in browser chat | One <code>search</code> call returned the official Open WebUI Tools documentation title and URL. |
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
- [Open WebUI Tool development](https://docs.openwebui.com/features/extensibility/plugin/tools/development/)
- [Open WebUI Community share and import](https://docs.openwebui.com/ecosystem/community/)
- [Open WebUI Valve storage and encryption](https://docs.openwebui.com/features/extensibility/plugin/development/valves/)
- [Ace Data Cloud API documentation](https://platform.acedata.cloud/documents)
