# Implementation Plan

## Scope

This task validates that the current `plugins/onion-sdd/` Phase 1 flow is runnable end to end. It does not implement `/onion-auto`.

Other adjacent capabilities, including AI self-review, metrics aggregation, Spec Pack registry notes, and marketplace readiness, may be checked and lightly fixed if the work stays local to `plugins/onion-sdd/`. Trellis source/script/runtime changes require explicit user confirmation before any design or implementation.

## Checklist

- [x] Review the task PRD and design.
- [x] Run static structure checks for `plugins/onion-sdd`.
- [x] Validate JSON files:
  - `plugins/onion-sdd/.cursor-plugin/plugin.json`
  - `plugins/onion-sdd/templates/current.example.json`
- [x] Check command and skill routing:
  - `/onion-plan` -> `tier-triage` -> `full-change` for Tier 2+
  - `full-change` -> `openspec-change` / `external-spec` / `verify-change`
  - `/onion-continue` -> `trellis-adapter` -> current/OpenSpec fallback
  - `/onion-finish` -> `verify-change` evidence gate
- [x] Check negative constraints:
  - no hard full-repository scan requirement
  - no runtime dependency on `/fe-sdd` or `fe-specflow`
  - `/onion-auto` remains explicitly out of scope
- [x] Check adjacent capability gaps, excluding `/onion-auto`:
  - AI self-review / spec review readiness
  - metrics / ROI state fields or docs
  - Spec Pack registry notes
  - marketplace readiness
- [x] Run one Tier 2+ walkthrough using a disposable OpenSpec smoke test.
- [x] Record validation results and gaps in `validation.md`.
- [x] Fix any small documentation/routing gaps found during validation.
- [x] Stop and ask the user before any Trellis source/script/runtime change.
- [x] Re-run affected checks after fixes.

## Validation Commands

```bash
find plugins/onion-sdd -type f | sort
python3 -m json.tool plugins/onion-sdd/.cursor-plugin/plugin.json
python3 -m json.tool plugins/onion-sdd/templates/current.example.json
rg -n "full-change|openspec-change|external-spec|verify-change" plugins/onion-sdd
rg -n "trellis-adapter|meta.onion|trellis_task|source_hashes" plugins/onion-sdd
rg -n "必须全量扫描|全量扫描项目|扫描当前仓库" plugins/onion-sdd
rg -n "/fe-sdd|调用 fe-specflow|依赖 fe-specflow" plugins/onion-sdd
rg -n "onion-auto|AI 自审|metrics|marketplace|Spec Pack" plugins/onion-sdd
node scripts/validate-template.mjs
```

## Walkthrough Mode

Create a disposable local OpenSpec change under `openspec/changes/onion-sdd-flow-smoke-test/`, populate the minimum Tier 2+ artifacts, exercise `/onion-continue` and `/onion-finish` reasoning against those artifacts, then leave the artifact as validation evidence or remove it if it creates unnecessary noise.

## Rollback

- If disposable walkthrough artifacts are created and the user does not want to keep them, delete only the smoke-test OpenSpec directory created by this task.
- Revert only files changed by this task.
- Do not modify `.trellis/scripts/**`, `.trellis/.runtime/**`, or Trellis runtime/source files without explicit user confirmation.
- Do not modify non-onion SDD plugins without separate approval.
