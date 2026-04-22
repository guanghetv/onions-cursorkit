# MVP Scope

The first release is intentionally narrow. It should complete one route cutover end to end.

## Included

- single route input
- exact HTTP method matching
- configurable `oldServiceName` and `newServiceName`
- required `oldServiceHint`, `newServiceHint`, and `workspaceRoot`
- Sourcegraph-based cross-repo discovery
- server-side caller cutover on the requested branch
- outward route tracing through gateway or proxy repos
- frontend or client entrypoint discovery from local repositories
- auto clone of missing repos into `~/work/`
- report pack generation under `~/work/_ai_reports/go-cutover/`
- automatic merge request creation or detection targeting `dev`, with result written into the report pack

## Excluded

- bulk cutover for many routes in one run
- automatic chat notifications
- automatic UI regression runs
- dependency upgrades or general refactors
- changing public API contracts

## Success Criteria

The MVP is successful when one route task can produce all of these:

1. all discovered server-side caller repos identified and updated or marked already cut over
2. outward-facing route identified, or an explicit dead-end report is produced
3. frontend or client entry candidates listed with concrete local file evidence
4. every output written into the report pack
