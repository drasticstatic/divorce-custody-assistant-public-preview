---
name: create-skill
description: >
  Use when Christopher wants to design, draft, or build a new Claude Code skill for the
  divorce-custody-assistant repo. TRIGGER when: "create skill", "build skill for",
  "make a skill", "new skill for [task]", "draft a skill". Do NOT use for: general task
  execution, explaining how skills work conceptually, or executing a skill that already
  exists. Never include case-identifying information in skill files — structure only.
---

# Skill: /create-skill — Divorce & Custody Assistant

Design a new Claude Code skill for this repo. Produce a draft ready for review.

## Privacy Rule (Before Writing Any Skill)

Skills in `.claude/skills/` are tracked in git. **Never include in any skill file:**
- Party names, case numbers, or specific allegations
- Financial figures, account numbers, or asset values
- Identifying details of any kind
- Content from `child-support/`, `custody/`, `divorce/`, or runtime case documents
- `.env`, credentials, gwsdc tokens, or Google Doc IDs

Skills describe **workflow structure only** — not case content.

---

## The 7 Rules for Effective Skills

1. **Debug with description echo:** Ask "When would you use the [skill-name] skill?" — Claude quotes the description back. Reveals what's vague.
2. **Negative triggers matter more than positive:** The "Do NOT use for..." line prevents skill hijacking. Write it first.
3. **Skills stack with CLAUDE.md and memory:** Skill = process. CLAUDE.md = context and rules. Don't repeat CLAUDE.md rules inside the skill.
4. **Build from what already worked:** Best skills are reverse-engineered from prompts that worked well in past sessions.
5. **Description is everything:** Too vague → skill never fires. Too broad → hijacks conversations. Test both.
6. **Laziness workaround:** If Claude cuts corners, add "Take your time. Quality over speed." to the invocation, not the skill file.
7. **Skills are portable:** The format is an open standard. Build once, works across sessions.

---

## Skill File Format

```markdown
---
name: skill-name
description: >
  One or two sentences. TRIGGER when: [specific conditions].
  Do NOT use for: [anti-triggers — be specific].
---

# Skill: /skill-name

[Full instructions.]

## Before Starting
[What to read/check]

## Steps
[Numbered process]

## Output Format
[What the result looks like]

## After Completing
[Cleanup, commits, follow-on actions]

## Quick Commands
[Exact bash commands — use [PLACEHOLDER] for anything variable]
```

---

## How to Create a Skill

1. Describe what you want the skill to do
2. Draft following the format above — start with "Do NOT use for"
3. Test: ask "When would you use the [skill-name] skill?"
4. Save to `.claude/skills/skill-name.md`
5. Add to the skills table below

---

## Skills in This Repo

| Skill | Trigger | Purpose |
|-------|---------|---------|
| `/startup` | "startup", "start session", "good morning" | Choose session backend, verify gwsdc auth, read session context |
| `/session-sync` | "session sync", "commit and sync", "end of work" | Stage, commit, push, update AGENT_SYNC.md, log session |
| `/create-skill` | "create skill", "build skill for", "new skill" | Design a new skill for this repo |

---

## Generation Workflow

1. **Write "Do NOT use for" first** — prevents skill hijacking
2. **Write positive triggers** — TRIGGER when: keywords, task types, phrasings (include synonyms)
3. **Write the body** — explain WHY, not just WHAT; concrete examples beat abstract placeholders
4. **Self-review:** Can I cut 20% without losing value? Are there rigid rules that should be reasoning instead?
5. **Test the trigger:** Ask "When would you use the [skill-name] skill?"

---

*Reference: `specs/workflow.md` for session conventions. Skills are gitignored from public preview per `gitexporter.config.json`.*
