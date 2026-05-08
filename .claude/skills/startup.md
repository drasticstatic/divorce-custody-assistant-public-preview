---
name: startup
description: >
  Use at the start of any Alfred or Fortuna session in the divorce-custody-assistant repo to
  choose the session backend and verify operational readiness. TRIGGER when: "startup",
  "start session", "good morning", "let's get started", "new session", "begin work",
  "morning", "start work", "initialize", "check proxy", "which backend", "session start",
  or any phrase indicating a new work session is beginning. Do NOT use for: mid-session
  model switches (use /model directly), mid-session task questions, or when Fortuna is
  already running a live case session.
---

# Startup — Divorce & Custody Assistant

Choose your session backend. Two modes — same Alfred identity, different engine.

## Session Modes

| Mode | Model | Use for |
|------|-------|---------|
| **Alfred-Anthropic** | Sonnet 4.6 / Opus 4.7 | Case strategy, document review, negotiation prep — anything affecting real decisions |
| **Alfred-NIM** | NVIDIA GLM-4.7 (free) | Exploratory questions, research, drafts, git/infra tasks |
| **Fortuna** | Always Anthropic | Case-specific deep work — never NIM for legal decisions |

**Hard rule:** NIM is never used for live legal decisions, document edits shared with counsel, or anything that directly affects the case.

---

## Step 1 — Check Proxy Status

```bash
curl -s http://localhost:8082/v1/models
```

**401 "Missing API key"** → Proxy UP ✅
**Connection refused** → Proxy DOWN — start it:

```bash
cd ~/code-forked/free-claude-code && nohup uv run free-claude-code > /tmp/fcc.log 2>&1 &
```

Wait ~4 seconds, re-check.

---

## Step 2 — Verify gwsdc Auth

```bash
gwsdc drive files list --params '{"pageSize": 1}'
```

If auth fails: `gwsdc auth login` — use cwilson.cswproductions@gmail.com (divorce-custody account).

---

## Step 3 — Read Session Context (in order)

1. `HANDOFF.md` — NIM pickup brief and case status snapshot
2. `AGENT-SYNC/AGENT_SYNC.md` — current system state
3. `PENDING-TASKS.md` — prioritized open tasks
4. `AGENT-SYNC/created-by-alfred/ALFRED_CONTEXT.md` — Alfred's infrastructure context for this repo
5. `AGENT-SYNC/created-by-fortuna/FORTUNA_CONTEXT.md` — full case context (Fortuna sessions)

---

## Step 4 — Choose Backend

### Alfred-Anthropic (default)
Proceed normally — `claude` in `~/code/divorce-custody-assistant/`.

### Alfred-NIM / Free Models

```bash
ANTHROPIC_BASE_URL=http://localhost:8082 ANTHROPIC_API_KEY=freecc claude
# Auth conflict warning appears — harmless, ignore
# /model → anthropic/nvidia_nim/z-ai/glm4.7
```

**NIM limits in this repo:**
- Text only — proxy rejects image blocks (error 400; restart session if jammed)
- "peer closed connection" / "Provider API request failed" — tell agent to continue; self-resolves
- Smaller context window — read large files in sections; use `HANDOFF.md` not full session log

---

## Quick Reference

```bash
# PNA document (Google Docs)
gwsdc docs documents get --params '{"documentId": "1bfxnTWKW3d6mM0v7KMHB_tqKbGDiYfxAt5OcXssg6Sw"}'

# Sayler emails
gwsdc gmail users messages list --params '{"userId": "me", "q": "from:rsayler@cmlaw1.com"}'

# Proxy status
curl -s http://localhost:8082/v1/models   # 401 = up | refused = down
```

---

*Reference: `specs/workflow.md` — agent roles, session modes, privacy rules, Fortuna operational workflow (§F0–F8).*
