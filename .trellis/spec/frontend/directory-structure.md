# 目录结构

## 插件目录形态

每个插件都在 `plugins/<plugin-name>/` 下自包含。典型结构：

```text
plugins/<plugin-name>/
├── .cursor-plugin/plugin.json
├── README.md
├── commands/
├── rules/
├── skills/
├── agents/
├── hooks/
├── mcp.json
└── assets/
```

只创建实际需要的目录。不要为了“完整”而放空目录。

## 组件目录职责

| 目录/文件 | 职责 | 例子 |
|-----------|------|------|
| `.cursor-plugin/plugin.json` | 插件 manifest | `plugins/onion-sdd/.cursor-plugin/plugin.json` |
| `commands/*.md` | slash command 入口说明 | `plugins/onion-sdd/commands/onion-plan.md` |
| `rules/*.mdc` | Cursor rule，控制何时加载约束 | `plugins/onion-sdd/rules/onion-sdd.mdc` |
| `skills/<name>/SKILL.md` | 可复用流程能力 | `plugins/onion-sdd/skills/tier-triage/SKILL.md` |
| `README.md` | 面向使用者的安装、入口和边界 | `plugins/workspace-specflow/README.md` |
| `assets/` | marketplace 展示图标等静态资源 | `plugins/frontend/assets/frontend.png` |
| `mcp.json` | 插件内 MCP server 配置 | `plugins/fe-figma-flow/mcp.json` |

## Marketplace 结构

`.cursor-plugin/marketplace.json` 的 `metadata.pluginRoot` 为 `plugins`。正式分发插件的 `source` 使用插件目录名，而不是 `./plugins/<name>`：

```json
{
  "name": "frontend",
  "source": "frontend",
  "description": "前端安全与工程规范..."
}
```

## 试点插件

试点插件可以只放在 `plugins/<name>/` 中，暂不注册 marketplace。必须在 README 写明：

- 手动指定路径试用。
- 不进入插件市场。
- 何时补注册与校验。

参考：`plugins/onion-sdd/README.md`。

## 同步插件

`plugins/frontend/`、`plugins/fe-figma-flow/`、`plugins/fe-onion-stack/` 的 manifest 描述中写明同步自 `ai-guardrails`。这些目录下的 rules/skills/mcp 内容可能由 `scripts/sync-guardrails.mjs` 覆盖。

不要在同步产物里做长期手工修改；需要长期生效的改动应回源或改同步脚本。
