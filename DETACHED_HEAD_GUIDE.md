# Detached HEAD Guide

## Why this file exists

This repository currently has two local checkouts pointing at the same commit:

- the active **Intent workspace**, attached to `main...origin/main`
- an older **home-repo worktree**, currently in **detached HEAD**

That setup is intentional and safe. This guide explains what detached HEAD means, why it is not a problem by itself, and how to work safely in this repo.

## Detached HEAD in plain English

Git normally has `HEAD` attached to a branch name such as `main`.

In a **detached HEAD** state, `HEAD` points directly to a commit instead of a branch name.

That means the checkout is still usable, but new commits made there are easier to lose track of unless you attach them to a branch.

## Current verified state for this repo

- The active Intent workspace is on `main...origin/main`
- The older home-repo worktree is on the **same commit** in detached HEAD
- The Intent workspace is the primary place for durable work and commit orchestration
- The detached worktree is fine as a helper checkout for reading, comparison, and careful temporary edits

## What is safe in detached HEAD

Detached HEAD is fine for:

- reading files
- searching the codebase
- comparing versions
- inspecting changes
- trying small temporary edits
- using the checkout as a secondary reference environment

## What needs caution in detached HEAD

Be careful when you are:

- making commits you want to keep
- doing a long editing session
- forgetting which checkout owns the durable branch history

The risk is not that detached HEAD is broken. The risk is that important work can become harder to locate or preserve if it never gets anchored to a branch.

## Recommended workflow for this repo

1. Treat the **Intent workspace** as the main place for durable work
2. Do normal commit-oriented work from the checkout attached to `main`
3. Use the detached worktree as a helper environment for review, comparison, or light temporary edits
4. If real development needs to happen in the detached worktree, create a branch there first

## If you need to work from the detached checkout

Before starting meaningful work, create a temporary branch so your commits are attached to a name:

`git switch -c my-temp-branch`

That makes it easier to:

- keep commit history visible
- move or merge work later
- avoid losing track of experimental changes

## Quick check commands

When in doubt, these commands are usually enough:

- `git status --short --branch`
- `git worktree list --porcelain`

They will tell you whether a checkout is attached to a branch, whether it tracks `origin/main`, and whether another worktree is detached.

## Practical takeaway

**Detached HEAD is fine for helper work. Named branches are better for durable work.**

---

## Update — 2026-08-23: how Christopher actually uses this setup

This split isn't a leftover to eventually clean up — Christopher keeps it this way on purpose, as a
standing, hands-on git-learning environment:

- The **Intent workspace** stays the single durable home for `main` — every real commit that needs to
  survive lives there, tracked against `origin/main` like any normal repo.
- The **detached home-repo worktree** (this checkout) is kept detached *deliberately*, as a low-stakes
  sandbox for actually practicing git concepts — checking out arbitrary commits, comparing states,
  trying small experimental edits — without any risk of accidentally moving `main` or disturbing the
  Intent workspace's history. It's a "safe to poke at" mirror of the same commit, not stale-and-forgotten.
- The value isn't just technical isolation — it's pedagogical. Seeing `git status --short --branch`
  report `HEAD (no branch)` here, right next to a normal attached checkout elsewhere, is a live, concrete
  example of the branch-vs-commit distinction this guide explains in the abstract above. Any agent
  session that lands in this checkout and finds it detached should treat that as expected state, not a
  problem to fix by switching to `main` (which is already checked out elsewhere and can't be checked out
  here simultaneously anyway).
- A quick-access redirect stub for this file lives in `my-template/workflow-templates/` so other repos'
  sessions can find this explanation without duplicating it.