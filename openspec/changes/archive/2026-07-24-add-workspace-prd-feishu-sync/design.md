# Design: add-workspace-prd-feishu-sync

## Context

方案 B（`prd.md` + `prototypes/` 为执行真相源）已落地原型与 PRD 可读性能力，但飞书同步延期。产品调研结论：人仍在飞书评审/讲解，Agent 消费 9 稿；需补齐「绑定 + 自动同步 + 一致性门禁」。

模式：多触发出口门 + 结果回写飞书机器区；契约层准源为 **本地 `prd.md`**，飞书为人读演示面。同步/排版/校验规程分别自包含于三个技能正文。


## Goals / Non-Goals

**Goals**

- 独立 `/prd-feishu-sync` + `/prd-consistency-check` + `/prd-publish` 编排
- `/req-new` 即 `lark-cli` 创建飞书文档并深度绑定
- 5/9 同步策略与 `v9_synced` 门控
- 9 稿本地瘦身（按语义删背景/价值）；原型保留；飞书七章产品模板不变
- 契约层一致性 A（结构）+ B（语义）；最新结果展示在飞书
- 9 稿确认后、提交前 **Agent 规程门禁**（须已 sync + check 非 fail；**本期无 git hook**，后续可加 husky）


**Non-Goals**

- 不修改飞书官方七章产品模板
- 不实现五交付物全量门禁 / 看板字段同步

- 不做评论自动回收 MR、需求导航 Base
- 不把飞书设为 Agent 准源

## Decisions

### 1. 方案 1 + 方案 2 结合

- **同步技能单独封装**（`/prd-feishu-sync`），校验独立（`/prd-consistency-check`）
- **`/prd-publish`** 仅编排 `sync → check`，不内嵌同步实现

### 2. 文档分层与序号策略

| 层 | 飞书 | 9 稿 `prd.md` |
|---|---|---|
| 讲解层（`narrative.background` / `value`，标题含背景/价值） | 有 | **整节删除** |
| 契约层（概述、版本、关键关注、回归、Feature、MODULE、验收等） | 有 | **权威** |
| 原型 | 链接说明 | `prototypes/` + 锚点（必留） |

一致性校验 **只覆盖契约层**。章节定位：**语义 unit key + 标题关键词优先，序号仅兼容**（`chapter-map.md`）。

**展示序号：不重排（定稿）**

- 飞书可继续用产品七章默认编号；同步/校验 **不依赖**写死 `3.1`/`3.2`。
- 本地 9 稿瘦身：按语义删讲解层；**不把**「关键关注/回归」改成更小展示号、**不把**四～七前移。
- 「为什么做」收敛到「需求概述」；「背景和价值」下直接接关键关注 / 回归。


### 3. 绑定模型（`metadata.yaml`）

```yaml
feishu_doc: <url>  # 兼容旧字段
feishu:
  doc_url: ...
  doc_token: ...
  created_at: ...
  last_synced_at: ...
  last_synced_stage: skeleton | v5 | v9 | reconcile | force_v5
  last_synced_commit: ...
  feishu_revision: ...
  v9_synced: false
  narrative_owned_by: feishu
consistency:
  status: unknown | pass | warn | fail
  checked_at: ...
  report_path: ...
  source_commit: ...
```

一需求一文档；换链须 `rebind`。

### 4. `/prd-feishu-sync` 子命令（规程内化于技能正文）

实现物为自包含技能：`plugins/workspace-specflow/skills/prd-feishu-sync/SKILL.md`。  
设计来源（CAS/受管区、module-row/图片、飞书排版局部写）的可操作规则 **已写入该 SKILL 正文**，运行时不依赖、不引用外部技能名。

技能内建能力要点：

- 契约准源本地 `prd.md`；四区 STATUS / REVIEW / PRD_BODY / CONSISTENCY（含「⏳ 未校验」占位）；禁默认 overwrite；精确 revision；预览确认

- MODULE 行级增量 + manifest；图片 Drive 文件夹 + `file_token`；临时同步稿默认不回写正式 prd
- 飞书排版：结论前置、表/callout/画板、去大段、改前 fetch / 改后回读；`--as user`
- 讲解层（`narrative.*`）不覆盖飞书已有正文；5/9 门控与 `v9_synced`

| 命令 | 行为 |
|---|---|
| `create` | `/req-new` 必调；创建飞书骨架（含四区 marker，含未校验占位）；写绑定 |

| `push` | 仅受管契约区 md→飞书；增量；内建排版与图片规程 |
| `pull` / `reconcile` | 三方对账，确认后写 md |
| `status` | 绑定、基线、漂移 |
| `rebind` | 显式换文档 |

**5/9 门控**：`v9_synced=true` 且 `push --stage v5` 无 `--force` → 拒绝；`--force` 须 diff 确认。`push --stage v9` 成功后 `v9_synced=true`。

### 5. 一致性校验 A+B

- **Critical**：绑定、结构对齐、MODULE 骨架、Feature↔MODULE、9 稿无讲解层回流、进开发前语义 B、T4 双条件
- **Warning**：评审前语义 B、可读性、新鲜度、原型建议、讲解层空壳
- 报告：`requirements/<id>/prototypes/prd-consistency-check-YYYY-MM-DD.md`
- 飞书底部机器 callout：校验结果 / 报告链接 / commit / 已跳过项（每次覆盖为最新）

### 6. 触发时机

1. PM 主动（禁止口头清单）
2. `/prd-publish` 第二步
3. `/pm-spec` 9 稿确认收口前
4. **git commit/push 前（Agent 规程）**：协助提交时须已 sync + check 非 fail；本期无仓库 hook 硬拦

5. 评审后 sync/reconcile 后再 check
6. `/qa-spec` 前读 `consistency.status`（开发侧由代码仓库流程读 confirmed `prd.md`，不再经 `/dev-start`）

### 7. 模板兼容

- 飞书创建与讲解仍用七章产品模板
- 仅收敛工作区 **9 稿** `prd.md` 契约子集
- 5 稿本地可仍含背景；9 稿确认时按语义从 md 移除 `narrative.*`（讲解保留在飞书）

## Architecture

```text
/req-new → sync create → 飞书骨架 + 绑定
/pm-spec-5 → (若 !v9_synced) sync push v5
/pm-spec → 瘦身 9 稿 → sync push v9 → v9_synced
/prd-publish → sync → check → 回写飞书结果
评审：改 md→push；改飞书契约→reconcile→push；只改讲解→不写 md
T4：未 sync 或 check fail → Agent 协助提交时阻断（无 hook 时裸 commit 可绕过）
下游 Agent：只读 9 稿契约 + 原型
```

## Risks / Trade-offs

| 风险 | 缓解 |
|---|---|
| 产品只改飞书不改 md | reconcile + T4/进开发前对未回收漂移 critical |
| 整篇 overwrite 丢评论/讲解 | push 仅契约映射块；禁静默全量覆盖讲解层 |
| force_v5 用旧稿盖飞书 | diff + STOP 确认 + warning 留痕 |
| 语义 B 误判 | 列 MODULE 差异由 PM 裁决；评审前可为 warning |
| lark-cli 不可用 | 失败显式；不伪造 pass |
| T4 无 hook 被绕过 | 介绍文档明示边界；后续评估 pre-commit/pre-push |


## Migration Plan

1. 落地三技能 + commands + metadata 模板扩展
2. 挂接 req-new / pm-spec-5 / pm-spec / awareness / README
3. 调整 9 稿模板与 C6 瘦身规则
4. 试点 1～2 个需求跑通 create→v5→v9→publish→T4
5. 再评估 hook 形态（Agent 规程 vs husky）

## Open Questions

1. T4 落点优先 pre-commit 还是 pre-push（实现期按仓库 hook 现状二选一）
2. 契约章节映射表是否与飞书标题文案强绑定（实现期固化一张映射表）
