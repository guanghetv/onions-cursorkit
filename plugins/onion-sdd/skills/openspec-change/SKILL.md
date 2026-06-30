---
name: openspec-change
description: 将 Onion SDD 完整流程的需求与设计结论写入 OpenSpec change 产物，包括 proposal、specs 和 tasks。
---

# OpenSpec Change

本技能负责把 Tier 2+ 完整流程的结论写入 `openspec/changes/<change-id>/`。Agent 写 Markdown 内容；OpenSpec CLI 的创建、校验、归档由用户在终端执行。

## 前置条件

- Tier 已确认为 2 或 3，或 Tier 0+/1 在实现中升级。
- 已有需求事实、范围边界、关键决策和验收口径。
- 用户已同意进入 OpenSpec 落盘阶段。

## 目录

```text
openspec/changes/<change-id>/
├── proposal.md
├── tasks.md
└── specs/
    └── <capability>/
        └── spec.md
```

如 OpenSpec CLI 可用，提示用户执行：

```bash
openspec new change "<change-id>"
```

如 CLI 不可用，可手工创建上述目录和文件，但最终仍建议用户在终端校验。

## change-id

使用 kebab-case，优先动词开头，例如：

- `add-invoice-export`
- `fix-payment-state-flow`
- `update-role-permission`

如果来自明确需求编号，可使用 `<requirement-id>-<repo-or-domain>`。

## proposal.md 模板

```markdown
# <change-id>

## 背景
- <需求来源、问题、用户价值>

## 目标
- <本次必须达成的结果>

## 变更
- <产品、交互、接口、数据或流程变化>

## 影响范围
- 页面/模块: <范围>
- 数据/API: <接口、字段、错误码或无>
- 权限/安全/资金: <影响或无>
- 兼容性: <旧行为、迁移或回滚注意>

## 不做范围
- <明确排除的相邻需求>

## 验收
- <必须通过的场景、命令或 E2E 条件>

## 风险与回滚
- <主要风险、验证补偿、回滚方案>

## 前端实现决策
- <仅前端相关变更填写；记录 Figma/局部范围、灰区决策和项目既有模式。无则删除本节>

## References
- <需求链接、外部 spec、截图或用户描述来源>
```

## spec.md 模板

```markdown
# <capability>

<一句话说明能力。>

## ADDED Requirements

### Requirement: <行为要求>

系统 MUST <清楚描述期望行为>。

#### Scenario: <主要场景>

- **WHEN** <触发条件>
- **AND** <附加条件>
- **THEN** <期望结果>
- **AND** <附加期望>

#### Scenario: <边界场景>

- **WHEN** <边界条件>
- **THEN** <期望结果>
```

按实际情况使用 `ADDED`、`MODIFIED` 或 `REMOVED`。每个关键验收场景必须能在 `tasks.md` 或 `e2e-report.md` 找到验证路径。

如果前端灰区决策涉及可观察行为，必须转成 Scenario。例如空态、加载态、错误态、防重复提交、权限展示和分页策略不能只停留在 `proposal.md` 说明里。

## tasks.md 模板

```markdown
# Tasks: <change-id>

> 执行约束
> - 每个任务必须有验证点。
> - 可自动化时遵守 TDD；无法自动化时记录人工或浏览器验证步骤。
> - 前端任务按需覆盖 L1 契约/mock、L2 行为 Scenario、L3 联调/真实 API、L4 Browser 交叉验证。
> - 外部 spec 到达后必须做差异分析。
> - Tier 2+ 默认需要 E2E 或等价验收报告。

## 1. <模块或能力>

- [ ] 1.1 <任务描述>
      验证点: <测试命令、静态检查、手动步骤或 E2E 场景>
```

## Trellis 同步

OpenSpec 落盘后，如果当前项目存在 Trellis 且当前需求已经绑定 Trellis task，使用 `trellis-adapter` 同步轻量 metadata：

- `task.json.meta.onion.change_id`
- `task.json.meta.onion.change_path`
- `task.json.meta.onion.tier`
- `task.json.meta.onion.phase = "openspec"`
- `task.json.meta.onion.last_action`

同步边界：

- OpenSpec 仍是正文唯一真相源；不要把 `proposal.md`、`specs/**/spec.md` 或 `tasks.md` 正文复制进 Trellis task。
- Trellis task 的 `prd.md` / `design.md` / `implement.md` 只保存任务级摘要、工程计划和验证/回滚点。
- 若 Trellis 不可用或当前没有 Trellis task，不阻塞 OpenSpec 落盘；继续使用 `.onion-sdd/current.json` 和 OpenSpec 产物恢复。

## 质量自检

落盘后逐项检查：

1. 3 个月后能否从 `proposal.md` 理解为什么改、改什么、不改什么？
2. `spec.md` 是否至少覆盖主要场景和边界场景？
3. `tasks.md` 是否能指导实现，不只是功能清单？
4. 验收步骤是否可复现？
5. 是否避免把完整需求正文复制到 Trellis task 里？

任一答案为否，先补齐产物再继续。
