---
name: exhibit4-refresh
description: >
  Regenerate Exhibit 4 (the vocational-compliance activity log) from live public
  GitHub commit history, verify it before it touches git, and stage the result.
  Use when: "refresh exhibit 4", "regenerate exhibit 4", "update the vocational log",
  or as a routine step of /session-sync. Do NOT use to edit exhibit-4 content by
  hand — the files are generated output; edit `build_vocational_log.py` instead if
  the format itself needs to change.
---

# Skill: /exhibit4-refresh — Exhibit 4 Auto-Refresh

Keeps `vocational-compliance/exhibit-4*.md` and `exhibit-4.html` honest and current by
re-running the generator against live public commit history, then verifying the output
before it's ever staged. See `specs/exhibit4-auto-refresh.spec.md` for the full design
and why this exists.

This same routine is what `.githooks/pre-commit` runs automatically once per UTC day —
this skill exists so an agent can also trigger it explicitly, or re-run it mid-session
after shipping something in another repo that should show up in Exhibit 4.

## Step 1 — Regenerate

```bash
python3 vocational-compliance/build_vocational_log.py --since 2026-01-01
```

`--until` defaults to today (UTC) — don't pass it explicitly. This overwrites
`exhibit-4-log.md`, every `exhibit-4-log-YYYY-MM.md`, and `exhibit-4.html` in place.

If this fails (network, `gh auth` expired, GitHub API outage): **stop here, warn, do
not proceed** — leave whatever Exhibit 4 content already exists untouched rather than
half-overwriting it.

## Step 2 — Privacy verification (must pass before anything is staged)

```bash
cd vocational-compliance
grep -Eo '\b[0-9]{2,}-[A-Za-z]{2,}-[0-9]{3,}\b|\bdocket[- ]?(no|number|#)\s*[:#]?\s*[0-9]+\b' exhibit-4*.md exhibit-4.html | wc -l   # real docket/case-no patterns — must be 0
grep -c '5328' exhibit-4*.md exhibit-4.html | grep -v ':0$'                                                                          # statute ref — must show nothing
grep -Eo '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+' exhibit-4*.md exhibit-4.html | grep -v 'noreply@anthropic.com'                           # non-Anthropic emails — must show nothing
cd ..
```

- "docket" appearing alone in `overview.md`'s sanitizer-methodology prose is a known
  false positive (it's the doc describing what gets stripped) — not a failure.
- A `5328` hit is a false positive when it's inside a **commit message quoted
  verbatim from an already-public repo**, describing a page that itself already
  publicly discusses the statute (e.g. `custody-factors.html`) — confirmed 2026-09-04
  with the "Add public custody-factors companion (scrubbed §5328 statute frame)"
  commit message. Nothing new is disclosed; Exhibit 4 only ever quotes commit
  messages that are already live on GitHub. It would only be a real failure if the
  surrounding text referenced actual case-specific docket/hearing content, which the
  privacy-first commit-message rule (see `session-sync.md`) prevents from existing in
  the first place.
- `wilson` is fine only as the maintainer's public name or a `wilson-lawn-ai-assist`
  repo URL — if it shows up any other way, stop and ask Christopher before proceeding.

**If any real check fails: STOP. Do not stage, do not commit, do not push.** Report
exactly what matched and where, and wait for Christopher before touching it further.
This is the one place where blocking is correct — the honesty-contract tradeoff (only
real, verifiable public commits) only holds if nothing sensitive slips in first.

## Step 3 — Stage

```bash
git add vocational-compliance/exhibit-4-log.md vocational-compliance/exhibit-4-log-*.md vocational-compliance/exhibit-4.html
```

Do not commit here — leave that to whichever routine called this skill
(`/session-sync`, or the calling agent's own commit step) so the regen rides along
with the rest of that session's work instead of creating a noisy standalone commit.

## Step 4 — Report

State plainly what changed: new commit count in range, whether any new week/month rows
appeared, and confirm Step 2 passed clean. If nothing changed since the last regen
(no new public commits landed), say so — don't manufacture a diff.
