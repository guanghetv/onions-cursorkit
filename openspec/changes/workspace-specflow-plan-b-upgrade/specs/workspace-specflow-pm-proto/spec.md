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

### Requirement: `/pm-proto` 须先完成 brainstorming 门禁

系统 SHALL 在写入 `prototypes/` 或 `assets/` 之前，先 Read 并遵循 `superpowers:brainstorming`，完成灰区澄清并与用户确认执行模式及本轮变更单。

#### Scenario: 未获用户放行前禁止写入原型

- **WHEN** `/pm-proto` 尚未完成 brainstorming 或用户未明确确认执行模式与变更单
- **THEN** 系统不得写入或修改 `prototypes/`、`assets/` 下任何文件

#### Scenario: 须遵循一次一问澄清流程

- **WHEN** `/pm-proto` 进入 brainstorming 步骤
- **THEN** 系统遵循 brainstorming 技能的一次一问流程，不得用「先出一版原型」代替用户确认

### Requirement: `/pm-proto` 应优先最小化迭代成本

系统 SHALL 在原型已存在的场景下优先采用快速迭代策略，避免每轮重做整页。

#### Scenario: 原型已存在时默认快速迭代

- **WHEN** `prototypes/index.html` 已存在且本轮需求为局部调整
- **THEN** 系统默认进入快速迭代模式，仅处理受影响模块与必要上下文

#### Scenario: 全量重构需显式触发

- **WHEN** 需要改整体视觉基线或核心流程骨架
- **THEN** 系统在明确确认后才进入全量重构模式

### Requirement: 原型迭代应使用结构化变更单

系统 SHALL 在每轮原型迭代前输出并确认“保留/新增/删除/调整”变更单，作为唯一执行输入。

#### Scenario: 迭代前确认本轮变更单

- **WHEN** 进入增量迭代流程
- **THEN** 系统先确认本轮变更单，再执行原型更新

#### Scenario: 迭代后输出改动摘要

- **WHEN** 原型更新完成
- **THEN** 系统输出“本轮已改/本轮未改”摘要，降低误改风险

### Requirement: 原型视觉基线应首轮锁定

系统 SHALL 在首次原型生成并确认后锁定视觉与交互基线，后续迭代默认不改基线。

#### Scenario: 首轮确认后锁定基线

- **WHEN** 首次原型生成完成且用户确认可用
- **THEN** 系统锁定当前视觉与交互基线，后续迭代仅允许业务细节调整

#### Scenario: 改动基线需显式确认

- **WHEN** 后续迭代涉及整体风格或核心流程骨架变更
- **THEN** 系统在用户显式确认后才允许改动已锁定基线

### Requirement: 原型迭代应通过快速验收门

系统 SHALL 在每轮原型迭代结束时执行快速验收门，确认改动有效且可引用。

#### Scenario: 快速验收门检查项

- **WHEN** 原型迭代完成
- **THEN** 系统检查主路径可走通、受影响模块改动生效、关键锚点仍可引用、无明显视觉错位

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
