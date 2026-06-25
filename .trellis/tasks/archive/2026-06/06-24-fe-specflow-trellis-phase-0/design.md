# 技术设计

## 架构

新增 `plugins/onion-sdd/`，采用静态 Cursor plugin 形态。Phase 0 **只新建 onion 自有制品**，不把其他插件作为执行依赖：

```text
plugins/onion-sdd/
  .cursor-plugin/plugin.json
  DESIGN-SUPPLEMENT.md
  README.md
  commands/
    onion-hotfix.md
    onion-tweak.md
    onion-plan.md
    onion-continue.md
    onion-finish.md
  skills/
    tier-triage/SKILL.md              ← Phase 0 新建
    mini-change/SKILL.md              ← Phase 0 新建
    light-change/SKILL.md             ← Phase 0 新建
  rules/
    onion-sdd.mdc                     ← Phase 0 新建；Tier 分级门禁
  templates/
    current.example.json              ← 轻量状态模板
```

所有交付物都是 Markdown/JSON 文档制品，不引入运行时代码。

## 边界

- **`onion-sdd` 负责**：Tier 路由命令、Tier 0+/1 轻量 OpenSpec 模板、Tier 2+ 完整 SDD 路径说明、按需上下文纪律、Phase 0 分级门禁。
- **其他插件**：不参与 `onion-sdd` 的执行链路；后续成熟能力应沉淀为 onion 自有 skills、模板和规则。
- **Trellis**：本期完全不介入；`/onion-continue` 仅扫描 OpenSpec 产物，不读写 `.trellis/` runtime。
- **轻量状态**：Phase 0 使用 `.onion-sdd/current.json` 记录当前变更的最小运行态；缺失或不可信时 fallback 到 OpenSpec 产物推断。
- **触发方式**：Phase 0 先只承诺 slash command 触发，不承诺自然语言弱触发；自然语言路由与 workflow-state 强恢复放到后续阶段。
- **剔除的重约束**：
  - 「进入需求对齐前必须全量扫描当前仓库」→ 改为按需读取。
  - Tier 0+/1 不要求完整 `superpowers:brainstorming` 流程。
  - Tier 0+/1 默认定向验证，不要求 E2E。
- **沉淀为 onion 口径**：
  - OpenSpec 目录结构与 CLI 分工（用户终端执行 `openspec`，Agent 写 Markdown）。
  - 需求澄清 → 完整 OpenSpec 落盘顺序（Tier 2+）。
  - E2E 与 `e2e-report.md` 归档门禁（Tier 2+）。

## 命令流程

| 命令 | Tier | 调用链 |
| --- | --- | --- |
| `/onion-hotfix` | 0+ | `tier-triage` → `mini-change` |
| `/onion-hotfix` | 0++ | 先修后补 → 24h 内补 `mini-change` |
| `/onion-tweak` | 1 | `tier-triage`（最多一轮范围确认）→ `light-change` |
| `/onion-plan` | 0 | 建议 commit/PR 自审，不落 change |
| `/onion-plan` | 0+/1 | 路由到 hotfix/tweak 命令语义 |
| `/onion-plan` | 2 | `tier-triage` → 按需采集需求 → 需求澄清 → onion 完整 OpenSpec → 任务拆解 → 实现/联调/E2E |
| `/onion-plan` | 3 | 同上，额外要求 parent/child 变更拆分说明 |
| `/onion-continue` | 任意 | 扫描 `openspec/changes/**` 产物推断阶段；Tier 2+ 按 onion 完整 SDD 路径继续 |
| `/onion-finish` | 任意 | 检查定向验证或 E2E 记录 → 提示归档与人工 commit；journal = 变更内/session 摘要，非 Trellis |

## Tier 契约

| Tier | 路径 | OpenSpec | 验证 | 流程参照 |
| --- | --- | --- | --- | --- |
| 0 | `/onion-plan` | 不落 change | commit/PR 自审 | onion 命令 |
| 0+ | `/onion-hotfix` | 有风险时 mini change | 定向验证 | `mini-change` |
| 0++ | `/onion-hotfix` | 先修后补 mini change | 快速验证 + 24h 内补记录 | `mini-change` |
| 1 | `/onion-tweak` | light change | 定向验证 | `light-change` |
| 2 | `/onion-plan` | 完整 OpenSpec | 必须 E2E | onion 完整 SDD 路径 |
| 3 | `/onion-plan` + 拆分 | 每 child 一套 change | 按 child 验证 | onion 完整 SDD 路径 |

自动升级 Tier 2 的红线（与飞书方案 revision 184 一致）：

- 新增或变更接口契约、YApi、后端 spec 或测试 spec 依赖。
- 涉及登录、权限、支付、订单、数据写入/删除或核心转化链路。
- 跨模块、跨仓影响，或需要多人并行协作。
- 定向验证无法覆盖主要风险。
- 负责人判断存在明显线上回归风险。

## Onion 独立流程

| 维度 | onion-sdd Phase 0 |
| --- | --- |
| 入口 | `/onion-plan` 等五命令 |
| 上下文 | **按需**读取 |
| brainstorming | Tier 0+/1 **跳过**；Tier 2+ 按 onion 完整路径保留 |
| OpenSpec 模板 | Tier 0+/1 新增 mini/light；Tier 2+ 使用 onion 自有完整模板口径 |
| E2E | Tier 0+/1 默认跳过；Tier 2+ 必须 |
| Rule glob | 见下节「共存策略」 |

## 共存策略

1. **`onion-sdd.mdc` glob**：匹配 `openspec/**` 为主；**不**匹配 broad 业务源码 glob，降低与其他流程规则冲突的风险。
2. **命令选型**：新试点统一使用 `/onion-*`。
3. **`.cursor/commands/opsx-*`**：仓库内实验性 OpenSpec CLI 流，与 onion 命令并列；onion 文档注明「业务 SDD 试点优先 `/onion-*`，opsx 命令不在本期范围」。
4. **试点隔离**：不注册 marketplace，减少未验证插件被团队误装；需要试用时手动指定 `plugins/onion-sdd/` 路径。

## 产物语言

- README、命令、技能、规则、OpenSpec 模板字段使用中文。
- 保留必要英文专有名词：OpenSpec、Tier、E2E、runtime、skill 名等。

## 验证设计

```bash
# 结构
find plugins/onion-sdd -type f | sort
python3 -m json.tool plugins/onion-sdd/.cursor-plugin/plugin.json

# 路由：每个 command 必须提到对应 skill
rg -l "tier-triage|mini-change|light-change|onion 完整 SDD|完整 SDD 路径|验收规则" plugins/onion-sdd/commands/

# 纪律：无全仓扫描硬约束；有按需上下文
rg -n "全量扫描|按需" plugins/onion-sdd
! rg -n "必须全量扫描|全量扫描项目|扫描当前仓库" plugins/onion-sdd  # 不应出现硬性措辞

# 隔离
git diff -- plugins ':!plugins/onion-sdd'

# 独立性：onion 产物不记录其它插件名
! rg -n "fe-specflow|fe-sdd|dev-workflow|design-to-opsx|pull-spec|e2e-verify" plugins/onion-sdd
```

试点期**不**要求 `node scripts/validate-template.mjs` 通过（未注册 marketplace）；需要人工试用时手动指定 `plugins/onion-sdd/` 路径；但 commands/skills frontmatter 仍按 `docs/add-a-plugin.md` 自检。

## 取舍

- **独立流程**：本期先写 3 个 onion skills + 5 个命令，Tier 2+ 先用命令文档沉淀完整 SDD 路径；代价是 Phase 0 尚未把完整路径拆成独立 skills。
- **不接 Trellis**：continue/finish 保持弱恢复 → Phase 0 简单；强恢复留后续 adapter。
- **不注册 marketplace**：试点安全；代价是需手动指定 `plugins/onion-sdd/` 路径安装验证。
- **去掉全仓扫描**：显著降低小任务成本；代价是 tier-triage 红线必须写清，防止轻量路径误吞高风险变更。
