# onion-sdd-flow-health Specification

## Requirement: Tier 2+ flow can be recovered and finished

Onion SDD MUST allow a Tier 2+ change to be recovered from existing artifacts and finished based on validation evidence.

### Scenario: Recover from Trellis metadata

- **Given** a Trellis task has `task.json.meta.onion.change_id` pointing to `onion-sdd-flow-smoke-test`
- **And** the change directory contains `proposal.md`, `specs/**/spec.md`, `tasks.md`, and `e2e-report.md`
- **When** `/onion-continue` is invoked
- **Then** it should prefer Trellis metadata as the recovery source
- **And** it should infer the next step as `finish` when `e2e-report.md` has a passing `## 验收结论`

### Scenario: Finish with passing validation evidence

- **Given** `tasks.md` has all tasks completed
- **And** `e2e-report.md` contains `结论: 通过`
- **And** `e2e-report.md` contains `阻塞项: 无`
- **When** `/onion-finish` evaluates the change
- **Then** it should suggest that the change can be archived
- **And** it should not execute `openspec archive` automatically

### Scenario: Preserve manual flow boundary

- **Given** the change is a Phase 1 smoke test
- **When** the flow reaches validation
- **Then** `/onion-auto` must remain out of scope
- **And** any Trellis source/script/runtime modification must require user confirmation before implementation

