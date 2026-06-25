# 技术设计

## 定位

本任务是 Phase 1 父任务，不直接修改 `plugins/onion-sdd/` 或 `.trellis/scripts/`。它定义 Phase 1 的系统边界、子任务拆分和跨子任务验收，具体实现分别落到两个子任务：

- `.trellis/tasks/06-25-onion-sdd-base-capabilities`
- `.trellis/tasks/06-25-onion-sdd-trellis-adapter`

## 架构顺序

Phase 1 按两层推进：

```text
现网 fe-specflow 能力
  ↓ 迁移/通用化，不作为运行时依赖
onion-sdd 基座能力
  - /onion-plan 完整 SDD 路径
  - /onion-continue 产物恢复
  - /onion-finish 验收门禁
  - mini/light 轻量路径保留
  ↓ 状态同步
Trellis adapter
  - task metadata
  - journal
  - workflow-state 恢复
  - parent/child task tree
```

## 边界

- OpenSpec 仍是变更正文的唯一真相源；Trellis 只保存状态、路径引用、hash、journal 和恢复提示。
- `onion-sdd` 不能在用户可见流程中要求调用 `/fe-sdd` 或读取 `plugins/fe-specflow` 作为运行时依赖。
- 允许参考并迁移 `fe-specflow` 的成熟能力，但最终命名、模板和门禁必须是 onion 自有口径。
- Tier 0+/1 的轻量策略不能被 Tier 2+ 完整流程拖重。

## 子任务契约

### 1. 基座能力子任务

负责补齐流程能力。完成后，`onion-sdd` 应该能独立描述并执行：

- 多源需求接入与失败提示。
- Tier 2+ 的需求澄清与完整 OpenSpec 落盘。
- `tasks.md` 与 TDD 任务规划纪律。
- 后端/QA spec 接入与差异分析。
- E2E/验收报告与 finish 归档门禁。
- `/onion-continue` 通过 OpenSpec 产物恢复下一步。

该子任务不实现 Trellis adapter；可在文档中保留状态字段与同步预留。

### 2. Adapter 子任务

依赖基座能力子任务完成后的 onion 阶段模型和产物清单。负责定义并实现：

- `.onion-sdd/current.json` 到 `task.json.meta.onion` 的兼容映射。
- active change 与 Trellis active task 的恢复优先级。
- `last_action` 到 workspace journal 的写入策略。
- `source_hashes` 的计算范围。
- Tier 3 parent/child 到 Trellis task tree 的映射。

## 兼容性

- Phase 0 的 `mini-change` / `light-change` / `tier-triage` 必须继续可用。
- 已存在的 `.onion-sdd/current.json` 模板字段不能被破坏；新增字段应向后兼容。
- 试点隔离仍然保留；marketplace 分发不进入本 Phase 1 主线。

## 回滚

- 基座能力子任务主要修改插件 Markdown/规则/模板，可通过回滚 `plugins/onion-sdd/` 相关文件恢复。
- Adapter 子任务如果触碰 `.trellis/scripts/**`，必须保持小步提交和基础命令验证；失败时回退 adapter 入口，不影响 Phase 0 文件。
