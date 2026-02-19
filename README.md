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

Point it at a PRD and it generates a test checklist at `tasks/audits/audit-[feature].md`. Every test story is written in plain language — specific UI elements, specific actions, specific expected results. No jargon.

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
tasks/
├── prd-feature-name.md              # Original PRD
├── prd-fix-feature-name.md          # Fix PRD from audit (Ralph consumes this)
├── prd-fix-feature-name-r2.md       # Round 2 fixes (if needed)
└── audits/
    ├── backlog.md                    # Index of all audits and statuses
    ├── audit-feature-name.md         # Test checklists with results
    └── ...
```

## Design Spec

See [audit-skill-spec.md](audit-skill-spec.md) for the full design document.

## Requirements

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code)
- [Ralph](https://github.com/snarktank/ralph) (for the full pipeline — audit skills work standalone too)

## License

MIT
