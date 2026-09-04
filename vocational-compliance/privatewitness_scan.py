#!/usr/bin/env python3
"""
privatewitness_scan.py — Exhibit 4 "Private Work" attribution lane

Purpose
-------
Exhibit 4 (build_vocational_log.py) can only ever see PUBLIC GitHub commit
history. Some real work — e.g. Mystarch, an Augment Intent workspace that is
private-forever by its own design with no public mirror — never appears there,
even though it's real, ongoing work. This module lets a private repo be named
and counted (never quoted, never linked, never diffed) in a visually separate
section of Exhibit 4, so the exhibit can attest to that work happening without
claiming the same "independently verifiable" status public rows carry.

Two-file model (mirrors the CSV split used elsewhere in this repo family):
  - vocational-compliance/privatewitness-registry.json   (PUBLIC, tracked)
        Which repos are in scope, their display name, and include/exclude
        status. No filesystem paths — this file is safe to publish as-is and
        is itself part of the honesty contract: anyone can see exactly which
        repos are counted and which were excluded, and why.
  - vocational-compliance/privatewitness-local/paths.json  (LOCAL ONLY, gitignored)
        Maps each registry repo id to its real local filesystem path, plus
        `scan_roots` — directories to sweep for repos not yet classified.
        Never committed anywhere, public or private.

What gets read from each included repo: commit SHA + date + one-line subject
(`git log --pretty=format:%h/%ad/%s`) — same three fields a public row's
Category/Description/Proof columns are built from. Christopher's explicit call
(2026-09-04): render Private Work rows in the same table format as public rows,
which requires reading real subject lines, not just counting them. The subject
line is run through build_vocational_log.py's own `sanitize_message()` +
`classify()` — the SAME functions and rubric applied to every public row, not a
second, looser pipeline — so private and public rows get identical redaction
treatment. Full diffs, file contents, and branch names are still never read.
The one thing a Private Work row can never carry is a working github.com link
— there isn't one — so the "Proof" column shows the local commit SHA instead:
real, git-verifiable, but not independently checkable by a reader the way a
public row's URL is.

New-repo default: excluded. A repo found under `scan_roots` that isn't already
in the registry is reported, never auto-added — mirrors the sync-public.yml
allowlist tripwire (new root paths fail CI until classified) applied here to
private-repo attribution instead of public-export paths.

CLI
---
    python3 privatewitness_scan.py --scan
        Sweep scan_roots for git repos not yet in the registry; report them.

    python3 privatewitness_scan.py --classify <id> <local-path> <include|exclude> "<note>"
        Register a repo: writes the id/local path into paths.json (local) and
        upserts display_name/status/note into the public registry.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REGISTRY_PATH = os.path.join(BASE_DIR, "privatewitness-registry.json")
LOCAL_PATHS_PATH = os.path.join(BASE_DIR, "privatewitness-local", "paths.json")


def week_key(dt: datetime) -> datetime:
    return (dt - timedelta(days=dt.weekday())).replace(
        hour=0, minute=0, second=0, microsecond=0)


def _load_json(path: str) -> dict:
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _save_json(path: str, data: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)
        fh.write("\n")


def load_registry() -> dict:
    return _load_json(REGISTRY_PATH).get("repos", {})


def load_local_paths() -> tuple[dict, list[str]]:
    data = _load_json(LOCAL_PATHS_PATH)
    return data.get("paths", {}), data.get("scan_roots", [])


def load_suppress_terms() -> list[str]:
    """Terms (repo names/slugs the account owner has deliberately kept
    unnamed) to scrub from EVERY row's description — public rows included,
    since a private commit's message can surface in the public mirror if that
    commit also touched a public-allowlisted path in the same commit. Local
    file only; returns [] if it doesn't exist, same fail-open posture as the
    rest of this module."""
    return _load_json(LOCAL_PATHS_PATH).get("suppress_terms", [])


def _is_git_repo(path: str) -> bool:
    return os.path.isdir(os.path.join(path, ".git"))


_FIELD_SEP = "\x1f"  # unit separator — won't collide with real commit text


def repo_commits(repo_path: str, since: str, until: str) -> list[dict]:
    """Return [{sha, date, message}, ...] for repo_path in [since, until].
    `message` is the raw one-line subject — sanitize_message()/classify() in
    build_vocational_log.py are applied to it by the caller, the SAME functions
    and rubric used for public rows, so private and public rows share one
    redaction/categorization pipeline rather than a second, easier-to-drift one."""
    if not _is_git_repo(repo_path):
        return []
    result = subprocess.run(
        ["git", "-C", repo_path, "log",
         f"--since={since}", f"--until={until} 23:59:59",
         "--date=short", f"--pretty=format:%h{_FIELD_SEP}%ad{_FIELD_SEP}%s"],
        capture_output=True, text=True, check=False,
    )
    if result.returncode != 0 or not result.stdout.strip():
        return []
    out = []
    for line in result.stdout.strip().splitlines():
        parts = line.split(_FIELD_SEP, 2)
        if len(parts) != 3:
            continue
        sha, date_s, subject = parts
        try:
            dt = datetime.strptime(date_s.strip(), "%Y-%m-%d")
        except ValueError:
            continue
        out.append({"sha": sha, "date": dt, "message": subject})
    return out


def get_privatewitness_commits_by_week(since: str, until: str) -> dict[datetime, list[dict]]:
    """Return {week_start_monday: [{repo, sha, date, message}, ...]} for every
    repo with status == 'included' in the public registry, whose local path is
    known. Silently returns {} if either config file is missing — this feature
    is opt-in local-machine state, not a hard requirement for the generator."""
    registry = load_registry()
    paths, _ = load_local_paths()
    result: dict[datetime, list[dict]] = {}
    for repo_id, meta in registry.items():
        if meta.get("status") != "included":
            continue
        path = paths.get(repo_id)
        if not path or not os.path.isdir(path):
            print(f"  [privatewitness] '{repo_id}' is included but has no valid "
                  f"local path — skipping", file=sys.stderr)
            continue
        display = meta.get("display_name", repo_id)
        for c in repo_commits(path, since, until):
            wk = week_key(c["date"])
            result.setdefault(wk, []).append({
                "repo": display, "sha": c["sha"],
                "date": c["date"], "message": c["message"],
            })
    for wk in result:
        result[wk].sort(key=lambda r: r["date"])
    return result


def scan(quiet: bool = False) -> list[str]:
    """Sweep scan_roots for git repos not already known; return their paths."""
    _, roots = load_local_paths()
    known_paths = {os.path.normpath(p) for p in load_local_paths()[0].values()}
    found_unknown = []
    for root in roots:
        root = os.path.expanduser(root)
        if not os.path.isdir(root):
            continue
        for entry in sorted(os.listdir(root)):
            candidate = os.path.join(root, entry)
            if not os.path.isdir(candidate):
                continue
            if _is_git_repo(candidate) and os.path.normpath(candidate) not in known_paths:
                found_unknown.append(candidate)
    if not quiet:
        if found_unknown:
            print("Unclassified private repos found (not yet in privatewitness "
                  "registry — excluded by default until reviewed):")
            for p in found_unknown:
                print(f"  - {p}")
            print("\nClassify with:\n"
                  "  python3 privatewitness_scan.py --classify <id> <path> include|exclude \"<note>\"")
        else:
            print("No unclassified repos found under scan_roots.")
    return found_unknown


def classify(repo_id: str, path: str, status: str, note: str) -> None:
    """status: 'include' or 'exclude' writes a normal, named entry to the
    PUBLIC registry (this is the honesty-contract-friendly path — anyone can
    see what was reviewed and why). 'exclude-silent' is different on purpose:
    it records the local path (so --scan stops re-flagging it) but writes
    NOTHING to the public registry — not even an excluded entry naming it.
    Use this for a repo whose very NAME/existence Christopher doesn't want
    surfaced anywhere public — an 'excluded, here's why' audit entry would
    itself defeat the point by naming the thing being hidden."""
    if status not in ("include", "exclude", "exclude-silent"):
        print("status must be 'include', 'exclude', or 'exclude-silent'", file=sys.stderr)
        sys.exit(2)
    slug = re.sub(r"[^a-z0-9_-]", "-", repo_id.lower())

    local_data = _load_json(LOCAL_PATHS_PATH)
    local_data.setdefault("paths", {})
    local_data.setdefault("scan_roots", [])
    local_data["paths"][slug] = os.path.abspath(os.path.expanduser(path))
    _save_json(LOCAL_PATHS_PATH, local_data)

    if status == "exclude-silent":
        local_data.setdefault("suppress_terms", [])
        basename = os.path.basename(os.path.normpath(path))
        for term in {slug, basename}:
            if term and term not in local_data["suppress_terms"]:
                local_data["suppress_terms"].append(term)
        _save_json(LOCAL_PATHS_PATH, local_data)
        print(f"Recorded '{slug}' locally as silently excluded — --scan will no "
              f"longer flag it, and it will NEVER appear in the public registry "
              f"or Exhibit 4, not even as a named exclusion. Its name/slug were "
              f"also added to suppress_terms, so sanitize_message() scrubs it "
              f"even if it surfaces inside a DIFFERENT repo's real commit message.")
        return

    status = "included" if status == "include" else "excluded"
    reg_data = _load_json(REGISTRY_PATH)
    reg_data.setdefault("repos", {})
    display_name = os.path.basename(os.path.normpath(path))
    reg_data["repos"][slug] = {
        "display_name": reg_data["repos"].get(slug, {}).get("display_name", display_name),
        "status": status,
        "added": datetime.now().date().isoformat(),
        "note": note,
    }
    _save_json(REGISTRY_PATH, reg_data)

    print(f"Classified '{slug}' as {status}. Public registry updated "
          f"(vocational-compliance/privatewitness-registry.json) — commit that. "
          f"Local path recorded (gitignored, never committed).")


def main(argv: list[str]) -> int:
    if not argv or argv[0] == "--scan":
        scan()
        return 0
    if argv[0] == "--classify":
        if len(argv) != 5:
            print("Usage: --classify <id> <local-path> <include|exclude> \"<note>\"",
                  file=sys.stderr)
            return 2
        classify(argv[1], argv[2], argv[3], argv[4])
        return 0
    print(__doc__)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
