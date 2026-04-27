---
name: telemetry-audit-from-csv
description: Audit telemetry readiness from repo-resolution.csv without modifying repositories. Use for /telemetry:audit-from-csv, framework inference, applicability matrix generation, and telemetry-audit-results.csv creation.
---

# Telemetry Audit From CSV

## Goal

Read confirmed `repo-resolution.csv`, run read-only single-repository audit workers, infer framework/template/applicability, and write `./telemetry-audit/telemetry-audit-results.csv`.

## Required References

- `references/audit-result-csv.md`
- `references/checkpoints.md`
- `references/framework-inference.md`
- `references/single-repo-worker.md`
- `references/telemetry-audit-checklist.md`
- `references/telemetry-instrument.md`

## Workflow

1. Run `/telemetry:doctor`.
2. Generate the audit plan and manifest:

```bash
python3 plugins/telemetry-suite/scripts/audit_from_csv.py plan --repo-resolution-csv ./telemetry-audit/repo-resolution.csv --output-csv ./telemetry-audit/telemetry-audit-results.csv --artifact-dir ./telemetry-audit --worker-concurrency 3
```

3. Dispatch read-only workers per manifest.
4. Merge results serially with the scheduler command.
5. Summarize the CSV and prepare for `/telemetry:instrument-from-csv`.

## Rules

- This stage does not modify business code.
- Go and Node are target languages; non-target languages are marked skipped.
- Preserve existing execution tracking fields when rerunning.
