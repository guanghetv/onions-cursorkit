# workspace-specflow-prd-publish Specification

## Purpose

定义 `/prd-publish` 一键编排：先 `/prd-feishu-sync push`，再 `/prd-consistency-check`；不内嵌同步实现细节。

## Requirements

### Requirement: 一键编排 sync 后 check

系统 SHALL 提供 `/prd-publish`，按顺序调用 `/prd-feishu-sync push` 与 `/prd-consistency-check`。

#### Scenario: 默认阶段选择

- **WHEN** 用户执行 `/prd-publish` 且未指定 stage
- **THEN** 若 `v9_synced` 为 true 或 `prd.stage` ∈ {`v9_pending`, `confirmed`}，则按 v9 推送；否则按当前 5 稿阶段推送

#### Scenario: sync 失败即停止

- **WHEN** `push` 失败
- **THEN** 不执行 check，不更新为通过态，并向用户报告失败原因

#### Scenario: check 失败明确阻断

- **WHEN** `push` 成功但 check 存在 critical fail
- **THEN** 命令以失败结论结束，飞书与 metadata 记录失败结果，不得宣称发布成功

#### Scenario: 成功收口

- **WHEN** sync 与 check 均无 critical fail
- **THEN** 飞书展示最新校验结果，`metadata.consistency` 与 `feishu.last_synced_*` 已更新

