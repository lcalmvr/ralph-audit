---
name: audit
description: "Generate a manual test checklist from a PRD. Use when a feature has been built and needs QA testing. Triggers on: create audit, audit this, generate test checklist, qa checklist, test this feature."
user-invocable: true
---

# Audit Checklist Generator

Generate a numbered manual test checklist from a PRD, saved to disk and tracked in the audit backlog.

---

## The Job

1. Identify the PRD to audit
2. Read the PRD thoroughly
3. Generate test stories — plain language, testable by a non-developer
4. Save to `tasks/audits/audit-[feature-name].md`
5. Add entry to `tasks/audits/backlog.md`

**Important:** Do NOT start testing. Just create the checklist. Remind the user: "Make sure your current changes from ralph.sh are committed and merged to main before testing."

---

## Step 1: Find the PRD

**Input:** The user provides a PRD file path, feature name, or nothing.

- If a file path is given, use it directly.
- If a feature name is given, look for `tasks/prd-[feature-name].md`.
- If nothing is given, list all `tasks/prd-*.md` files (excluding `prd-fix-*`) and ask the user to pick.

Read the PRD thoroughly before generating stories.

---

## Step 2: Generate Test Stories

Write test stories that follow these rules strictly:

### What Makes a Good Test Story

- **Testable by a non-developer.** No jargon: no "CRUD," no "API returns 200," no "state updates," no "component renders."
- **Steps reference specific UI elements:** page names, URLs, button labels, field names, visible text on screen.
- **Expected results describe what the user SEES:** "The carrier name appears in the list" — not "Record is persisted to database."
- **One thing per story.** Don't combine "add a carrier AND edit it AND delete it" into one story.
- **Include negative cases:** "Leave the name field blank and click Save — an error message appears below the field."

### What Makes a Bad Test Story

- "CRUD works" — What does this mean? Test what?
- "Page loads correctly" — What should be ON the page?
- "All 6 tabs functional" — That's 6 stories, not 1.
- "Styling matches other pages" — Matches WHAT specifically?
- "API returns data" — The tester can't see API responses.

### Story Format

```markdown
### Story N: [Short description of what you're testing]
**Area:** [Page name or component]
**Steps:**
1. Navigate to `http://localhost:3000/[specific-url]`
2. [Specific action — click, type, select, scroll]
3. [Another specific action]

**Expected Result:** [What you should see — describe the visual outcome]

**Result:** ☐ PASS / ☐ FAIL
**Notes:**
```

### Grouping and Numbering

- Group stories by feature area, page, or component. Use markdown `##` headers for groups.
- Number stories sequentially across the entire checklist: Story 1, Story 2, ... Story N. Do NOT restart numbering per section.

---

## Step 3: Save the Checklist

**File:** `tasks/audits/audit-[feature-name].md`

```markdown
# Audit Checklist: [Feature Name]
**PRD:** tasks/prd-[feature-name].md
**Date Generated:** YYYY-MM-DD
**Status:** PENDING

---

## [Section Name]

### Story 1: ...
...

### Story 2: ...
...

## [Next Section]

### Story 3: ...
...
```

Create the `tasks/audits/` directory if it doesn't exist.

---

## Step 4: Update Backlog

**File:** `tasks/audits/backlog.md`

If the file doesn't exist, create it with the table header:

```markdown
# Audit Backlog

| Feature | PRD | Audit File | Date | Status |
|---------|-----|------------|------|--------|
```

Append a row for the new audit:

```markdown
| [Feature Name] | tasks/prd-[feature-name].md | tasks/audits/audit-[feature-name].md | YYYY-MM-DD | PENDING |
```

---

## Checklist Before Saving

- [ ] Every story is testable by someone who has never seen the code
- [ ] Steps reference specific pages, URLs, buttons, and fields
- [ ] Expected results describe what the user SEES on screen
- [ ] No story combines multiple distinct tests
- [ ] Negative cases included where relevant
- [ ] Stories numbered sequentially (no restarts per section)
- [ ] Saved to `tasks/audits/audit-[feature-name].md`
- [ ] Backlog entry added to `tasks/audits/backlog.md`
