# CursorKit

维护洋葱私有 Cursor 插件市场 **`onions-plugins`**：每个插件在仓库内以独立目录发布，由根目录的 `marketplace.json` 聚合为可安装包。

## 仓库结构

| 路径 | 说明 |
| --- | --- |
| `plugins/<name>/` | 单插件源码：`rules/`、`skills/`、`commands/`、`assets/` 等，以及必需的 `plugins/<name>/.cursor-plugin/plugin.json` |
| `.cursor-plugin/marketplace.json` | 市场清单：声明 `pluginRoot`（当前为 `plugins`）及插件列表，`source` 为相对 `pluginRoot` 的插件目录名 |
| `docs/add-a-plugin.md` | 新增插件的步骤、清单字段与校验说明 |
| `scripts/validate-template.mjs` | 提交前校验插件与市场配置 |
| `install/cursor` | 将本仓库中的 `.cursor` 配置（commands / rules / skills）同步到目标项目或 `~/.cursor`，见 `install/README.md` |
| `scripts/sync-guardrails.mjs` | 从 [ai-guardrails](https://gitlab.yc345.tv/) 仓库同步前端 skills / rules / mcp 到 `frontend`、`fe-figma-flow`、`fe-onion-stack` 插件 |

## 新增插件

在 Cursor 中可参考 [`docs/add-a-plugin.md`](docs/add-a-plugin.md) 操作：创建 `plugins/<插件名>/`、编写 `plugin.json`、在 `.cursor-plugin/marketplace.json` 注册，并运行 `node scripts/validate-template.mjs` 通过校验后再提交。

**建议：直接告诉cursor 参考 docs/add-a-plugin.md 新增某某插件**

## 安装使用（插件市场）

**Cursor** → **Settings** → **Plugins** → **onions-plugins** → 进入插件市场 → 选择插件 → **Add to Cursor**

- **后端 / 全栈（含 Go 与团队后端规范）**：建议安装 **Common** + **Backend**
- **仅需文档规范、代码审查、飞书分支等通用能力**：可只安装 **Common**
- **前端安全审查 / 工程规范**：建议安装 **Common** + **Frontend**
- **前端 Figma 还原 / 响应式开发**：建议安装 **fe-figma-flow**（可叠加 **fe-onion-stack**）
- **洋葱内部前端技术栈（onion-ui / onion-utils / 视频）**：安装 **fe-onion-stack**
- **前端/后端 Spec-Driven（OpenSpec 变更目录）**：按需安装 **fe-specflow** / **be-specflow**（可与 Common 同装）

## 当前插件

| 插件 ID | 说明 |
| --- | --- |
| **common** | 通用：`rules`（如文档语言规范）、`commands`（如 `/cr`）、`skills`（本地 AI 代码审查、飞书需求分支等） |
| **backend** | 后端：`rules`（Go、HTTP、数据库、工程约定、安全合规等） |
| **frontend** | 前端安全与规范（同步自 ai-guardrails）：`skills`（fe-security、技术选型守卫、页面体验审查、工程化标准、性能优化）+ `rules`（commit、fe-engineering-\*、性能优化触发规则） |
| **fe-figma-flow** | 前端 Figma 还原工作流（同步自 ai-guardrails）：figma-read、img CDN 处理、响应式布局分析与实现、design-tokens，内置 Figma/CDN/DevTools `mcp.json` |
| **fe-onion-stack** | 前端洋葱内部技术栈（同步自 ai-guardrails）：onion-ui、onion-utils、洋葱视频、API 层规范 |
| **fe-specflow** | 前端 Specflow：OpenSpec + Superpowers 编排，`/fe-sdd`、pull-spec、e2e-verify 等 |
| **be-specflow** | 后端 Specflow：同上后端视角，`/be-sdd`、前端契约/QA spec 拉取、交叉验证与归档 |

## 与 ai-guardrails 的同步

`frontend`、`fe-figma-flow`、`fe-onion-stack` 三个插件的内容**同步自 [ai-guardrails](https://gitlab.yc345.tv/) 仓库**（source of truth），请勿在本仓库手改这些插件的 `skills/`、`rules/`、`mcp.json`，改动请提交到 ai-guardrails 后重新同步：

```bash
# 默认源为本地 ../ai-guardrails，可用 --source 指定路径
node scripts/sync-guardrails.mjs
node scripts/validate-template.mjs
```

每个同步插件根目录的 `.sync-meta.json` 记录了内容源版本、commit 与同步时间。内容到插件的映射表维护在 `scripts/sync-guardrails.mjs` 的 `PLUGIN_MAPPING` 中。

## Reviewer
