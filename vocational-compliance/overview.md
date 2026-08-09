# Vocational Compliance Log — Overview & "Why"

> A concise, navigable companion to the
> [Weekly Vocational Activity & Work-Search Log](https://github.com/drasticstatic/divorce-custody-assistant-public-preview/blob/main/vocational-compliance/exhibit-4-log.md).

---

## What this is

This directory publishes a **public, attributable record** of technical
product-development work — software engineering, quantitative trading, and
Web3/blockchain infrastructure — translated into the formal categories a
Domestic Relations work-search order expects ("job contacts," "hours of
effort," "vocational activity").

It exists to make one argument, honestly and in public:

> In the modern software / Web3 / quantitative-trading sector, a developer's
> verifiable GitHub commit history **is** the work-search record. Forcing a
> senior-grade technologist into non-technical, low-wage labor to "log
> contacts" does not maximize earning capacity; it permanently devalues it.
> This log translates the real, public labor that **is** the career-building
> activity into the audit-ready shape the order asks for.

---

## Why it is public

Visibility is the evidence, not a side effect.

In decentralized engineering markets, technical competency, independent
contractor payouts, and developer grants are secured through **verified
public commits, live protocol deployments, open-source contributions, and
prop-firm evaluation combines.** A static, timestamped, attributable commit
history across public repositories is the medium of that evidence. A
side-channel, private log of "hours spent" carries none of that weight.

Publishing it on GitHub Pages (served raw off `main` via a privacy-preserving
sync pipeline) means every row is independently verifiable by any reviewing
officer — the proof links resolve straight to `github.com`.

---

## How the log is built (methodology)

The log is **generated, not hand-edited** — `build_vocational_log.py` pulls
real commits in one reproducible pass and regenerates the markdown. This keeps
the artifact honest: there is no gap between "what the log claims" and "what
the public commit record shows."

### Honesty contract (non-negotiable)

1. **Every row comes from a real public commit** with a verifiable proof link
   that resolves on `github.com`. No padding, no fabricated activity.
2. **Public-only by construction.** The generator queries only the
   maintainer's public repositories (originally-public repos plus the
   `-public-preview` / `-public` mirrors of private repos). Commits that
   touched only private paths are pruned by the sync's `git filter-repo` step,
   so they correctly do **not** appear. That is the desired behavior: only
   attributable, on-the-record work surfaces.
3. **Attribution is filtered.** Only commits attributable to the maintainer's
   known GitHub identities are counted; another contributor's work is never
   claimed. SHA rewriting by the filter pipeline is handled correctly — links
   always point at the **public** repo's commit SHA, never the private one.
4. **Commit subjects are sanitized** before quoting: emails, long hex tokens,
   `key=`-style secret assignments, and docket/case-number patterns are
   stripped so nothing sensitive leaks through a quoted message line.

### Equivalence rubric

A single commit does **not** equal one job contact. Each commit is classified
by activity category (keyword match over repo name + message), and each
category carries an equivalence — "hours" of product development or "actions"
of job-search equivalent. A final category, **Trading**, is sourced from
external Tradovate and TradeZella trade-history CSVs (digested via the
separate trading-assistant repo) rather than from the commit record, so time
on the charts is visible even on days with no commits. Futures prop-firm
sessions run Sunday 18:00 to Friday 17:00 EST; crypto is managed around the
clock, with an attempted daily break from 17:00–18:00:

| Activity Category | Equivalence | What it represents |
|---|---|---|
| Code Deployment | 6 hrs | Technical infrastructure / production releases / portfolio architecture |
| Risk Evaluation | 8 hrs | Quantitative compliance audits / security verification / behavioral case studies / sandbox frameworks / sophisticated safeguards |
| Retraining Milestone | 4 hrs | Vocational skill advancement / curriculum mastery / applied self-study |
| Technical Outreach | 2 actions | Direct business development / employer-client engagement / lead generation |
| Beta-Testing & Calibration | 5 hrs | System integration / QA / product optimization / performance tuning |
| Audit / Education | 3 hrs | Performance assessments / codebase auditing / peer-coach dissection |
| Product Management (default) | 4 hrs | Full-stack engineering / innovation / startup labor / platform builds / MVP iterations |
| Trading | session hrs | Live futures session screen-time / chart dedication / discretionary model stress testing / systematic strategy analysis / proprietary combine execution |

The compliance target shown per week (8 attributable actions) is **context**,
not a fabricated count — the log shows what actually happened, then surfaces
the aggregate so a reviewer can see the real shape of the labor.

### Contributions heatmap

The interactive export (`exhibit-4.html`) opens with a year-at-a-glance
**Contributions Heatmap** so a reviewer can see the cadence of the labor
before opening any month. Every calendar day in the reporting window carries
blue shading — a floor level of attestable daily-activity **context** (crypto
is managed around the clock, so no day reads as blank), deepening with the
number of attributable commits that day. A small **colored dot** marks each
activity category hit that day (color = the legend key), so the category mix
reads at a glance without partitioning the square. A **green dot** marks a
trading session — a *placeholder* scheduled session until the verified
Tradovate/TradeZella CSVs land (digested via the trading-assistant repo), then
a *verified* session carrying real hours. The distinction is kept honest in
`reporting-context.md`: blue shading is attestable context, not a verified
commit claim; the dots are the verifiable markers.

### Reproducibility

```bash
# Regenerate the full-year log (monthly files + TOC index + HTML accordion):
python3 vocational-compliance/build_vocational_log.py \
    --since 2026-01-01 --until 2026-08-10
```

The generator writes a **table-of-contents index** (`exhibit-4-log.md` —
journey summary + aggregate + monthly links), one **per-month file**
(`exhibit-4-log-YYYY-MM.md`, each fileable as a standalone date-range exhibit),
and an **interactive accordion export** (`exhibit-4.html`) — all
cross-linked to each other and back to the public-preview homepage. To extend
the reporting period, change the `--since` / `--until` flags and re-run. The
output is always a faithful snapshot of the stated range — nothing is silently
appended.

---

## The legal framework it supports (public-facing summary)

This log accompanies a formal memorandum filed with Domestic Relations. The
memorandum (filed version retains all case-specific detail) makes two points
this artifact operationalizes:

1. **Trader / business profit-motive, not a hobby.** Under IRC §183 (hobby-loss
   rules) and the federal Trader Tax Status standard, sustained, systematic,
   substantial-investment activity undertaken with intent to profit is a
   legitimate pre-revenue **startup business**, not casual investing. The
   public commit record on these pages is direct evidence of the
   "continuous, regular, and systematic" activity that standard requires.

2. **Good-faith capacity maximization, not willful underemployment.** Under
   Pennsylvania family law, earning capacity — not a forced low-wage
   placement — governs support. A good-faith, intensive retraining and
   startup-launch pivot designed to *restore* a high baseline earning capacity
   is the opposite of evasion. Forcing the work into non-technical channels
   would permanently impair the very capacity the support obligation depends
   on. This log is the proof that the pivot is real, ongoing, and measurable.

> **Scope note:** This public overview deliberately omits all case-specific
> identifiers — names, case numbers, addresses, dollar figures, and the
> specifics of any marital agreement. Those live in the filed memorandum. What
> remains here is the reusable **structure and methodology**, so that another
> technologist facing a work-search order during a pre-revenue startup phase
> can adapt it as a template.

---

## Using this as a template

If you are a developer / trader whose real labor *is* public commit work and
you need to evidence it for a vocational or work-search compliance review:

1. **Fork the `vocational-compliance/` directory** into your own
   public-preview repo.
2. **Set `KNOWN_AUTHOR_IDENTITIES`** in `build_vocational_log.py` to **your**
   GitHub login(s) so only your attributable commits are counted.
3. **Tune `CATEGORY_RUBRIC`** keywords to match your work's vocabulary
   (e.g. swap trading terms for embedded/ML/devops terms).
4. **Adjust the `--since` / `--until`** window to your reporting period.
5. **Publish via a privacy-preserving pipeline** (allowlist-style filter so
   private repos never leak). See `my-template/workflow-templates/` for the
   canonical `sync-public.yml` pattern.
6. Keep the **honesty contract**: never pad. The history is the exhibit.

---

## How AI tooling helps with this predicament

This kind of compliance artifact is unusual: it asks someone who is already
working full-time at a technical pivot to *also* stop and prove, in formal
legal shape, that the labor they are already doing **is** the work-search
activity. For a pro se litigant who is simultaneously a technologist, that's a
near-impossible documentation burden done by hand. Two classes of tool make it
tractable:

- **A coding-agent CLI (Claude Code CLI).** The log above — including the
  generator, the equivalence rubric, the privacy-safe sanitization, and the
  regenerable pipeline that ties it to a public-preview commit record — was
  built, iterated, and documented collaboratively with a coding agent in the
  terminal. The agent reads the source repos, drafts the legal-adjacent prose,
  and operationalizes "verifiable public record" into an actual repeatable
  build. The human stays the author and the sworn declarant; the agent is the
  scaffolding that makes producing the evidence realistic while the human keeps
  doing the underlying work.

- **A screen-awareness assistant (Littlebird).** When memory of *which* task
  happened *when* is the gap — especially across a stretch of unpaid,
  non-GitHub labor (infra overhauls, contract work, trading sessions not yet
  pushed) — a local, on-device screen-awareness assistant that observed the
  work in real time can be consulted to confirm dates and tasks rather than
  reconstructing them from memory. That keeps the backfill honest: the dates
  are corroborated by what the machine actually saw, not by what a person hopes
  they remember under a deadline.

Together these tools do not manufacture evidence — they make **genuine**
evidence producible. The honesty contract in this log (real commits, real
proof links, no padding) is what keeps the assistance legitimate rather than
self-undermining. For anyone else in this predicament — capable, working, but
needing to *show* it in a shape a court recognizes — the same pattern applies:
let the agent build the repeatable evidence pipeline, let screen-awareness
corroborate the parts with no commit trail, and stay the sworn author of the
result.

---

## Files in this directory

| File | Purpose |
|---|---|
| [`exhibit-4-log.md`](https://github.com/drasticstatic/divorce-custody-assistant-public-preview/blob/main/vocational-compliance/exhibit-4-log.md) | Table-of-contents index — journey summary + aggregate + monthly links (the entry point) |
| [`exhibit-4.html`](https://drasticstatic.github.io/divorce-custody-assistant-public-preview/vocational-compliance/exhibit-4.html) | Interactive accordion export (live web surface) |
| `exhibit-4-log-YYYY-MM.md` | Per-month vocational logs — each fileable as a separate date-range exhibit |
| [`overview.md`](https://github.com/drasticstatic/divorce-custody-assistant-public-preview/blob/main/vocational-compliance/overview.md) | This file — the framework & template guide |
| [`journey-context.md`](https://github.com/drasticstatic/divorce-custody-assistant-public-preview/blob/main/vocational-compliance/journey-context.md) | Pre-2026 classroom→portfolio narrative (injected into the TOC index) |
| [`reporting-context.md`](https://github.com/drasticstatic/divorce-custody-assistant-public-preview/blob/main/vocational-compliance/reporting-context.md) | Known reporting gaps & context (injected into the TOC index) |
| [`build_vocational_log.py`](https://github.com/drasticstatic/divorce-custody-assistant-public-preview/blob/main/vocational-compliance/build_vocational_log.py) | The reproducible generator |
| [`trading-days.csv.example`](https://github.com/drasticstatic/divorce-custody-assistant-public-preview/blob/main/vocational-compliance/trading-days.csv.example) | Tradovate + TradeZella trading-session ingestion template — copy to `trading-days.csv` (or flow verified CSVs in via the trading-assistant repo) to flip the heatmap overlay from placeholder to verified |

---

## Verification

The log is generated from independently-verifiable public data. Sworn
verification language and signatures rest with the filed memorandum; this
public artifact lets any reviewer trace every claimed hour or action back to
a real, timestamped, attributable commit without taking anyone's word for it.

---

*Generated and maintained as part of a public technical-vocational record.
Regenerable at any time from the public commit record.*
