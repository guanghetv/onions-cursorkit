# Design: onsf-auto automated SDD flow

## Overview

`/onsf-auto` adds an automated execution layer on top of existing Onion SDD commands and skills. It is not a replacement for the manual `/onsf-*` commands. It is an auto-orchestrator that lets the AI run eligible Onion SDD flows without stopping for mid-flow user interaction, while preserving high-risk stop conditions and the existing no-auto-commit/no-auto-archive boundary.

The first version uses a thin command plus one reusable skill:

- `commands/onsf-auto.md`: user-facing slash command entry and submode contract.
- `skills/auto-flow/SKILL.md`: automated state machine, risk gate, spec self-review, diff self-review, validation closure, and Trellis metadata sync rules.

## Entry Contract

`/onsf-auto` supports inferred mode and explicit submodes:

| Input | Meaning |
| --- | --- |
| `/onsf-auto` | Infer whether this is new, continue, verify, or finish-ready from current state and user intent |
| `/onsf-auto new` | Start or update a new Onion SDD change from user input |
| `/onsf-auto continue` | Resume an existing change and continue pending tasks |
| `/onsf-auto verify` | Run verification/self-review and update report artifacts |
| `/onsf-auto finish-check` | Check whether the change is ready for `/onsf-finish`, without archiving |

The command delegates to `auto-flow`; the command file should not duplicate the state machine.

## State Machine

`auto-flow` runs these phases:

1. **Recover context**
   - Read active Trellis task `task.json.meta.onion` when present.
   - Fall back to `.onion-sdd/current.json` if present and trustworthy.
   - Fall back to `openspec/changes/**` scanning.
   - Never create, start, archive, or otherwise transition Trellis tasks.

2. **Infer intent**
   - No current change: `new`.
   - Existing change with incomplete `tasks.md`: `continue`.
   - Completed tasks without verification report: `verify`.
   - Passing `e2e-report.md`: `finish-ready`.
   - Explicit submode overrides inference.

3. **Classify tier and auto mode**
   - Use `tier-triage` semantics.
   - Emit tier, selected route, auto mode, confidence, blockers, and assumptions.
   - Auto mode values:
     - `停止`: high-risk blocker or insufficient confidence.
     - `半自动`: continue with documented low/medium-risk assumptions.
     - `全自动`: enough context to run through implementation and verification.

4. **Generate/update SDD artifacts**
   - Tier 0: no OpenSpec unless implementation creates meaningful code changes requiring a mini record.
   - Tier 0+/0++: use mini-change.
   - Tier 1: use light-change.
   - Tier 2+: use full-change and openspec-change.
   - External/YApi/QA evidence uses existing `external-spec`, `pull-yapi`, `re-check`, and `verify-change` contracts.

5. **Spec self-review**
   - Block placeholders, unfinished template text, contradictions, ambiguous acceptance criteria, and out-of-scope work.
   - Check consistency among proposal, specs, tasks, backend/YApi/QA artifacts, and assumptions.
   - Fix low-risk spec defects inline before implementation.
   - Stop on high-risk conflicts or unresolvable ambiguity.

6. **Implementation**
   - Business-code edits are allowed only after a current change and `tasks.md` exist.
   - Follow task validation points and existing repo patterns.
   - Do not run browser automation unless environment is available and no login/permission blocker exists.

7. **Diff self-review**
   - Confirm diff matches current change scope and tasks.
   - Detect unrelated file churn.
   - Check implementation against OpenSpec and external/YApi/QA evidence.
   - Fix review findings before completion when safe.

8. **Verification closure**
   - Run available lint/type/test commands when discoverable and relevant.
   - Update `tasks.md` status and write/update `e2e-report.md` for Tier 2+.
   - End at ready-for-user-review/commit.
   - Do not commit, run `openspec archive`, or archive Trellis tasks.

## Risk Gate

The selected policy is: high-risk stops, low/medium-risk continues with explicit assumptions.

Continue automatically when:

- Missing detail is low/medium risk and can be captured as an assumption.
- Scope is local and testable.
- Field additions are optional or non-breaking.
- Style/copy/layout ambiguity can follow existing local patterns.

Stop when:

- Permissions, security, payment, funds, audit, or destructive data behavior is involved.
- A response field is deleted or renamed, or a required/optional field change affects validation.
- Method/path/error-code changes conflict with implementation or tests.
- QA spec conflicts with YApi/backend spec and no precedence resolves it.
- Cross-module state-machine behavior is ambiguous.
- Critical validation cannot run and no equivalent evidence exists.
- The command would need to create/start/archive a Trellis task or commit/archive code/history.

## Trellis Integration

`/onsf-auto` may integrate with Trellis only when an active task already exists.

Allowed:

- Write/update `task.json.meta.onion` references through documented `trellis-adapter` protocol.
- Sync change id, change path, tier, phase, last action, and source hashes.
- Use Trellis task status as context for recovery.

Forbidden:

- Auto-create Trellis tasks.
- Auto-start planning tasks.
- Auto-archive tasks.
- Modify `.trellis/scripts/**` or `.trellis/.runtime/**`.
- Copy OpenSpec body into Trellis task files or journal.

## Documentation Updates

The implementation must update stale “out of scope” language:

- `README.md`
- `USAGE.md` if it describes command map or current limitations.
- `rules/onion-sdd.mdc`
- `commands/onsf-plan.md` if it still says `/onsf-auto` is outside the base capability.
- `skills/tier-triage/SKILL.md`
- `DESIGN-SUPPLEMENT.md` if needed to mark the first auto version as implemented rather than future-only.

## Compatibility

Manual commands remain valid:

- `/onsf-fix`
- `/onsf-tweak`
- `/onsf-plan`
- `/onsf-continue`
- `/onsf-finish`

`/onsf-auto` reuses their skill contracts and does not alter their meaning.

## Rollback

The change is documentation/skill/command level. Rollback means removing:

- `commands/onsf-auto.md`
- `skills/auto-flow/SKILL.md`
- command-map references and auto-flow documentation updates

Manual SDD flows should continue to work throughout and after rollback.
