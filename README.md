# 🔏 Divorce & Custody Assistant ⛓️‍💥

> Privacy-first, AI-assisted case management for pro se litigation support

<p align="left"><a href="https://drasticstatic.github.io/divorce-custody-assistant-public-preview/"><img src="https://img.shields.io/badge/%F0%9F%8C%90%20Public%20Preview-Configured-brightgreen" alt="Public Preview"></a> <a href="https://github.com/open-condo-software/gitexporter"><img src="https://img.shields.io/badge/Synced%20via-GitExporter-blue" alt="Synced via GitExporter"></a> <a href="https://code.claude.com/docs/en/overview"><img src="https://img.shields.io/badge/Built%20with-Claude%20Code%20CLI-blueviolet" alt="Built with Claude Code CLI"></a> <a href="https://build.nvidia.com/"><img src="https://img.shields.io/badge/Powered%20by-NVIDIA%20NIM-76b900" alt="NVIDIA NIM"></a> <a href="https://github.com/drasticstatic/divorce-custody-assistant/actions/workflows/sync-public.yml"><img src="https://github.com/drasticstatic/divorce-custody-assistant/actions/workflows/sync-public.yml/badge.svg" alt="Sync"></a></p>

---

**🌐 [Explore the Public Preview →](https://drasticstatic.github.io/divorce-custody-assistant-public-preview/)** &nbsp;&nbsp;<big>·&nbsp;&amp;&nbsp;·</big>&nbsp;&nbsp; [👀 View Sample Marp Deck 📰](https://drasticstatic.github.io/divorce-custody-assistant-public-preview/divorce-palette-sample.marp.html)

---

> 🔒 Public mirror notice: This repository is partially mirrored as a public preview of the private source via an automated GitExporter pipeline. The public version includes this README and other files made available.

> Note for visitors: The working repository stays private, and the public preview intentionally excludes any proprietary content, internal specs, agent coordination files, startup instructions, workflow config, and any runtime-loaded case material.

## What this project is for

This repository is for building a privacy-conscious legal workflow assistant that helps organize and prepare casework without publishing sensitive case details. Planned capabilities include:

- document intake and classification
- custody-factor evidence mapping
- filing and deadline tracking
- financial exposure modeling
- judge-ready narrative and exhibit preparation
- cross-examination rehearsal

## Current status

**In-progress** - the public preview is intentionally limited while the private working repository remains the source of truth

## Public preview boundary

The public mirror is automated from the private repo, but private-by-default rules apply:

- new root directories are treated as private until explicitly classified for export
- case documents, filings, evaluations, correspondence, and other runtime-loaded local sources are never committed to the public mirror and if applicable, and if not already, they will be filed with the prothonotary and entered in as exibits.

## Agent roles

Built and maintained with **Anthropic's Claude** (Claude Code CLI + NVIDIA NIM).

**Alfred** is the primary operator for this workspace — running in both Anthropic (full quality) and NVIDIA NIM (free-tier, for research and housekeeping) modes. Alfred handles infrastructure, git ops, AGENT-SYNC coordination, session pickups, and anything that doesn't require deep case context.

**🌐 [Who Is Alfred? →](https://drasticstatic.github.io/anthropas-argus-alfred-public-preview/)** &nbsp;&nbsp;<big>·&nbsp;&amp;&nbsp;·</big>&nbsp;&nbsp; [👀 View Sample Marp Deck 📰](https://drasticstatic.github.io/anthropas-argus-alfred-public-preview/alfred-palette-sample.marp.html)

**Fortuna** is called in when tasks require case strategy, document review, financial modeling, negotiation prep, or legal depth. Fortuna uses Anthropic by default for case-sensitive work; NIM is available for non-sensitive drafts and research.

**🌐 [Who Is Fortuna? →](https://drasticstatic.github.io/trading-assistant-public-preview/)** &nbsp;&nbsp;<big>·&nbsp;&amp;&nbsp;·</big>&nbsp;&nbsp; [👀 View Sample Marp Deck 📰](https://drasticstatic.github.io/trading-assistant-public-preview/setup/trading-palette-sample.marp.html)

## Public-safe principle

This mirror is for sharing structure, automation patterns, and explicitly approved public-facing materials only. It is not a publication channel for sensitive legal records or repo-internal coordination artifacts

---

## Recent developments

### Vocational compliance log (Exhibit 4)

A `vocational-compliance/` suite translates real, public software-development and quantitative-trading work into the formal categories a domestic-relations work-search order expects ("hours of effort," "job contacts," "vocational activity"). It is **generated, not hand-edited** — `build_vocational_log.py` queries the maintainer's public repositories (and the `-public-preview` / `-public` mirrors of private repos) in one reproducible pass, so there is never a gap between what the log claims and what the public commit record shows.

The generator emits three cross-linked artifacts:

- **`exhibit-4-log.md`** — the table-of-contents index (journey summary, aggregate totals, and monthly links)
- **`exhibit-4-log-YYYY-MM.md`** — one per-month weekly log, each fileable as a standalone date-range exhibit
- **`exhibit-4.html`** — an interactive accordion version of the full record, served live on GitHub Pages

Every row carries a **full** commit URL (not abbreviated) so a printed or PDF copy — filed with the prothonotary — lets a reader type the link into a browser. Each artifact cross-links to the others and back to the public-preview homepage. The directory also carries `overview.md`, `journey-context.md`, and `reporting-context.md` sidecars that frame the methodology, the pre-2026 classroom→portfolio arc, and the known reporting gaps.

**Honesty contract:** every row derives from a real attributable public commit (no padding), only the maintainer's known GitHub identities are counted, commit subjects are sanitized before quoting (emails, hex tokens, and case-number patterns stripped), and commits that touched only private paths never surface (they are pruned by the sync pipeline).

### Landing page redesign

The public-preview landing (`index.html`) was rebuilt as an intentional-minimal framing page that embeds the interactive Exhibit 4, exposes the related records as GitHub blob links, and carries a small mercy-themed modal. A custom `404.html` now returns a hard GitHub Pages 404 for any pruned or never-published path (previously these rendered the default Jekyll soft-404 placeholder at HTTP 200).

### Interactive contribution heatmap & exhaustive Exhibit 1–3 companions

Exhibit 4's centerpiece is now a **GitHub-style contribution heatmap** rendered from the same attribution data as the log — a clickable full-year SVG thumbnail that opens a fullscreen lightbox via an enlarge button (or by tapping any day). Each day carries category-colored dots for the eight activity classes plus a teal trading-day marker; clicking a day jumps straight to that week's recorded entry in the log below. Desktop visitors get a hover tooltip; mobile visitors get a rotate-for-best-view hint, and an on-page color key rolls the eight categories up so a printed or PDF copy stays legible without the live site.

The three companion exhibits that frame Exhibit 4 were rewritten as **exhaustive public companions** rather than stubs, each describing its document's role and structure only — no private figures, account balances, or case-specific detail are published:

- **Exhibit 1 — Vocational Pivot & Good-Faith Work Search:** the structural argument — liquid-capital exhaustion, a contractually-allocated internal offset that clears the arrears to a zero balance, and a 40+ hour/week retraining schedule across four live technical-trading programs (each with its published weekly cadence) — followed by a redefinition of "good-faith work search" for the modern web3 / DAO-grant economy, where verifiable commits and deployments replace the résumé-and-application loop.
- **Exhibit 2 — Trader Tax Status & Profit Motive:** a briefing memorandum on the controlling standard (IRC §183 hobby-loss rules and trader-tax-status factors) and how an attributable, timestamped public record defeats a willful-underemployment posture.
- **Exhibit 3 — Income & Guidelines Expense Statement:** the economic reference point, plus a formal Prayer Request for Special Relief asking the Court to recognize the documented operational insolvency, accept the structural offset as the good-faith compliance path, and accept Exhibit 4 as a valid work-search equivalent during the pre-revenue launch phase.

The landing page exposes these as dark-blue navigation pills alongside the Exhibit 4 embed, and a hard guard keeps the escaped `<iframe>` text token inert — it appears as text exactly twice and never resolves to a real element — so the embedded viewer cannot swallow the rest of the page. The "meet-the-developer" modal was likewise polished: Alfred's third-person review sits in a cool blue-grey, with the closing signature set in calligraphy.

---

## Google Workspace CLI (`gws`) setup — sterilized overview

This workspace uses the `gws` CLI to talk to a dedicated, isolated Google account for case correspondence, court documents, and legal filings. The local setup guide (`GWS_SETUP.md`, kept private) walks through the one-time configuration; this README documents only the **mechanism**, so the pattern is reusable without exposing any account identifiers or document IDs.

**Multi-account architecture.** The machine runs several isolated `gws` profiles — one per Google account / repo context. Each profile gets a shell alias of the form `gws<abbrev>` (the abbreviation denotes the project) so the account is always explicit at the command line and a bare `gws` is never used. Aliases include one for this repo's account and one for a separate devine-news automation project; each alias sets a per-profile `GOOGLE_WORKSPACE_CLI_CONFIG_DIR` so credentials and token caches never cross accounts.

**One-time setup (the documented flow).** For each account: create an OAuth 2.0 **Desktop app** credential inside a dedicated GCP project, enable the Workspace APIs the account needs, drop the downloaded `client_secret.json` into the profile's config directory (gitignored), add the account as a **test user** on the OAuth consent screen, and run `gws auth login` through the alias to complete the OAuth flow in the browser. The token is stored encrypted in the config dir and never touches the repository.

**Drive API vs. Docs API — the key distinction.** The **Drive API** can *create* a Google Doc by uploading content with the Google Doc mime type, but it cannot read or modify the *contents* of an existing doc. The **Docs API** (`documents.get`, `documents.batchUpdate`) is required for any in-place content editing — inserting text, filling tables, replacing placeholders. Profiles scoped to drafting-only get away with Drive alone; profiles that need to edit existing shared docs require the Docs API enabled.

**Privacy model.** Config directories are local-only — never synced, never committed. Profiles are strictly isolated from one another by config dir, GCP project, and OAuth client. Anything accessed through `gws` stays local; per the security rules nothing case-specific is committed to this repo. The full step-by-step guide lives in `GWS_SETUP.md` in the private working repository alongside the example commands for read/write Drive, Docs, and Gmail operations.

