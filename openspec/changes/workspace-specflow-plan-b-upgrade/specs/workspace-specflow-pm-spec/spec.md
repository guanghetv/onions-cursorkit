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

### Requirement: 本地优先冲突策略

系统 SHALL 在本地与飞书内容冲突时默认本地 `prd.md` 为准，并给出差异提示。

#### Scenario: 本地与飞书均有内容且不一致

- **WHEN** `/pm-spec` 检测到本地内容与飞书内容存在显著差异
- **THEN** 系统默认以本地为基准继续流程，并输出差异摘要供人工确认

### Requirement: 增加 PRD AI Review

系统 SHALL 在 `/pm-spec` 中加入 AI Review 环节，包含高风险检查、评分与可执行建议。

#### Scenario: 触发高风险阻断

- **WHEN** AI Review 命中高风险规则
- **THEN** 系统阻断直接 confirmed，并输出问题项与修复建议

#### Scenario: 输出评分与改进建议

- **WHEN** AI Review 完成
- **THEN** 系统生成 0-100 评分，以及最多 3 条高收益改进建议，并写入 `prototypes/ai-review.md`

#### Scenario: PRD 中仅保留评审结论

- **WHEN** AI Review 完成并回写 PRD
- **THEN** `prd.md` 仅保留“可开工结论（可开工 / 建议完善后开工 / 不可开工）”，不展示评分明细与改进建议正文

#### Scenario: 飞书原文待补链不计分

- **WHEN** 需求来源缺少飞书原文链接或待补链
- **THEN** 系统不将其纳入评分项与阻断项，不影响可开工结论判定

### Requirement: PRD 输出需具备高可读性

系统 SHALL 输出“阅读友好 + 结构清晰”的 PRD，避免大段文字堆叠。

#### Scenario: 富文本化输出约束

- **WHEN** `/pm-spec` 生成或增强 `prd.md`
- **THEN** 系统优先使用列表、表格、checklist、callout、流程图等块状结构，而非连续大段正文

#### Scenario: 默认启用自适应 WYSIWYG 友好标记

- **WHEN** `/pm-spec` 生成或增强 `prd.md`
- **THEN** 系统默认开启面向 WYSIWYG 的自适应标记策略：`[新增/修改]` 与验收 checklist 为必开，callout 与 Mermaid 按内容复杂度按需启用

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
  1) 需求描述
  2) 变更点
  3) 验收标准
  4) 模块特有边界与异常（可选）
  5) 引用

#### Scenario: 无原型引用时显式说明

- **WHEN** 某 MODULE 不包含原型引用
- **THEN** 在引用块中显式写明“无原型（原因）”

### Requirement: 轻量 metadata 约束

系统 SHALL 保持 metadata 轻量，不新增复杂评审状态机字段与开发关联字段。

#### Scenario: 执行 `/pm-spec` 后的 metadata 写入

- **WHEN** `/pm-spec` 完成并更新状态
- **THEN** 系统仅维护最小必要字段与 `prd.status/test_spec.status`，不写入复杂 review 结构
