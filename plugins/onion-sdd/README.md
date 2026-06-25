# onion-sdd

Onion SDD 是一个通用 SDD 试点插件，用 slash command 把变更按复杂度分层：小变更走轻量 OpenSpec 产物，中大型变更进入 onion 自有完整 SDD 基座能力。它保留成熟 SDD 闭环中的需求接入、OpenSpec、任务规划、外部 spec 接入、E2E/验收和归档门禁，同时降低小任务的流程厚度。

## 当前能力

- 承诺 slash command 触发，不依赖自然语言弱触发。
- 通过 Tier 分级决定是否写 OpenSpec、写到什么粒度、何时升级到完整工作流。
- 提供 Tier 0+/Tier 1 的 mini/light OpenSpec 模板与验证纪律。
- Tier 2+ 使用 onion 自有完整 SDD skills，覆盖需求接入、完整 OpenSpec、任务规划、外部 spec 接入、E2E/验收和 finish 门禁。
- 按需读取与当前变更相关的需求、代码、OpenSpec、测试和验证材料，不设置全仓扫描硬约束。

## 目录

```text
plugins/onion-sdd/
├── .cursor-plugin/plugin.json
├── DESIGN-SUPPLEMENT.md
├── commands/
│   ├── onion-hotfix.md
│   ├── onion-tweak.md
│   ├── onion-plan.md
│   ├── onion-continue.md
│   └── onion-finish.md
├── rules/
│   └── onion-sdd.mdc
├── skills/
    ├── tier-triage/SKILL.md
    ├── mini-change/SKILL.md
    ├── light-change/SKILL.md
    ├── full-change/SKILL.md
    ├── openspec-change/SKILL.md
    ├── external-spec/SKILL.md
    └── verify-change/SKILL.md
└── templates/
    └── current.example.json
```

## 命令地图

| 命令 | 用途 | 主要技能 |
|------|------|----------|
| `/onion-hotfix` | Tier 0+/0++ : 小修复/低风险配置调整/紧急故障 | `tier-triage` → `mini-change` |
| `/onion-tweak` | Tier 1 : 单点轻量体验或行为调整 | `tier-triage` → `light-change` |
| `/onion-plan` | 判断变更层级并进入合适流程（主入口） | `tier-triage`，Tier 2+ 进入 `full-change` |
| `/onion-continue` | 从已有 `openspec/changes/**` 产物恢复上下文 | `.onion-sdd/current.json` + OpenSpec 产物 + 对应 skill |
| `/onion-finish` | 检查验证证据、任务完成度与归档条件 | `mini-change` / `light-change` / `verify-change` |

## Tier 路由

| Tier | 场景 | 默认处理 |
|------|------|----------|
| Tier 0 | 纯问答、排查、不需要修改 | 不创建 OpenSpec |
| Tier 0 (内部) | 纯内部修正（类型/lint/重构）或纯配置/文档 | 不创建 OpenSpec，commit 说明验证 |
| Tier 0+ | 明确且低风险的小改动 | 使用 mini change |
| Tier 0++ | 线上 P0/P1 紧急故障 | 先修后补，24h 内补 mini OpenSpec |
| Tier 1 | 单模块轻量行为或体验调整 | 使用 light change |
| Tier 2 | 跨模块、接口、状态流、数据契约或明显产品语义变化 | 转入 onion 完整 SDD 流程 |
| Tier 3 | 多仓、多角色、多阶段或需要拆分父子任务 | 先拆分，再按子任务进入完整流程 |

遇到风险红线时必须升级：需求不清、影响范围跨模块、数据契约变化、权限/安全/支付/资金相关、需要 E2E 门禁、或用户明确要求完整设计。

## 独立流程

`onion-sdd` 是独立的 SDD 插件流程，不要求安装其他 SDD 插件才能工作。所有用户可见的命令、技能、规则和产物口径都以 onion 自身为准；后续成熟能力应按 onion 的命名、模板和门禁沉淀到本插件内。

## 完整 SDD 基座

Tier 2+ 使用以下 onion 自有能力：

| Skill | 作用 |
|-------|------|
| `full-change` | 完整流程编排：需求接入、澄清、阶段推断、任务规划和事件路由 |
| `openspec-change` | 将设计结论写入 `proposal.md`、`specs/**/spec.md`、`tasks.md` |
| `external-spec` | 接入后端/API/QA/外部 spec，写入 `backend-*.md`、`qa-*.md` 并做差异分析 |
| `verify-change` | 生成验证清单，执行或记录 E2E/等价验收，写入 `e2e-report.md` |

完整流程仍遵循 OpenSpec 分工：用户在终端执行 OpenSpec CLI，Agent 负责变更目录中的 Markdown 产物。

## 试点安装

Phase 0 采用试点隔离方式：手动指定 `plugins/onion-sdd/` 路径在 Cursor 中试用。暂不注册 `.cursor-plugin/marketplace.json`，暂不更新仓库顶层 README，暂不进入插件市场分发。

## 当前不做

- 不做 `/onion-auto`；AI 自审、弱触发和自动推荐后续再补。
- 不做 Trellis adapter，不读写 Trellis workflow-state；后续由 adapter 把 onion 状态同步到 Trellis task runtime。
- 不做运行时指标、注册表、marketplace 发布和脚本校验集成。
- 不自动执行 `openspec archive`，不自动提交 git commit。
- 不修改试点目录外的既有插件。
- 不做 Tier 3 parent/child 任务自动化（仅做判定提示；后续接入 Trellis task tree）。

## 运行时状态

Phase 0 使用 `.onion-sdd/current.json` 维护当前变更的轻量运行时状态：

```jsonc
{
  "version": 1,
  "active_change_id": "2025-06-25-fix-payment-button",
  "tier": "0+",
  "phase": "implement",
  "last_action": "tasks.md 第 3 项已勾选完成，定向验证通过",
  "last_action_at": "2025-06-25T15:30:00+08:00",
  "upgrade_risk": false,
  "metrics": {
    "created_at": "2025-06-25T14:00:00+08:00",
    "triage_completed_at": "2025-06-25T14:05:00+08:00",
    "tasks_completed_at": null,
    "verified_at": null,
    "finished_at": null
  }
}
```

该文件由 onion-sdd 命令自动维护，不要求手动编辑。后续接入 Trellis 后由 adapter 单向同步替换。

模板见 `templates/current.example.json`。

## 带债归档

"债"指归档时已知但未解决的风险或未完成项。可以带债归档的：
- tasks.md 中已声明"不做"的项
- Tier 0+/1 只做了单浏览器定向验证（需标注）
- 已知兼容性问题已创建 follow-up issue

不可带债归档：
- Tier 2+ 跳过的 E2E
- 涉及升级红线的未同步接口契约
- 涉及支付/资金/权限的未验证变更

带债归档要求在 `proposal.md` 增加 `## 带债项` 章节逐条列明，并为每条债创建 follow-up issue。`/onion-finish` 输出中标注债项数。

## Rollback/Revert

| Revert 场景 | 处理方式 |
|-------------|----------|
| 未归档 change | tasks.md 追加 revert 任务 + 验证，正常 finish |
| 已归档 change | 创建新 change（change-id 含 "revert-<原id>"），按内容重新定 Tier |
| Tier 0++ 修复引发新问题 | 使用 Tier 0++ 紧急回退；触发流程审计 |

## 完整设计文档

补充设计细节见 [DESIGN-SUPPLEMENT.md](./DESIGN-SUPPLEMENT.md)。

## 验证建议

```bash
find plugins/onion-sdd -type f | sort
python3 -m json.tool plugins/onion-sdd/.cursor-plugin/plugin.json
rg -n "full-change|openspec-change|external-spec|verify-change" plugins/onion-sdd
```
