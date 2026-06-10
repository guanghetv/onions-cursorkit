---
name: pm-spec
description: >-
  Use when user mentions: 产品spec/pm-spec/转换需求/增强prd/spec转换/结构化需求/PRD评审。
  Triggers when requirements directory exists and prd.md needs structuring/review.
---

# /pm-spec — prd.md 结构化增强与 AI Review

<HARD-GATE>
在 Step 3 Brainstorming 完成且用户**明确确认**需求拆分与关键决策之前，**禁止**：

- 写入或大幅改写 `prd.md` 的结构化内容（Step 4）
- 执行 AI Review 并更新 `metadata.yaml.prd.status`（Step 5–6）
- 以「prd 已有内容 / 飞书已拉取」为由跳过澄清

「扫了一眼 prd」≠ 已完成 brainstorming——必须 **Read 并遵循** `superpowers:brainstorming` 的 SKILL.md 全流程。
</HARD-GATE>

## 前置条件

- 需求目录已创建（`/req-new` 已执行）
- 目标目录存在 `prd.md` 与 `metadata.yaml`

## 核心原则

**prd.md 就是产品 spec**。不生成替代文件，只在现有 `prd.md` 上增强。

- 兼容飞书读取：本地空模板时允许从 `metadata.yaml.feishu_doc` 拉取并回填（`lark-cli` 优先，`feishu-mcp` 兜底）
- 条件化优先：若本地 `prd.md` 已有实质内容，与飞书冲突时默认以本地为准；若 `prd.md` 为空模板，则以飞书文档为主并回填生成标准 PRD
- 默认启用 WYSIWYG 友好输出（面向 `Markdown for Humans`），并作为 `confirmed` 前置质量门禁
- 输出可读：严格禁止大段文字；连续正文超过 6 行判定为违规，且即便未超 6 行但可读性差也可判定违规
- 富文本“适量且必须”：每份 PRD 至少包含 1 个非 AI 区块的重点关注模块（callout）；验收 checklist 必开；`[新增/修改]` 必开；callout/mermaid 按规则触发，避免滥用
- 复杂流程强制图示：存在分支逻辑，或流程步骤 >= 5 时，必须提供 Mermaid 流程图
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

### Step 3: Brainstorming（需求澄清）【阻断步骤】

**REQUIRED SUB-SKILL:** 先 Read `superpowers:brainstorming` 的 SKILL.md（可用 Glob `**/superpowers/**/brainstorming/SKILL.md` 定位），并**完整遵循**其流程；不得跳过、不得缩略为「内部推断」。

与产品同学澄清（遵循 brainstorming **一次一问**）：

- 澄清模糊点、边界与灰区（必须向用户确认，不得默认假设）
- 确认 MODULE 拆分
- 明确验收标准
- 确认 `开发速览` 中的**需求类型**（新增 / 迭代）与**影响范围**（页面 / 模块 / 流程）；未填写则在此步补齐
- **迭代需求**：确认**本轮变更 MODULE 清单**（如 `MODULE-2, MODULE-3`），供 Step 5 聚焦评审；可对照 `关键变更摘要` 核对
- 确认**回归范围**：哪些既有页面/流程/MODULE 需回归验证；哪些明确不纳入及原因（禁止含糊写「无回归」）

产出澄清摘要并**等待用户确认**后，方可进入 Step 4。用户用自然语言确认（如「可以」「按这个来」「继续写 PRD」）即视为放行。

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

必须新增以下顶层固定块，不得仅在 AI Review 区块体现：

- **关键关注（必填）**（1~3 条）：本需求最重要风险或变更点
- **回归范围（必填）**：需回归项 + 不纳入本次回归的范围与原因；禁止仅写「无回归」

### Step 5: AI Review

读取 `references/ai-review-rubric.md` 执行评审：

1. **确定评审范围**：按 `开发速览.需求类型`（新增=全量 / 迭代=按 Step 3「本轮变更 MODULE 清单」聚焦深审）；MODULE `[新增/修改]` 只标记本次变更内容，不决定评审范围
2. **深审透镜**：对深审 MODULE 检查内容质量、可读性、用户场景（目标用户 / 核心场景 / 边缘异常）
3. **P0 阻断**：命中任一条 P0 规则则阻断 confirmed
4. **P1/P2 建议**：P0/P1 全量列出且每条须含位置锚点、建议与可粘贴示例；P2 最多 3 条
5. **0-100 评分**：五维评分写入 `ai-review.md`

评审结果落盘规则：

- 详细记录（评审范围、评分、定位问题项、改进建议）写入 `prototypes/ai-review.md`
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
