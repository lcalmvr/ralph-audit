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
2. Filter to only FAIL stories (from the Hub's results JSON)
3. Open the Audit Hub so the user can re-test
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

**Load two files:**
- `tasks/audits/audit-[feature].json` — the checklist (story details)
- `tasks/audits/results-[feature].json` — the previous test results from the Hub

---

## Step 2: Show Failed Stories

Read the results JSON. Collect stories where `results[id] === "fail"`. Cross-reference with the checklist JSON to get story titles.

Print:

```
Rechecking [Feature Name] — [N] failed stories to verify

Previously failed:
- Story 3: [Title] — [Notes from previous test]
- Story 7: [Title] — [Notes from previous test]
- Story 12: [Title] — [Notes from previous test]

The Audit Hub will open with your checklist. Re-test the failed stories above.
Make sure Ralph's fixes are committed and merged to main.
```

---

## Step 3: Open the Audit Hub

Start the hub server and open it:

```bash
python ~/.claude/skills/ralph-audit/serve.py tasks/audits &
open http://localhost:4000/?feature=[feature-name]
```

Tell the user to re-test the failed stories in the Hub by updating their pass/fail status. Wait for them to confirm they're done.

---

## Step 4: Reload and Evaluate Results

After the user confirms re-testing is complete, re-read `tasks/audits/results-[feature].json` to get updated results.

Check only the previously-failed story IDs:

### All Previously-Failed Stories Now Pass

```
All fixes verified! [Feature Name] audit is now CLOSED.

Recheck results:
- Story 3: PASS (was FAIL)
- Story 7: PASS (was FAIL)
- Story 12: PASS (was FAIL)
```

- Update audit markdown file status to CLOSED
- Update backlog.md status to CLOSED

### Some Stories Still Fail

```
Recheck results for [Feature Name]:
- Story 3: PASS (was FAIL)
- Story 7: STILL FAILING — [new notes]
- Story 12: PASS (was FAIL)

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

Results accumulate in the same `results-[feature].json` file — the Hub overwrites results as stories are re-tested.
