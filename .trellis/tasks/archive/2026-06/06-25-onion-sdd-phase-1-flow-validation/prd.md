# onion-sdd Phase 1 final flow validation

## Goal

验证 `plugins/onion-sdd/` 的 Phase 1 主流程已经可以被用户按 slash command 跑起来：从 `/onion-plan` 进入 Tier 分级和完整 SDD 基座，经过 OpenSpec 产物、Trellis adapter 恢复提示、验证报告门禁，最后由 `/onion-finish` 给出是否可归档的判断。

本任务是最终集成验收，核心是把当前 Phase 1 主流程跑起来。`/onion-auto` 明确不做，放到后续迭代优化。除 `/onion-auto` 外，验收中发现的缺口可以在本任务内修复；若涉及 Trellis 源码、`.trellis/scripts/**` 或 `.trellis/.runtime/**` 改造，必须先停止并请用户确认。

## Confirmed Facts

- 当前没有 active Trellis task，工作区在创建本任务前是 clean。
- Phase 1 的两个子任务已归档：
  - `06-25-onion-sdd-base-capabilities`
  - `06-25-onion-sdd-trellis-adapter`
- `plugins/onion-sdd/` 已包含命令入口：
  - `/onion-plan`
  - `/onion-continue`
  - `/onion-finish`
  - `/onion-hotfix`
  - `/onion-tweak`
- `plugins/onion-sdd/skills/` 已包含完整流程相关 skills：
  - `full-change`
  - `openspec-change`
  - `external-spec`
  - `verify-change`
  - `trellis-adapter`
- `/onion-plan` 明确 Tier 2+ 进入 onion 自有完整 SDD skills，不要求调用其他 SDD 插件。
- `/onion-continue` 明确恢复优先级：Trellis active task -> `.onion-sdd/current.json` -> `openspec/changes/**` fallback。
- `/onion-finish` 明确 Tier 2+ 以 `e2e-report.md` 的 `## 验收结论` 或用户确认的等价验收证据作为归档判断入口。
- README 与规则文件已声明 `/onion-auto` 不属于当前基座能力。

## Requirements

- 验收必须证明 Phase 1 主流程可以完整串联，而不只是单文件存在。
- 验收范围包括：
  - 插件文件结构和 JSON 格式。
  - command frontmatter 和主要入口文案。
  - Tier 2+ 命令到 skill 的路由完整性。
  - Trellis adapter 字段、恢复优先级和边界说明。
  - `/onion-finish` 对 Tier 2+ 验收门禁的判断口径。
  - 无“全量扫描项目”硬约束回归。
  - 无要求用户调用 `/fe-sdd` 或依赖 `fe-specflow` 执行的运行时说明。
- 验收应包含一条最小 Tier 2+ 流程演练，确认以下产物链路能被文档和命令规则解释：
  - `proposal.md`
  - `specs/**/spec.md`
  - `tasks.md`
  - 可选的 `backend-*.md` / `qa-*.md`
  - `e2e-report.md`
  - `task.json.meta.onion` / `.onion-sdd/current.json` 的恢复提示
- 验收过程中发现的文档断点、路由断点或边界措辞问题，应在本任务内修正并重新验证。
- 除 `/onion-auto` 外，AI spec self-review、metrics 聚合、Spec Pack registry、marketplace 分发等能力可以纳入验收观察或后续修复建议；如果是小范围文档/配置补齐，也可以在本任务内处理。
- 涉及 Trellis 源码、`.trellis/scripts/**` 或 `.trellis/.runtime/**` 的任何改造，必须先与用户确认后再规划或实现。
- 不自动执行 `openspec archive`。
- 不自动提交 git commit，除非用户另行要求。

## Acceptance Criteria

- [x] Phase 1 final validation task has a clear PRD and, if needed, an execution checklist.
- [x] Structure check passes for `plugins/onion-sdd`.
- [x] `plugins/onion-sdd/.cursor-plugin/plugin.json` and `plugins/onion-sdd/templates/current.example.json` parse as JSON.
- [x] `/onion-plan` routes Tier 2+ to onion-owned `full-change`, `openspec-change`, `external-spec`, and `verify-change`.
- [x] `/onion-continue` documents Trellis-aware recovery and OpenSpec fallback.
- [x] `/onion-finish` documents Tier 2+ validation and归档门禁.
- [x] `trellis-adapter` documents `meta.onion`, `trellis_task`, `source_hashes`, conflict handling, and the no-Trellis-source-change boundary.
- [x] No hard full-repository scan requirement is present in `plugins/onion-sdd`.
- [x] No runtime dependency wording requires `/fe-sdd` or `fe-specflow`.
- [x] `/onion-auto` is explicitly excluded from this final validation.
- [x] AI self-review, metrics aggregation, Spec Pack registry, and marketplace publishing are either validated as present, fixed if small and local, or recorded as follow-up gaps.
- [x] Any required Trellis source/script/runtime change is stopped before implementation and brought back to the user for confirmation.
- [x] A Tier 2+ flow walkthrough result is recorded in this task, including any gaps found and whether the flow is ready for a real pilot.

## Out of Scope

- Implementing `/onion-auto`.
- Implementing Trellis source/script/runtime changes without explicit user confirmation.
- Reworking existing non-onion SDD plugins unless the validation proves a small cross-reference fix is required and user approves.

## Open Questions

- None blocking. The user approved doing all non-`/onion-auto` validation/fix work, with Trellis source改造 requiring separate confirmation.

## Notes

- Keep `prd.md` focused on requirements, constraints, and acceptance criteria.
- Lightweight tasks can remain PRD-only.
- For complex tasks, add `design.md` for technical design and `implement.md` for execution planning before `task.py start`.
