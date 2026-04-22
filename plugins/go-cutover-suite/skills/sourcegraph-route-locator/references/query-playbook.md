# Query Playbook

## Normalize The Routes

Generate these variants before searching:

- old route raw form
- new route raw form
- colon-param form
- brace-param form
- wildcard or routePattern-friendly form such as `*` fragments when the codebase uses glob-like matching
- template-string-friendly form such as stable prefix + `${id}` + stable suffix
- plain stable fragment
- trailing stable fragment

If the route contains IDs or dynamic segments, search both `oldRoute` and `newRoute`, including full route and stable fragments.

## Query Order

0. `whoami` auth check through the shared helper
1. Exact method and `oldRoute`
2. Exact method and `newRoute`
3. Exact `oldRoute` only
4. Exact `newRoute` only
5. Exact method and stable fragment
6. Old service name, client wrapper name, or domain hint plus oldRoute fragment
7. New service name, client wrapper name, or domain hint plus newRoute fragment
8. Derived function names or RPC names
9. Repo-scoped gateway search
10. Repo-scoped backend search

Do not stop after the first zero-result query. The first exact query is only the narrowest probe.
Prefer `patterntype:literal` for route and path searches.

## Result Convergence

Treat Sourcegraph discovery as a convergence loop, not a single search:

1. run the full query order
2. deduplicate repositories from all result sets
3. if new repositories appear, run repo-scoped follow-up searches inside each of them
4. if output looks truncated or suspiciously sparse, widen the route variant set and rerun
5. stop only when the repo set is stable and every candidate has a next action

Every nominated repository must end in one of these states:

- local verification required
- already verified relevant
- already verified irrelevant
- blocked because the repo is unavailable locally and clone failed

Do not claim "all callers found" until every candidate repo has been processed.

## Query Templates

Use Sourcegraph query syntax inside the GraphQL `search(query: ...)` field.

Sourcegraph is only for:

- locating candidate repositories
- locating matched files or symbols
- confirming which projects are relevant to the route

Sourcegraph is not for:

- deciding the final frontend test scope
- deciding which page is the real user entrypoint
- deciding the exact manual test flow

After a frontend or client project is identified, switch to local repo analysis. If the repo is missing under `workspaceRoot`, clone it first and then inspect local code.

After any backend, gateway, or frontend repo is identified, do a local expansion search. Do not rely on Sourcegraph snippets alone for final inclusion or exclusion.

When the user provides service names, treat `oldServiceName` and `newServiceName` as first-class search inputs. Prefer exact service-name strings before broader business keywords.

For this Sourcegraph instance:

- prefer `repo:teacher`, `repo:onions-school`, `repo:activityh5` style repo filters first
- do not rely on `repo:^full/repo/name$` exact regex filters for content search unless you have already verified they work
- for route strings, prefer `patterntype:literal`

### Old route exact match

```text
type:file patterntype:literal repo:<oldServiceName> "<oldRoute>"
```

### New route exact match

```text
type:file patterntype:literal repo:<newServiceName> "<newRoute>"
```

### Method plus old route

```text
type:file patterntype:literal "<METHOD>" "<oldRoute>"
```

### Method plus new route

```text
type:file patterntype:literal "<METHOD>" "<newRoute>"
```

### Exact old route only

```text
type:file patterntype:literal "<oldRoute>"
```

### Exact new route only

```text
type:file patterntype:literal "<newRoute>"
```

### Stable fragment plus method

```text
type:file patterntype:literal "<METHOD>" "<stable-route-fragment>"
```

### Gateway configs

```text
type:file patterntype:literal (repo:onions-school OR repo:teacher-tenant OR repo:apisix) "admin-room/students"
```

### Old-service and backend caller search

```text
type:file patterntype:literal ("<oldServiceName>" OR "<oldServiceHint>" OR "<old-client-name>") "admin-room/students"
```

### Service hints

```text
type:file patterntype:literal "<oldServiceName>" OR "<newServiceName>" OR "<oldServiceHint>" OR "<newServiceHint>"
```

## Local Expansion After Sourcegraph

Once a repo is nominated, search locally with multiple shapes instead of exact literals only:

- exact old/new route strings
- stable route fragments such as `"admin-room"` and `"detail"`
- routePattern or wildcard forms such as `"/admin-room/*/detail"`
- template-string forms such as `` `/admin-room/${id}/detail` ``
- host or config forms such as `teacher.teacherschool`, `teacher-school.teacherschool`, `teacherHost`, `teacherSchoolHost`
- wrapper/helper forms such as `proxyForReplaceUrl`, `proxyForUserId`, `request.get`, `client.get`, `thirdPart`, `serviceAgent`

When the route prefix is variable-driven:

1. find the call site that uses the fragment or helper
2. trace the imported constant, config object, or service client definition
3. reconstruct the effective target path from local evidence

Do not discard a repo merely because the full final path is not present as one literal string.

## Ranking Heuristics

- Prefer code over docs.
- Prefer config or handler files over tests.
- Prefer exact route constants over vague string fragments.
- Prefer hits that include both route and method in the same file.

## Classification Heuristics

### Old-service repo

Treat the repo that matches `oldServiceName` as an explicit old-service reference target when the route still exists there or when it still forwards traffic into the old route chain.

Typical evidence:

- old route registration
- route rewrite or canary config still anchored in `teacher`
- service host or middleware config that still sends traffic through `oldServiceName`

Use this repo to understand and compare the old chain.
Do not modify this repo by default unless the user explicitly asks to change the old service itself.

### Gateway or proxy repo

Treat the repo as gateway when the evidence shows route exposure or forwarding:

- `proxyForReplaceUrl(...)`
- route registration such as `path: '/public/...`
- `routePattern` with `replacePath`
- canary or traffic-comparison middleware
- reverse proxy or API gateway config

These repos are still in scope for server-side cutover if they forward traffic through the old service chain.

### Other backend caller repo

Treat the repo as backend caller only when the evidence shows a real downstream dependency on the old service:

- old host name or service name matching `oldServiceName`
- old client constructor or old endpoint constant
- direct HTTP request to the old route
- repo-layer adapter or third-party wrapper targeting the old service

### Frontend or client repo

Treat frontend or client repos as local-analysis targets unless the user explicitly asks to edit them.

Sourcegraph may nominate the project, but the final test scope must come from local code search after the project exists under `workspaceRoot`.

If a repo already points to `newServiceName`, `newServiceHint`, or the new route chain, classify it as already cut over, not as pending server-side work.
