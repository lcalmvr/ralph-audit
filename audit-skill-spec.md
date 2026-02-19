# /audit Skill Spec — SoftBox Development QA Process

## Purpose

Standardize the manual testing and feedback loop that happens after `ralph.sh` finishes building features. This skill closes the gap between "code is built" and "code is verified and ready for the next cycle."

## Context: Where This Fits in the Pipeline

```
Ramble → /prd → PRD saved to tasks/ (as prd-[feature-name].md)
PRD → /ralph → JSON task file
JSON → ralph.sh → features built (branches from main)
Developer commits + merges to main
─── THIS SKILL FILLS THE GAP BELOW ───
/audit → test checklist generated, added to backlog
/audit-live OR /audit-batch → findings logged
/audit-results → fix list compiled, formatted for /ralph
Developer commits + merges to main
Fix list → /audit-results generates a fix PRD → /ralph consumes it → ralph.sh → /audit-recheck (failed stories only)
/audit-recheck → all pass → audit CLOSED
Repeat until clean
```

New requirements discovered during testing do NOT go through /audit. They start a new ramble → /prd cycle.

---

## Commands

### 1. `/audit`

**What it does:** Reads the PRD for a given feature, generates a numbered checklist of plain-language test stories, saves it to disk, and adds an entry to the backlog index.

**Input:** The PRD file path or feature name. If ambiguous, prompt the user to select from available PRDs in `tasks/`.

**Output:** A markdown file saved to `tasks/audits/audit-[feature-name].md` with the following structure:

```markdown
# Audit Checklist: [Feature Name]
**PRD:** tasks/prd-[feature-name].md
**Date Generated:** YYYY-MM-DD
**Status:** PENDING

---

## Test Stories

### Story 1: [Short description]
**Area:** [Feature area / page / component]
**Steps:**
1. Navigate to [specific page/URL]
2. Click [specific element]
3. Enter [specific data] into [specific field]
4. Click [specific button]

**Expected Result:** [What should happen, described visually]

**Result:** ☐ PASS / ☐ FAIL
**Notes:**

---

### Story 2: [Short description]
...
```

**Test story rules:**
- Every story must be testable by a non-developer. No jargon, no "CRUD enabled," no "API returns 200."
- Steps must reference specific UI elements: page names, button labels, field names, visible text.
- Expected results describe what the user SEES, not what the code does. "The carrier name appears in the list" not "Record is persisted to database."
- Group stories by feature area / page / component.
- Include negative cases where relevant: "Leave carrier name blank and click save. Verify an error message appears below the field."
- Number stories sequentially across the entire checklist (Story 1 through Story N, not restarting per section).

**Backlog index:** After generating the checklist, append an entry to `tasks/audits/backlog.md`:

```markdown
| Feature | PRD | Audit File | Date | Status |
|---------|-----|------------|------|--------|
| Submission Intake | tasks/prd-submission-intake.md | tasks/audits/audit-submission-intake.md | 2026-02-19 | PENDING |
```

If `backlog.md` doesn't exist, create it with the table header.

**Git reminder:** Before generating, remind the user: "Make sure your current changes from ralph.sh are committed and merged to main."

---

### 2. `/audit-live`

**What it does:** Starts an interactive testing session. Pulls up a pending audit checklist and walks the user through stories one at a time, logging results as they go.

**Input:** Feature name or audit file path. If omitted and there's only one IN PROGRESS or PENDING audit, use it. If multiple, show a list from backlog.md and ask the user to pick.

**Behavior:**
1. Load the audit checklist file.
2. Present Story 1 to the user — show the steps and expected result.
3. Wait for the user's response. Acceptable inputs:
   - "pass" or "yes" or "good" → Mark PASS, move to next story.
   - "fail" or "no" + description → Mark FAIL, log the user's notes as findings. The user may share a screenshot — immediately describe it in text and log the description (see screenshot handling below).
   - "skip" → Mark SKIPPED, move to next story.
   - "stop" or "done for now" → Save progress and exit. Status remains IN PROGRESS. User can resume later.
   - New requirement or scope change identified → Log it in a separate "New Requirements" section at the bottom of the audit file. Do NOT mix it into the fix list.
4. After each response, present the next story.
5. When all stories are complete (or user says "done"), print a summary: X passed, Y failed, Z skipped. Prompt the user to run `/audit-results` to compile the fix list.

**Logging format:** As the user reports findings, update the audit file in place:

```markdown
### Story 5: Save new submission
...
**Result:** ✗ FAIL
**Notes:** Carrier name field is left-aligned within the modal body. Should be center-aligned consistent with other form fields. Modal also does not close after clicking save — stays open with no confirmation.
```

**Screenshot handling:** Screenshots are ephemeral — they live in the conversation, not on disk. When the user drags a screenshot into the terminal:

1. Look at the screenshot immediately
2. Write a detailed text description into the Notes field right then — do NOT defer this
3. The text description IS the permanent record. Focus on:
   - What specific element is wrong
   - What it currently looks like (position, color, size, text content)
   - What it should look like
   - Spatial relationships (alignment, positioning relative to other elements)
   - Any other visible issues in the screenshot
4. No file is saved, no path is referenced, no cleanup needed

**Status updates:** Mark the audit file status as IN PROGRESS when the session starts. Update backlog.md accordingly. When resuming an IN PROGRESS audit, pick up from the first untested story (no Result logged yet).

---

### 3. `/audit-results`

**What it does:** Reads a completed (or partially completed) audit file, compiles all FAIL findings into a structured fix list formatted as input for `/ralph`, and marks the audit as REVIEWED.

**Input:** Feature name or audit file path. If omitted and there's only one IN PROGRESS audit, use it. If multiple, show a picker.

**Output:** Two things happen:

#### A. Audit file gets a summary appended

```markdown
---

## Summary
- **Total Stories:** 10
- **Passed:** 7
- **Failed:** 2
- **Skipped:** 1
- **New Requirements Identified:** 1

---

## New Requirements (separate /prd cycle)

### NR-1: Bulk submission upload
**From Story 8**
**Description:** During testing, realized we need the ability to upload multiple submissions via CSV. Not covered in original PRD.
**Action:** New ramble → /prd → /ralph cycle. Not a fix.
```

#### B. A fix PRD is generated as a separate file

`/audit-results` generates a **standalone PRD file** saved to `tasks/prd-fix-[feature-name].md`. This file uses the same structure that `/prd` produces, so `/ralph` can consume it directly without knowing the difference.

The fix PRD follows the `/prd` output format: Introduction, Goals, User Stories with acceptance criteria, and Functional Requirements. Each failed audit story becomes a user story with verifiable acceptance criteria.

```markdown
# Fix PRD: [Feature Name] — Audit Fixes

**Source Audit:** tasks/audits/audit-[feature-name].md
**Date:** YYYY-MM-DD

> Commit and merge current changes to main before running /ralph with this fix PRD.

## Introduction

This PRD addresses issues identified during manual QA audit of the [Feature Name] implementation. Each requirement below maps to a specific failed test story from the audit checklist.

## Goals

- Resolve all FAIL findings from audit-[feature-name].md
- Maintain existing passing functionality (no regressions)

## User Stories

### US-1: Carrier name field alignment
**Description:** As a user, I want the carrier name field in the submission modal to be visually consistent with other form fields so the interface looks professional.
**From Audit Story 5**
**Acceptance Criteria:**
- Carrier name field is center-aligned within the new submission modal
- Alignment and padding matches all other form fields in the same modal
- Typecheck passes
- Verify in browser using dev-browser skill

### US-2: Modal closes with confirmation after save
**Description:** As a user, I want confirmation that my submission was saved and to be returned to the list so I know the action completed.
**From Audit Story 5**
**Acceptance Criteria:**
- After successful save, modal closes automatically
- Brief success confirmation is displayed (toast or inline message)
- User is returned to submissions list with new entry visible
- Typecheck passes
- Verify in browser using dev-browser skill

## Functional Requirements

- **FR-1:** Center-align the carrier name input field within the new submission modal, matching the alignment and padding of all other form fields in that modal.
- **FR-2:** On successful submission save, close the modal, display a transient success message, and return the user to the submissions list view with the newly created entry visible.

## Non-Goals (Out of Scope)

- New features or enhancements not identified in the original audit
- Changes to passing functionality

## Success Metrics

- All previously failed audit stories pass on re-test
- No regressions in previously passing stories
```

**Fix PRD rules:**
- The fix PRD must use the same structure as `/prd` output: Introduction, Goals, User Stories (with "As a [user]..." descriptions and acceptance criteria), Functional Requirements (FR-1, FR-2, etc.), Non-Goals, and Success Metrics.
- Every user story must include "Typecheck passes" and "Verify in browser using dev-browser skill" as acceptance criteria (matching `/prd` conventions).
- Each user story maps back to a specific audit story number for traceability.
- User stories must be small enough to complete in one Ralph iteration. If a failed audit story is too complex, split it into multiple user stories.
- Fixes are written as requirements, not bug reports. "The carrier name field must be center-aligned" not "carrier name is left-aligned (bug)."
- If one audit story produced multiple issues, they become separate user stories.
- New requirements are NOT included in the fix PRD. They stay in the audit file's "New Requirements" section and require a separate ramble → /prd cycle.

**Status update:** Mark the audit file status as REVIEWED. Update backlog.md.

---

### 4. `/audit-batch`

**What it does:** Takes a block of freeform text (the user's testing notes), maps findings against the audit checklist, logs results, and automatically runs `/audit-results` at the end.

**Input:**
1. Feature name or audit file path. If omitted and there's only one PENDING or IN PROGRESS audit, use it. If multiple, show a picker.
2. A block of freeform text — the user's testing notes in whatever format they wrote them.

**Behavior:**
1. Load the audit checklist.
2. Parse the freeform text. Match findings to story numbers where possible. The user might write:
   - "Stories 1-4 passed. Story 5 failed — carrier name is left aligned and modal doesn't close. Story 6 passed. Skipped 7. Story 8 — this works but I realized we need bulk upload too."
   - Or less structured: "The submission form mostly works but the alignment is off on carrier name and the modal stays open after save. Everything else looked fine except I couldn't test the export because the button was missing."
3. For each story, determine PASS / FAIL / SKIPPED based on the text. If the text is ambiguous for a story, mark it as UNCLEAR and include a note.
4. Log all findings into the audit file in the same format as `/audit-live`.
5. Automatically run `/audit-results` logic — compile summary, fix list, and new requirements.

**Ambiguity handling:** If the user's notes don't clearly map to specific stories, do your best to match and flag anything uncertain:

```markdown
### Story 7: Export submissions to CSV
**Result:** ⚠ UNCLEAR
**Notes:** User notes mention "couldn't test the export because the button was missing." This may indicate a FAIL (export button not rendered) or may be an environment issue. Flagged for follow-up.
```

---

### 5. `/audit-recheck`

**What it does:** Loads a REVIEWED audit, filters to only the FAIL stories, walks the user through re-testing just those. Used after Ralph fixes issues from the fix PRD.

**Input:** Feature name or audit file path. If omitted and there's only one REVIEWED audit, use it. If multiple, show a picker.

**Behavior:**
1. Load the audit file. Only show stories that were marked FAIL.
2. Present each failed story one at a time (same flow as `/audit-live`).
3. For each story, user responds pass/fail/skip.
4. If ALL previously-failed stories now pass:
   - Mark audit status as CLOSED
   - Update backlog.md
   - Print: "All fixes verified. Audit closed."
5. If some stories still fail:
   - Keep status as REVIEWED
   - Ask: "X stories still failing. Run /audit-results to generate an updated fix PRD?"
   - If yes, generate a new fix PRD (`prd-fix-[feature-name]-r2.md`) with only the remaining failures

**Round tracking:** Append round number to fix PRDs after the first: `prd-fix-feature-r2.md`, `prd-fix-feature-r3.md`. The original audit file accumulates all results — each re-check updates the Result field in place.

---

## Audit Selection Logic (shared across all commands)

Since multiple audits can be open at once, every command uses this logic:

1. **User specifies a name or path** → Use it directly
2. **User specifies nothing, only one audit in the relevant status** → Use it automatically
3. **User specifies nothing, multiple audits in the relevant status** → Show a numbered list from backlog.md, ask user to pick

Relevant statuses per command:
- `/audit-live`: PENDING or IN PROGRESS
- `/audit-batch`: PENDING or IN PROGRESS
- `/audit-results`: IN PROGRESS (has findings logged)
- `/audit-recheck`: REVIEWED

---

## File Structure

```
tasks/
├── prd-submission-intake.md          # Original PRD from /prd
├── prd-fix-submission-intake.md      # Fix PRD from /audit-results (consumed by /ralph)
├── prd-fix-submission-intake-r2.md   # Second round fix PRD (if needed)
├── prd-carrier-management.md
└── audits/
    ├── backlog.md                     # Index of all audits and their status
    ├── audit-submission-intake.md     # Individual audit files
    ├── audit-carrier-management.md
    └── ...
```

**Backlog statuses:**
- `PENDING` — Checklist generated, not yet tested
- `IN PROGRESS` — Testing started via /audit-live, not finished
- `REVIEWED` — Testing complete, fix list compiled
- `CLOSED` — All fixes verified in subsequent audit-recheck cycle

---

## Git / Branch Workflow Reminders

The skill does NOT interact with git. But it must remind the user at key moments:

1. **Before running `/audit`:** "Make sure your current changes from ralph.sh are committed and merged to main."
2. **At the top of the fix PRD output:** "Commit and merge current changes to main before running /ralph with this fix PRD."
3. **These are reminders only.** The user handles git manually.

---

## What This Skill Does NOT Do

- **No screenshot storage.** Screenshots are ephemeral in the Claude Code conversation. Findings are captured as text descriptions written immediately when the screenshot is shared.
- **No git operations.** Commit and merge are manual.
- **No code fixes.** The fix list feeds into /ralph, which does the building.
- **No new PRDs.** New requirements identified during audit are flagged for a separate /prd cycle.
- **No automated testing.** This is a human testing workflow. The skill structures the process, not replaces the tester.
