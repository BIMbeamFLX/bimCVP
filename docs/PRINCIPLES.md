# Gemeinwert / BIM CVP — Design Principles

**Status.** Living document. Every architecture decision is checked against these three principles.

---

## 1. We build nothing ourselves

We build only the glue. Anything that exists as a mature open-source tool gets wired together, never reimplemented.

**What we consume rather than build:**

| Function | Existing tool |
|---|---|
| Signing / identity | Alby, nos2x (NIP-07), or Amber (NIP-46) on mobile |
| Relay | strfry or nostr-rs-relay |
| Blob storage | Blossom server (any compliant) |
| Avatar | DiceBear (deterministic, no API key) |
| Optional premium avatar | Fal.ai / Together.ai (later) |
| Nostr SDK | NDK from CDN |
| IFC parsing | IfcOpenShell |
| Web IFC viewer | @thatopen/components (web-ifc + Three.js) |
| Timechain notary | OpenTimestamps |
| Lightning | LNbits or Cashu mint |
| Group model | NIP-29 (if relay supports it) else NIP-72 or p-tags in 30902 |
| Long-form | NIP-23 |
| File metadata | NIP-94 |
| Zaps | NIP-57 |

**What we write ourselves:**

- UI layer (HTML/JS, single-file prototypes)
- Event schema conventions (KIND-REGISTRY.md)
- Building logbook generator (templating)
- IFC ingest CLI (Python glue)
- Adapter conventions (`nodrive://` URL scheme)
- Provincial-CDE export adapters (push to ACCA usBIM, Catenda Hub, ACC, etc.)

If something is in neither of those two lists — stop. Search whether it already exists. Only then build.

---

## 2. The target is the bureaucracy toaster

The dumbest conceivable user. Outside the tech bubble. Has had the same Outlook setup for fifteen years. Thinks "cloud" is a weather phenomenon. Receives a new ACC license reminder every quarter and doesn't know what to do with it.

**Consequences:**

- **No hex strings in the UI.** Ever. Not even as "pro mode".
- **No npub/nsec strings in the primary surface.** Use words like "character", "avatar", "profile", "identity".
- **No concept explanations.** If the user doesn't understand, the user isn't wrong — the UI is.
- **Default values everywhere.** No setup questionnaire with ten fields. No choice when a sensible default exists.
- **Familiar paradigms.** "Create character" instead of "generate key". "Enter the world" instead of "login". "Participants" instead of "pubkeys".
- **Failure modes visual.** When the relay is down, the UI does not say "WebSocket connection refused" — it says "the workshop is temporarily unreachable".
- **One action per screen.** Never two primary buttons on the same step.

---

## 3. Key backup is not our problem (in pilot)

Private-key backup is the unsolved UX problem of all sovereign tech. We don't try to solve it in the pilot. Three paths, all delegated:

- **Path A — browser extension (primary).** Alby / nos2x / nsec.app. They handle backup themselves, with mnemonic, password, browser sync. We dock via NIP-07. We don't own the key, don't see it, are not responsible.
- **Path B — mobile signer.** Amber (Android), nsec.app, Bunker server. NIP-46 adapter in the UI. Again: backup is the signer's job.
- **Path C — throwaway identity (pilot fallback).** Browser localStorage. Clear warning in the UI: "You can lose this character if you clear the browser. OK for pilot." If someone loses it: re-create, project admin (Bob) re-adds.

**When backup matters again:**

- After the pilot, when real clients arrive.
- When Frostr multi-sig approvals become legally binding.
- When Sat balances sit on a pilot npub.

Until then: not our problem. Period.

### 3a. Amendment — bounded custodial recovery for the pilot (2026-05)

Field reality overrode the absolutist version above: the pilot's real users are
non-technical construction people who *will* lose keys, and "make a new npub" is
unacceptable UX for them. The pilot therefore adds a **fourth, default path** on
top of A/B/C — without removing them:

- **Path D — managed identity (Tier 1, pilot default).** A server-side NIP-46
  bunker custodies the key; the user logs in via LNbits and gets a fresh bunker
  connect token, **same npub**, on any new device. The browser still never sees
  an nsec. Paths A/B stay available for power users (sovereign, no custody);
  Path C stays for throwaway demos.

This is a **deliberate, bounded, documented deviation**, not a reversal:

- Custody protects against *loss*, not *compromise*. A compromised key still
  falls back to "new npub + admin re-link" (Path C semantics).
- It is bounded to a *named* pilot circle, behind an encrypted keystore with the
  operator key offline, and must be written into the DSFA.
- "When backup matters again" (above) is unchanged: post-pilot, Tier-1 users
  migrate to their own NIP-07/NIP-46 or FROST/Frostr multi-sig.

Full model, recovery semantics and trust boundary: **`identity-architecture.md`**
(binding). §1, §2 and §4 are unaffected.

---

## 4. Public ledger, private conversation

Every signed claim that needs to survive is on Nostr — auditable, replicable, long-lived. Every working conversation that does not need to survive runs on a private layer with Forward Secrecy.

**The two-layer rule:**

| Public ledger (Nostr Events, kind:309xx + 11xx) | Private layer (White Noise / MLS-on-Nostr) |
|---|---|
| Project definition, member list (kind:30902) | Team discussions, pre-consensus negotiations |
| IFC reference, Blossom URL (kind:30904) | Calculation reviews, bidding strategy |
| BCF topic, viewpoint (kind:30900-01) | Subcontractor selection conversations |
| Approval / Abnahme (kind:30970) | Compliance whistleblowing |
| Audit-trail (kind:1171) | Internal critique before public comment |
| Maintenance event (kind:30962) | Personal / HR matters in larger teams |
| Quantity records (LV / Capitolato refs) | Confidential client requirements pre-tender |

The two layers share the same `npub` as identity root. A signed public event MAY carry a `["white-noise-group", "<group-id>"]` tag pointing to the private discussion that preceded it. The discussion stays private. Only the decision is public.

**Why MLS, not just NIP-44/NIP-17:**

- Forward Secrecy: a compromised key today does not retroactively decrypt yesterday's group chat. Critical for 50-year construction records.
- Scalable group operations: NIP-17 gift-wrapping scales poorly past a dozen members. MLS scales to thousands without re-encryption per message.
- Metadata protection: NIP-17 leaks `who-talks-to-whom` to relays. MLS hides group membership at protocol level.
- Standards body: MLS is an IETF RFC. NIP-17 is a Nostr proposal. For long-lived legally relevant work, the more boring standard wins.

**Veto-Heuristik-Anwendung:** *„Building our own DM layer?"* — No. White Noise exists, runs on Nostr, is open source. We wrap, we don't reinvent.

**Production-Readiness:** White Noise is mid-2025-launched. Identity is `npub`, so if White Noise is later replaced by SimpleX or another MLS-on-Nostr implementation, identity travels with the user. Pilot may use NIP-17 as fallback where White Noise is unavailable (e.g. mobile field workers without MLS client). Decision matrix: default White Noise, fallback NIP-17, never NIP-04.

---

## Corollaries

- **No "login" in our world.** We have "choose character" (NIP-07 connection) or "create character" (generation).
- **No "account" in our world.** We have a character with a profile.
- **No "forgot password" in our world.** We have "import backup" or "create new character".
- **No data-loss drama.** In the pilot, all project data is recoverable — events live on relay + Blossom, character loss = new character, admin re-adds the npub, business as usual.

---

## Veto heuristic

For every new feature idea:

1. **Does the feature already exist somewhere?** Yes → integrate, don't build. No → continue.
2. **Does an Outlook user understand it without explanation?** No → simplify or hide. Yes → continue.
3. **Does it punt backup responsibility away from us?** Yes → accept, or delegate to Path A/B. No → continue.
4. **If all three pass:** build.

---

*Anyone who wants to violate a principle writes an ADR (Architecture Decision Record) explaining why. Default is: follow the principle.*
