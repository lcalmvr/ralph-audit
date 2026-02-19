# ralph-audit

Manual QA testing skills for [Claude Code](https://docs.anthropic.com/en/docs/claude-code), designed to work with the [Ralph](https://github.com/snarktank/ralph) autonomous agent pipeline.

Closes the gap between "code is built" and "code is verified" — generates test checklists from PRDs, walks you through testing, and compiles failures into fix PRDs that Ralph can consume directly.

## Pipeline

```
/prd → /ralph → ralph.sh → features built
                                ↓
                            /audit → test checklist generated
                                ↓
                     /audit-live or /audit-batch → findings logged
                                ↓
                         /audit-results → fix PRD generated
                                ↓
                  /ralph → ralph.sh → fixes built
                                ↓
                         /audit-recheck → verify fixes → CLOSED
```

## Commands

| Command | What it does |
|---------|-------------|
| `/audit` | Read a PRD, generate a numbered test checklist with plain-language stories |
| `/audit-live` | Interactive testing — walk through stories one at a time, log pass/fail |
| `/audit-batch` | Paste freeform testing notes, auto-map to stories, generate fix PRD |
| `/audit-results` | Compile FAIL findings into a standalone fix PRD for Ralph |
| `/audit-recheck` | Re-test only failed stories after fixes. All pass → audit CLOSED |

## Audit Hub

A web UI for shared QA testing. Two people can test the same checklist and see each other's pass/fail results in real time.

```bash
# Start the hub (from your project root)
python ~/.claude/skills/ralph-audit/serve.py tasks/audits

# Opens at http://localhost:4000
# Share via ngrok: ngrok http 4000
```

The hub reads `audit-*.json` files from the directory you point it at, and saves results to `results-*.json` in the same directory. No database, no dependencies beyond Python 3.

The `/audit` skill generates the JSON files automatically. You can also write them by hand:

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

## Install

Clone into your Claude Code skills directory:

```bash
cd ~/.claude/skills
git clone https://github.com/lcalmvr/ralph-audit.git
cd ralph-audit

# Symlink each skill so Claude Code discovers them
cd ~/.claude/skills
ln -s ralph-audit/audit audit
ln -s ralph-audit/audit-live audit-live
ln -s ralph-audit/audit-batch audit-batch
ln -s ralph-audit/audit-results audit-results
ln -s ralph-audit/audit-recheck audit-recheck
```

Restart Claude Code. The five `/audit-*` commands will be available.

## How It Works

### `/audit` — Generate Checklist

Point it at a PRD and it generates a test checklist at `tasks/audits/audit-[feature].md` and `tasks/audits/audit-[feature].json`. Every test story is written in plain language — specific UI elements, specific actions, specific expected results. No jargon. Opens the Audit Hub automatically.

### `/audit-live` — Interactive Testing

Presents stories one at a time. You respond pass/fail/skip. Drop in screenshots — they get described as text and logged (no files saved). Stop anytime, resume later.

### `/audit-batch` — Bulk Results

Paste your freeform testing notes. The skill maps them to stories, shows you the mapping for confirmation, then generates the fix PRD.

### `/audit-results` — Fix PRD

Compiles all failures into a standalone PRD file (`tasks/prd-fix-[feature].md`) that uses the same format as `/prd` output. Ralph consumes it directly — no translation needed.

### `/audit-recheck` — Verify Fixes

After Ralph fixes things, re-test only the failed stories. All pass → audit closed. Still failing → generates another fix PRD (round 2, 3, etc.) until clean.

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
        ├── audit-feature-name.json      # Machine-readable (hub reads this)
        └── results-feature-name.json    # Pass/fail results (hub writes this)
```

## Design Spec

See [audit-skill-spec.md](audit-skill-spec.md) for the full design document.

## Requirements

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code)
- Python 3 (for the Audit Hub — no pip packages needed)
- [Ralph](https://github.com/snarktank/ralph) (for the full pipeline — audit skills work standalone too)

## License

MIT
