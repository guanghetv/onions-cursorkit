## 1. OpenSpec 与模板基础

- [x] 1.1 评审并通过 `proposal.md`、`design.md`、specs、本 tasks 清单
- [x] 1.2 新增 `plugins/workspace-specflow/skills/pm-spec/references/prd-template.md`（9稿：飞书一~七 + 3.3/3.4 + MODULE 映射）
- [x] 1.3 新增 `plugins/workspace-specflow/skills/pm-spec-5/references/prd-template-v5.md`（5稿：允许 `[待定]`，AI Review 结论措辞为交互评审系列）
- [x] 1.4 在模板中明确：不在文档顶部加元信息表；PM/日期走第二章版本表

## 2. AI Review Rubric

- [x] 2.1 更新 `ai-review-rubric.md`（9稿）：锚点迁移至 `### 3.3`/`### 3.4`、`## 一、需求概述`、`## 五、需求详情说明`；新增「禁止 `[待定]`」P0
- [x] 2.2 新增 `pm-spec-5/references/ai-review-rubric-v5.md`：放宽待定/验收/开放问题；结论为「可进入交互评审」系列；评审记录写 `ai-review-v5.md`
- [x] 2.3 9稿 rubric 保留 plan-b 九条 P0 体系，仅更新章节引用与 MODULE 位置描述

## 3. `/pm-spec-5` 技能（新增）

- [x] 3.1 新增 `plugins/workspace-specflow/skills/pm-spec-5/SKILL.md`
- [x] 3.2 新增 `plugins/workspace-specflow/commands/pm-spec-5.md`
- [x] 3.3 Step 1：飞书拉取按 h2 一~七映射；本地优先策略与 plan-b 一致
- [x] 3.4 Step 3：brainstorming 聚焦 MODULE 初拆、灰区、开放问题（一次一问）
- [x] 3.5 Step 4：按 `prd-template-v5.md` 结构化；第四章写 MODULE 列；第五章每 MODULE 一节 3 列表格
- [x] 3.6 Step 5：轻量 AI Review（`ai-review-rubric-v5.md`）
- [x] 3.7 Step 6：确认后 → 快照 `snapshots/prd-v5-<date>.md`；版本表追加 `5-n` 行；更新 `metadata.prd.v5` 与 `prd.stage`
- [x] 3.8 明确：确认后 `prd.md` 仍可由产品手工修改，不锁定

## 4. `/pm-spec` 升级为 9稿

- [x] 4.1 更新 `pm-spec/SKILL.md`：语义为 9稿定稿；Step 1 读取最新 v5 快照并输出 5→9 差异摘要
- [x] 4.2 更新 `commands/pm-spec.md` description 注明「9稿 / 交互评审后定稿」
- [x] 4.3 Step 3：brainstorming 聚焦消除待定项、确认交互结论
- [x] 4.4 Step 4：按 9稿 `prd-template.md` 输出；禁止残留 `[待定]`
- [x] 4.5 Step 6：确认后 → 快照 `snapshots/prd-v9-<date>.md`；版本表追加 `9-n` 行；`prd.status=confirmed`
- [x] 4.6 版本表规则：仅确认时追加行，日常 Agent 改写不追加（决策 A）

## 5. `/req-new` 初始化与中文目录命名

- [x] 5.1 更新 `req-new/references/templates.md`：`prd.md` 改为飞书七章空骨架；`metadata.yaml` 增加 `prd.stage/v5/v9`；`id` 注释改为「稳定英文 slug」
- [x] 5.2 更新 `req-new/SKILL.md`：目录名改为清洗后中文；`id` 生成 kebab-case slug；重名消歧 `-2`/`-MMDD`；废除 D14
- [x] 5.3 Step 3 用户确认时展示：中文目录名、`id` slug、`name`、模块，允许修正 `id`
- [x] 5.4 Agent 从飞书/一句话补齐骨架；`stage=v5_pending`；创建 `snapshots/.gitkeep`
- [x] 5.5 默认引导：`/req-new` → `/pm-proto`（可选）→ `/pm-spec-5`

## 5b. 中文目录命名配套

- [x] 5b.1 更新 `req-status/SKILL.md`：列表显示 `name（id: <slug>）` 或中文目录名
- [x] 5b.2 更新 `dev-start/SKILL.md`：需求选择列表优先中文目录名 + `id`
- [x] 5b.3 更新 `workspace-awareness.mdc`：废除 kebab-case 目录约束，写明中文目录 + slug 规则
- [x] 5b.4 更新 `README.md`：目录结构示例改为 `requirements/订单退款流程优化/`

## 6. 进度与文档

- [x] 6.1 更新 `req-status/SKILL.md`：展示 PRD 5稿/9稿 双状态与快照路径（与 5b.1 合并执行）
- [x] 6.2 更新 `README.md` 产品流程段：5稿→交互评审→9稿
- [x] 6.3 更新 `rules/workspace-awareness.mdc`：命令表增加 `/pm-spec-5`；流程阶段更新（与 5b.3 合并执行）
- [x] 6.4 更新 `pm-proto` 下一步引导为 `/pm-spec-5` → `/pm-spec`

## 7. 验证（实现后）

- [ ] 7.1 用飞书模板 URL 跑通 `/req-new` → `/pm-spec-5`：检查章节映射与 v5 快照
- [ ] 7.2 手工改 `prd.md` 后跑 `/pm-spec`：检查 5→9 diff、待定消除、v9 快照、`prd.status=confirmed`
- [ ] 7.3 确认 `/qa-spec`、`/dev-start` 在 9稿 confirmed 前仍被门禁阻断
- [ ] 7.4 确认版本表仅在两次确认各追加一行，中间改写不追加
- [ ] 7.5 验证 `/req-new` 中文目录创建与重名消歧（`-2` 后缀）
- [ ] 7.6 验证 `req-status` / `dev-start` 列表可正确显示中文目录名与 `id` slug
