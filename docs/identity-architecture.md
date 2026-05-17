# Identity Architecture

Single source of truth for how identity, key custody and recovery work in the
Gemeinwert / BIM CVP pilot. Binding for the backend setup and the future app
build. Read together with `PRINCIPLES.md` (§3 amended by this document) and
`BACKEND-SETUP.md`.

> **Implementation status (v1, 2026-05).** Tier-1 custodial onboarding is now
> built: the `provision` service (private `backend-deploy/`, encrypted
> keystore, LNbits + nostrnip5 + relay-allowlist cron) + the `webapp/` UI
> (email magic-link join/login/recover, project code/QR self-enrol). v1 signs
> **server-side** in `provision` (key decrypted in memory only there) — fully
> meets "no nsec in the browser, managed, email-recoverable". The **standalone
> NIP-46 bunker** (so the *same* managed key also works in external Nostr
> clients / White Noise) is the documented **next increment** — no migration,
> same keys. Tier-2 (NIP-07) / Tier-3 (throwaway) remain as written for power
> users; not used by the v1 managed flow.

---

## Why this exists

The pilot's real users are non-technical construction people ("bureaucracy
toaster"). They will lose Nostr keys. The original `PRINCIPLES.md` §3 ("keys
delegated to a signer; lost key = make a new npub") is unacceptable UX for them.
This document defines a **deliberate, bounded, documented pilot deviation**:
managed (custodial) identity with stable npub recovery, while keeping a fully
sovereign path for power users.

This is a **pilot-phase** decision. It is bounded by the Trust boundary section
and must be revisited before any non-pilot scale-up.

---

## The three identity tiers

The browser **never sees an nsec** in any tier. One frontend interface
(`signer.js`) abstracts all three; every tool is signer-agnostic.

| Tier | Default for | Mechanism | Lose access → |
|---|---|---|---|
| **1 — Managed** | non-technical pilot users (default) | LNbits account → server-side **NIP-46 bunker** holds the key → app signs via bunker | re-login to LNbits → fresh bunker connect token, **same npub**; admin can reset the LNbits credential |
| **2 — Sovereign** | power users | **NIP-07** browser extension (Alby / nos2x). No custody, no LNbits dependency | the user's own signer problem (unchanged from PRINCIPLES §3) |
| **3 — Throwaway** | demos / quick trials | key in `localStorage`, explicit "you can lose this" warning | gone; project admin re-links a new npub in `kind:30902` |

---

## Recovery semantics — read carefully

**Custody protects against _loss_, not _compromise_.**

- **Lost device / forgot access (the common case):** the Nostr key still exists
  in the bunker keystore. The user re-authenticates to LNbits, the glue issues a
  **new NIP-46 connect token** for the *same* key. The **npub never changes**, no
  project data re-linking needed. The admin can reset the user's LNbits
  credential (UserManager) without ever touching the key.
- **Recovery = resetting the _access credential_**, not the key. You never
  "rotate" a Nostr key to a new value while keeping the identity — that is
  impossible by definition (the npub *is* the public key).
- **Compromised key (someone else got it):** custody cannot save you. This falls
  back to the existing PRINCIPLES path — issue a **new npub**, admin re-links
  membership in `kind:30902` p-tags. This path must remain implemented and
  tested; it is not dead code.

---

## Components

```
Browser (app)
  └─ signer.js ── Tier 2: window.nostr (NIP-07)              → no server
                  Tier 1: NIP-46 client ── wss://bunker.bimcvp.com  ┐
                  Tier 3: localStorage key                          │
                                                                    │
Domains: gemeinwert.com = brand website (DACH).                     │
         bimcvp.com     = protocol/identity/services (this stack).  │
                                                                    │
VPS (Hetzner CX23)                                                  │
  ├─ caddy            TLS; serves gemeinwert.com (site) + bimcvp.com │
  ├─ strfry (public)  wss://relay.bimcvp.com  write-policy plugin    │
  ├─ strfry (private) localhost/tailnet only (optional, deferred)   │
  ├─ lnbits           pay.bimcvp.com   wallet engine only           │
  ├─ bunker           wss://bunker.bimcvp.com  custodies Tier-1 keys ┘
  ├─ blossom          blossom.bimcvp.com  blobs (Volume on demand)
  └─ phoenixd         :9740 internal   LNbits funding backend
```

LNbits is the **account/login/wallet** system of record only. It is **not** the
BIM system of record: project membership and roles stay event-defined in
`kind:30902` p-tags (hard constraint — no relational mirror of BIM data).

---

## The only bespoke component: the provisioning glue

Everything else is wired existing tooling (PRINCIPLES §1). The glue is small and
security-critical.

### NIP-46 bunker (do not write a signer)

- **Pilot:** `nak bunker` (fiatjaf `nak`) — one signer per key, scriptable,
  minimal.
- **Sturdier / multi-tenant:** self-hosted `nsec.app` / Knox backend.
- Start with `nak bunker`; the glue must abstract it so Knox can replace it with
  no frontend change. `nak bunker` is single-key — re-validate the approach at
  ~5–10 users.

### `provision` service (~tiny, the only custom code; server-side, NOT in the public web repo)

- **Create managed identity:** generate keypair → encrypt at rest → register
  with bunker → create LNbits user + wallet + Lightning Address → write one
  mapping row.
- **Recover:** authenticate to LNbits → issue fresh bunker connect token for the
  existing key → same npub.
- **Mapping table — identity plumbing only:**
  `lnbits_user_id  ↔  npub  ↔  bunker_ref  ↔  lightning_address`
  No roles, no BIM data, no project state.
- **Keystore:** encrypted (age / libsodium) with an operator key held offline.
  This is the trust boundary.

### Frontend signer abstraction — `app/assets/signer.js`

Single interface, resolves per tier:

```
getPublicKey()            → hex pubkey
signEvent(unsignedEvent)  → signed event
```

- Tier 2: delegate to `window.nostr` (NIP-07).
- Tier 1: NIP-46 client (nostr-tools / NDK) talking to `wss://bunker.bimcvp.com`.
- Tier 3: local key in `localStorage`, sign in-page (throwaway only).

Every tool (`character.html`, `keys.html`, `bcf-quickform.html`,
`bcf-thread.html`, ingest UIs) calls **only** this interface. The nsec is never
exposed to page code in any tier.

---

## Per-user provisioning result (Tier 1)

Creating a managed identity yields, in one flow:

1. **LNbits user + wallet** (UserManager API) — the login/account.
2. **Managed Nostr key** registered in the bunker — the signing identity.
3. **Lightning Address** `name@bimcvp.com` (lnurlp + nostrnip5; well-known
   served on the bimcvp.com apex via Caddy) — a human handle that *also* serves
   **NIP-05**, so the npub is discoverable by name
   (PRINCIPLES §2 intelligibility — no hex strings in UI).
4. **NWC connection** (`nostr+walletconnect://…`, `nostrnwc`) — so the same npub
   can zap / pay from its wallet.

One action → the user is a Nostr **and** Lightning native participant with a
recoverable identity and a readable handle.

---

## Trust boundary (must also land in the DSFA)

- The operator can technically sign as any Tier-1 user (custodial). This is
  acceptable **only** for a pilot with a *named* stakeholder circle, and only
  when stated openly — never silently.
- Keystore encrypted at rest; operator key offline; access logged.
- The DSFA template in `BACKEND-SETUP.md` must be extended with custodial-key
  processing as a data category and the operator as processor.
- Tier 2 (NIP-07) is offered to anyone who wants zero custody.
- **Post-pilot migration path:** Tier-1 users export to their own NIP-07 / NIP-46
  signer, or move to FROST / Frostr multi-sig (already flagged as the post-pilot
  step in PRINCIPLES). Custodial Tier-1 must not scale to anonymous public users
  without revisiting this document.

---

## Verification checklist (when the backend is built)

1. Provision a Tier-1 user → LNbits user+wallet exist; `name@bimcvp.com`
   resolves via LNURL **and** NIP-05; NWC URI works (test zap, phoenixd small sats).
2. Sign a `kind:30900` via the bunker through `signer.js`; event lands on the
   public relay and verifies (`tools/verify.py`).
3. **Recovery test:** wipe browser/localStorage → re-login to LNbits → new bunker
   token → publish again → **same npub** on both events.
4. Tier 2: NIP-07 (Alby) signs and publishes with zero LNbits/bunker involvement.
5. **Compromise drill:** new-npub + `kind:30902` re-link path works end to end
   (the non-recoverable case is handled, not silently broken).
