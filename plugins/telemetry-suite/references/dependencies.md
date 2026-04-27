# Telemetry Suite Dependencies

## Required tools

- `python3` for scheduler scripts.
- `git` for clone/fetch/branch/push.
- `node`, `npm`, and `npx` for Feishu CLI installation.
- `lark-cli` for reading Feishu Base service inventory.
- `glab` for GitLab MR fallback and auth diagnostics.
- `agent` for Cursor headless worker execution in stage 2/3.

## Feishu CLI

Install and initialize Feishu CLI using the official guide:

- [飞书 CLI 安装指南](https://open.feishu.cn/document/no_class/mcp-archive/feishu-cli-installation-guide.md)
- [飞书 CLI 能力文档](https://open.feishu.cn/document/mcp_open_tools/feishu-cli-let-ai-actually-do-your-work-in-feishu)

Common setup commands:

```bash
npm install -g @larksuite/cli
npx -y skills add https://open.feishu.cn --skill -y
lark-cli config init --new
lark-cli auth login --recommend
lark-cli auth status
```

`/telemetry:resolve-repos` requires `lark-cli auth status` to pass.

## Local config

Private config lives at:

```text
~/.cursor/telemetry-suite/config.json
```

This file may contain secrets and must not be committed. Workspace overrides can live at:

```text
.cursor/telemetry-suite.local.json
```

## Recommended preflight

Run before each large batch:

```bash
python3 plugins/telemetry-suite/scripts/telemetry_cli.py doctor
```
