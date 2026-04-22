---
name: go-cutover-batch
description: Use when creating or running a batch of Go route cutover tasks that should execute sequentially with shared old/new service defaults, gateway defaults, retries, state tracking, and summary reporting.
---

# Go Cutover Batch

## Overview

Use this skill to batch multiple `/go-cutover-orchestrator` tasks in sequence.
This skill is a batch coordinator. It does not replace the single-route cutover logic.
For each task, if server-side code changes were made, the underlying cutover flow must commit and push automatically instead of pausing for user confirmation.
For each task that produces real server-side code changes, the default flow should also create a Merge Request targeting `dev`; if automatic creation is unavailable, the report must still record the blocker and a direct create-MR URL.
The default operating mode is no-interruption execution: do not stop between tasks to ask for routine confirmations, intermediate choices, or commit/push approval.
Treat every batch as new work from scratch. Do not rely on previous batch results, old report packs, or historical task statuses as a reason to skip task execution.
For editable repositories in a new batch, default to `master -> branch` instead of reusing the current local feature branch as baseline.
If a local repo is blocked by uncommitted changes on another branch, prefer an isolated worktree under `~/.config/superpowers/worktrees/<repo>/<branch>` instead of asking the user where or whether to switch.

In the current Cursor conversation, the preferred execution model is:

1. organize the batch in this session
2. run tasks sequentially in this same conversation
3. track progress explicitly
4. summarize results at the end

Do not default to shelling out to `agent` to invoke another agent session when the current conversation can execute the tasks directly.

Default principles:

- batch-level `oldServiceName/newServiceName/oldNamespace/newNamespace`
- task-level `oldRoute/newRoute/method/branch`
- every batch execution starts fresh from the current repositories
- old batch state and old reports are references at most, never skip signals
- the repository named by `oldServiceName` is reference-only by default
- the repository named by `newServiceName` is implementation-reference by default
- default gateway repos:
  - `onions-school`
  - `channel-platform-server`
  - `channel`
  - `teacher-tenant`
- `serviceName + namespace => host`
  - example: `teacher + teacherschool => teacher.teacherschool`
- `SOURCEGRAPH_TOKEN` should come from the environment or the independent `sourcegraph-token` refresh flow, not from manually pasted batch input by default
- `apisixAdminKeyEnvVar` means the environment variable name that stores the APISIX key, not the key value itself

## When to Use

- The user wants to create a batch of route cutover tasks
- The user wants to run multiple cutovers one by one
- The user wants retries, state tracking, report collection, or batch summaries
- The user mentions `批量切换接口`, `执行批次`, `route cutover batch`, or `批次任务`

Do not use this skill for a single direct cutover when no batching or scheduling is needed.

## Files

- `scripts/batch_cli.py`: create/list batch JSON files
- `scripts/exec_batch.py`: optional external sequential runner for out-of-band automation
- `scripts/exec_cursor.py`: optional single-task external prompt runner
- `scripts/state.py`: SQLite state and lock helpers
- `scripts/alert.py`: Feishu alert sender
- `references/batch-json-schema.md`: batch JSON structure
- `references/config.json`: local default config

## Quick Start

### Preferred in-chat workflow

Ask to create or execute a batch in this conversation.
The assistant should:

1. collect or load batch-level defaults
2. automatically validate or refresh the Sourcegraph token before the batch starts
3. build a task list
4. execute tasks one by one with `/go-cutover-orchestrator`
5. keep explicit per-task status
6. validate that each task produced its required report pack
7. summarize successes, failures, blockers, and report paths

### Optional external utilities

Create interactively:

```bash
python3 "<plugin-root>/skills/go-cutover-batch/scripts/batch_cli.py" create
```

Quick create:

```bash
python3 "<plugin-root>/skills/go-cutover-batch/scripts/batch_cli.py" quick \
  --oldRoute "/admin-room/list" \
  --newRoute "/teacher-school/admin-room/list" \
  --branch "feat/m-xxxx" \
  --oldService "teacher" \
  --newService "teacher-school" \
  --oldNamespace "teacherschool" \
  --newNamespace "teacherschool"
```

Run externally:

```bash
python3 "<plugin-root>/skills/go-cutover-batch/scripts/exec_batch.py" \
  "<workspace-root>/openclaw-runner/batches/<batch-id>.json"
```

## Recommended Input Model

### Batch-level defaults

- `oldServiceName`
- `newServiceName`
- `oldNamespace`
- `newNamespace`
- `SOURCEGRAPH_URL`
- `GITLAB_URL`

### Task-level core fields

- `oldRoute`
- `newRoute`
- `method`
- `branch`

### Optional overrides

- task-level service fields for rare exceptions
- `gatewayRepos`
- `apisixAdminURL`
- `apisixAdminURLs`
- `apisixAdminKeyEnvVar`
- `oldServiceHint`
- `newServiceHint`

If `oldServiceHint/newServiceHint` is omitted, the runner builds:

- `oldServiceHint = oldServiceName.oldNamespace`
- `newServiceHint = newServiceName.newNamespace`

## Batch Workflow

### In-chat preferred workflow

1. Create or load a batch definition
2. Before running the first task, call the independent `sourcegraph-token` script to validate or refresh the token
   - if `SOURCEGRAPH_TOKEN` is already set in the environment and valid, reuse it
   - if it is missing or expired, refresh it automatically
3. Write down task order explicitly
4. Execute tasks sequentially in this conversation
5. After each task, record one of:
   - `succeeded`
   - `failed`
   - `blocked`
6. Before editing any repo, prepare it from `master -> branch`; if the current local checkout is unsafe to switch, automatically use an isolated worktree
7. After each task, record the task report directory path and validate required markdown/json artifacts
8. For any repo with real code changes, create or attempt to create a Merge Request targeting `dev`, then record its status and link in the report pack
9. Continue to the next task unless a true hard blocker should stop the whole batch
10. Emit final batch summary
11. In the final user-facing summary, always主动给出每条任务或批次汇总报告包路径，不要等用户再要求“补报告”
12. In the final user-facing summary, also展示每个改动仓库的 Merge Request 状态和直达链接
13. Treat a task as incomplete if it changed code but did not leave commit/push evidence
14. Treat a task as incomplete if the required report pack is missing, incomplete, or not mentioned in the final summary
15. Treat a task as incomplete if code changes were pushed but no Merge Request result was recorded for the changed repo
16. In headless or automated execution, never wait for the user to reply mid-task; infer or fail fast with a blocker note
17. Do not skip a task just because a previous batch said it was already done; re-run the task against current code and decide again

### Optional external runner workflow

1. Create or load a batch JSON
2. Persist batch/task records in SQLite
3. Run tasks sequentially
4. Lock `repo+branch` based on gateway repos and any legacy target repos
5. Invoke one headless agent run per task
6. Validate the generated report directory and `artifacts/execution.json`
7. Retry retryable failures
8. Emit final batch summary

State persistence is for locking, visibility, and current-run bookkeeping only.
Do not treat persisted task status from an older run as permission to skip or auto-complete a task in a new batch execution.

## Success Criteria

A task is considered successful only when:

1. the task completed its full `/go-cutover-orchestrator` workflow
2. a new or updated report directory exists
3. required report files exist
4. `artifacts/execution.json` contains a success-like status such as:
   - `success`
   - `succeeded`
   - `already_cut_over`
   - `no_code_change`
   - `noop`
5. when code changes happened, `artifacts/execution.json` also includes non-empty `commitsCreated` and `pushesCompleted`
6. the assistant can name the report directory path in the final user-facing response without waiting for an extra user prompt
7. editable repos were prepared from `master -> branch`, either in-place when safe or through an isolated worktree when the current checkout was unsafe to reuse
8. for each changed repo, the report records a Merge Request result against `dev`, including a direct URL to the created MR when available, or a direct create-MR URL plus blocker reason when creation failed

## 环境变量约定

推荐把敏感值放在环境变量里，而不是直接贴进批次输入。

### Sourcegraph

- `SOURCEGRAPH_TOKEN`
  - 推荐：不手工传
  - 执行器会在批次开始前自动检查
  - 未设置或已过期时，会自动调用独立版 `sourcegraph-token` 刷新

### APISIX

- `apisixAdminKeyEnvVar`
  - 填的是变量名，例如：`APISIX_ADMIN_KEY`
  - 不要把真实 key 值直接写进批次 prompt
  - 如果不填，默认就是 `APISIX_ADMIN_KEY`

### 推荐设置方式

```bash
export APISIX_ADMIN_KEY="<your-apisix-admin-key>"
export SOURCEGRAPH_URL="https://sourcegraph.yc345.tv"
export GITLAB_URL="https://gitlab.yc345.tv"
```

如果你想手工指定 Sourcegraph token，也可以：

```bash
export SOURCEGRAPH_TOKEN="<your-sourcegraph-token>"
```

但通常不需要，执行器会自动刷新。

If using the optional external runner, `agent` exit code must also be `0`.
If the task finished with `already_cut_over`, `no_code_change`, or `noop`, missing commit/push evidence is acceptable.

## Common Mistakes

- Treating this skill as the single-route cutover implementation
- Treating the `oldServiceName` repo itself as a caller-edit target
- Using the external runner by default when the current conversation can execute the batch directly
- Filling task-level service fields for every task when batch defaults are enough
- Forcing users to provide `targetRepos` or `gatewayHints`
- Reusing previous batch conclusions to skip discovery, validation, or report generation in a new batch
- Treating report generation as optional post-processing that happens only when the user explicitly asks
- Pasting raw APISIX key values into `apisixAdminKeyEnvVar` instead of passing the environment variable name
- Manually pasting `SOURCEGRAPH_TOKEN` into every batch prompt instead of letting the environment/auto-refresh flow manage it
- Asking the user whether a new cutover batch should branch from the current feature branch instead of defaulting to `master`
- Asking the user where to place an isolated worktree during batch execution when a safe global default path would unblock progress
- Pushing changed branches without also attempting a Merge Request to `dev`
- Omitting Merge Request status or link from the final report and user-facing summary
- Stopping mid-batch to ask about minor ambiguity, commit approval, or routine next-step choices
- Running tasks in parallel in one agent session
- Trusting external runner exit code without validating `execution.json`
- Treating `success` alone as enough when changed repos did not record both commit and push evidence

## References

- Batch schema: `references/batch-json-schema.md`
- Local defaults: `references/config.json`
