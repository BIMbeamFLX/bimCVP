# Gemeinwert / BIM CVP — Brand Concept

**Status.** Brand decided May 2026. Living document — every brand convention is documented here.

---

## Name

- **Gemeinwert** (brand proper noun)
- **BIM CVP — Common Value Protocol** (English / international / standards discourse)

One word as a proper noun. English as a three-letter acronym in the buildingSMART family style (BCF, IDS, IDM, MVD … now CVP), long form *Common Value Protocol* as standards frame.

**Usage:**

- General audience (PA, architects, site managers): **Gemeinwert**
- International / openBIM standards context: **BIM CVP**
- English dev docs: **CVP** as short form, *Common Value Protocol* spelled out on first occurrence
- NIP draft to `nostr-protocol/nips`: *BIM CVP* in the title, *Common Value Protocol* in the description

## Domains

- `gemeinwert.com` — main entry
- `gemeinwert.it` — Italy / Provincia di Bolzano context
- `gemeinwert.eu` — neutral European
- `gemeinwert.de` — if available/buyable, else skip
- (optional later) `bimcvp.org` or `commonvalueprotocol.org` for standards/dev pivot

## Motto

| Audience | Motto |
|---|---|
| PA / architects | **"The open layer for signed construction."** |
| International / standards | **"The open layer for signed construction."** |
| Dev / Nostr space | **"build better with nostr"** |
| openBIM insiders | **"BIM CVP — Common Value Protocol"** as self-explanation |

The main site uses the English motto. Dev docs and the GitHub README use *build better with nostr* as the subtitle. Standards PRs use the full English name.

## Brand positioning

Gemeinwert / BIM CVP is the **standards project** and **open layer** on which signed construction workflows run. Non-extractive, MIT-licensed, openly extensible.

**Bimbeam** is the first commercial service provider on top of Gemeinwert — DVM marketplace provider for HKLS, CAM audit, owner advisory. Other providers welcome.

Analogy: Linux + Red Hat. Gemeinwert = Linux. Bimbeam = Red Hat. Catenda, ACCA, other platforms can use the same pattern.

## Two-word identity

> **Gemeinwert. Signed.**
> **CVP. Signed.**

Used as ultra-short marketing slogan if needed. Expresses mission and mechanism in three syllables.

## Brand architecture

```
Gemeinwert / BIM CVP            — platform / standards / movement
  ├─ wiki                       — buildingSMART knowledge, standards mapping
  ├─ app                        — managed onboarding (app.bimcvp.com)
  ├─ marketplace                — DVM listings (NIP-90-based)
  └─ providers
       ├─ Bimbeam               — Felix's services: HKLS / MEP / CAM
       └─ (more)                — other providers join over time
```

## Visual identity

Continues from existing HTML tools:

| Element | Value |
|---|---|
| Background | `#0f1419` (dark-blue charcoal) |
| Panel | `#1a2027` |
| Lines | `#2a3440` |
| Text | `#e8e8e8` |
| Secondary text | `#8a9aab` |
| Accent (gold) | `#f4c430` |
| Accent-2 (blue) | `#5b9bd5` |
| Success green | `#4ade80` |
| Warning red | `#f87171` |

Typography: Serif (Georgia) for headlines, Sans-Serif (system stack) for body, Monospace (SF Mono / Menlo) for code.

Logo: not yet designed. Candidates:

- Stylised Edelweiss in accent gold (alpine roots)
- An anchor plus workbench silhouette
- A "G" with a trace-line underneath
- Pure wordmark, no image — clean, professional

Pure wordmark is the simplest path until a logo is decided.

## Language conventions

- **Single site language: English.** The brand site, dev docs, code, NIP drafts and GitHub are all English. There is no separate German or Italian site version.
- **Source of truth:** English (dev docs, code, NIP drafts, GitHub)

Standards-compliance vocabulary is kept consistent in English throughout.

## Voice / tone

- **To PA / bureaucracy toaster**: respectful, clear, no tech jargon, trust-building
- **To architects / planners**: collegial, direct, technical-precise
- **To devs / Nostr community**: tinker-style, slightly playful, technically deep
- **To Bitcoin insiders**: concise, factual, no marketing speech

## What NOT to mention in the main facade

- *Bitcoin* — not in brand stack, not in front-page copy (comes actively later)
- *Nostr* — as a term not prominent, only in technical documentation
- *Blockchain* — never
- *Crypto* — never
- *Wallet* — not prominent, only in technical layers

These terms live in the secondary motto (*build better with nostr*) for dev audiences and in the dev docs section — never on the landing page for site managers.

## File status (rename to Gemeinwert / EN-primary)

| File | Status | When |
|---|---|---|
| `README.md` | done, EN primary | now |
| `docs/BRAND.md` | done, EN primary | now |
| `docs/PRINCIPLES.md` | EN primary | next pass |
| `docs/KIND-REGISTRY.md` | EN primary | next pass |
| `docs/STANDARDS-PROFILE.md` | EN primary | next pass |
| `docs/BACKEND-SETUP.md` | EN primary | next pass |
| `docs/bcf-nostr-nip-research.md` | EN primary | next pass |
| `web/index.html` | Gemeinwert rename done | now |
| `web/wiki/index.html` | rebrand | next pass |
| `web/character.html` | rebrand | next pass |
| `web/admin.html` | rebrand | next pass |
| `web/keys.html` | rebrand | next pass |
| Knowledge wiki pages | EN versions to be authored | follow-on waves |

---

*Status: May 2026. Brand fixed. All docs are authored in English.*
