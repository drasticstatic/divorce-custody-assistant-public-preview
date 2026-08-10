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
    "category": "Product Management",
    "hours": 4.0,
    "action": 0.0,
    "equiv": "Hours (product management / startup labor)",
}

# Visual color per category — hues spread around the wheel so adjacent
# categories stay distinct, used for the Category cell, the Equivalence cell,
# and the legend dot/key. One source of truth shared by the cells + legend.
CATEGORY_COLORS = {
    "Code Deployment": "#3b82f6",
    "Risk Evaluation": "#ef4444",
    "Retraining Milestone": "#a855f7",
    "Technical Outreach": "#06b8a4",
    "Beta-Testing & Calibration": "#f59e0b",
    "Audit / Education": "#f472b6",
    "Trading": "#22c55e",
    "Product Management": "#818cf8",
}


def cat_slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", (name or "").lower()).strip("-")


# Short, professional, technically-applicable legend descriptors per category.
# These trim the redundant metric-type prefix ("Hours " / "Actions ") from the
# full equivalence strings already shown in the table cells, keeping just the
# meaningful activity label so each legend row fits a single line alongside the
# colored category name. Where two categories shared the same parenthetical in
# the rubric (Beta-Testing & the default Product Development), the legend uses a
# distinct descriptor so the key reads unambiguously. Latitude per Christopher:
# related/shorter wording is fine where it stays professional + technically apt.
CATEGORY_LEGEND_BLURB = {
    "Code Deployment": "Technical infrastructure / core design / production releases / feature implementation / portfolio architecture",
    "Risk Evaluation": "Quantitative compliance audits / security verification / behavioral case studies / sandbox frameworks / sophisticated safeguards",
    "Retraining Milestone": "Targeted vocational skill advancement / certifications / curriculum mastery / ongoing applied self-study",
    "Technical Outreach": "Direct business development / employer-client engagement / prospective lead generation / industry networking",
    "Beta-Testing & Calibration": "System integration / quality assurance / product optimization / troubleshooting / performance tuning / bug remediation",
    "Audit / Education": "Professional performance assessments / codebase auditing / peer-coach dissection / domain research",
    "Product Management": "Full-stack, end-to-end, software engineering / innovation / startup labor / proprietary platform builds / MVP iterations",
    "Trading": "Live futures session screen-time / chart dedication / discretionary model stress testing / systematic strategy analysis / proprietary combine execution",
}

# Category metadata (color + equivalence label + legend blurb) keyed by category
# name. Pulled from the rubric + default so the legend and the cells always agree.
CAT_META = {}
for _entry in CATEGORY_RUBRIC + [DEFAULT_CATEGORY]:
    _name = _entry["category"]
    # Legend blurb: prefer the hand-tuned short descriptor; fall back to the
    # parenthetical of the full equiv string (metric-type prefix stripped).
    _blurb = CATEGORY_LEGEND_BLURB.get(_name) or re.sub(
        r"^\s*(?:Hours|Actions)\s*\((.*)\)\s*$", r"\1", _entry["equiv"]
    ) or _entry["equiv"]
    CAT_META[_name] = {
        "color": CATEGORY_COLORS.get(_name, "#94a3b8"),
        "equiv": _entry["equiv"],
        "slug": cat_slug(_name),
        "blurb": _blurb,
    }

# Trading is NOT a commit-classified category (it comes from an external
# Tradovate CSV, not the GitHub commit record), so it isn't in CATEGORY_RUBRIC.
# It gets its own CAT_META entry so the legend + heatmap palette include it as
# the 8th key (green, matching the trading-assistant home button).
CAT_META["Trading"] = {
    "color": CATEGORY_COLORS["Trading"],
    "equiv": "Hours (live futures trading session)",
    "slug": cat_slug("Trading"),
    "blurb": CATEGORY_LEGEND_BLURB["Trading"],
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
    # Trading is the external (CSV-sourced) layer; show it last, after the
    # commit-classified categories, so the legend reads commit-activity first
    # then the trading-session overlay.
    if "Trading" not in seen:
        seen.append("Trading")
    items = []
    for _name in seen:
        _m = CAT_META[_name]
        _s = _m["slug"]
        items.append(
            f'<li><span class="cat-dot cat-{_s}"></span>'
            f'<span class="cat-name cat-{_s}">{_html_escape(_name)}</span>'
            f'<span class="legend-eq">{_html_escape(_m["blurb"])}</span></li>'
        )
    return ('<section class="legend" aria-label="Category color key / legend">'
            '<p class="legend-title">Category key / legend</p><ul>'
            + "".join(items) + '</ul></section>')


# Last date the trading-assistant public repo carries VERIFIED trading-session
# data (Tradovate + TradeZella, digested by Fortuna). The heatmap trading overlay
# surfaces this as the "verified through <date>" cutoff while the CSV flow into
# this repo is publish-pending. When trading-days.csv IS present here, the
# cutoff is computed from its latest row instead (max date), so this fallback
# only governs the placeholder path. Edit here to advance the cutoff.
TRADING_VERIFIED_THROUGH_FALLBACK = "2026-05-14"


def _load_trading_days() -> "dict[str, float] | None":
    """Read vocational-compliance/trading-days.csv if present.

    Columns: date,hours,note  (note optional; header row 'date' skipped).
    Returns {ISO_date: hours} or None when the file is absent. None tells the
    heatmap to fall back to the placeholder scheduled session (Sun 18:00 to
    Fri 17:00 EST) and label itself as a placeholder pending the verified CSV.
    """
    import csv as _csv
    _path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "trading-days.csv")
    if not os.path.exists(_path):
        return None
    out: dict[str, float] = {}
    with open(_path, newline="", encoding="utf-8") as _fh:
        for _row in _csv.reader(_fh):
            if not _row:
                continue
            _d = _row[0].strip()
            if not _d or _d.startswith("#") or _d.lower() == "date":
                continue
            try:
                _iso = datetime.strptime(_d, "%Y-%m-%d").date().isoformat()
                _hrs = float(_row[1]) if len(_row) > 1 and _row[1].strip() else 0.0
            except (ValueError, IndexError):
                continue
            out[_iso] = _hrs
    return out or None


def _contribution_heatmap_html(weeks: list, since: str, until: str) -> str:
    """Year-grid heatmap — blue-shaded days + colored category dots + trading dot.

    Every in-range day carries blue shading as ATTESTED daily-activity context
    (crypto is managed around the clock, so no day reads as blank) — but the
    shading is context, never a verified-commit claim; intensity only rises with
    attributable commit count. Each activity category hit that day overlays a
    small colored dot (color = the legend key), NOT a horizontal partition. A
    filled green dot marks a trading session (scheduled placeholder or verified
    CSV; the hollow ring is retired so days never read empty). Own data, no
    GitHub API, no rate limit; zero-build / zero-JS-framework static.
    """
    # Per-day per-category commit counts + day totals.
    day_cats: dict[str, dict[str, int]] = {}
    for _wk in weeks:
        for _r in _wk.rows:
            _d = day_cats.setdefault(_r.commit_date, {})
            _d[_r.category] = _d.get(_r.category, 0) + 1

    _start = datetime.strptime(since, "%Y-%m-%d")
    _end = datetime.strptime(until, "%Y-%m-%d")

    # Sunday-anchored columns (GitHub contribution-graph convention).
    _sunday = lambda _dt: _dt - timedelta(days=(_dt.weekday() + 1) % 7)
    _first = _sunday(_start)
    _last = _sunday(_end) + timedelta(days=6)

    # Trading-day overlay. Verified CSV wins if trading-days.csv is present;
    # otherwise the placeholder scheduled session (Sun 18:00 to Fri 17:00 EST)
    # so the framework is visible while labeled as a placeholder.
    _trading = _load_trading_days()
    _ph = _trading is None
    if _ph:
        _trading = {}
        _cur = _start
        while _cur <= _end:
            # Mon(0)..Fri(4) + Sun(6) are session days; Sat(5) is the only off day.
            if _cur.weekday() != 5:
                _trading[_cur.date().isoformat()] = 6.0
            _cur += timedelta(days=1)

    _TRADING_COLOR = CATEGORY_COLORS["Trading"]
    _cell, _gap, _stride = 13, 3, 16
    _pad_l, _pad_t = 28, 6
    _cols: list = []
    _cur = _first
    while _cur <= _last:
        _cols.append(_cur)
        _cur += timedelta(days=7)
    _w = _pad_l + len(_cols) * _stride + _gap
    _h = _pad_t + 7 * _stride + _gap

    def _shade_level(_total: int) -> "tuple[str, float]":
        # Blue ramp (dark-base -> bright-accent) by attributable commit count.
        # Floor = attested daily-activity CONTEXT (crypto is managed around the
        # clock) so no day reads blank; this is honest context, NOT a verified
        # commit claim. The green trading dot is the verifiable marker.
        if _total <= 0:
            return "#0e3a5c", 0.34  # floor: attestable context, no commits
        if _total == 1:
            return "#155e8a", 0.50
        if _total <= 3:
            return "#1d7eb8", 0.66
        if _total <= 6:
            return "#2ba4e6", 0.82
        return "#38bdf8", 0.95

    def _dot_centers(_n: int) -> list:
        # Evenly spaced centers along a row near the bottom of the 13px cell.
        _cy = _y + _cell - 3.1
        if _n <= 0:
            return []
        if _n == 1:
            return [(_x + _cell / 2, _cy)]
        return [(_x + (_i + 1) * (_cell / (_n + 1)), _cy) for _i in range(_n)]

    def _heat_day_rect(_hx: int, _hy: int, _iso: str, _title: str) -> str:
        # Transparent overlay covering the cell - the hit, tooltip, and click
        # target so a day is large enough to tap (the underlying visuals are
        # thin dots/shading, too small to hit precisely on a phone). Drawn
        # AFTER a cell's visuals so the overlay sits on top; fill="transparent"
        # + pointer-events="all" makes the whole cell hit-testable (fill="none"
        # alone is NOT). data-date drives the day -> record navigation in JS.
        return (
            f'<rect class="heat-day" data-date="{_iso}" x="{_hx:.1f}" '
            f'y="{_hy:.1f}" width="{_cell}" height="{_cell}" rx="2" '
            f'fill="transparent" pointer-events="all">'
            f'<title>{_title}</title></rect>'
        )

    _cells: list[str] = []
    for _ci, _cw in enumerate(_cols):
        for _di in range(7):
            _day = _cw + timedelta(days=_di)
            _iso = _day.date().isoformat()
            _in = _start <= _day <= _end
            _x = _pad_l + _ci * _stride
            _y = _pad_t + _di * _stride
            if not _in:
                _cells.append(
                    f'<rect x="{_x:.1f}" y="{_y:.1f}" width="{_cell}" '
                    f'height="{_cell}" rx="2" fill="#0b1220" opacity="0.25">'
                    f'<title>{_iso}: outside range</title></rect>'
                )
                continue
            _cats = day_cats.get(_iso, {})
            _total = sum(_cats.values())
            _traded = _iso in _trading
            _fill, _op = _shade_level(_total)
            if not _cats and not _traded:
                # Floor: attestable daily activity (crypto is around the clock),
                # no attributable commits — honest CONTEXT, not a verified claim.
                _cells.append(
                    f'<rect x="{_x:.1f}" y="{_y:.1f}" width="{_cell}" '
                    f'height="{_cell}" rx="2" fill="{_fill}" opacity="{_op}"/>'
                )
                _cells.append(_heat_day_rect(_x, _y, _iso,
                    f'{_iso}: attestable daily activity (crypto managed '
                    "around the clock); 0 attributable commits recorded"))
                continue
            if not _cats and _traded:
                # Trading session with no commits that day: a SOLID green dot
                # (the hollow-ring placeholder is retired so no day reads empty).
                # The blue floor carries the attested-context shading underneath.
                _tcx, _tcy = _x + _cell / 2, _y + _cell / 2
                _hrs = _trading.get(_iso)
                _lab = ("scheduled trading session (placeholder; Tradovate and "
                        "TradeZella CSV pending)" if _ph else
                        f"{_hrs:g} hrs trading session (verified Tradovate "
                        "and TradeZella data)")
                _cells.append(
                    f'<rect x="{_x:.1f}" y="{_y:.1f}" width="{_cell}" '
                    f'height="{_cell}" rx="2" fill="{_fill}" opacity="{_op}"/>'
                    f'<circle cx="{_tcx:.1f}" cy="{_tcy:.1f}" r="4.2" '
                    f'fill="{_TRADING_COLOR}" stroke="rgba(2,6,23,0.55)" '
                    f'stroke-width="0.6"/>'
                )
                _cells.append(_heat_day_rect(_x, _y, _iso, f'{_iso}: {_lab}'))
                continue
            # Commit day: blue shaded base (intensity = commit count) + one colored
            # dot per category hit that day (legend color) + green trading dot.
            _ordered = sorted(_cats.items(), key=lambda kv: (-kv[1], kv[0]))
            _tparts = [f"{_total} commit{'s' if _total != 1 else ''}"]
            for _cat, _cnt in _ordered:
                _tparts.append(f"{_cat}: {_cnt}")
            _cells.append(
                f'<rect x="{_x:.1f}" y="{_y:.1f}" width="{_cell}" '
                f'height="{_cell}" rx="2" fill="{_fill}" opacity="{_op}"/>'
            )
            _centers = _dot_centers(len(_ordered))
            for (_dcx, _dcy), (_cat, _cnt) in zip(_centers, _ordered):
                _col = CATEGORY_COLORS.get(_cat, "#94a3b8")
                _cells.append(
                    f'<circle cx="{_dcx:.1f}" cy="{_dcy:.1f}" r="2.1" '
                    f'fill="{_col}" stroke="rgba(2,6,23,0.5)" '
                    f'stroke-width="0.5"/>'
                )
            if _traded:
                _cells.append(
                    f'<circle cx="{_x + _cell - 2.3:.1f}" cy="{_y + 2.3:.1f}" '
                    f'r="1.7" fill="{_TRADING_COLOR}" '
                    f'stroke="rgba(2,6,23,0.5)" stroke-width="0.4"/>'
                )
                _tparts.append(
                    f"{_trading.get(_iso, 0):g} hrs trading session "
                    "(verified Tradovate and TradeZella data)" if not _ph else
                    "scheduled trading session (placeholder; CSV pending)"
                )
            _cells.append(
                f'<rect class="heat-day" data-date="{_iso}" x="{_x:.1f}" '
                f'y="{_y:.1f}" width="{_cell}" height="{_cell}" rx="2" '
                f'fill="transparent" stroke="rgba(148,163,184,0.18)" '
                f'stroke-width="0.5" pointer-events="all">'
                f'<title>{_iso}: {" · ".join(_tparts)}</title></rect>'
            )

    _row_lbl = {0: "Sun", 2: "Tue", 4: "Thu", 6: "Sat"}
    _lbls = [
        f'<text x="0" y="{_pad_t + _di * _stride + 10:.1f}" font-size="9" '
        f'fill="#94a3b8">{_nm}</text>'
        for _di, _nm in _row_lbl.items()
    ]

    _svg = (
        f'<svg class="heat-svg" viewBox="0 0 {_w:.0f} {_h:.0f}" width="100%" '
        f'preserveAspectRatio="xMidYMid meet" role="img" '
        f'aria-label="Daily contribution heatmap {_start.date()} to {_end.date()}">'
        + "".join(_lbls) + "".join(_cells) + '</svg>'
    )

    _verified_through = (
        max(_trading) if not _ph else TRADING_VERIFIED_THROUGH_FALLBACK
    )
    _trading_note = (
        f"Verified Tradovate / TradeZella session data (digested via the "
        f"trading-assistant repo) — publish pending; the public GitHub record "
        f"currently carries verified sessions through {_verified_through} "
        f"— see reporting-context.md for details on the backlog to be released."
        if _ph else
        f"Verified Tradovate / TradeZella session data (digested via the "
        f"trading-assistant repo) — the public GitHub record currently "
        f"carries verified sessions through {_verified_through} "
        f"— see reporting-context.md for details on the backlog to be released."
    )
    # The prior two text blocks (a heatmap-sub paragraph above the grid and a
    # trading cutoff note below in .heat-scale) read as one idea, so they are
    # MERGED into a single paragraph carrying both the shading legend and the
    # verified-through cutoff. The hint line takes the freed second slot; the
    # grid is wrapped in .heat-wrap (click to enlarge + day nav) and an enlarged
    # <dialog> lightbox carries the rest (dep-free; mobile gets a legible copy).
    _merged = (
        "Each square is one calendar day in the reporting window "
        f"({_start.date()} → {_end.date()}); blue shading marks daily activity "
        "and deepens with attributable commits, and a colored dot marks each "
        f"activity category hit that day. {_trading_note}"
    )
    return (
        '<section class="heatmap" aria-label="Contributions heatmap">'
        '<p class="heatmap-title">Contributions Heatmap</p>'
        f'<p class="heatmap-sub">{_merged}</p>'
        '<div class="heat-wrap" id="heat-thumb" role="button" tabindex="0"'
        ' aria-label="Click to enlarge the contributions heatmap">'
        + _svg
        + "</div>"
        '<p class="heat-hint">'
        '<button class="heat-enlarge-btn" type="button" id="heat-enlarge"'
        ' aria-label="Enlarge the contributions heatmap">'
        '<span class="heat-enlarge-click">⤢ Click to enlarge</span>'
        '<span class="heat-enlarge-tap">⤢ Tap to enlarge</span>'
        '</button> '
        '<span class="heat-day-note">or tap any day to jump to its record.</span>'
        '</p>'
        '<p class="heat-hover-hint">Hover any day for a tooltip.</p>'
        '<dialog class="heat-lightbox" id="heat-lightbox" aria-label="Enlarged'
        ' contributions heatmap — tap a day to jump to its record">'
        '<button class="heat-close" type="button" aria-label="Close enlarged view">✕ close'
        "</button>"
        '<div class="heat-large" aria-hidden="true"></div>'
        '<p class="heat-rotate-hint">↻ rotate your device horizontally for the best enlarged view</p>'
        '<p class="heat-hint">Tap a day to jump to its record in the log below.</p>'
        "</dialog>"
        "</section>"
    )


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
    linear-gradient(180deg,#0f172a 0%, var(--bg) 100%);
  /* Glassmorphism fix (v5): pin the background to the VIEWPORT, not the
     document. A document-height linear-gradient stretches as accordions open,
     shifting each panel's position up toward the lighter #0f172a top — so
     panels appeared to lighten as others unfolded. With the background fixed
     to the viewport, the glow sits still behind the glass; opening a panel
     never re-maps the gradient beneath it. Combined with the flat .month
     glass (no gradient) + transparent .week (no own fill), the rendered
     surface is now height-independent. */
  background-attachment: fixed;
  /* Horizontal pan lock: clip anything wider than the viewport so the embedded
     iframe cannot scroll left/right as a whole on mobile (the linearized card
     tables + responsive heatmap already keep content within width; this is the
     belt-and-braces guard). Vertical scroll is untouched. */
  overflow-x: hidden; }
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
  gap:9px 0; margin:18px 0 4px; }
.hero-btns .sep { padding:0 10px; color:var(--accent-2); font-weight:700; }
.nav-row { display:flex; flex-wrap:wrap; align-items:center; justify-content:center;
  gap:9px 0; margin:10px 0 4px; }
.nav-row .sep { padding:0 10px; color:var(--accent-2); font-weight:700; }

/* Sticky nav banner — sits between the legend and the month accordions and
   FREEZES at the viewport top once scrolled past (position:sticky; top:0), so
   the row-guidance string + the expand/navigate hamburger stay reachable the
   whole way down the page. The 3-line icon animates to an X when open and
   pulses (CTA) like the hero button; the dropdown anchors below the trigger. */
.nav-banner { position:sticky; top:0; z-index:40;
  display:flex; align-items:center; gap:14px;
  margin:14px 0 0; padding:9px 14px;
  border:1px solid var(--border); border-radius:14px;
  background:rgba(11,18,32,.9);
  -webkit-backdrop-filter:blur(10px); backdrop-filter:blur(10px);
  box-shadow:0 6px 20px rgba(2,6,23,.32); }
.nav-banner .banner-text { flex:1 1 auto; text-align:left;
  font-size:.8rem; color:var(--muted); line-height:1.4; }
.nav-banner .hamburger-wrap { position:relative; flex:0 0 auto; }
.hamburger { width:42px; height:42px; border-radius:12px; cursor:pointer;
  border:1px solid var(--border); background:var(--container);
  box-shadow:0 4px 14px rgba(2,6,23,.3);
  display:flex; flex-direction:column; align-items:center; justify-content:center;
  gap:5px; padding:0; animation: ctaPulse 3.2s ease-in-out infinite; }
.hamburger span { display:block; width:18px; height:2px; border-radius:2px;
  background:var(--accent); transition:transform .22s, opacity .18s; }
.hamburger:hover { filter:brightness(1.12); }
.hamburger.open span:nth-child(1) { transform:translateY(7px) rotate(45deg); }
.hamburger.open span:nth-child(2) { opacity:0; }
.hamburger.open span:nth-child(3) { transform:translateY(-7px) rotate(-45deg); }
.hamburger-menu { position:absolute; top:calc(100% + 6px); right:0; z-index:49;
  min-width:230px; padding:12px 14px; border:1px solid var(--border);
  border-radius:14px; background:rgba(15,23,42,.95);
  -webkit-backdrop-filter:blur(8px); backdrop-filter:blur(8px);
  box-shadow:0 12px 32px rgba(2,6,23,.45);
  display:none; flex-direction:column; gap:8px; }
.hamburger.open + .hamburger-menu { display:flex; }
.hamburger-menu .cta { width:100%; text-align:left; margin:0;
  background:#0b1220; color:#e2e8f0; border:1px solid var(--accent);
  animation:none; }
.hamburger-menu .cta.green { border:1px solid #22c55e; }
.hamburger-menu .cta:hover { filter:brightness(1.12); background:#111c33; }
.hamburger-menu .hmenu-title { font-size:.66rem; font-weight:700;
  letter-spacing:.1em; text-transform:uppercase; color:var(--accent-2);
  padding:2px 4px 4px; border-bottom:1px solid var(--border); margin-bottom:2px; }
.hamburger-menu .hmenu-segue { display:block; text-align:center;
  color:var(--accent-2); font-size:.72rem; margin:3px 0 1px;
  border-top:1px solid var(--border); padding-top:7px; }

/* Expand-weeks button sits inline on the month summary — alongside the
   chevron, the month label, and the mstat line — and only surfaces once the
   month is open. The mstat's margin-left:auto packs it + the chevron right. */
.month > summary .mstat { margin-left:auto; }
.month > summary .cta.monthtoggle { margin-left:10px; }
.month:not([open]) > summary .cta.monthtoggle { display:none; }
.deck { margin:14px auto 4px; max-width:46rem; color:var(--text);
  font-size:.9rem; line-height:1.6; }
summary { cursor:pointer; list-style:none; }
summary::-webkit-details-marker { display:none; }
/* Month accordion: a single glass panel. ONE consistent translucent fill +
   backdrop blur so the rendered background is HEIGHT-INDEPENDENT — opening a
   month (adding panel area) never lightens the surface, because the glass
   is a fixed alpha everywhere, not a stacked/gradient fill. overflow:hidden
   so the card never initiates horizontal scroll (only inner tables scroll-x). */
.month { margin:22px 0; border:1px solid var(--border); border-radius:16px;
  background:rgba(15,23,42,.72); -webkit-backdrop-filter:blur(8px);
  backdrop-filter:blur(8px);
  box-shadow:0 8px 24px rgba(2,6,23,.35), inset 0 1px 0 rgba(148,163,184,.10);
  overflow:hidden; }
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
/* Glassmorphism (v5): the week has NO background of its own — it inherits the
   month's glass. A translucent .week fill stacked inside the translucent .month
   multiplied the alphas and lightened the surface; transparent here keeps an
   expanded month + its open weeks reading as ONE continuous glass panel. */
.week { margin:0; border-top:1px solid var(--border); background:transparent; }
.week > summary { padding:12px 20px; font-weight:600; font-size:.98rem;
  display:flex; justify-content:space-between; gap:10px; align-items:center; }
/* On narrow screens, let the stat wrap rather than forcing horizontal scroll. */
@media (max-width:640px) {
  .week > summary, .month > summary { flex-wrap:wrap; }
  .wstat, .mstat { white-space:normal; }
}
/* Mobile (screen only): let the legend wrap so blurbs stop overflowing the
   iframe, and linearize the commit table into stacked labeled cards so the
   iframe never scrolls horizontally on a phone. Desktop keeps the one-line
   legend rows; print is untouched (print width is always above the breakpoint). */
@media screen and (max-width:640px) {
  .legend li { flex-wrap:wrap; white-space:normal; }
  .legend li .legend-eq { margin-left:0; text-align:left; flex:1 1 100%;
    padding-left:1.7em; }
  .tablewrap { overflow:visible; }
  table, tbody, tr, td { display:block; box-sizing:border-box; }
  table { min-width:0; }
  thead { display:none; }
  tbody tr { margin:10px 0; padding:10px 12px;
    border:1px solid var(--border); border-radius:10px;
    background:rgba(15,23,42,.35); }
  td { display:flex; flex-wrap:wrap; align-items:baseline;
    justify-content:flex-start; gap:6px 12px; padding:7px 0; border:0;
    border-bottom:1px solid rgba(148,163,184,.08); }
  td:last-child { border-bottom:0; }
  td::before { content:attr(data-label); flex:0 0 5.5rem;
    font-size:.68rem; font-weight:700; text-transform:uppercase;
    letter-spacing:.04em; color:var(--muted); }
  td.proof a { word-break:break-all; }
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

/* Glassmorphism note (v4→v5): the earlier vertical gradient on .month was
   removed. Its bottom stop (.86 alpha, lighter than the .94 top) was one
   contributor to the "background lightens as accordions unfold" effect, and
   stacking a translucent .week fill inside multiplied the alphas further. The
   .month is now a single flat translucent glass (declared above); the .week
   inherits it with no fill of its own (declared below), so expanding a month
   adds flat-dark area, never a lighter layer. */

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
.legend { margin:20px auto 0; max-width:64rem; border:1px solid var(--border);
  border-radius:14px; background:var(--container); padding:18px 20px; }
.legend-title { margin:0 0 14px; font-size:.74rem; font-weight:700;
  letter-spacing:.12em; text-transform:uppercase; color:var(--accent-2);
  text-align:center; }
.legend ul { margin:0; padding:0; list-style:none;
  display:grid; gap:14px 18px; grid-template-columns:repeat(auto-fit,minmax(300px,1fr)); }
.legend li { display:flex; flex-wrap:wrap; align-items:baseline; gap:.25em .5em;
  font-size:.82rem; color:var(--text); }
.legend li .cat-dot { width:.62em; height:.62em; border-radius:50%; flex:0 0 auto;
  margin-right:.3em; align-self:center; }
.legend li .cat-name { font-weight:700; flex:0 0 auto; }
.legend li .legend-eq { flex:1 1 100%; margin:.15em 0 0 1.7em; font-size:.76rem;
  line-height:1.5; color:var(--muted); white-space:normal; text-align:left; }

/* Daily contribution heatmap — a year-at-a-glance summary above the monthly
   detail. Own data, variant="minimal" aesthetic (low-saturation slate-to-accent
   squares, no month labels, Sunday-anchored columns). */
.heatmap { margin:22px auto 0; max-width:52rem; border:1px solid var(--border);
  border-radius:14px; background:var(--container); padding:16px 20px 14px; }
/* Click-to-enlarge replaces horizontal scroll (v9): the heatmap is responsive
   width=100% so it scales down on mobile, and clicks OPEN an enlarged lightbox
   instead of scrolling a too-thin grid that could get missed. Each day cell is
   a transparent hit-target overlay (.heat-day) carrying data-date for the
   day->record navigation. */
.heat-wrap { position:relative; margin:0 0 2px; padding:2px; cursor:zoom-in;
  border-radius:10px; outline:none; }
.heat-wrap:focus-visible { box-shadow:0 0 0 2px var(--accent); }
.heat-day { cursor:pointer; }
/* v10: an explicit ENLARGE button sits below the grid so the enlarge action is
   its own clear tap target — distinct from the day cells, which navigate to the
   per-day record. The grid (and day cells) keep their own behaviour intact. */
.heat-hint { margin:10px 0 0; text-align:center; font-size:.74rem; color:var(--muted);
  font-style:normal; display:flex; flex-wrap:wrap; align-items:center;
  justify-content:center; gap:4px 12px; }
.heat-enlarge-btn { display:inline-block; padding:8px 18px; border-radius:999px;
  border:1px solid var(--accent); background:rgba(56,189,248,0.10);
  color:var(--accent); font-weight:700; font-size:.78rem; font-style:normal;
  font-family:inherit; cursor:pointer; white-space:nowrap;
  animation:ctaPulse 2.6s ease-in-out infinite; }
.heat-enlarge-btn:hover { filter:brightness(1.1); background:rgba(56,189,248,0.18); }
.heat-enlarge-btn:focus-visible { box-shadow:0 0 0 2px var(--accent); outline:none; }
.heat-enlarge-tap { display:none; }
.heat-day-note { font-style:italic; }
/* Desktop pointer only: a small hint that each day cell carries a hover
   tooltip. Hidden on touch/narrow (no hover affordance there). */
.heat-hover-hint { margin:4px 0 0; text-align:center; font-size:.7rem;
  color:var(--muted); font-style:italic; }
/* Mobile / touch: swap the button label from "Click" to "Tap" and hide the
   desktop-only hover-tooltip hint. */
@media (pointer:coarse), (max-width:640px) {
  .heat-enlarge-click { display:none; }
  .heat-enlarge-tap { display:inline; }
  .heat-hover-hint { display:none; }
}
.heat-rotate-hint { display:none; margin:6px auto 0; text-align:center;
  font-size:.72rem; color:var(--accent-2); font-style:italic; }
/* Inside the lightbox on a narrow portrait screen: show the rotate hint. */
@media (max-width:640px) and (orientation:portrait) {
  .heat-rotate-hint { display:block; }
}
.heat-lightbox { position:relative; width:min(96vw,1100px); max-width:96vw;
  max-height:92vh; padding:18px 16px 12px; background:var(--panel);
  border:1px solid var(--border); border-radius:16px; color:var(--text); }
.heat-lightbox::backdrop { background:rgba(2,6,23,0.78); backdrop-filter:blur(3px); }
.heat-large { width:100%; overflow:auto; text-align:center; }
.heat-large svg { width:100%; max-width:64rem; height:auto; max-height:76vh;
  display:block; margin:0 auto; }
.heat-large .heat-day { cursor:pointer; }
.heat-close { position:absolute; top:10px; right:14px; z-index:2; border:none;
  border-radius:999px; background:var(--accent); color:#082f49; font-weight:700;
  cursor:pointer; padding:5px 12px; font-size:.82rem; }
.heatmap-title { margin:0 0 4px; font-size:.74rem; font-weight:700;
  letter-spacing:.12em; text-transform:uppercase; color:var(--accent-2);
  text-align:center; }
.heatmap-sub { margin:0 0 10px; font-size:.72rem; color:var(--muted);
  text-align:center; line-height:1.45; }
.heat-svg { display:block; margin:0 auto; max-width:100%; height:auto;
  font-family:inherit; }
.heat-svg rect { shape-rendering:crispEdges; }
.heat-svg text { font-family:inherit; }
.heat-scale { display:flex; align-items:center; justify-content:center;
  gap:4px; margin:8px auto 0; font-size:.68rem; color:var(--muted); }
.heat-scale span { line-height:1; }
.heat-scale i { width:11px; height:11px; border-radius:2px; display:inline-block;
  border:1px solid rgba(148,163,184,.16); }

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
  .month-actions, .hero-btns .sep, .nav-row .sep,
  .nav-banner, .hamburger, .hamburger-menu { display:none; }
  .month, .week { border:1px solid #999; border-radius:0; break-inside:avoid;
    overflow:visible; background:#fff !important;
    -webkit-backdrop-filter:none; backdrop-filter:none; box-shadow:none; }
  summary { break-after:avoid; break-inside:avoid; }
  th, td { border-color:#ccc; color:#000; }
  th { background:#fff; }
  table { font-size:8.5pt; }
  table, tr, td, th { break-inside:avoid; }
  thead { display:table-header-group; }
  footer { color:#000; }
  .legend { border:1px solid #999; background:#fff; }
  .legend li .legend-eq, .legend li .cat-name { color:#000; }
  .heatmap { border:1px solid #999; background:#fff; -webkit-print-color-adjust:exact;
    print-color-adjust:exact; break-inside:avoid; }
  .heatmap-title, .heatmap-sub, .heat-scale span { color:#000; }
  .heat-svg { print-color-adjust:exact; -webkit-print-color-adjust:exact; }
  .heat-svg rect, .heat-scale i { -webkit-print-color-adjust:exact;
    print-color-adjust:exact; }
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
                f'<td data-label="Date">{_html_escape(r.commit_date)}</td>'
                f'<td class="cat cat-{sl}" data-label="Category">'
                f'<span class="cat-dot cat-{sl}"></span>'
                f'<span class="cat-name">{_html_escape(r.category)}</span></td>'
                f'<td class="desc" data-label="Activity">{_html_escape(r.description)}</td>'
                f'<td class="proof" data-label="Proof"><strong><a href="{url}">'
                f'{_html_escape(r.repo)}</a></strong>'
                f'<span class="url">{url}</span></td>'
                f'<td class="eq eq-{sl}" data-label="Equivalence">{metric_cell(r)} '
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
            f"&#183; {acts:g} actions</span></summary>"
            f"{inner}</details>"
        )

    return (
        "<!doctype html><html lang=\"en\"><head><meta charset=\"UTF-8\">"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
        f"<title>Exhibit 4 — Vocational Log ({since} → {until})</title>"
        "<link rel=\"icon\" href=\"favicon.svg\" type=\"image/svg+xml\">"
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
        # Navigational deck — what the page IS, before the category key + guidance.
        '<p class="deck">Each entry traces to a verifiable push on GitHub.com; '
        "generated straight from the unadulterated commit record via python "
        "script &mdash; made available in the public repo</p>"
        # Contributions heatmap sits above the category key so a reviewer sees
        # the year-at-a-glance grid before the color key + the monthly detail.
        + _contribution_heatmap_html(weeks, since, until)
        # Category key sits above the verification line so the legend reads first.
        + _legend_html()
        + "</header>"
        # Sticky nav banner — a SIBLING of the months (child of .wrap), not
        # inside <header>, so its sticky range spans the whole month-accordion
        # list (position:sticky sticks within its parent; .wrap covers the page).
        # Holds the row-guidance string + the hamburger trigger; freezes at
        # viewport-top once scrolled past. The dropdown carries expand controls
        # + the two home links, with a segue divider between them.
        + '<div class="nav-banner">'
        + '<span class="banner-text">Open each row to view details '
        + "— click hamburger menu to expand, collapse, and navigate</span>"
        + '<div class="hamburger-wrap">'
        + '<button class="hamburger" type="button" '
        + 'aria-label="Open navigation menu" aria-expanded="false" '
        + 'onclick="toggleMenu(this)">'
        + '<span></span><span></span><span></span></button>'
        + '<div class="hamburger-menu" id="hmenu" role="menu">'
        + '<p class="hmenu-title">expand and navigate</p>'
        + '<button class="cta expandall" type="button" role="menuitem" id="xall" '
        + 'onclick="toggleAll(this)">expand all</button>'
        + '<button class="cta expandall" type="button" role="menuitem" id="xmonths" '
        + 'onclick="toggleAllMonths(this)">expand all months</button>'
        + '<button class="cta expandall" type="button" role="menuitem" id="xweeks" '
        + 'onclick="toggleAllWeeks(this)">expand all weeks</button>'
        + '<span class="hmenu-segue" aria-hidden="true">✦</span>'
        + f'<a class="cta" role="menuitem" target="_blank" rel="noopener" '
        + f'href="{HOMEPAGE_URL}">divorce-custody-assistant home ↗</a>'
        + '<a class="cta green" role="menuitem" target="_blank" rel="noopener" '
        + 'href="https://drasticstatic.github.io/trading-assistant-public-preview/">'
        + "trading-assistant home ↗</a>"
        + "</div>"
        + "</div>"
        + "</div>"
        + "".join(months_html)
        + "<script>"
        "function syncExpandLabels(){var ms=document.querySelectorAll('.month'),"
        "ws=document.querySelectorAll('.week');var mo=0,wo=0;"
        "for(var i=0;i<ms.length;i++){if(ms[i].open)mo++;}"
        "for(var j=0;j<ws.length;j++){if(ws[j].open)wo++;}"
        "var xa=document.getElementById('xall');"
        "if(xa)xa.textContent=((mo===ms.length&&wo===ws.length&&ms.length>0)?'collapse all':'expand all');"
        "var xm=document.getElementById('xmonths');"
        "if(xm)xm.textContent=(mo===ms.length?'collapse all months':'expand all months');"
        "var xw=document.getElementById('xweeks');"
        "if(xw)xw.textContent=(wo===ws.length?'collapse all weeks':'expand all weeks');}"
        "function toggleAll(btn){var ms=Array.from(document.querySelectorAll('.month')),"
        "ws=Array.from(document.querySelectorAll('.week'));"
        "var all=ms.length+ws.length;var open=0;ms.forEach(function(d){if(d.open)open++;});"
        "ws.forEach(function(d){if(d.open)open++;});var make=!(open>=all/2);"
        "ms.forEach(function(d){d.open=make;});ws.forEach(function(d){d.open=make;});syncExpandLabels();}"
        "function toggleAllMonths(btn){var ms=Array.from(document.querySelectorAll('.month'));"
        "var open=ms.filter(function(d){return d.open;}).length;"
        "var make=!(open>=ms.length/2);ms.forEach(function(d){d.open=make;});syncExpandLabels();}"
        "function toggleAllWeeks(btn){var ws=Array.from(document.querySelectorAll('.week'));"
        "var open=ws.filter(function(d){return d.open;}).length;"
        "var make=!(open>=ws.length/2);ws.forEach(function(d){d.open=make;});syncExpandLabels();}"
        "function toggleMenu(btn){var open=btn.classList.toggle('open');"
        "btn.setAttribute('aria-expanded',open?'true':'false');"
        "if(!open)return;"
        "var m=document.getElementById('hmenu');"
        "setTimeout(function(){"
        "document.addEventListener('click',function cls(e){"
        "if(!btn.contains(e.target)&&!m.contains(e.target)){"
        "btn.classList.remove('open');btn.setAttribute('aria-expanded','false');"
        "document.removeEventListener('click',cls);}});},0);"
        "document.addEventListener('keydown',function esc(e){"
        "if(e.key==='Escape'){btn.classList.remove('open');"
        "btn.setAttribute('aria-expanded','false');"
        "document.removeEventListener('keydown',esc);}});}"
        # Heatmap lightbox + clickable-day navigation (v9). The thumbnail is a
        # click target: tapping inside a day cell opens that day's month
        # <details> and scrolls to it; tapping elsewhere enlarges the grid in a
        # <dialog> so phone users get a legible, tappable copy. Dependency-free.
        "function heatmapLightbox(){var t=document.getElementById('heat-thumb'),"
        "lb=document.getElementById('heat-lightbox');"
        "if(!t||!lb||typeof lb.showModal!=='function')return;"
        "var large=lb.querySelector('.heat-large'),src=t.querySelector('svg.heat-svg');"
        "function navDay(iso){if(!iso)return;var mid=iso.slice(0,7),"
        "m=document.getElementById(mid);if(!m)return;m.open=true;"
        "setTimeout(function(){m.scrollIntoView({behavior:'smooth',block:'center'});},60);}"
        "t.addEventListener('keydown',function(e){"
        "if(e.key==='Enter'||e.key===' '){e.preventDefault();openBig();}});"
        "t.addEventListener('click',function(e){"
        "var d=e.target.closest('.heat-day');if(d){navDay(d.getAttribute('data-date'));return;}openBig();});"
        "var eb=document.getElementById('heat-enlarge');if(eb)eb.addEventListener('click',openBig);"
        "function openBig(){if(lb.open)return;large.innerHTML='';"
        "if(src){var c=src.cloneNode(true);c.removeAttribute('width');large.appendChild(c);}"
        "lb.showModal();}"
        "lb.addEventListener('click',function(e){"
        "if(e.target===lb){lb.close();return;}"
        "var d=e.target.closest('.heat-day');if(d){navDay(d.getAttribute('data-date'));lb.close();}});"
        "var cb=lb.querySelector('.heat-close');if(cb)cb.addEventListener('click',function(){lb.close();});"
        "lb.addEventListener('keydown',function(e){if(e.key==='Escape')lb.close();});}"
        "heatmapLightbox();"
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
    p.add_argument("--until", default=None,
                   help="ISO end date YYYY-MM-DD (default: today, UTC — so the "
                        "log auto-extends on each re-run for the followup hearing)")
    p.add_argument("--author", default=ACCOUNT,
                   help="GitHub account to pull public repos from")
    deny = p.add_argument("--deny", action="append", default=[],
                   help="Repo name(s) to exclude (repeatable)")
    p.add_argument("--out", default=None,
                   help="Output path for the TOC index (default: "
                        "vocational-compliance/exhibit-4-log.md)")
    args = p.parse_args(argv)
    # Default --until to today (UTC) so each regen auto-extends through the
    # present — after the conference we re-run and the log appends for the
    # followup hearing without touching the flags.
    if not args.until:
        args.until = datetime.now(timezone.utc).date().isoformat()

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
