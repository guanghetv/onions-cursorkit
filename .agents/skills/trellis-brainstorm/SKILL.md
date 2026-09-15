---
name: trellis-brainstorm
description: "Guides collaborative requirements discovery before implementation. Creates task directory, seeds PRD, asks high-value questions one at a time, researches technical choices, and converges on MVP scope. Use when requirements are unclear, there are multiple valid approaches, or the user describes a new feature or complex task."
---

# Trellis Brainstorm

## Non-Negotiable Interview Contract

Interview me relentlessly about every **unresolved** aspect of this plan until we reach a shared understanding. Walk down each branch of the design tree, resolving dependencies between decisions one-by-one. For each question, provide your recommended answer.

Ask the questions one at a time.

## Non-Negotiable No Re-Ask Rule

Never re-ask a decision that is already recorded as confirmed in the brainstorm working memory.

Before asking any question:

1. Read `prd.md` → `## 已确认决策` (create an empty table if missing) and any resolved open questions.
2. Skip any question that is semantically equivalent to an already-confirmed decision; reuse the recorded conclusion.
3. Do **not** require OpenSpec `proposal.md` during brainstorm. Brainstorm memory lives in `prd.md` only.

`Interview relentlessly` applies only to **unresolved** branches. Resolved decisions must not be rephrased and asked again. Re-asking after the user already answered is a flow deadlock — treat it as a hard failure of this skill.

## Non-Negotiable Write-Before-Next-Ask Rule

After each user answer (including AskQuestion card choices):

1. Restate the chosen option or conclusion in one sentence (so it survives context compression).
2. Immediately append/update `prd.md` → `## 已确认决策`.
3. Only then ask the next question.

Do not ask the next question in the same turn before `prd.md` is updated. Do **not** write OpenSpec `proposal.md` during brainstorm; that happens after brainstorm converges and the user enters the OpenSpec phase.

## Non-Negotiable Evidence Rule

If a question can be answered by exploring the codebase, explore the codebase instead.

This is mandatory. Before asking the user a question, first check whether the answer is already available in code, tests, configs, docs, existing specs, task history, or `prd.md` → `## 已确认决策`.

Do not ask the user to confirm facts that the repository can answer. Ask only for product intent, preference, scope, risk tolerance, or decisions that remain ambiguous after inspection.

---

Use this skill during Phase 1 planning to turn the user's request into clear requirements and planning artifacts.

## Preconditions

Use this skill only after task-creation consent has been given and the user is ready to enter Trellis planning.

If no task exists yet, create one:

```bash
TASK_DIR=$(python3 ./.trellis/scripts/task.py create "<short task title>" --slug <slug>)
```

Use a concise title from the user's request. Use a slug without a date prefix. `task.py create` adds the `MM-DD-` directory prefix automatically.

`task.py create` creates the default `prd.md`. Update that file with the current understanding before asking follow-up questions. Ensure `## 已确认决策` exists before the first interview question.

## Planning Flow

1. Capture the user's request and initial known facts in `prd.md`.
2. Inspect available evidence before asking questions:
   - code, tests, fixtures, and configs
   - README files, docs, existing specs, and domain notes
   - related Trellis tasks, research files, and session history when present
3. Separate what you found into:
   - confirmed facts
   - product intent still needed from the user
   - scope or risk decisions still needed from the user
   - likely out-of-scope items
4. Ask the single highest-value **remaining unresolved** question (after applying the No Re-Ask Rule).
5. Include your recommended answer with the question.
6. After each user answer, apply Write-Before-Next-Ask: update `prd.md` → `## 已确认决策` before continuing. Never re-ask that decision.
7. For complex tasks, create or update `design.md` and `implement.md` before implementation starts.
8. Before final review or `task.py start`, run the PRD convergence pass below.
9. When brainstorm has converged and the user agrees to OpenSpec 落盘, hand confirmed decisions to `openspec-change` to copy `## 已确认决策` into `proposal.md`. That copy is a later phase — not part of each brainstorm turn.

Do not invent a project-specific product/spec hierarchy. If the repository already has product, domain, or spec docs, use them. If it does not, proceed with the evidence that exists.

## Question Rules

Ask only one question per message.

Each question must include:

- the decision needed
- why the answer matters
- your recommended answer
- the trade-off if the user chooses differently

Do not ask process questions such as whether to search, inspect files, or continue brainstorming. Do the evidence work directly. Ask the user only when the remaining issue is a product decision, preference, scope boundary, or risk tolerance choice.

If you catch yourself about to ask something already in `## 已确认决策`, stop, cite the recorded conclusion, and move to the next unresolved branch — or end brainstorm if nothing unresolved remains.

## Thinking Framework: First Principles Analysis

When requirements are vague, solutions feel over-engineered, or you're about to add complexity "because everyone does" — decompose to fundamental truths before reasoning upward.

### Step 1: Restate the Problem

Strip away implementation details to one sentence.

### Step 2: List Fundamental Truths

What is absolutely true (not opinion or convention)?

### Step 3: Challenge Assumptions

For each component of the current plan:

- **Fact or convention?**
- **What if we removed this?**
- **Solving the actual problem or a symptom?**
- **Who benefits from this complexity?**

### Step 4: Build Up from Truths

1. Start with the minimum viable mechanism satisfying all truths
2. Add complexity only when a specific truth demands it
3. Each addition must answer: "Which truth requires this?"

### Step 5: Validate

- Does the solution solve the original problem?
- What assumptions need verification?
- What's the simplest experiment to test it?

## Artifact Rules

`prd.md` records requirements and acceptance:

- goal and user value
- confirmed facts
- `## 已确认决策` (brainstorm working memory — required during interview)
- requirements
- acceptance criteria
- out of scope
- open questions that still block planning (must not duplicate 已确认决策)

`design.md` records technical design for complex tasks.

`implement.md` records execution planning for complex tasks.

Lightweight tasks may have only `prd.md`. Complex tasks must have `prd.md`, `design.md`, and `implement.md` before `task.py start`.

## PRD Convergence Pass

Before declaring planning ready or running `task.py start`, rewrite `prd.md` once against the final structure. This is the final planning gate.

The pass must be lossless:

- Collapse repeated facts into one authoritative section.
- Fold temporary brainstorm sections such as `What I already know`, `Assumptions`, and resolved `Open Questions` into Goal, Background, Requirements, Technical Notes, or Acceptance Criteria.
- Keep `## 已确认决策` as the authoritative interview ledger; remove only rows that were superseded and explicitly replaced.
- Remove resolved open questions instead of leaving empty or already-answered sections.
- Preserve every file:line anchor, decision, constraint, requirement ID, and acceptance-criteria mapping.
- Keep only genuinely blocking open questions.

After the pass, read `prd.md` top to bottom and verify that no fact is repeated across sections unless the repetition adds new information.

## Quality Bar

Before declaring planning ready:

- `prd.md` contains testable acceptance criteria.
- `prd.md` has passed the PRD convergence pass.
- `## 已确认决策` reflects every user answer from the interview; none were left only in chat.
- Repository-answerable questions have already been answered through inspection.
- Remaining open questions are genuinely about user intent or scope.
- Complex tasks have `design.md` and `implement.md`.
- The user has reviewed the final planning artifacts or explicitly approved proceeding.

Do not start implementation until the user approves or asks for implementation.
