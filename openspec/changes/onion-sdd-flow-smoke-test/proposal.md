# Onion SDD Flow Smoke Test

## Why

本变更用于验证 `plugins/onion-sdd/` Phase 1 手动流程是否可以完整跑通。它不是业务需求，而是一条 Tier 2+ 流程演练样例，用来证明 `/onion-plan`、完整 OpenSpec、Trellis adapter 恢复、`verify-change` 和 `/onion-finish` 能围绕同一组产物给出一致判断。

## What Changes

- 模拟一个 Tier 2+ 变更：为 Onion SDD 增加“流程健康检查”能力说明。
- 产出完整 OpenSpec 链路：
  - `proposal.md`
  - `specs/onion-sdd-flow-health/spec.md`
  - `tasks.md`
  - `backend-smoke.md`
  - `qa-smoke.md`
  - `e2e-report.md`
- 模拟 Trellis adapter 的恢复信息，验证 `meta.onion` 与 `.onion-sdd/current.json` 只保存引用和摘要，不复制正文。

## Impact

- 影响范围：仅用于 `onion-sdd` Phase 1 final flow validation。
- 不修改业务代码。
- 不修改 Trellis 源码、`.trellis/scripts/**` 或 `.trellis/.runtime/**`。
- 不实现 `/onion-auto`。

## 带债项

无。

