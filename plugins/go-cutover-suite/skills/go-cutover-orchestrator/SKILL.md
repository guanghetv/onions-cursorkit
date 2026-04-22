---
name: go-cutover-orchestrator
description: Use when the user wants to switch gateway or proxy repos and other backend services from an old service chain to a new Go service, trace or infer frontend/client test entry points after route cutover, especially when one interface may be exposed through multiple gateways or APISIX admin endpoints, or mentions 路由切换, 灰度完成后切调用, 切老接口到 go, 网关暴露路由, 梳理测试入口, full-chain cutover.
---

# Go Cutover Orchestrator

## Goal

Drive one route cutover from the user-provided old route and old service chain to the user-provided new route and new Go service across all in-scope server-side callers, while treating the old-service repo as reference-only, then trace the outward route and locate frontend or client entry points for testing.
Default to uninterrupted execution: infer, continue, verify, commit, push, and finish the full chain without pausing for routine user confirmation.
Treat every invocation as a fresh task: do not rely on previous batch results, previous report packs, or prior conversation conclusions as a reason to skip discovery, verification, edits, or reporting.

## Required Input

Provide these inputs up front:

- `oldRoute`: 重构前路由，例如 `/admin-room/students/{studentId}/all`
- `newRoute`: 重构后路由，例如 `/teacher-school/admin-room/students/{studentId}/all`
- `method`: HTTP method, required for exact matching
- `branch`: target branch name for every changed repository
- Treat `branch` as the target feature branch name to be prepared from `master` for every edited repository in this task
- `oldServiceName`: old service name or repo identity, such as `teacher`
- `newServiceName`: new Go service name or repo identity, such as `teacher-school`
- `oldNamespace`: old service namespace, such as `teacherschool`
- `newNamespace`: new service namespace, such as `teacherschool`
- `oldServiceHint`: optional old service domain, client name, host, or repo hint. If omitted, derive from `oldServiceName + "." + oldNamespace`
- `newServiceHint`: optional new Go service prefix, domain, host, or proto/client hint. If omitted, derive from `newServiceName + "." + newNamespace`
- `workspaceRoot`: local workspace root, such as `~/work`
- `gatewayRepos`: optional known gateway, proxy, or route-exposure repos. Default to `onions-school`, `channel-platform-server`, `channel`, `teacher-tenant`
- `apisixAdminURL`: optional APISIX Admin API route-list endpoint, used as a parallel outward-route evidence source during gateway tracing and frontend scope analysis when provided
- `apisixAdminURLs`: optional list of APISIX Admin API route-list endpoints when the same interface may be exposed by multiple APISIX gateways; when provided, all of them should be checked
- `apisixAdminKeyEnvVar`: optional env var name that stores APISIX `X-API-KEY`, default `APISIX_ADMIN_KEY`
- `SOURCEGRAPH_TOKEN` should normally come from the environment or the independent `sourcegraph-token` refresh flow rather than being pasted into the prompt

## Input Contract

These fields are mandatory:

- `oldRoute`
- `newRoute`
- `method`
- `branch`
- `oldServiceName`
- `newServiceName`
- `oldNamespace`
- `newNamespace`
- `workspaceRoot`

If any mandatory field is missing, infer it first when safe from the prompt, route pattern, repo naming, or known host conventions.
Ask only when a mandatory field cannot be inferred safely enough to avoid a hard blocker.
Do not start Sourcegraph search, local repo search, branch creation, file edits, or report generation until all hard blockers are resolved.
If `oldServiceHint` or `newServiceHint` is missing but both service name and namespace are present, derive the default host-style hint automatically.

Recommended but optional:

- `gatewayRepos`
- `apisixAdminURL`
- `apisixAdminURLs`
- `apisixAdminKeyEnvVar`
- `oldServiceHint`
- `newServiceHint`

If `gatewayRepos` is omitted, default to `onions-school`, `channel-platform-server`, `channel`, `teacher-tenant`.
Use `gatewayRepos` as strong priors for classifying gateway layers, but never treat them as the only allowed gateway evidence.
If `oldServiceHint` is omitted, default to `oldServiceName.oldNamespace`.
If `newServiceHint` is omitted, default to `newServiceName.newNamespace`.
Use `apisixAdminURL` and `apisixAdminKeyEnvVar` when APISIX may be part of the outward exposure chain.
If `apisixAdminURL` or `apisixAdminURLs` is provided, treat APISIX as a parallel gateway-evidence source during gateway tracing and frontend scope analysis rather than a dead-end-only fallback.
If both `apisixAdminURL` and `apisixAdminURLs` are present, treat them as one deduplicated list of APISIX gateway sources and check all of them.

## Shared Scripts

Shared scripts live in `skills/go-cutover-orchestrator/scripts/` within this plugin package.

- `sourcegraph_graphql.py`: query Sourcegraph through GraphQL
- `repo_bootstrap.sh`: ensure `master -> branch` workflow in a local repo
- `gitlab_clone_or_update.sh`: clone or update missing repos under `~/work`
- `gitlab_create_mr.py`: create or detect a GitLab Merge Request targeting `dev`
- `gitlab_push_and_create_mr.py`: push the branch and create a GitLab Merge Request targeting `dev` in the same command

**REQUIRED SUB-SKILL:** Use `apisix-admin-route-finder` whenever APISIX endpoints are provided, so APISIX evidence can be collected in parallel with code-gateway tracing.

Read `references/report-contract.md` before writing final outputs.
Read `references/script-env.md` before invoking the shared scripts.
Read `references/mvp-scope.md` when deciding whether a task is inside the first release.
Read `references/input-contract.md` before starting any cutover task.

## Workflow

1. Normalize the routes.
Search both `oldRoute` and `newRoute`, including transformed variants such as `{studentId}` and `:studentId`.
Also derive stable suffix fragments for fallback matching, such as:
- same terminal suffix like `/students/{studentId}/all`
- service-prefix-stripped variants such as removing `/teacher-school`
- normalized parameter forms like `{id}`, `:id`, `${id}`

2. Validate environment.
Check `SOURCEGRAPH_URL`, `SOURCEGRAPH_TOKEN`, and `GITLAB_URL`.
Before discovery begins, call the independent `sourcegraph-token` script to validate or refresh the Sourcegraph token automatically when possible, then continue with the fresh token.
Treat `apisixAdminKeyEnvVar` as the name of an environment variable, not the secret value itself.
For GitLab access, prefer `GITLAB_TOKEN`; otherwise fall back to SSH clone URLs.

3. Run companion skills in order.
- Use `sourcegraph-route-locator` to find candidate backend repos and files.
- Pass `gatewayRepos` into discovery so gateway, proxy, and route-exposure repos can be recognized earlier and ranked ahead of generic backend hits.
- Do not treat the repositories named by `oldServiceName` or `newServiceName` as caller-discovery targets. Use them only later for interface verification and old/new contract comparison.
- Do not treat the first few Sourcegraph hits as the full answer. Keep expanding queries, deduplicating repositories, and checking whether more route-related repos remain until the candidate set is stable.
- After Sourcegraph has produced the candidate set, ensure every non-noise candidate repo exists locally under `workspaceRoot`, then inspect the local code before deciding whether it is in scope, already cut over, or a false positive.
- Local inspection is mandatory even when Sourcegraph already found exact hits. Use local indexed search and code navigation to catch different spellings and indirections, such as route fragments, regex-style route patterns, helper wrappers, config constants, template strings, host variables, service-agent aliases, imported API constants, and prefix variables that assemble the final path dynamically.
- Do not rely on exact literal route strings alone during local inspection. Also search with regex and derived patterns for:
  - old/new stable route fragments
  - route-prefix declarations such as `router.prefix('/admin-room')` or `prefix: '/admin-room'`
  - wildcard or catch-all declarations such as `path: '/*'`, `router.all(...)`, or method-scoped fallback handlers
  - wrapper/helper names such as proxy, request, client, serviceAgent, thirdPart, adapter
  - generic proxy handlers such as `teacher.proxy()`, `serviceAgent.proxy()`, or `<service>.proxy()`
  - routePattern/replacePath style forwarding
  - method-specific call shapes like `get(...)`, `post(...)`, `put(...)`, `delete(...)`
- Do not use `oldServiceName`, `newServiceName`, their namespaces, or derived hosts as primary caller-discovery terms. Use them only to verify that an already nominated non-service repo truly points to the old chain, or to compare service contracts.
- If a candidate repo has variable-based path construction, follow the local symbol chain until you can classify it with evidence. Do not drop the repo merely because the final URL is not written as one full literal string.
- If a candidate repo combines a matching route-family prefix with a method-scoped wildcard or catch-all proxy to the old service, treat that as concrete old-route-chain evidence even when the exact child path literal is absent. Do not mark the task `out of scope` for that repo until you have checked whether the target route is covered by the wildcard and whether an explicit override already switches it to the new service.
- Before switching any caller, inspect the candidate interface in `newServiceName` first using `newRoute`, then inspect the matching interface in `oldServiceName` using `oldRoute`.
- Compare old/new route, method, parameters, and core logic.
- Only continue to caller cutover when the old and new interfaces can be treated as the same route for migration purposes.
- Use `backend-service-switch` to update all in-scope server-side repos that still depend on the old service or old route chain.
- Use `gateway-route-tracer` to trace the outward-facing route and aggregate route evidence from both code gateways and APISIX gateways.
- If `apisixAdminURL` or `apisixAdminURLs` is provided, require `gateway-route-tracer` to invoke `apisix-admin-route-finder` once per APISIX endpoint and merge the results, even when code gateways already produced plausible outward routes.
- Do not stop after the first code gateway or APISIX source produces one plausible outward route. Continue until every discovered code gateway source and every provided APISIX source has a verification outcome or is explicitly marked unavailable.
- If `gateway-route-tracer` cannot prove an outward-facing route from either code gateways or APISIX, require it to emit a dead-end note plus fallback route hypotheses derived from the normalized suffix, method, route-shape similarity, and any route-family evidence gathered from both source types.
- Use `frontend-entry-finder` to locate frontend or client entry points from local repositories using the merged route-evidence set.
- When no outward-facing route is confirmed, let `frontend-entry-finder` search by fallback route hypotheses such as same suffix, same terminal action, same resource nouns, and same parameterized shape. All such candidates must be labeled speculative rather than confirmed.

4. Write the report pack.
Create a timestamped directory under `~/work/_ai_reports/go-cutover/` and populate the required markdown and JSON artifacts.
All Markdown reports in the pack must use Chinese headings, Chinese field labels, and Chinese explanatory text.
Treat report-pack creation as part of the core task, not as optional polish. Do not wait for the user to ask for the report pack explicitly.

4.5. Handle Merge Requests for changed repos.
For every server-side repo that produced real code changes and was pushed successfully, create or attempt to create a Merge Request targeting `dev`.
Prefer a real created MR URL when GitLab API or authenticated web automation is available.
If automatic creation is not possible, still record:
- `mergeRequestStatus`
- blocker reason
- direct create-MR URL such as `.../-/merge_requests/new?merge_request[source_branch]=<branch>&merge_request[target_branch]=dev`
Do not treat Merge Request handling as optional post-processing.

5. Summarize the result.
Report changed repos, traced outer routes, frontend entry candidates, remaining risks, a concise Chinese feature-flow summary for testers, a short Chinese anomaly summary, the report-pack directory path, and the Merge Request result for every changed repo.

## Execution Rules

- Treat one user request as one route cutover task.
- Treat every new task as a fresh cutover from scratch, even if a similar route or the same route was handled before in another batch or report.
- Treat the absence of a user reply during execution as the normal case, especially in batch or headless runs. Do not pause waiting for confirmation on routine decisions.
- If mandatory input is missing, infer it first when safe and continue without interrupting the workflow.
- Keep the public API stable unless the user explicitly asks to change it.
- Only modify server-side callers during the switch phase.
- Treat these as in-scope server-side callers:
  - gateway or proxy repos that still forward traffic into `oldServiceName` or its old route chain
  - other backend repos that still call `oldServiceName` directly
- In gateway or proxy repos, treat `route prefix + wildcard/catch-all + old-service proxy` as real forwarding evidence, not as a weak hint. Such repos stay in scope until the migrated route is shown to be explicitly overridden to the new service, still falling through to the old service, or blocked by ambiguous routing order.
- Treat `gatewayRepos` as explicit user knowledge about which repos likely serve gateway or route-exposure roles. When omitted, use the default gateway repo set. In all cases, still require concrete local evidence before marking a repo in scope.
- Treat APISIX Admin API evidence as a parallel gateway-evidence source whenever `apisixAdminURL` or `apisixAdminURLs` is provided. It must still be tied back to the migrated route by path, method, or route-family evidence.
- One migrated interface may be exposed through multiple code gateways, multiple APISIX gateways, or both. Keep all distinct outward routes and group them by gateway source instead of collapsing them into a single guessed answer.
- If APISIX endpoints are provided for the task, do not skip them merely because a code gateway already produced one outward-facing route. The final route evidence must reflect both code-gateway and APISIX checks.
- Treat the repo named by `oldServiceName` as reference-only unless the user explicitly asks to modify the old service itself.
- Treat the repo named by `newServiceName` as implementation-reference only during caller discovery. Use it to confirm the new contract, not as a default caller-edit target.
- Treat frontend and client repos as trace-only unless the user explicitly asks to edit them.
- Match `oldRoute + newRoute + method + oldServiceName + newServiceName` together before editing.
- If a repo is missing locally, clone it under `workspaceRoot` and continue.
- After creating or switching the task branch in a service-side repo, ensure the branch exists on the remote.
- For new cutover work, default every edited repo to `master -> branch`. Do not ask whether to reuse the current local feature branch as the working baseline.
- If the local branch exists but the remote branch does not, push it automatically without asking.
- If the target branch already contains existing code changes or uncommitted changes, treat them as the normal working baseline for this task and continue on top of them.
- If a repo has uncommitted changes on a different branch, prefer an isolated worktree rooted at `~/.config/superpowers/worktrees/<repo>/<branch>` and continue there from `master -> branch` instead of stopping to ask the user. Only report a blocker if the isolated worktree cannot be created or bootstrapped safely.
- If a server-side repo ends this task with real code changes, do not ask whether to commit or push. Automatically stage only the cutover-relevant files, create a commit, and push the target branch.
- If a server-side repo ends this task with real code changes, do not stop after push. Continue to create or attempt to create a Merge Request targeting `dev`, then write the result and link into the report pack.
- Do not treat report generation as optional follow-up work. A task is not complete until the required report pack exists on disk and is ready to hand back to the user.
- If the target branch already had baseline changes before this task, do not blindly stage unrelated files. Commit only the files directly touched or extended by the cutover, unless the repo workflow requires a broader staged set for correctness.
- If multiple candidate repos remain after tracing, keep all candidates and rank them instead of guessing.
- Never write secrets into scripts, reports, or source files.
- Do not use local workspace grep as a silent replacement for failed Sourcegraph discovery.
- Do not exclude gateway repos or proxy repos from cutover just because they are forwarding layers. If they still participate in the old service route chain, they are in scope for server-side cutover.
- Do not modify the old-service repo's caller code by default. Use it only to confirm old-route behavior, old contracts, and comparison evidence.
- Use Sourcegraph only to locate relevant projects and files. Determine frontend or client test scope only from local repositories after the project exists under `workspaceRoot`.
- Do not reuse old report packs, old batch state, or previous `already cut over` conclusions as execution shortcuts. Re-run discovery and local verification against the current repositories every time.
- Sourcegraph discovery is incomplete until every candidate repo from every useful query family has a local verification outcome. Each candidate must end in exactly one state: `changed`, `already cut over`, `out of scope`, `false positive`, or `blocked`, with evidence.
- Do not output `out of scope` for a gateway or proxy repo if a matching route-family prefix plus wildcard/catch-all old-service proxy still covers the target method. In that case the repo must end as `changed`, `already cut over`, or `blocked`.
- Do not silently stop after editing only the first few direct callers. If Sourcegraph or local expansion suggests more route-related backend repos, continue until every candidate has been verified locally.
- Always verify the `newServiceName` interface first, then verify the `oldServiceName` interface, and only switch caller code after confirming route, method, parameter shape, and business meaning are aligned.
- Do not stop to ask about non-blocking issues when a safe default lets the workflow continue.
- Finish the full chain first, then present a short Chinese anomaly summary at the end.
- When multiple reasonable execution paths exist, choose the lowest-risk path automatically and continue.
- Ask only for true hard blockers such as invalid credentials, unsafe destructive conflicts, or an unidentifiable target repo.
- In batch or headless execution, do not ask even for clarifications that would normally be acceptable in chat. Either infer safely and continue, or end the task with a clear blocker record.
- If existing uncommitted changes are already on the target branch, treat them as part of this task's working context and continue through verification, frontend scope analysis, report generation, and commit/push without asking.
- Treat commit or push failure after a real code change as a task failure or blocker, not as an optional follow-up for the user.
- If no gateway outward route can be confirmed, do not stop frontend scope analysis. Continue with local frontend inference using route-similarity heuristics such as same suffix, same trailing action segment, same resource nouns, and same normalized parameter pattern.
- When using fallback route inference, clearly separate `confirmed` candidates from `speculative` candidates in both the report pack and the user-facing summary.
- If one route is exposed by multiple gateways, keep all `confirmed` gateway-specific outward routes, and let frontend scope analysis consider the union rather than the first hit only.
- If the task ultimately cannot continue because of a true hard blocker, fail fast with a concise blocker summary in the report pack instead of waiting indefinitely for user input.
- If the current repositories prove the route is already cut over, you may output `already cut over`, but only after fresh verification in this run rather than by trusting any earlier run.

## Validation

Before calling the task complete:

1. Confirm each changed backend repo is on the requested branch.
2. Confirm each changed backend repo has a corresponding remote branch.
3. Confirm each changed backend repo was prepared from `master -> branch`, either in-place when safe or through an isolated worktree when the current checkout could not be reused safely.
4. Confirm every edited call site matches the requested HTTP method.
5. Confirm every changed server-side repo had real `oldServiceName` or old-route-chain evidence before the edit.
6. Confirm the repo named by `oldServiceName` was treated as reference-only unless the user explicitly requested changes there.
7. Confirm the result covers all discovered non-old-service server-side callers, not just one backend repo, and that every discovered candidate repo has a local verification result.
8. Confirm at least one outward-facing route or an explicit dead-end note exists.
9. Confirm frontend entry output includes project, local file, reason, test suggestion, and confidence source such as `confirmed-by-gateway-route` or `speculative-by-similar-route`.
10. Confirm changed service-side repos were committed and pushed unless they were already cut over with no code diff.
11. Confirm the report includes a clear old/new interface comparison result before any caller switch.
12. Confirm the report pack matches `references/report-contract.md`.
13. Confirm APISIX evidence, when used, is recorded as `confirmed-by-apisix` or `speculative-by-apisix-route-family` instead of being mixed into generic notes.
14. Confirm every discovered code gateway source and every provided APISIX source ended in one of these states: `confirmed-route`, `fallback-only`, `dead-end`, `blocked`, or `unavailable`.
15. Confirm no repo was labeled `out of scope` before checking for route-family prefix coverage, wildcard/catch-all handlers, and generic old-service proxy fallbacks.
16. Confirm `artifacts/execution.json` contains commit and push evidence for every task that produced real code changes.
17. Confirm the report pack records a Merge Request result for every changed repo, including a direct URL when available.
18. Confirm the final user-facing summary explicitly includes the report-pack directory path and Merge Request links or create-MR links, instead of assuming the user will ask for them later.

## Example Prompts

- “把 `/admin-room/students/{studentId}/all` 切到 `/teacher-school/admin-room/students/{studentId}/all`，从 `teacher.teacherschool` 切到 `teacher-school.teacherschool`，新分支叫 `feat/cutover-admin-room`，并帮我梳理前端测试入口。”
- “把这个接口从 `oldRoute` 切到 `newRoute`，从 `oldServiceName + oldNamespace` 切到 `newServiceName + newNamespace`，并追到网关暴露路由和前端功能入口。”

Use this full template when the user wants a copy-and-fill prompt:

```text
/go-cutover-orchestrator
SOURCEGRAPH_URL: <可选，默认 https://sourcegraph.yc345.tv>
# SOURCEGRAPH_TOKEN: 通常不必手填，默认从环境变量或自动刷新获取
GITLAB_URL: <可选，默认 https://gitlab.yc345.tv>

oldRoute: <old route>
newRoute: <new route>
method: <GET|POST|PUT|DELETE>
branch: <branch>
oldServiceName: <old service name>
newServiceName: <new service name>
oldNamespace: <old namespace>
newNamespace: <new namespace>
workspaceRoot: <local workspace root>

gatewayRepos: <optional known gateway/proxy repos>
apisixAdminURL: <optional APISIX admin routes endpoint>
apisixAdminURLs: <optional multiple APISIX admin routes endpoints>
apisixAdminKeyEnvVar: <optional env var name for APISIX X-API-KEY>
```

Advanced optional overrides:

```text
oldServiceHint: <optional old service hint; defaults to oldServiceName.oldNamespace>
newServiceHint: <optional new service hint; defaults to newServiceName.newNamespace>
```

Use this Chinese filled-template version when the user prefers Chinese field guidance:

```text
/go-cutover-orchestrator
SOURCEGRAPH_URL: <可选，默认 https://sourcegraph.yc345.tv>
# SOURCEGRAPH_TOKEN: 通常不必手填，默认从环境变量或自动刷新获取
GITLAB_URL: <可选，默认 https://gitlab.yc345.tv>

oldRoute: <重构前路由>
newRoute: <重构后路由>
method: <请求方法，如 GET>
branch: <分支名>
oldServiceName: <老服务名>
newServiceName: <新服务名>
oldNamespace: <老服务 namespace，如 teacherschool>
newNamespace: <新服务 namespace，如 teacherschool>
workspaceRoot: <本地项目根目录，如 ~/work>

gatewayRepos: <可选，网关/代理/暴露层仓库，默认 onions-school, channel-platform-server, channel, teacher-tenant>
apisixAdminURL: <可选，APISIX Admin API 的 routes 地址>
apisixAdminURLs: <可选，多个 APISIX Admin API 的 routes 地址，逗号分隔>
apisixAdminKeyEnvVar: <可选，保存 APISIX X-API-KEY 的环境变量名，默认 APISIX_ADMIN_KEY>
```

高级可选覆盖：

```text
oldServiceHint: <可选，老服务域名/host/client/proto线索，不填则默认 oldServiceName.oldNamespace>
newServiceHint: <可选，新服务域名/host/client/proto线索，不填则默认 newServiceName.newNamespace>
```

Use this Chinese real example when the migration is from `teacher` to `teacher-school`:

```text
/go-cutover-orchestrator
SOURCEGRAPH_URL: https://sourcegraph.yc345.tv
# SOURCEGRAPH_TOKEN: 自动检查/刷新
GITLAB_URL: https://gitlab.yc345.tv

oldRoute: /admin-room/list
newRoute: /teacher-school/admin-room/list
method: GET
branch: feat/m-6920925476
oldServiceName: teacher
newServiceName: teacher-school
oldNamespace: teacherschool
newNamespace: teacherschool
workspaceRoot: ~/work

gatewayRepos: onions-school, channel-platform-server, channel, teacher-tenant
apisixAdminURL: https://school-test.example.com/apisix/admin/routes
apisixAdminURLs: https://school-test.example.com/apisix/admin/routes, https://school-open.example.com/apisix/admin/routes
apisixAdminKeyEnvVar: APISIX_ADMIN_KEY
```

Use this Chinese real example when the route contains path parameters:

```text
/go-cutover-orchestrator
SOURCEGRAPH_URL: https://sourcegraph.yc345.tv
# SOURCEGRAPH_TOKEN: 自动检查/刷新
GITLAB_URL: https://gitlab.yc345.tv

oldRoute: /admin-room/{ref}/detail
newRoute: /teacher-school/admin-room/{ref}/detail
method: GET
branch: feat/m-6920925476
oldServiceName: teacher
newServiceName: teacher-school
oldNamespace: teacherschool
newNamespace: teacherschool
workspaceRoot: ~/work

gatewayRepos: onions-school, channel-platform-server, channel, teacher-tenant
apisixAdminURL: https://school-test.example.com/apisix/admin/routes
apisixAdminURLs: https://school-test.example.com/apisix/admin/routes, https://school-open.example.com/apisix/admin/routes
apisixAdminKeyEnvVar: APISIX_ADMIN_KEY
```
