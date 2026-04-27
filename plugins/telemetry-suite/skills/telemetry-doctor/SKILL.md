---
name: telemetry-doctor
description: Diagnose Telemetry Suite prerequisites and configuration. Use before resolve/audit/instrument stages, or when GitLab, Feishu CLI, glab, Cursor agent CLI, CSV schema, or permission errors occur.
---

# Telemetry Doctor

## Goal

Run read-only checks before telemetry workflow execution. Doctor must not modify business repositories or write telemetry result CSV files.

## Required References

- `../../references/dependencies.md`
- `../../references/troubleshooting.md`

## Default Workflow

1. Run the mechanical check:

```bash
python3 plugins/telemetry-suite/scripts/telemetry_cli.py doctor
```

2. Interpret failures by category:
   - Environment: missing `python3`, `git`, `node`, `npm`, `npx`, `lark-cli`, `glab`, or `agent`.
   - Auth: `lark-cli auth status`, GitLab token, or `glab auth status` failed.
   - Agent infrastructure: Cursor `agent -p --output-format json` smoke test failed.
   - Config: private config missing required GitLab or Feishu fields.
3. Do not proceed to `/telemetry:resolve-repos` unless Feishu and GitLab checks pass.
4. Do not proceed to `/telemetry:instrument-from-csv` unless Cursor agent CLI and MR creation prerequisites pass.

## Rules

- Infrastructure failures are not business repository blockers.
- If doctor fails, report exact failing checks and suggested command from `dependencies.md`.
