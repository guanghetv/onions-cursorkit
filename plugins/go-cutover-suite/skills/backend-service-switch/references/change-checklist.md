# Change Checklist

## Before Editing

- Confirm the repository is the correct server-side cutover repo.
- Confirm the route and method match the user request.
- Confirm the branch workflow is `master -> target branch`.
- Check whether the target is:
  - gateway/proxy repo
  - other backend caller repo
- Confirm the repo still contains `oldServiceName` or old-route-chain evidence.
- Confirm this repo was selected after Sourcegraph discovery and local verification, not only from one exact literal match.
- If the repo is frontend or client only, reclassify it out of the backend-switch phase.
- Treat the repo matching `oldServiceName` as reference-only unless the user explicitly asks to edit it.
- If the target branch already contains existing code changes or uncommitted changes, treat them as part of the current task context and continue on top of them.
- If the repo has uncommitted changes on a different branch, stop and report conflict risk instead of auto-switching.
- Find the target interface in `newServiceName` first.
- Find the matching interface in `oldServiceName` second.
- Compare route, method, parameters, request/response shape, and business meaning before editing any caller.
- If the old and new interfaces cannot be treated as the same route for migration, do not cut the caller.
- Before deciding "no change needed", locally search the repo with multiple patterns:
  - exact old/new route strings
  - stable route fragments
  - helper wrappers, client aliases, and adapter names
  - host/config variables and template-string path construction
  - routePattern/replacePath style forwarding
- If the path is assembled dynamically, follow the local symbol chain until you can prove the repo is already cut over or out of scope.

## Common Edit Targets

- HTTP client base URL or service discovery name
- route path prefix
- gateway or proxy forwarding target
- old-service route registration or rewrite config
- proto or generated client imports
- repo adapter or third-party wrapper methods
- request or response converters needed for compatibility

## Do Not Change

- unrelated methods on the same path
- frontend-facing public routes
- dependency versions
- generated files unless the repo workflow requires regeneration

## Verification Targets

- repo is on the requested branch
- report whether bootstrap ran in clean mode or continued on top of existing target-branch work
- edited call sites still map to the same business action
- edited call sites changed from `oldServiceName` or old route chain to `newServiceName` or new route chain
- the report contains a clear old/new interface comparison result
- if changes were made, a commit exists and the branch has been pushed
- if changes were made, commit/push happened automatically without waiting for extra user confirmation
- if changes were made, execution evidence records both the created commit and the completed push
- if no changes were needed, the repo is marked `already cut over`
- if no changes were needed, the report still explains the exact local evidence for `already cut over` or `out of scope`
- old-service repo remained unchanged unless explicitly requested
- build or targeted test command succeeds
- report pack captures changed files and risks
