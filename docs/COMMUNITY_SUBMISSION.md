# Open WebUI Community submission pack

**Top 5 service-first release materials (2026-10-18):** [Suno](community/suno.md), [Seedance](community/seedance.md), [Happy Horse](community/happy_horse.md), [GPT Image](community/gpt_image.md), and [Nano Banana](community/nano_banana.md) each have a separate Tool title, description, relevant search terms/tags/category proposal, exact source hash, bilingual onboarding and publication ledger in the [catalog](community/catalog.json). They install independently; no bundle install is required. Current Tool source version is **0.1.1**, the optional model Pipe remains **0.1.0**. There are no verified official post URLs yet.

Use the service name first, followed by **by Ace Data Cloud**, and explain the publisher relationship. Use Ace's own publisher icon if a field is offered; do not copy a third-party mark or imply creator endorsement. Only enter categories and tags accepted by the real form. A `tags` source hint is not evidence that Community indexed it. Do not add unrelated keywords, promise ranking, or submit another copy of an existing Ace entry.

Tools are the primary type for these five model-callable media actions. A Pipe is reserved for a model/provider in the model picker; the optional Ace personal-model-Key Function is not a replacement for the five independently searchable Tool entries. A separate Pipelines deployment would add an installation requirement without improving these one-file Tool imports.

The [Open WebUI Community guide](https://docs.openwebui.com/ecosystem/community/) uses the **Share** menu inside a running Open WebUI instance. A Function is shared from **Admin Panel → Functions** by an administrator; a Tool is shared from **Workspace → Tools**. The website needs a separate openwebui.com account. The share opens a prefilled post in a new tab, and publication only happens when the signed-in account finishes the post.

Ace Data Cloud chat models already work through Open WebUI's native OpenAI-compatible Connection. The Pipe is an **optional** Community Function for users who need a personal model key. Each service remains one separately importable Tool file and one distinct Community post. Keeping the source files in one GitHub repository does not combine the installs. The [service comparison](SERVICES.md#dify-scope-comparison) records where these first-run Tools cover fewer actions than the corresponding Dify plugins; do not describe them as full Dify feature parity.

[Open WebUI's site terms](https://openwebui.com/terms) prohibit automated agents or scripts from generating searches, requests or queries to its website, and prohibit spam or duplicative promotions. Publish interactively through the official UI. Review every post's full source, title, scope and links before submitting. These are separate service implementations with distinct actions; do not post duplicate generic advertisements.

## Before the first post

1. Merge the reviewed [source PR](https://github.com/AceDataCloud/OpenWebUIPlugins/pull/1) when the Ace repository reviewer authorizes it. Confirm the main branch contains the exact files.
2. Use an Ace Data Cloud-controlled openwebui.com account. Import the main-branch Pipe and the desired Tools into an administrator-owned Open WebUI instance, then compare their source against the merged commit. Do not put an API key in any source or Community text.
3. Browse the official Community library manually for existing Ace Data Cloud entries before each post. Use the matching existing entry if one exists.
4. For each item, click **Share** on that installed Function or Tool. Confirm the post type, title, source and links; then publish once. If the form offers a logo/image field, use Ace Data Cloud's existing canonical brand asset and verify the rendered crop. Record the public post URL and commit SHA. Community listings are user-contributed and are not code-security endorsements.

## Distinct post drafts

Use these as short descriptions. After the source PR is merged, link posts to the public [English first-run guide](https://github.com/AceDataCloud/OpenWebUIPlugins/blob/main/README.md), [中文教程](https://github.com/AceDataCloud/OpenWebUIPlugins/blob/main/readme/README_zh_Hans.md), [service permissions](https://github.com/AceDataCloud/OpenWebUIPlugins/blob/main/docs/SERVICES.md), and [privacy](https://github.com/AceDataCloud/OpenWebUIPlugins/blob/main/PRIVACY.md). Verify those absolute links before publishing; relative links from this repository do not resolve inside a Community post. Do not claim Marketplace review, default inclusion or featured status.

| Type | Title | Distinct user-facing description | Source |
| --- | --- | --- | --- |
| Optional Pipe | Ace Data Cloud Models | Add administrator-selected Ace Data Cloud chat models with each user's personal application key. Use the native OpenAI-compatible Connection for a shared administrator key. | [Pipe](../functions/acedatacloud_pipe.py) |
| Tool | GPT Image by Ace Data Cloud | Generate or edit one image, then query the same task ID for the completed image URL. | [GPT Image](../tools/gpt_image.py) |
| Tool | Suno by Ace Data Cloud | Generate music or lyrics and retrieve the same music task without resubmitting. | [Suno](../tools/suno.py) |
| Tool | Seedance by Ace Data Cloud | Submit a short text-to-video task and retrieve its video result by task ID. | [Seedance](../tools/seedance.py) |
| Tool | Fish Audio by Ace Data Cloud | Convert text to speech with a selected public voice model, then retrieve the audio task. | [Fish Audio](../tools/fish_audio.py) |
| Tool | Seedream by Ace Data Cloud | Generate or edit an image with Seedream and query the completed task. | [Seedream](../tools/seedream.py) |
| Tool | Happy Horse by Ace Data Cloud | Generate a short Happy Horse video and read the task's final media URL. | [Happy Horse](../tools/happy_horse.py) |
| Tool | Qwen Image by Ace Data Cloud | Generate one Qwen Image picture and retrieve the result by task ID. | [Qwen Image](../tools/qwen_image.py) |
| Tool | Veo by Ace Data Cloud | Generate or extend a Veo video and query its asynchronous task. | [Veo](../tools/veo.py) |
| Tool | Google Search by Ace Data Cloud | Search web, images, news, maps, places or videos in one explicit API call. | [Google Search](../tools/google_search.py) |
| Tool | Grok by Ace Data Cloud | Ask a Grok chat model or generate a Grok video; video starts with the public 1.5 fast reverse model and supports task lookup. | [Grok](../tools/grok.py) |
| Tool | Face Transform by Ace Data Cloud | Analyze face landmarks or beautify an image the user is allowed to process. | [Face Transform](../tools/face_transform.py) |
| Tool | Midjourney by Ace Data Cloud | Generate a Midjourney image and query its final task result. | [Midjourney](../tools/midjourney.py) |
| Tool | Flux by Ace Data Cloud | Generate or edit a Flux image, then retrieve the same task's output. | [Flux](../tools/flux.py) |
| Tool | MiniMax H3 by Ace Data Cloud | Submit a MiniMax H3 text-to-video task and retrieve its result. | [MiniMax H3](../tools/minimax_h3.py) |
| Tool | Wan by Ace Data Cloud | Generate a Wan text-to-video task and retrieve the completed video. | [Wan](../tools/wan.py) |
| Tool | Kling by Ace Data Cloud | Generate a Kling text-to-video task and query its result by task ID. | [Kling](../tools/kling.py) |
| Tool | Nano Banana by Ace Data Cloud | Generate or edit one Nano Banana image and retrieve the completed task; the user can explicitly choose nano-banana-2.1. | [Nano Banana](../tools/nano_banana.py) |

Each Tool has a masked per-user API key field and a separate **Allow Billable Calls** switch that defaults off. The Pipe's personal key is configured under **Chat Controls → Valves → Functions**. Posting the source does not grant credentials, service access or model read access.

## Record acceptance item by item

For each post, record: public URL, owner identity, source commit/version, visible search result, **Get** import into a separate ordinary user's instance, administrator read grants, personal key configuration, model/Tool selection, one real action, terminal task and openable output where applicable, and matching Credits usage. A published post without normal-user import is not enough for directory acceptance. An accepted task without a terminal result is not a completed service call. Keep default-inclusion and featured/recommended status separate from Community publication.
