# add-workspace-prd-feishu-sync

## Why

方案 B 已将 Git `prd.md` + `prototypes/` 定为产研执行真相源，但「飞书镜像同步」在上一期明确延期。现场反馈显示：

1. 正式 Review / 讲解仍在飞书；设计与开发在飞书评论标注。
2. 产品多已用工作区产出 PRD，却靠人工或旧整段覆盖工具同步，存在过期飞书稿与双写成本。
3. Agent / `/qa-spec` / 代码仓库开发流程消费 9 稿 `prd.md`，需要与飞书契约层严格一致，且提交前可门禁。

本变更补齐方案 B 缺失环：独立同步技能 + 一致性校验门 + 一键编排，并在 `/req-new` 即用 `lark-cli` 创建飞书文档。

飞书项目：[产研spec流程优化--飞书文档自动更新方案调研及实现](https://project.feishu.cn/ruxiao/tec_prd/detail/7016921222)

## What Changes

- 新增独立技能 **`/prd-feishu-sync`**（单独封装，只做同步；规程自包含，不外挂其它技能名）
  - 内建：四区 marker（含 CONSISTENCY「⏳ 未校验」）、精确 revision、对账、禁 overwrite、MODULE 行级增量、图片 manifest、飞书排版（结论前置/表/callout/画板）与改前 fetch / 改后回读

  - `create`：`/req-new` 末尾必调，`lark-cli` 创建飞书文档并深度绑定
  - `push` / `pull|reconcile` / `status` / `rebind`
  - 契约层 md→飞书；讲解层（`narrative.*`，标题含背景/价值）飞书独占，push 不覆盖
  - **5/9 门控**：`v9_synced=true` 后默认不再同步 5 稿，除非 `--force`
- **9 稿瘦身不重排序号**：按语义删本地背景/价值整节，保留关键关注/回归与四～七展示号（unit key 对齐，禁止只靠序号）
- 新增 **`/prd-consistency-check`**（出口门；范围收窄到契约层）
  - 契约层结构 A（critical）+ 语义 B（评审前 warning / 进开发前 critical）
  - 多触发：主动、publish、9 稿确认、**提交前 Agent 规程（本期无 git hook）**、评审后再检、`/qa-spec` 前

- **移除** 已闲置的 `/dev-start`（技能与命令）；开发改由代码仓库 SDD 直接读 confirmed `prd.md`
  - 最新结果回写飞书底部机器 callout + 本地报告
- 新增 **`/prd-publish`**：编排 `sync → check` 的一键入口（方案 1+2 结合）
- 挂接生命周期：`/req-new`、`/pm-spec-5`、`/pm-spec` 按门控调用 sync
- **9 稿瘦身**：本地 `prd.md` 确认 9 稿后不含讲解层（背景/价值）；**不修改**飞书七章产品模板；原型与锚点保留
- 扩展 `metadata.yaml`：`feishu.*` 绑定与 `consistency.*` 状态（保持可解释、非复杂状态机）


## Capabilities

### New Capabilities

- `workspace-specflow-prd-feishu-sync`：飞书文档创建、契约同步、回收对账与 5/9 门控
- `workspace-specflow-prd-consistency-check`：契约层一致性校验与结果回写
- `workspace-specflow-prd-publish`：sync + check 一键编排

### Modified Capabilities

- `workspace-specflow-prd-template`：9 稿本地契约子集（讲解层迁出）
- `workspace-specflow-pm-spec`：9 稿确认后必 sync；收口前可挂 check
- `workspace-specflow-pm-spec-5`：未 `v9_synced` 时 sync；已同步则默认跳过

## Impact

- 目录：`plugins/workspace-specflow/skills/`、`commands/`、`rules/workspace-awareness.mdc`、`README.md`
- 依赖：`lark-cli`（必选路径）；不可用时同步失败且不得伪造 check pass
- 兼容：存量需求首次 sync 时补绑定；旧全七章 `prd.md` 在升 9 稿时迁出讲解层
- 不搬全量交付物门禁 / 看板三字段；同步与排版规则以本插件技能正文为准

## 不做范围


- 飞书项目 Base「需求导航」整页
- 飞书评论自动变 MR
- Codex→Cursor 迁移、双仓搬运本身
- 以飞书正文为 Agent 唯一准源（本期契约层准源仍为本地 9 稿 `prd.md`）
- 不恢复 `/dev-start`；开发入口以代码仓库 SDD 为准

## 验收

- `/req-new` 后 metadata 含可用 `feishu.doc_token`，飞书文档已创建
- 5 稿更新可 sync；9 稿 sync 后 5 稿默认同步被拒绝，`--force` 需确认
- 9 稿 md 无讲解层（背景/价值）；飞书仍可有背景；契约 MODULE A+B 一致；章节按语义定位
- check 结果出现在飞书 CONSISTENCY 区（未跑为「⏳ 未校验」）；走 `/pm-spec`/`/qa-spec`/`/prd-publish` 时 T4/开工路径可阻断；裸 commit 本期无 hook
- `/prd-publish` 一次完成 sync+check


## References

- 方案 wiki：https://guanghe.feishu.cn/wiki/WKlvwTYaXioVd7kDeWkcxWKvnTf
- 产品现状说明：https://guanghe.feishu.cn/docx/Q4JqdpHrmoizYqxkypocnYzTngf
- 飞书项目：https://project.feishu.cn/ruxiao/tec_prd/detail/7016921222
- 实现规程：`plugins/workspace-specflow/skills/prd-feishu-sync/SKILL.md`（及 consistency-check / publish）
