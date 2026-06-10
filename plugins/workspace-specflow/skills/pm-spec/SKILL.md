---
name: pm-spec
description: >-
  Use when user mentions: 产品spec/pm-spec/转换需求/增强prd/spec转换/结构化需求/PRD评审。
  Triggers when requirements directory exists and prd.md needs structuring/review.
---

# /pm-spec — prd.md 结构化增强与 AI Review

## 前置条件

- 需求目录已创建（`/req-new` 已执行）
- 目标目录存在 `prd.md` 与 `metadata.yaml`

## 核心原则

**prd.md 就是产品 spec**。不生成替代文件，只在现有 `prd.md` 上增强。

- 兼容飞书读取：本地空模板时允许从 `metadata.yaml.feishu_doc` 拉取并回填（`lark-cli` 优先，`feishu-mcp` 兜底）
- 本地优先：本地与飞书冲突时默认以本地 `prd.md` 为准
- 默认启用 WYSIWYG 友好输出（面向 `Markdown for Humans`）
- 输出可读：禁止大段文字，优先块状结构（列表/表格/checklist/callout/流程图）
- 富文本“适量”策略：`[新增/修改]` 与验收 checklist 必开；callout/mermaid 按需启用
- 结构稳定：MODULE 标题与块结构固定，便于开发和测试引用

## 流程

### Step 1: 定位需求 & 读取输入

扫描 `requirements/` 下目标需求，读取 `prd.md`：

- **prd.md 已有内容**：直接使用
- **prd.md 为空模板**：如存在 `metadata.yaml.feishu_doc`，按“`lark-cli` 优先、`feishu-mcp` 兜底”的顺序读取飞书文档回填本地；两者都不可用时提示建议安装 `lark-cli`
- **无飞书链接场景**：直接基于当前需求与原型信息增强 `prd.md`，不提示补链

若本地与飞书均有内容且差异明显：输出差异摘要，默认本地优先继续。

### Step 2: 读取原型与引用信息（可选）

若 `prototypes/` 存在原型文件，作为 PRD 增强输入。无原型需求可跳过。

若存在 `assets/` 截图，默认与原型锚点双轨引用；若暂无截图，仅提示建议补充关键截图，不阻断流程。

### Step 3: Brainstorming（需求澄清）

调用 `superpowers:brainstorming` 进行业务澄清：

- 澄清模糊点与边界
- 确认 MODULE 拆分
- 明确验收标准

### Step 4: 结构化增强 `prd.md`

在 `prd.md` 中输出“顶层阅读层 + MODULE 结构层”。模板见 `references/prd-template.md`。

MODULE 标题固定格式：

`MODULE-N: <模块名> [新增/修改]`

每个 MODULE 采用轻量 5 块：

1. 需求描述
2. 变更点
3. 验收标准
4. 模块特有边界与异常（可选）
5. 引用（无原型时写“无原型（原因）”）

### Step 5: AI Review

读取 `references/ai-review-rubric.md` 执行评审：

- 5 条高风险阻断规则
- 0-100 评分
- 最多 3 条高收益改进建议

若命中高风险项：阻断 confirmed，先修复后重跑。

评审结果落盘规则：

- 详细记录（评分、维度说明、改进建议）写入 `prototypes/ai-review.md`
- `prd.md` 仅保留 AI Review 可开工结论，不混入评分细节

### Step 6: 人工确认与状态更新

通过 review 后写入 `prd.md`，更新 `metadata.yaml.prd.status = confirmed`。

### Step 7: 提示下一步

测试同学 → `/qa-spec`；开发同学 → `/dev-start`（不需要等测试 spec）。

若本轮无截图，提示建议后续补充 `assets/` 关键截图以提升文档直观性（非阻断）。

## 约束

- 增强而非覆盖（决策 D30）
- 产品 spec 只描述需求本质，不涉及技术实现（决策 D6）
- MODULE ID 是稳定锚点（决策 D21）
- metadata 轻量：不新增复杂 review 状态与开发关联字段
