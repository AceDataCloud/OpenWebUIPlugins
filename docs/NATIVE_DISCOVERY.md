# Native model discovery and independent Community services

Checked against official Open WebUI sources on **2026-10-18**. Source/publication, official discovery, installation and actual use are separate stages.

## A. Ace in the native model connection workflow

The current [connection dialog](https://github.com/open-webui/open-webui/blob/079fb19e75f8be4b44fada0c755cf383b21a625b/src/lib/components/AddConnectionModal.svelte) offers common endpoint suggestions for OpenAI, Anthropic, Mistral, Groq, OpenRouter and xAI. Ace Data Cloud is absent. Its separate **Advanced → Provider** selector chooses protocol/management behavior (Default, Azure, llama.cpp, LM Studio, LiteLLM); it is not a general brand catalog. Adding an arbitrary Ace value there without backend behavior would misrepresent the contract.

The smallest native discovery proposal is to add a labelled **Ace Data Cloud** endpoint suggestion using `https://api.acedata.cloud/v1` beside OpenRouter. The administrator selects it, fills an application Key, verifies discovery and grants model Read. This would reduce endpoint memorization; it would not create an enabled/default connection, approve every model feature, or make the optional Pipe native. A complete named provider picker is a larger upstream design decision.

Open WebUI's [contribution policy](https://docs.openwebui.com/contributing/#submit-code) says: **“We accept code PRs only when we have explicitly requested them, or when the changes are limited to i18n/localization.”** The [PR template](https://github.com/open-webui/open-webui/blob/079fb19e75f8be4b44fada0c755cf383b21a625b/.github/pull_request_template.md) requires a maintainer-request link, a `dev` target and agreement to its CLA. There is no maintainer request for an Ace code change, and this task does not authorize accepting legal terms. Therefore no unsolicited upstream code PR or CLA acceptance has been performed.

An exact-current-`dev` one-line patch and evidence-backed proposal are prepared in the independent tracking handoff. They are not installed, submitted or shipped. The next external step is an account holder's scoped proposal through the project's permitted Discussion process, then a maintainer invitation and authorized CLA decision before a code PR. Do not reopen the declined [tutorial PR #1453](https://github.com/open-webui/docs/pull/1453) as a substitute or claim that this source repository delivers native/default status.

## B. Services discoverable by their own names

The [official Community guide](https://docs.openwebui.com/ecosystem/community/) explicitly supports keyword discovery, separate Tool/Function posts, **Get → Import**, and **Share** from a running instance. The [plugin guide](https://docs.openwebui.com/features/extensibility/community/) recommends searching by what users want to do. Its examples include multi-plugin repositories, so an independent install/post is not tied to a separate Git repository. The [Tool format](https://docs.openwebui.com/features/extensibility/plugin/tools/development/) is one self-contained Python file; title and description auto-fill the editor.

| User intent | Entry type and proposed title | Why |
| --- | --- | --- |
| Music and lyrics | **Tool — Suno by Ace Data Cloud** | Model can select music/lyrics actions and retrieve the same task. |
| Seedance video | **Tool — Seedance by Ace Data Cloud** | One video service, one install, explicit submit/query boundary. |
| HappyHorse video | **Tool — Happy Horse by Ace Data Cloud** | Service-name title plus relevant HappyHorse spelling in description/tags. |
| Generate/edit images | **Tool — GPT Image by Ace Data Cloud** | Image actions and one task lookup remain a separate install. |
| Nano Banana images | **Tool — Nano Banana by Ace Data Cloud** | Independent image generation/editing entry. |
| Personal model Key | **Pipe Function — Ace Data Cloud Models** | Appears in model picker; optional, admin import, separate personal Key. |

The five Tools avoid a second Pipelines server and do not need the other service files. Generic HTTP MCP/OpenAPI connections remain optional for deployments already using those interfaces; they do not replace the five discoverable entries.

**No Community listing is claimed.** Titles/descriptions, suggested tags/categories, source hashes and bilingual steps are ready in [the five-entry catalog](community/catalog.json). `tags` frontmatter is a hint only; the live website form and published search results must verify accepted taxonomy and indexing. Each title declares the Ace publisher and each draft disclaims creator endorsement. Use only relevant service terms and Ace's publisher mark; do not manufacture ranking, downloads, accounts or duplicate entries.

## One source, independent installs

Keep `AceDataCloud/OpenWebUIPlugins` as the source for the 17 separate Tool files. Each of the Top 5 has its own title, actions, guide, draft and future official post. A new `SunoOpenWebUI`-style mirror repository would not change the official one-file Get/import mechanism; at this stage it would duplicate release/security maintenance without an extra install surface. Re-evaluate if the platform later requires per-repository manifests, artifacts or ownership. This decision does not reject independent branded distribution: the independent unit is the actual Community Tool/post.

## Before publication

Finish source review/merge; compare exact file hashes. The existing Ace Community account holder must manually check for entries, publish/update each distinct service once through **Workspace → Tools → Share**, record public URLs and code versions, then verify search and installation in a separate instance. Functions use **Admin Panel → Functions → Share**. Any website legal acceptance remains with the authorized account holder. No automatic website search, bulk post, paid request or promotional or review-chasing message is performed by the material builder.
