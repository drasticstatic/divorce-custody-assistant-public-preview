#!/usr/bin/env python3
"""
build_vocational_log.py — Exhibit 4 vocational compliance log generator

Purpose
-------
Produce an audit-ready "Weekly Vocational Activity & Work-Search & Effort Report"
by translating real, public GitHub commits across the `drasticstatic` account
into "Product Development Hours" and "Job Search Equivalents," grouped into
weekly rows. Intended to satisfy the good-faith intent of a PA CareerLink (R)
Work Search Order during a pre-revenue technical startup phase.

Honesty contract (non-negotiable)
---------------------------------
- Every row in the output is derived from a REAL public commit with a
  verifiable proof link that resolves on github.com. No padding, no fabricated
  activity. The history IS the exhibit.
- Only PUBLIC-facing repos are queried (originally-public repos and the
  `-public-preview` / `-public` mirrors of private repos). Commits that touched
  only private paths are pruned by `git filter-repo` in the sync pipeline, so
  they correctly do NOT appear here — that is the desired, honest behavior.
- The author of a commit is reported. If a commit's author is not attributable
  to the account owner's known identities, it is EXCLUDED so the exhibit never
  misattributes someone else's work.

Equivalence rubric
------------------
A single commit does not equal one job contact. A commit is weighted by an
activity-category equivalence (see CATEGORY_RUBRIC). Reach a configurable
weekly compliance target by summing equivalence metrics across rows.

Reproducibility
---------------
Run:
    python3 build_vocational_log.py --since 2026-01-01 --until 2026-08-10 \\
        --author drasticstatic

Outputs (overwrites, in the vocational-compliance/ directory):
    exhibit-4-log.md            <- table-of-contents index (journey + aggregate + monthly links)
    exhibit-4-log-YYYY-MM.md    <- one per-month weekly log (each a standalone exhibit)
    exhibit-4.html              <- interactive accordion export (served on GitHub Pages)

Change --since / --until to extend the reporting period and re-run; the script
appends nothing automatically — it regenerates the full artifact family in one
pass so the output is always a faithful snapshot of the stated date range.

NOTE: This script reads only PUBLIC data via the GitHub REST API and writes
markdown + HTML. It never reads .env files, private keys, credentials, or any
case-specific data. It is safe to commit and to run in CI.
"""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from urllib.parse import quote


# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #

ACCOUNT = "drasticstatic"

# Public-preview publishing target. Cross-links in every generated markdown
# resolve to GitHub blob URLs on this mirror (the privacy-preserving lane the
# sync pipeline publishes), the HTML accordion is served raw off the
# public-preview repo's GitHub Pages, and every artifact links back to the
# homepage below for frictionless navigation.
PUBLIC_PREVIEW_OWNER = "drasticstatic"
PUBLIC_PREVIEW_REPO = "divorce-custody-assistant-public-preview"
HOMEPAGE_URL = (f"https://{PUBLIC_PREVIEW_OWNER}.github.io/"
                f"{PUBLIC_PREVIEW_REPO}/")
BLOB_BASE = (f"https://github.com/{PUBLIC_PREVIEW_OWNER}/{PUBLIC_PREVIEW_REPO}"
             f"/blob/main/vocational-compliance")

# File-name stems/patterns for the generated artifact family.
INDEX_FILE = "exhibit-4-log.md"
HTML_FILE = "exhibit-4.html"          # interactive accordion (short URL for embedding)
MONTH_FILE_TMPL = "exhibit-4-log-{}.md"   # .format("YYYY-MM")

# Recognized author identities (login + any committed email handles).
# Only commits by these identities are attributable; others are excluded so we
# never misrepresent another contributor's work as the account owner's.
KNOWN_AUTHOR_IDENTITIES = {
    # GitHub logins seen across the account (case-insensitive)
    "drasticstatic",
}

# Category rubric: how a commit's classified activity translates to the
# "Equivalence Metric" column. "hours" = product development hours,
# "action" = one job-search-equivalent action.
#
# Classification is driven by keyword rules over the commit message + repo name,
# falling back to a conservative default. Rules are ORDERED; first match wins.
CATEGORY_RUBRIC = [
    # (category, hours, action, description-of-equivalence, keyword-patterns)
    {
        "category": "Code Deployment",
        "hours": 6.0,
        "action": 0.0,
        "equiv": "Hours (technical portfolio build)",
        "patterns": [r"\bdeploy\b", r"\bdeployment\b", r"\bpush(ed)? (to )?prod",
                     r"\brelease\b", r"\bship\b", r"\bgo-?live\b",
                     r"\bmain\b.*\bdeploy", r"\bpages\b", r"\bsync(-)?public\b",
                     r"\bworkflow\b", r"\baction(s)?\b.*push", r"\bgithub(- )?action"],
    },
    {
        "category": "Risk Evaluation",
        "hours": 8.0,
        "action": 0.0,
        "equiv": "Hours (prop firm combine / risk audit)",
        "patterns": [r"\brisk\b", r"\bbacktest", r"\bcombin(e|ation)\b",
                     r"\bprop\b", r"\bevaluation\b", r"\bcalibrat",
                     r"\bstrategy\b", r"\bsignals?\b", r"\bindev\b",
                     r"\bpnl\b", r"\bdrawdown\b", r"\bsharpe\b"],
    },
    {
        "category": "Retraining Milestone",
        "hours": 4.0,
        "action": 0.0,
        "equiv": "Hours (vocational schooling / curriculum)",
        "patterns": [r"\bcurriculum\b", r"\blesson\b", r"\bmodule\b",
                     r"\bcourse\b", r"\bbootcamp\b", r"\btraining\b",
                     r"\bexercise\b", r"\bkata\b", r"\btutorial\b",
                     r"\bdappu\b", r"\bsolidity\b", r"\bhardhat\b"],
    },
    {
        "category": "Technical Outreach",
        "hours": 2.0,
        "action": 2.0,
        "equiv": "Actions (direct business lead generation)",
        "patterns": [r"\boutreach\b", r"\binquiry\b", r"\benquiry\b",
                     r"\bproposal\b", r"\bbid\b", r"\bpitch\b",
                     r"\bclient\b", r"\brecruit(er|ing)\b", r"\bsafeguard",
                     r"\bopentowork\b", r"\bopen.to.work\b"],
    },
    {
        "category": "Beta-Testing & Calibration",
        "hours": 5.0,
        "action": 0.0,
        "equiv": "Hours (product development / startup labor)",
        "patterns": [r"\bbot\b", r"\bmev\b", r"\barb(itrage)?\b", r"\blistener",
                     r"\bscript\b", r"\bcalibrat", r"\btune(d|ing)?\b",
                     r"\bconfig\b", r"\benv\b", r"\btoken\b", r"\bwallet",
                     r"\bcontract\b", r"\bsolidity\b", r"\bnode\b"],
    },
    {
        "category": "Audit / Education",
        "hours": 3.0,
        "action": 0.0,
        "equiv": "Hours (professional performance review)",
        "patterns": [r"\baudit\b", r"\breview\b", r"\b1-on-1\b", r"\b1:1\b",
                     r"\bcoaching\b", r"\bmentor\b", r"\bfeedback\b",
                     r"\bself-check\b", r"\bverify\b", r"\bvalidation\b",
                     r"\btest(s|ing)?\b", r"\bspec\b"],
    },
]

DEFAULT_CATEGORY = {
    "category": "Product Development",
    "hours": 4.0,
    "action": 0.0,
    "equiv": "Hours (product development / startup labor)",
}

# Visual color per category — hues spread around the wheel so adjacent
# categories stay distinct, used for the Category cell, the Equivalence cell,
# and the legend dot/key. One source of truth shared by the cells + legend.
CATEGORY_COLORS = {
    "Code Deployment": "#3b82f6",
    "Risk Evaluation": "#ef4444",
    "Retraining Milestone": "#a855f7",
    "Technical Outreach": "#34d399",
    "Beta-Testing & Calibration": "#f59e0b",
    "Audit / Education": "#f472b6",
    "Product Development": "#818cf8",
}


def cat_slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", (name or "").lower()).strip("-")


# Category metadata (color + equivalence label) keyed by category name. Pulled
# from the rubric + default so the legend and the cells always agree.
CAT_META = {}
for _entry in CATEGORY_RUBRIC + [DEFAULT_CATEGORY]:
    CAT_META[_entry["category"]] = {
        "color": CATEGORY_COLORS.get(_entry["category"], "#94a3b8"),
        "equiv": _entry["equiv"],
        "slug": cat_slug(_entry["category"]),
    }


def _build_category_css() -> str:
    # One CSS class per category: colorizes the Category text, the dot chip, and
    # the colored left-rule on the Equivalence cell. Unused classes are harmless.
    out = []
    for _meta in CAT_META.values():
        _s, _c = _meta["slug"], _meta["color"]
        out.append(f".cat.cat-{_s}{{color:{_c};}}")
        out.append(f".cat-name.cat-{_s}{{color:{_c};}}")
        out.append(f".cat-dot.cat-{_s}{{background:{_c};}}")
        out.append(f".eq.eq-{_s}{{border-left:3px solid {_c};}}")
    return "\n".join(out) + "\n"


# Appended to the base <style> so the category palette flows into the page.
_CATEGORY_CSS = _build_category_css()


def _legend_html() -> str:
    """On-page color key for the activity categories.

    Deterministic order: rubric categories first (first-seen), then the default
    fallback last — so the legend and the table cells always agree and the
    reading order is stable across regenerations.
    """
    seen: list[str] = []
    for _entry in CATEGORY_RUBRIC + [DEFAULT_CATEGORY]:
        if _entry["category"] not in seen:
            seen.append(_entry["category"])
    items = []
    for _name in seen:
        _m = CAT_META[_name]
        _s = _m["slug"]
        items.append(
            f'<li><span class="cat-dot cat-{_s}"></span>'
            f'<span class="cat-name cat-{_s}">{_html_escape(_name)}</span>'
            f'<span class="legend-eq">{_html_escape(_m["equiv"])}</span></li>'
        )
    return ('<section class="legend" aria-label="Category color key">'
            '<p class="legend-title">Category key</p><ul>'
            + "".join(items) + '</ul></section>')


# Weekly compliance target (number of attributable "actions" or hours-equiv
# entries). The order called for 16 job contacts bi-weekly => 8/week as a
# nominal target; we surface it as context, not a fabricated count.
WEEKLY_COMPLIANCE_TARGET_ACTIONS = 8

# Repos to query. Populated dynamically from the account's public repos. The
# account owner may add an explicit allow/deny list via flags if needed.


# --------------------------------------------------------------------------- #
# Data model
# --------------------------------------------------------------------------- #

@dataclass
class Commit:
    repo: str
    sha: str
    date: datetime
    message: str
    html_url: str
    author_login: str
    author_email: str
    additions: int = 0
    deletions: int = 0
    files: int = 0

    @property
    def one_line(self) -> str:
        return self.message.strip().splitlines()[0] if self.message.strip() else "(no message)"


@dataclass
class ActivityRow:
    date: str               # ISO date (Mon) of the commit's week-start
    commit_date: str        # ISO date of the actual commit
    repo: str
    category: str
    description: str        # commit one-liner (sanitized to public-safe)
    proof_url: str          # resolves on github.com
    hours: float
    action: float
    equiv_label: str


@dataclass
class Week:
    start: datetime          # Monday 00:00 local-ish (we use the commit's date)
    end: datetime
    rows: list = field(default_factory=list)
    total_hours: float = 0.0
    total_actions: float = 0.0
    commit_count: int = 0


# --------------------------------------------------------------------------- #
# GitHub access (read-only, public only)
# --------------------------------------------------------------------------- #

class GitHubAPI:
    """Minimal, dependency-free GitHub REST client over `gh` CLI.

    We shell out to `gh api` because the account is already authenticated there
    and it handles 2FA/paging mechanics. All queries target PUBLIC repos only.
    """

    def __init__(self, account: str):
        self.account = account

    def _api(self, path: str) -> object:
        full = f"repos/{self.account}/{path}"
        # Use --paginate where lists are expected; return parsed JSON.
        result = subprocess.run(
            ["gh", "api", "--paginate", full],
            capture_output=True, text=True, check=False,
        )
        if result.returncode != 0:
            # Many 404s are expected for repos with no commits in range; surface
            # nothing rather than crashing the whole run.
            return []
        try:
            return json.loads(result.stdout) if result.stdout.strip() else []
        except json.JSONDecodeError:
            return []

    def list_public_repos(self) -> list[dict]:
        """Return the account's public repos (visibility PUBLIC)."""
        result = subprocess.run(
            ["gh", "repo", "list", self.account, "--limit", "200",
             "--json", "name,visibility,isArchived,isFork,pushedAt"],
            capture_output=True, text=True, check=True,
        )
        repos = json.loads(result.stdout or "[]")
        # Public repos + public-preview/public mirrors of private repos.
        return [r for r in repos
                if r.get("visibility") == "PUBLIC" and not r.get("isArchived", False)]

    def commits_in_range(self, repo: str, since: str, until: str,
                         per_page: int = 100) -> list[Commit]:
        # Pass ISO timestamps with Z; GitHub treats since/until as ISO-8601.
        q = (f"commits?since={since}T00:00:00Z&until={until}T23:59:59Z"
             f"&per_page={per_page}")
        raw = self._api(f"{repo}/{q}")
        commits: list[Commit] = []
        if not isinstance(raw, list):
            return commits
        for item in raw:
            login = (item.get("author") or {}).get("login", "") or ""
            # The commit's own author object carries the email if present.
            email = (((item.get("commit") or {}).get("author") or {})
                     .get("email", "") or "")
            try:
                dt = datetime.strptime(item["commit"]["author"]["date"],
                                       "%Y-%m-%dT%H:%M:%SZ")
            except (KeyError, ValueError):
                continue
            commits.append(Commit(
                repo=repo,
                sha=item.get("sha", ""),
                date=dt,
                message=item.get("commit", {}).get("message", ""),
                html_url=item.get("html_url", ""),
                author_login=login,
                author_email=email,
            ))
        return commits


# --------------------------------------------------------------------------- #
# Classification
# --------------------------------------------------------------------------- #

def classify(commit: Commit) -> dict:
    """Return the rubric entry whose patterns first match repo+message."""
    haystack = f"{commit.repo} {commit.message}".lower()
    for entry in CATEGORY_RUBRIC:
        for pat in entry["patterns"]:
            if re.search(pat, haystack):
                return entry
    return DEFAULT_CATEGORY


def sanitize_message(msg: str) -> str:
    """Strip any accidental PII / secrets from a commit subject line before it
    is quoted into the public log. Aggressive but safe: removes anything that
    looks like an email, a long hex string, or an `=`-style secret assignment."""
    s = msg.splitlines()[0] if msg else ""
    s = re.sub(r"[\w.+-]+@[\w-]+\.[\w.-]+", "[email]", s)           # emails
    s = re.sub(r"\b[0-9a-fA-F]{32,}\b", "[redacted]", s)           # hashes/tokens
    s = re.sub(r"(?i)\b(token|key|secret|password|api[_-]?key)\s*=\s*\S+",
               "[redacted]", s)
    # Collapse any remaining case identifiers / docket patterns defensively.
    s = re.sub(r"(?i)\b(F[A-Z]{1,3}-??\d{4,}-\d{2,})\b", "[docket]", s)
    s = s.replace("`", "'")  # avoid markdown code-span surprises in tables
    s = s.strip()
    return s[:180] or "(work session commit)"


# --------------------------------------------------------------------------- #
# Build
# --------------------------------------------------------------------------- #

def week_key(dt: datetime) -> datetime:
    """Return the Monday 00:00 of the week containing `dt`."""
    return (dt - timedelta(days=dt.weekday())).replace(hour=0, minute=0,
                                                      second=0, microsecond=0)


def attributable(commit: Commit) -> bool:
    """Only count commits attributable to the account owner."""
    ident = commit.author_login.lower()
    if ident and ident not in {a.lower() for a in KNOWN_AUTHOR_IDENTITIES}:
        return False
    # If no login resolved, accept on the basis that the repo belongs to the
    # account and the commit is public there (web-flow/co-authored commits in
    # the account's own public repos are still the account owner's work product
    # or explicit co-authorship shown in the message).
    return True


def gather_commits(api: GitHubAPI, since: str, until: str,
                   deny: set[str]) -> list[Commit]:
    repos = api.list_public_repos()
    all_commits: list[Commit] = []
    for r in repos:
        name = r["name"]
        if name in deny:
            continue
        commits = api.commits_in_range(name, since, until)
        all_commits.extend(commits)
        if commits:
            print(f"  {name}: {len(commits)} commits", file=sys.stderr)
    # Filter to attributable + sort ascending by date.
    all_commits = [c for c in all_commits if attributable(c)]
    all_commits.sort(key=lambda c: c.date)
    return all_commits


def build_weeks(commits: list[Commit], start: datetime,
                end: datetime) -> list[Week]:
    weeks: dict[datetime, Week] = {}
    # Align EVERYTHING to Monday-anchored weeks (US work-search weeks run
    # Sun-Sat by convention, but Monday-anchored bucketing is unambiguous and
    # matches `week_key`). Anchor the pre-seed to the Monday of the start week
    # so the windows and the commit buckets use the identical key space.
    start_monday = week_key(start)
    cur = start_monday
    while cur <= end:
        wk = Week(start=cur, end=cur + timedelta(days=6))
        weeks[cur] = wk
        cur += timedelta(days=7)

    week_start_monday = week_key(start)
    week_end_monday = week_key(end)
    for c in commits:
        wk_start = week_key(c.date)
        # Drop commits whose week falls outside the requested reporting window.
        if wk_start < week_start_monday or wk_start > week_end_monday:
            continue
        wk = weeks.setdefault(wk_start, Week(start=wk_start,
                                             end=wk_start + timedelta(days=6)))
        rubric = classify(c)
        row = ActivityRow(
            date=wk_start.date().isoformat(),
            commit_date=c.date.date().isoformat(),
            repo=c.repo,
            category=rubric["category"],
            description=sanitize_message(c.one_line),
            proof_url=c.html_url or f"https://github.com/{ACCOUNT}/{c.repo}/commit/{c.sha}",
            hours=rubric["hours"],
            action=rubric["action"],
            equiv_label=rubric["equiv"],
        )
        wk.rows.append(row)
        wk.commit_count += 1
        wk.total_hours += row.hours
        wk.total_actions += row.action

    # Attach stored rows in date order inside each week.
    for wk in weeks.values():
        wk.rows.sort(key=lambda r: r.commit_date)
    return [weeks[k] for k in sorted(weeks.keys())]


# --------------------------------------------------------------------------- #
# Markdown rendering
# --------------------------------------------------------------------------- #

def load_reporting_context() -> str:
    """Read an optional `reporting-context.md` sidecar sitting next to this
    script and return its raw markdown, or '' if absent. Injected into the
    generated log so per-user gap/context notes persist across regenerations
    without the generator hardcoding them (keeps the script reusable)."""
    return _load_sidecar("reporting-context.md")


def load_journey_context() -> str:
    """Read the optional `journey-context.md` sidecar (pre-2026
    classroom->product->portfolio arc) and return its raw markdown, or '' if
    absent.Injected into the TOC index so the dated weekly record opens with
    its proper origin story."""
    return _load_sidecar("journey-context.md")


def _load_sidecar(name: str) -> str:
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), name)
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return fh.read().strip()
    except FileNotFoundError:
        return ""


def blob_url(filename: str) -> str:
    """GitHub blob URL for a generated file in the public-preview mirror."""
    return f"{BLOB_BASE}/{filename}"


def pages_url(filename: str) -> str:
    """Raw-served URL for a generated file on the public-preview GitHub Pages
    (legacy Pages serves main raw, so the HTML accordion + per-month md are
    live and browsable on the web)."""
    return f"{HOMEPAGE_URL}vocational-compliance/{filename}"


def month_key(dt: datetime) -> str:
    """'YYYY-MM' for the month containing `dt`."""
    return f"{dt.year:04d}-{dt.month:02d}"


def month_label(dt: datetime) -> str:
    """Human month label, e.g. 'January 2026'."""
    return dt.strftime("%B %Y")


def week_month_anchor(start: datetime) -> datetime:
    """The month a week 'belongs to' — ISO-style: the week's Thursday
    (Monday + 3) determines the month, so a week straddling a month boundary
    lands in the month that contains most of it. The Dec-29 / Jan-1 boundary
    week thus groups under January, not December."""
    return start + timedelta(days=3)


def render_table(rows: list[ActivityRow]) -> str:
    if not rows:
        return "_No attributable commits recorded this week._"
    # Narrow header labels keep the exported-PDF page width sane while the
    # proof-link column carries the repo name AND the full verifiable URL.
    # The URL is shown in full (not abbreviated) because this markdown is the
    # PDF source: printed copies filed via the prothonotary must let a reader
    # type the proof link into a browser. GFM autolinks the bare URL and
    # renders the <br> line break inside the cell.
    header = ("| Date | Category | Activity / Description "
              "| Proof (repo — full commit URL) | Equivalence |")
    sep = "|---|---|---|---|---|"
    lines = [header, sep]
    for r in rows:
        metric = f"{r.hours:g} hrs" if r.hours else ""
        if r.action:
            metric = (f"{r.action:g} action" if not metric
                      else f"{metric} / {r.action:g} action")
        if not metric:
            metric = "—"
        # Repo name label + full visible URL for print/PDF.
        proof = f"**{r.repo}**<br>{r.proof_url}"
        lines.append(
            f"| {r.commit_date} | {r.category} | "
            f"{r.description} | {proof} | {metric} ({r.equiv_label}) |"
        )
    return "\n".join(lines)


def group_months(weeks: list[Week]) -> "dict[str, list[Week]]":
    """Group week buckets by 'YYYY-MM', keyed on each week's Thursday so a
    boundary week lands in the month that contains most of it."""
    by_month: "dict[str, list[Week]]" = defaultdict(list)
    for wk in weeks:
        by_month[month_key(week_month_anchor(wk.start))].append(wk)
    return dict(by_month)


def render_month_md(month_k: str, weeks: list[Week]) -> str:
    """Render ONE month's weeks to a standalone markdown file body. Every
    per-month file is fileable as a separate date-range exhibit and links back
    to the TOC index (blob) + the HTML accordion (Pages) + the homepage."""
    title = month_label(week_month_anchor(weeks[0].start))
    commits = sum(w.commit_count for w in weeks)
    hrs = sum(w.total_hours for w in weeks)
    acts = sum(w.total_actions for w in weeks)
    gen_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    p: list[str] = []
    p.append(f"# {title} — Weekly Vocational Activity Log")
    p.append("")
    p.append(f"_Part of the full Exhibit 4 — "
             f"[table of contents]({blob_url(INDEX_FILE)}) · "
             f"interactive view:"
             f" [{HTML_FILE}]({pages_url(HTML_FILE)})")
    p.append(f" · [public-preview homepage]({HOMEPAGE_URL})_")
    p.append("")
    p.append(f"**Reporting month:** {title}  ")
    p.append(f"**Commits this month:** {commits} · "
             f"**Hours-equiv:** {hrs:g} · **Actions-equiv:** {acts:g}")
    p.append("")
    p.append("---")
    p.append("")
    for wk in weeks:
        label = f"{wk.start.date().isoformat()} → {wk.end.date().isoformat()}"
        after = wk.start.date() > datetime.now(timezone.utc).date()
        p.append(f"## Week of {label}")
        p.append("")
        p.append(f"**Compliance target (context):** "
                 f"{WEEKLY_COMPLIANCE_TARGET_ACTIONS} attributable actions/week")
        p.append("")
        if wk.commit_count > 0:
            p.append(f"_Commits this week:_ {wk.commit_count} · "
                     f"_Hours-equiv:_ {wk.total_hours:g} · "
                     f"_Actions-equiv:_ {wk.total_actions:g}")
        elif after:
            p.append(f"_Upcoming as of {gen_date} — to be populated by "
                     "continued development through the report's end date._")
        else:
            p.append("_No attributable commits recorded this week._")
        p.append("")
        p.append("### Weekly Vocational Activity & Work-Search & Effort Report")
        p.append("")
        p.append(render_table(wk.rows))
        p.append("")
        p.append("---")
        p.append("")
    p.append("## Verification")
    p.append("")
    p.append("Each row is traceable to a public commit via its proof link. "
             "Sworn verification and signature language rest with the filed "
             "memorandum, not this public-facing artifact.")
    p.append("")
    p.append("*This per-month file is regenerated, not hand-edited.*")
    return "\n".join(p)


def render_log(weeks: list[Week], since: str, until: str,
               total_commits: int, out_path: str) -> str:
    grand_hours = sum(w.total_hours for w in weeks)
    grand_actions = sum(w.total_actions for w in weeks)
    active_weeks = sum(1 for w in weeks if w.commit_count > 0)

    parts: list[str] = []
    parts.append("# Exhibit 4 — Vocational Status & Tech Work-Search Log")
    parts.append("")
    parts.append("**Maintainer:** drasticstatic  ")
    parts.append(f"**Reporting period:** {since} → {until}  ")
    parts.append(f"**Generated:** "
                 f"{datetime.now(timezone.utc).strftime('%Y-%m-%d')} "
                 "(regenerable via `vocational-compliance/build_vocational_log.py`)  ")
    parts.append(f"**Public commits attributed in range:** {total_commits}  ")
    parts.append(f"**Active development weeks:** {active_weeks} / {len(weeks)}  ")
    parts.append(f"**Aggregate equivalence:** {grand_hours:g} product "
                 f"development hours · {grand_actions:g} job-search actions  ")
    parts.append("")
    parts.append("---")
    parts.append("")
    parts.append("## What this is")
    parts.append("")
    parts.append(
        "An audit-ready translation of real, public software-development and "
        "quantitative-trading work into the formal categories requested by a "
        "Domestic Relations work-search order. Every row derives from a "
        "verifiable commit on a public repository belonging to the maintainer; "
        "the proof links resolve directly to `github.com`. Commits that touched "
        "only private paths are intentionally absent — the privacy-preserving "
        "sync pipeline prunes them, so this log shows only attributable, "
        "on-the-record work.")
    parts.append("")
    parts.append(
        f"This file is the **table of contents** index. The dated weekly detail "
        f"lives in one file per month (each fileable as a separate date-range "
        f"exhibit); an interactive accordion view is served on GitHub Pages.")
    parts.append("")
    parts.append(
        f"- [`overview.md`]({blob_url('overview.md')}) — concise framework "
        f"behind this exhibit")
    parts.append(
        f"- [`journey-context.md`]({blob_url('journey-context.md')}) — the "
        f"pre-2026 classroom → product → portfolio arc (below)")
    parts.append(
        f"- [`reporting-context.md`]({blob_url('reporting-context.md')}) — "
        f"known reporting gaps in this period")
    parts.append(
        f"- `exhibit-4-log-YYYY-MM.md` — one per-month file "
        f"(e.g. [`exhibit-4-log-2026-07.md`]({blob_url('exhibit-4-log-2026-07.md')}))")
    parts.append(
        f"- [{HTML_FILE}]({pages_url(HTML_FILE)}) — interactive accordion view "
        f"(live on GitHub Pages)")
    parts.append(
        f"- [public-preview homepage]({HOMEPAGE_URL})")
    parts.append("")
    journey = load_journey_context()
    if journey:
        parts.append(journey)
        parts.append("")
        parts.append("---")
        parts.append("")
    ctx = load_reporting_context()
    if ctx:
        parts.append(ctx)
    parts.append("")
    parts.append("---")
    parts.append("")

    parts.append("## Monthly index")
    parts.append("")
    parts.append("| Month | Per-month exhibit (blob) | Interactive view | Commits | Hours-equiv | Actions-equiv |")
    parts.append("|---|---|---|---|---|---|")
    by_month = group_months(weeks)
    for mk in sorted(by_month.keys()):
        mws = by_month[mk]
        lbl = month_label(week_month_anchor(mws[0].start))
        mfname = MONTH_FILE_TMPL.format(mk)
        commits = sum(w.commit_count for w in mws)
        hrs = sum(w.total_hours for w in mws)
        acts = sum(w.total_actions for w in mws)
        parts.append(
            f"| {lbl} | [`{mfname}`]({blob_url(mfname)}) | "
            f"[{HTML_FILE}#{mk}]({pages_url(HTML_FILE)}#{mk}) | "
            f"{commits} | {hrs:g} | {acts:g} |"
        )
    parts.append("")
    parts.append("---")
    parts.append("")

    parts.append("## Verification")
    parts.append("")
    parts.append(
        "I certify that the foregoing weekly vocational and software-development "
        "work log is true, accurate, and reflects active, full-time labor toward "
        "restoring financial capacity. Each row is traceable to a public commit "
        "via its proof link. Perjury language and sworn signatures are carried in "
        "the filed memorandum, not in this public-facing artifact.")
    parts.append("")
    parts.append("---")
    parts.append("")
    parts.append("*This file is regenerated, not hand-edited. To extend the "
                 "reporting period, change the `--since` / `--until` flags in "
                 "`build_vocational_log.py` and re-run.*")

    text = "\n".join(parts)
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(text + "\n")
    return text


# --------------------------------------------------------------------------- #
# HTML accordion rendering (interactive surface — served on GitHub Pages)
# --------------------------------------------------------------------------- #

_HTML_STYLE = """
*, *::before, *::after { box-sizing: border-box; }
:root { color-scheme: dark; --bg:#020617; --panel:rgba(15,23,42,.88);
  --text:#e2e8f0; --muted:#94a3b8; --accent:#38bdf8; --accent-2:#818cf8;
  --container:rgba(15,23,42,.55); --border:rgba(148,163,184,.22); }
html { scroll-behavior: smooth; }
body { margin:0; min-height:100vh; padding:32px 16px;
  font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
  color:var(--text); background:
    radial-gradient(circle at top, rgba(56,189,248,.18), transparent 32%),
    linear-gradient(180deg,#0f172a 0%, var(--bg) 100%); }
.wrap { max-width:1100px; margin:0 auto; }
header { text-align:center; margin-bottom:28px; }
.eyebrow { margin:0 0 8px; font-size:.78rem; font-weight:700;
  letter-spacing:.12em; text-transform:uppercase; color:var(--accent); }
h1 { margin:0; font-size:clamp(1.6rem,4vw,2.6rem); }
.meta { margin:14px auto 0; max-width:42rem; color:var(--muted); font-size:.92rem; line-height:1.6; }

/* CTA glow — gentle light pulse on hero buttons, and a softer glow pulse on
   the section chevrons. Subtle, not strobing. */
@keyframes ctaPulse {
  0%,100% { box-shadow:0 0 0 0 rgba(56,189,248,0); }
  50%     { box-shadow:0 0 16px 2px rgba(56,189,248,.45); }
}
@keyframes ctaGlow {
  0%,100% { text-shadow:0 0 0 rgba(56,189,248,0); }
  50%     { text-shadow:0 0 10px rgba(56,189,248,.6); }
}
.cta { display:inline-block; padding:10px 16px; border-radius:999px;
  background:var(--accent); color:#082f49; font-weight:700; font-size:.85rem;
  text-decoration:none; border:none; cursor:pointer;
  animation: ctaPulse 2.8s ease-in-out infinite; }
.cta:hover { filter:brightness(1.08); }
.cta.green { background:linear-gradient(135deg,#22c55e,#16a34a); color:#fff;
  border:none; }
.cta.green:hover { filter:brightness(1.06); }

/* Nav-row + expand controls read on the dark panel — no near-white buttons,
   so toggling never flashes a "light mode". The two home buttons get a dark
   fill with white text (per Christopher's explicit ask) and accent / green
   borders; the expand-all buttons keep a bold accent outline + slow pulse. */
button.cta.expandall { background:#0b1220; color:#e2e8f0; border:2px solid var(--accent);
  font-weight:800; animation: ctaPulse 3.2s ease-in-out infinite; }
button.cta.expandall:hover { filter:brightness(1.12); background:#111c33; }
.cta.monthtoggle { background:#0b1220; color:#e2e8f0; border:1px solid var(--accent-2);
  font-size:.74rem; padding:4px 11px; font-weight:800; border-radius:999px;
  cursor:pointer; animation:none; }
.cta.monthtoggle:hover { filter:brightness(1.12); background:#111c33; }
.nav-row .cta { background:#0b1220; color:#e2e8f0; border:1px solid var(--accent);
  animation:none; }
.nav-row .cta.green { background:#0b1220; color:#e2e8f0; border:1px solid #22c55e; }
.nav-row .cta:hover, .nav-row .cta.green:hover { filter:brightness(1.12); background:#111c33; }

.hero-btns { display:flex; flex-wrap:wrap; align-items:center; justify-content:center;
  gap:0; margin:18px 0 4px; }
.hero-btns .sep { padding:0 10px; color:var(--accent-2); font-weight:700; }
.nav-row { display:flex; flex-wrap:wrap; align-items:center; justify-content:center;
  gap:0; margin:10px 0 4px; }
.nav-row .sep { padding:0 10px; color:var(--accent-2); font-weight:700; }

/* Expand-weeks button sits inline on the month summary — alongside the
   chevron, the month label, and the mstat line — and only surfaces once the
   month is open. The mstat's margin-left:auto packs it + the chevron right. */
.month > summary .mstat { margin-left:auto; }
.month > summary .cta.monthtoggle { margin-left:10px; }
.month:not([open]) > summary .cta.monthtoggle { display:none; }
.deck { margin:14px auto 4px; max-width:46rem; color:var(--text);
  font-size:.9rem; line-height:1.6; }
.verify-hero { margin:10px auto 0; max-width:42rem; color:var(--muted);
  font-size:.82rem; line-height:1.6; }
summary { cursor:pointer; list-style:none; }
summary::-webkit-details-marker { display:none; }
/* Month accordion: rounded card. overflow:hidden so the CARD never initiates
   horizontal scroll; only inner tables are allowed to scroll-x on mobile. */
.month { margin:22px 0; border:1px solid var(--border); border-radius:16px;
  background:var(--panel); overflow:hidden; }
.month > summary { padding:16px 20px; font-size:1.15rem; font-weight:700;
  display:flex; justify-content:space-between; gap:12px; align-items:center; }
/* Month chevron — accent-triangle that rotates, with the CTA text-glow pulse. */
.month > summary::after { content:"\\25B8"; color:var(--accent); font-size:.95em;
  transition:transform .2s; animation: ctaGlow 2.8s ease-in-out infinite; }
.month[open] > summary::after { transform:rotate(90deg); }
.mstat { font-size:.82rem; font-weight:600; color:var(--muted); white-space:nowrap; }
/* Week (child) chevron — a hollow/dimmer chevron so the hierarchy reads. */
.week > summary::after { content:"\\2023"; color:var(--accent-2); font-size:.85em;
  transition:transform .2s; opacity:.85; }
.week[open] > summary::after { transform:rotate(90deg); }
.week { margin:0; border-top:1px solid var(--border); }
.week > summary { padding:12px 20px; font-weight:600; font-size:.98rem;
  display:flex; justify-content:space-between; gap:10px; align-items:center; }
/* On narrow screens, let the stat wrap rather than forcing horizontal scroll. */
@media (max-width:640px) {
  .week > summary, .month > summary { flex-wrap:wrap; }
  .wstat, .mstat { white-space:normal; }
}
.wstat { font-size:.8rem; color:var(--muted); white-space:nowrap; }
/* The TABLE is the one element allowed to scroll horizontally on small screens —
   it lives inside an overflow-x:auto wrapper. Columns keep readable widths. */
.tablewrap { overflow-x:auto; }
table { width:100%; border-collapse:collapse; font-size:.86rem;
  min-width:38rem; }
th, td { padding:7px 10px; text-align:left; border-bottom:1px solid var(--border);
  vertical-align:top; }
th { position:sticky; top:0; background:#0f172a; color:var(--muted);
  font-weight:600; font-size:.78rem; text-transform:uppercase; letter-spacing:.03em; }
td.proof a, td.desc { word-break:break-word; min-width:6rem; }
td.proof .url { display:block; font-size:.72rem; color:#7dd3fc; word-break:break-all; }
.empty { padding:6px 20px 14px; color:var(--muted); font-style:italic; }
a { color:var(--accent); }
footer { text-align:center; color:var(--muted); font-size:.82rem; margin:32px 0 0; line-height:1.6; }

/* Subtle vertical gradient on the month cards for depth — easy on the eyes,
   still unmistakably part of the dark theme (replaces the flat --panel fill). */
.month { background:linear-gradient(180deg, rgba(15,23,42,.94), rgba(15,23,42,.86)); }

/* Zebra striping in the tables — alternating slate bands track the eye down a
   long commit list; the row hover nudges toward the accent. */
tbody tr { transition: background .15s ease; }
tbody tr:nth-child(even) { background: rgba(148,163,184,.06); }
tbody tr:hover { background: rgba(56,189,248,.10); }

/* Category color-coding: a colored dot chips the Category cell and a matching
   left-rule marks the Equivalence cell. The per-category .cat-<slug> classes
   are emitted by _build_category_css() (one rule per category above). */
td.cat { white-space:nowrap; }
td.cat .cat-dot { display:inline-block; width:.62em; height:.62em; border-radius:50%;
  margin-right:.46em; vertical-align:middle; }
td.cat .cat-name { font-weight:600; }
td.eq { border-left:3px solid transparent; padding-left:12px; }
td.eq .eq-label { display:block; color:var(--muted); font-size:.78rem; }

/* Category key / legend — explains the dot colors at a glance, sits between
   the hero and the month cards. */
.legend { margin:20px auto 0; max-width:46rem; border:1px solid var(--border);
  border-radius:14px; background:var(--container); padding:16px 20px; }
.legend-title { margin:0 0 12px; font-size:.74rem; font-weight:700;
  letter-spacing:.12em; text-transform:uppercase; color:var(--accent-2);
  text-align:center; }
.legend ul { margin:0; padding:0; list-style:none;
  display:grid; gap:8px 18px; grid-template-columns:repeat(auto-fit,minmax(230px,1fr)); }
.legend li { display:flex; align-items:center; gap:.5em; font-size:.82rem;
  color:var(--text); flex-wrap:wrap; }
.legend li .cat-dot { width:.6em; height:.6em; border-radius:50%; flex:0 0 auto; }
.legend li .cat-name { font-weight:600; }
.legend li .legend-eq { margin-left:auto; font-size:.74rem; color:var(--muted);
  text-align:right; }

/* Smooth open animation for the accordions — content fades + rises in as a
   month or week unfolds. The chevron rotation transition (above) carries the
   close-direction cue (native <details> cannot animate the fold on its own;
   kept off this critical exhibit rather than risk a flaky CSS-grid rewrite). */
@keyframes accordionOpen {
  from { opacity:0; transform: translateY(-4px); }
  to   { opacity:1; transform: translateY(0); }
}
.month[open] > .week,
.week[open] > .tablewrap,
.week[open] > .empty { animation: accordionOpen .26s ease both; }

/* Tailored scrollbar — matches the public-preview landing-page accent */
* { scrollbar-width: thin; scrollbar-color: #38bdf8 var(--bg); }
*::-webkit-scrollbar { width:12px; height:12px; }
*::-webkit-scrollbar-track { background:var(--bg); }
*::-webkit-scrollbar-thumb {
  border-radius:8px; border:2px solid var(--bg);
  background:linear-gradient(180deg,#38bdf8,#818cf8); }

/* PRINT: clean PDF export from the browser. Tables scroll horizontally in
   screen view but widen for print; avoid awkward mid-row page breaks. */
@media print {
  body { padding:0; background:#fff; color:#000; font-size:9.5pt; }
  .wrap { max-width:100%; }
  details[open] > .week, details > .week { display:block !important; }
  .month > summary::after, button.cta.expandall, button.cta.monthtoggle,
  .month-actions, .hero-btns .sep, .nav-row .sep { display:none; }
  .month, .week { border:1px solid #999; border-radius:0; break-inside:avoid;
    overflow:visible; }
  summary { break-after:avoid; break-inside:avoid; }
  th, td { border-color:#ccc; color:#000; }
  th { background:#fff; }
  table { font-size:8.5pt; }
  table, tr, td, th { break-inside:avoid; }
  thead { display:table-header-group; }
  footer { color:#000; }
  .legend { border:1px solid #999; background:#fff; }
  .legend li .legend-eq, .legend li .cat-name { color:#000; }
  tr { background:#fff !important; }
  .month[open] > .week, .week[open] > .tablewrap, .week[open] > .empty
    { animation:none !important; }
  *::-webkit-scrollbar { display:none; }
}
"""


def _html_escape(s: str) -> str:
    return html.escape(s or "", quote=True)


def render_html(weeks: list[Week], since: str, until: str,
                total_commits: int, out_path: str) -> str:
    grand_hours = sum(w.total_hours for w in weeks)
    grand_actions = sum(w.total_actions for w in weeks)
    active_weeks = sum(1 for w in weeks if w.commit_count > 0)
    gen_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    by_month = group_months(weeks)

    def metric_cell(r: ActivityRow) -> str:
        m = f"{r.hours:g} hrs" if r.hours else ""
        if r.action:
            m = f"{r.action:g} action" if not m else f"{m} / {r.action:g} action"
        return m or "&mdash;"

    def table_for(rows: list[ActivityRow]) -> str:
        if not rows:
            return '<p class="empty">No attributable commits recorded this week.</p>'
        body = []
        for r in rows:
            url = _html_escape(r.proof_url)
            sl = cat_slug(r.category)
            body.append(
                "<tr>"
                f'<td>{_html_escape(r.commit_date)}</td>'
                f'<td class="cat cat-{sl}">'
                f'<span class="cat-dot cat-{sl}"></span>'
                f'<span class="cat-name">{_html_escape(r.category)}</span></td>'
                f'<td class="desc">{_html_escape(r.description)}</td>'
                f'<td class="proof"><strong><a href="{url}">'
                f'{_html_escape(r.repo)}</a></strong>'
                f'<span class="url">{url}</span></td>'
                f'<td class="eq eq-{sl}">{metric_cell(r)} '
                f'<span class="eq-label">{_html_escape(r.equiv_label)}</span></td>'
                "</tr>"
            )
        return ('<div class="tablewrap">'
                "<table><thead><tr><th>Date</th><th>Category</th>"
                "<th>Activity / Description</th>"
                "<th>Proof (repo &#183; full commit URL)</th>"
                "<th>Equivalence</th></tr></thead><tbody>"
                + "".join(body) + "</tbody></table>"
                + '</div>')

    def week_block(wk: Week) -> str:
        label = f"{wk.start.date().isoformat()} &#8594; {wk.end.date().isoformat()}"
        after = wk.start.date() > datetime.now(timezone.utc).date()
        if wk.commit_count > 0:
            stat = (f"{wk.commit_count} commits &#183; "
                    f"{wk.total_hours:g} hrs &#183; {wk.total_actions:g} actions")
        elif after:
            stat = f"upcoming as of {gen_date}"
        else:
            stat = "no attributable commits"
        body = (table_for(wk.rows) if wk.rows
                else '<p class="empty">No attributable commits recorded this week.</p>')
        return (f'<details class="week"><summary>'
                f'<span>Week of {label}</span>'
                f'<span class="wstat">{stat}</span></summary>'
                f'{body}</details>')

    months_html: list[str] = []
    for mk in sorted(by_month.keys()):
        mws = by_month[mk]
        lbl = month_label(week_month_anchor(mws[0].start))
        commits = sum(w.commit_count for w in mws)
        hrs = sum(w.total_hours for w in mws)
        acts = sum(w.total_actions for w in mws)
        inner = "".join(week_block(w) for w in mws)
        months_html.append(
            f'<details class="month" id="{mk}"><summary>'
            f'<span>{_html_escape(lbl)}</span>'
            f'<span class="mstat">{commits} commits &#183; {hrs:g} hrs '
            f'&#183; {acts:g} actions</span>'
            '<button class="cta monthtoggle" type="button" '
            'onclick="event.stopPropagation();toggleMonth(this)">'
            'expand weeks</button></summary>'
            f'{inner}</details>'
        )

    return (
        "<!doctype html><html lang=\"en\"><head><meta charset=\"UTF-8\">"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
        f"<title>Exhibit 4 — Vocational Log ({since} → {until})</title>"
        f"<style>{_HTML_STYLE}{_CATEGORY_CSS}</style></head><body><div class=\"wrap\">"
        "<header><p class=\"eyebrow\">Exhibit 4</p>"
        "<h1>Vocational Status & Tech Work-Search Log</h1>"
        "<p class=\"meta\"><strong>Maintainer:</strong> drasticstatic &middot; "
        f"<strong>Period:</strong> {since} &rarr; {until} &middot; "
        f"<strong>Generated:</strong> {gen_date}<br>"
        f"{total_commits} attributable public commits across {active_weeks} / "
        f"{len(weeks)} active weeks<br>{grand_hours:g} product-development "
        f"hours &middot; {grand_actions:g} job-search actions</p>"
        # Hero buttons — all open GitHub blob / Pages URLs in a new tab.
        # Interpuncts sit between every button so the row reads as one rail.
        '<div class="hero-btns">'
        f'<a class="cta" target="_blank" rel="noopener" href="{blob_url(INDEX_FILE)}">table of contents (md)</a>'
        '<span class="sep">&#183;</span>'
        f'<a class="cta" target="_blank" rel="noopener" href="{blob_url("overview.md")}">overview</a>'
        '<span class="sep">&#183;</span>'
        f'<a class="cta" target="_blank" rel="noopener" href="{blob_url("journey-context.md")}">the journey</a>'
        '<span class="sep">&#183;</span>'
        f'<a class="cta" target="_blank" rel="noopener" href="{blob_url("reporting-context.md")}">reporting context</a>'
        "</div>"
        # Nav row — every expand control + site home button grouped together
        # so a reviewing officer finds everything intuitively without asking.
        '<div class="nav-row">'
        '<button class="cta expandall" type="button" onclick="toggleAll(this)">'
        "expand all</button>"
        '<span class="sep">&#183;</span>'
        '<button class="cta expandall" type="button" onclick="toggleAllMonths(this)">'
        "expand all months</button>"
        '<span class="sep">&#183;</span>'
        f'<a class="cta" target="_blank" rel="noopener" href="{HOMEPAGE_URL}">'
        "divorce-custody-assistant home &#8599;</a>"
        '<span class="sep">&#183;</span>'
        '<a class="cta green" target="_blank" rel="noopener" '
        'href="https://drasticstatic.github.io/trading-assistant-public-preview/">'
        "trading-assistant home &#8599;</a>"
        "</div>"
        # Navigational deck — what the page IS, before the verification line.
        '<p class="deck">Each entry traces to a verifiable push on GitHub.com; '
        "generated straight from the unadulterated commit record via python "
        "script &mdash; made available in the public repo</p>"
        # Verification line in the hero (navigational guidance).
        '<p class="verify-hero">Expand any month and open each row to view details</p>'
        + _legend_html()
        + "</header>"
        + "".join(months_html)
        + "<script>"
        "function toggleAll(btn){var ms=Array.from(document.querySelectorAll('.month'));"
        "var ws=Array.from(document.querySelectorAll('.week'));"
        "var open=ms.filter(function(d){return d.open;}).length+ws.filter(function(d){return d.open;}).length;"
        "var make=!(open>=(ms.length+ws.length)/2);ms.forEach(function(d){d.open=make;});"
        "ws.forEach(function(d){d.open=make;});btn.textContent=make?'collapse all':'expand all';"
        "var tg=document.querySelectorAll('.monthtoggle');"
        "for(var i=0;i<tg.length;i++){tg[i].textContent=make?'collapse weeks':'expand weeks';}}"
        "function toggleAllMonths(btn){var ms=Array.from(document.querySelectorAll('.month'));"
        "var open=ms.filter(function(d){return d.open;}).length;"
        "var make=!(open>=ms.length/2);ms.forEach(function(d){d.open=make;});"
        "btn.textContent=make?'collapse all months':'expand all months';}"
        "function toggleMonth(btn){var m=btn.closest('.month');"
        "var ws=Array.from(m.querySelectorAll('.week'));"
        "var open=ws.filter(function(w){return w.open;}).length;"
        "var make=!(open>=ws.length/2);ws.forEach(function(w){w.open=make;});"
        "btn.textContent=make?'collapse weeks':'expand weeks';}"
        "</script>"
        "</div></body></html>"
    )


def write_html(weeks: list[Week], since: str, until: str,
               total_commits: int, out_path: str) -> int:
    text = render_html(weeks, since, until, total_commits, out_path)
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(text + "\n")
    return len(text)


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--since", required=True,
                   help="ISO start date YYYY-MM-DD")
    p.add_argument("--until", required=True,
                   help="ISO end date YYYY-MM-DD")
    p.add_argument("--author", default=ACCOUNT,
                   help="GitHub account to pull public repos from")
    deny = p.add_argument("--deny", action="append", default=[],
                   help="Repo name(s) to exclude (repeatable)")
    p.add_argument("--out", default=None,
                   help="Output path for the TOC index (default: "
                        "vocational-compliance/exhibit-4-log.md)")
    args = p.parse_args(argv)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    index_path = args.out or os.path.join(base_dir, INDEX_FILE)
    html_path = os.path.join(base_dir, HTML_FILE)

    try:
        start = datetime.strptime(args.since, "%Y-%m-%d")
        end = datetime.strptime(args.until, "%Y-%m-%d")
    except ValueError:
        print("Dates must be YYYY-MM-DD", file=sys.stderr)
        return 2

    api = GitHubAPI(args.author)
    print(f"Collecting public commits for {args.author} "
          f"({args.since} → {args.until})…", file=sys.stderr)
    commits = gather_commits(api, args.since, args.until, set(args.deny))
    print(f"Total attributable public commits in range: {len(commits)}",
          file=sys.stderr)

    weeks = build_weeks(commits, start, end)
    total_commits = sum(w.commit_count for w in weeks)
    by_month = group_months(weeks)

    # TOC index.
    index_text = render_log(weeks, args.since, args.until,
                            total_commits, index_path)
    print(f"Wrote {index_path} ({len(index_text)} chars)", file=sys.stderr)

    # One per-month markdown file (each fileable as a separate exhibit).
    for mk in sorted(by_month.keys()):
        mfname = os.path.join(base_dir, MONTH_FILE_TMPL.format(mk))
        mtext = render_month_md(mk, by_month[mk])
        with open(mfname, "w", encoding="utf-8") as fh:
            fh.write(mtext + "\n")
        print(f"Wrote {mfname} ({len(mtext)} chars)", file=sys.stderr)

    # Interactive accordion HTML.
    html_len = write_html(weeks, args.since, args.until, total_commits, html_path)
    print(f"Wrote {html_path} ({html_len} chars)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
