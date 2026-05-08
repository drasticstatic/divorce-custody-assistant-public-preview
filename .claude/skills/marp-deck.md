---
name: marp-deck
description: >
  Use to generate a professional legal-themed Marp slide deck from a case document, factor
  analysis, timeline, or court-facing summary. TRIGGER when: "create a deck for", "make slides
  from", "marp this", "turn [doc] into slides", "presentation for", "shareable deck", "Marp
  version of", "slide summary of". Do NOT use for: creating the underlying document (build that
  first), or when the user wants a formatted markdown export rather than slides.
---

# Skill: /marp-deck — Divorce & Custody Assistant

Convert a case document, factor analysis, or timeline into a professional, court-appropriate
Marp slide deck and generate the HTML output.

## Quick Command

```bash
# Generate HTML from any .marp.md file
~/.nvm/versions/node/v22.12.0/bin/marp [path/to/file].marp.md -o [path/to/file].marp.html
```

---

## Before Starting

1. Confirm the source document exists and is complete
2. Identify output location: `smarttrader-ai/` equivalent → use case-appropriate working dir
3. Read the source to extract key content and structure
4. Confirm no identifying case details in slide content (privacy rule — see below)

---

## Privacy Rule (Every Deck)

Slide decks committed to git must follow the same rules as all committed files:
- No party names, case numbers, or specific allegations in committed `.marp.md` files
- Use placeholder labels: `[Party A]`, `[Party B]`, `[Date TBD]` for anything case-specific
- Court-facing decks with real names/details belong in runtime/local only (gitignored)

---

## Legal Color Theme

Professional, court-appropriate palette — restrained and credible:

```markdown
---
marp: true
theme: default
paginate: true
backgroundColor: '#f8f9fa'
color: '#1a202c'
style: |
  h1 { color: #1a3a5c; border-bottom: 2px solid #2c5f8a; padding-bottom: 10px; }
  h2 { color: '#2c5f8a'; margin-bottom: 0.4em; }
  h3 { color: '#4a6fa5'; }
  strong { color: #1a3a5c; }
  em { color: #4a6fa5; font-style: normal; }
  code { background: #edf2f7; color: #2d3748; padding: 2px 6px; border-radius: 3px; }
  pre { background: #f7fafc; border: 1px solid #e2e8f0; border-radius: 4px; padding: 1em; }
  table { border-collapse: collapse; width: 100%; font-size: 0.85em; }
  th { background: #2c5f8a; color: #ffffff; padding: 8px 12px; }
  td { border: 1px solid #cbd5e0; padding: 6px 12px; color: #2d3748; }
  blockquote { border-left: 4px solid #4a6fa5; padding-left: 1em; color: #718096; font-style: italic; }
  section { font-family: 'Georgia', 'Times New Roman', serif; }
---
```

**Why this palette:** White/light background reads well in courtroom projectors and PDFs.
Navy `#1a3a5c` and steel blue `#2c5f8a` convey credibility. Serif font matches legal document conventions. No flashy colors — nothing that reads as advocacy.

> **Note:** This theme is a starting point. Tailor further as the repo's visual identity develops — similar to how PIR Devine News has its dark navy/green scheme and trading-assistant has its own identity.

---

## Document Types

| Source | Deck Type | Key Slides |
|--------|-----------|-----------|
| Factor analysis (§ 5328) | Evidence map | Cover, one slide per factor, summary score |
| Timeline | Chronological narrative | Cover, grouped date ranges, key events |
| Case summary | Overview deck | Cover, parties, issues, positions, next steps |
| Financial analysis | Numbers deck | Cover, income/expense tables, comparison, conclusions |
| Hearing prep | Argument outline | Cover, each point, anticipated responses, ask |

---

## Step 1 — Create the .marp.md File

```markdown
---
marp: true
theme: default
paginate: true
backgroundColor: '#f8f9fa'
color: '#1a202c'
style: |
  [paste style block from Legal Color Theme above]
---

<!-- Cover slide -->
# [Document Title]
**[Date] — Prepared by Alfred / Fortuna**

*Confidential — Attorney-Client / Work Product*

---

<!-- Context slide -->
## Background

[Brief neutral context — 3-4 bullet points]

---

<!-- Main content — one idea per slide -->
## [Section Title]

[Content — factual, source-grounded, no speculation]

---

<!-- If evidence table -->
## [Factor / Issue]

| Category | Notes |
|----------|-------|
| Supporting | [factual summary] |
| Contrary | [factual summary] |
| Status | [new / reviewed / needs follow-up] |

---

<!-- Closing slide -->
## Summary & Next Steps

- [Key conclusion 1]
- [Key conclusion 2]
- Next: [specific action item]
```

---

## Step 2 — Naming Convention

```
[topic]-[YYYYMMDD].marp.md
[topic]-[YYYYMMDD].marp.html
```

Examples:
- `factor-analysis-20260507.marp.md` → custody factor evidence map
- `hearing-prep-20260512.marp.md` → child support hearing outline

**Location:** Working directory appropriate to document type (gitignored paths for anything with case specifics).

---

## Step 3 — Generate HTML

```bash
~/.nvm/versions/node/v22.12.0/bin/marp [file].marp.md -o [file].marp.html
```

Verify in browser: check that tables are readable, navy headers render correctly, and pagination is clean.

---

## After Completing

1. Verify HTML opens and all slides render correctly
2. If the file contains no identifying case details: commit `.marp.md` and `.marp.html`
3. If it contains real names/case specifics: keep local only (gitignored)
4. Add to session log with file name and purpose

---

## Reference

- Marp binary: `~/.nvm/versions/node/v22.12.0/bin/marp`
- Quick syntax: `~/.claude/skills/marp-quick-reference.md` (alfred repo) or trading-assistant
- Legal palette: white `#f8f9fa` · navy `#1a3a5c` · steel blue `#2c5f8a` · gray `#718096`
- PIR comparison: dark navy/green scheme in `pir-devine-news/.claude/skills/marp-deck.md`
- Trading-assistant: canonical `create-skill.marp.html` (linked externally — stays there)
