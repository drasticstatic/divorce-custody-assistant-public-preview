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

What gets read from each included repo: ONLY commit dates
(`git log --pretty=format:%ad --date=short`). Never a commit message, diff,
author email, or branch name. That is a deliberate ceiling, not an oversight —
naming the repo was an explicit, deliberate choice; reading its actual commit
content to summarize was not, and would require the same kind of scrub
judgment call this project has repeatedly chosen to avoid by architecture
instead of by discipline (see form-433f public/private split in tax-assistant
for the same pattern).

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


def _is_git_repo(path: str) -> bool:
    return os.path.isdir(os.path.join(path, ".git"))


def commit_dates(repo_path: str, since: str, until: str) -> list[datetime]:
    """Return only commit DATES for repo_path in [since, until]. Never reads
    messages, authors, diffs, or branch names — count + date only, by design."""
    if not _is_git_repo(repo_path):
        return []
    result = subprocess.run(
        ["git", "-C", repo_path, "log",
         f"--since={since}", f"--until={until} 23:59:59",
         "--date=short", "--pretty=format:%ad"],
        capture_output=True, text=True, check=False,
    )
    if result.returncode != 0 or not result.stdout.strip():
        return []
    out = []
    for line in result.stdout.strip().splitlines():
        try:
            out.append(datetime.strptime(line.strip(), "%Y-%m-%d"))
        except ValueError:
            continue
    return out


def get_privatewitness_by_week(since: str, until: str) -> dict[datetime, list[tuple[str, int]]]:
    """Return {week_start_monday: [(display_name, commit_count), ...]} for every
    repo with status == 'included' in the public registry, whose local path is
    known. Silently returns {} if either config file is missing — this feature
    is opt-in local-machine state, not a hard requirement for the generator."""
    registry = load_registry()
    paths, _ = load_local_paths()
    result: dict[datetime, dict[str, int]] = {}
    for repo_id, meta in registry.items():
        if meta.get("status") != "included":
            continue
        path = paths.get(repo_id)
        if not path or not os.path.isdir(path):
            print(f"  [privatewitness] '{repo_id}' is included but has no valid "
                  f"local path — skipping", file=sys.stderr)
            continue
        display = meta.get("display_name", repo_id)
        for dt in commit_dates(path, since, until):
            wk = week_key(dt)
            result.setdefault(wk, {})
            result[wk][display] = result[wk].get(display, 0) + 1
    return {wk: sorted(counts.items()) for wk, counts in result.items()}


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
    if status not in ("include", "exclude"):
        print("status must be 'include' or 'exclude'", file=sys.stderr)
        sys.exit(2)
    status = "included" if status == "include" else "excluded"
    slug = re.sub(r"[^a-z0-9_-]", "-", repo_id.lower())

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

    local_data = _load_json(LOCAL_PATHS_PATH)
    local_data.setdefault("paths", {})
    local_data.setdefault("scan_roots", [])
    local_data["paths"][slug] = os.path.abspath(os.path.expanduser(path))
    _save_json(LOCAL_PATHS_PATH, local_data)

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
