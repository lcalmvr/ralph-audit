---
name: audit-results
description: "Compile audit findings into a fix PRD that Ralph can consume. Generates a standalone PRD from failed test stories. Triggers on: audit results, compile fixes, generate fix list, create fix prd."
user-invocable: true
---

# Audit Results — Compile Fix PRD

Read a tested audit checklist, compile all FAIL findings into a fix PRD formatted for `/ralph`, and mark the audit as REVIEWED.

---

## The Job

1. Find and load the tested audit file
2. Count results (pass/fail/skip/unclear)
3. Append a summary to the audit file
4. Generate a fix PRD from all FAIL stories
5. Update audit status to REVIEWED

**Important:** Do NOT fix anything. The fix PRD feeds into `/ralph`, which does the building.

---

## Step 1: Find the Audit

Use the shared audit selection logic:

1. **User specifies a name or path** → Load it directly.
2. **User specifies nothing** → Read `tasks/audits/backlog.md`. Find audits with status IN PROGRESS.
   - If exactly one → Use it automatically.
   - If multiple → Show a numbered list, ask the user to pick.
   - If none → Tell the user: "No audits with findings. Run `/audit-live` or `/audit-batch` first."

---

## Step 2: Append Summary to Audit File

At the bottom of the audit file, add:

```markdown
---

## Summary
- **Total Stories:** [N]
- **Passed:** [X]
- **Failed:** [Y]
- **Skipped:** [Z]
- **Unclear:** [U]
- **New Requirements Identified:** [R]
```

If there are items in the "New Requirements" section, keep them as-is — they are NOT part of the fix PRD.

Update the audit file status from IN PROGRESS to REVIEWED. Update backlog.md to match.

---

## Step 3: Generate Fix PRD

**Only if there are FAIL results.** If everything passed, skip this step and print: "All stories passed! No fix PRD needed."

**File:** `tasks/prd-fix-[feature-name].md`

The fix PRD must use the exact same structure as `/prd` output so `/ralph` can consume it without knowing it came from an audit.

### Fix PRD Template

```markdown
# Fix PRD: [Feature Name] — Audit Fixes

**Source Audit:** tasks/audits/audit-[feature-name].md
**Date:** YYYY-MM-DD

> Commit and merge current changes to main before running /ralph with this fix PRD.

## Introduction

This PRD addresses issues identified during manual QA audit of the [Feature Name] implementation. Each requirement maps to a failed test story from the audit checklist.

## Goals

- Resolve all FAIL findings from audit-[feature-name].md
- Maintain existing passing functionality (no regressions)

## User Stories

### US-001: [Fix title derived from the issue]
**Description:** As a [user], I want [the correct behavior] so that [benefit].
**From Audit Story [N]**
**Acceptance Criteria:**
- [Specific fix criterion — what the corrected behavior looks like]
- [Another criterion if needed]
- Typecheck passes
- Verify in browser using dev-browser skill

### US-002: ...

## Functional Requirements

- **FR-1:** [Specific, unambiguous requirement]
- **FR-2:** ...

## Non-Goals (Out of Scope)

- New features or enhancements not identified in the original audit
- Changes to passing functionality

## Success Metrics

- All previously failed audit stories pass on re-test
- No regressions in previously passing stories
```

### Fix PRD Rules

1. **Same structure as `/prd` output.** Introduction, Goals, User Stories, Functional Requirements, Non-Goals, Success Metrics.

2. **Every user story gets:**
   - "Typecheck passes" as acceptance criterion
   - "Verify in browser using dev-browser skill" as acceptance criterion
   - A "From Audit Story N" reference for traceability

3. **Fixes are requirements, not bug reports.** Write "The carrier name field must be center-aligned within the modal" — not "carrier name is left-aligned (bug)."

4. **One issue per user story.** If one audit story uncovered multiple issues (e.g., alignment AND modal not closing), split them into separate user stories.

5. **Stories must be small.** Each must be completable in one Ralph iteration. If a fix is complex, split it.

6. **New requirements stay OUT.** They are in the audit file's "New Requirements" section and need a separate `/prd` cycle.

7. **Sequential IDs.** US-001, US-002, etc. FR-1, FR-2, etc.

---

## Step 4: Print Summary

After generating everything, print:

```
Audit results compiled for: [Feature Name]

Summary: X passed, Y failed, Z skipped
Fix PRD: tasks/prd-fix-[feature-name].md ([Y] user stories)

Next steps:
1. Commit and merge current changes to main
2. Run `/ralph` with the fix PRD
3. After Ralph finishes, run `/audit-recheck` to verify fixes
```

If there are new requirements, also print:

```
New requirements identified (not in fix PRD):
- NR-1: [Description] — needs separate /prd cycle
```
