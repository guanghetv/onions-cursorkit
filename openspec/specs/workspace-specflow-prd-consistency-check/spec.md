# workspace-specflow-prd-consistency-check Specification

## Purpose

定义契约层一致性校验（结构 A + 语义 B）、多触发真跑、结果落盘与飞书 CONSISTENCY 回写；不负责推送正文。

## Requirements

### Requirement: 校验范围仅限契约层

系统 SHALL 仅对契约层做一致性校验，忽略飞书讲解层与本地已删除的背景章节差异。

#### Scenario: 讲解层差异不 fail

- **WHEN** 飞书讲解层（`narrative.*`，标题含背景/价值）与本地不一致或本地无对应章节
- **THEN** 系统不因此判定 critical fail

#### Scenario: 契约 MODULE 必须对齐

- **WHEN** 执行一致性校验
- **THEN** 系统对映射表内契约章节与每个 `MODULE-N` 执行结构检查，并在进开发前/T4 阶段执行语义对齐检查

### Requirement: 结构 A 为 critical

系统 SHALL 将绑定完整性、章节/MODULE 结构对齐、Feature↔MODULE 交叉引用、9 稿讲解层回流禁止列为 critical。

#### Scenario: 缺少绑定

- **WHEN** `feishu.doc_token` 缺失或飞书不可 fetch
- **THEN** 总体结论为 fail（critical）

#### Scenario: 9 稿仍含讲解层

- **WHEN** 自检为进开发前/T4/qa-spec 前（或 `prd.stage` 为 `v9_pending`/`confirmed`，或 `v9_synced=true`，或本地标明 9稿），且本地仍存在 `narrative.*`（标题含背景/价值，含空壳或「见飞书」指针）
- **THEN** 判定 critical fail，并提示按语义整节删除（讲解只在飞书；禁止留指针）
- **AND** 不得因 `prd.stage` 尚未写成 `confirmed`（`/pm-spec` 在 check 之后才写）而跳过本项

#### Scenario: 5 稿评审前允许本地讲解层

- **WHEN** 自检阶段为纯「评审前」且未命中 C6 适用条件
- **THEN** 本地仍含背景/价值讲解小节不构成 C6 fail

#### Scenario: MODULE 缺验收或原型说明

- **WHEN** 某 MODULE 缺少验收标准，或既无原型锚点也无「无原型（原因）」
- **THEN** 判定 critical fail

### Requirement: 语义 B 分阶段定级

系统 SHALL 对契约 MODULE 做意图一致性比对：评审前可为 warning，进开发前与提交前门禁为 critical。

#### Scenario: 评审前语义差异

- **WHEN** 自检阶段为评审前，且某 MODULE 飞书与 md 意图不一致
- **THEN** 该项为 warning，不单独构成 hard block（其它 critical 仍生效）

#### Scenario: 进开发前语义差异

- **WHEN** 自检阶段为进开发前或 T4 提交门禁，且某 MODULE 意图不一致
- **THEN** 该项为 critical fail

### Requirement: 多触发必须真跑

系统 SHALL 在约定触发点实际执行校验并落盘报告，禁止用对话口头清单代替。

#### Scenario: 主动触发

- **WHEN** 用户提出一致性校验、能否开工、评审就绪等意图
- **THEN** 系统执行完整校验并输出报告路径与摘要

#### Scenario: 9 稿确认前

- **WHEN** `/pm-spec` 准备将 `prd.status` 置为 confirmed
- **THEN** 须先通过本校验（或显式处于允许的 warn-only 策略且无 critical）；存在 critical fail 时不得 confirmed

#### Scenario: 提交前双条件（Agent 规程）

- **WHEN** 9 稿已确认且 Agent 协助 git commit/push 需求目录变更
- **THEN** 若相对 `last_synced` 仍有未推送契约改动，或 `consistency.status` 为 `fail`，Agent 须阻断并提示先 `/prd-publish`（本期不依赖 git hook；裸提交可绕过）

#### Scenario: 下游启动前

- **WHEN** `/qa-spec` 启动且需求已 confirmed
- **THEN** 若 `consistency.status` 为 `fail` 或缺失必要校验，系统阻断或强警告（实现须在技能中明示默认阻断）

### Requirement: 结果落盘并回写飞书

系统 SHALL 将最新校验结果写入本地报告与 `metadata.consistency`，并回写飞书底部机器维护区。

#### Scenario: 本地报告

- **WHEN** 校验完成
- **THEN** 写入 `requirements/<id>/prototypes/prd-consistency-check-YYYY-MM-DD.md`（同日覆盖），并更新 `consistency.status/checked_at/report_path/source_commit`

#### Scenario: 飞书展示最新结论

- **WHEN** 校验完成且飞书可写
- **THEN** 飞书 CONSISTENCY 机器区覆盖为总体结论（✅/⚠️/❌）、日期、报告路径、对应 commit；不再显示「⏳ 未校验」

#### Scenario: 未校验时飞书可见

- **WHEN** 文档已 create 但尚未成功跑完一致性校验
- **THEN** 飞书 CONSISTENCY 区保持「⏳ 未校验」占位（由 sync create/rebind/补插维护），不得伪造通过结论

#### Scenario: 只读交付物正文

- **WHEN** 校验执行
- **THEN** 除报告、`metadata.consistency`、飞书机器 callout、已跳过项留痕外，不修改 MODULE 契约正文

### Requirement: 与同步协作

系统 SHALL 在校验前处理绑定缺失与飞书超前漂移，不得在未同步时假装与飞书一致。

#### Scenario: 飞书契约超前

- **WHEN** 检测到飞书契约相对 md 超前且未 reconcile
- **THEN** 进开发前/T4 判定 critical；评审前可为 warning 并建议 `/prd-feishu-sync pull`

#### Scenario: 本地新于飞书

- **WHEN** 本地契约新于 `last_synced` 且未 push
- **THEN** T4 要求先 `/prd-publish`；其它阶段至少 warning

