# Script And Environment Contract

## Shared Environment Variables

- `SOURCEGRAPH_URL`: Sourcegraph base URL or GraphQL endpoint
- `SOURCEGRAPH_TOKEN`: Sourcegraph access token. If missing or expired, the independent `sourcegraph-token` script should refresh it before cutover starts
- `GITLAB_URL`: GitLab base URL, defaults to `https://gitlab.yc345.tv`
- `GITLAB_TOKEN`: optional GitLab token for HTTPS clone
- `APISIX_ADMIN_KEY`: optional APISIX Admin API key used only for read-only route discovery

## Recommended Shell Setup

```bash
export SOURCEGRAPH_URL="https://sourcegraph.yc345.tv"
export GITLAB_URL="https://gitlab.yc345.tv"
export APISIX_ADMIN_KEY="<your-apisix-admin-key>"
```

`SOURCEGRAPH_URL` 和 `GITLAB_URL` 都有默认值，所以通常不设置也可以；只有当你要覆盖默认地址时才显式导出。

Optional:

```bash
export SOURCEGRAPH_TOKEN="<your-sourcegraph-token>"
```

Usually you do not need to set `SOURCEGRAPH_TOKEN` manually, because the independent `sourcegraph-token` flow can refresh it automatically.

## APISIX Route Discovery

When APISIX is part of the gateway chain, prefer passing these optional task inputs:

- `apisixAdminURL`
- `apisixAdminURLs`
- `apisixAdminKeyEnvVar`

Default behavior:

- `apisixAdminKeyEnvVar`: default to `APISIX_ADMIN_KEY`
- `apisixAdminURL` is the single-endpoint form; `apisixAdminURLs` is the multi-gateway form
- if both are present, treat them as one deduplicated list of APISIX gateway sources
- never write the APISIX admin key into scripts, reports, or source files
- use the key only at runtime through the `X-API-KEY` header

## `sourcegraph_graphql.py`

### Commands

- `whoami`
- `search --query <query> [--first N] [--lines-per-file N]`
- `repos --query <query> [--first N]`
- `file --repo <repo> --path <path> [--rev <rev>] [--start-line N] [--end-line N]`

### Output

Always prints JSON to stdout.

## `repo_bootstrap.sh`

### Required Args

- `--repo-path`
- `--branch`

### Optional Args

- `--base master`
- `--remote origin`
- `--allow-dirty`
- `--no-push-remote`

### Output

Prints JSON with repo path, base branch, target branch, whether the branch already existed, the checked-out commit, remote branch status, dirty-worktree state, and bootstrap mode. When `bootstrapMode` is `continue_on_dirty_target_branch`, treat the existing target-branch changes as part of the current task context. If the local branch exists but the remote branch is missing, the script should push the branch automatically by default.

## `gitlab_clone_or_update.sh`

### Required Args

- `--repo <namespace/project>`

### Optional Args

- `--dest-root ~/work`
- `--branch <branch>`
- `--protocol auto|https|ssh`
- `--keep-namespace`

### Output

Prints JSON with the local path, action, current branch, commit, and clone URL.

## `gitlab_create_mr.py`

### Required Args

- `--repo-path`
- `--branch`

### Optional Args

- `--target-branch <branch>` defaults to `dev`
- `--gitlab-url <url>` defaults to `GITLAB_URL`
- `--remote <name>` defaults to `origin`
- `--title <title>`
- `--description <description>`

### Behavior

- first tries GitLab push options to create an MR
- if `GITLAB_TOKEN` is available, also tries GitLab API to detect existing MRs or create one directly
- always prints JSON to stdout
- when creation is not possible, returns a JSON result with blocker reason and a direct create-MR URL targeting `dev`

## `gitlab_push_and_create_mr.py`

### Required Args

- `--repo-path`
- `--branch`

### Optional Args

- `--target-branch <branch>` defaults to `dev`
- `--gitlab-url <url>` defaults to `GITLAB_URL`
- `--remote <name>` defaults to `origin`
- `--title <title>`
- `--description <description>`
- `--set-upstream`

### Behavior

- performs the real push with GitLab push options in the same command
- this is the preferred path when local SSH/certificate auth is already sufficient for GitLab
- if GitLab emits an MR URL, returns it directly
- if push succeeds but GitLab does not emit an MR URL, returns a direct create-MR URL
- if `GITLAB_TOKEN` exists, may additionally query for an already-created MR URL
