# Technical Design

## Purpose

This task is the Phase 1 integration validation for `plugins/onion-sdd/`. It proves that the manual Onion SDD flow can run from entry command to finish gate, and it may fix small local gaps found during validation.

`/onion-auto` is explicitly excluded. It remains a future iteration.

## Validation Layers

### 1. Static Contract Validation

Check that the plugin surface is coherent:

- command files exist and have frontmatter
- skill files exist and have frontmatter
- plugin JSON and current-state template parse
- README, rules, commands, and skills agree on Tier routing
- no hard full-repository scan requirement is reintroduced
- no user-facing runtime dependency on `/fe-sdd` or `fe-specflow`

### 2. Flow Walkthrough

Use a disposable Tier 2+ OpenSpec smoke test to exercise the expected artifact chain:

```text
/onion-plan
  -> tier-triage
  -> full-change
  -> openspec-change
  -> proposal.md / specs/**/spec.md / tasks.md
  -> optional external-spec
  -> verify-change / e2e-report.md
  -> /onion-continue recovery reasoning
  -> /onion-finish archive judgment
```

The walkthrough may create `openspec/changes/onion-sdd-flow-smoke-test/` as validation evidence. If the artifact is noisy after validation, remove only that smoke-test directory.

### 3. Optional Capability Gap Review

Except for `/onion-auto`, related Phase 2+ capabilities can be inspected or lightly improved when the gap is local to `plugins/onion-sdd/`:

- AI spec self-review language or hooks
- metrics / ROI fields or documentation
- Spec Pack registry integration notes
- marketplace readiness documentation or manifest metadata

If the gap requires broad implementation rather than local documentation/config cleanup, record it in `validation.md` as a follow-up instead of expanding this task indefinitely.

## Trellis Boundary

Trellis source, script, and runtime changes are approval-gated:

- Do not edit `.trellis/scripts/**`, `.trellis/.runtime/**`, or Trellis source/runtime behavior during this task without explicit user confirmation.
- If validation shows Trellis changes are required, stop, document the needed change and rationale in `validation.md`, and ask the user before planning or implementing it.
- Plugin-side Trellis adapter documentation, `task.json.meta.onion` examples, and smoke-test metadata are allowed.

## Compatibility

- OpenSpec remains the source of truth for change body.
- Trellis metadata stores recovery hints, hashes, parent/child references, and journal summaries only.
- Existing Phase 0 mini/light paths must remain valid.
- Existing non-onion SDD plugins are not changed unless separately approved.

## Completion Output

The task should produce `validation.md` containing:

- commands run
- static validation results
- walkthrough artifacts created
- `/onion-continue` recovery result
- `/onion-finish` judgment result
- small fixes applied, if any
- follow-up gaps, especially anything requiring Trellis source changes
