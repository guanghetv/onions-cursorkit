# Validation Report

## Summary

Phase 1 manual Onion SDD flow is runnable end to end for the validated scope:

```text
/onion-plan
  -> tier-triage
  -> full-change
  -> openspec-change
  -> proposal.md / specs/**/spec.md / tasks.md
  -> external-spec sample
  -> verify-change / e2e-report.md
  -> /onion-continue recovery
  -> /onion-finish archive judgment
```

`/onion-auto` remains out of scope. No Trellis source, `.trellis/scripts/**`, or `.trellis/.runtime/**` changes were made.

## Static Checks

| Check | Result | Notes |
| --- | --- | --- |
| `find plugins/onion-sdd -type f | sort` | Pass | Plugin contains commands, rules, skills, README, design supplement, and state template. |
| `python3 -m json.tool plugins/onion-sdd/.cursor-plugin/plugin.json` | Pass | Manifest parses after description update. |
| `python3 -m json.tool plugins/onion-sdd/templates/current.example.json` | Pass | Template parses. |
| `python3 -m json.tool .cursor-plugin/marketplace.json` | Pass | `onion-sdd` is registered with `source: "onion-sdd"`. |
| `node scripts/validate-template.mjs` | Pass | Only optional hooks/mcp warnings, now including `onion-sdd`. |

## Routing Checks

| Check | Result |
| --- | --- |
| `rg -n "full-change|openspec-change|external-spec|verify-change" plugins/onion-sdd` | Pass |
| `rg -n "trellis-adapter|meta.onion|trellis_task|source_hashes" plugins/onion-sdd` | Pass |
| `/onion-plan` routes Tier 2+ to onion-owned full flow skills | Pass |
| `/onion-continue` defines Trellis active task -> current.json -> OpenSpec fallback | Pass |
| `/onion-finish` uses `e2e-report.md` `## 验收结论` for Tier 2+ finish judgment | Pass |

## Negative Checks

| Check | Result |
| --- | --- |
| `rg -n "必须全量扫描|全量扫描项目|扫描当前仓库" plugins/onion-sdd` | Pass, no matches |
| `rg -n "/fe-sdd|调用 fe-specflow|依赖 fe-specflow" plugins/onion-sdd` | Pass, no matches |
| `/onion-auto` implementation | Not done, intentionally out of scope |
| Trellis source/script/runtime changes | Not done; confirmation gate preserved |

## Smoke Test Artifacts

Created disposable OpenSpec smoke-test change:

```text
openspec/changes/onion-sdd-flow-smoke-test/
├── .openspec.yaml
├── proposal.md
├── specs/onion-sdd-flow-health/spec.md
├── tasks.md
├── backend-smoke.md
├── qa-smoke.md
└── e2e-report.md
```

Created lightweight current state during the walkthrough, then reset it after validation so future `/onion-continue` calls do not treat the smoke test as the active change:

```text
.onion-sdd/current.json
  active_change_id = null
  phase = idle
```

Updated current Trellis task metadata:

```text
.trellis/tasks/06-25-onion-sdd-phase-1-flow-validation/task.json
  meta.onion.change_id = onion-sdd-flow-smoke-test
  meta.onion.phase = finish
```

## /onion-continue Result

Expected recovery output:

```markdown
## Trellis Adapter 状态

- 恢复来源: Trellis active task
- change-id: onion-sdd-flow-smoke-test
- Trellis task: .trellis/tasks/06-25-onion-sdd-phase-1-flow-validation
- phase: finish
- stale: 无
- 下一步: 读取 /onion-finish，基于 e2e-report.md 判断是否可归档
```

Reasoning:

- Active task `task.json.meta.onion.change_path` points to an existing change directory.
- `.onion-sdd/current.json` pointed to the same change during validation, then was reset to idle after the smoke test completed.
- `e2e-report.md` exists and contains a passing `## 验收结论`.

## /onion-finish Result

Expected finish output:

```markdown
## Onion Finish 判断

- change-id: onion-sdd-flow-smoke-test
- Tier: 2
- 任务状态: tasks.md 全部完成
- 验证证据: e2e-report.md
- 验收结论: 通过
- 阻塞项: 无
- 带债项: 无
- 归档建议: 可归档
```

The flow should only suggest `openspec archive onion-sdd-flow-smoke-test`; it must not execute archive automatically.

## Fixes Applied

- Registered `onion-sdd` in `.cursor-plugin/marketplace.json`.
- Updated `plugins/onion-sdd/.cursor-plugin/plugin.json` description to include full OpenSpec, Trellis adapter, and E2E/finish gate.
- Updated `plugins/onion-sdd/README.md` from trial-only install wording to marketplace registration wording.
- Updated `plugins/onion-sdd/rules/onion-sdd.mdc` so only `/onion-auto` remains excluded from the current base flow; metrics/marketplace/Spec Pack can continue through validation or later tasks.
- Updated `docs/add-a-plugin.md` marketplace source example to match this repository's `metadata.pluginRoot: "plugins"` convention.
- Reset `.onion-sdd/current.json` to idle after the smoke test and documented the idle contract in `/onion-continue`, `trellis-adapter`, README, and `.trellis/spec/frontend/state-management.md`.
- Added front-end parity capabilities to onion-owned flow without adding a brainstorming hard gate:
  - Figma / local redesign scope rules and front-end gray-area decisions in `full-change`, `openspec-change`, README, and rule.
  - workspace-native external spec strategy, `requirement_ref`, `modules`, fallback behavior, and metadata source in `external-spec`.
  - Browser automation confirmation, built-in browser preference, login/blocker handling, and evidence rules in `verify-change`.
  - Commit review discipline for user-requested commits in `full-change`, README, and rule.

## Follow-Up Gaps

- `/onion-auto` remains explicitly future work.
- AI self-review, weak natural-language trigger, metrics aggregation, and Spec Pack registry are not blockers for the manual Phase 1 flow. They can be planned as separate optimizations.
- Front-end parity now covers Figma/gray areas, workspace-native spec intake, Browser automation constraints, and commit review discipline at the documentation/skill level. It does not add a mandatory brainstorming gate by request.
- `onion-sdd` has no `hooks/hooks.json`, `mcp.json`, or custom logo asset. `validate-template.mjs` treats these as optional warnings only.
- Historical `ARCHITECTURE-KNOWLEDGE.md` still records Phase 0 non-goals, including marketplace publishing. This is historical context, not current user-facing install guidance.
