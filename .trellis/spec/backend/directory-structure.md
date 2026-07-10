# 目录结构

## 仓库形态

本仓库是 Cursor/AI 插件与 Trellis 工作流资产仓库，不是单一业务后端服务。后端相关内容主要有三类：

- `plugins/backend/`：Go、数据库、安全合规等后端规则资产。
- `plugins/be-specflow/`、`plugins/go-cutover-suite/`：后端研发工作流与路由切换命令/技能。
- `.trellis/scripts/`、`scripts/`、`install/`：Trellis 与插件市场的工具脚本。

## 顶层目录职责

| 目录 | 职责 | 示例 |
|------|------|------|
| `plugins/<name>/` | 一个可独立安装的 Cursor 插件 | `plugins/backend/`, `plugins/onion-sdd/` |
| `plugins/<name>/.cursor-plugin/plugin.json` | 插件 manifest | `plugins/workspace-specflow/.cursor-plugin/plugin.json` |
| `plugins/<name>/rules/*.mdc` | Cursor rule，必须有 frontmatter | `plugins/backend/rules/go-error-handling.mdc` |
| `plugins/<name>/commands/*.md` | slash command 文档 | `plugins/go-cutover-suite/commands/go-cutover.md` |
| `plugins/<name>/skills/<skill>/SKILL.md` | 可复用 skill | `plugins/workspace-specflow/skills/dev-start/SKILL.md` |
| `plugins/<name>/scripts/*.py` | 插件内薄运行时 helper（可选；如 onion-sdd） | `plugins/onion-sdd/scripts/onion_state.py` |
| `.trellis/scripts/` | Trellis 本地 Python 工具 | `.trellis/scripts/task.py` |
| `scripts/` | Node/CI 辅助脚本 | `scripts/validate-template.mjs` |
| `.cursor-plugin/marketplace.json` | 插件市场索引 | `.cursor-plugin/marketplace.json` |

## 新增插件目录规范

新增插件优先遵循 `docs/add-a-plugin.md`：

```text
plugins/my-plugin/
├── .cursor-plugin/plugin.json
├── README.md
├── commands/
├── rules/
├── skills/
└── assets/
```

只创建实际需要的子目录。未注册试点插件可以暂不更新 `.cursor-plugin/marketplace.json`，但必须在 README 中说明试点安装方式。

## Trellis 脚本边界

`.trellis/scripts/` 采用 Python 模块拆分：

- CLI 入口：`.trellis/scripts/task.py`、`.trellis/scripts/get_context.py`、`.trellis/scripts/add_session.py`
- 公共逻辑：`.trellis/scripts/common/*.py`
- hooks：`.trellis/scripts/hooks/*.py`

新增 Trellis 行为时优先放在 `common/` 中，再由 CLI 入口调用。不要把大量逻辑堆在入口脚本里。

参考：
- `.trellis/scripts/common/task_store.py`
- `.trellis/scripts/common/safe_commit.py`
- `.trellis/scripts/task.py`

## 命名约定

- 插件目录和插件 `name` 使用 kebab-case 或现有 lowercase 名称，例如 `workspace-specflow`、`go-cutover-suite`。
- rule 文件使用描述性 kebab-case，例如 `go-error-handling.mdc`、`fe-engineering-build-test-quality.mdc`。
- skill 目录名与 `SKILL.md` frontmatter 的 `name` 保持一致。
- Trellis Python 文件使用 snake_case。

## 常见错误

- 不要在插件目录外散落 commands/rules/skills。
- 不要新增插件后忘记 `.cursor-plugin/plugin.json`。
- 不要把试点插件直接注册 marketplace，除非需求明确要求进入分发。
- 不要在 Trellis 脚本中 `git add .trellis/`；只能 stage 明确产品路径。
