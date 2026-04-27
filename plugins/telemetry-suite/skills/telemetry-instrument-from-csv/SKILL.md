---
name: telemetry-instrument-from-csv
description: Instrument repositories from telemetry-audit-results.csv. Use for /telemetry:instrument-from-csv when automatically generating per-repo plans, modifying code, running verification, committing, pushing, creating GitLab MRs, and backfilling execution state.
---

# Telemetry Instrument From CSV

## Goal

Consume `telemetry-audit-results.csv`, select rows with applicable missing telemetry items, generate per-repo plans, prepare writable repos, delegate each repo to a single worker, verify, commit, push, create or reuse MR, and serially backfill the CSV.

## Required References

- `../telemetry-audit-from-csv/references/audit-result-csv.md`
- `../telemetry-audit-from-csv/references/telemetry-instrument.md`
- `references/checkpoints.md`
- `references/subagent-dispatch.md`
- `references/single-repo-worker.md`
- `../../references/troubleshooting.md`

## Workflow

1. Run `/telemetry:doctor` first.
2. Generate manifest:

```bash
python3 plugins/telemetry-suite/scripts/instrument_from_csv.py plan --input-csv ./telemetry-audit/telemetry-audit-results.csv --artifact-dir ./telemetry-audit --output-manifest ./telemetry-audit/instrument-manifest.json --worker-concurrency 1
```

3. For each dispatch item, run `prepare-repo`; only dispatch workers after local repo path exists and contains `.git`.
4. Worker handles exactly one repo: modify only applicable missing items, verify, commit, push, create or reuse MR.
5. Parse worker output with `parse-worker-output`, then serially `merge-json`.
6. Re-plan until candidate count is zero.

## Rules

- This stage modifies business repositories and creates MRs.
- Infrastructure failures from Cursor agent CLI must stop the drain without writing business blockers.
- CSV writes must be serialized by the scheduler.
- Terminal statuses are not redispatched: `已提MR`, `已完成`, `无需接入`, `已跳过`, `阻塞`, `待确认方案`.
