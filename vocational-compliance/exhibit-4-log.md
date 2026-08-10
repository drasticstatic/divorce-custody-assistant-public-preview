# Exhibit 4 — Vocational Status & Tech Work-Search Log

**Maintainer:** drasticstatic  
**Reporting period:** 2026-01-01 → 2026-08-10  
**Generated:** 2026-08-10 (regenerable via `vocational-compliance/build_vocational_log.py`)  
**Public commits attributed in range:** 1026  
**Active development weeks:** 26 / 33  
**Aggregate equivalence:** 4618 product development hours · 30 job-search actions  

---

## What this is

An audit-ready translation of real, public software-development and quantitative-trading work into the formal categories requested by a Domestic Relations work-search order. Every row derives from a verifiable commit on a public repository belonging to the maintainer; the proof links resolve directly to `github.com`. Commits that touched only private paths are intentionally absent — the privacy-preserving sync pipeline prunes them, so this log shows only attributable, on-the-record work.

This file is the **table of contents** index. The dated weekly detail lives in one file per month (each fileable as a separate date-range exhibit); an interactive accordion view is served on GitHub Pages.

- [`overview.md`](https://github.com/drasticstatic/divorce-custody-assistant-public-preview/blob/main/vocational-compliance/overview.md) — concise framework behind this exhibit
- [`journey-context.md`](https://github.com/drasticstatic/divorce-custody-assistant-public-preview/blob/main/vocational-compliance/journey-context.md) — the pre-2026 classroom → product → portfolio arc (below)
- [`reporting-context.md`](https://github.com/drasticstatic/divorce-custody-assistant-public-preview/blob/main/vocational-compliance/reporting-context.md) — known reporting gaps in this period
- `exhibit-4-log-YYYY-MM.md` — one per-month file (e.g. [`exhibit-4-log-2026-07.md`](https://github.com/drasticstatic/divorce-custody-assistant-public-preview/blob/main/vocational-compliance/exhibit-4-log-2026-07.md))
- [exhibit-4.html](https://drasticstatic.github.io/divorce-custody-assistant-public-preview/vocational-compliance/exhibit-4.html) — interactive accordion view (live on GitHub Pages)
- [public-preview homepage](https://drasticstatic.github.io/divorce-custody-assistant-public-preview/)

## The journey behind this record (brief, pre-2026)

This compliance log opens on January 2026, but the labor it documents did not
begin then. The dated weekly entries below are the later chapter of an arc that
was already underway. This brief summary frames what came before, grounded in
the public repository record, so the dated log is read in its proper context.

**1. Classroom — the DappUniversity blockchain bootcamp (May – Sep 2025).**
The craft underlying this practice was built in an immersive
blockchain-developer bootcamp: smart-contract fundamentals, Hardhat workflows,
and the canonical capstones built in sequence:

| Created | Repository | Capstone |
|---|---|---|
| 2025-05-01 | `blockchain-developer-bootcamp`, `hardhat_example` | Course foundations, Hardhat tooling |
| 2025-05-17 | `crowdsale` | Token crowdsale contract |
| 2025-06-21 | `dao` | Decentralized autonomous organization |
| 2025-07-16 | `nft_dappu-punks` | NFT dapp |
| 2025-07-27 | `solidity_intensive` | Solidity intensive |
| 2025-09-21 | `amm` | Automated market-maker |

These repos remain public on the maintainer's GitHub as the verifiable record
of the schooling. The `code-forked/` local working directory holds curated
working copies of upstream open-source projects studied and integrated into
the trading system (attribution below).

**2. First product + portfolio (May – Dec 2025).** The classroom met practice
early: the first product — a gratitude-token project (created 2025-05-25) — and
the first trading bot, an arbitrage dapp over the DappUniversity v3 curriculum
(`trading-bot_arbitrage_DAPPUv3_hardhat_UNI-CAKE`, created 2025-07-18). During
this phase the work was migrated off the local machine and onto GitHub Pages:
early publish experiments (the `gratitude-token-project_testPublish_*`
repositories of Oct 2025 and Jan 2026), a public docs surface
(`gratitude-token-project_docs`, 2025-10-09), local directory
reorganization, older work forked-and-curated, and a `resume` repository
(2025-12-12) anchoring the portfolio. The purpose of this phase was to make the
learning visible and attributable — the same honesty contract this compliance
record runs on.

**3. Practice — the startup pivot (Feb 2026 → present).** Classroom-to-product
at scale: the `trading-assistant` quantitative-trading platform (private
2026-02-21 → public-preview 2026-02-22), a personal developer portal
(`drasticstatic.github.io`, 2026-03-11), the multi-repo dev ecosystem, and a
cluster of market-data and automation MCP integrations stood up together at the
end of April 2026 (`tradingview-mcp-jackson`, `robinhood-mcp`, `hummingbot-mcp`,
`hummingbot-api`). This is the phase the weekly log below documents in
attributable, dated detail from January 2026 forward.

### Attribution — the `code-forked/` working set (curated upstream copies)

Not every repo in the record is authored from scratch. The `code-forked/`
directory holds curated working copies of upstream open-source projects that
were studied, integrated, and in some cases extended for the trading system.
Public attribution of those upstreams:

| Working copy (`drasticstatic/`) | Upstream | Purpose |
|---|---|---|
| `free-claude-code` | [`Alishahryar1/free-claude-code`](https://github.com/Alishahryar1/free-claude-code) | Anthropic-compatible proxy for NVIDIA NIM / DeepSeek / OpenRouter / Ollama (powers the multi-agent dev system) |
| `hummingbot` | [`hummingbot/hummingbot`](https://github.com/hummingbot/hummingbot) | Open-source crypto market-making / arbitrage bot engine |
| `hummingbot-mcp` | [`hummingbot/mcp`](https://github.com/hummingbot/mcp) | Model Context Protocol layer for the bot |
| `hummingbot-api` | [`hummingbot/hummingbot-api`](https://github.com/hummingbot/hummingbot-api) | Python REST/WebSocket client for the Hummingbot API server |
| `robinhood-mcp` | [`verygoodplugins/robinhood-mcp`](https://github.com/verygoodplugins/robinhood-mcp) | MCP layer for the Robinhood brokerage (equities/options market data) |
| `tradingview-mcp-jackson` | [`LewisWJackson/tradingview-mcp-jackson`](https://github.com/LewisWJackson/tradingview-mcp-jackson) | MCP layer for the TradingView desktop client (charting / signal flow) |

The maintainer's value-add is the integration, configuration, trading-strategy
work, and the higher-order multi-agent system these plugs into — not the claim
of authoring the upstream libraries themselves. The upstream repos are linked
above so attribution is explicit and verifiable.

> **On dating.** The classroom capstones were migrated to GitHub after the
> instruction; their repository *creation* dates above post-date the actual
> coursework. What is certain and verifiable: the practice this compliance
> record evidences did not begin on January 1, 2026 — it is the harvest of an
> intensive classroom → product → portfolio arc that was in motion through all
> of 2025.

The repos named above are independently verifiable on the maintainer's public
GitHub profile at `https://github.com/drasticstatic` (the private product repos
each have a public `-public-preview` or `-public` mirror, which is the lane the
dated log below counts).

---

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

---

## Monthly index

| Month | Per-month exhibit (blob) | Interactive view | Commits | Hours-equiv | Actions-equiv |
|---|---|---|---|---|---|
| January 2026 | [`exhibit-4-log-2026-01.md`](https://github.com/drasticstatic/divorce-custody-assistant-public-preview/blob/main/vocational-compliance/exhibit-4-log-2026-01.md) | [exhibit-4.html#2026-01](https://drasticstatic.github.io/divorce-custody-assistant-public-preview/vocational-compliance/exhibit-4.html#2026-01) | 36 | 171 | 0 |
| February 2026 | [`exhibit-4-log-2026-02.md`](https://github.com/drasticstatic/divorce-custody-assistant-public-preview/blob/main/vocational-compliance/exhibit-4-log-2026-02.md) | [exhibit-4.html#2026-02](https://drasticstatic.github.io/divorce-custody-assistant-public-preview/vocational-compliance/exhibit-4.html#2026-02) | 63 | 311 | 0 |
| March 2026 | [`exhibit-4-log-2026-03.md`](https://github.com/drasticstatic/divorce-custody-assistant-public-preview/blob/main/vocational-compliance/exhibit-4-log-2026-03.md) | [exhibit-4.html#2026-03](https://drasticstatic.github.io/divorce-custody-assistant-public-preview/vocational-compliance/exhibit-4.html#2026-03) | 243 | 1099 | 2 |
| April 2026 | [`exhibit-4-log-2026-04.md`](https://github.com/drasticstatic/divorce-custody-assistant-public-preview/blob/main/vocational-compliance/exhibit-4-log-2026-04.md) | [exhibit-4.html#2026-04](https://drasticstatic.github.io/divorce-custody-assistant-public-preview/vocational-compliance/exhibit-4.html#2026-04) | 350 | 1582 | 18 |
| May 2026 | [`exhibit-4-log-2026-05.md`](https://github.com/drasticstatic/divorce-custody-assistant-public-preview/blob/main/vocational-compliance/exhibit-4-log-2026-05.md) | [exhibit-4.html#2026-05](https://drasticstatic.github.io/divorce-custody-assistant-public-preview/vocational-compliance/exhibit-4.html#2026-05) | 267 | 1163 | 8 |
| June 2026 | [`exhibit-4-log-2026-06.md`](https://github.com/drasticstatic/divorce-custody-assistant-public-preview/blob/main/vocational-compliance/exhibit-4-log-2026-06.md) | [exhibit-4.html#2026-06](https://drasticstatic.github.io/divorce-custody-assistant-public-preview/vocational-compliance/exhibit-4.html#2026-06) | 29 | 128 | 0 |
| July 2026 | [`exhibit-4-log-2026-07.md`](https://github.com/drasticstatic/divorce-custody-assistant-public-preview/blob/main/vocational-compliance/exhibit-4-log-2026-07.md) | [exhibit-4.html#2026-07](https://drasticstatic.github.io/divorce-custody-assistant-public-preview/vocational-compliance/exhibit-4.html#2026-07) | 34 | 147 | 0 |
| August 2026 | [`exhibit-4-log-2026-08.md`](https://github.com/drasticstatic/divorce-custody-assistant-public-preview/blob/main/vocational-compliance/exhibit-4-log-2026-08.md) | [exhibit-4.html#2026-08](https://drasticstatic.github.io/divorce-custody-assistant-public-preview/vocational-compliance/exhibit-4.html#2026-08) | 4 | 17 | 2 |

---

## Verification

I certify that the foregoing weekly vocational and software-development work log is true, accurate, and reflects active, full-time labor toward restoring financial capacity. Each row is traceable to a public commit via its proof link. Perjury language and sworn signatures are carried in the filed memorandum, not in this public-facing artifact.

---

*This file is regenerated, not hand-edited. To extend the reporting period, change the `--since` / `--until` flags in `build_vocational_log.py` and re-run.*
