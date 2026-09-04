---
name: session-sync
description: >
  Run the full mid-session or end-of-work sync routine: stage and commit all outstanding structural work, push to remote, update AGENT_SYNC.md with cross-agent handoff notes, and create or append the session log. Use when: "session sync", "sync everything", "commit and sync", "push and log", "update agent sync", "end of work", "sync before I go", "commit all changes", "log session", or wanting to save progress without a full session close. Do NOT use for: single-file commits, or when there is nothing to commit.
---

# Skill: /session-sync — Divorce & Custody Assistant

Execute the complete sync routine: stage outstanding structural work, commit with a privacy-safe message, push to remote, update AGENT_SYNC.md, and create or append the session log.

## Privacy-first rule (every commit)

Never include in commit messages: party names, case numbers, specific allegations, financial figures, or identifying details. Describe **structure only**.

✅ "Update custody factor mapping logic"
❌ "Add evidence for [name] hearing"

---

## Step 1 — Refresh Exhibit 4

Run `/exhibit4-refresh` (see `.claude/skills/exhibit4-refresh.md`) before staging
anything else. It regenerates `vocational-compliance/exhibit-4*` from live public
commit history, runs its own privacy verification, and stages the result — or stops
and reports if that verification fails. Don't skip this even if this session's own
work didn't touch `vocational-compliance/` — the point is catching commits pushed to
*other* public repos (trading-assistant, tax-assistant, etc.) since the last regen.
(A commit-time hook was considered as a second trigger but deliberately not built —
see `specs/exhibit4-auto-refresh.spec.md` for why. This session-sync step is currently
the only automated trigger.)

## Step 2 — Check Status and Stage Work

If structural files changed this session, update the knowledge graph first:

```bash
graphify update .
```

`graphify update` is AST-only — **no API call, no cost, always safe to run.**

`graphify extract .` (full re-extraction) requires an LLM API key. Only needed if the graph doesn't exist yet or the repo structure has changed significantly. If extraction hits the Gemini free-tier rate limit (429), **stop and ask Christopher** before switching to a paid API key — do not auto-run with a paid key.

Then stage:

```bash
git status
git add specs/ AGENT-SYNC/ PENDING-TASKS.md CLAUDE.md AGENTS.md HANDOFF.md graphify-out/
```

Never stage: `sessions/`, `logs/`, `child-support/`, `custody/`, `divorce/`, `*alias`, `.env`, credentials, or any runtime case documents.

---

## Step 3 — Commit

```bash
git commit -m "$(cat <<'EOF'
Brief structural description — no names, case numbers, or identifying details

- What changed structurally
- Why it changed

Co-Authored-By: [agent] · [engine] · [model]
EOF
)"
```

Footer format is `Agent · Engine · Model` — see this repo's own `CLAUDE.md` ("Commit footer" line) for
the current values. Don't hardcode examples here; they drifted out of sync with `CLAUDE.md` once
already (dropped the `<noreply@anthropic.com>` tail, `Claude` → `ClaudeCodeCLI`, 2026-09-02) and a
second copy in this file is what let that happen unnoticed. This repo is managed by Alfred + Fortuna
directly, not Kavanah (see `CLAUDE.md`'s agent-roster section).

---

## Step 4 — Push

```bash
git push origin HEAD:main
```

If push fails (remote ahead):
```bash
git pull --rebase origin main && git push origin HEAD:main
```

---

## Step 5 — Update AGENT_SYNC.md (every sync)

Append to `AGENT-SYNC/AGENT_SYNC.md`:

```markdown
## 📡 [Month Day, Year] Session Summary ([Agent])
**Session type:** [infrastructure / case-work / research / cross-repo]
- [What was completed]
- [Key decision or outcome]
- Commit: [short hash] — [message]
```

---

## Step 6 — Backup Session JSONL (if small enough)

```bash
PROJ="$HOME/.claude/projects/-Users-christopherwilson-code-divorce-custody-assistant"
LATEST=$(ls -t "$PROJ"/*.jsonl 2>/dev/null | head -1)
SIZE=$(stat -f%z "$LATEST" 2>/dev/null)
[ -n "$LATEST" ] && [ "$SIZE" -lt 20971520 ] && \
  cp "$LATEST" AGENT-SYNC/app-data-claude/ && \
  echo "✓ Backed up $(basename $LATEST)" || \
  echo "⚠ JSONL too large (>20MB) or not found — stays at source only"
```

---

## Step 7 — Session Log (local only — gitignored)

Path: `logs/{agent}/2026/05-May/session_YYYYMMDD_{anthropic|nvidia}.md`

```markdown
## YYYY-MM-DD — [session type: case-work / infrastructure / research]
- [What was accomplished]
- [Key decision or outcome]
- Commit: [short hash] — [message]
```

Session logs are **never committed** in this repo (privacy). Local only.

---

## Step 8 — Final Push

```bash
git add AGENT-SYNC/
git commit -m "$(cat <<'EOF'
Update agent sync [date]

Co-Authored-By: [agent] · [engine] · [model]
EOF
)"
git push origin main
```

Same footer note as Step 3 — pull the current format from `CLAUDE.md`, don't hardcode it here.

---

## What NOT to do

- Never commit `sessions/`, `logs/`, or any case working directories
- Never write names, case numbers, or allegations in commit messages or AGENT_SYNC
- Don't skip AGENT_SYNC — it's how Alfred and Fortuna stay aligned between sessions
