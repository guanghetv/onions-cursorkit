# 前端与插件资产开发规范

> 本目录面向本仓库中的前端相关 Cursor 插件、规则、commands、skills 和文档资产。这里的“frontend”不是业务前端应用源码目录。

## 适用范围

- `plugins/frontend/**`：前端安全、工程规范、性能优化等规则资产。
- `plugins/fe-figma-flow/**`、`plugins/fe-onion-stack/**`：前端工作流与内部技术栈插件。
- `plugins/fe-specflow/**`、`plugins/workspace-specflow/**`、`plugins/onion-sdd/**`：Spec-Driven 工作流插件。
- `.cursor/commands/**`、`.cursor/skills/**`：Cursor 本地命令/技能。
- Markdown 文档、`.mdc` 规则、`SKILL.md` 技能文件。

## 指南索引

| 指南 | 内容 | 状态 |
|------|------|------|
| [目录结构](./directory-structure.md) | 插件、commands、rules、skills 的组织方式 | 已填充 |
| [组件规范](./component-guidelines.md) | 本仓库无 UI 组件；记录插件文档组件的写法 | 已填充 |
| [Hook 规范](./hook-guidelines.md) | 本仓库无 React hooks；记录 Cursor/Trellis hook 资产边界 | 已填充 |
| [状态管理](./state-management.md) | OpenSpec、Trellis、轻量 JSON 状态的使用边界 | 已填充 |
| [质量规范](./quality-guidelines.md) | frontmatter、插件校验、文档审查 | 已填充 |
| [类型安全](./type-safety.md) | JSON manifest、YAML frontmatter、Markdown 模板字段 | 已填充 |

## 开发前检查清单

- 新增或修改插件前阅读 `docs/add-a-plugin.md`。
- 改正式插件市场条目前阅读 `.cursor-plugin/marketplace.json` 和 `scripts/validate-template.mjs`。
- 改同步插件前检查 manifest 描述是否写有“同步自 ai-guardrails，请勿手改”。
- 改命令/技能/规则时先看同插件内已有文件，保持命名、中文表达和路径口径一致。

## 质量检查

```bash
node scripts/validate-template.mjs
python3 -m json.tool plugins/<plugin>/.cursor-plugin/plugin.json
```

另外要人工确认 `.trellis/spec/` 中没有模板占位语、空章节或仍在要求英文填写的旧说明。

未注册试点插件可局部检查：

```bash
find plugins/<plugin> -type f | sort
python3 -m json.tool plugins/<plugin>/.cursor-plugin/plugin.json
```

## 语言

规则、README、命令说明、skill 文档默认中文；技术名词、文件路径、命令、API 字段保留英文。
