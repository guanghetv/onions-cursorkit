---
name: sourcegraph-route-locator
description: Use when the user needs cross-repo route search, route call-site discovery, Sourcegraph-based repository identification, or wants to switch from one named service to another, especially when default gateway repos should be prioritized or route evidence may be assembled dynamically, or mentions 搜索调用方, sourcegraph 检索路由, 网关仓库, 查代码位置, locate call sites.
---

# Sourcegraph Route Locator

## Goal

Find the most likely repositories, files, and symbols related to one old route, one new route, and one method, then rank them for the next migration phase across all server-side callers and frontend projects.

## Inputs

- `oldRoute`
- `newRoute`
- `method`
- `oldServiceName`
- `newServiceName`
- `oldNamespace`
- `newNamespace`
- `oldServiceHint`
- `newServiceHint`
- `workspaceRoot`
- Optional `gatewayRepos`

## Input Validation

Prefer to run queries only after these inputs are present:

- `oldRoute`
- `newRoute`
- `method`
- `oldServiceName`
- `newServiceName`
- `oldNamespace`
- `newNamespace`
- `workspaceRoot`

If one is missing, first try safe inference from the prompt, route pattern, repo names, or known host conventions.
Do not interrupt the workflow for non-blocking ambiguity.
Only stop when the missing value cannot be inferred safely or the search target cannot be identified with enough confidence.
If `oldServiceHint` or `newServiceHint` is missing but service name plus namespace is present, derive the host-style hint automatically.

## Default Workflow

1. Validate Sourcegraph access first.
Run the shared helper `whoami` check before search.
If auth fails or the token is invalid, stop and report the Sourcegraph failure explicitly.
Do not silently replace Sourcegraph discovery with local-only grep.

2. Generate route variants.
Use both `oldRoute` and `newRoute`, including raw route, colon-param route, brace-param route, and trimmed path fragments.
Also derive fallback similarity fragments for later frontend inference, such as stable terminal suffixes, service-prefix-stripped variants, and normalized parameterized forms.

3. Build query families.
Run Sourcegraph queries in this order:
- `method + oldRoute`
- `method + newRoute`
- exact `oldRoute` only
- exact `newRoute` only
- `method + stable oldRoute fragment`
- `method + stable newRoute fragment`
- likely RPC or function names derived from the route
- user-provided `gatewayRepos` scoped search
- known gateway repo search
- known backend repo search

Do not use the repositories named by `oldServiceName` or `newServiceName` as caller-discovery query scopes.
Do not use `oldServiceName`, `newServiceName`, their hints, or derived hosts as the primary broad discovery terms for caller repos.
Use them only after a non-service repo has already been nominated, in order to verify whether that repo truly points to the old chain, and later to fetch old/new interface evidence for comparison.

Do not stop when one query returns a few plausible repositories. Continue until:

- the repo set stops growing after the remaining query families
- repo-scoped follow-up searches on newly discovered repos no longer add route-related candidates
- you have checked whether Sourcegraph output was truncated or obviously incomplete

If necessary, rerun with narrower repo filters or additional route variants instead of assuming the first batch is complete.

Prefer `patterntype:literal` for route searches.
Prefer short repo filters such as `repo:teacher` or `repo:onions-school` before trying full-name exact regex repo filters.
When `gatewayRepos` is provided, prioritize those repo filters before generic gateway guesses.
When `gatewayRepos` is omitted, prioritize this default repo set first: `onions-school`, `channel-platform-server`, `channel`, `teacher-tenant`.
Do not stop once those repos are covered.

4. Query through the shared script.
Use `skills/go-cutover-orchestrator/scripts/sourcegraph_graphql.py` from this plugin.

5. Expand every candidate locally.
For every non-noise candidate repo discovered by Sourcegraph:

- ensure the repo exists locally under `workspaceRoot`; clone it first if needed
- search the local repo beyond exact route literals
- use regex and derived patterns to catch alternate spellings and assembled paths
- follow constants, imports, wrapper helpers, and config aliases when the path is built dynamically

At minimum, locally search for combinations of:

- stable route fragments such as `admin-room`, `detail`, `students`, `teachers`
- path parameter variants such as `{id}`, `:id`, `*`, `${id}`, concatenated fragments
- route-prefix declarations such as `router.prefix('/admin-room')` or `prefix: '/admin-room'`
- wildcard or catch-all declarations such as `path: '/*'`, `router.all(...)`, or method-scoped fallback handlers
- wrapper/helper names such as `proxy`, `request`, `client`, `adapter`, `thirdPart`, `serviceAgent`
- generic proxy handlers such as `teacher.proxy()`, `serviceAgent.proxy()`, or `<service>.proxy()`
- gateway patterns such as `routePattern`, `replacePath`, `proxyForReplaceUrl`, `proxyForUserId`
- method-specific usage around the route, not just the route string itself

Only after a repo is nominated by route or gateway evidence should you use old/new service names, namespaces, derived hosts, or host constants to verify the chain inside that repo.

If the route prefix is stored in a variable or config object, follow the local symbol chain until you can classify the repo with concrete evidence.
If a repo combines a matching route-family prefix with a method-scoped wildcard or catch-all proxy to the old service, treat that as concrete old-route-chain evidence even when the exact child path literal is absent. Do not drop the repo as `out of scope` until you have checked whether the target route is covered by the wildcard and whether an explicit override already switches it to the new service.

6. Classify results.
Assign each hit to one of these buckets:
- old-service reference repo
- new-service implementation repo
- gateway or proxy repo
- other backend caller repo
- frontend or client project
- low-confidence noise

Classification must be based on the strongest available local evidence after Sourcegraph nomination, not on Sourcegraph snippets alone.
The repos named by `oldServiceName` and `newServiceName` must never be promoted into caller-edit targets merely because they match service-name or host-name evidence.

7. Rank candidates.
Prefer exact method matches, route constant definitions, client wrappers, repo-layer callers, and gateway configs over generic string matches.

Treat these as server-side cutover targets when evidence is present:

- gateway or proxy repos that still forward traffic into `oldServiceName` or its old route chain
- backend service repos that directly call `oldServiceName`

Treat the repo named by `oldServiceName` as a reference repo by default:

- use it to confirm old route behavior
- use it to confirm old client or host patterns
- use it to compare old and new route chains
- do not treat it as a default code-edit target

Treat the repo named by `newServiceName` as an implementation reference repo by default:

- use it to confirm the new route behavior
- use it to locate the new interface definition or implementation
- do not treat it as a default caller-edit target

Do not classify a repo as `old-service reference repo` or `other backend caller repo` unless at least one hit shows real old-service call evidence, such as:

- old host or service discovery name
- old client import or old proto package
- direct HTTP client call to the old route
- repo adapter or third-party wrapper that still targets the old service

Treat a repo as `gateway or proxy repo` when the evidence shows route forwarding or proxy behavior, such as:

- `proxyForReplaceUrl(...)`
- route registration or outward-facing path declarations
- module-level route prefix plus wildcard or catch-all forwarding such as `prefix: '/admin-room'` with `path: '/*'`
- generic proxy handler bound to the old service such as `teacher.proxy()` or `serviceAgent.proxy()`
- traffic comparison or canary rewrite config
- `routePattern` plus `replacePath`
- middleware or config that forwards traffic but does not own the downstream old-service client call

Gateway and proxy repos remain in scope for server-side cutover if they still forward to the old service chain.
If the repo is explicitly listed in `gatewayRepos`, use that as a prioritization hint, not as sufficient proof by itself. Concrete local forwarding evidence is still required.

8. Emit structured output.
Produce a markdown summary and a JSON artifact with candidate repos, files, matched lines, reason, and confidence.
If the search cannot prove an outward-facing gateway route, also emit fallback route seeds for later frontend analysis: `same_suffix`, `same_action_tail`, `same_resource_nouns`, and `normalized_param_shape`.

For frontend or client hits, only output:

- project or repository name
- matched file path
- why the project is relevant

Do not infer the actual test entrypoint, page flow, or feature scope from Sourcegraph search alone.
That work belongs to the local analysis phase in `frontend-entry-finder`.

For service-side cutover, also output:

- the most likely `newServiceName` interface definition or implementation file
- the most likely `oldServiceName` interface definition or implementation file
- enough evidence to compare route, method, parameters, and business intent

## Ranking Rules

- Highest confidence: exact `method + oldRoute` or `method + newRoute` matches in client wrappers, proto/http annotations, gateway configs
- Medium confidence: route fragment + service name in repo or adapter code
- Lower confidence: route fragment only in docs, tests, or comments
- When confidence is otherwise equal, prioritize repos that match user-provided `gatewayRepos`, or the default gateway repo set when none was provided

Discard pure documentation hits unless they are the only evidence available.
Discard frontend hits from the server-side cutover buckets.

## Validation

Before handing off:

1. Confirm every high-confidence result includes repo, file path, and matched line preview.
2. Confirm each server-side cutover candidate includes either real old-service call evidence or real old-route forwarding evidence.
3. Confirm the repo corresponding to `oldServiceName` is checked as a reference repo when relevant.
4. Confirm at least one server-side cutover candidate exists, or explicitly mark the search as blocked.
5. Separate gateway candidates from frontend project candidates instead of merging them.
6. Do not claim test scope from Sourcegraph evidence alone.
7. Confirm the locator output contains both new-service and old-service interface evidence for comparison before cutover.
8. Confirm every repo nominated by Sourcegraph was either locally verified or explicitly marked unverified with a reason.
9. Confirm repos were not dropped only because the full route string was assembled dynamically, hidden behind a route prefix, or covered by a wildcard/catch-all proxy.
10. Confirm `gatewayRepos` was applied as a ranking hint when provided, or that the default gateway repo set was used when omitted.

## Reference

Read `references/query-playbook.md` for query templates and normalization rules.
