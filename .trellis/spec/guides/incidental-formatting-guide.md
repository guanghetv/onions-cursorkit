# Incidental Formatting Guide

> **Purpose**: State the scope discipline that applies *before* you edit, and use `git diff` only to verify you followed it — not to decide, after the fact, what counts as in scope.

---

## The Standing Rule (precondition — decide before you edit, not from the diff)

Only touch content that belongs to the current requirement's scope. This is a pre-development convention, not something inferred from `git diff` afterward: don't reformat, restyle, reorder, or reword anything outside the task's scope, even if it looks like a harmless cleanup or an improvement you noticed along the way.

`git diff` after the edit is a **verification step** — it checks whether you (or a tool acting on your behalf) actually respected the rule above. It is never the place where the "is this okay to touch" decision gets made; that decision is already fixed before you start editing.

---

## The Problem This Guide Addresses

Some edit tools (or the underlying editor) auto-reformat a file on write as a side effect — e.g. realigning Markdown pipe-table columns with padding, or normalizing blank lines around lists — independent of what you asked for. This can inject changes into sections you never intended to touch, even ones far from your edit.

This is a **tool side-effect**, not a scope decision. The standing rule ("don't touch unrelated content") still applies in full; the question is only how to classify what the tool injected once you verify it with `git diff`.

---

## Classifying a Tool-Injected Hunk During Verification

When `git diff` shows a hunk outside your intended change, it means the tool deviated from the standing rule on your behalf. Classify it immediately — don't leave it open as a debate across turns:

| Hunk type | Why it passes/fails the standing rule | Action |
|-----------|----------------------------------------|--------|
| **Format-only** — whitespace/column padding/alignment, blank-line normalization; no word, value, or order changed | No actual content was touched — the rule is upheld in substance despite the diff noise | Leave it; no revert needed |
| **Content change** — any wording, value, ordering, or logic difference, however small | The rule was violated, regardless of which tool caused it | Revert immediately; restore the original text for that hunk |

---

## Example

```diff
- | 阶段 | 产物 | 入口 |
- |------|------|------|
+ | 阶段      | 产物                                          | 入口          |
+ | --------- | --------------------------------------------- | ------------- |
```

✅ **Leave it** — only padding/alignment added, cell text unchanged; no unrelated content was actually touched.

```diff
- | 平台 | 追加条目 |
+ | 平台 | 追加条目（不含 opsx-*.md） |
```

❌ **Revert** — cell wording changed; this is a scope violation caught during verification, not a formatting side-effect.

---

## Why This Matters

- The scope discipline ("don't touch unrelated content") must be settled before you start editing — treating it as something `git diff` decides after the fact gets the causality backwards and invites scope creep.
- Reverting harmless formatting churns the diff for no reason and costs a review cycle.
- Silently keeping a content change that hitched a ride on a tool's auto-format pass is a correctness bug — the user only asked for one specific change.
- `git diff` after editing exists to catch tool side-effects that slipped past your intent, not to renegotiate scope.
