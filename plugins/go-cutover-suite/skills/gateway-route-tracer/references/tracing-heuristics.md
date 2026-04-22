# Tracing Heuristics

## Repo Priority

Search in this order unless the locator results strongly suggest otherwise:

1. known gateway repos such as `onions-school`
2. tenant or aggregation repos such as `teacher-tenant`
3. proxy or config repos such as `apisix`
4. backend service repos that also expose HTTP routes

## Files To Prefer

- route registration files
- gateway config files
- proto files with HTTP annotations
- handler or controller files
- service wiring files

## What Counts As A Traced Step

Each step should have at least one of:

- matched route string
- matched method
- matched handler or proxy target
- config key that maps the internal route to the external route

## Dead-End Rules

Mark the chain as a dead end when:

- the backend symbol has no caller in the next layer
- only docs mention the route
- the repo cannot be accessed and no alternative evidence exists

When this happens, record the last confirmed step instead of guessing.
