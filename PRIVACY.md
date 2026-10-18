# Privacy

The native OpenAI-compatible Connection, optional Pipe and Tools send the inputs you choose, plus the matching application API key, to <code>https://api.acedata.cloud</code> over HTTPS. The checked-in Python code uses fixed Ace Data Cloud endpoints. It does not read local files, run shell commands, or send data to another host. If you provide a public image or video URL, Ace Data Cloud may fetch that media to perform the requested operation. Only submit material you have permission to process.

For the native Connection, an administrator configures a key that is shared by users allowed to use those models; protect it in the server configuration and limit model access. For the optional Pipe and each Tool, a user enters a separate key in Open WebUI User Valves. The Valve field is masked in the UI. Open WebUI stores Valve values in its own database; masking alone does not encrypt them. Administrators should enable <code>ENABLE_VALVE_ENCRYPTION=true</code> and keep <code>WEBUI_SECRET_KEY</code> stable. The source files and Community shares contain no key or Valve value.

Open WebUI stores chats and Tool results according to the instance administrator's settings. Ace Data Cloud API calls and billing follow the current [Ace Data Cloud privacy policy](https://platform.acedata.cloud/privacy) and [service terms](https://platform.acedata.cloud/terms). Generated media URLs and task IDs appear in chat results. Do not share private task links or keys in public chats.

The Tools make no automatic retry of a generation request. A separate read-only <code>retrieve_task</code> call can inspect the same task ID without submitting new media work. Tool API calls may consume Credits at current service pricing. The per-user **Allow Billable Calls** switch is off by default.

Contact dev@acedata.cloud or open a [source issue](https://github.com/AceDataCloud/OpenWebUIPlugins/issues) without including credentials or private media.
