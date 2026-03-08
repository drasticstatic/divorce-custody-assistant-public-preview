# Divorce & Custody Assistant

> Privacy-first, AI-assisted case management for pro se litigation support

<p align="left">
  <a href="https://drasticstatic.github.io/divorce-custody-assistant-public-preview/"><img src="https://img.shields.io/badge/%F0%9F%8C%90%20Public%20Preview-Configured-brightgreen" alt="Public Preview"></a>
  <a href="https://github.com/open-condo-software/gitexporter"><img src="https://img.shields.io/badge/Synced%20via-GitExporter-blue" alt="Synced via GitExporter"></a>
  <a href="https://code.claude.com/docs/en/overview"><img src="https://img.shields.io/badge/Claude%20Code%20CLI-Anthropic-1f2937" alt="Claude Code CLI"></a>
  <a href="https://www.augmentcode.com/"><img src="https://img.shields.io/badge/Augment-Code-2563eb" alt="Augment"></a>
</p>

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

- **Fortuna** — session intelligence and operating context
- **Kavanah** — coordination and task orchestration
- **Auggie** — implementation and automation work

## Public-safe principle

This mirror is for sharing structure, automation patterns, and explicitly approved public-facing materials only. It is not a publication channel for sensitive legal records or repo-internal coordination artifacts