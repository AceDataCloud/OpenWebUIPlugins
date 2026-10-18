"""Build local, independently publishable Top 5 materials; never contact Community.

The Python Tool is the install unit. The manifest locks its exact bytes and lists
the separately imported actions. Official post URLs remain null until verified.
"""
from __future__ import annotations

import ast
import hashlib
import importlib.util
import inspect
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlencode

from generate_service_tools import DISCOVERY, SERVICES

ROOT = Path(__file__).resolve().parents[1]
CATALOG = (
    ("suno", "Suno", "Music / Audio", "生成音乐或歌词，通过同一任务号获取完成后的音频。", "suno music lyrics audio", "generate_music", "prompt A short gentle instrumental piano melody for a sunrise, no vocals; model chirp-v6; instrumental true"),
    ("seedance", "Seedance", "Video", "生成 Seedance 视频，通过同一任务号获取完成后的视频链接。", "seedance video text-to-video", "generate_video", "prompt A quiet mountain lake at sunrise; duration 4; resolution 480p; ratio 16:9"),
    ("happy_horse", "Happy Horse", "Video", "生成 Happy Horse（HappyHorse）视频，通过同一任务号查询完成结果。", "happyhorse happy horse video", "generate_video", "prompt A quiet mountain lake at sunrise; duration 3; resolution 720P; ratio 16:9"),
    ("gpt_image", "GPT Image", "Images", "生成或编辑 GPT Image 图片，通过同一任务号查询完成后的图片。", "gpt image gpt-image image editing", "generate_image", "prompt A single lime green origami boat on a cream background, no text; model gpt-image-2; size 1024x1024; quality low"),
    ("nano_banana", "Nano Banana", "Images", "生成或编辑 Nano Banana 图片，通过同一任务号查询完成结果。", "nano banana nano-banana image editing", "generate_image", "prompt A single lime green origami boat on a cream background, no text; model nano-banana-2-lite; resolution 1K; aspect_ratio 1:1"),
)


def link(slug: str, placement: str, path: str) -> str:
    return "https://platform.acedata.cloud/" + path + "?" + urlencode({
        "utm_source": "opensource", "utm_medium": "referral", "utm_campaign": "evergreen",
        "utm_content": f"{slug}openwebui_{placement}",
    })


def load(slug: str):
    path = ROOT / "tools" / f"{slug}.py"
    spec = importlib.util.spec_from_file_location("community_" + slug, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    text = path.read_text()
    metadata = dict(re.findall(r"^([a-z_]+): (.+)$", ast.get_docstring(ast.parse(text)) or "", re.M))
    service = next(item for item in SERVICES if item.slug == slug)
    return path, module, metadata, service


def build() -> dict[Path, str]:
    outputs = {}
    entries = []
    for slug, name, category, zh_description, search, first_method, args in CATALOG:
        path, module, metadata, service = load(slug)
        methods = [
            {"name": method, "signature": str(inspect.signature(fn)), "read_only": method == "retrieve_task"}
            for method, fn in inspect.getmembers(module.Tools(), inspect.ismethod) if not method.startswith("_")
        ]
        apis = sorted({action.path for action in service.actions} | {service.task_path})
        item = {
            "id": slug, "title": metadata["title"], "publisher": "Ace Data Cloud",
            "type": "Tool", "description": metadata["description"], "description_zh": zh_description,
            "search_terms": search.split(), "suggested_tags": DISCOVERY[slug][1].split(", "),
            "suggested_category": category,
            "publisher_icon": "_assets/acedata-mark.png",
            "brand_disclosure": "Integration by Ace Data Cloud. Not an official plugin from the named model/service creator.",
            "source_file": f"tools/{slug}.py", "source_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "version": metadata["version"], "required_open_webui_version": metadata["required_open_webui_version"],
            "install_unit": "one self-contained Python file; no companion Tool or Pipeline required",
            "official_directory_url": "https://openwebui.com/search", "official_listing_url": None,
            "publication_status": "not_submitted", "source_pr": "https://github.com/AceDataCloud/OpenWebUIPlugins/pull/1",
            "allowed_apis": apis, "methods": methods,
            "readme_en": f"readme/services/{slug}.md", "readme_zh": f"readme/services/zh-Hans/{slug}.md",
            "application_key_url": link(slug, "community_api_key", "console/applications"),
            "pricing_url": link(slug, "community_pricing", "models"),
            "install_verified_from_community": False,
        }
        entries.append(item)
        source_url = "https://github.com/AceDataCloud/OpenWebUIPlugins/blob/v0.1.1/" + item["source_file"]
        api_text = ", ".join(f"`{api}`" for api in apis)
        submit_prompt = f"Use {item['title']} {first_method} exactly once with {args}. Report the task ID. Do not retry, generate again, or poll automatically."
        query_prompt = f"Use {item['title']} retrieve_task exactly once with task_id <your-task-id>. Report status, success, and media_urls. This is read-only. Never generate a new task."
        common = {
            "title": item["title"], "file": item["source_file"], "source": source_url,
            "apis": api_text, "submit": submit_prompt, "query": query_prompt,
            "version": item["version"], "key": link(slug, "readme_api_key", "console/applications"),
            "pricing": link(slug, "readme_pricing", "models"),
        }
        en = f'''# {name} for Open WebUI

{metadata['description']} This is an integration **by Ace Data Cloud**, not an official plugin from the {name} creator. Install this service independently; no Ace bundle or separate Pipelines server is required.

[简体中文](zh-Hans/{slug}.md) · [Current access and pricing]({common['pricing']})

## 1. Find and install the correct Tool

**Community publication is pending (2026-10-18). There is no verified Get/install post URL yet.** In the [official Community library](https://openwebui.com/search), manually search **{name}**, then check for **{item['title']}**, the Ace Data Cloud author, and the reviewed source. A matching name alone does not establish ownership. The official account holder must check for an existing entry before publishing; this guide does not claim that search currently finds ours.

After a verified post is linked here, use its **Get → your Open WebUI URL → Import** flow, review the code, and save. Functions go to Admin Panel; this service is a **Tool** and belongs in **Workspace → Tools**. Until Community publication, use the [first-party v0.1.1 GitHub release](https://github.com/AceDataCloud/OpenWebUIPlugins/releases/tag/v0.1.1) for this service’s separate Python, import JSON or ZIP; see the [download/import instructions](../../docs/RELEASE.md). An administrator can also import the [tagged source file]({common['source']}) using **Workspace → Tools → Create → Import From Link**. GitHub distribution is available independently of Community publication and is not evidence of Community search/Get. Save an existing file over its prior entry instead of creating a duplicate. Proposed Tool version: **{common['version']}**.

The administrator grants intended users **Read** access. Keep code creation/import permissions with trusted administrators. Source review is required because a Tool runs Python inside your server. Open WebUI installs this one file without another Ace Tool; its own `httpx` requirement must be available.

![Real Open WebUI Tools workspace after administrator import](../../_assets/tutorial/10-admin-tools.png)

Historical real v0.11.4 screenshot, first committed 2026-10-09. It shows manual installation of the previous names; the service-first title above is the proposed update. It does not prove Community publication.

## 2. Register, sign in, and copy or create a Key

1. Register or sign in at [Ace Data Cloud → Applications]({common['key']}). If needed, choose **Initialize General Application** first.
2. Open **General Application**. Check **{name}** access, current price and balance. A service-specific key works only for that service; a General Application key covers only services your account is entitled to use.
3. Copy the selected application key (**1**) or open **Manage Keys** (**2**) and choose **Create** for a dedicated Open WebUI key.

![Copy a key or open Manage Keys](../../_assets/tutorial/get-api-key-en.png)

4. Use a name such as `Open WebUI {name}`. Set expiry, usage limits and Allowed APIs as appropriate, create, then copy from the application/credential list. Restricted keys need: {api_text}.

![Create an optional dedicated credential](../../_assets/tutorial/create-api-key-en.png)

These are redacted Ace Console reference screenshots reused byte-for-byte from [SunoDify](https://github.com/AceDataCloud/SunoDify/tree/8d3d03570e73324220f111f7fe343da0792a8071/_assets/tutorial), downloaded and reviewed 2026-10-18. The old example name says `Dify tutorial`; enter `Open WebUI {name}` instead. No real credential is visible. Copy only the token, without `Bearer ` or quotes. A `platform-...` management token is not the service key.

## 3. Paste the personal Key in Open WebUI

As an ordinary user, select an authorized chat model that supports tool calling. Open the composer's **Integrations → Tools**, find **{item['title']}**, and open its sliders/settings. In **User Valves**, paste your Key into **Api Key** and Save. The shared model Connection and optional model Pipe do not fill this Tool's Key. The model itself can incur separate charges.

![Real masked User Valves in Open WebUI](../../_assets/tutorial/04-user-valves.png)

This historical v0.11.4 real screenshot uses Google Search to show the same Key and **Allow Billable Calls** fields. It is not a new {name} run. The switch defaults **off** in the source; the picture shows a tester who explicitly turned it on. Enable Valve encryption with a stable server secret to protect stored keys.

## 4. First action, then the same task

Check current pricing and balance before any generation. Enable only this Tool and turn on **Allow Billable Calls** only for the intended action. Do not send this prompt unless the charge is intended:

```text
{submit_prompt}
```

Record `task_id`, turn **Allow Billable Calls** off, and keep this Tool attached. Query the same ID later:

```text
{query_prompt}
```

`pending` means wait and query that same ID again later; never regenerate to poll. A result is complete only with terminal success and an openable image/audio/video link. These prompts specify the intended contract; they are not evidence of a new {name} generation. Advanced actions outside the listed methods are not included.

## 5. Results, usage and common issues

An accepted task returns a task ID. A finished query returns `status: succeeded`, `success: true`, and final `media_urls`; failed/pending tasks have no final media URLs. Open your own output and match the unique generation usage in [Ace usage history](https://platform.acedata.cloud/console/usages). Amounts are Credits and depend on current account pricing; the model, titles, tags and follow-up suggestions can create additional requests. No fixed historical test price is promised here.

| Problem | Check |
| --- | --- |
| Tool missing | Administrator imported this one file and granted **Read**; re-enable it for the current chat. |
| Key/billable switch error | Fill this Tool's personal User Valves; enable the switch only for the intended paid submit. Queries work with it off. |
| 401/403 | Application Key, expiry, service access, balance and Allowed APIs. |
| Pending task | Query the same task ID later; do not submit again. |
| Timeout/5xx | Check existing request history for an accepted task before any resubmission. Paid actions are never automatically retried. |

[Scope and APIs](../../docs/SERVICES.md) · [Privacy](../../PRIVACY.md) · [Issues](https://github.com/AceDataCloud/OpenWebUIPlugins/issues) · dev@acedata.cloud
'''
        zh = f'''# {name} Open WebUI 独立工具

{zh_description} 本集成由 **Ace Data Cloud** 提供，并非 {name} 创建方的官方插件。只安装这一项即可，不必安装整个 Ace 合集或另开 Pipelines 服务。

[English](../{slug}.md) · [当前权限与价格]({common['pricing']})

## 1. 查找并安装正确条目

**2026-10-18：Community 尚待发布，暂无核实的 Get/安装帖链接。** 在 [Open WebUI 官方 Community](https://openwebui.com/search) 人工搜索 **{name}**，核对标题 **{item['title']}**、Ace 作者与源码；名字相同不代表就是本条目。账号持有人发布前还须人工查重，本文不声称现在已经搜到 Ace 条目。

正式帖子验证后，应通过其 **Get → 填实例 URL → Import** 导入、审源码并保存。此项是 **Tool**，位于 **Workspace → Tools**；不是 Admin Panel 的 Function。Community 发布前，可从 [GitHub v0.1.1 版本](https://github.com/AceDataCloud/OpenWebUIPlugins/releases/tag/v0.1.1) 下载该服务独立 Python、导入 JSON 或 ZIP，见[下载说明](../../../docs/RELEASE.md)；也可由管理员用 **Workspace → Tools → Create → Import From Link** 导入[标签源文件]({common['source']})。GitHub 是独立可用的一方分发，不等于 Community 搜索/Get 已上线。已有旧条目时更新它，不重复创建。拟发布版本 **{common['version']}**。

管理员给目标用户授予 **Read**，代码导入/编辑权限仅留给可信管理员；Tool 会在服务器内执行 Python。只需此文件，其 `httpx` 依赖须可用。

![真实 Open WebUI 工具工作区](../../../_assets/tutorial/10-admin-tools.png)

真实历史 v0.11.4 图，2026-10-09 首次入库；旧名称与本次拟发布的服务优先标题不同。它只证明手动导入，不证明 Community 上架。

## 2. 注册登录并复制或创建专用 Key

1. 注册并登录 [Ace Data Cloud → 我的应用]({common['key']})；没有通用应用时先点 **初始化通用应用**。
2. 打开 **General Application / 通用应用**，核对 **{name}** 权限、当前价格和余额。单服务 Key 限对应服务；通用 Key 也只能用账号有权使用的服务。
3. 点击图中 **①** 复制已有 Key，或 **② Manage Keys** → **Create** 新建独立 Open WebUI Key。

![复制已有 Key 或打开密钥管理](../../../_assets/tutorial/get-api-key-en.png)

4. 名称例如 `Open WebUI {name}`，按需设置有效期、用量和 Allowed APIs，创建后回列表复制。启用 API 限制时应包含：{api_text}。

![创建可选的专用凭据](../../../_assets/tutorial/create-api-key-en.png)

两张 Ace 控制台脱敏参考图原字节复用自 [SunoDify](https://github.com/AceDataCloud/SunoDify/tree/8d3d03570e73324220f111f7fe343da0792a8071/_assets/tutorial)，2026-10-18 下载复核；旧例名称为 `Dify tutorial`，此处改填 `Open WebUI {name}`。没有可见真实凭据。仅复制 Token 字符串，不带 `Bearer `、引号或遮挡字符；`platform-...` 管理 Token 不能代替服务 Key。

## 3. 在 Open WebUI 粘贴个人 Key

普通用户选择有工具调用能力、已授权的聊天模型。在输入框旁 **Integrations → Tools** 找 **{item['title']}**，点滑块/设置，进入 **User Valves**，将 Key 粘贴到 **Api Key** 并保存。模型 Connection、可选 Pipe 与本 Tool 的 Key 相互独立，模型调用会另外计费。

![真实 Open WebUI 个人设置与遮蔽 Key](../../../_assets/tutorial/04-user-valves.png)

此真实历史 v0.11.4 图使用 Google Search 展示相同 Key 与 **Allow Billable Calls** 控件，不是新 {name} 调用。源码中开关默认关闭；图中测试者手动打开了它。存储加密需管理员配置 Valve 加密和稳定服务器密钥，遮蔽输入框本身不等于加密。

## 4. 首次动作与同任务查询

先检查当前价、余额；只启用此 Tool，并仅在准备承担这次费用时打开 **Allow Billable Calls**。收费示例提示词：

```text
{submit_prompt}
```

拿到 `task_id` 后关闭计费开关，保持 Tool 附加到聊天；稍后只查同一个 ID：

```text
{query_prompt}
```

`pending` 表示稍后继续查同 ID，不能为轮询再次生成。终态成功后打开返回的图片/音视频链接确认结果。这些提示词描述合同，不是已新发 {name} 生成的证据；高级动作见范围表，不宣称完整覆盖全部 API。

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
'''
        outputs[ROOT / item["readme_en"]] = en
        outputs[ROOT / item["readme_zh"]] = zh
        draft = f'''# {item['title']}

LOCAL PUBLICATION DRAFT — not yet posted. Version {item['version']}.

{item['description']}

{item['brand_disclosure']}

- Post type: **Tool**; one independently importable file.
- Search focus: {search}. Suggested tags: {', '.join(item['suggested_tags'])}.
- Suggested category, only if offered by the website: {category}.
- Author/publisher: **Ace Data Cloud**, using the existing Ace-controlled account. Publisher icon, only if the form offers it: [Ace mark](../../_assets/acedata-mark.png); not the named service creator's logo.
- Official post/Get URL: **pending**. Do not substitute a repository or search URL for a verified listing.
- Source: [{item['source_file']}]({source_url}); SHA-256 `{item['source_sha256']}`.
- [English walkthrough](../../{item['readme_en']}) · [中文教程](../../{item['readme_zh']}). Convert these to absolute merged-source URLs in the website form.
- [Get the correct Key]({item['application_key_url']}) · [Check price/access]({item['pricing_url']}).
- Allowed APIs: {api_text}.
- Official Community Share/import process: https://docs.openwebui.com/ecosystem/community/.

## Publish once, then verify

1. Source PR #1 is merged. Confirm the release/source bytes match this digest. Install this one Tool in the administrator's instance.
2. Account holder manually searches {name} and Ace variants. Update an existing Ace-owned entry if present; do not post a duplicate.
3. **Workspace → Tools → Share** opens the prefilled website form. Review exact title, description, full source and allowed tags/category. Use Ace's own publisher mark if the form offers an icon; do not imply the named service's official endorsement.
4. Finish only through the authenticated official UI, after the account holder handles any legal terms. Record the exact public post URL and visible code version. Do not run an automated website script.
5. Verify keyword discovery, a separate instance's **Get → Import**, admin Read grants, user's masked Key and off-by-default billing switch. Run only an authorized action or a same-ID read-only lookup; record final media and unique usage separately.

None of the steps above is claimed complete by this draft. A `tags` frontmatter hint is not proof the website indexed it; enter only accepted tags in the actual form and verify the published search result. No new generation or paid request is sent by this script.
'''
        outputs[ROOT / "docs/community" / f"{slug}.md"] = draft
    outputs[ROOT / "docs/community/catalog.json"] = json.dumps({
        "schema_version": 1, "prepared_on": "2026-10-18", "publication_status": "local_materials_only",
        "source_repository": "https://github.com/AceDataCloud/OpenWebUIPlugins",
        "independent_entries": entries,
    }, ensure_ascii=False, indent=2) + "\n"
    return outputs


def main() -> int:
    outputs = build()
    if "--check" in sys.argv:
        stale = [str(path.relative_to(ROOT)) for path, content in outputs.items() if not path.exists() or path.read_text() != content]
        if stale:
            print("Stale Community materials: " + ", ".join(stale))
            return 1
    else:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
    print(f"{'Checked' if '--check' in sys.argv else 'Built'} 5 separate entry drafts, 10 bilingual guides and a source-hash catalog; no publication or API calls.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
