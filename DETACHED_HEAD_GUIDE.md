# Detached HEAD Guide

A reference for this repo's dual-checkout git setup: what detached HEAD means, why this repo runs
that way on purpose, and how to work safely in either checkout.

## The setup

This repository has two local checkouts pointing at related commits:

- **The primary checkout** (this one, at `~/code/divorce-custody-assistant`) — kept in **detached
  HEAD**. `HEAD` points directly at a commit rather than a branch name.
- **An Augment Intent worktree**, attached to `main`.

## Detached HEAD in plain English

Git normally keeps `HEAD` attached to a branch name such as `main`. In a **detached HEAD** state,
`HEAD` points directly to a commit instead. The checkout is fully usable — you can read, edit, and
commit normally — but new commits made there are easier to lose track of unless they get anchored to
a branch name or pushed somewhere.

## Why this repo runs this way

This is not an oversight to fix. The detached checkout is where real work has actually been landing:
commits made here (both plain edits and Claude Code CLI sessions) push straight through to
`origin/main`, verified directly against git history — `git log` on this checkout and `origin/main`
land on the same commit. The Augment Intent worktree, by contrast, has drifted stale relative to it at
various points; it is a secondary, less-current track, not the "durable home" a project's `main`
branch would normally imply.

The practical friction this setup solves: commits work fine from an editor even while a checkout is
detached, but many git UIs (VS Code's push flow included) don't reliably push a detached HEAD to a
named remote branch — pushes from a detached checkout sometimes fail or hang. When that happens, the
fix is a direct, explicit push:

```bash
git push origin HEAD:main
```

That's the one command this whole setup exists to explain. Everything else below is how to work
safely around it.

## Working safely in a detached checkout

Detached HEAD is fine, without any special care, for:

- reading files and searching the codebase
- comparing versions and inspecting changes
- small, immediately-committed edits
- using the checkout as a day-to-day working environment, as long as commits get pushed

Take a moment before:

- starting a long editing session you might want to pause mid-way — an uncommitted detached-HEAD
  session is easier to lose track of than one on a named branch
- assuming a `git checkout main` or similar branch switch is safe — `main` may already be checked
  out in the other worktree, and a branch can't be checked out in two worktrees simultaneously

If you want the extra safety of a named branch for a substantial piece of work, create one:

```bash
git switch -c my-temp-branch
```

This keeps commit history visible and makes it easier to move or merge the work later — but it's not
required for routine work; committing directly in detached HEAD and pushing with `git push origin
HEAD:main` is the normal, expected workflow here.

## Quick reference

| Command | Tells you |
|---|---|
| `git status --short --branch` | Whether this checkout is attached to a branch or detached |
| `git worktree list --porcelain` | Every worktree for this repo and which commit/branch each is on |
| `git log --oneline -5` vs `git log --oneline origin/main -5` | Whether local and remote have diverged |
| `git push origin HEAD:main` | Explicit push from a detached checkout to the named remote branch |

## For agents landing in this checkout

Finding `HEAD (no branch)` here is expected state, not a problem to fix. Don't switch to `main` (it's
checked out elsewhere and can't be checked out here simultaneously). Commit normally; if a push fails
or the user reports VS Code couldn't push, run `git push origin HEAD:main` directly.

---

*A quick-access redirect stub for this file lives in
[`my-template/workflow-templates/DETACHED_HEAD_GUIDE.md`](https://github.com/drasticstatic/my-template/blob/main/workflow-templates/DETACHED_HEAD_GUIDE.md).*
