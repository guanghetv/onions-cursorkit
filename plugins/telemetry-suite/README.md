# Telemetry Suite

Telemetry Suite is a Cursor workflow plugin for batch observability adoption. It resolves services from Feishu Base, maps them to GitLab repositories, audits Go/Node telemetry gaps, and can automatically instrument repositories, verify changes, push branches, and create GitLab merge requests.

## Commands

- `/telemetry:setup` - create local private configuration.
- `/telemetry:doctor` - check dependencies, credentials, Cursor agent CLI, and GitLab/Feishu access.
- `/telemetry:resolve-repos` - fetch Feishu service inventory and generate `repo-resolution.csv`.
- `/telemetry:audit-from-csv` - audit repositories and generate `telemetry-audit-results.csv`.
- `/telemetry:instrument-from-csv` - instrument applicable missing telemetry items and create or reuse MRs.

## Configuration

Private config lives at `~/.cursor/telemetry-suite/config.json`. Do not commit this file. See `references/config.schema.json` and `references/dependencies.md`.

## Safety

Stage 1 stops for manual repository confirmation. Stage 2 is read-only. Stage 3 modifies business repositories and creates MRs. Always run `/telemetry:doctor` before a large batch.
