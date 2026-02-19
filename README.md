# ralph-audit

Manual QA testing for [Claude Code](https://docs.anthropic.com/en/docs/claude-code), designed for the [Ralph](https://github.com/snarktank/ralph) autonomous agent pipeline.

Closes the gap between "code is built" and "code is verified" — generates test checklists from PRDs, provides a shared web UI for testing, and compiles failures into fix PRDs that Ralph consumes directly.

## Workflow

```
Feature built (by Ralph or manually)
        ↓
    /audit → generates test checklist + opens Audit Hub
        ↓
    Test in Hub (http://localhost:4000) — share via ngrok
        ↓
    /audit-results → compiles failures into fix PRD
        ↓
    /ralph → fixes built
        ↓
    /audit-recheck → re-test failures only → all pass = CLOSED
```

### Step by step

1. **`/audit`** — Point it at a PRD. It generates a test checklist (.md + .json), starts the Audit Hub, and opens it in your browser.
2. **Test in the Hub** — Click through stories, mark pass/fail/skip, add notes. Results auto-save to disk. Share the URL via ngrok for pair testing.
3. **`/audit-results`** — Reads the Hub's results JSON, compiles all failures into a fix PRD (`tasks/prd-fix-[feature].md`) that Ralph can consume directly.
4. **`/ralph`** — Feed it the fix PRD. Fixes get built.
5. **`/audit-recheck`** — Opens the Hub, you re-test only the failed stories. All pass = audit closed. Still failing = another fix PRD, repeat from step 4.

## Audit Hub

A web UI for shared QA testing. Two people can test the same checklist and see each other's results in real time.

```bash
# Start the hub (from your project root)
python ~/.claude/skills/ralph-audit/serve.py tasks/audits

# Opens at http://localhost:4000
# Share via ngrok: ngrok http 4000
```

The `/audit` skill starts the hub automatically — you only need to run this manually if the server isn't already running.

**Features:**
- Pass / Fail / Skip buttons per story, with notes on any status
- New Requirements section — capture ideas that come up during testing (not bugs, but new work)
- Shared persistence — results save to JSON files on disk, visible to all connected browsers
- Export Results button for downloading raw JSON
- Progress tracking with pass/fail/skip/remaining counts

The hub reads `audit-*.json` files from the directory you point it at and saves results to `results-*.json` in the same directory. No database, no dependencies beyond Python 3.

## Install

```bash
cd ~/.claude/skills
git clone https://github.com/lcalmvr/ralph-audit.git

# Symlink each skill so Claude Code discovers them
ln -s ralph-audit/audit audit
ln -s ralph-audit/audit-live audit-live
ln -s ralph-audit/audit-batch audit-batch
ln -s ralph-audit/audit-results audit-results
ln -s ralph-audit/audit-recheck audit-recheck
```

Restart Claude Code. The `/audit*` commands will be available.

## Commands

| Command | What it does |
|---------|-------------|
| `/audit` | Generate a test checklist from a PRD, open the Hub |
| `/audit-results` | Read Hub results, compile failures into a fix PRD for Ralph |
| `/audit-recheck` | Re-test failed stories in the Hub after fixes. All pass = CLOSED |
| `/audit-live` | Walk through stories one at a time in the terminal (CLI alternative) |
| `/audit-batch` | Paste freeform testing notes, auto-map to stories (CLI alternative) |

## File Structure

```
your-project/
└── tasks/
    ├── prd-feature-name.md              # Original PRD
    ├── prd-fix-feature-name.md          # Fix PRD from audit (Ralph consumes this)
    ├── prd-fix-feature-name-r2.md       # Round 2 fixes (if needed)
    └── audits/
        ├── backlog.md                   # Index of all audits and statuses
        ├── audit-feature-name.md        # Human-readable checklist
        ├── audit-feature-name.json      # Machine-readable (Hub reads this)
        └── results-feature-name.json    # Pass/fail/skip + notes + new requirements (Hub writes this)
```

## JSON Format

### Checklist (`audit-*.json`)

The `/audit` skill generates these automatically. You can also write them by hand:

```json
{
  "feature": "my-feature",
  "prd": "tasks/prd-my-feature.md",
  "date": "2025-01-15",
  "sections": [
    {
      "title": "Section Name",
      "stories": [
        {
          "id": 1,
          "title": "What you're testing",
          "steps": ["Do this", "Then this"],
          "expected": "You should see this"
        }
      ]
    }
  ]
}
```

### Results (`results-*.json`)

Written by the Hub automatically. Read by `/audit-results` and `/audit-recheck`:

```json
{
  "feature": "my-feature",
  "updated_at": "2025-01-15T18:30:00+00:00",
  "results": { "1": "pass", "2": "fail", "3": "skip" },
  "notes": { "2": "Button is missing from the page" },
  "new_requirements": ["Need bulk upload capability"]
}
```

## Design Spec

See [audit-skill-spec.md](audit-skill-spec.md) for the full design document.

## Requirements

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code)
- Python 3 (for the Audit Hub — no pip packages needed)
- [Ralph](https://github.com/snarktank/ralph) (for the full pipeline — audit skills work standalone too)

## License

MIT
