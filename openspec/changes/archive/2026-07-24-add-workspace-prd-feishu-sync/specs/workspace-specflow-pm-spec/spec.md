# Workspace Specflow PM Spec (9稿) Delta

挂接飞书同步、瘦身与一致性门禁。

## ADDED Requirements

### Requirement: 9 稿确认后同步飞书

系统 SHALL 在 `/pm-spec` 9 稿用户确认通过后调用 `/prd-feishu-sync push --stage v9`。

#### Scenario: 确认后必推送

- **WHEN** 9 稿确认流程收口成功
- **THEN** 系统执行 v9 同步；成功后 `feishu.v9_synced` 为 true

#### Scenario: 同步失败不得假装完成

- **WHEN** v9 同步失败
- **THEN** 系统不得向用户宣称飞书已是最新；须明确失败并给出重试命令（`/prd-publish` 或 `push --stage v9`）

### Requirement: 9 稿确认执行瘦身

系统 SHALL 在 9 稿结构化收口时移除本地讲解层正文，保留契约层与原型引用。

#### Scenario: 按语义移除讲解层

- **WHEN** 9 稿确认前本地仍含背景/价值章节正文（`narrative.*`，按标题关键词识别）
- **THEN** 系统将讲解内容保留在飞书侧（若不存在则提示补讲解），并从 `prd.md` 整节删除这些讲解小节（禁止「见飞书」指针；不得只靠展示序号判断）

### Requirement: confirmed 前一致性校验

系统 SHALL 在设置 `prd.status = confirmed` 之前执行 `/prd-consistency-check`（或等价经由 `/prd-publish`）。

#### Scenario: critical 阻断 confirmed

- **WHEN** 一致性校验存在 critical fail
- **THEN** 系统不得将 `prd.status` 设为 `confirmed`
