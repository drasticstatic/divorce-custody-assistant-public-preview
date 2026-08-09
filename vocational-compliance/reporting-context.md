## Reporting context & known gaps

The log below counts only **attributable, public** commits — work that has
already surfaced on a public repository. Two things shape the record and
should be read alongside the empty or light weeks, so they are not mistaken
for inactivity:

### 1. Trading-development backlog (to be published and backdated)

A substantial body of quantitative-trading work — proprietary-combine
evaluations, daily market briefs, risk calibrations, and bot maintenance —
accumulated during this reporting period but was not yet pushed to the
public-facing repositories. That backlog is being published incrementally and
will be reflected in subsequent regenerations of this log (backdated to the
dates the work was actually performed, preserving attributable history).

### 2. Non-GitHub labor during the mid-May → mid-June window

During the mid-May through mid-June window, technical labor was directed at a
**non-profit web-infrastructure overhaul** rather than at repos that produce
public commits. Specifically: modernizing the back-end, front-end, and
server-side of the
**[Psychedelics In Recovery™](https://www.psychedelicsinrecovery.org) (PIR®)**
fellowship's web presence — WordPress, WPX hosting, SiteGround, subdomains,
and their integrations with Zoom, Google, WhatsApp, and related tooling — a
system that had been neglected for lack of service before this work was
volunteered. This is legitimate, full-time technical labor; it simply does
not generate attributable public commit events, which is why that stretch of
weeks shows no rows here. It is logged as context, not counted toward the
equivalence totals (which by design count only verifiable public commits).

### 3. Screen-awareness backfill (Littlebird, alongside Fortuna's Tradelog)

To make the backfill accurate rather than reconstructed from memory,
**Littlebird** — an on-device screen-awareness assistant that observed the work
in real time — will be consulted to confirm dates and tasks before the gap is
closed. That review is pending; until then, this note stands as an honest
marker that the window contained active labor awaiting its attributable record.

The Littlebird back-dating is scheduled to be completed alongside **Fortuna's
Tradelog** work in the trading-assistant repo — the same effort that digests
the verified Tradovate and TradeZella session CSVs into this log's trading
overlay — so the non-GitHub labor (including the mid-May → mid-June
**Psychedelics In Recovery™ (PIR®)** web-infrastructure overhaul above) and the
verified trading sessions land in one coherent, corroborated backfill rather
than two separate guesses.

### 4. Trading-session overlay (heatmap)

The **Contributions Heatmap** carries a green trading overlay so that time
spent on the charts is visible even when no GitHub commit was pushed that day.
Two trading modes are reflected: **futures prop-firm sessions** run Sunday
18:00 to Friday 17:00 EST, and **crypto** is managed around the clock with an
attempted daily break from 17:00 to 18:00. A **green dot** marks a trading
session on the day it falls.

Each calendar day in the heatmap also carries **blue shading** and small
**colored category dots**, and an honesty distinction between them matters:

- **Blue shading** — *attestable daily-activity context.* Because crypto is
  managed around the clock, **every day carries at least some shading, and no
  day reads as blank**. The shading only deepens with the number of
  attributable public commits that day. This is honest **context**, **not a
  verified-commit claim** — a faintly-shaded day with no commits attests that
  activity happened, not that a verifiable public commit was pushed.
- **Colored category dots** — each activity category hit that day overlays a
  small dot in the legend's color, so the **category mix** reads at a glance
  (these *are* tied to attributable commits).
- **Green dot** — a **trading session**. Until the verified Tradovate and
  TradeZella trade-history CSVs are in, every session day shows a **placeholder
  green dot** (the hollow ring is retired so no day reads empty). This is a
  framework, **not a verified claim** — it shows where real session data will
  land once the CSVs are ingested. Once `vocational-compliance/trading-days.csv`
  (columns `date,hours,note`; see `trading-days.csv.example`) is present, the
  generator reads it and each matching day carries a **verified green dot** with
  the real session hours. Regeneration is one command: `python3
  vocational-compliance/build_vocational_log.py --since 2026-01-01`.

The Tradovate and TradeZella CSVs themselves are digested by the separate
**trading-assistant** repo (Fortuna) and flow into `trading-days.csv` here, so
the verified overlay is produced without exposing raw trading data in this
repo — only the daily session hours, as additive heatmap context.

Trading time is **displayed** on the heatmap as context — it is not folded into
the commit-derived equivalence totals in the tables (which by design count only
verifiable public commits), keeping the sworn equivalence numbers conservative
and the trading layer additive. When the CSVs arrive, the sessions become
verified evidence rather than a placeholder frame.
