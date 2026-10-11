# Ace Data Cloud for Open WebUI

Connect Ace Data Cloud chat models with Open WebUI's **native OpenAI-compatible Connection**, then install only the service Tools your users need. Each of the 17 Tools is a separate Python file and can be imported independently. An optional Pipe Function offers a personal model key for each user. The Tool and Pipe paths were tested on Open WebUI v0.11.4.

[简体中文教程](readme/README_zh_Hans.md) · [Service actions and API permissions](docs/SERVICES.md) · [Current models and pricing](https://platform.acedata.cloud/models)

**Publication status (2026-10-12):** this source is in [Ace Data Cloud PR #1](https://github.com/AceDataCloud/OpenWebUIPlugins/pull/1), awaiting merge. Open WebUI Community posts are pending. A GitHub source import is not a Community listing. Once posts are published, verify the author and source code on openwebui.com before clicking Get.

## 1. Start Open WebUI and review the source

If you already run Open WebUI v0.11.4 or later, continue to step 2. For a local first run, this copyable command contains no Ace Data Cloud key:

~~~bash
docker run -d --name open-webui -p 127.0.0.1:3000:8080 \
  -e WEBUI_SECRET_KEY="$(openssl rand -hex 32)" \
  -e ENABLE_VALVE_ENCRYPTION=true \
  -v open-webui:/app/backend/data \
  ghcr.io/open-webui/open-webui:v0.11.4
~~~

Open http://localhost:3000 and create the first account, which becomes the administrator. This command starts one local container; for a long-lived deployment, keep <code>WEBUI_SECRET_KEY</code> in your secret manager and reuse it if you replace the container. Changing it makes encrypted Valve values unreadable. The server needs HTTPS access to <code>api.acedata.cloud</code>. Review every Python file before importing it; Open WebUI executes Functions and Tools inside its server process.

## 2. Get the right Ace Data Cloud key

1. Sign in at [Ace Data Cloud → Applications](https://platform.acedata.cloud/console/applications).
2. Open **General Application**. Copy its API key with the copy icon (**1**) or choose **Manage Keys** (**2**) to create a separate Open WebUI key. A service-specific key works only for that service.
3. Check your service access, current price and balance. If you enable **Allowed APIs** for a restricted key, include every endpoint the chosen Connection, Pipe or Tool calls. The [service table](docs/SERVICES.md) names them. A shared administrator Connection and each user's Tool Valve may use different keys.

![Copy the API key from General Application](./_assets/tutorial/00-get-api-key.png)

Paste the token string only. Do not include <code>Bearer </code> or quotation marks. A platform management token beginning with <code>platform-</code> is not the application API key expected here. Do not paste a key into chat text, a prompt, a workflow export, or a GitHub issue.

## 3. Connect chat models with the native Connection

This is [Open WebUI's recommended route for an OpenAI-compatible provider](https://docs.openwebui.com/getting-started/quick-start/connect-a-provider/starting-with-functions/). Ace Data Cloud already provides <code>/v1/models</code> and <code>/v1/chat/completions</code>, so a Pipe is not needed for ordinary model access.

As an **Open WebUI administrator**, open **Admin Panel → Settings → Connections → OpenAI API**, add a connection, and enter:

| Field | Value |
| --- | --- |
| API Base URL | <code>https://api.acedata.cloud/v1</code> |
| API Key | Your Ace Data Cloud **application** API key, entered privately in the admin UI |

Save and **Verify Connection**. The base URL must end in <code>/v1</code>; Open WebUI appends <code>/models</code> and <code>/chat/completions</code>. A restricted key needs both <code>/v1/models</code> and <code>/v1/chat/completions</code>. In **Admin Panel → Settings → Models**, grant the intended users or group **Read** access to the chosen models. Select a model returned by your account's live model list; model availability and price can change. For a small chat check, send <code>Reply with the single word OK.</code> and confirm the reply is <code>OK</code>.

The administrator's Connection key is shared by everyone authorized to use those models. Keep that key in the server configuration and restrict model access to the intended users. Service Tools below use their own **per-user** keys and billable switches. If each chat user must bring a separate Ace Data Cloud key, use the optional Pipe in step 4. Open WebUI's experimental direct per-user Connections have different browser storage and CORS requirements; they are not the same deployment path.

## 4. Optional: install the personal-key model Pipe

As an **Open WebUI administrator**:

1. Open **Admin Panel → Functions → Import From Link**. Import [functions/acedatacloud_pipe.py](functions/acedatacloud_pipe.py) from its GitHub file URL, review the code, and save it as <code>acedatacloud_models</code>.
2. Turn the Pipe **Active**. Its admin Valves contain <code>MODEL_IDS</code>, initially <code>gpt-5.6-luna,deepseek-v4-flash</code>. Keep only public chat model IDs available to your Ace key. The Pipe adds each ID to the model picker; it does not grant users access by itself.
3. In **Admin Panel → Settings → Models**, give the intended users or group **Read** access to each Pipe model (or make each public to signed-in users). In the local test, a regular user saw no Pipe models until both model IDs received read access. Avoid <code>BYPASS_MODEL_ACCESS_CONTROL</code> for this setup.

![Installed and active model Pipe in the admin panel](./_assets/tutorial/09-admin-functions.png)

As a **regular user**, choose **Ace Data Cloud/gpt-5.6-luna** from the model picker. Open **Chat Controls → Valves**, switch the first selector from **Tools** to **Functions**, select **Ace Data Cloud Models**, and paste your key into **Api Key**. The field is masked on screen; the admin should enable Valve encryption at rest as in step 1.

![Pipe model appears in the regular user's model picker](./_assets/tutorial/01-model-picker.png)

![Set the personal model key in Chat Controls → Valves → Functions](./_assets/tutorial/08-pipe-user-key.png)

Send <code>Reply with the single word OK.</code> A successful first chat returns <code>OK</code>. The Pipe sends the selected model ID and messages to <code>https://api.acedata.cloud/v1/chat/completions</code> using **your** User Valve key. A restricted key needs <code>/v1/chat/completions</code>; the Pipe does not call <code>/v1/models</code> because the administrator controls its short model list. The screenshots in this section show the tested personal-key path.

## 5. Install one Tool and make a real search

As an administrator, open **Workspace → Tools**, use the **Create** menu's **Import From Link**, and import [tools/google_search.py](tools/google_search.py). Review and save it as <code>acedatacloud_google_search</code>. Grant the intended users or group **Read** access. Granting read access lets them run the Tool; the ability to create or import Tools must remain with trusted administrators. You can repeat this step for any service file in the [service table](docs/SERVICES.md).

![17 separate Tools installed in the test workspace](./_assets/tutorial/10-admin-tools.png)

As a regular user:

1. In a new chat, select a working Ace Data Cloud chat model from the native Connection, or **Ace Data Cloud/gpt-5.6-luna** if using the optional Pipe. Click the four-diamond **Integrations** icon next to the composer → **Tools**. Search for **Ace Data Cloud Google Search**. The screenshots show the tested Pipe model.
2. Click its sliders icon. In **User Valves**, enter your application key and turn on **Allow Billable Calls**; click **Save**. For a restricted key, allow <code>/serp/google</code>.
3. Toggle this Tool on for the chat and send the exact first-run prompt below. Open WebUI's **Native** tool-calling mode is the tested default.

![Select Google Search independently](./_assets/tutorial/02-tool-picker.png)

![Personal key is masked and billable calls are an explicit switch](./_assets/tutorial/04-user-valves.png)

~~~text
Use Ace Data Cloud Google Search exactly once for the official Open WebUI documentation about Tools. Return the first result title and URL; do not make any other search calls.
~~~

The tested result contained <code>Tools / Open WebUI</code> and https://docs.openwebui.com/features/extensibility/plugin/tools/. Open **View Result from search** to inspect the tool output. One matching usage record for the test key had HTTP 200 and deducted **0.009 Credits** under that account's discount; check your current price. Turn **Allow Billable Calls** off when you are finished.

![A regular user's real Google Search Tool result](./_assets/tutorial/03-google-search-result.png)

## 6. Generate one image, then query the same task

Install [tools/gpt_image.py](tools/gpt_image.py) as a separate Tool and grant read access. This example uses one <code>gpt-image-2</code> image at <code>1024x1024</code>, quality <code>low</code>. Check current pricing and balance first. If your key restricts APIs, allow both <code>/openai/images/generations</code> **and** <code>/openai/tasks</code>.

In a new chat, enable only **Ace Data Cloud GPT Image** under **Integrations → Tools**. Open its sliders icon, paste your personal key, and turn on **Allow Billable Calls**. Send:

~~~text
Call Ace Data Cloud GPT Image generate_image exactly once with model gpt-image-2, size 1024x1024, quality low, and prompt: A single lime green origami boat on a plain cream background, clean studio photograph, no text. Report the task ID. Do not call generate_image again or poll automatically.
~~~

The generation Tool returns a <code>task_id</code>. **That is an accepted task, not a completed image.** Record the ID and turn **Allow Billable Calls** off. The actual test submitted exactly one new generation and returned task <code>7893131f-77d0-4f93-b779-d192a74dd3e8</code>.

![One generation call returned a task ID](./_assets/tutorial/05-gpt-image-submitted.png)

The lower part of this real capture shows an unsuccessful follow-up: the Tool was no longer attached to that chat, so the model could not call <code>retrieve_task</code>. The submitted task ID remained valid. Re-enable the Tool in a new chat as follows; do not regenerate the image.

Open a **new chat**, re-enable **Ace Data Cloud GPT Image** in **Integrations → Tools**, and keep billable calls disabled. Use your own task ID in this read-only prompt:

~~~text
Use the attached Ace Data Cloud GPT Image retrieve_task function exactly once on task ID <your-task-id>. Report status, success, and the first media URL. This is a read-only lookup. Never generate a new image.
~~~

If the status is <code>pending</code>, repeat **only** <code>retrieve_task</code> with the same ID later. If the model says the tool is unavailable, re-enable the Tool in the chat before asking again. Wait for <code>status: succeeded</code> and <code>success: true</code>, then open the returned image URL. A green chat reply alone does not prove that a media task completed.

![The same task completed and returned a media URL](./_assets/tutorial/06-gpt-image-result.png)

![Actual first-run image from the completed task](./_assets/tutorial/07-gpt-image-output.png)

In [Ace Data Cloud Console usage](https://platform.acedata.cloud/console), locate the single generation request and its Credits deduction. For the test above, one matching <code>ApiUsage</code> record had HTTP 200 and deducted **0.099 Credits** under that account's discount. This is an observed test charge, not a promised price; consult the current price and your package rate. Task queries did not submit another generation.

## Other independent Tools

The [service table and Dify comparison](docs/SERVICES.md) list each of the 17 Tool files, its exposed action methods, task-query path, restricted-key Allowed APIs, and the larger Dify action surface. Media Tools default **Allow Billable Calls** to off. Each exposes a read-only <code>retrieve_task</code> method where the service uses asynchronous tasks. Google Search and Face Transform return results directly. Nano Banana supports explicit <code>nano-banana-2.1</code> selection for generation or editing; the first-run default remains <code>nano-banana-2-lite</code> until you check its current price. Grok video now defaults to Dify's public <code>grok-imagine-video-1.5-fast:reverse</code>, 6 seconds, 480p. These files cover the named first-run actions, not every advanced Dify action or API catalog variant.

## Troubleshooting and security

| Symptom | Check |
| --- | --- |
| Connection model, Pipe model or Tool missing for a regular user | Administrator must grant read access to each model and Tool. Import permission is separate. For a Connection, also verify the base URL and <code>/v1/models</code> access. |
| Tool says key or billable calls missing | Fill that Tool's own User Valves; the shared Connection key or optional Pipe key is separate. Turn on the billable switch only for the call you intend. |
| HTTP 401 / 403 | Use an application API key, check expiration, service access, balance and Allowed APIs. |
| HTTP 400 | Check the exact model, action and parameters in the [service table](docs/SERVICES.md). |
| HTTP 429 | Reduce concurrency and wait; do not enable automatic paid retries. |
| Timeout / HTTP 5xx / missing task ID | Inspect request history before resubmitting a billable generation. Do not create a second task just to poll. |
| <code>pending</code> or empty media list | Use <code>retrieve_task</code> on the same ID later. |

Tools and Functions execute arbitrary Python inside Open WebUI. Inspect each file before import, restrict Tool creation to trusted administrators, keep your instance updated, and enable <code>ENABLE_VALVE_ENCRYPTION=true</code> with a stable <code>WEBUI_SECRET_KEY</code>. A masked password field alone does **not** encrypt values in the database. Open WebUI v0.11.4 has optional experimental **Tool Permissions → Ask for approval**; it is off by default and does not gate automations or channel replies. The per-user billable switch in these Tools stays off by default.

[Privacy](PRIVACY.md) · [Source and development checks](docs/DEVELOPMENT.md) · [Community submission pack](docs/COMMUNITY_SUBMISSION.md) · [Report a problem](https://github.com/AceDataCloud/OpenWebUIPlugins/issues) · dev@acedata.cloud
