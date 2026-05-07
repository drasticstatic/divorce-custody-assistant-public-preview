# Workflow — Divorce & Custody Assistant
### Session Coordination & Agent Handoff Protocol

---

## Overview

This repo is worked on by multiple agents depending on the task at hand. This document defines the workflow for coordinating sessions, handoffs, and version control across the ecosystem.

---

## Agent Roles

| Agent | Platform | Domain | When to Use |
|-------|----------|--------|-------------|
| **Fortuna** | Claude Code CLI (Sonnet/Opus) | Session intelligence, context awareness, behavioral coaching, emotional containment support | Primary for this repo — case strategy, document review, negotiation prep |
| **Alfred** | Claude Code CLI (Anthropic or NIM) | System coordinator, free-model sandbox, cross-repo housekeeping | Quick research, git operations, file organization, exploratory questions |
| **Auggie** | Augment CLI | Code builds, infrastructure, automation | Google Workspace tooling, document intake pipelines, MCP servers |
| **Kavanah** | Augment Intent | Spec-driven orchestration, cross-repo coordination | Multi-repo planning, documentation builds, agent handoffs |

---

## Session Modes

### Fortuna-Anthropic (Default)
- **Model:** Sonnet 4.6 / Opus 4.7
- **Use for:** Case strategy, document review, negotiation prep, emotional support, any task where quality cannot be compromised
- **Command:** `claude` (default)

### Alfred-NIM (Free Tier)
- **Model:** NVIDIA NIM (GLM-4.7 or similar)
- **Use for:** Exploratory questions, research, drafts, tasks that would otherwise eat Claude quota unnecessarily
- **Command:** `ANTHROPIC_BASE_URL=http://localhost:8082 ANTHROPIC_API_KEY=freecc claude` → `/model` → NIM
- **Error handling:** If you see "peer closed connection without sending complete message body" or "Provider API request failed", simply ask the agent to continue — these are transient NIM errors

**Rule:** Fortuna sessions are always Alfred-Anthropic. NIM is never used for live legal decisions or document edits that will be shared with opposing counsel.

---

## Session Log Naming

- **Fortuna-Anthropic sessions:** `logs/fortuna/YYYY/MM-Mon/session_YYYYMMDD.md`
- **Alfred-NIM sessions:** `logs/alfred/YYYY/MM-Mon/session_YYYYMMDD_nvidia.md`
- **Alfred-Anthropic sessions:** `logs/alfred/YYYY/MM-Mon/session_YYYYMMDD_anthropic.md`

Use `_anthropic` not `_claude` — avoids search collisions with `CLAUDE.md` files and is consistent with provider naming (`_nvidia` = NVIDIA, `_anthropic` = Anthropic).

---

## Handoff Protocol

### When to Hand Off

1. **Task domain changes** — e.g., from case strategy (Fortuna) to infrastructure setup (Auggie)
2. **Agent context is getting bloated** — hand off to a fresh session with a focused prompt
3. **Cross-repo coordination needed** — Kavanah for multi-repo planning
4. **Free-model sandbox appropriate** — Alfred-NIM for exploratory work

### Handoff Files

- **Outbound:** `AGENT-SYNC/created-by-{agent}/PROMPT_YYYYMMDD.md`
- **Inbound:** Read `AGENT-SYNC/created-by-{other-agent}/PROMPT_YYYYMMDD.md` at session start

**File naming convention:** Files live in the **creator's** directory, named after the **recipient**:
- Fortuna → Kavanah: `AGENT-SYNC/created-by-fortuna/prompts/YYYY/MM-Mon/KAVANAH_PROMPT_YYYYMMDD.md`
- Alfred → Fortuna: `AGENT-SYNC/created-by-alfred/prompts/YYYY/MM-Mon/FORTUNA_PROMPT_YYYYMMDD.md`

Never add content to another agent's prompt file — create your own.

---

## Version Control Workflow

### Branch Strategy

- **main** — stable, always deployable
- **feature/*** — work-in-progress branches for specific features
- **detached HEAD** — temporary state during worktree operations; always resolve before session end

### Commit Discipline

- Commit after every meaningful change — do not leave uncommitted work at session end
- Commit messages should be generic (no case numbers, party names, or identifying details)
- After every `git commit`, immediately `git push origin main` (or the appropriate branch)

### Git vs. Google Docs Version History

| What you're tracing | Best source |
|-------------------|-------------|
| What the PNA said at any point in time | Google Docs version history |
| Who commented / suggested what | Google Docs version history |
| Agent scripts, case infrastructure, CLAUDE.md changes | Git history |
| Case strategy notes, specs | Git history |

Google Docs version history is timestamped to the minute, attributed by Google account, and shows exactly what changed in the document — exactly what you need if there's ever a dispute about what was in a draft. Git is the right source for everything in this repo. They complement each other; neither replaces the other.

---

## Privacy & Security

### Never Commit

- Court documents, evaluations, or legal filings (these load from iCloud Drive aliases at runtime)
- Case numbers, party names, or specific allegations in commit messages
- Identifying details (names, addresses, financials) in any committed file
- `.env` files, credentials, API keys, or any secret material

### Gitignore Rules

- `sessions/` — local-only session transcripts
- `child-support/`, `custody/`, `divorce/` — case working directories
- `*alias` — iCloud Drive aliases
- `.gws/`, `gws-credentials*` — Google Workspace CLI credentials

### Cross-Repo Privacy Firewall

- No divorce/custody data in trading-assistant or web3 repos — ever
- No trading strategy data or web3 code in this repo — ever
- Agents have awareness of Christopher's full project ecosystem but data stays strictly isolated

---

## Quick Reference

### Common Commands

```bash
# Start a Fortuna session (default)
claude

# Start an Alfred-NIM session
ANTHROPIC_BASE_URL=http://localhost:8082 ANTHROPIC_API_KEY=freecc claude

# Check git status
git status

# Commit and push
git add .
git commit -m "descriptive message"
git push origin main

# Create a handoff file
mkdir -p AGENT-SYNC/created-by-fortuna/prompts/YYYY/MM-Mon
# Then write the prompt file
```

### File Locations

- **Session logs:** `logs/{agent}/YYYY/MM-Mon/session_YYYYMMDD.md`
- **Handoffs:** `AGENT-SYNC/created-by-{agent}/prompts/YYYY/MM-Mon/{RECIPIENT}_PROMPT_YYYYMMDD.md`
- **Case documents:** Referenced via `cases-w-Erica_alias.md` → iCloud Drive
- **Google Docs:** Accessed via `gwsdc` alias (Google Workspace CLI)

---

## Session Start Checklist

1. Read `AGENT-SYNC/POINTER.md` for cross-repo coordination status
2. Read `specs/divorce-custody-system.spec.md` for system architecture
3. Read `STARTUP_INSTRUCTIONS_by-Kavanah_Augment-Intent.md` for full project context
4. Check `PENDING-TASKS.md` for open tasks
5. Verify git status — resolve any detached HEAD or uncommitted changes
6. Create session log in appropriate `logs/` directory

---

## Session End Checklist

1. Commit all meaningful changes
2. Push to origin
3. Create handoff file if another agent needs to continue the work
4. Update `PENDING-TASKS.md` with any new tasks or completed items
5. Save session log to `logs/` directory
6. Note any NIM errors encountered for future reference

---

*Last updated: May 7, 2026*
