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

## 新增插件

在 Cursor 中可参考 [`docs/add-a-plugin.md`](docs/add-a-plugin.md) 操作：创建 `plugins/<插件名>/`、编写 `plugin.json`、在 `.cursor-plugin/marketplace.json` 注册，并运行 `node scripts/validate-template.mjs` 通过校验后再提交。

**建议：直接告诉cursor 参考 docs/add-a-plugin.md 新增某某插件**

## 安装使用（插件市场）

**Cursor** → **Settings** → **Plugins** → **onions-plugins** → 进入插件市场 → 选择插件 → **Add to Cursor**

- **后端 / 全栈（含 Go 与团队后端规范）**：建议安装 **Common** + **Backend**
- **仅需文档规范、代码审查、飞书分支等通用能力**：可只安装 **Common**

## 当前插件

| 插件 ID | 说明 |
| --- | --- |
| **common** | 通用：`rules`（如文档语言规范）、`commands`（如 `/cr`）、`skills`（本地 AI 代码审查、飞书需求分支等） |
| **backend** | 后端：`rules`（Go、HTTP、数据库、工程约定、安全合规等） |
