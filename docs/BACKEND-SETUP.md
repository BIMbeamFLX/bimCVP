# Sovereign AEC — Backend Setup

**Zweck.** Reproduzierbarer Docker-Compose-Stack mit Nostr-Relay (strfry), Blossom-Server, LNbits und Caddy als Reverse-Proxy. Setup für Pilot auf einem Linux-Laptop oder einem kleinen VPS. Ziel: in unter 30 Minuten lauffähig, OpenClaw-automatisierbar.

**Adressat.** OpenClaw / Claude Code auf dem Pilot-Laptop. Jeder Schritt ist atomar, mit Verifikation. Bei Verifikations-Fehler stoppen und Logs zurückmelden.

**Prinzipien-Bezug.** Folgt `PRINCIPLES.md`: wir installieren reife OSS-Komponenten, schreiben nur Konfiguration, keine eigene Lightning-/Relay-/Storage-Implementierung.

---

## 0. Voraussetzungen prüfen

```bash
docker --version          # >= 24.x
docker compose version    # v2.x
openssl version           # any recent
curl --version            # any recent
jq --version              # für Tests
```

Falls einer fehlt:

```bash
# Debian/Ubuntu
sudo apt-get update
sudo apt-get install -y docker.io docker-compose-plugin curl jq openssl
sudo usermod -aG docker $USER
# nach usermod neu einloggen
```

**Test:**

```bash
docker run --rm hello-world
```

Muss erfolgreich durchlaufen.

---

## 1. Repository-Struktur

```bash
mkdir -p ~/sovereign-aec-backend/{strfry/data,strfry/conf,blossom/data,blossom/config,lnbits/data,caddy/data,caddy/config}
cd ~/sovereign-aec-backend
```

Verzeichnis-Baum nachher:

```
sovereign-aec-backend/
├── docker-compose.yml
├── .env                    # secrets, NICHT committen
├── Caddyfile
├── strfry/
│   ├── conf/strfry.conf
│   └── data/
├── blossom/
│   ├── config/config.yml
│   └── data/
├── lnbits/
│   ├── .env
│   └── data/
└── caddy/
    ├── data/
    └── config/
```

---

## 2. Globales `.env` erzeugen

```bash
cat > .env <<'EOF'
# Sovereign AEC Backend — globale Konfiguration
# NICHT committen, NICHT teilen.

# Domain (optional — für TLS via Caddy). Leer lassen für localhost-only.
SAEC_DOMAIN=

# Admin-Pubkey (Hex 64 Zeichen). Wird Whitelist-Eintrag in Relay + Blossom + LNbits.
SAEC_ADMIN_PUBKEY=

# LNbits — wird beim ersten Boot über die UI gesetzt. Leer lassen.
LNBITS_SUPER_USER_ID=

# Ports — Defaults sind OK
STRFRY_PORT=7777
BLOSSOM_PORT=3000
LNBITS_PORT=5000
CADDY_HTTP_PORT=80
CADDY_HTTPS_PORT=443
EOF
chmod 600 .env
```

**Aktion vor weiter:** Felix' Admin-pubkey eintragen. Falls noch nicht da:

```bash
# In keys.html (Browser) generieren ODER mit nostril:
docker run --rm ghcr.io/jb55/nostril:latest --hex
# Output kopieren in SAEC_ADMIN_PUBKEY in .env
```

---

## 3. `docker-compose.yml`

```bash
cat > docker-compose.yml <<'EOF'
services:
  strfry:
    image: dockurr/strfry:latest
    container_name: saec-strfry
    restart: unless-stopped
    ports:
      - "${STRFRY_PORT:-7777}:7777"
    volumes:
      - ./strfry/data:/app/strfry-db
      - ./strfry/conf/strfry.conf:/etc/strfry.conf:ro
    environment:
      - STRFRY_CONFIG=/etc/strfry.conf

  blossom:
    image: ghcr.io/hzrd149/blossom-server:latest
    container_name: saec-blossom
    restart: unless-stopped
    ports:
      - "${BLOSSOM_PORT:-3000}:3000"
    volumes:
      - ./blossom/data:/app/data
      - ./blossom/config/config.yml:/app/config.yml:ro

  lnbits:
    image: lnbitsdocker/lnbits-legend:latest
    container_name: saec-lnbits
    restart: unless-stopped
    ports:
      - "${LNBITS_PORT:-5000}:5000"
    volumes:
      - ./lnbits/data:/app/data
    env_file:
      - ./lnbits/.env

  caddy:
    image: caddy:2
    container_name: saec-caddy
    restart: unless-stopped
    ports:
      - "${CADDY_HTTP_PORT:-80}:80"
      - "${CADDY_HTTPS_PORT:-443}:443"
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile:ro
      - ./caddy/data:/data
      - ./caddy/config:/config
    depends_on:
      - strfry
      - blossom
      - lnbits

networks:
  default:
    name: saec
EOF
```

---

## 4. strfry-Konfiguration

```bash
cat > strfry/conf/strfry.conf <<'EOF'
# strfry — Sovereign AEC Pilot
db = "/app/strfry-db"

relay {
    bind = "0.0.0.0"
    port = 7777

    nofiles = 1024000
    realIpHeader = "x-forwarded-for"

    info {
        name = "Sovereign AEC Pilot Relay"
        description = "Pilot-Relay für BCF, IFC, Bautagebuch, Gebäudebuch."
        pubkey = ""
        contact = ""
        software = "git+https://github.com/hoytech/strfry.git"
        version = ""
    }

    maxWebsocketPayloadSize = 1048576

    autoPingSeconds = 55

    enableTcpKeepalive = true

    queryTimesliceBudgetMicroseconds = 10000

    maxFilterLimit = 500

    maxSubsPerConnection = 20

    writePolicy {
        # plugin = "/etc/whitelist.sh"   # Aktivieren für Pubkey-Whitelist (siehe 8.2)
    }

    compression {
        enabled = true
        slidingWindow = true
    }

    logging {
        dumpInAll = false
        dumpInEvents = false
        dumpInReqs = false
        dbScanPerf = false
        invalidEvents = true
    }

    numThreads {
        ingester = 3
        reqWorker = 3
        reqMonitor = 3
        yesstr = 1
    }
}

events {
    maxEventSize = 65536
    rejectEventsNewerThanSeconds = 900
    rejectEventsOlderThanSeconds = 94608000
    rejectEphemeralEventsOlderThanSeconds = 60
    ephemeralEventsLifetimeSeconds = 300
    maxNumTags = 2000
    maxTagValSize = 1024
}
EOF
```

**Notiz:** writePolicy ist initial offen — jeder kann publishen. Sobald Pilot-Phase, Whitelist via Plugin aktivieren (siehe 8.2).

---

## 5. Blossom-Konfiguration

```bash
cat > blossom/config/config.yml <<'EOF'
publicDomain: http://localhost:3000

databasePath: /app/data/sqlite.db

storage:
  backend: local
  local:
    dir: /app/data/blobs

cache:
  maxSize: 100MB

upload:
  enabled: true
  requireAuth: true
  # leere Liste = jeder authentifizierte Pubkey darf hochladen
  # für Tightening: liste explizit npub-Hex auf
  allowList: []
  blockList: []
  mimeTypeBlocklist:
    - text/html
  mimeTypeAllowlist:
    - application/x-step          # IFC
    - application/octet-stream
    - image/png
    - image/jpeg
    - image/svg+xml
    - image/webp
    - application/pdf
    - application/json
    - text/plain
    - text/markdown
  maxFileSize: 524288000          # 500 MB

list:
  requireAuth: false

download:
  requireAuth: false

discovery:
  upstreams: []

EOF
```

---

## 6. LNbits-Konfiguration

```bash
cat > lnbits/.env <<'EOF'
# LNbits — Sovereign AEC Pilot
# Doku: https://github.com/lnbits/lnbits

# Wallet-Backend
LNBITS_BACKEND_WALLET_CLASS=FakeWallet
FAKE_WALLET_SECRET=changeme-saec-pilot

# UI
LNBITS_SITE_TITLE="Sovereign AEC Treasury"
LNBITS_SITE_TAGLINE="Pilot Wallet"
LNBITS_DENOMINATION=sats

# Datenbank (SQLite reicht für Pilot)
LNBITS_DATA_FOLDER=/app/data
LNBITS_DATABASE_URL=sqlite:///app/data/database.sqlite3

# Extensions die wir brauchen
LNBITS_EXTENSIONS_DEFAULT_INSTALL=invoices,lnurlp,satspay,splitpayments,nostrnwc,cashu

# Theme
LNBITS_DEFAULT_THEME=monochrome
LNBITS_AD_SPACE_ENABLED=false

# Network
HOST=0.0.0.0
PORT=5000

# Security
LNBITS_RATE_LIMIT_NO=10/minute
LNBITS_ALLOWED_USERS=  # wird nach 1. Boot gesetzt

EOF
chmod 600 lnbits/.env
```

**Hinweis:** `FakeWallet` für Setup-Test. Switch auf echtes Wallet (Phoenixd / LND) in Schritt 11.

---

## 7. Caddyfile

**Variante A — lokal nur, ohne Domain:**

```bash
cat > Caddyfile <<'EOF'
{
    admin off
    auto_https off
}

:80 {
    handle /relay* {
        reverse_proxy strfry:7777
    }
    handle /blossom* {
        reverse_proxy blossom:3000
    }
    handle /wallet* {
        reverse_proxy lnbits:5000
    }
    handle {
        respond "Sovereign AEC Backend. Reach via /relay, /blossom, /wallet" 200
    }
}
EOF
```

**Variante B — mit eigener Domain (sobald Pilot öffentlich geht):**

Variante A erst, Variante B kommt in Schritt 12.

---

## 8. Erster Boot

```bash
docker compose pull
docker compose up -d
```

**Verifikation (jeder Punkt muss OK):**

```bash
# Container alle laufend?
docker compose ps
# Erwartete State: Up für strfry, blossom, lnbits, caddy

# Strfry-Relay erreichbar?
curl -s -H 'Accept: application/nostr+json' http://localhost:7777 | jq .name
# Erwartet: "Sovereign AEC Pilot Relay"

# Blossom erreichbar?
curl -s http://localhost:3000/ | head -c 200
# Erwartet: HTML-Response oder JSON-Status

# LNbits erreichbar?
curl -s http://localhost:5000/ -o /dev/null -w "%{http_code}\n"
# Erwartet: 200 oder 307

# Caddy-Gateway?
curl -s http://localhost:80/ -o /dev/null -w "%{http_code}\n"
# Erwartet: 200
```

Bei Fehler:

```bash
docker compose logs --tail=50 <service>
```

zeigt die Logs und an OpenClaw zurückmelden.

---

## 9. Initial-Provisioning

### 9.1 LNbits Super-User anlegen

```bash
# Im Browser öffnen:
open http://localhost:5000/wallet
# (Linux: xdg-open ...)
```

Erster Aufruf legt automatisch eine Wallet an. URL-Hash in der Adresszeile enthält die User-ID. Diese ID jetzt sichern:

```bash
# User-ID aus Browser kopieren, dann:
read -p "LNbits User-ID aus URL eingeben: " UID
sed -i "s|LNBITS_SUPER_USER_ID=.*|LNBITS_SUPER_USER_ID=$UID|" .env
echo "LNBITS_SUPER_USER_ID gesetzt: $UID"
```

Diese User-ID ist dein Admin-Account. Bookmark setzen, nicht verlieren.

### 9.2 Test-Event in strfry publishen

```bash
docker run --rm --network saec ghcr.io/jb55/nostril:latest \
    --sec $(openssl rand -hex 32) \
    --kind 1 \
    --content "saec-backend setup test" | \
docker run --rm -i --network saec ghcr.io/jb55/nak:latest event ws://strfry:7777
```

Erwartet: keine Fehler. Event landet in strfry-DB.

### 9.3 Test-Read von strfry

```bash
docker run --rm --network saec ghcr.io/jb55/nak:latest req -k 1 --limit 5 ws://strfry:7777
```

Erwartet: liefert das eben gepostete Event zurück (eventuell mehr, falls Multi-Tests).

### 9.4 Test-Upload zu Blossom

Aus dem Browser einfacher — mit `keys.html` oder über die LNbits-Wallet-UI mit der Blossom-Extension. CLI-Test:

```bash
# Mit Felix's Admin-nsec (kurz eintippen, danach `history -d $((HISTCMD-1))` zum löschen)
read -s -p "ADMIN-NSEC: " NSEC
echo

# Mit blossom-cli oder einem kleinen Python-Snippet — siehe ingest.py
# Hier nur Connectivity-Test:
curl -s http://localhost:3000/list/$(echo $NSEC | xxd -p | head -c 64)
# (kann leer sein wenn noch nichts hochgeladen)
```

---

## 10. DSFA-Skelett (GDPR Art. 35)

Pflicht-Doku, wenn personenbezogene Daten verarbeitet werden — also sobald reale Beteiligte mitmachen. Skeleton-Datei anlegen:

```bash
cat > DSFA.md <<'EOF'
# Datenschutz-Folgenabschätzung — Sovereign AEC Pilot

## 1. Verantwortlicher
Felix Hitthaler, [Adresse], hitthaler@bimbeam.at

## 2. Zweck der Verarbeitung
Koordinations- und Dokumentationsdaten eines Bauprojekts (Pilot Building).

## 3. Datenkategorien
- pubkey (npub) — pseudonyme Identität, kein Echtname obligat
- Profile-Metadaten (Name, Funktionsbezeichnung) wenn freiwillig hinterlegt
- Bau-Koordinations-Inhalte (BCF Topics, Comments, IFC-Modelle)
- Zahlungsdaten via Lightning (Payment-Hashes, kein Klarname)
- Tagebucheinträge (Wetter, Lieferungen, Personal-Anwesenheit nur als Anzahl)

## 4. Empfänger / Verarbeiter
- Selbst-betriebenes strfry-Relay (local)
- Selbst-betriebener Blossom-Server (local)
- Selbst-betriebener LNbits-Instanz (local)
- Bei öffentlichem Pilot: ggf. Hetzner / NOI Techpark als Hosting-Provider mit AVV

## 5. Aufbewahrungsdauer
- Projekt-Daten: lebenslang (Audit-/Gewährleistungs-relevant)
- Test-Daten: 30 Tage nach Pilot-Ende

## 6. Betroffenenrechte
- Profil-Löschung: NIP-09 Delete (best-effort über Relays)
- Auskunft: per Event-Filter aus dem Relay-DB
- Recht auf Vergessenwerden: Hard-Delete auf eigener Relay-DB möglich

## 7. TOM (Technische und Organisatorische Maßnahmen)
- TLS für alle Verbindungen
- Pubkey-Whitelist auf Relay + Blossom
- Backups verschlüsselt (LUKS)
- Zugriff auf Server nur über SSH-Key
- Logs minimal

## 8. Risiko-Bewertung
- Re-Identifikation über pubkey: mittel, dadurch dass Beteiligte freiwillig ihren Klarnamen in den Profil-Events öffentlichen
- Mitigation: Empfehlung an Beteiligte, pseudonyme Profile zu verwenden

## 9. Konsultation Aufsichtsbehörde
- Italien: Garante per la protezione dei dati personali
- Vor öffentlichem Pilot-Start informieren falls > 100 Datensätze
EOF
```

OpenClaw bitte: NICHT veröffentlichen. Wird mit dem Pilotpartner gemeinsam finalisiert.

---

## 11. Wallet-Backend wechseln (von FakeWallet zu echt)

**Sobald echte Sats fließen sollen** — am einfachsten Phoenixd:

```bash
# Phoenixd in den Stack
cat >> docker-compose.yml <<'EOF'

  phoenixd:
    image: thealtsstreet/phoenixd:latest
    container_name: saec-phoenixd
    restart: unless-stopped
    volumes:
      - ./phoenixd/data:/data
    environment:
      - HTTP_BIND_IP=0.0.0.0
EOF

# LNbits umkonfigurieren:
sed -i "s|LNBITS_BACKEND_WALLET_CLASS=FakeWallet|LNBITS_BACKEND_WALLET_CLASS=PhoenixdWallet|" lnbits/.env
echo "PHOENIXD_API_ENDPOINT=http://phoenixd:9740" >> lnbits/.env
echo "PHOENIXD_API_PASSWORD=$(openssl rand -hex 32)" >> lnbits/.env

docker compose up -d phoenixd lnbits
```

**Hinweis:** Phoenixd ohne expliziten Kanal-Setup geht direkt — Acinq managed die Channels. Für Pilot sehr gut, für Hochlast-Anwendungen später eigener LND.

---

## 12. Öffentliche Domain einrichten (wenn Pilot extern erreichbar sein muss)

Sobald eine Domain (z. B. `pilot.bimbeam.at`) auf den Server zeigt:

```bash
# DNS A-Record auf Server-IP zeigend, dann:
sed -i "s|SAEC_DOMAIN=.*|SAEC_DOMAIN=pilot.bimbeam.at|" .env

# Caddyfile auf Variante B
cat > Caddyfile <<EOF
relay.${SAEC_DOMAIN} {
    reverse_proxy strfry:7777
}

blossom.${SAEC_DOMAIN} {
    reverse_proxy blossom:3000
    header Access-Control-Allow-Origin "*"
}

wallet.${SAEC_DOMAIN} {
    reverse_proxy lnbits:5000
}

${SAEC_DOMAIN} {
    respond "Sovereign AEC Pilot. Subdomains: relay, blossom, wallet." 200
}
EOF

docker compose restart caddy
```

Caddy holt sich automatisch Let's-Encrypt-Zertifikate.

---

## 13. Backups

Volumes pro Service unterscheidlich sensibel.

```bash
# Backup-Skript
cat > backup.sh <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
DEST=~/saec-backups/$(date +%Y-%m-%d_%H%M%S)
mkdir -p "$DEST"
docker compose stop
tar czf "$DEST/strfry-db.tar.gz" strfry/data
tar czf "$DEST/blossom-data.tar.gz" blossom/data
tar czf "$DEST/lnbits-data.tar.gz" lnbits/data
cp .env "$DEST/.env"
cp lnbits/.env "$DEST/lnbits.env"
docker compose up -d
echo "Backup in $DEST"
EOF
chmod +x backup.sh
```

**Cron-Empfehlung:** täglich um 03:00.

```bash
crontab -e
# füge ein:
# 0 3 * * * cd ~/sovereign-aec-backend && ./backup.sh > /var/log/saec-backup.log 2>&1
```

**Wichtig:** LNbits-`.env` enthält Wallet-Secrets. Sichere die separat (z. B. auf USB-Stick + Tresor) sobald echte Sats drauf sind.

---

## 14. Troubleshooting (häufige Fälle)

### Relay verbindet nicht (Client sagt „Connection refused")
- `docker compose ps` — läuft strfry?
- `docker compose logs strfry --tail=30`
- Port-Konflikt? `ss -tlnp | grep 7777`
- Firewall? `sudo ufw status` — Port 7777 frei?

### Blossom rejects Upload mit 401
- Auth-Event vom Client hat falsche Signatur oder ist abgelaufen (>5 min)
- `requireAuth: false` in config.yml temporär setzen für Test
- Allow-List leer = jeder Pubkey OK; gefüllt → eigener npub ergänzen

### LNbits zeigt „connection error" zur Wallet
- FakeWallet ist standardmäßig OK; wenn Phoenixd: Container läuft?
- `docker compose logs lnbits | grep -i wallet`

### Caddy bekommt kein TLS-Zertifikat
- DNS noch nicht propagiert? `dig pilot.bimbeam.at`
- Port 80 + 443 von außen erreichbar? Test via `https://check-your-website.server-daten.de`
- Caddy-Logs: `docker compose logs caddy --tail=50`

---

## 15. Nächste Schritte (nach erfolgreichem Setup)

OpenClaw soll Felix berichten:

1. **Status-Übersicht** — alle vier Container laufen, Verifikations-Tests grün.
2. **LNbits-User-ID** — gesichert in `.env`, Bookmark in Browser.
3. **Admin-pubkey** — eingetragen, kann Events publishen + Blossom-Uploads.
4. **DSFA.md** — Skeleton vorhanden, Lücken für Pilotpartner markiert.
5. **Offene Konfig-Punkte** — falls etwas im Setup übersprungen werden musste.

Danach kann Felix:

- `character.html` aufrufen, Relay-URL = `ws://localhost:7777`, Blossom-URL = `http://localhost:3000` eintragen
- `admin.html` öffnen, erstes Projekt anlegen
- `ingest.py` gegen das eigene Setup laufen lassen für IFC-Hochlade-Test
- LNbits-Wallet öffnen, erste Test-Invoice generieren

---

## 16. Pilot-Zielarchitektur (freigegeben 2026-05)

Ersetzt das Laptop-+-Tailscale-Setup. Verbindlich ergänzend zu
`identity-architecture.md`. Laptop/Tailscale entfällt fürs Backend; Tailscale
bleibt höchstens Admin-Zugang zum VPS.

### 16.1 Server & Storage

- **Hetzner Cloud CX23** (2 vCPU x86, 4 GB RAM, 40 GB, ≈ €4,49/Mon),
  Ubuntu 24.04 + Docker. EU-Standort (DSGVO/DSFA — Custodial-Keys bleiben in der EU).
- **Hetzner Volume bei Bedarf** (~€0,044/GB/Mon) für Blossom/IFC-Blobs, erst
  angehängt wenn das Blob-Wachstum es braucht. Hält große IFC-Daten getrennt von
  Relay-DB / LNbits / phoenixd — Blob-Wachstum kann die Money-/Key-Box nie
  volllaufen lassen. Server-Resize (RAM/CPU) später möglich; x86 gewählt, weil
  ARM↔x86 nicht tauschbar.

### 16.2 DNS (Domains bei World4You; `bimbeam.at` NICHT anfassen — Mail)

Domain-Split (deckt sich mit `BRAND.md`): **gemeinwert.com** = Marken-Website
(DACH, menschliches Publikum). **bimcvp.com** = Protokoll/Identity/Services
(international, Dev/NIP). Kein 301 — sie cross-linken. Beide via demselben
Hetzner-Caddy.

| Record | Ziel |
|---|---|
| `gemeinwert.com` @ / `www`  A | VPS-IP (Marken-Website) |
| `bimcvp.com` @ / `www`  A     | VPS-IP (Protokoll-Hub + NIP-05) |
| `relay.bimcvp.com`  A         | VPS-IP |
| `pay.bimcvp.com`    A         | VPS-IP |
| `blossom.bimcvp.com` A        | VPS-IP |
| `bunker.bimcvp.com` A         | VPS-IP (Phase 2) |

NIP-05/Lightning-Address-Handles sind `name@bimcvp.com` (well-known auf dem
bimcvp.com-Apex via Caddy → LNbits `nostrnip5`). Caddy macht Auto-TLS für alle.

### 16.3 Container auf dem VPS

- `caddy` — Reverse Proxy / TLS; serviert `gemeinwert.com` (statische Site) und
  `bimcvp.com` (Protokoll-Hub + NIP-05). Kein GitHub Pages.
- `strfry` **public** → `wss://relay.bimcvp.com`, **Write-Policy-Plugin aktiv**
  (nur Pilot-Pubkeys bzw. Events mit Projekt-`a`-Tag `30902:<pubkey>:<guid>`;
  vgl. Abschnitt strfry `writePolicy`). Pflicht bevor öffentlich.
- `strfry` **private** (optional, anfangs aufschiebbar) — 2. Container, nur
  localhost/tailnet, eigene DB + Write-Policy. Interner WIP-Layer (PRINCIPLES §4).
- `lnbits` → `https://pay.bimcvp.com` — **stock, reine Wallet-Engine** (kein Fork).
  Backend `LNBITS_BACKEND_WALLET_CLASS=PhoenixdWallet` → `http://phoenixd:9740`.
  Extensions aktiv: `usermanager`, `nostrnwc`, `lnurlp`, `nostrnip5`
  (bestehende `invoices, satspay, splitpayments, cashu` bleiben). Nicht
  aktivierte Extensions sind inert — nichts zu „strippen", kein Fork.
- `bunker` — NIP-46-Signer → `wss://bunker.bimcvp.com`, custodiert Tier-1-Keys.
  Pilot: `nak bunker` (fiatjaf `nak`); abstrahiert, damit Knox/nsec.app es ohne
  Frontend-Änderung ersetzen kann. Bei ~5–10 Usern Ansatz re-validieren.
- `blossom` → `https://blossom.bimcvp.com` (Blobs ggf. auf Volume).
- `phoenixd` — LNbits-Funding, nur intern `:9740`. Minimal mit Test-Sats funden.

### 16.4 Per-User-Provisioning (Tier 1)

Ein dünner server-seitiger `provision`-Glue (einzige Eigenbau-Komponente, **nicht
im public Web-Repo**) erzeugt in einem Flow: LNbits-User+Wallet (UserManager-API)
→ Managed Nostr-Key im Bunker → Lightning-Address `name@bimcvp.com`
(lnurlp+nostrnip5 auf dem bimcvp.com-Apex, dient auch als NIP-05)
→ NWC-Connection (`nostrnwc`).
Mapping-Tabelle nur Identity-Plumbing: `lnbits_user_id ↔ npub ↔ bunker_ref ↔
lightning_address` — keine Rollen, keine BIM-Daten (Projekt-Mitgliedschaft bleibt
event-definiert in `kind:30902`). Keystore verschlüsselt, Operator-Key offline →
das ist die Trust-Boundary (siehe `identity-architecture.md`; DSFA Abschnitt 3
ergänzen: Datenkategorie „custodial Nostr-Keys", Operator als Verarbeiter).

### 16.5 Recovery (Kurzfassung — Details in identity-architecture.md)

Key verloren ≠ Key kompromittiert. Verlust: LNbits-Login → neuer Bunker-Token →
**gleicher npub**, Admin kann LNbits-Credential resetten (UserManager), Key bleibt.
Kompromittierung: neuer npub + Admin-Re-Link in `kind:30902` (Path-C-Semantik) —
dieser Pfad bleibt implementiert und getestet.

---

*Stand: v0.1. Pilot-tauglich. Production-Hardening (Backups offsite, Monitoring, automated Updates) im Phase-2-Plan.*
