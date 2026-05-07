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

## Step 1 — Check Status and Stage Work

```bash
git status
git add specs/ AGENT-SYNC/ PENDING-TASKS.md CLAUDE.md AGENTS.md HANDOFF.md
```

Never stage: `sessions/`, `logs/`, `child-support/`, `custody/`, `divorce/`, `*alias`, `.env`, credentials, or any runtime case documents.

---

## Step 2 — Commit

```bash
git commit -m "$(cat <<'EOF'
Brief structural description — no names, case numbers, or identifying details

- What changed structurally
- Why it changed

Co-Authored-By: Alfred · Claude · Sonnet 4.6
EOF
)"
```

Adjust `Co-Authored-By` to the actual agent and model:
- Alfred-Anthropic: `Alfred · Claude · Sonnet 4.6`
- Fortuna: `Fortuna · Claude · Sonnet 4.6`
- Alfred-NIM: `Alfred · Claude · NVIDIA NIM Z-AI GLM-4.7`

---

## Step 3 — Push

```bash
git push origin main
```

If push fails (remote ahead):
```bash
git pull --rebase origin main && git push origin main
```

---

## Step 4 — Update AGENT_SYNC.md (every sync)

Append to `AGENT-SYNC/AGENT_SYNC.md`:

```markdown
## 📡 [Month Day, Year] Session Summary ([Agent])
**Session type:** [infrastructure / case-work / research / cross-repo]
- [What was completed]
- [Key decision or outcome]
- Commit: [short hash] — [message]
```

---

## Step 5 — Backup Session JSONL (if small enough)

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

## Step 6 — Session Log (local only — gitignored)

Path: `logs/{agent}/2026/05-May/session_YYYYMMDD_{anthropic|nvidia}.md`

```markdown
## YYYY-MM-DD — [session type: case-work / infrastructure / research]
- [What was accomplished]
- [Key decision or outcome]
- Commit: [short hash] — [message]
```

Session logs are **never committed** in this repo (privacy). Local only.

---

## Step 7 — Final Push

```bash
git add AGENT-SYNC/
git commit -m "Update agent sync [date]"
git push origin main
```

---

## What NOT to do

- Never commit `sessions/`, `logs/`, or any case working directories
- Never write names, case numbers, or allegations in commit messages or AGENT_SYNC
- Don't skip AGENT_SYNC — it's how Alfred and Fortuna stay aligned between sessions
