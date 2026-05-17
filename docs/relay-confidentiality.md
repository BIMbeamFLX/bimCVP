# Relay Confidentiality — Risk Analysis (decision deferred)

Status: **direction chosen (Increment B), build deferred** — see last section.
No implementation yet. Binding read alongside
`PRINCIPLES.md §4` (private layer), `identity-architecture.md` (custodial trust
boundary) and `BACKEND-SETUP.md §16` (DSFA). No client names in this repo
(trust boundary): a real engagement is referred to as "a confidential pilot".

## The problem

The public relay (`relay.bimcvp.com`) gates **writes** only (allowlist plugin).
**Reads are open** — strfry default, nothing restricts subscriptions. Therefore
every BCF payload is **world-readable cleartext**: topic titles, descriptions,
site addresses, who coordinates with whom, project structure.

- **Severity: high — but scoped to `content`.** What must be confidential is
  the BCF **payload** (titles, descriptions, addresses, the substance). The
  exposure is cleartext content on an open relay.
- **Tags stay public by design.** `s`/`bcf-status`, `bcf-type`,
  `a`, `p`, timestamps are *intended* to be public: a tamper-evident,
  independently verifiable record that coordination happened, when, in which
  project, between which keys. That public activity trail is a **feature
  (notarized proof)**, not a leak. The only rule: never put substance into tags.

## North star & hard invariant

- **Hard invariant:** cleartext BCF content is **never** posted over a relay —
  public or private. Encryption of `content` is mandatory, not optional.
- **Vision:** a planners' coordination *infranet* — every office can
  **self-host** a bimcvp node (relay + provision). Public, verifiable
  coordination metadata; confidential content. Federated, no vendor in the
  middle.
- **Hardest part (explicit):** custody and **rotation of the per-project
  content key across multiple bunkers** (threshold / FROST-style, multi-office),
  so no single host is a single point of trust or failure. This is the project's
  hardest problem; it extends the post-pilot FROST/Frostr note in `PRINCIPLES.md`
  and the NIP-46 bunker increment in `identity-architecture.md`. Out of scope
  for the pilot build; in scope for the architecture.

## What does *not* solve it (the "it stays centralized" point)

- **Read-AUTH (NIP-42) on the relay:** only members can read, but the **relay
  operator still sees cleartext** — centralized trust remains. Per-project read
  scoping on a *single* open relay is brittle (strfry cannot cleanly read-gate
  by project × identity).
- **Shared-key encryption, key held by `provision`:** content becomes
  ciphertext to outsiders, but the operator still holds the key — honest, but
  not zero-trust.

## The real options (staged)

| # | Approach | Protects against | Operator sees | Effort | Maturity |
|---|---|---|---|---|---|
| **A** | **Private internal relay** per pilot (tailnet/localhost, not public) | the public | yes (cleartext) | small — already designed in PRINCIPLES §4 | now |
| **B** | **NIP-44 content encryption**, per-project key custodied by `provision` | public + relay storage | only key holders | medium — app + provision | good |
| **C** | **MLS / NIP-EE** (White Noise): true E2E, forward secrecy | everyone incl. operator | no (ciphertext only) | large; **the web UI cannot do this** (browser MLS = security regression, PRINCIPLES §1) → White Noise *client* only | alpha |

Notes:
- **B** keeps tags public **on purpose** (notarized coordination trail) and
  encrypts only `content` → server-side `#a`/status filtering is preserved.
  Simpler and better than tag-minimization; the design just forbids substance
  in tags.
- The north-star extension of **B** is per-project key custody/rotation across
  **multiple self-hosted bunkers** (no single trusted host) — the project's
  hardest problem, deliberately staged after the pilot.
- **C** is the sovereign end state for the private *messaging* layer, by design
  **not** the web BCF UI. Transport kinds (443/444/445/1059) are already
  accepted unconditionally by the write-policy plugin, so infra is ready when a
  White Noise–based private layer is exercised.

## Recommendation (for the decision, when taken)

1. **Public demos:** fictional *Citadel* data only. Never enter confidential
   client content into the public relay. Label demo data as an example.
2. **Real pilot:** **A now** (private, non-public relay for the engagement —
   fast, already in §4), then **B as the next increment** (per-project NIP-44,
   custodial — consistent with the v1 custodial identity model).
3. **Sovereign end state:** **C** via White Noise for the private layer; the web
   surface stays public-by-design.
4. **DSFA:** record "confidential project data + operator readability" as a
   processing activity / trust boundary (same shape as the custodial-key
   boundary already documented).

## Chosen direction — Increment B (spec, not yet built)

Decided: **per-project content key, server-side, custodial** — consistent with
the v1 model (provision already signs server-side; it now also encrypts /
decrypts server-side). **A stays the stopgap** until B ships; **C** (MLS) stays
the sovereign end state. Build deferred (after the Bozen showcase). This is the
spec.

### B.1 Key model
- One **Project Content Key (PCK)** per project: 32-byte random, generated by
  `provision` at project creation (`/api/admin/project`).
- Stored in the keystore **encrypted under the operator master key**, exactly
  like member secret keys (same table/trust boundary, AES-256-GCM).
- Scope is **per project** — a PCK leak exposes one project's history only
  (bounded blast radius; this is the point).
- **North-star (post-pilot):** the PCK is not held by one host but
  custodied/rotated across **multiple self-hosted bunkers** (threshold /
  FROST-style, one per office). Pilot = single custodial holder; the data model
  (versioned PCK, per-event PCK version) is designed so multi-bunker custody
  drops in without re-encryption of history. This is the hardest part of the
  project and is tracked here on purpose.

### B.2 Encrypt / decrypt (server-side)
- On publish (`/api/sign-publish`): `provision` encrypts the BCF JSON `content`
  with the project's PCK (NIP-44 v2 / XChaCha20-Poly1305) **before** signing &
  relaying. The relay only ever stores ciphertext.
- On read: the webapp fetches events and sends them to a `provision` endpoint
  (authenticated member of that project) which decrypts and returns plaintext
  over TLS. The browser never holds the PCK. Operator readability = the
  already-accepted custodial trust boundary (NOT zero-trust; that is C).

### B.3 Tags stay public — by design
- Tags are **kept public**: `d`, `a` (`30902:<owner>:<guid>`), `bcf-guid`,
  `bcf-version`, `s`/`bcf-status`, `bcf-type`, `p`, timestamps. This is the
  notarized coordination trail (proof that work happened, when, in which
  project, between which keys) and it preserves server-side `#a`/status
  filtering — the existing feed query is unchanged.
- **Only `content` is encrypted.** The single hard rule: **no substance in
  tags** — titles, descriptions, addresses, names live only inside the
  encrypted payload, never in a tag value.
- Net public surface (intended): a verifiable activity ledger with **zero BCF
  substance**. That public ledger is a feature, not a leak.

### B.4 Membership change = key rotation (not optional)
- Removing a member ⇒ generate a **new PCK**, distribute to remaining members,
  encrypt new events under it. **Old ciphertext stays readable** to whoever held
  the old key — inherent to shared-key groups. No forward secrecy / PCS; that is
  exactly the C/MLS boundary. Acceptable for a *named pilot circle*, must be
  stated openly.
- Rotation must be designed in from day one (PCK is versioned; events carry the
  PCK version), never retrofitted.

### B.5 DSFA
- Add a processing entry: "confidential project content, encrypted at rest on
  the relay, decryptable by the operator (custodial PCK) — bounded to the named
  pilot circle, access logged". Same shape as the custodial-key boundary.

### B.6 Node key backup = BIP39 12-word mnemonic (NIP-06)

The substrate for node/operator key custody — **not** an end-user artifact.

- **Boundary (hard):** end users never see a seed. Their recovery stays
  email-only; the tech stays hidden. The 12 words exist **only** at the
  node/operator/bunker layer.
- **Model:** a node's root secret is a **BIP39 12-word mnemonic**. From its
  seed, derive deterministically (NIP-06, `m/44'/1237'/…`, BIP32):
  (a) the operator master key that encrypts the keystore, (b) the PCK custody
  root (B.1). One seed backs up the whole node. `nostr-sdk` already exposes
  `Keys.from_mnemonic` → no bespoke crypto.
- **Replaces** the opaque `PROVISION_MASTER_KEY` blob backup with the familiar
  Bitcoin mental model: 12 words on paper/steel = the node is recoverable.
- **Backward compatible:** the derived 32-byte key equals today's
  `PROVISION_MASTER_KEY`. The pilot runs unchanged; the mnemonic is the
  **post-Bozen** upgrade of *backup*, not a break.
- **Enables the hardest part:** the seed is the natural basis for multi-bunker
  custody — SLIP39 / Shamir or FROST-threshold split of the 12 words across
  offices (one bunker per office), no single point of trust. This is where
  B.1's north-star plugs in concretely.

Until B is built: confidential data does not go on the public relay (use A).
The mnemonic/node-backup model is post-pilot; the pilot keeps the current
`PROVISION_MASTER_KEY` (already backed up in a password manager).
