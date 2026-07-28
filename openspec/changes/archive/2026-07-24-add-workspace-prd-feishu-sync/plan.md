# Workspace PRD ↔ 飞书同步与一致性校验 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在 `workspace-specflow` 落地独立 `/prd-feishu-sync`、`/prd-consistency-check`、`/prd-publish`，并挂到 req-new / pm-spec-5 / pm-spec / qa-spec，使飞书为人读面、9 稿 `prd.md` 为 Agent 契约准源且可门禁。

**Architecture:** 同步与校验解耦；publish 只编排。同步/增量/排版规程全部内化进 `prd-feishu-sync/SKILL.md`（四区 + CAS、MODULE 行级、图片 manifest、结论前置与局部回读），不外挂其它技能。契约层准源为本地 `prd.md`；讲解层（`narrative.*`）飞书独占；章节按语义 unit + 标题关键词定位（序号仅兼容）；9 稿瘦身不重排序号。


**Tech Stack:** Cursor skills/commands（Markdown）、`lark-cli`、可选 Python 发布脚本、`metadata.yaml` / manifest、OpenSpec change `add-workspace-prd-feishu-sync`。


**Spec 权威：** `openspec/changes/add-workspace-prd-feishu-sync/`（`proposal.md` / `design.md` / `specs/**` / `tasks.md`）

## Global Constraints

- 不同步改 `fe-specflow` / `be-specflow`（除非另开 change）
- 禁止默认飞书全文 `overwrite`；写前预览确认；写后回读
- `v9_synced=true` 后默认拒绝 v5 push，除非 `--force` + diff 确认
- 9 稿按语义去掉背景/价值正文，**不重排**关键关注/回归与四～七展示号
- `/dev-start` 已删除，计划中不得恢复
- lark-cli 失败不得伪造 check/sync pass
- 提交门禁：先完整 `/cr`（aicr-local），再 commit（本仓库规则）

## File Map

| 路径 | 职责 |
|---|---|
| `plugins/workspace-specflow/skills/prd-feishu-sync/**` | 自包含同步技能（+ 可选 chapter-map 附表） |
| `plugins/workspace-specflow/skills/prd-consistency-check/**` | 自包含一致性校验技能 |

| `plugins/workspace-specflow/skills/prd-publish/**` | sync→check 编排 |
| `plugins/workspace-specflow/commands/*.md` | 上述三命令入口 |
| `plugins/workspace-specflow/skills/req-new/**` | 末尾强制 create |
| `plugins/workspace-specflow/skills/pm-spec-5/**` | v5 sync 门控 |
| `plugins/workspace-specflow/skills/pm-spec/**` | 瘦身 + v9 sync + check 后 confirmed |
| `plugins/workspace-specflow/skills/qa-spec/**` | 启动前读 consistency |
| `plugins/workspace-specflow/skills/req-new/references/templates.md` | metadata 扩展 |
| `plugins/workspace-specflow/skills/pm-spec/references/prd-template.md` | 9 稿瘦身说明 |
| `plugins/workspace-specflow/rules/workspace-awareness.mdc` | 命令表（dev-start 已删，补新命令） |
| `plugins/workspace-specflow/README.md` | 产品/测试说明补 sync/check/publish |
| 可选 `plugins/workspace-specflow/skills/prd-feishu-sync/scripts/**` | 若移植发布器；首期可纯 Agent+lark-cli |

---

### Task 1: Metadata、9 稿模板、章节映射表

**Files:**
- Modify: `plugins/workspace-specflow/skills/req-new/references/templates.md`
- Modify: `plugins/workspace-specflow/skills/pm-spec/references/prd-template.md`
- Create: `plugins/workspace-specflow/skills/prd-feishu-sync/references/chapter-map.md`

**Produces:** `feishu.*` / `consistency.*` 字段形状；契约章节映射表（供 sync/check 共用）


- [x] **Step 1:** 在 `templates.md` 的 `metadata.yaml` 示例中增加设计文档中的 `feishu` / `consistency` 块；保留 `feishu_doc` 兼容注释「与 feishu.doc_url 同步」
- [x] **Step 2:** 在 `prd-template.md` 文首增加「9 稿确认后」规则：按语义无背景/价值实质正文；关键关注/回归与四～七**不改号**；原型锚点必留
- [x] **Step 3:** 写 `chapter-map.md`：表格列出本地 h2/h3 ↔ 飞书标题 ↔ sync unit key（含 MODULE-N）；标注讲解层「仅飞书、不进一致性」
- [x] **Step 4:** 自检：打开三文件，确认与 `specs/workspace-specflow-prd-template/spec.md` 场景一致
- [ ] **Step 5:** Commit（仅在用户要求且通过 `/cr` 后）

```text
feat(workspace-specflow): 扩展 metadata 与 9 稿瘦身模板及章节映射
```

---

### Task 2: `/prd-feishu-sync` 自包含技能

**Files:**
- Create: `plugins/workspace-specflow/skills/prd-feishu-sync/SKILL.md`
- Create: `plugins/workspace-specflow/commands/prd-feishu-sync.md`

**Consumes:** Task 1 `chapter-map.md`  
**Produces:** 可发现的 sync 命令；子命令路由；禁止 overwrite 的硬规则；排版/读写规程写在 SKILL 正文

- [x] **Step 1:** 将四区/CAS、module-row/manifest/图片、飞书排版与局部回读 **直接写入** `SKILL.md`（不维护外部「吸收清单」、不引用其它技能名）

- [x] **Step 2:** frontmatter + 意图路由：`create|push|pull|reconcile|status|rebind`；明确「不做一致性结论」
- [x] **Step 3:** 安全硬约束段：禁 overwrite；预览确认；精确 revision；讲解层/REVIEW 保护
- [x] **Step 4:** 写 `commands/prd-feishu-sync.md` 短入口
- [x] **Step 5:** 更新 `workspace-awareness.mdc` 与 `README.md` 命令表加入 `/prd-feishu-sync`（勿动 fe/be）

**验证：** 在对话中触发「同步 PRD 到飞书」描述能命中 skill；SKILL 含「禁止默认 overwrite」与排版规程原文，且无「见某某技能」类外挂引用。



---

### Task 3: `create` + 绑定 + 骨架

**Files:**
- Modify: `plugins/workspace-specflow/skills/prd-feishu-sync/SKILL.md`（create 流程，含四区布局正文）
- Modify: `plugins/workspace-specflow/skills/req-new/SKILL.md`（末尾必调 create）

**Consumes:** metadata 字段、chapter-map  
**Produces:** `/req-new` → 飞书文档 + token 绑定

- [x] **Step 1:** sync skill `create`：auth → `docs +create`（七章骨架+讲解占位+STATUS/REVIEW/PRD_BODY）→ 回写 `feishu.doc_*` / `feishu_doc` → `last_synced_stage=skeleton`
- [x] **Step 2:** `req-new` 目录创建成功后强制 `/prd-feishu-sync create`；失败明确报错，不假装已绑定
- [ ] **Step 3:** 试点：真机 `lark-cli` create（见 Task 9）
- [ ] **Step 4:** 试点验证：outline 可见骨架；metadata 有 token（见 Task 9）

---

### Task 4: `push` 增量、5/9 门控、可读性

**Files:**
- Modify: `prd-feishu-sync/SKILL.md`（门控、增量、manifest、排版均写在正文；**不**另建 `push.md` / `manifest-schema.md`）

**Produces:** 安全 push；v5/v9/`--force` 行为

- [x] **Step 1:** 5/9 门控伪代码写入 SKILL「安全硬约束」：

```text
if stage==v5 and metadata.feishu.v9_synced and not force:
  reject("9稿已同步，5稿默认不再推送；需要则 --force")
if stage==v5 and force:
  show_diff; STOP for confirm; last_synced_stage=force_v5
if stage==v9 and success:
  v9_synced=true
```

- [x] **Step 2:** 推送流程：fetch with-ids → chapter-map / MODULE 行 hash → 局部替换 → 图片与排版内建规程 → 禁动讲解层与 REVIEW
- [x] **Step 3:** 成功后更新 `last_synced_*`、`feishu_revision`、manifest（最小集，规程在 SKILL）
- [ ] **Step 4:** 真机验证清单（见 Task 9）：二次 push 后飞书背景/价值仍在；改一 MODULE 后仅该行变；无 force 的 v5 在 v9_synced 下被拒

---

### Task 5: `pull` / `reconcile` / `status` / `rebind`

**Files:**
- Modify: `prd-feishu-sync/SKILL.md`（规程写在正文；**不**另建 `reconcile.md`）

**Produces:** 飞书超前不静默写 md；status 可读

- [x] **Step 1:** `status`：绑定、v9_synced、last_synced、consistency、漂移摘要
- [x] **Step 2:** `reconcile`：三方对账 → STOP 确认 → 才写 md 契约；讲解层不进 md
- [x] **Step 3:** `rebind`：显式确认后改 token，重置 sync 标记并提示全量 push
- [ ] **Step 4:** 真机验证（见 Task 9）：未确认时改飞书契约，本地 prd.md 不被静默改写

---

### Task 6: `/prd-consistency-check`

**Files:**
- Create: `plugins/workspace-specflow/skills/prd-consistency-check/SKILL.md`（C/W 规则与报告字段均在正文；**不**另建 `rules.md` / 报告模板文件）
- Create: `plugins/workspace-specflow/commands/prd-consistency-check.md`

**Consumes:** chapter-map、feishu 绑定、prd.md  
**Produces:** 报告 + metadata.consistency + 飞书 callout

- [x] **Step 1:** SKILL 列出 C1–C7 / W1–W5；讲解层 diff → 不 fail
- [x] **Step 2:** 流程：阶段 → fetch → 结构 A → 语义 B → 落盘报告 → 更新 metadata → 回写飞书机器区
- [x] **Step 3:** 硬规则：命中触发词必须真跑，禁止口头清单
- [ ] **Step 4:** 真机验证（见 Task 9）：缺 token → fail；9 稿仍含讲解层背景/价值 → fail；仅飞书背景不同 → 非 critical

---

### Task 7: `/prd-publish` 编排

**Files:**
- Create: `plugins/workspace-specflow/skills/prd-publish/SKILL.md`
- Create: `plugins/workspace-specflow/commands/prd-publish.md`

**Consumes:** sync push、consistency-check  
**Produces:** 一键入口

- [x] **Step 1:** 流程：`auto` stage → sync push → 失败则停 → check → 汇总
- [ ] **Step 2:** 真机/人为验证：push 失败时不出现 check「通过」（见 Task 9）

---

### Task 8: 生命周期挂接（pm-spec-5 / pm-spec / qa-spec / T4）

**Files:**
- Modify: `plugins/workspace-specflow/skills/pm-spec-5/SKILL.md`
- Modify: `plugins/workspace-specflow/skills/pm-spec/SKILL.md`
- Modify: `plugins/workspace-specflow/skills/pm-spec/references/ai-review-rubric.md`（9 稿瘦身后锚点对齐概述/`3.3`/`3.4`）
- Modify: `plugins/workspace-specflow/skills/qa-spec/SKILL.md`
- Modify: `plugins/workspace-specflow/rules/workspace-awareness.mdc`
- Modify: `plugins/workspace-specflow/README.md`

**Produces:** 端到端流程挂接

- [x] **Step 1:** `pm-spec-5`：若 `!v9_synced` → push v5；若 `v9_synced` → 跳过并提示 force
- [x] **Step 2:** `pm-spec`：瘦身 → push v9 → check → critical 则禁止 confirmed；AI Review rubric 与瘦身一致
- [x] **Step 3:** `qa-spec`：读 `consistency.status`；fail 默认阻断
- [x] **Step 4:** T4：awareness / README / publish skill 写明确认后 commit 前须 `/prd-publish`（Agent 规程；本期无 husky）
- [x] **Step 5:** README：飞书讲解 vs 9 稿 Agent；新命令表；七章产品模板不废

---

### Task 9: 试点验收（真实飞书）

**Files:** 无新代码；产出试点笔记可写 `openspec/changes/add-workspace-prd-feishu-sync/pilot-notes.md`

**验证场景（对齐 proposal 验收）：**

- [ ] **Step 1:** `/req-new` → 飞书已创建、metadata 有 token
- [ ] **Step 2:** 5 稿多次 push 更新契约；讲解层不被清空
- [ ] **Step 3:** 9 稿 publish：本地无讲解层（背景/价值）正文、契约展示序号未重排、`v9_synced=true`
- [ ] **Step 4:** 再改 5 稿默认同步被拒；`--force` 需确认
- [ ] **Step 5:** 改飞书契约 → reconcile → 写 md → 再 check；飞书 callout 为最新结论
- [ ] **Step 6:** 未 sync 时提交/qa 路径出现阻断文案
- [ ] **Step 7:** 关联飞书项目 [7016921222](https://project.feishu.cn/ruxiao/tec_prd/detail/7016921222) 进度说明

---

## Spec Coverage（自检）

| Spec 能力 | 计划任务 |
|---|---|
| prd-feishu-sync（create/push/门控/对账/排版内建） | Task 2–5（规程已落 SKILL；真机见 Task 9） |
| prd-consistency-check | Task 6（规程已落；真机见 Task 9） |
| prd-publish | Task 7 |
| prd-template 瘦身不重排 + 9 稿 AI Review 对齐 | Task 1、8、9 |
| pm-spec / pm-spec-5 挂接 | Task 8 |
| 移除 dev-start | 已完成（勿回归） |

## 状态

- Task 1–8：**规程与挂接已完成**（自包含 SKILL，无拆分 references 外挂）
- Task 9：真机飞书试点待做
- Commit：用户要求且 `/cr` 通过后执行
