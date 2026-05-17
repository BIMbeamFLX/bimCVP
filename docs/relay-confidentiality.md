# Relay Confidentiality — Risk Analysis (decision deferred)

Status: **analysis only**, no implementation. Binding read alongside
`PRINCIPLES.md §4` (private layer), `identity-architecture.md` (custodial trust
boundary) and `BACKEND-SETUP.md §16` (DSFA). No client names in this repo
(trust boundary): a real engagement is referred to as "a confidential pilot".

## The problem

The public relay (`relay.bimcvp.com`) gates **writes** only (allowlist plugin).
**Reads are open** — strfry default, nothing restricts subscriptions. Therefore
every BCF payload is **world-readable cleartext**: topic titles, descriptions,
site addresses, who coordinates with whom, project structure.

- **Severity: high.** Acceptable for the fictional *Citadel* showcase. **Not**
  acceptable for confidential client project data.
- Even if `content` were encrypted, **tags leak metadata**: `s`/`bcf-status`,
  `bcf-type`, `a` (= `30902:<owner-pubkey>:<guid>`), `p` (participants) → status,
  activity volume and the social/project graph remain visible.

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
- **B** still leaks tag metadata unless tags are also encrypted — which then
  removes server-side filtering (must move to the client). Confidentiality vs.
  queryability is the core trade-off.
- **C** is the sovereign end state for the private layer, by design **not** the
  web BCF UI. The transport kinds (443/444/445/1059) are already accepted
  unconditionally by the write-policy plugin, so infra is ready when a White
  Noise–based private layer is exercised.

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

## Open decision

Which path (A / A→B / B / defer) for the first confidential pilot is **not yet
decided**. This document exists so the choice is made deliberately, not by
omission. Until decided: confidential data does not go on the public relay.
