---
name: telemetry-resolve-repos
description: Resolve telemetry target services from Feishu Base into GitLab repositories. Use for /telemetry:resolve-repos, first-stage service inventory fetching, repo-resolution.csv generation, and manual repository confirmation workflows.
---

# Telemetry Resolve Repos

## Goal

Fetch Kubernetes service inventory from Feishu, filter target backend production services, resolve GitLab repositories, and generate `./telemetry-audit/repo-resolution.csv`. This stage stops for manual confirmation.

## Required References

- `references/base-defaults.md`
- `references/service-inventory-json.md`
- `references/repo-resolution-csv.md`
- `references/checkpoints.md`
- `../../references/dependencies.md`

## Workflow

1. Run `/telemetry:doctor` first.
2. Fetch inventory using plugin config defaults:

```bash
python3 plugins/telemetry-suite/scripts/fetch_service_inventory.py --output-file ./telemetry-audit/service-inventory.json
```

3. Resolve repositories:

```bash
python3 plugins/telemetry-suite/scripts/resolve_repos.py --inventory-file ./telemetry-audit/service-inventory.json --output-csv ./telemetry-audit/repo-resolution.csv
```

4. Stop and ask the user to review `待确认` and `未找到` rows.

## Rules

- Use `~/.cursor/telemetry-suite/config.json` for tokens and Feishu Base defaults.
- Do not continue to audit until repository mapping has been confirmed.
- Do not commit generated CSVs unless the user explicitly asks.
