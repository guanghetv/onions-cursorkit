# onion-sdd Trellis adapter 状态同步

## 目标

在 `onion-sdd` 基座能力补齐后，将 OpenSpec / onion 轻量状态与 Trellis task runtime 建立可恢复、可同步、可回退的 adapter 协议，使 `/onion-continue` 能利用 Trellis 状态、journal 和 parent/child task tree 提升跨会话恢复能力。

## 依赖

- 必须等待 `.trellis/tasks/06-25-onion-sdd-base-capabilities` 完成或至少稳定以下契约：
  - onion 完整流程阶段模型。
  - `onion-sdd` 自有 skills 与命令路由。
  - OpenSpec 产物清单。
  - `/onion-continue` 的 OpenSpec fallback 规则。
  - `/onion-finish` 的验收门禁。

## 已确认事实

- 飞书技术方案 revision `201` 将 Trellis 定位为可插拔运行时，不替代 OpenSpec。
- OpenSpec 是单次变更正文唯一真相源。
- Trellis 只维护 metadata、phase、hash、path、journal、团队规范注入和恢复提示。
- Phase 0 的 `.onion-sdd/current.json` 字段包括 `active_change_id`、`tier`、`phase`、`last_action`、`last_action_at`、`upgrade_risk`、`metrics`。
- 当前 Trellis `task.json` 已有可扩展 `meta` 字段和 `children` / `parent` 字段。
- 当前 Trellis `task.py create/start/archive/list/current`、`add_session.py` 已能覆盖 adapter 第一版所需的任务创建、父子任务、归档和 journal 写入；不需要先修改 `.trellis/scripts/**`。
- `onion-sdd` 基座能力子任务已完成并归档，已新增 `full-change`、`openspec-change`、`external-spec`、`verify-change` 四个 onion 自有 skill。
- 用户明确补充：整个 onion-sdd × Trellis 方案都不改造 Trellis 源码或本仓库 `.trellis/scripts/**`；如后续确实涉及 Trellis 改造，必须先与用户确认后再规划。

## 需求

- 定义 `.onion-sdd/current.json` 与 `task.json.meta.onion` 的字段映射。
- 定义 OpenSpec change-id 与 Trellis task id / task dir 的对应关系。
- 定义 `/onion-continue` 的恢复优先级：
  - Trellis active task。
  - `.onion-sdd/current.json`。
  - `openspec/changes/**` 产物扫描。
- 定义 `last_action` / `last_action_at` 写入 workspace journal 的策略。
- 定义外部 spec / QA / E2E 产物的 `source_hashes` 计算和存储策略。
- 定义 Tier 3 parent/child 变更到 Trellis parent/child task tree 的映射。
- 新增 onion 自有 `trellis-adapter` skill，作为用户和 Agent 的 adapter 协议入口。
- 更新 `/onion-continue`、README、规则与状态模板，使 Trellis-aware 恢复路径可执行。
- 不复制 OpenSpec 正文到 Trellis task PRD 或 JSONL。
- 不破坏现有 Trellis `task.py create/start/archive/list/current` 基础行为。

## 验收标准

- [x] Adapter 设计明确 OpenSpec、`.onion-sdd/current.json`、Trellis task metadata 三者边界。
- [x] `task.json.meta.onion` 字段结构可标准 JSON 解析，且向后兼容。
- [x] `/onion-continue` 文档说明 Trellis-aware 恢复路径和 fallback。
- [x] journal 写入策略明确，不要求用户手工双写。
- [x] Tier 3 parent/child 映射明确。
- [x] `plugins/onion-sdd/skills/trellis-adapter/SKILL.md` 存在，并说明字段映射、同步时机、恢复优先级和回滚策略。
- [x] 基础 Trellis 命令验证通过。

## 不做范围

- 不重写 Trellis 核心工作流。
- 不深 fork Trellis。
- 不把 OpenSpec 正文复制进 `.trellis/tasks/**/prd.md`。
- 不实现 marketplace 分发、metrics 聚合、`/onion-auto`。
- 不在本子任务中修改 `.trellis/scripts/**`；如后续发现必须新增脚本辅助命令，另开任务或回到计划阶段。
- 不在未确认的情况下提出或实施 Trellis 源码/脚本改造。

## 开放问题

- 无阻塞性开放问题。第一版 adapter 采用插件内 skill + 文档协议，不改 Trellis 脚本。
