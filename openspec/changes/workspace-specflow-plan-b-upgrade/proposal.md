## Why

`workspace-specflow` 目前在产研协作中仍存在三类核心问题：

1. 产品在 Cursor 与飞书之间双写 PRD，维护成本高且容易不一致。
2. `prd.md` 对人可读性不足，缺少重点标识、流程图、截图等阅读友好元素。
3. 原型生产与 PRD 结构化耦合在同一阶段，无法兼容“有原型 / 无原型”两类需求。

基于方案 B（`prd.md` + 可选 `prototypes/` 为真相源），需要先完成插件侧的核心升级：原型生成、原型反推 PRD、以及“对人可读”的 PRD 结构规范。飞书镜像同步不纳入本期范围。

## What Changes

- 新增 `workspace-specflow` 技能：`/pm-proto`
  - 用于快速产出或迭代原型资产（`prototypes/` 与 `assets/`）
  - 生成前扫描工作区前端上下文（样式规范、页面逻辑、核心交互）并进行脑暴澄清
  - 默认流程中先于 `/pm-spec` 执行，支持“先原型后 PRD”
  - 与 `/pm-spec` 解耦，避免职责混杂
- 升级 `/pm-spec`
  - 保持对飞书文档读取能力兼容，且优先使用 `lark-cli`
  - `lark-cli` 不可用时降级可用方案并提示建议安装
  - 输入冲突时默认本地 `prd.md` 为准
  - 增加 AI Review（高风险项 + 评分 + 改进建议），详细记录外置到 `prototypes/ai-review.md`
  - `prd.md` 仅保留 AI Review 可开工结论，不混入评分明细与改进建议
  - 保持 metadata 轻量，不新增复杂状态字段
  - 默认开启面向 WYSIWYG 的自适应富文本输出（适量使用 callout/checklist/mermaid/行内状态）
  - MODULE 标题统一为 `MODULE-N: <模块名> [新增/修改]`
  - 每个 MODULE 采用轻量 5 块结构（含可选边界/异常），引用优先“原型锚点 + 截图”
  - 无截图场景仅提示建议补充，不阻断 `/pm-spec` 完成
- 优化 `/req-new` 引导
  - 初始化后默认引导到 `/pm-proto`，不再默认要求先完善 `prd.md`
  - 不提示“飞书原文待补链”相关待办

## Capabilities

### New Capabilities

- `workspace-specflow-pm-proto`: 产品原型快速生成与迭代能力

### Modified Capabilities

- `workspace-specflow-pm-spec`: PRD 结构化与评审能力升级，兼容飞书读取并坚持本地优先

## Impact

- 影响目录：
  - `plugins/workspace-specflow/skills/req-new/`
  - `plugins/workspace-specflow/skills/pm-spec/`
  - `plugins/workspace-specflow/skills/pm-proto/`（新增）
- 对现有 `/req-new` 行为不引入额外显式开关，保持 PM 入口简单。
- `metadata.yaml` 不新增复杂状态机，仅保留最小字段与 `prd.status/test_spec.status`。
- 飞书镜像同步能力延期到后续迭代，本期只保留设计输入，不做实现承诺。
