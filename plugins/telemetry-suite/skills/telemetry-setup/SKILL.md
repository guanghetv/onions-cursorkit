---
name: telemetry-setup
description: Initialize telemetry-suite local configuration. Use when installing the Telemetry Suite plugin, configuring GitLab token, Feishu CLI/Base settings, workspace defaults, or before first running /telemetry commands.
---

# Telemetry Setup

## Goal

Prepare local private configuration for the Telemetry Suite plugin. This command is a setup wizard, not a batch execution command.

## Required References

- `../../references/dependencies.md`
- `../../references/config.schema.json`

## Default Workflow

1. Explain that private config is stored at `~/.cursor/telemetry-suite/config.json`.
2. Verify Feishu CLI installation path from the dependency guide.
3. Collect or confirm GitLab URL/token, Feishu Base token/table/view, workspace root, and artifact directory.
4. Use the helper command when writing config is requested:

```bash
python3 plugins/telemetry-suite/scripts/telemetry_cli.py setup --write \
  --gitlab-url "https://gitlab.yc345.tv" \
  --gitlab-token "<TOKEN>" \
  --feishu-base-token "<BASE_TOKEN>" \
  --feishu-table-id "<TABLE_ID>" \
  --feishu-view-id "<VIEW_ID>"
```

5. After setup, run `/telemetry:doctor`.

## Rules

- Never commit private config or tokens.
- Prefer browser-assisted Feishu login via `lark-cli auth login --recommend`.
- If credentials are missing, stop with exact next action rather than running the batch workflow.
