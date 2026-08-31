# workspace-specflow for Codex

与 Cursor 工作区插件 `plugins/workspace-specflow/` 是同一套能力，不是另写的新插件。本目录只做 Codex 侧的分发适配：业务 skill 正文仍只在原目录维护；此处保存 Codex manifest、跨仓适配（如 `workspace-code-context`）和插件内打包工具。Cursor 与 Codex 可并存安装，互不影响。

## 构建

在 cursorkit 仓库根执行：

```bash
python3 codex-plugins/workspace-specflow/scripts/pack.py sync
python3 codex-plugins/workspace-specflow/scripts/pack.py check
python3 codex-plugins/workspace-specflow/scripts/pack.py pack
```

默认产物为 `codex-plugins/workspace-specflow/dist/workspace-specflow.zip`。ZIP 自包含可运行资源，但不包含维护用的 `scripts/pack.py`、测试或源锁文件。

源 skill 变化后，`check` 会因 `source-lock.json` 漂移而失败；先审阅变化，再执行 `sync` 更新锁。

## 安装

将 ZIP 交给使用者，通过 ChatGPT desktop 的 Codex / Work 模式打开 Plugins，在个人插件的创建或测试入口上传 skills-only ZIP。安装后新建会话，应能发现 workspace-specflow 原有技能和新增的 `workspace-code-context`。

Codex CLI 当前不直接从 ZIP 安装插件。需要 CLI 管理时，应先把解压后的插件目录加入本地 marketplace，再使用 `codex plugin` 浏览、安装或移除。详见 [OpenAI Codex 插件打包文档](https://developers.openai.com/plugins/build/plugins)。

## 依赖

- CodeWiki MCP：跨仓代码检索首选；认证由目标 Codex 环境管理，本包不内置凭证。
- brainstorming skill：`pm-proto`、`pm-spec-5`、`pm-spec` 和 `qa-spec` 的既有流程依赖。
- `lark-cli`、XMind MCP、Python、`curl`：按具体 workspace-specflow skill 的前置条件安装。

缺少可选依赖时必须按对应 skill 的停止或降级规则处理，不能假装步骤已完成。

## 升级与卸载

- 升级：拉取最新 cursorkit，执行 `sync`、`check`、`pack`，再用新 ZIP 替换旧版本。
- 卸载：从 Codex 的插件管理入口移除 `workspace-specflow`。
- 回滚：重新安装上一版 ZIP；不会影响 Cursor marketplace 中原有的 workspace-specflow 插件。

## CodeWiki 与降级

涉及代码扫描时，Codex 先加载 `workspace-code-context`：

1. 读取 specs 仓的 `workspace-repos.json`。
2. 通过 remote path 映射 GitNexus 规范仓名并调用 CodeWiki。
3. CodeWiki 不可用时，按 registry `path` 做本地只读扫描并提示用户。
4. 两种方式都不可用时，只停止依赖代码证据的当前步骤。

插件不保存 MCP token、用户凭证或私有认证信息。
