---
name: audit-recheck
description: "Re-test only the failed stories from a previous audit. Used after Ralph fixes issues. Triggers on: recheck audit, verify fixes, retest failures, audit recheck."
user-invocable: true
---

# Audit Recheck — Verify Fixes

Re-test only the previously FAIL stories from a REVIEWED audit. Used after Ralph has fixed the issues from the fix PRD.

---

## The Job

1. Find and load a REVIEWED audit
2. Filter to only FAIL stories
3. Walk the user through re-testing each one
4. If all pass → mark audit CLOSED
5. If some still fail → offer to generate an updated fix PRD

---

## Step 1: Find the Audit

Use the shared audit selection logic:

1. **User specifies a name or path** → Load it directly.
2. **User specifies nothing** → Read `tasks/audits/backlog.md`. Find audits with status REVIEWED.
   - If exactly one → Use it automatically.
   - If multiple → Show a numbered list, ask the user to pick.
   - If none → Tell the user: "No reviewed audits to recheck. Run `/audit-results` on a tested audit first."

---

## Step 2: Filter to Failed Stories

Read the audit file. Collect only stories where `**Result:** ✗ FAIL`.

Print:

```
Rechecking [Feature Name] — [N] failed stories to verify

Previously failed:
- Story 3: [Title]
- Story 7: [Title]
- Story 12: [Title]

Let's go through them. Make sure Ralph's fixes are committed and merged to main.
```

---

## Step 3: Walk Through Failed Stories

Present each previously-failed story one at a time (same flow as `/audit-live`):

```
**Story N: [Title]** (previously FAILED)
Area: [Area]

Steps:
1. [Step 1]
2. [Step 2]

Expected: [Expected result]

Previous issue: [The notes from the original failure]

Pass, fail, or skip?
```

Handle responses the same as `/audit-live`:
- pass → Update result to `✓ PASS (recheck)`
- fail → Update result to `✗ FAIL (recheck)` with new notes
- screenshot → Describe in text, log as fail
- skip → `⊘ SKIPPED (recheck)`

Update the audit file after each response.

---

## Step 4: Evaluate Results

After all failed stories are re-tested:

### All Previously-Failed Stories Now Pass

```
All fixes verified! [Feature Name] audit is now CLOSED.

Recheck results:
- Story 3: ✓ PASS (was FAIL)
- Story 7: ✓ PASS (was FAIL)
- Story 12: ✓ PASS (was FAIL)
```

- Update audit file status to CLOSED
- Update backlog.md status to CLOSED

### Some Stories Still Fail

```
Recheck results for [Feature Name]:
- Story 3: ✓ PASS (was FAIL)
- Story 7: ✗ STILL FAILING
- Story 12: ✓ PASS (was FAIL)

[X] of [Y] fixes verified. [Z] still failing.

Generate an updated fix PRD for the remaining failures? (yes/no)
```

If yes:
- Generate `tasks/prd-fix-[feature-name]-r2.md` (or `-r3`, `-r4`, incrementing the round number)
- Use the same format as `/audit-results` fix PRD
- Only include the stories that still fail
- Print: "Fix PRD (round 2): `tasks/prd-fix-[feature-name]-r2.md`. Commit, merge, run `/ralph`, then `/audit-recheck` again."

If no:
- Keep status as REVIEWED
- Print: "Audit stays in REVIEWED status. Re-run `/audit-recheck` when ready."

---

## Round Tracking

Fix PRDs after the first round get a round suffix:
- Round 1: `prd-fix-[feature-name].md` (no suffix)
- Round 2: `prd-fix-[feature-name]-r2.md`
- Round 3: `prd-fix-[feature-name]-r3.md`

The original audit file accumulates all results. Recheck updates the Result field in place — the original failure notes are preserved, and the recheck result is appended or replaces the result marker.
