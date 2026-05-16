---
title: "Sovereign AEC Sprint — six HTML prototypes in six weeks"
description: "A focused, single-engineer experiment to ship the AEC industry's missing Nostr-native primitives — one HTML file per week. BCF coordination, signed construction diaries, Lightning bounties, and a public content layer."
lang: en
canonical: /labs/sovereign-aec-sprint
---

# Sovereign AEC Sprint

**Six HTML prototypes in six weeks.** No backends, no frameworks, no platforms — just signed events, Lightning, and the open web.

This page collects the work-in-progress for the Sovereign Engineering Cohort sprint. Each prototype is a single HTML file that ships a small, sharp idea from the BIM and construction industry onto the Nostr protocol. The goal is not to launch a startup — it's to show what the AEC stack looks like when it's owned by the people who use it.

---

## The premise

The buildings industry runs on platforms. ACC, BIMcollab, Trimble Connect, ProjectWise — every coordination workflow lives behind someone else's login. The standards underneath (IFC, BCF, IDS from buildingSMART) are open, but the data is locked.

Nostr changes the math. Identity is a keypair. Events are signed JSON. Relays are interchangeable. The same primitives that power decentralized social media also power decentralized engineering — once someone builds the adapters.

This sprint is a wager that the smallest useful AEC primitives can each be expressed as a self-contained HTML page, signed by the user's own keys, and survive on commodity relays. If five out of six work, the case is made.

---

## The six prototypes

### Week 1 — Citadel × Open Content

**An aggregator for long-form AEC articles published natively on Nostr.**

Subscribes to a curated list of HKLS, BIM, and construction npubs. Renders the last 20 NIP-23 long-form posts with author, date, tags, and a markdown preview. Embeddable as a section in [citadel-resources.com](https://citadel-resources.com). Multilingual filter (German, Italian, English) so the European side of the industry is not an afterthought.

**Event kinds.** `kind:30023` (NIP-23 long-form), `kind:0` (profile metadata).
**Status.** Planned for week 1.

---

### Week 2 — BCF Quickform

**The smallest possible BCF implementation.**

A single HTML form. Login via NIP-07. Type a title, a description, a status, a priority, a due date. Hit publish. A `kind:30900` BCF Topic event lands on a handful of relays. The feed below updates live with topics from a test tribe. Other planners see your topic the moment you send it.

No viewpoints, no 3D renderer, no multi-project setup — those are explicitly out of scope. The point is to prove that the BCF data model maps cleanly onto a replaceable Nostr event, and that it works in a browser without a backend.

**Event kinds.** `kind:30900` (BCF Topic).
**Status.** Planned for week 2.

---

### Week 3 — BCF Thread

**Comments, audit trail, snapshots — the second half of BCF.**

Open a topic from week 2's feed. See the snapshot at the top, the description below, the comment thread chronologically, and a collapsed audit trail showing every status change with author and timestamp. Reply inline. If you're the assignee or a moderator, the status dropdown is live.

NIP-10 markers handle threading. Each status change publishes both the updated topic (replaceable) and an immutable `kind:1171` audit event, so the history is reconstructable forever.

**Event kinds.** `kind:1170` (comment), `kind:1171` (audit), `kind:30900` (topic replacement).
**Status.** Planned for week 3.

---

### Week 4 — OTS Bautagebuch

**Construction site diary, signed and anchored to the Bitcoin timechain.**

Every construction project in the German-speaking world legally requires a daily site diary — weather, headcount, deliveries, incidents. In a dispute, this diary is evidence. Today it lives in PDFs and spreadsheets on someone's hard drive.

This prototype turns the daily entry into a signed Nostr event plus an OpenTimestamps anchor on the Bitcoin chain. Cost per entry: zero. Legal weight: significant. After a few hours the OTS proof finalizes; the verify button reads it back and shows the block height where the entry was attested.

**Event kind.** `kind:30960` (diary entry, parameterized replaceable, `d=<project-id>-YYYY-MM-DD`).
**Status.** Planned for week 4.

---

### Week 5 — plebbim

**Lightning bounty board on top of BCF issues.**

Every open BCF topic can be funded with Lightning zaps. The card grid sorts issues by accumulated sats. Click "Fund this issue" to zap directly through your NIP-07 wallet — Alby, Mutiny, anything that speaks NIP-57. When the topic flips to "Resolved", the card moves to a resolved stack with the resolver's npub credited.

The economics are kept simple in v1: zaps go directly to the topic author by default. Cashu-based escrow with delayed release to the actual resolver is a phase-two move.

**Event kinds.** `kind:30900` (read), `kind:1171` (status), `kind:9735` (zap receipts), `kind:9734` (zap requests).
**Status.** Planned for week 5.

---

### Week 6 — Polish & Landing

**Unified look, demo videos, a pitch.**

All five prototypes get the same header, the same color palette, and the same footer. Each one gets a 60-second Loom demo. A landing page collects them in a grid with screenshots and one-line pitches. The week closes with a pitch deck framing the six weeks against the wider roadmap: standards drafts in phase two, infrastructure in phase three.

No bonus prototype. Week 6 is the buffer. If anything in weeks 1–5 took longer than planned, this is where it gets caught.

---

## Stack philosophy

Single HTML files. ES Modules. NDK loaded from a CDN. NIP-07 for signing. Blossom URLs for binary attachments. Chart.js where charts help. Marked.js where markdown is rendered. OpenTimestamps for time anchoring. Deploy on Cloudflare Pages or GitHub Pages. MIT license.

The constraint is deliberate. Frameworks, bundlers, design systems, and authentication services all add friction at a stage where friction is the enemy. If a prototype can't be built in a single HTML file, it's almost certainly not a phase-one prototype.

---

## Parallel products

This sprint is one half of a larger workshop. Two other products run on their own tracks and are not part of the SE sprint:

**AdlerHort** is a local, GDPR-compliant AI data filter for planning offices. It turns decades of file chaos on a NAS into a searchable knowledge base — fully on-premises, no cloud upload. Runs on a workshop GPU, classifies via Ollama and qwen3, indexes into Qdrant, logs every decision into SQLite as the single source of truth. Phase zero (deduplication) is ready; phase one (scan and review) is under active development. The business model is a free FOSS core plus a Bimbeam EU SaaS for metadata and thumbnails.

**ZapViz** is a Lightning-powered real-time AI art installation for parties and events. Guests scan a QR code, zap with a prompt as memo, and watch their idea evolve at 30–60 frames per second on a big screen — StreamDiffusion behind the scenes, Ollama or Groq enhancing prompts, optional FLUX seed generation, MJPEG out to the projector. Runs on commodity NVIDIA hardware via Docker.

Both products exist independently and do not depend on the sprint. The sprint sits cleanly alongside them: AdlerHort owns the local-data and AI side; ZapViz owns the spectacle and Lightning-art side; the sprint owns the protocol and coordination side.

---

## Roadmap

**Phase 1 (now, six weeks).** The HTML prototypes above. Ship six, demo five.

**Phase 2 (the season after).** Turn what works into proper NIP drafts: BCF over Nostr, Information Delivery Specification (IDS) on Nostr, a Data Vending Machine for IFC validation, a Product Data Template kind for the EU Digital Product Passport, an Office Collaboration Format (OCF) for encrypted team coordination. These are real specifications with test vectors, not just demos.

**Phase 3 (the year after).** The infrastructure bet — a Nostr-native control plane over any storage backend, with end-to-end encryption client-side. Local filesystem, Blossom, S3, WebDAV, hashtree, and FIPS mesh as adapters. The working name is `nodrive`. Phase one already reserves the URL scheme `nodrive://npub/path` in file references, so the prototypes are forward-compatible with phase three from day one.

---

## Why this matters

The buildings industry is at the edge of three big shifts at once: the EU Digital Product Passport for construction materials becomes mandatory from 2027. The recast EPBD requires verifiable building-performance monitoring. ISO 19650 has standardized the process layer for common data environments.

Each of these regulatory hooks creates a need for signed, verifiable, vendor-neutral data exchange. The classical answer is more centralized platforms. The Nostr answer is signed events on commodity relays plus client-side encryption — cheaper, more sovereign, and structurally harder to capture.

This sprint is a small contribution to that answer. If it works for one engineering office, it works for the next.

---

## Follow along

The prototypes will land week by week. Each ships with a live demo, a README, and a short video.

- **Nostr.** Author npub published on the landing once setup is complete.
- **Code.** GitHub monorepo, MIT license, conventional commits.
- **Updates.** Long-form posts on Nostr (NIP-23), aggregated through the week-one prototype itself.

If you build in BIM, HVAC, MEP, or run a planning office and want to test any of these against real workflows: get in touch.

---

*Last updated: May 2026. The plan is firm; the details move. AdlerHort and ZapViz are tracked separately on their own pages.*
