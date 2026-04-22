---
name: backend-service-switch
description: Switches server-side caller code from a user-provided old service to a user-provided new Go service. Use when a route has already been migrated to Go and the next step is to cut gateway or proxy repos and other backend services over on a fresh branch from master, while treating the old-service repo as reference-only unless the user explicitly asks to edit it, or when the user mentions 切调用, 替换老服务调用, endpoint migration, 后端改调 go 服务.
---

# Backend Service Switch

## Goal

Update all in-scope non-old-service server-side repositories so they call the user-provided new Go service instead of the user-provided old service chain, while keeping the outer API unchanged for frontend and client callers.

## Inputs

- target server-side repo
- `oldRoute`
- `newRoute`
- `method`
- `branch`
- `oldServiceName`
- `newServiceName`
- `oldServiceHint`
- `newServiceHint`
- sourcegraph evidence from the locator stage

## Input Validation

Do not enter the switch phase until these fields are all present:

- target server-side repo
- `oldRoute`
- `newRoute`
- `method`
- `branch`
- `oldServiceName`
- `newServiceName`
- `oldServiceHint`
- `newServiceHint`

If any required field is missing, first try safe inference from the task context and locator output.
Do not interrupt the workflow for non-blocking ambiguity.
Only stop before branch creation or code edits when the missing value cannot be inferred safely or when a conflict cannot be resolved without unsafe action.

## Default Workflow

1. Bootstrap the repository.
Run `skills/go-cutover-orchestrator/scripts/repo_bootstrap.sh` from this plugin to enforce `master -> branch`.
By default this bootstrap step should also ensure the branch exists on the remote.
If the target branch already contains existing code changes or uncommitted changes, treat them as the normal working baseline for this task and continue on top of them instead of forcing a clean checkout.
If the repo has uncommitted changes on a different branch, do not ask the user whether to reuse that branch. Instead, prefer an isolated worktree rooted at `~/.config/superpowers/worktrees/<repo>/<branch>` and run the same `master -> branch` bootstrap there. Only stop and report a blocker if the isolated worktree cannot be created or bootstrapped safely.

2. Inspect only likely backend call sites.
Focus on:

- gateway or proxy configs
- client wrappers, repo adapters, `third_party`, `third_parts`
- `proto`, `*.go`, `*.js`, and service integration files

Do not inspect the repository named by `oldServiceName` as a caller-edit target.
Do not inspect the repository named by `newServiceName` as a caller-edit target.
Use those two repositories only as contract references:

- `newServiceName`: verify the new interface first
- `oldServiceName`: verify the old interface second

Do not limit inspection to exact route literals. In the local repo, also search for:

- stable route fragments
- route-prefix declarations such as `router.prefix('/admin-room')` or `prefix: '/admin-room'`
- wildcard or catch-all declarations such as `path: '/*'`, `router.all(...)`, or method-scoped fallback handlers
- host variables and service config aliases
- template strings and concatenated path fragments
- wrapper/helper names such as `proxy`, `request`, `client`, `adapter`, `thirdPart`, `serviceAgent`
- generic proxy handlers such as `teacher.proxy()`, `serviceAgent.proxy()`, or `<service>.proxy()`
- routePattern/replacePath style forwarding

If the target path is assembled dynamically, follow the local symbol chain until you can classify the call site with evidence.
If a repo combines a matching route-family prefix with a wildcard or catch-all proxy to the old service, treat that as a real in-scope caller even when the exact child route is not written literally. Before calling it `out of scope`, determine whether the migrated route is still falling through the wildcard, already has an explicit new-service override, or is blocked by ambiguous routing order.

3. Inspect the new service first.
Locate the target interface in `newServiceName` and confirm:

- `newRoute`
- method
- parameters and parameter names
- request and response shape
- core business meaning

4. Inspect the old service second.
Locate the matching interface in `oldServiceName` and confirm:

- `oldRoute`
- method
- parameters and parameter names
- request and response shape
- core business meaning

5. Compare before editing.
Verify that the new and old interfaces are equivalent enough to switch callers safely.
Do not edit any caller until this comparison is done.
If `oldRoute`, `newRoute`, method, parameters, or business meaning do not line up, stop the cutover for that caller and record the mismatch.
Confirm the repo still contains real `oldServiceName` or old-route-chain evidence, and confirm the repo is not merely the old-service repository itself.

Server-side repos fall into three in-scope categories:

- gateway or proxy repo that forwards into `oldServiceName`
- other backend repo that calls `oldServiceName` directly

The repo named by `oldServiceName` is reference-only by default and should not be modified in this phase unless the user explicitly asks for it.

Do not proceed with server-side edits if the only evidence is:

- frontend or client usage
- docs without executable route or client logic
- unrelated route fragments

If the repo already points to `newServiceName` or the new route chain, mark it as `already cut over` and move on to the next in-scope server-side candidate.
Do not mark a repo `already cut over` or `out of scope` until local evidence has been checked, even if Sourcegraph nominated it weakly.

6. Perform the cutover.
Typical changes:
- swap old base URL or service name to the new Go service
- update old route forwarding to the new Go route
- when a gateway repo uses `prefix + wildcard/catch-all + old-service proxy`, prefer adding or updating an explicit route override for the migrated interface before the wildcard fallback instead of replacing the entire wildcard
- switch imported client or proto package if required
- keep request and response semantics compatible

7. Regenerate or rebuild only when needed.
If proto or generated client bindings change, run the repo-specific generation command.

8. Record the result.
Write changed file list, changed call sites, and regression risks into the report pack.

9. Finalize the repo when changes exist.

- stage only the cutover-relevant changes
- create a commit immediately without asking the user again
- push the branch to the remote immediately and verify upstream state
- create or attempt to create a Merge Request targeting `dev`
- record the Merge Request result and direct URL in the report pack

Use `skills/go-cutover-orchestrator/scripts/gitlab_push_and_create_mr.py` from this plugin during the real push step when possible.
Use `skills/go-cutover-orchestrator/scripts/gitlab_create_mr.py` from this plugin only as a fallback for after-the-fact detection or create-link generation.

If the repo is already cut over and no file changes are needed, do not create an empty commit. Still verify the branch exists on the remote and record this repo as `already cut over`.
If the local branch exists but the remote branch does not, push the branch automatically without asking.
If the target branch already had unrelated baseline files, do not use a blanket stage of the whole repo unless the repo workflow requires it for correctness.

## Guardrails

- Do not modify frontend-facing route contracts unless explicitly requested.
- Do not change unrelated methods on the same path.
- Do not upgrade dependencies as part of the cutover.
- Do not replace a broad wildcard or catch-all old-service proxy wholesale unless the whole covered route family has already been migrated and verified. For partial migrations, add the smallest explicit override that captures only the requested route and method.
- If the repo has existing code changes or uncommitted changes on the target branch, treat them as part of the task context and continue through switch, verification, report generation, and commit/push on top of them.
- If this task creates real code changes, commit and push them by default instead of pausing to ask the user.
- If this task creates real code changes, also create or attempt to create a Merge Request targeting `dev` by default instead of leaving it as optional follow-up work.
- For new cutover work, do not reuse the current local feature branch as the default baseline. Edited repos should start from `master -> branch`, using an isolated worktree when the current checkout is unsafe to reuse.
- If the repo has uncommitted changes on a different branch, do not stop merely to ask about branch switching; prefer isolated worktree execution and only report a blocker if that isolation path fails.
- Do not modify the old-service repo's caller code unless the user explicitly asks to edit the old service itself.
- Do not modify frontend or client repos in this phase.
- Do not stop for minor non-blocking issues if a reasonable default decision allows the cutover to continue safely.
- Treat commit or push failure after a real code change as a failure or blocker, not as optional follow-up work.

## Validation

Before leaving the repo:

1. Confirm the repo is on the requested branch.
2. Confirm the branch exists on the remote and is configured for tracking.
3. Confirm whether the repo continued on top of existing target-branch work or ran from a clean checkout.
4. Confirm each edited call site matches the requested method.
5. Confirm each edited call site used to target `oldServiceName` or the old route chain and now targets `newServiceName` or the new route chain.
6. Confirm the old-service repo was not modified unless the user explicitly asked for it.
7. Confirm the report captures the old/new interface comparison result before the caller change.
8. If code changes were made, confirm a commit was created and the branch was pushed to the remote.
9. Run a build or targeted verification command appropriate for the repo.
10. Capture the verification result in the report pack.
11. Confirm the repo was not skipped just because the final route was hidden behind variables, helpers, or imported constants.
12. Confirm any wildcard or catch-all fallback to the old service now has either a verified explicit override for the migrated route or a documented blocker explaining why no safe override was added.
13. Confirm the report or execution artifact records both commit evidence and push evidence when code changes were made.
14. Confirm the report captures `mergeRequestStatus` and either a created MR URL or a direct create-MR URL targeting `dev`.

## Reference

Read `references/change-checklist.md` before editing caller code.
