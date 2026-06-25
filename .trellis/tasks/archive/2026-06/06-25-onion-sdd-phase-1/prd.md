# onion-sdd Phase 1 改造

## 目标

在 Phase 0 已交付 `plugins/onion-sdd/` 静态试点插件的基础上，推进 onion-sdd Phase 1：先补齐以现网 `fe-specflow` 为基座的基础 SDD 闭环能力，再接入 Trellis adapter / 状态同步，使 `onion-sdd` 成为“fe-specflow 基座能力 + 去重门禁 + Trellis 运行时”的新方案。

## 已确认事实

- 用户已确认 Phase 1 主线选择 **Trellis adapter / 状态同步**，暂不以 marketplace 分发为主线。
- 用户进一步澄清：技术方案意图不是只做一个轻量命令壳，而是把原 `fe-specflow` 的基础能力复制并通用化为 `onion-sdd` 基座，去掉部分复杂流程门禁后，再结合 Trellis 运行时产出新方案。
- 已读取飞书技术方案 `https://guanghe.feishu.cn/wiki/FcsSwnZ1TiqLdskGa8EcO9U2nmb`，当前 revision `201`。文档核心结论包括：保留现有 `fe-specflow` 主流程能力；抽象通用 SDD 流程层为 `onion-sdd`；OpenSpec 作为唯一变更正文；Trellis 作为可插拔 task 运行时与团队 Spec Pack 注入。
- Phase 0 任务已归档，`plugins/onion-sdd/` 已包含 plugin manifest、README、五个 `/onion-*` 命令、三个 skill、规则文件和 `.onion-sdd/current.json` 示例模板。
- Phase 0 明确不做 Trellis adapter、workflow-state 强恢复、marketplace 注册、脚本校验集成、`/onion-auto`、AI spec self-review、metrics 平台和 Spec Pack registry。
- `DESIGN-SUPPLEMENT.md` 对 Phase 1 的明确预留包括：
  - `.onion-sdd/current.json.phase` → `task.json.phase` adapter 同步。
  - `.onion-sdd/current.json.tier` → `task.json.tier` adapter 同步。
  - `.onion-sdd/current.json.last_action` → workspace journal。
  - `task.json.source_hashes` 用于来源 hash。
  - Tier 3 parent/child 迁移到 Trellis task tree。
- 当前 Trellis task schema 已有 `children`、`parent` 和可扩展 `meta` 字段；尚未看到专门的 onion adapter 字段。
- 本仓库插件市场规范要求正式分发插件注册 `.cursor-plugin/marketplace.json` 并通过 `node scripts/validate-template.mjs`；试点插件可暂不注册，但 README 需要说明边界。
- 相关规范要求：JSON 状态必须可标准解析，中文文档默认使用中文，插件目录自包含，不创建空目录。
- 与 `fe-specflow` 对比的当前仓库差距：
  - `onion-sdd` Phase 0 已具备 Tier 0+/1 的分级、mini/light OpenSpec 模板、轻量 continue/finish 和去全仓扫描纪律。
  - 按飞书技术方案，`onion-sdd` 应具备原 `fe-specflow` 的基础能力：多源需求接入、设计澄清、OpenSpec 落盘、TDD 任务规划、后端/QA spec 接入、E2E 验证与归档门禁。
  - 当前仓库中的 `onion-sdd` 对 Tier 2+ 仍主要停留在 README / command 文档说明，未沉淀为 onion 自有完整 skills；这是 Phase 1 需要补齐的基座能力缺口。

## 候选 Phase 1 范围

Phase 1 主线需要拆成两个串行层次，而不是二选一：

- **层次 1：补齐 fe-specflow 基座能力（必须先做）**
  - 在现有 `/onion-*` 命令流程基础上，补齐原 `fe-specflow` 的基础 SDD 闭环能力。
  - 将原 `dev-workflow`、`design-to-opsx`、`pull-spec`、`e2e-verify` 中的通用能力迁移/改写为 onion 自有命令、skill、模板和门禁。
  - 保留 `onion-sdd` 去复杂门禁的设计：Tier 0+/1 不走完整 brainstorming / 默认 E2E；Tier 2+ 才进入完整闭环。
  - 不把 `fe-specflow` 作为运行时依赖，也不在 onion 产物中要求用户调用 `/fe-sdd`。

- **层次 2：Trellis adapter / 状态同步主线（在基座能力上接入）**
  - 将 `.onion-sdd/current.json` 的轻量状态与 Trellis task runtime 建立单向同步或兼容映射。
  - 明确 `task.json.meta.onion` 等扩展字段，承载 tier、phase、source hashes、active change id 和 last action。
  - 让 `/onion-continue` 的恢复口径从 OpenSpec fallback 进化为 Trellis-aware，但仍保持 onion 独立流程。
  - 为 Tier 3 parent/child 拆分设计 Trellis 任务树映射。

- **暂不作为主线：试点分发 / 校验落地**
  - 注册 marketplace，接入 `scripts/validate-template.mjs`。
  - 补齐 logo/assets、manifest metadata、README 安装方式和校验说明。
  - 强化 frontmatter、规则 glob、命令到 skill 的校验，让 onion-sdd 可以从手动试用进入正式分发。

## 子任务拆分

本父任务不直接实施代码，负责保存 Phase 1 源要求、子任务关系和最终集成验收。

| 子任务 | 路径 | 交付边界 | 顺序 |
| --- | --- | --- | --- |
| 补齐 fe-specflow 基座能力 | `.trellis/tasks/06-25-onion-sdd-base-capabilities` | 让 `onion-sdd` 在现有 `/onion-*` 命令下具备原 `fe-specflow` 的基础 SDD 闭环能力，并保留 Tier 0+/1 轻量化 | 先做 |
| Trellis adapter 状态同步 | `.trellis/tasks/06-25-onion-sdd-trellis-adapter` | 在基座能力明确后，将 onion 状态与 Trellis task metadata / journal / parent-child 建立同步与恢复协议 | 后做 |

## 需求

- Phase 1 以“补齐 fe-specflow 基座能力 + Trellis adapter / 状态同步”为本次可交付范围，避免同时铺开分发、auto、自审和 metrics。
- Phase 1 仍保持 `onion-sdd` 独立流程定位，不能把其他 SDD 插件作为运行时依赖。
- 必须先在现有命令流程基础上补齐原 `fe-specflow` 的基础能力：
  - `/onion-plan` 支持 Tier 2+ 的完整需求澄清与 OpenSpec 落盘路径，而不只是文档占位。
  - `/onion-continue` 能基于 OpenSpec 产物 + onion/Trellis 状态继续完整流程中的下一步。
  - `/onion-finish` 能检查 Tier 2+ 验证报告与归档门禁。
  - 补齐 onion 自有 skills，覆盖完整 OpenSpec 落盘、外部 spec 接入、E2E/验收报告等基础能力。
  - Tier 0+/1 继续保留 mini/light 轻量化，不被完整流程门禁拖重。
- Trellis adapter 需要在基座能力明确后接入：
  - 明确 `.onion-sdd/current.json` 与 Trellis task metadata 的字段映射。
  - 明确同步方向、冲突处理、fallback 策略和兼容策略。
  - 更新 `/onion-continue`、`/onion-plan`、README、规则或新增 onion 自有 skill，使用户能理解 Phase 1 的恢复路径。
  - 不破坏现有 Trellis task 创建、启动、归档和 active task 解析。
- 若选择分发主线：
  - 注册 `onion-sdd` 到 marketplace。
  - 补齐正式分发所需 metadata 和必要静态资产。
  - 通过模板校验，并更新 README 中“试点隔离”的表述。
- 任何代码或脚本改动都必须有对应验证命令；纯文档改动需有结构、frontmatter、关键短语和隔离检查。

## 验收标准

- [ ] Phase 1 主线已确认：先补齐 `fe-specflow` 基座能力，再接入 Trellis adapter / 状态同步。
- [ ] `design.md` / `implement.md` 中形成可执行方案。
- [ ] 两个子任务均有独立 PRD，且 adapter 子任务明确依赖基座能力产物。
- [ ] `onion-sdd` 在现有命令流程基础上具备原 `fe-specflow` 的基础能力闭环：需求接入/澄清、完整 OpenSpec、tasks/TDD 纪律、外部 spec 接入、E2E/验收报告、finish 门禁。
- [ ] Tier 0+/1 仍保持轻量化，跳过复杂 brainstorming 与默认 E2E，但有 mini/light OpenSpec 与定向验证记录。
- [ ] 产物不重新引入“全量扫描项目”硬约束。
- [ ] `onion-sdd` 仍不依赖其他 SDD 插件执行。
- [ ] 相关 README、commands、skills、rules 与 Phase 1 主线口径一致。
- [ ] 若涉及 `.trellis/scripts/**`，必须验证现有 Trellis 基础命令仍可运行。
- [ ] 若涉及 marketplace，必须通过 `node scripts/validate-template.mjs` 或记录明确偏离原因。
- [ ] Git diff 不包含与 Phase 1 主线无关的试点外改动。

## 不做范围

- 不在本任务内同时实现 `/onion-auto`、AI spec self-review、metrics 聚合平台和 Spec Pack registry。
- 不改造既有 `fe-specflow`、`workspace-specflow`、`be-specflow` 插件执行链路。
- 不把 `fe-specflow` 作为 `onion-sdd` 的运行时依赖；可以参考/迁移其能力，但最终要沉淀为 onion 自有命令、skill、模板和规则。
- 不把 Phase 0 已明确排除的“全仓扫描”重新作为硬性前置。
- 不自动执行 `openspec archive` 或 git commit。

## 开放问题

- 无阻塞性开放问题。当前规划采用两个子任务串行推进：先补完整 SDD 基座能力，再做 Trellis adapter。
