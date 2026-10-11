# Service Tools and restricted-key permissions

Each link is one self-contained Python Tool file. Import only the services your users need. The administrator grants Tool read access separately from the user's personal Ace Data Cloud API key. Every billable method requires that user's **Allow Billable Calls** switch to be on; it defaults off.

| Service Tool | Exposed actions | First-run choice | Allowed APIs for a restricted key |
| --- | --- | --- | --- |
| [GPT Image](../tools/gpt_image.py) | <code>generate_image</code>, <code>edit_image</code>, <code>retrieve_task</code> | <code>gpt-image-2</code>, 1024x1024, low, one image | <code>/openai/images/generations</code>, <code>/openai/images/edits</code> if editing, <code>/openai/tasks</code> |
| [Suno](../tools/suno.py) | <code>generate_music</code>, <code>generate_lyrics</code>, <code>retrieve_task</code> | <code>chirp-v6</code>, instrumental | <code>/suno/audios</code>, <code>/suno/lyrics</code> if used, <code>/suno/tasks</code> |
| [Seedance](../tools/seedance.py) | <code>generate_video</code>, <code>retrieve_task</code> | <code>doubao-seedance-2-0-mini-260615</code>, 4 s, 480p | <code>/seedance/videos</code>, <code>/seedance/tasks</code> |
| [Fish Audio](../tools/fish_audio.py) | <code>text_to_speech</code>, <code>retrieve_task</code> | <code>s2-pro</code>, mp3; model is an API header | <code>/fish/tts</code>, <code>/fish/tasks</code> |
| [Seedream](../tools/seedream.py) | <code>generate_image</code>, <code>edit_image</code>, <code>retrieve_task</code> | <code>doubao-seedream-5-0-lite-260128</code>, 2K | <code>/seedream/images</code>, <code>/seedream/tasks</code> |
| [Happy Horse](../tools/happy_horse.py) | <code>generate_video</code>, <code>retrieve_task</code> | <code>happyhorse-1.1-t2v</code>, 3 s, 720P | <code>/happyhorse/videos</code>, <code>/happyhorse/tasks</code> |
| [Qwen Image](../tools/qwen_image.py) | <code>generate_image</code>, <code>retrieve_task</code> | <code>qwen-image-3.0</code>, 1024*1024 | <code>/qwen-image/images</code>, <code>/qwen-image/tasks</code> |
| [Veo](../tools/veo.py) | <code>generate_video</code>, <code>extend_video</code>, <code>retrieve_task</code> | <code>veo31-fast</code>, text to video | <code>/veo/videos</code>, <code>/veo/extend</code> if used, <code>/veo/tasks</code> |
| [Google Search](../tools/google_search.py) | <code>search</code> | Web search, 3 results, page 1 | <code>/serp/google</code> |
| [Grok](../tools/grok.py) | <code>ask_grok</code>, <code>generate_video</code>, <code>retrieve_task</code> | <code>grok-4</code> chat; video: <code>grok-imagine-video-1.5-fast:reverse</code>, 6 s, 480p | <code>/grok/chat/completions</code>, <code>/grok/videos</code> if used, <code>/grok/tasks</code> |
| [Face Transform](../tools/face_transform.py) | <code>analyze_face</code>, <code>beautify_face</code> | Public HTTPS image URL you may process | <code>/face/analyze</code>, <code>/face/beautify</code> if used |
| [Midjourney](../tools/midjourney.py) | <code>imagine</code>, <code>retrieve_task</code> | Version 8.2, fast | <code>/midjourney/imagine</code>, <code>/midjourney/tasks</code> |
| [Flux](../tools/flux.py) | <code>generate_image</code>, <code>edit_image</code>, <code>retrieve_task</code> | <code>flux-dev</code>, 1024x1024 | <code>/flux/images</code>, <code>/flux/tasks</code> |
| [MiniMax H3](../tools/minimax_h3.py) | <code>generate_video</code>, <code>retrieve_task</code> | H3, 4 s, 768P | <code>/minimax/videos</code>, <code>/minimax/tasks</code> |
| [Wan](../tools/wan.py) | <code>generate_video</code>, <code>retrieve_task</code> | <code>wan2.6-t2v</code>, 5 s, 720P | <code>/wan/videos</code>, <code>/wan/tasks</code> |
| [Kling](../tools/kling.py) | <code>generate_video</code>, <code>retrieve_task</code> | <code>kling-v3-turbo</code>, 5 s, standard | <code>/kling/videos</code>, <code>/kling/tasks</code> |
| [Nano Banana](../tools/nano_banana.py) | <code>generate_image</code>, <code>edit_image</code>, <code>retrieve_task</code> | <code>nano-banana-2-lite</code>, 1K, one image | <code>/nano-banana/images</code>, <code>/nano-banana/tasks</code> |

The recommended model setup is Open WebUI's native OpenAI-compatible Connection, with base URL <code>https://api.acedata.cloud/v1</code>; a restricted key needs <code>/v1/models</code> and <code>/v1/chat/completions</code>. The optional [model Pipe](../functions/acedatacloud_pipe.py) is for a personal key per user. It needs only <code>/v1/chat/completions</code>; its administrator selects displayed model IDs, and each user fills the Pipe's own key under **Chat Controls → Valves → Functions**. The Connection key and each Tool's User Valve key are separate.

## Dify scope comparison

The 17 service names match Ace Data Cloud's 17 formal Dify Tool submissions. **The action surface is narrower.** Open WebUI Community installs one Tool file at a time, so this repository keeps one self-contained file and one future Community post per service. A separate GitHub repository per file would add release overhead without changing installation or permissions. As of 2026-10-12, the Dify provider manifests expose 97 action entries across these services, including batch queries, listing and advanced or destructive actions. These Open WebUI files expose 24 billable primary methods, 15 read-only task lookups and the Google Search method. Dify's larger action count does not mean that all advanced actions are safe first-run defaults here.

| Service | Dify action entries | Additional Dify capabilities not exposed by this Open WebUI Tool |
| --- | ---: | --- |
| GPT Image | 5 | Task list and batch retrieval. |
| Suno | 19 | Reference upload, format downloads, vocals/personas, projects, custom models and batch retrieval. |
| Seedance | 3 | Batch retrieval; richer generation inputs are outside this first-run method. |
| Fish Audio | 7 | Voice search, voice/model creation and batch retrieval. |
| Seedream | 5 | Layer decomposition and batch retrieval. |
| Happy Horse | 3 | Batch retrieval; image-to-video and editing modes are outside this first-run method. |
| Qwen Image | 3 | Batch retrieval. |
| Veo | 7 | Object editing, reshoot, upscale and batch retrieval. |
| Google Search | 1 | The single Dify search action is represented by <code>search</code>. |
| Grok | 4 | Batch retrieval; chat parameters and video reference inputs are narrower. |
| Face Transform | 1 | Dify's single action selects from more face operations; this Tool exposes only analysis and beautification. |
| Midjourney | 9 | Edit, describe, translate, video, seed, shorten and batch retrieval. |
| Flux | 5 | Video generation and batch retrieval. |
| MiniMax H3 | 5 | Task listing, deletion and batch retrieval. |
| Wan | 4 | Wan 3 generation and batch retrieval. |
| Kling | 12 | Motion, lip sync, talking photo, commerce, apparel, voices, elements and batch retrieval. |
| Nano Banana | 4 | Batch retrieval. Dify v0.0.3 also accepts <code>nano-banana-2.1</code> for generation and editing; select it explicitly here after checking access and pricing. The lower-cost <code>nano-banana-2-lite</code> remains the default. |

The counts come from the Dify provider manifests; a Dify action can itself support several modes. They document a scope gap, not a claim that Open WebUI cannot support those modes. Add an action only after verifying its current public API contract, cost, and one real outcome. For chat, use the native Connection instead of adding a second Tool for every model.

## Task handling

A generation method submits one request. If it returns <code>task_id</code>, its result is still pending until <code>retrieve_task</code> reports a terminal status. Query the **same ID** with the same service Tool. A query is read-only and works with **Allow Billable Calls** off. A returned URL should be opened and checked; an accepted task or green Open WebUI chat message alone is not proof of a finished media result.

If a service returns a synchronous result, the Tool uses <code>status: returned</code> with the response in <code>result</code>. Other possible statuses are <code>pending</code>, <code>succeeded</code> and <code>failed</code>. Do not resubmit a generation on a timeout until you inspect request history for an accepted task.

These initial Tools expose the listed actions. The larger Ace Data Cloud API catalog may offer more actions and model variants. Check the current [model catalog](https://platform.acedata.cloud/models) and [service documentation](https://platform.acedata.cloud/documents) before choosing a different model or higher resolution.
