# LNbits Integration — Sovereign AEC Pilot

**Premise.** Following Principle 1 ("we do not build anything ourselves") we delegate the entire Lightning layer to LNbits. We only wire Nostr events ↔ LNbits APIs ↔ webhook endpoints.

---

## Architecture position

```
            ┌──────────────────────────────────────┐
            │  Nostr-Client (Browser + NDK)        │
            │  - BCF UI, bounty board, Gebäudebuch │
            └──────┬─────────────────┬─────────────┘
                   │ Events          │ Pay-Links / NWC
                   v                 v
            ┌──────────┐      ┌─────────────────┐
            │  Relay   │      │     LNbits      │
            │ (strfry) │      │  - Wallets       │
            └──────────┘      │  - LNURLP-Links  │
                   ^          │  - NWC-Server    │
                   │ kind:9735│  - Webhooks      │
                   └──────────┤  - Cashu-Mint    │
                              └─────────────────┘
                                       │
                              optional: Boltz, Onchain
```

LNbits runs on the same pilot laptop as the relay + Blossom. Docker Compose service no. 3.

---

## Concrete integration points

### 1. Bounty board on BCF topics

**Flow:**

1. The UI client reads the `kind:30900` topic list from the relay.
2. Per topic, LNbits creates an LNURL-P endpoint (via `POST /lnurlp/api/v1/links`):
   - `description`: topic title
   - `min`, `max`: configurable
   - `comment_chars`: active (for donor notes)
   - `webhook_url`: points to a small endpoint (see 4)
3. The topic card in the UI shows an LN button → opens a QR with the LNURL.
4. Whoever zaps pays directly to the LNbits wallet of the topic creator.

**What we do not build:** the Lightning backend, the invoice creation, the payment aggregation.

### 2. Requirements-planning DVM and validation DVM

**Flow:**

1. The provider bids on a NIP-90 job (`kind:5xxx`).
2. The provider creates an LNbits invoice (`POST /api/v1/payments` with `out: false`).
3. The provider attaches the invoice to the result event (`kind:6xxx`) — tag `["amount", "<msats>", "<bolt11>"]`.
4. The client pays via NWC or their own wallet.
5. The LNbits webhook fires on payment → our endpoint writes a `kind:7000` payment confirmation to the relay.

### 3. NIP-47 NWC — Nostr Wallet Connect

LNbits has the NWC server built in (via an extension). User flow:

1. The user logs into their LNbits wallet (or receives a wallet link from the admin).
2. In the wallet settings they click "Nostr Wallet Connect" and copy the `nostr+walletconnect://...` URI.
3. In their Nostr client (Coracle, Amethyst, or our bounty-board UI) they paste the URI.
4. From now on: every zap request of the client goes via NWC to LNbits, LNbits pays, done.

**Meaning for UX:** the user clicks "Zap 500 sats" in the bounty-board UI and it just happens — no wallet-app switch, no Lightning wallet picker. Exactly the non-technical construction user use case.

### 4. Webhook → Nostr bridge

A tiny service (50 lines of Python or Node) that listens for LNbits webhooks and publishes Nostr events. Example:

```python
@app.post("/webhook/lnbits/<topic_event_id>")
def on_paid(topic_event_id):
    payload = request.json
    # payload: amount, comment, payment_hash, ...
    publish_zap_receipt(
        kind=9735,
        tags=[
            ["e", topic_event_id],
            ["bolt11", payload["bolt11"]],
            ["amount", str(payload["amount"])],
            ["description", payload.get("comment", "")],
        ],
        content="",
    )
```

Hosted on the same laptop. Small, replaceable, without pretension.

### 5. Admin workflow

The non-technical admin (project lead) sees in the UI:

- **"Open project wallet"** → a button that creates a new wallet via the LNbits admin API, sets tags, saves API keys.
- **"Assign a wallet to a participant"** → a member gets a sub-wallet with their own NWC link.
- **"Post a bounty"** → create an LNURL-P for a BCF topic.
- **"Payment to a planner"** → opens the LNbits UI directly with a pre-filled recipient + amount.

The admin sees no hex strings, no LN channels, no routing details. LNbits already hides all of that.

### 6. Reporting / accounting

LNbits has a built-in transaction list with a filter + CSV export. For fee reports or tax preparation we can simply pull all payments per wallet via the LNbits API + join them to Nostr events (which BCF topic produced which sat income).

### 7. Managed identity provisioning (Tier 1)

Released 2026-05. Binding: `identity-architecture.md`. Here LNbits is a
**pure wallet engine + account/login**, *not* the identity system of record —
that is the NIP-46 bunker + a minimal mapping table. No fork; non-enabled
extensions are inert.

Active extensions: `usermanager`, `nostrnwc`, `lnurlp`, `nostrnip5`.

One flow creates per pilot user:

1. **LNbits user + wallet** via the UserManager API → the login/account.
2. **Managed Nostr key** registered in the bunker (`nak bunker` in the pilot).
3. **Lightning address** `name@bimcvp.com` (lnurlp + nostrnip5, well-known on
   the bimcvp.com apex) — a human
   handle, also serving as **NIP-05** (discovery without hex, PRINCIPLES §2).
4. **NWC connection** (`nostr+walletconnect://…`, `nostrnwc`) — the same npub
   can zap/pay.

The mapping table is identity plumbing only:
`lnbits_user_id ↔ npub ↔ bunker_ref ↔ lightning_address` — no roles, no
BIM data (project membership stays `kind:30902`).

Recovery: key lost ≠ compromised. Loss → LNbits login → new
bunker token → **same npub**; the admin resets the credential via UserManager, the key
remains. Compromise → new npub + re-link in `kind:30902`.

---

## What our wiring tools must be

Per integration point we need exactly one adapter — all small:

| Adapter | Task | Size |
|---|---|---|
| `lnbits-client.js` | create an LNURL-P link, fetch wallet info | ~80 LoC |
| `lnbits-webhook.py` | receive the webhook → publish a Nostr event | ~50 LoC |
| `nwc-helper.js` | parse the NWC URI, send a pay request | NDK can already do this |
| `wallet-provisioning.py` | admin API for wallet creation | ~60 LoC |
| `provision` (server-side) | UserManager + bunker key + lnaddress + NWC + mapping; the only self-built component, **not in the public web repo** | small, security-critical |

In total under 250 lines of glue (the `provision` glue separately, server-side).

---

## Concrete actions for the backend setup

In `BACKEND-SETUP.md` (comes next) add the following Compose service:

```yaml
lnbits:
  image: lnbitsdocker/lnbits-legend:latest
  restart: unless-stopped
  ports:
    - "5000:5000"
  volumes:
    - ./lnbits-data:/app/data
  environment:
    - LNBITS_BACKEND_WALLET_CLASS=LndRestWallet  # or PhoenixdWallet / VoltageWallet
    - LND_REST_ENDPOINT=https://your-lnd:8080
    - LND_REST_MACAROON=base64...
    - LNBITS_SITE_TITLE=Sovereign AEC Treasury
    - LNBITS_ADMIN_USERS=<your-lnbits-user-id>
    - LNBITS_ALLOWED_USERS=<comma-list>
```

Initially local with the LNbits built-in SQLite and a Phoenixd wallet in the same container — zero setup for the pilot. Switch to your own LND later when real amounts flow.

LNbits URL: `http://localhost:5000`. Caddy in front for TLS as soon as it is needed publicly.

---

## Security / responsibility

- **Wallet keys on the laptop** are a risk. Pilot: only small amounts (max. a few k sats for tests). Real value flows later on hardened infrastructure (own server, own LND node).
- **Multi-sig / cosign:** LNbits has no native cosign; we do that later via a Frostr layer on Nostr (approval multi-sig on the pay-trigger event).
- **Audit trail:** all payments produce a `kind:9735` on the relay via the webhook → accounting lives on the timechain/Nostr layer, not only in LNbits.

---

## Open Questions

1. **Wallet backend choice** — Phoenixd (self-hosting, simple, automatic channel management) vs. own LND (more control, more effort) vs. Voltage Cloud (hosted, fast, costs)? Recommendation for the pilot: Phoenixd.
2. **Who hosts LNbits for the pilot?** DECIDED (2026-05): a small EU VPS (low-cost, GDPR region), together with strfry/bunker/blossom/phoenixd/caddy. The laptop/Tailscale is dropped. Details: `BACKEND-SETUP.md` §16.
3. **Cashu now or later?** A Cashu mint via the LNbits extension is doable with little effort. Use case: anonymous sub-payments in the office, requirements-planning DVM escrow. Recommendation: not in the sprint, but keep it ready as a Phase 2 button.
4. **DPIA for LNbits?** If only the admin and testers are on it: no personal-data problem. With real participants, the DPIA must state that LN payment metadata is collected.

---

*LNbits is exactly what Principle 1 promises: a mature OSS tool with better UX than anything we could build ourselves. We wire, they deliver.*
