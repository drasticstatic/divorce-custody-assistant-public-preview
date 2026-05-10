# Divorce & Custody Assistant

> Privacy-first, AI-assisted case management for pro se litigation support

<p align="left"><a href="https://drasticstatic.github.io/divorce-custody-assistant-public-preview/"><img src="https://img.shields.io/badge/%F0%9F%8C%90%20Public%20Preview-Configured-brightgreen" alt="Public Preview"></a> <a href="https://github.com/open-condo-software/gitexporter"><img src="https://img.shields.io/badge/Synced%20via-GitExporter-blue" alt="Synced via GitExporter"></a> <a href="https://code.claude.com/docs/en/overview"><img src="https://img.shields.io/badge/Built%20with-Claude%20Code%20CLI-blueviolet" alt="Built with Claude Code CLI"></a> <a href="https://build.nvidia.com/"><img src="https://img.shields.io/badge/Powered%20by-NVIDIA%20NIM-76b900" alt="NVIDIA NIM"></a></p>

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

**Fortuna** is called in when tasks require case strategy, document review, financial modeling, negotiation prep, or legal depth. Fortuna uses Anthropic by default for case-sensitive work; NIM is available for non-sensitive drafts and research.

## Public-safe principle

This mirror is for sharing structure, automation patterns, and explicitly approved public-facing materials only. It is not a publication channel for sensitive legal records or repo-internal coordination artifacts