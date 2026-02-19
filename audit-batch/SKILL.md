---
name: audit-batch
description: "Log audit results from freeform testing notes. Paste your notes, they get mapped to the checklist, and a fix PRD is generated. Triggers on: audit batch, log test results, here are my test notes, batch audit."
user-invocable: true
---

# Audit Batch — Log Results from Freeform Notes

Take the user's freeform testing notes, map them to audit stories, log results, and generate the fix PRD.

---

## The Job

1. Find and load the audit checklist
2. Receive freeform testing notes from the user
3. Map notes to specific stories
4. Log pass/fail/skip/unclear for each story
5. Automatically run the `/audit-results` workflow (summary + fix PRD)

---

## Step 1: Find the Audit

Use the shared audit selection logic:

1. **User specifies a name or path** → Load it directly.
2. **User specifies nothing** → Read `tasks/audits/backlog.md`. Find audits with status PENDING or IN PROGRESS.
   - If exactly one → Use it automatically.
   - If multiple → Show a numbered list, ask the user to pick.
   - If none → Tell the user: "No pending audits. Run `/audit` to generate one."

---

## Step 2: Receive Notes

The user provides testing notes in any format. Examples:

**Structured:**
```
Stories 1-4 passed. Story 5 failed — carrier name is left aligned and modal doesn't close. Story 6 passed. Skipped 7. Story 8 works but I realized we need bulk upload too.
```

**Unstructured:**
```
The submission form mostly works but the alignment is off on carrier name and the modal stays open after save. Everything else looked fine except I couldn't test the export because the button was missing.
```

**Mixed with screenshots:**
The user may also share screenshots. Handle them the same as in `/audit-live` — immediately describe the visual issue in text.

---

## Step 3: Map Notes to Stories

For each story in the audit checklist, determine a result:

- **PASS** — User explicitly says it passed, or says "everything else worked" (implying stories not mentioned as failures passed).
- **FAIL** — User describes a problem that maps to this story's expected behavior.
- **SKIPPED** — User says they skipped it or couldn't test it.
- **UNCLEAR** — The notes don't clearly address this story. Could be a pass (user didn't mention any issues) or could be untested.

### Mapping Rules

1. **Explicit story references** ("Story 5 failed") → Map directly.
2. **Feature descriptions** ("carrier name alignment is off") → Match to the story that tests carrier name display.
3. **Blanket passes** ("everything else looked fine") → Mark unmentioned stories as PASS, but add a note: "Implied pass — not explicitly tested."
4. **Unmentioned stories with no blanket statement** → Mark as UNCLEAR with note: "Not addressed in testing notes."
5. **New requirements** ("realized we need bulk upload") → Do NOT mark any story. Add to "New Requirements" section.

### Ambiguity Handling

When a note is ambiguous, mark as UNCLEAR and explain:

```markdown
**Result:** ⚠ UNCLEAR
**Notes:** User notes mention "couldn't test the export because the button was missing." This may indicate a FAIL (export button not rendered) or may be an environment issue. Flagged for follow-up.
```

---

## Step 4: Log Results

Update the audit file with results in the same format as `/audit-live`:

- `✓ PASS` for passes
- `✗ FAIL` for failures (with detailed notes)
- `⊘ SKIPPED` for skips
- `⚠ UNCLEAR` for ambiguous items

Update the audit status to IN PROGRESS. Update backlog.md.

---

## Step 5: Show the User What Was Mapped

Before generating the fix PRD, show the user a summary of how their notes were mapped:

```
Mapped your notes to 15 stories:
- Passed: 10 (3 implied)
- Failed: 3
- Skipped: 1
- Unclear: 1

Unclear items:
- Story 7: "couldn't test export" — FAIL or environment issue?

Does this mapping look right? (Say "yes" to proceed, or correct any items)
```

Wait for confirmation. If the user corrects items, update the audit file before proceeding.

---

## Step 6: Generate Results

After confirmation, automatically run the `/audit-results` workflow:
1. Append summary to audit file
2. Generate fix PRD at `tasks/prd-fix-[feature-name].md`
3. Mark audit as REVIEWED
4. Update backlog.md

See `/audit-results` skill for the full workflow.
