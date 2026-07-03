# onsf-auto automated SDD flow

## Goal

Implement `/onsf-auto` as the automated execution layer for Onion SDD. It should let the AI run the Onion SDD flow with no mid-flow user interaction for eligible changes: classify the request, create or update SDD artifacts, execute implementation work, run verification, and self-review the spec/diff. It must stop short of automatic commit, archive, or destructive/high-risk decisions.

## Confirmed Facts

- User intent: `/onsf-auto` is for AI to automatically use the SDD process, not merely recommend which manual `/onsf-*` command to run.
- First-version scope selected by user: option C.
  - Automatically run SDD artifacts, implementation, tests, spec self-review, diff self-review, and verification report.
  - Do not automatically commit or archive.
- No-interaction stop policy selected by user: option B.
  - Low/medium-risk gaps may continue with explicit assumptions.
  - High-risk gaps must stop and report blockers.
- Implementation shape selected by user: option B.
  - Add `/onsf-auto` as the command entry.
  - Add a dedicated `auto-flow` skill for the automated SDD state machine, stop policy, spec self-review, diff self-review, and verification closure.
- Trellis relationship selected by user: option B.
  - If an active Trellis task already exists, `/onsf-auto` may bind/sync `meta.onion`, phase, change id, and source hashes.
  - If no active Trellis task exists, `/onsf-auto` must not create one automatically; it continues using OpenSpec and optional `.onion-sdd/current.json`.
- Entry semantics selected by user: option C.
  - Default `/onsf-auto` auto-detects new/continue/verify/finish-ready intent from current state and user input.
  - Explicit submodes such as `/onsf-auto new`, `/onsf-auto continue`, and `/onsf-auto verify` may override inference.
- Design approach selected by user: option B.
  - `/onsf-auto` is a thin command entry.
  - `skills/auto-flow/SKILL.md` owns the automated SDD state machine and reusable automation rules.
- Original design document link: `https://guanghe.feishu.cn/wiki/FcsSwnZ1TiqLdskGa8EcO9U2nmb`.
  - Direct remote reading is currently blocked by Feishu/login access in this environment.
  - Repository history records that earlier tasks read this document at revisions `188` and `201`.
- Existing `plugins/onion-sdd/DESIGN-SUPPLEMENT.md` preserved forward-compatible auto fields:
  - `auto 模式判定: <人工 / 半自动 / 全自动>`
  - `auto 置信度: <0.0-1.0>`
  - `auto 阻断原因: <reason>`
- Existing `tier-triage` currently hard-codes `auto 模式判定: 人工` and says not to use `/onsf-auto`.
- Current `onion-sdd` has the manual command set: `/onsf-fix`, `/onsf-tweak`, `/onsf-plan`, `/onsf-continue`, `/onsf-finish`.
- Current `onion-sdd` already has the full-flow skills needed for automation orchestration:
  - `tier-triage`
  - `mini-change`
  - `light-change`
  - `full-change`
  - `openspec-change`
  - `external-spec`
  - `pull-yapi`
  - `re-check`
  - `verify-change`
  - `trellis-adapter`
- Current docs state `/onsf-auto`, AI self-review, weak natural-language triggers, and auto recommendations are out of scope. This task will revise that boundary.

## Requirements

- Add `/onsf-auto` as an Onion SDD command that can execute eligible SDD flows without asking the user mid-flow.
- Add `skills/auto-flow/SKILL.md` as the reusable automation orchestrator behind `/onsf-auto`.
- `/onsf-auto` must classify the request using Onion Tier rules and produce auto metadata:
  - mode: manual / semi-auto / full-auto
  - confidence
  - blockers
  - selected route
- `/onsf-auto` must support automatic execution through implementation and verification for eligible changes:
  - Tier 0+/0++ mini flow
  - Tier 1 light flow
  - Tier 2+ full flow when requirements are sufficiently clear
- `/onsf-auto` must create or update OpenSpec artifacts according to the selected tier.
- `/onsf-auto` must self-review generated specs before implementation:
  - placeholder scan
  - contradiction scan
  - scope and acceptance scan
  - conflict with known external spec/YApi/QA evidence
- `/onsf-auto` must self-review code changes before completion:
  - diff matches current OpenSpec/tasks
  - no unrelated file churn
  - tests/verification recorded
  - known blockers recorded
- `/onsf-auto` must not automatically run `git commit`, `openspec archive`, Trellis archive, or equivalent irreversible history/cleanup actions.
- `/onsf-auto` must stop and report blockers when required information is missing or risk exceeds the allowed no-interaction policy.
- `/onsf-auto` must use the selected stop policy:
  - Continue automatically for low/medium-risk gaps when assumptions can be written down and verified later.
  - Stop for high-risk gaps such as permissions/security/payment/funds, destructive data changes, delete/rename response fields, cross-module state-machine ambiguity, QA/YApi conflicts, or inability to verify a critical path.
- `/onsf-auto` must remain an onion-sdd-native flow; it may reuse onion skills but must not depend on `fe-specflow`.
- `/onsf-auto` must respect Trellis task-creation consent rules:
  - It may sync to an existing active task.
  - It must not create, start, archive, or otherwise transition Trellis tasks by itself.
- `/onsf-auto` must support both inferred and explicit entry modes:
  - inferred default mode
  - explicit `new`
  - explicit `continue`
  - explicit `verify`
  - explicit finish-readiness check without automatic archive

## Acceptance Criteria

- [x] `plugins/onion-sdd/commands/onsf-auto.md` exists with valid command frontmatter and describes no-interaction automated execution.
- [x] Onion SDD docs and rules no longer claim `/onsf-auto` is out of scope.
- [x] `tier-triage` no longer hard-codes auto mode to manual for `/onsf-auto`; it documents auto mode, confidence, blockers, and routing behavior.
- [x] `commands/onsf-auto.md` exists and delegates automation orchestration to `skills/auto-flow/SKILL.md`.
- [x] `skills/auto-flow/SKILL.md` performs auto orchestration across tier triage, OpenSpec writing, implementation discipline, spec self-review, diff self-review, and verification.
- [x] Auto mode stop conditions are explicit and testable, following the “high-risk stop, low/medium-risk continue with assumptions” policy.
- [x] Auto mode forbids automatic commit/archive and documents that completion stops at “ready for user review/commit”.
- [x] Auto mode does not create Trellis tasks automatically; with an existing active task it may sync only onion metadata and phase references.
- [x] `/onsf-auto` defaults to state-based intent detection and also documents explicit submodes.
- [x] Existing manual `/onsf-*` commands remain valid and unchanged in purpose.
- [x] YApi/external/QA spec behavior remains compatible with the recently added `pull-yapi` and `re-check` flows.
- [x] Validation commands cover file presence, command/skill references, frontmatter/JSON checks, and relevant text checks.

## Validation Results

- Passed: `git diff --check`
- Passed: `python3 -m json.tool plugins/onion-sdd/.cursor-plugin/plugin.json`
- Passed: source and `.cursor` copies match for changed command/skill/rule files.
- Passed: stale `/onsf-auto` out-of-scope text scan.
- Known unrelated failure: `node scripts/validate-template.mjs` still fails because `plugins/fe-specflow/skills/design-to-opsx/SKILL.md` is missing `description` frontmatter.

## Out of Scope

- Automatically committing to Git.
- Automatically running `openspec archive` or Trellis task archive.
- Building a separate runtime daemon, hook system, or marketplace automation service.
- Depending on `fe-specflow` at runtime.
- Requiring successful remote Feishu access as part of local validation.

## Open Questions

- None blocking. Planning should now produce `design.md` and `implement.md`.
