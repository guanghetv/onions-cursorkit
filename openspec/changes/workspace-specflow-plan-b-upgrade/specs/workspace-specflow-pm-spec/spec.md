# Workspace Specflow PM Spec Upgrade

## MODIFIED Requirements

### Requirement: `/pm-spec` 保持飞书读取兼容

系统 SHALL 保持 `/pm-spec` 对飞书文档读取能力的兼容，不破坏已有以飞书为输入的使用方式。

#### Scenario: 飞书读取优先使用 lark-cli

- **WHEN** `/pm-spec` 需要读取飞书文档
- **THEN** 系统优先使用 `lark-cli` 获取内容

#### Scenario: lark-cli 不可用时的降级与提示

- **WHEN** 环境未安装或不可用 `lark-cli`
- **THEN** 系统降级到可用的飞书读取方式（如 feishu-mcp），并明确提示“建议安装 `lark-cli` 以获得稳定的一致体验”

#### Scenario: 本地 PRD 为空时从飞书回填

- **WHEN** `prd.md` 为空或仅模板内容，且存在可用飞书链接
- **THEN** 系统读取飞书文档内容并回填到本地 `prd.md`

### Requirement: 条件化优先冲突策略

系统 SHALL 采用条件化优先策略：本地 `prd.md` 有实质内容时本地优先；本地为空模板时以飞书文档为主并回填标准 PRD。

#### Scenario: 本地与飞书均有内容且不一致

- **WHEN** `/pm-spec` 检测到本地内容与飞书内容存在显著差异
- **THEN** 系统默认以本地为基准继续流程，并输出差异摘要供人工确认

#### Scenario: 本地为空模板且存在飞书输入

- **WHEN** `prd.md` 为空模板，且存在可用飞书链接
- **THEN** 系统以飞书文档内容为主回填生成标准 PRD，而不是继续沿用空模板

### Requirement: `/pm-spec` 须先完成 brainstorming 门禁

系统 SHALL 在结构化改写 `prd.md` 或执行 AI Review 之前，先 Read 并遵循 `superpowers:brainstorming`，完成灰区澄清并与用户确认 MODULE 拆分、需求类型及（迭代时）本轮变更 MODULE 清单。

#### Scenario: 未获用户放行前禁止改写 PRD

- **WHEN** `/pm-spec` 尚未完成 brainstorming 或用户未明确确认关键决策
- **THEN** 系统不得结构化改写 `prd.md`，不得执行 AI Review 或更新 `prd.status`

#### Scenario: 不得因已有内容跳过澄清

- **WHEN** 本地 `prd.md` 或飞书文档已有实质内容
- **THEN** 系统仍须完成 brainstorming 与用户确认，不得直接假定内容完整并跳过澄清

#### Scenario: 须遵循一次一问澄清流程

- **WHEN** `/pm-spec` 进入 brainstorming 步骤
- **THEN** 系统遵循 brainstorming 技能的一次一问流程，不得用「先出一版 PRD」代替用户确认

### Requirement: 增加 PRD AI Review

系统 SHALL 在 `/pm-spec` 中加入 AI Review 环节，包含 P0 阻断、五维评分与可定位改进建议。

#### Scenario: 触发 P0 阻断

- **WHEN** AI Review 命中任一条 P0 规则（共 9 条：内容质量 5 + 可读性结构 3 + 用户场景 1）
- **THEN** 系统阻断直接 confirmed，并输出带位置锚点的问题项与修复建议

#### Scenario: 按需求类型确定评审范围

- **WHEN** `开发速览.需求类型` 为新增
- **THEN** 系统对所有 MODULE、全局背景与关键关注执行全量深审

#### Scenario: 迭代需求聚焦深审

- **WHEN** `开发速览.需求类型` 为迭代，且 Step 3 已确认本轮变更 MODULE 清单
- **THEN** 系统仅对清单内 MODULE 与关键关注深审；PRD 中其他 MODULE 仅做一致性轻审

#### Scenario: 迭代需求缺少变更清单时降级

- **WHEN** 需求类型为迭代，但 Step 3 未确认清单且关键变更摘要也无法推断 MODULE
- **THEN** 系统降级为全量深审，并在 `ai-review.md` 注明原因

#### Scenario: 输出评分与分层建议

- **WHEN** AI Review 完成
- **THEN** 系统生成 0-100 五维评分（目标与用户场景 25、范围与边界 20、MODULE 结构 20、验收可测试性 20、可读性与引用 15），P0/P1 问题项全量写入 `prototypes/ai-review.md`，P2 优化建议最多 3 条

#### Scenario: 问题项须可定位可改写

- **WHEN** AI Review 输出 P0 或 P1 问题项
- **THEN** 每条须包含位置锚点（`MODULE-N / 块名` 或章节名）、类别标签（用户场景/功能逻辑/边界范围/可读性/原型展示）、具体建议与可粘贴示例（一段可直接贴回 `prd.md` 的改写片段）

#### Scenario: PRD 中仅保留评审结论

- **WHEN** AI Review 完成并回写 PRD
- **THEN** `prd.md` 仅保留“可开工结论（可开工 / 建议完善后开工 / 不可开工）”，不展示评分明细与改进建议正文

#### Scenario: 飞书原文待补链不计分

- **WHEN** 需求来源缺少飞书原文链接或待补链
- **THEN** 系统不将其纳入评分项与阻断项，不影响可开工结论判定

### Requirement: PRD 输出需具备高可读性（强规则门禁）

系统 SHALL 输出“阅读友好 + 结构清晰”的 PRD，并将可读性作为 `confirmed` 前置质量门禁。

#### Scenario: 严格禁止大段文字

- **WHEN** `/pm-spec` 生成或增强 `prd.md`
- **THEN** 系统禁止连续正文超过 6 行；虽未超 6 行但主观可读性差同样判定违规并阻断 confirmed

#### Scenario: 必须包含非 AI 区块的重点关注模块

- **WHEN** `/pm-spec` 完成结构化增强
- **THEN** 系统输出 `## 关键关注（必填）` 区块（1~3 条 callout），且重点信息不得仅出现在 AI Review 结论区

#### Scenario: 必须包含回归范围且表述无歧义

- **WHEN** `/pm-spec` 完成结构化增强
- **THEN** 系统输出 `## 回归范围（必填）` 区块，写明需回归项或不纳入本次回归的范围与原因；禁止仅写「无回归」等歧义表述

#### Scenario: 默认启用 WYSIWYG 友好标记且适量使用

- **WHEN** `/pm-spec` 生成或增强 `prd.md`
- **THEN** 系统默认开启面向 WYSIWYG 的标记策略：`[新增/修改]` 与验收 checklist 必开；callout 适量使用，禁止无意义堆叠

#### Scenario: 复杂流程强制 Mermaid

- **WHEN** 需求存在分支逻辑，或流程步骤 >= 5
- **THEN** 系统必须提供 Mermaid 流程图；缺失则阻断 confirmed

#### Scenario: 迭代需求模块级影响时 Mermaid 可局部表达

- **WHEN** 需求类型为迭代、`影响范围` 为模块，且复杂流程仅涉及本轮变更 MODULE
- **THEN** 系统允许在变更 MODULE 内提供局部 Mermaid 图示，不要求重画全局主流程图

#### Scenario: 顶层摘要可选但简洁

- **WHEN** PRD 包含“关键变更摘要”
- **THEN** 系统输出简洁摘要；如无必要可省略该节并直接进入 MODULE 详情

### Requirement: 原型与截图双轨引用（截图非阻断）

系统 SHALL 在有原型场景下优先输出“原型锚点 + 截图”双轨引用，并在截图缺失时采用非阻断提示。

#### Scenario: 同时输出原型锚点与截图引用

- **WHEN** 需求存在原型且有可用截图
- **THEN** 系统在 MODULE 引用中同时输出 `prototypes/index.html#module-x` 与 `assets/module-x.png`

#### Scenario: 无截图时仅提示建议

- **WHEN** 需求存在原型但暂无截图
- **THEN** 系统提示建议补充关键截图以提升可读性，但不阻断 `/pm-spec` 完成

### Requirement: MODULE 结构轻量且统一

系统 SHALL 使用轻量 MODULE 模板，兼容“有原型 / 无原型”两类需求。

#### Scenario: MODULE 标题规范

- **WHEN** 生成 MODULE 标题
- **THEN** 使用 `MODULE-N: <模块名> [新增/修改]` 格式，不附加优先级字段

#### Scenario: MODULE 固定块结构

- **WHEN** 生成单个 MODULE 内容
- **THEN** 包含以下块：
  1) 需求描述（含目标用户、核心场景、边缘/异常场景）
  2) 变更点
  3) 验收标准
  4) 模块特有边界与异常（可选）
  5) 引用

#### Scenario: 深审 MODULE 须覆盖用户场景

- **WHEN** AI Review 深审某 MODULE
- **THEN** 其需求描述须包含目标用户（一句话）、核心场景（主路径）与边缘/异常场景（业务需要时）；完全缺失目标用户与场景则 P0 阻断

#### Scenario: MODULE 标签不决定评审范围

- **WHEN** MODULE 标题带 `[新增/修改]`
- **THEN** 该标签仅表示本次 PRD 变更内容；迭代需求的评审范围由 `开发速览.需求类型` 与 Step 3 本轮变更 MODULE 清单决定

#### Scenario: 无原型引用时显式说明

- **WHEN** 某 MODULE 不包含原型引用
- **THEN** 在引用块中显式写明“无原型（原因）”

### Requirement: 轻量 metadata 约束

系统 SHALL 保持 metadata 轻量，不新增复杂评审状态机字段与开发关联字段。

#### Scenario: 执行 `/pm-spec` 后的 metadata 写入

- **WHEN** `/pm-spec` 完成并更新状态
- **THEN** 系统仅维护最小必要字段与 `prd.status/test_spec.status`，不写入复杂 review 结构
