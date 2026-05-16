# LNbits Integration — Sovereign AEC Pilot

**Premisse.** Nach Prinzip 1 („wir bauen nichts selbst") delegieren wir die gesamte Lightning-Schicht an LNbits. Wir verkabeln nur Nostr-Events ↔ LNbits-APIs ↔ Webhook-Endpoints.

---

## Architektur-Position

```
            ┌──────────────────────────────────────┐
            │  Nostr-Client (Browser + NDK)        │
            │  - BCF UI, plebbim, Gebäudebuch      │
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

LNbits läuft auf demselben Pilot-Laptop wie Relay + Blossom. Docker-Compose-Service Nr. 3.

---

## Konkrete Integrations-Punkte

### 1. plebbim — Bounty-Board auf BCF-Topics

**Flow:**

1. UI-Client liest `kind:30900` Topic-Liste vom Relay.
2. Pro Topic erzeugt LNbits einen LNURL-P-Endpoint (via `POST /lnurlp/api/v1/links`):
   - `description`: Topic-Titel
   - `min`, `max`: konfigurierbar
   - `comment_chars`: aktiv (für Spender-Notizen)
   - `webhook_url`: zeigt auf einen kleinen Endpoint (siehe 4)
3. Topic-Card im UI zeigt LN-Button → öffnet QR mit dem LNURL.
4. Wer zappt, zahlt direkt an die LNbits-Wallet des Topic-Creators.

**Was wir nicht bauen:** das Lightning-Backend, die Invoice-Erzeugung, die Zahlungs-Aggregation.

### 2. Bedarfsplanungs-DVM und Validation-DVM

**Flow:**

1. Provider bietet auf einen NIP-90-Auftrag (`kind:5xxx`).
2. Provider erzeugt eine LNbits-Invoice (`POST /api/v1/payments` mit `out: false`).
3. Provider hängt die Invoice an das Result-Event (`kind:6xxx`) — Tag `["amount", "<msats>", "<bolt11>"]`.
4. Auftraggeber zahlt via NWC oder eigenem Wallet.
5. LNbits-Webhook fired bei Bezahlung → unser Endpoint schreibt `kind:7000` Payment-Confirmation auf den Relay.

### 3. NIP-47 NWC — Nostr Wallet Connect

LNbits hat NWC-Server eingebaut (über Extension). User-Flow:

1. User loggt sich in seine LNbits-Wallet (oder bekommt vom Admin einen Wallet-Link).
2. In den Wallet-Settings klickt er auf „Nostr Wallet Connect" und kopiert die `nostr+walletconnect://...` URI.
3. In seinem Nostr-Client (Coracle, Amethyst, oder unserer plebbim.html) fügt er die URI ein.
4. Ab jetzt: jeder Zap-Request des Clients geht über NWC an LNbits, LNbits zahlt, fertig.

**Bedeutung für UX:** Der User klickt im plebbim-UI auf „Zap 500 sats" und es passiert — kein Wallet-App-Wechsel, kein Lightning-Wallet-Picker. Genau der Bürokratie-Toaster-Use-Case.

### 4. Webhook → Nostr-Bridge

Ein winziger Service (50 Zeilen Python oder Node), der auf LNbits-Webhooks lauscht und Nostr-Events publisht. Beispiel:

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

Hostet auf demselben Laptop. Klein, ersetzbar, ohne Anspruch.

### 5. Admin-Workflow

Der Bürokratie-Toaster-Admin (Projektleiter) sieht im UI:

- **„Projekt-Wallet eröffnen"** → Button, der via LNbits-Admin-API eine neue Wallet anlegt, Tags setzt, API-Keys speichert.
- **„Beteiligten Wallet zuweisen"** → ein Member bekommt eine Sub-Wallet mit eigenem NWC-Link.
- **„Bounty aussetzen"** → für ein BCF-Topic einen LNURL-P erzeugen.
- **„Zahlung an Planer"** → öffnet LNbits-UI direkt mit vorausgefülltem Empfänger + Betrag.

Der Admin sieht keine Hex-Strings, keine LN-Channels, keine Routing-Details. LNbits versteckt das alles bereits.

### 6. Reporting / Buchhaltung

LNbits hat eingebaute Transaction-Liste mit Filter + CSV-Export. Für Honorar-Berichte oder Steuer-Vorbereitung können wir einfach via LNbits-API alle Zahlungen pro Wallet ziehen + auf Nostr-Events joinen (welche BCF-Topic hat welchen Sat-Eingang erzeugt).

---

## Was unsere Verkabelungs-Tools sein müssen

Pro Integrationspunkt brauchen wir genau einen Adapter — alle klein:

| Adapter | Aufgabe | Größe |
|---|---|---|
| `lnbits-client.js` | LNURL-P-Link erzeugen, Wallet-Info holen | ~80 LoC |
| `lnbits-webhook.py` | Webhook empfangen → Nostr-Event publishen | ~50 LoC |
| `nwc-helper.js` | NWC-URI parsen, Pay-Request senden | NDK kann das bereits |
| `wallet-provisioning.py` | Admin-API für Wallet-Anlage | ~60 LoC |

Insgesamt unter 250 Zeilen Klebstoff.

---

## Konkrete Aktionen für Backend-Setup

In der `BACKEND-SETUP.md` (kommt als nächstes) folgender Compose-Service hinzu:

```yaml
lnbits:
  image: lnbitsdocker/lnbits-legend:latest
  restart: unless-stopped
  ports:
    - "5000:5000"
  volumes:
    - ./lnbits-data:/app/data
  environment:
    - LNBITS_BACKEND_WALLET_CLASS=LndRestWallet  # oder PhoenixdWallet / VoltageWallet
    - LND_REST_ENDPOINT=https://your-lnd:8080
    - LND_REST_MACAROON=base64...
    - LNBITS_SITE_TITLE=Sovereign AEC Treasury
    - LNBITS_ADMIN_USERS=<your-lnbits-user-id>
    - LNBITS_ALLOWED_USERS=<comma-list>
```

Anfangs lokal mit LNbits Eingebauter SQLite und einem Phoenixd-Wallet im selben Container — Null-Setup für Pilot. Später auf eigenen LND switchen, wenn echte Beträge fließen.

LNbits-URL: `http://localhost:5000`. Caddy davor für TLS sobald öffentlich nötig.

---

## Sicherheit / Verantwortung

- **Wallet-Keys auf dem Laptop** sind ein Risiko. Pilot: Nur kleine Beträge (max. paar k sats für Tests). Reale Wertströme später auf gehärtete Infrastruktur (eigener Server, eigenes LND-Node).
- **Multi-Sig / Cosign:** LNbits hat keinen nativen Cosign, das machen wir später via Frostr-Layer auf Nostr (Approval-Multi-Sig auf das Pay-Trigger-Event).
- **Audit-Trail:** alle Zahlungen erzeugen via Webhook ein `kind:9735` auf dem Relay → Buchhaltung lebt auf der Timechain-/Nostr-Schicht, nicht nur in LNbits.

---

## Open Questions

1. **Wallet-Backend-Wahl** — Phoenixd (selbsthostend, simpel, automatisches Channel-Management) vs. eigener LND (mehr Kontrolle, mehr Aufwand) vs. Voltage Cloud (gehostet, schnell, kostet)? Empfehlung für Pilot: Phoenixd.
2. **Wer hostet LNbits für den Pilot?** the maintainer's Laptop ist OK für Test. Für Provinz-Bozen-Demo lieber auf einen Hetzner-Mini-VPS oder NOI-Techpark-Hosting umziehen — Stromausfall an deinem Schreibtisch sollte nicht den Pilot abschießen.
3. **Cashu sofort oder später?** Cashu-Mint via LNbits-Extension ist mit wenig Aufwand machbar. Use-Case: anonyme Sub-Zahlungen im Büro, Bedarfsplanungs-DVM-Escrow. Empfehlung: nicht im Sprint, aber als Phase-2-Knopf bereithalten.
4. **DSFA für LNbits?** Wenn nur die Adminin und Tester drauf sind: kein personenbezogenes Datenproblem. Bei realen Beteiligten muss in der DSFA stehen, dass LN-Zahlungs-Metadaten anfallen.

---

*LNbits ist genau das, was Prinzip 1 verspricht: ein reifes OSS-Tool mit besserer UX als alles, was wir selbst bauen könnten. Wir verkabeln, sie liefern.*
