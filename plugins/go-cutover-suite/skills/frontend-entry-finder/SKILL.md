---
name: frontend-entry-finder
description: Use when the user wants to know which page, module, or app flow should be tested after a route cutover, when a frontend or client entrypoint must be found from local repos, or when the gateway trace dead-ends and frontend scope must be inferred from similar routes, or mentions 前端入口, 客户端入口, 功能入口, 测试入口, clone missing frontend repo.
---

# Frontend Entry Finder

## Goal

Map one outward-facing route or one merged outward-route evidence set to the most likely frontend or client feature entry points so the user can test the cutover efficiently.
If no outward-facing route is confirmed, fall back to route-similarity inference and keep those results clearly marked as speculative.

## Inputs

- outward-facing route and method
- optional multiple confirmed outward routes from different code gateway and APISIX sources
- gateway trace results
- optional fallback route hypotheses when no outward-facing route is confirmed
- optional frontend repo hints
- `workspaceRoot`

## Default Workflow

1. Determine candidate projects.
Use Sourcegraph only to determine candidate project names and matched files.
Do not decide feature scope from Sourcegraph results.

2. Ensure the project exists locally.
Search under `workspaceRoot` first.
If the project is missing locally, run `skills/go-cutover-orchestrator/scripts/gitlab_clone_or_update.sh` from this plugin and continue.
Do not produce final test entry candidates until the project exists locally or clone has failed explicitly.

3. Choose the analysis mode.
Use `confirmed-route` mode when the gateway trace produced one or more outward-facing routes from code gateways, APISIX gateways, or both.
Use `similar-route-fallback` mode when the gateway trace ended without a confirmed outward route but did produce fallback route hypotheses.
If multiple code gateway or APISIX sources produced multiple confirmed outward routes, analyze the union and keep the gateway source attached to each candidate path.
If APISIX endpoints were provided upstream, assume the gateway trace already checked all of them and consume the merged route evidence rather than only the code-gateway subset.

4. Analyze the local project only.
Search from API client layer outward in the local checkout.
Prioritize:
- route constants and API modules
- service wrappers
- page or screen modules
- menu text or feature labels
- analytics or tracking names that reveal business context

In `similar-route-fallback` mode, search not only exact routes but also route families that match:
- same stable suffix
- same trailing action segment such as `list`, `detail`, `all`, `create`, `update`
- same resource nouns in the path
- same normalized parameterized shape such as `{id}`, `:id`, `${id}`
- same method plus similar API module or service wrapper names

5. Build test entry candidates.
Write the report in two layers:

- first, a concise Chinese feature-flow summary that explains how a user actually reaches the interface, step by step
- second, the detailed evidence for each candidate

Both layers must stay fully in Chinese except for code identifiers, paths, and route literals.

For each candidate, include:
- project
- file path
- entry type such as page, modal, list action, submission flow
- why it likely maps to the route
- suggested manual test path
- confidence such as `confirmed` or `speculative`
- evidence source such as `exact-route`, `derived-symbol`, `similar-route`, `confirmed-by-code-gateway`, `confirmed-by-apisix`, or `mixed-route-union`

6. Rank candidates.
Prefer direct route usage over indirect references.
Prefer `confirmed-route` candidates over `similar-route-fallback` candidates.
Inside fallback mode, rank same suffix plus same action tail above generic semantic matches.
If two candidates come from different confirmed code gateway or APISIX routes, keep both instead of collapsing to one winner.

If Sourcegraph and local code disagree, trust the local repository state and record the mismatch in the report.

## Guardrails

- Do not modify frontend code in this phase.
- If multiple apps consume the same route, report all of them.
- If the project cannot be cloned, record the exact blocker and stop at project-level evidence. Do not fabricate local test scope from remote evidence alone.
- Do not present fallback similarity matches as confirmed route usage.

## Validation

Before finishing:

1. Confirm each candidate includes project, file, reason, and test suggestion.
2. Confirm each candidate comes from local project evidence, not just Sourcegraph evidence.
3. Confirm the route, fallback route hypothesis, or a strong derived symbol appears in the local project evidence.
4. Separate confirmed entries from speculative ones.
5. Confirm the report starts with a concise Chinese feature-flow summary that a tester can follow step by step without opening code.
6. Confirm each flow states which user action actually triggers the interface at the last step.
7. Confirm each speculative candidate explains which similarity rule made it relevant, such as same suffix or same action tail.
8. Confirm APISIX-confirmed outward routes were not dropped merely because a code gateway already produced another confirmed route.

## Reference

Read `references/entrypoint-report-format.md` for the output structure.
