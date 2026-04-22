---
name: gateway-route-tracer
description: Use when the route may pass through onions-school, teacher-tenant, apisix, or similar gateway layers, when explicit gateway repo hints are available, or when one interface may map to multiple gateway exposures and the user asks to find all outward-facing routes instead of stopping at the first one, or mentions 网关暴露路由.
---

# Gateway Route Tracer

## Goal

Start from a confirmed server-side caller or service function and trace the chain upward until you find the route that frontend or client code uses directly, while also identifying any remaining upstream server-side repos that still need cutover.
When APISIX endpoints are provided, treat them as a parallel outward-route evidence layer rather than a dead-end-only supplement.

## Inputs

- backend repo and changed call sites
- `oldRoute`
- `newRoute`
- `method`
- `oldServiceName`
- `newServiceName`
- locator output
- optional `gatewayRepos`
- optional `apisixAdminURL`
- optional `apisixAdminURLs`
- optional `apisixAdminKeyEnvVar`

## Default Workflow

1. Start from the changed server-side symbol or path.
Use the switch report to identify the exact client wrapper, repo method, middleware rule, or service function to trace.

2. Search code gateway repositories first.
Prioritize user-provided `gatewayRepos` first.
If `gatewayRepos` is omitted, start from this default repo set: `onions-school`, `channel-platform-server`, `channel`, `teacher-tenant`, then expand if needed.
Do not assume there is only one gateway path. Keep tracing until every discovered code gateway source is classified.

3. Follow the mapping layer by layer.
Track:
- internal client call
- adapter or repo method
- service handler
- gateway or proxy config
- outward-facing route

4. Query APISIX in parallel when endpoints are provided.
If `apisixAdminURL` or `apisixAdminURLs` is available, use `apisix-admin-route-finder` even when code gateways already produced plausible outward routes.
If multiple APISIX admin endpoints are provided, invoke the APISIX finder once per endpoint and keep the `sourceName` in the merged result.
Treat APISIX as a read-only gateway-evidence source that is parallel to code gateways:
- exact or strong prefix route plus method match can upgrade the trace to `confirmed`
- suffix or route-family similarity only produces fallback hypotheses

If no APISIX endpoints are provided, skip this step and continue with code-gateway evidence only.

5. Merge route evidence and record branch points.
Combine code-gateway evidence and APISIX evidence into one outward-route evidence set without losing the original source type.
If one backend route maps to multiple outward routes, keep them all and rank them.
If multiple gateways expose the same route family, keep every gateway-tagged route instead of collapsing to one winner.
If code gateways and APISIX both expose routes for the same migrated interface, preserve both and tag each one with its source type and source name.

6. Stop only at one of these states.
- outward-facing HTTP route identified
- dead end with strong evidence
- no confirmed outward route, but fallback route hypotheses generated for frontend analysis
- blocked by missing repo or access

## Output Rules

Produce both markdown and JSON output that include:

- repo
- file path
- symbol or config key
- method
- route
- reason this is part of the chain
- confidence such as `confirmed` or `fallback-hypothesis`
- evidence source such as `code-gateway`, `apisix-admin-api`, or `mixed`
- gateway source such as repo name or APISIX `sourceName`
- source status such as `confirmed-route`, `fallback-only`, `dead-end`, `blocked`, or `unavailable`

If no outward-facing route can be confirmed, output fallback route hypotheses for downstream frontend analysis. Derive them from:
- same stable suffix as `oldRoute` or `newRoute`
- service-prefix-stripped variants
- same trailing action segment such as `list`, `detail`, `all`, `create`, `update`
- same resource nouns and normalized parameter shape

## Validation

Before handing off:

1. Confirm each traced step has a concrete code or config reference.
2. Confirm the final outward route includes method and path.
3. If no outward route exists, state exactly where the chain stopped.
4. If no outward route exists, emit at least one fallback route hypothesis or explicitly state why even hypothesis generation is blocked.
5. If APISIX endpoints were provided, confirm every provided endpoint was checked or explicitly marked unavailable.
6. If APISIX was used, confirm the result states whether the route was `confirmed-by-apisix` or remained only a fallback hypothesis.
7. Confirm the tracer did not stop at the first successful code gateway or APISIX hit when additional gateway sources were still unverified.

## Reference

Read `references/tracing-heuristics.md` for repo priorities and dead-end handling.
