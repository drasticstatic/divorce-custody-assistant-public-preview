#!/usr/bin/env python3
"""
check_commit_messages.py — pre-push guard against a repeat of the 2026-09-04 leak

What happened once already: a commit describing privateWitness work named a
repo Christopher had asked to keep unnamed, directly in the commit message
body. The commit touched a publicly-synced path, so the full message went
live on the public mirror. build_vocational_log.py's sanitize_message() now
scrubs that term from EXHIBIT CONTENT — but nothing was checking the actual
git commit messages themselves before they left the machine. This closes that
gap, per the finding in AGENT-SYNC/created-by-mystarch/
2026-09-04_leaked-commit-message-scrub-RESOLVED.md.

This deliberately does NOT run in GitHub Actions / sync-public.yml: the most
sensitive terms live only in privatewitness-local/paths.json's
`suppress_terms`, which is gitignored and never present in a CI checkout —
checking it there would mean either committing the denylist itself (which
partly defeats "exclude-silent"'s purpose for a name-sensitive entry) or
missing exactly the cases that matter most. So this runs locally, as a
`/session-sync` step, on whichever commits are about to be pushed.

Usage:
    python3 check_commit_messages.py [<since-ref>]
        <since-ref> defaults to 'origin/main' — checks every commit in
        <since-ref>..HEAD. Exits 1 and prints the offending commit(s) if any
        commit message contains a suppressed term or an excluded repo's
        display name; exits 0 otherwise.
"""

from __future__ import annotations

import subprocess
import sys

import privatewitness_scan as pw


def terms_to_check() -> list[str]:
    terms = list(pw.load_suppress_terms())
    for repo_id, meta in pw.load_registry().items():
        if meta.get("status") == "excluded":
            terms.append(meta.get("display_name", repo_id))
    return [t for t in terms if t]


def offending_commits(since_ref: str, terms: list[str]) -> list[tuple[str, str, str]]:
    """Return [(sha, term, message), ...] for every commit in since_ref..HEAD
    whose message contains one of `terms` (case-insensitive)."""
    result = subprocess.run(
        ["git", "log", f"{since_ref}..HEAD", "--format=%H%x1f%B%x1e"],
        capture_output=True, text=True, check=False,
    )
    if result.returncode != 0:
        print(f"  [check_commit_messages] couldn't diff against {since_ref} "
              f"({result.stderr.strip()}) — skipping, nothing to compare yet",
              file=sys.stderr)
        return []
    hits = []
    for record in result.stdout.split("\x1e"):
        if not record.strip():
            continue
        sha, _, message = record.partition("\x1f")
        low = message.lower()
        for term in terms:
            if term.lower() in low:
                hits.append((sha.strip()[:10], term, message.strip().splitlines()[0]))
    return hits


def main(argv: list[str]) -> int:
    since_ref = argv[0] if argv else "origin/main"
    terms = terms_to_check()
    if not terms:
        print("  [check_commit_messages] no suppressed/excluded terms configured — nothing to check")
        return 0
    hits = offending_commits(since_ref, terms)
    if not hits:
        print(f"  [check_commit_messages] clean — no commit in {since_ref}..HEAD "
              f"mentions a suppressed or excluded term")
        return 0
    print("BLOCKED — a commit about to be pushed names something that should stay "
          "unnamed:", file=sys.stderr)
    for sha, term, subject in hits:
        print(f"  {sha}  matched \"{term}\"  — {subject}", file=sys.stderr)
    print("\nFix the message (git rebase -i, reword) before pushing. Do not push "
          "past this check.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
