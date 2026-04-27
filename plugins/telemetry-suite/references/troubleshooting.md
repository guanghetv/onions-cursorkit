# Telemetry Suite Troubleshooting

## Infrastructure failures

These failures are not business repository blockers and should not be written as `执行状态=阻塞` for a service row:

- Cursor `agent` returns `You have an unpaid invoice`.
- Cursor `agent` returns `read ECONNRESET`.
- Cursor CLI config rename fails with `ENOENT`.
- `lark-cli auth status` fails before service inventory fetch.

Stop the drain, fix the environment, then rerun.

## GitLab and MR creation

MR creation order is:

1. GitLab API create or reuse MR.
2. Git push option `merge_request.create`.
3. `glab mr create` / `glab mr list` fallback.

If `glab` is installed but returns `403 insufficient_scope`, record token or permission blocking, not missing `glab`.

## CSV safety

Only the scheduler writes `telemetry-audit-results.csv`. Worker outputs must be saved separately and merged serially. If CSV decoding fails, restore from the newest clean backup before rerunning.

## Stage semantics

- Stage 1 stops for manual repository confirmation.
- Stage 2 is read-only.
- Stage 3 modifies repositories, pushes branches, and creates or reuses MRs.
- Terminal statuses are not redispatched: `已提MR`, `已完成`, `无需接入`, `已跳过`, `阻塞`, `待确认方案`.
