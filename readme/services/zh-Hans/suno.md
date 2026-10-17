# Suno Open WebUI 独立工具

生成音乐或歌词，通过同一任务号获取完成后的音频。 本集成由 **Ace Data Cloud** 提供，并非 Suno 创建方的官方插件。只安装这一项即可，不必安装整个 Ace 合集或另开 Pipelines 服务。

[English](../suno.md) · [当前权限与价格](https://platform.acedata.cloud/models?utm_source=opensource&utm_medium=referral&utm_campaign=evergreen&utm_content=sunoopenwebui_readme_pricing)

## 1. 查找并安装正确条目

**2026-10-18：Community 尚待发布，暂无核实的 Get/安装帖链接。** 在 [Open WebUI 官方 Community](https://openwebui.com/search) 人工搜索 **Suno**，核对标题 **Suno by Ace Data Cloud**、Ace 作者与源码；名字相同不代表就是本条目。账号持有人发布前还须人工查重，本文不声称现在已经搜到 Ace 条目。

正式帖子验证后，应通过其 **Get → 填实例 URL → Import** 导入、审源码并保存。此项是 **Tool**，位于 **Workspace → Tools**；不是 Admin Panel 的 Function。暂时可由管理员用 **Workspace → Tools → Create → Import From Link** 导入 [PR 源文件](https://github.com/AceDataCloud/OpenWebUIPlugins/blob/codex/openwebui-provider-tools/tools/suno.py)作手动预览，不能算官方分发。已有旧条目时更新它，不重复创建。拟发布版本 **0.1.1**。

管理员给目标用户授予 **Read**，代码导入/编辑权限仅留给可信管理员；Tool 会在服务器内执行 Python。只需此文件，其 `httpx` 依赖须可用。

![真实 Open WebUI 工具工作区](../../../_assets/tutorial/10-admin-tools.png)

真实历史 v0.11.4 图，2026-10-09 首次入库；旧名称与本次拟发布的服务优先标题不同。它只证明手动导入，不证明 Community 上架。

## 2. 注册登录并复制或创建专用 Key

1. 注册并登录 [Ace Data Cloud → 我的应用](https://platform.acedata.cloud/console/applications?utm_source=opensource&utm_medium=referral&utm_campaign=evergreen&utm_content=sunoopenwebui_readme_api_key)；没有通用应用时先点 **初始化通用应用**。
2. 打开 **General Application / 通用应用**，核对 **Suno** 权限、当前价格和余额。单服务 Key 限对应服务；通用 Key 也只能用账号有权使用的服务。
3. 点击图中 **①** 复制已有 Key，或 **② Manage Keys** → **Create** 新建独立 Open WebUI Key。

![复制已有 Key 或打开密钥管理](../../../_assets/tutorial/get-api-key-en.png)

4. 名称例如 `Open WebUI Suno`，按需设置有效期、用量和 Allowed APIs，创建后回列表复制。启用 API 限制时应包含：`/suno/audios`, `/suno/lyrics`, `/suno/tasks`。

![创建可选的专用凭据](../../../_assets/tutorial/create-api-key-en.png)

两张 Ace 控制台脱敏参考图原字节复用自 [SunoDify](https://github.com/AceDataCloud/SunoDify/tree/8d3d03570e73324220f111f7fe343da0792a8071/_assets/tutorial)，2026-10-18 下载复核；旧例名称为 `Dify tutorial`，此处改填 `Open WebUI Suno`。没有可见真实凭据。仅复制 Token 字符串，不带 `Bearer `、引号或遮挡字符；`platform-...` 管理 Token 不能代替服务 Key。

## 3. 在 Open WebUI 粘贴个人 Key

普通用户选择有工具调用能力、已授权的聊天模型。在输入框旁 **Integrations → Tools** 找 **Suno by Ace Data Cloud**，点滑块/设置，进入 **User Valves**，将 Key 粘贴到 **Api Key** 并保存。模型 Connection、可选 Pipe 与本 Tool 的 Key 相互独立，模型调用会另外计费。

![真实 Open WebUI 个人设置与遮蔽 Key](../../../_assets/tutorial/04-user-valves.png)

此真实历史 v0.11.4 图使用 Google Search 展示相同 Key 与 **Allow Billable Calls** 控件，不是新 Suno 调用。源码中开关默认关闭；图中测试者手动打开了它。存储加密需管理员配置 Valve 加密和稳定服务器密钥，遮蔽输入框本身不等于加密。

## 4. 首次动作与同任务查询

先检查当前价、余额；只启用此 Tool，并仅在准备承担这次费用时打开 **Allow Billable Calls**。收费示例提示词：

```text
Use Suno by Ace Data Cloud generate_music exactly once with prompt A short gentle instrumental piano melody for a sunrise, no vocals; model chirp-v6; instrumental true. Report the task ID. Do not retry, generate again, or poll automatically.
```

拿到 `task_id` 后关闭计费开关，保持 Tool 附加到聊天；稍后只查同一个 ID：

```text
Use Suno by Ace Data Cloud retrieve_task exactly once with task_id <your-task-id>. Report status, success, and media_urls. This is read-only. Never generate a new task.
```

`pending` 表示稍后继续查同 ID，不能为轮询再次生成。终态成功后打开返回的图片/音视频链接确认结果。这些提示词描述合同，不是已新发 Suno 生成的证据；高级动作见范围表，不宣称完整覆盖全部 API。

## 5. 结果、账单与常见问题

提交接受只会返回任务号；完成查询应有 `status: succeeded`、`success: true` 和最终 `media_urls`。pending/failed 不返回最终媒体。到 [Ace 使用历史](https://platform.acedata.cloud/console/usages)按 Key、时间窗口核对唯一生成和 Credits；模型、标题、标签及后续提问可能另发请求。这里不承诺历史测试价。

| 问题 | 检查 |
| --- | --- |
| 找不到 Tool | 管理员已导入这一个文件并授 Read；当前聊天重新启用。 |
| Key/计费开关错误 | 填此 Tool 自己的 User Valves；仅收费提交需要开关，查询可关闭。 |
| 401/403 | 应用 Key、过期、服务权限、余额和 Allowed APIs。 |
| 任务 pending | 稍后只查原任务号，不重复生成。 |
| 超时/5xx | 先查请求历史是否已接受；收费提交不会自动重试。 |

[方法与 API](../../../docs/SERVICES.md) · [隐私](../../../PRIVACY.md) · [问题反馈](https://github.com/AceDataCloud/OpenWebUIPlugins/issues) · dev@acedata.cloud
