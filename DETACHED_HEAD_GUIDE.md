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