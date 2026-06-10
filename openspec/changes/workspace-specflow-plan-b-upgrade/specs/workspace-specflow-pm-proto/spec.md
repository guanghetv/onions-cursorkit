# Workspace Specflow PM Proto

## ADDED Requirements

### Requirement: 提供独立的 `/pm-proto` 原型生产能力

系统 SHALL 提供独立于 `/pm-spec` 的原型生产技能 `/pm-proto`，用于快速生成或迭代 `prototypes/` 资产。

#### Scenario: 从空白生成原型骨架

- **WHEN** 用户在需求目录执行 `/pm-proto` 且不存在可用原型文件
- **THEN** 系统生成 `prototypes/index.html` 的基础骨架

#### Scenario: 增量更新已有原型

- **WHEN** 用户在已有 `prototypes/index.html` 的需求目录执行 `/pm-proto`
- **THEN** 系统在不破坏已有结构的前提下进行增量修改

### Requirement: `/pm-proto` 生成前必须进行工作区扫描与脑暴澄清

系统 SHALL 在原型生成前先扫描当前工作区可复用上下文，并执行脑暴澄清，减少返工并提升原型一致性。

#### Scenario: 扫描工作区前端项目与需求上下文

- **WHEN** 用户执行 `/pm-proto`
- **THEN** 系统优先扫描 `workspace-repos.json`、需求目录上下文（`prd.md`、`prototypes/`、`assets/`）以及可访问前端项目中的样式规范、页面逻辑与核心交互

#### Scenario: 原型生成前执行需求与交互脑暴

- **WHEN** 工作区扫描完成且准备生成原型
- **THEN** 系统先进行需求与交互澄清（页面目标、关键路径、异常场景、复用与改动范围），再进入原型生成

### Requirement: `/pm-proto` 不应修改 PRD 状态

系统 SHALL 确保 `/pm-proto` 只处理原型资产，不修改 `prd.status` 或触发确认流程。

#### Scenario: 原型更新后状态保持

- **WHEN** `/pm-proto` 完成原型生成或修改
- **THEN** `metadata.yaml` 中 `prd.status` 保持原值不变

### Requirement: 支持可选视觉辅助资产

系统 SHALL 允许 `/pm-proto` 产出与原型相关的可选视觉辅助资产（如截图、流程图文件）供 PRD 引用。

#### Scenario: 生成流程图或截图资产

- **WHEN** 用户要求补充流程或关键页面示意
- **THEN** 系统可在 `assets/` 下生成可引用文件，并给出引用路径

#### Scenario: 未生成截图时的处理

- **WHEN** `/pm-proto` 完成原型生成但未产出截图
- **THEN** 系统提示“建议补充关键截图以提升 PRD 可读性”，但不阻断后续 `/pm-spec`
