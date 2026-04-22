# Input Contract

## Mandatory Inputs

These fields are required for every cutover task:

- `oldRoute`
- `newRoute`
- `method`
- `branch`
- `oldServiceName`
- `newServiceName`
- `oldNamespace`
- `newNamespace`
- `workspaceRoot`

## Enforcement Rule

If any mandatory input is missing:

1. first try safe inference or safe defaults
2. continue automatically if the missing value can be inferred with high confidence
3. do not interrupt the workflow for non-blocking ambiguity
4. only stop when the workflow cannot continue safely

## Headless And Batch Rule

When the task is running under a batch runner, headless agent, or any context where user interaction is not expected:

1. do not pause to ask follow-up questions
2. prefer safe inference, safe defaults, and lowest-risk continuation
3. if a true hard blocker remains, end the task quickly with a blocker record instead of waiting for a reply
4. treat the current task as brand new rather than as a continuation of any previous batch, report, or partial attempt
5. use current repository evidence only; do not trust prior `already cut over` or `no change` conclusions without re-verification

## Hard Stop Conditions

Only stop for these cases:

- the missing value cannot be inferred safely
- required credentials are missing or invalid
- a destructive or irreversible action would be needed
- the repo has a branch-conflict or worktree-conflict that cannot be resolved safely
- the repo to be edited cannot be identified with sufficient confidence
- the remote operation required for completion is forbidden or impossible

## Safe Default Rules

- `workspaceRoot`: use the user-provided value; do not guess beyond obvious current workspace conventions
- `oldNamespace` / `newNamespace`: infer from service host conventions when highly consistent
- `oldServiceHint` / `newServiceHint`: if omitted, derive from `serviceName.namespace`, or infer from host names, route prefixes, or nearby repo evidence when highly consistent
- `gatewayRepos`: if omitted, default to `onions-school`, `channel-platform-server`, `channel`, `teacher-tenant`

## Default Decision Principle

When several reasonable paths exist:

1. choose the lowest-risk path
2. prefer completing the full chain over pausing for clarification
3. record the choice and any residual uncertainty in the final anomaly summary

## Recommended Optional Inputs

These are optional but useful when available:

- `gatewayRepos`
- `apisixAdminURL`
- `apisixAdminURLs`
- `apisixAdminKeyEnvVar`

## Why These Inputs Are Mandatory

- `oldRoute`: identifies the old integration target
- `newRoute`: identifies the new target route to switch to
- `method`: prevents same-path cross-method mistakes
- `branch`: controls every repo edit destination
- `oldServiceName`: tells the skill what to replace
- `newServiceName`: tells the skill what to switch to
- `oldNamespace`: helps build the old service host and improves search precision
- `newNamespace`: helps build the new service host and improves search precision
- `workspaceRoot`: tells the skill where local repositories must be searched or cloned
