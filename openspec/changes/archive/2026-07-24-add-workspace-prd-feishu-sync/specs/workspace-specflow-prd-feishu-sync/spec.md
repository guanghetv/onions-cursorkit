# Workspace Specflow PRD Feishu Sync

独立封装的飞书同步能力：创建文档、契约层推送/回收、绑定维护与 5/9 同步门控。不做一致性结论门禁。

规程自包含于 `prd-feishu-sync` 技能正文（四区 STATUS/REVIEW/PRD_BODY/CONSISTENCY、CAS、MODULE 行级增量与图片、飞书排版与局部读写），运行时不依赖外部技能引用。


## ADDED Requirements

### Requirement: 自包含同步与飞书写作协议

系统 SHALL 在 `/prd-feishu-sync` 技能正文中完整规定同步与飞书写作协议，禁止默认全文 overwrite。

#### Scenario: 受管区与禁覆盖

- **WHEN** 对已有飞书文档执行 `push`
- **THEN** 仅更新受管契约正文区（或等价 marker 圈定区域）；不得 `overwrite` 整篇；不得静默覆盖评审区与飞书讲解层

#### Scenario: 增量粒度

- **WHEN** MODULE 表格或契约章节有局部变更
- **THEN** 优先章节文案精准替换 + MODULE 行级替换；变更单元与图片纳入 hash/manifest；远端手工改动与本地冲突时进入对账而非静默覆盖

#### Scenario: 发布确认与基线

- **WHEN** 执行真实飞书写入
- **THEN** 须有差异预览与明确确认；成功后登记 source commit / feishu revision 类基线（可落在 `review-sync.yaml` 或等价 metadata 扩展字段）

#### Scenario: 飞书排版与局部读写

- **WHEN** `create` 或 `push` 写入/更新飞书可读内容
- **THEN** 系统按技能内建排版规则执行（结论前置、表/callout/画板、避免大段纯文字），用局部更新；写后回读校验目标区块存在且邻接内容未误删

### Requirement: 同步技能单独封装

系统 SHALL 提供独立命令 `/prd-feishu-sync`，将飞书同步与一致性校验解耦。

#### Scenario: 子命令齐全

- **WHEN** 产品或 Agent 调用同步能力
- **THEN** 支持至少 `create`、`push`、`pull`（或 `reconcile`）、`status`、`rebind` 子命令

#### Scenario: 不做开工结论

- **WHEN** `/prd-feishu-sync` 执行成功或失败
- **THEN** 系统不写入「可开工 / 一致性通过」类结论；可建议随后执行 `/prd-consistency-check`

### Requirement: 初始化即创建飞书文档

系统 SHALL 在 `/req-new` 完成需求目录创建后调用 `/prd-feishu-sync create`，使用 `lark-cli` 创建飞书文档并深度绑定。

#### Scenario: create 写入绑定

- **WHEN** `create` 成功
- **THEN** `metadata.yaml` 含 `feishu.doc_url`、`feishu.doc_token`，且兼容字段 `feishu_doc` 与 `doc_url` 一致；`last_synced_stage` 为 `skeleton`

#### Scenario: create 写入未校验占位

- **WHEN** `create` 成功
- **THEN** 飞书文档含 `[PRD-SYNC:CONSISTENCY:v1]` 机器区，文案含「⏳ 未校验」；本地 `consistency.status` 为 `unknown`；后续普通 `push` 不得改写该区结论

#### Scenario: lark-cli 不可用


- **WHEN** 环境无法使用 `lark-cli` 完成创建
- **THEN** 系统明确失败并提示安装/登录，不得伪造已绑定成功

### Requirement: 深度绑定单文档

系统 SHALL 使每个需求目录仅绑定一篇飞书文档，并以 `feishu.doc_token` 为唯一操作标识。

#### Scenario: 禁止静默换链

- **WHEN** 已存在有效 `doc_token`
- **THEN** 普通 `push`/`create` 不得静默改写为另一文档；更换须走 `rebind` 并经用户确认

#### Scenario: 操作前校验绑定

- **WHEN** 执行 `push` / `pull` / `reconcile`
- **THEN** 若缺少 `doc_token`，系统阻断并指引先 `create` 或 `rebind`

### Requirement: 契约层推送且保留讲解层

系统 SHALL 在 `push` 时仅更新飞书契约层章节，不覆盖飞书讲解层（`narrative.background` / `narrative.value`，按标题关键词定位）。

#### Scenario: 推送契约映射

- **WHEN** `push` 执行且本地契约章节有更新
- **THEN** 飞书对应契约章节与本地对齐（含 Feature、MODULE、关键关注、回归、目标向概述、版本表等 `chapter-map` 内 unit）

#### Scenario: 不覆盖讲解层

- **WHEN** 飞书已有背景/价值等讲解正文（`narrative.*`）
- **THEN** `push` 不得用本地空缺或旧内容清空/覆盖这些讲解段落

#### Scenario: 章节按语义定位

- **WHEN** sync 需要识别背景、价值、关键关注等小节
- **THEN** 须按 unit key + 标题关键词匹配；不得将展示序号（如标题里的 3.1）作为唯一判据

### Requirement: 5/9 同步门控

系统 SHALL 在 9 稿已成功同步后默认停止 5 稿同步，除非产品显式强制。

#### Scenario: 9 稿同步成功打标

- **WHEN** `push --stage v9` 成功
- **THEN** `feishu.v9_synced` 为 `true`，`last_synced_stage` 为 `v9`

#### Scenario: 已 v9 后默认拒绝 v5

- **WHEN** `v9_synced` 为 `true` 且请求 `push --stage v5` 且未带 `--force`
- **THEN** 系统拒绝同步，并提示使用 `--force` 的显式命令

#### Scenario: 强制同步 5 稿

- **WHEN** `push --stage v5 --force` 且用户确认 diff 摘要
- **THEN** 允许推送，`last_synced_stage` 为 `force_v5`，并留下 warning 级留痕

#### Scenario: 未 v9 时 5 稿可同步

- **WHEN** `v9_synced` 为 `false` 且 `/pm-spec-5` 确认或请求 `push --stage v5`
- **THEN** 系统允许同步飞书契约层

### Requirement: 评审回收对账

系统 SHALL 支持从飞书契约层回收变更到本地 `prd.md`，且须经产品确认。

#### Scenario: reconcile 确认后写 md

- **WHEN** 飞书契约相对本地超前，且用户确认对账单
- **THEN** 系统将契约差异写回 `prd.md`，不把讲解层写入本地 9 稿

#### Scenario: 未确认不写 md

- **WHEN** 对账单尚未获用户确认
- **THEN** 系统不得修改 `prd.md` 契约正文

### Requirement: 推送时可读性处理

系统 SHALL 在 `push` 时对飞书契约区做可读性排版，避免大段连续正文。

#### Scenario: 去大段

- **WHEN** 待推送契约段落存在过长连续正文（与 `/pm-spec` 可读阈值对齐，如连续超过 6 行）
- **THEN** 系统拆为列表/表格/callout 后再写入飞书，或阻断并提示先改本地

#### Scenario: 复杂流程画板尽力而为

- **WHEN** 契约中含复杂流程 Mermaid
- **THEN** 系统尽力转为飞书画板；失败时保留代码块并 warning，不假装成功转画板
