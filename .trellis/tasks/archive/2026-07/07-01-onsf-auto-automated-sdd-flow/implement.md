# Implementation Plan: onsf-auto automated SDD flow

## Preconditions

- Stay within `plugins/onion-sdd/**` and current project `.cursor/**` trial copy as needed.
- Do not modify Trellis runtime scripts.
- Do not implement code outside plugin docs/commands/skills/rules unless validation reveals a required template metadata update.

## Steps

1. Add the command entry.
   - Create `plugins/onion-sdd/commands/onsf-auto.md`.
   - Define inferred mode and explicit submodes: `new`, `continue`, `verify`, `finish-check`.
   - Delegate orchestration to `skills/auto-flow/SKILL.md`.
   - State no-auto-commit, no-auto-archive, and no-auto-Trellis-task-creation boundaries.

2. Add the auto-flow skill.
   - Create `plugins/onion-sdd/skills/auto-flow/SKILL.md`.
   - Include state recovery, intent inference, tier/auto metadata, risk gate, spec self-review, implementation discipline, diff self-review, verification closure, and Trellis sync boundaries.
   - Reference existing onion skills instead of duplicating their templates.

3. Update tier triage.
   - Replace Phase 0 hard-coded “manual only” wording with auto-aware metadata.
   - Keep manual command behavior valid.
   - Document auto mode values, confidence, blockers, and assumptions.

4. Update command/rule/docs references.
   - Add `/onsf-auto` to command maps and trigger boundaries.
   - Remove or revise stale “not in scope” statements.
   - Update README and USAGE command tables if present.
   - Update `DESIGN-SUPPLEMENT.md` auto section to distinguish historical forward-compatibility from first implemented auto flow.

5. Sync `.cursor` trial copy.
   - Copy/add the updated onion command, skill, and rules/docs that exist under `.cursor`.
   - Verify source and `.cursor` critical files match when applicable.

6. Validate.
   - `git diff --check`
   - `python3 -m json.tool plugins/onion-sdd/.cursor-plugin/plugin.json`
   - `find plugins/onion-sdd -type f | sort`
   - `rg -n "onsf-auto|auto-flow|auto 模式|自动|不自动提交|不自动归档|Trellis" plugins/onion-sdd .cursor/commands .cursor/skills .cursor/rules -S`
   - `node scripts/validate-template.mjs` and record any unrelated existing failures.

## Review Gates

- Confirm no text says `/onsf-auto` is out of scope after implementation, except historical notes clearly marked as old design context.
- Confirm `/onsf-auto` cannot be interpreted as permission to commit/archive/create Trellis tasks.
- Confirm manual `/onsf-*` commands retain their existing meanings.
- Confirm YApi, external spec, and QA precedence remains compatible with `pull-yapi`, `re-check`, `external-spec`, and `verify-change`.

## Rollback Points

- After adding command/skill: remove the two new files if the shape is rejected.
- After docs updates: revert only documentation references if validation finds ambiguous scope.
- Before final response: do not leave `.cursor` trial copy diverged from source plugin for the files touched.
