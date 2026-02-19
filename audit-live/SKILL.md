---
name: audit-live
description: "Interactive manual testing session. Walk through an audit checklist story by story, logging pass/fail results. Triggers on: start testing, audit live, test session, walk me through the audit, let's test."
user-invocable: true
---

# Audit Live — Interactive Testing Session

Walk the user through an audit checklist story by story, logging results in real time.

---

## The Job

1. Find and load the audit checklist
2. Present each story one at a time
3. Log the user's pass/fail/skip responses
4. Handle screenshots by writing text descriptions immediately
5. Save progress to the audit file after each story
6. Print summary when done

---

## Step 1: Find the Audit

Use the shared audit selection logic:

1. **User specifies a name or path** → Load it directly.
2. **User specifies nothing** → Read `tasks/audits/backlog.md`. Find audits with status PENDING or IN PROGRESS.
   - If exactly one → Use it automatically.
   - If multiple → Show a numbered list, ask the user to pick.
   - If none → Tell the user: "No pending audits. Run `/audit` to generate one."

If the audit status is PENDING, update it to IN PROGRESS. Update `backlog.md` to match.

If the audit is IN PROGRESS (resuming), find the first story that has no Result logged yet and start from there.

---

## Step 2: Present Stories

For each untested story, show:

```
**Story N: [Title]**
Area: [Area]

Steps:
1. [Step 1]
2. [Step 2]
3. [Step 3]

Expected: [Expected result]

Pass, fail, or skip?
```

Then wait for the user's response.

---

## Step 3: Handle Responses

**"pass" / "yes" / "good" / "p"**
→ Update the audit file:
```markdown
**Result:** ✓ PASS
**Notes:**
```
→ Move to next story.

**"fail" / "no" / "f" + description**
→ Update the audit file:
```markdown
**Result:** ✗ FAIL
**Notes:** [User's description of the issue]
```
→ Move to next story.

**User shares a screenshot (with or without text)**
→ This is a FAIL. Immediately:
1. Look at the screenshot
2. Write a detailed text description into the Notes field. Include:
   - What specific element is wrong
   - What it currently looks like (position, color, size, text)
   - What it should look like
   - Spatial relationships relative to other elements
   - Any other visible issues
3. The text description is the permanent record — no file is saved
4. If the user also typed a description, combine both
→ Update the audit file with the text description.
→ Move to next story.

**"skip" / "s"**
→ Update the audit file:
```markdown
**Result:** ⊘ SKIPPED
**Notes:**
```
→ Move to next story.

**"stop" / "done for now" / "pause"**
→ Save current progress. Status stays IN PROGRESS.
→ Print progress so far: "Completed X of Y stories. Z passed, W failed. Resume anytime with `/audit-live`."
→ Stop presenting stories.

**User mentions a new requirement or feature idea**
→ Acknowledge it, but do NOT log it as a pass/fail.
→ Add it to a "New Requirements" section at the bottom of the audit file:
```markdown
## New Requirements

### NR-1: [Short description]
**Identified during Story N**
**Description:** [What the user described]
**Action:** New ramble → /prd → /ralph cycle. Not a fix.
```
→ Then re-present the current story for a pass/fail verdict.

---

## Step 4: Summary

When all stories are tested (or user says "done"), print:

```
Audit complete: [Feature Name]
- Passed: X
- Failed: Y
- Skipped: Z
- New Requirements: N

[If Y > 0]: Run `/audit-results` to compile the fix list for Ralph.
[If Y == 0]: All stories passed! No fixes needed.
```

---

## File Updates

Every time a result is logged, update the audit file immediately. Don't batch updates — if the session crashes, progress is preserved.

The audit file and backlog.md are the only files modified by this skill.
