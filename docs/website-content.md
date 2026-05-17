# Sovereign AEC — Six Prototypes in Six Weeks

> A focused sprint to bring Nostr, Bitcoin and Bauwesen together. Six small browser apps, one per week, each pushing one specific capability into the open. No backends, no platforms, no lock-in.

---

## Hero

**The headline.**
We are building the missing layer between BIM and Bitcoin. Six HTML prototypes, shipped weekly, that show what an open, sovereign AEC stack actually looks like in practice.

**The sub-headline.**
Open content, signed coordination, timestamped on-site records, and Lightning-funded issue resolution — all running directly in your browser, with your own keys.

**Call to action.**
Watch the weekly demos. Fork the code. Bring your own keys.

---

## Why this exists

Construction-industry software is among the most centralised, most locked-in, and most expensive corners of professional software. A single BCF issue lives behind a vendor portal. A daily site log lives in a folder no court will trust. A property datasheet from a manufacturer lives in a PDF that nobody can verify.

Nostr changes the substrate. Identity becomes a keypair you control. Coordination becomes signed events that any relay can carry. Payments are sats, not invoices in 60 days.

This project does not propose a single big platform. It ships six small, sharp prototypes, each of which proves one part of the picture works. By the end of the sprint, the pieces fit together. By the end of the year, they become standards.

---

## The Six Prototypes

### Week 1 — Open Content Hub
*citadel-open-content.html*

A single HTML page that aggregates long-form articles from curated AEC and MEP authors on Nostr. Filter by topic, read in the browser, follow the authors you trust. Drops into existing Bitcoin-education sites like citadel-resources.com as a fresh content layer.

**What it proves.** That domain knowledge can live and circulate on open protocols, with no editor, no paywall, no platform.

### Week 2 — BCF QuickForm
*bcf-quickform.html*

The smallest possible BIM Collaboration Format implementation. Log in with a Nostr signer, fill in title, status, priority and due date, click publish. Your BCF topic is now a signed Nostr event that anyone with the link can read.

**What it proves.** That coordination between planners does not need a vendor portal — only a shared protocol and shared keys.

### Week 3 — BCF Thread
*bcf-thread.html*

The other half of BCF. Open any topic by link, see the full comment thread, the audit trail of every status change, the snapshot the issue refers to. Add a comment, change the status, watch the event propagate across relays in seconds.

**What it proves.** That a full multi-party coordination workflow can run entirely in a browser with no server in the middle.

### Week 4 — Timestamped Construction Diary
*ots-bautagebuch.html*

A daily site log with cryptographic teeth. Each entry — weather, crew, deliveries, incidents — is signed as a Nostr event and anchored to the Bitcoin timechain via OpenTimestamps. Six months later, anyone can verify the entry existed on the day it claims.

**What it proves.** That legally relevant construction records can be made tamper-evident at zero marginal cost, using only public infrastructure.

### Week 5 — Bounty Board — Lightning Bounties for BIM Issues
*the bounty-board UI*

A board of open BCF issues from the test tribe, each fundable with Lightning zaps. Want a specific clash resolved this week? Fund it. Want a coordination issue prioritised? Top up the bounty. Resolvers earn sats on completion, automatically and transparently.

**What it proves.** That money can flow into the right corners of a project as easily as a thumbs-up — and that markets can form around open issues without a platform skimming the middle.

### Week 6 — Polish and Launch
*The landing page that ties the five demos together.*

Consistent branding across all prototypes, one-minute demo videos for each, READMEs with stack notes, a single landing index showcasing the sprint as one coherent story. A pitch deck that frames the six weeks as Phase 1 of a larger sovereign-AEC vision.

---

## Tech Stack

Everything below runs in the browser. No backend, no cloud, no subscription.

| Layer | Tool |
|---|---|
| Identity | Nostr — keypair-based, NIP-07 browser signers (Alby, nos2x) |
| Coordination | Nostr events — BCF topics as `kind:30900`, comments as `kind:1170` |
| Long-form content | NIP-23 long-form articles (`kind:30023`) |
| Payments | Lightning via NIP-57 zaps on events |
| Tamper-evidence | OpenTimestamps anchored to the Bitcoin timechain |
| File storage | Blossom (sha256-addressed blobs, hosted by anyone) |
| Render | Vanilla JavaScript, marked.js for Markdown, Chart.js for charts |
| Deploy | Static hosting on Cloudflare Pages or GitHub Pages |
| License | MIT, all repositories public |

---

## Roadmap

**Phase 1 — Six prototypes (the current sprint).**
Five working browser apps, one landing page, one pitch deck. Shipped, demoed, open-sourced.

**Phase 2 — The standards layer.**
Full NIP drafts for BCF, IDS (Information Delivery Specification), LOIN (Level of Information Need), and an IFC Validation Service expressed as a Data Vending Machine. The prototypes harden into specs and reference implementations.

**Phase 3 — The infrastructure layer.**
`nodrive` — a sovereign drive with pluggable storage adapters (LocalFS, Blossom, hashtree, S3, even existing cloud drives). Encryption client-side, identity via Nostr, addressing via Merkle roots. The filesystem that every AEC workflow above can lean on.

---

## Parallel Tracks

Two commercial products run alongside this open-source sprint, and inform it without depending on it.

**AdlerHort.** A local, GDPR-compliant AI data filter for planning offices. Transforms decades of mixed BIM and CAD chaos on NAS systems into a clean, AI-searchable knowledge base — without cloud, without license fees, without exporting a single file. Built on Ollama, Qdrant and SQLite. ISO 19650 aligned.

**ZapViz.** A Lightning-powered, real-time AI art installation for events and parties. Guests scan a QR code, zap a prompt, and watch their idea evolve live on screen at 30–60 frames per second via StreamDiffusion. Lightning, LLMs, and continuous img2img feedback in one box.

Both are separate products on separate stacks. They share the worldview — sovereign by default, local where it matters, Lightning for value — but they do not block, depend on, or compete with the SE sprint.

---

## Who this is for

- **Planners and BIM managers** who want to coordinate without renewing yet another vendor subscription.
- **Construction lawyers and clients** who want site records that hold up in court without a notary.
- **Manufacturers** preparing for the EU Digital Product Passport and want a head start on sovereign product data.
- **Engineers and architects** who already think in Bitcoin time preference and want their tooling to match.
- **Developers and Sovereign Engineering alumni** who want to fork small, sharp, working prototypes instead of monolithic platforms.

---

## Get Involved

- Watch the weekly demo drops.
- Fork the code on GitHub.
- Submit a topic on the test tribe.
- Zap an issue you care about.
- Join the AEC Nostr community starting to form on the open-content hub.

The point of an open protocol is that you do not need permission to use it. Bring your own keys.

---

## Imprint

Built by Felix Hitthaler — engineer in HKLS/MEP and BIM, sustainable building and circular economy, working across Italy, Austria and Germany. Reachable as a Nostr npub on the project tribe.

License: MIT for code, CC BY 4.0 for written content. Specifications proposed for inclusion in `nostr-protocol/nips` once stable.
