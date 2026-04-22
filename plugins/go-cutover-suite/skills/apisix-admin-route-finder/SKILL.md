---
name: apisix-admin-route-finder
description: Use when a migrated route may be exposed through one or more APISIX gateways, when the user provides APISIX Admin API endpoints that should be checked as part of gateway tracing, or when route evidence is needed before inferring frontend test scope.
---

# APISIX Admin Route Finder

## Overview

Use APISIX Admin API as a parallel gateway-evidence source when APISIX Admin endpoints are provided for the task.
One migrated interface may be exposed by multiple APISIX gateways at the same time. Do not stop after the first APISIX hit.

This skill is for read-only route discovery. It must never save the APISIX admin key into code, scripts, reports, or docs.

## When to Use

- The route may be exposed through APISIX in the test cluster
- The user provides `apisixAdminURL` or `apisixAdminURLs` and APISIX should be checked as part of normal gateway tracing
- Code gateways dead-end before an outward-facing route is confirmed
- The user provides `apisixAdminURL` and an admin key through an environment variable
- You need better evidence before handing off to `frontend-entry-finder`

Do not use this skill to create, update, patch, or delete APISIX routes.

## Inputs

- `apisixAdminURL`: one full Admin API routes endpoint, usually `/apisix/admin/routes`
- optional `apisixAdminURLs`: multiple Admin API route-list endpoints when the same interface may be exposed by more than one APISIX gateway
- `apisixAdminKeyEnvVar`: env var name that stores `X-API-KEY`, default `APISIX_ADMIN_KEY`
- `oldRoute`
- `newRoute`
- `method`
- optional host, label, or route-name hints

Minimum recommended input:

- `apisixAdminURL`
- `oldRoute`
- `newRoute`
- `method`

The helper script can now auto-derive route seeds from `oldRoute` and `newRoute`, so manual `--uri-prefix`, `--uri-fragment`, and `--same-suffix` are optional overrides rather than mandatory inputs.
If there are multiple APISIX gateways, run the helper once per `apisixAdminURL` and preserve a distinct `sourceName` for each result set.

## Quick Reference

| Goal | Preferred input |
| --- | --- |
| Confirm exact outward route | `--old-route` + `--new-route` + `--method` |
| Search service-prefix-stripped route | auto-derived from old/new route, or override with `--uri-prefix` |
| Search similar route family | auto-derived suffix and fragments, or override with `--same-suffix` + `--uri-fragment` |
| Narrow APISIX scan server-side | `--uri-fragment`, `--name-hint`, `--label-hint` |
| Inspect derived seeds only | `--dry-run` |

## Core Pattern

1. Build route seeds from `oldRoute` and `newRoute`
2. Query APISIX with paging
3. Rank matches by exact route, prefix, suffix, and method
4. Keep every gateway source separate and do not stop at the first hit
5. Emit `confirmed`, `probable`, or `speculative`
6. Hand off the result to `gateway-route-tracer` as part of the merged outward-route evidence set, and then to `frontend-entry-finder`

## Implementation

### 1. Prepare route seeds

Always derive all of these before querying:

- exact routes: `oldRoute`, `newRoute`
- prefix-stripped variants such as removing `/teacher-school`
- stable suffix such as `/students/{studentId}/all`
- stable fragments such as `admin-room`, `students`, `all`

The helper script now does this automatically when `--old-route` and `--new-route` are provided.
Manual flags should be used only when you want to add stronger repo-specific or environment-specific hints.

### 2. Run the helper script

Use:

```bash
python "<plugin-root>/skills/apisix-admin-route-finder/scripts/query_apisix_routes.py" \
  --admin-url "$APISIX_ADMIN_URL" \
  --source-name "apisix-school-test" \
  --key-env "APISIX_ADMIN_KEY" \
  --method "GET" \
  --old-route "/admin-room/students/{studentId}/all" \
  --new-route "/teacher-school/admin-room/students/{studentId}/all"
```

If the live route uses concrete IDs instead of `{studentId}`, the script still benefits from the route-family structure. Add manual `--same-suffix` or `--uri-fragment` only when the auto-derived seeds are not specific enough.

### 2.1 Inspect derived seeds before live query

Use:

```bash
python "<plugin-root>/skills/apisix-admin-route-finder/scripts/query_apisix_routes.py" \
  --admin-url "$APISIX_ADMIN_URL" \
  --source-name "apisix-school-test" \
  --old-route "/admin-room/students/{studentId}/all" \
  --new-route "/teacher-school/admin-room/students/{studentId}/all" \
  --method "GET" \
  --dry-run
```

This prints:

- manual inputs
- auto-derived `querySeeds`
- planned APISIX list queries

Use this when you want to verify whether the auto-derived fragments and suffixes are good enough before touching the live cluster.

### 3. Interpret the result

- `confirmed`: exact route or strong prefix match with compatible method
- `probable`: strong fragment or suffix evidence, but not enough to call it exact
- `speculative`: only weak similarity evidence
- `sourceName`: the gateway source that produced this evidence

### 3.1 Multiple APISIX gateways

If the user provides multiple APISIX Admin API endpoints:

1. run the helper once per endpoint
2. set a different `--source-name` for each gateway
3. merge results by keeping `sourceName`
4. preserve all distinct outward routes instead of collapsing them into one guess

If two gateways expose different outward routes for the same migrated interface, keep both and pass both to `gateway-route-tracer` and `frontend-entry-finder`.
If code gateways also produced outward routes for the same interface, do not treat the APISIX result as optional noise. Preserve it as a parallel exposure source.

When handing off to `frontend-entry-finder`:

- treat `confirmed` as outward-route evidence
- treat `probable` and `speculative` as fallback hypotheses only

## APISIX Notes

- Admin API supports paging for `routes` via `page` and `page_size`
- `uri`, `name`, and `label` list filters can reduce the scan set
- multiple list filters are intersected by APISIX
- `filter=` on routes is limited to `service_id` and `upstream_id`, so route-prefix discovery should primarily use `uri` and local ranking
- route definitions may use either `uri` or `uris`
- the helper script auto-derives exact routes, stable prefixes, common suffixes, and route fragments from `oldRoute` and `newRoute`

## Common Mistakes

- Hardcoding the admin key into the skill, report, or script
- Treating APISIX `uri` query as an exact prefix operator; it is safer to treat it as server-side narrowing, then do local ranking
- Ignoring `uris` and only checking `uri`
- Treating `probable` or `speculative` APISIX hits as confirmed frontend routes
- Stopping after one APISIX hit without checking route method and status
- Passing too many manual hints before checking what `--dry-run` already derived automatically
- Losing the gateway source when merging results from multiple APISIX endpoints

## Handoff Rules

- `go-cutover-orchestrator`: use this skill whenever APISIX endpoints are provided for the task, so APISIX evidence can be gathered in parallel with code-gateway tracing
- `gateway-route-tracer`: use this skill as a regular parallel check when APISIX endpoints are available, not only before declaring a dead end
- if multiple APISIX gateways exist, invoke this skill once per gateway endpoint and aggregate all gateway-tagged results
- `frontend-entry-finder`: consume `confirmed` as strong evidence and `probable/speculative` as fallback route hypotheses
