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
- 不复制 OpenSpec 正文到 Trellis task PRD 或 JSONL。
- 不破坏现有 Trellis `task.py create/start/archive/list/current` 基础行为。

## 验收标准

- [ ] Adapter 设计明确 OpenSpec、`.onion-sdd/current.json`、Trellis task metadata 三者边界。
- [ ] `task.json.meta.onion` 字段结构可标准 JSON 解析，且向后兼容。
- [ ] `/onion-continue` 文档说明 Trellis-aware 恢复路径和 fallback。
- [ ] journal 写入策略明确，不要求用户手工双写。
- [ ] Tier 3 parent/child 映射明确。
- [ ] 基础 Trellis 命令验证通过。

## 不做范围

- 不重写 Trellis 核心工作流。
- 不深 fork Trellis。
- 不把 OpenSpec 正文复制进 `.trellis/tasks/**/prd.md`。
- 不实现 marketplace 分发、metrics 聚合、`/onion-auto`。

## 开放问题

- 等基座能力子任务完成后，再决定 adapter 是纯文档/skill 级协议，还是需要修改 `.trellis/scripts/**` 提供辅助命令。
