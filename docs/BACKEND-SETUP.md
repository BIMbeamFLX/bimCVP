# Sovereign AEC — Backend Setup

**Purpose.** Reproducible Docker Compose stack with a Nostr relay (strfry), Blossom server, LNbits and Caddy as a reverse proxy. Setup for the pilot on a Linux laptop or a small VPS. Goal: running in under 30 minutes, automatable by OpenClaw.

**Audience.** OpenClaw / Claude Code on the pilot laptop. Every step is atomic, with verification. On a verification failure, stop and report the logs back.

**Principles reference.** Follows `PRINCIPLES.md`: we install mature OSS components and only write configuration, no custom Lightning/relay/storage implementation.

---

## 0. Check prerequisites

```bash
docker --version          # >= 24.x
docker compose version    # v2.x
openssl version           # any recent
curl --version            # any recent
jq --version              # for tests
```

If one is missing:

```bash
# Debian/Ubuntu
sudo apt-get update
sudo apt-get install -y docker.io docker-compose-plugin curl jq openssl
sudo usermod -aG docker $USER
# log out and back in after usermod
```

**Test:**

```bash
docker run --rm hello-world
```

Must complete successfully.

---

## 1. Repository structure

```bash
mkdir -p ~/sovereign-aec-backend/{strfry/data,strfry/conf,blossom/data,blossom/config,lnbits/data,caddy/data,caddy/config}
cd ~/sovereign-aec-backend
```

Directory tree afterwards:

```
sovereign-aec-backend/
├── docker-compose.yml
├── .env                    # secrets, do NOT commit
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

## 2. Create the global `.env`

```bash
cat > .env <<'EOF'
# Sovereign AEC Backend — global configuration
# Do NOT commit, do NOT share.

# Domain (optional — for TLS via Caddy). Leave empty for localhost-only.
SAEC_DOMAIN=

# Admin pubkey (hex, 64 chars). Becomes the whitelist entry in relay + Blossom + LNbits.
SAEC_ADMIN_PUBKEY=

# LNbits — set on first boot via the UI. Leave empty.
LNBITS_SUPER_USER_ID=

# Ports — defaults are OK
STRFRY_PORT=7777
BLOSSOM_PORT=3000
LNBITS_PORT=5000
CADDY_HTTP_PORT=80
CADDY_HTTPS_PORT=443
EOF
chmod 600 .env
```

**Action before continuing:** enter Felix' admin pubkey. If it does not exist yet:

```bash
# Generate in keys.html (browser) OR with nostril:
docker run --rm ghcr.io/jb55/nostril:latest --hex
# Copy the output into SAEC_ADMIN_PUBKEY in .env
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

## 4. strfry configuration

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
        description = "Pilot relay for BCF, IFC, construction log, building book."
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
        # plugin = "/etc/whitelist.sh"   # Enable for pubkey whitelist (see 8.2)
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

**Note:** the writePolicy is initially open — anyone can publish. Once the pilot phase starts, enable the whitelist via the plugin (see 8.2).

---

## 5. Blossom configuration

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
  # empty list = any authenticated pubkey may upload
  # to tighten: list npub hex values explicitly
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

## 6. LNbits configuration

```bash
cat > lnbits/.env <<'EOF'
# LNbits — Sovereign AEC Pilot
# Docs: https://github.com/lnbits/lnbits

# Wallet backend
LNBITS_BACKEND_WALLET_CLASS=FakeWallet
FAKE_WALLET_SECRET=changeme-saec-pilot

# UI
LNBITS_SITE_TITLE="Sovereign AEC Treasury"
LNBITS_SITE_TAGLINE="Pilot Wallet"
LNBITS_DENOMINATION=sats

# Database (SQLite is enough for the pilot)
LNBITS_DATA_FOLDER=/app/data
LNBITS_DATABASE_URL=sqlite:///app/data/database.sqlite3

# Extensions we need
LNBITS_EXTENSIONS_DEFAULT_INSTALL=invoices,lnurlp,satspay,splitpayments,nostrnwc,cashu

# Theme
LNBITS_DEFAULT_THEME=monochrome
LNBITS_AD_SPACE_ENABLED=false

# Network
HOST=0.0.0.0
PORT=5000

# Security
LNBITS_RATE_LIMIT_NO=10/minute
LNBITS_ALLOWED_USERS=  # set after the 1st boot

EOF
chmod 600 lnbits/.env
```

**Note:** `FakeWallet` is for the setup test. Switch to a real wallet (Phoenixd / LND) in step 11.

---

## 7. Caddyfile

**Variant A — local only, without a domain:**

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

**Variant B — with your own domain (once the pilot goes public):**

Variant A first, Variant B comes in step 12.

---

## 8. First boot

```bash
docker compose pull
docker compose up -d
```

**Verification (every point must be OK):**

```bash
# All containers running?
docker compose ps
# Expected state: Up for strfry, blossom, lnbits, caddy

# Strfry relay reachable?
curl -s -H 'Accept: application/nostr+json' http://localhost:7777 | jq .name
# Expected: "Sovereign AEC Pilot Relay"

# Blossom reachable?
curl -s http://localhost:3000/ | head -c 200
# Expected: HTML response or JSON status

# LNbits reachable?
curl -s http://localhost:5000/ -o /dev/null -w "%{http_code}\n"
# Expected: 200 or 307

# Caddy gateway?
curl -s http://localhost:80/ -o /dev/null -w "%{http_code}\n"
# Expected: 200
```

On failure:

```bash
docker compose logs --tail=50 <service>
```

shows the logs; report them back to OpenClaw.

---

## 9. Initial provisioning

### 9.1 Create the LNbits super user

```bash
# Open in the browser:
open http://localhost:5000/wallet
# (Linux: xdg-open ...)
```

The first call automatically creates a wallet. The URL hash in the address bar contains the user ID. Save this ID now:

```bash
# Copy the user ID from the browser, then:
read -p "Enter the LNbits user ID from the URL: " UID
sed -i "s|LNBITS_SUPER_USER_ID=.*|LNBITS_SUPER_USER_ID=$UID|" .env
echo "LNBITS_SUPER_USER_ID set: $UID"
```

This user ID is your admin account. Bookmark it, do not lose it.

### 9.2 Publish a test event to strfry

```bash
docker run --rm --network saec ghcr.io/jb55/nostril:latest \
    --sec $(openssl rand -hex 32) \
    --kind 1 \
    --content "saec-backend setup test" | \
docker run --rm -i --network saec ghcr.io/jb55/nak:latest event ws://strfry:7777
```

Expected: no errors. The event lands in the strfry DB.

### 9.3 Test read from strfry

```bash
docker run --rm --network saec ghcr.io/jb55/nak:latest req -k 1 --limit 5 ws://strfry:7777
```

Expected: returns the event just posted (possibly more, in case of multiple tests).

### 9.4 Test upload to Blossom

Easier from the browser — with `keys.html` or via the LNbits wallet UI using the Blossom extension. CLI test:

```bash
# With Felix's admin nsec (type it briefly, then `history -d $((HISTCMD-1))` to delete it)
read -s -p "ADMIN-NSEC: " NSEC
echo

# With blossom-cli or a small Python snippet — see ingest.py
# Connectivity test only here:
curl -s http://localhost:3000/list/$(echo $NSEC | xxd -p | head -c 64)
# (may be empty if nothing has been uploaded yet)
```

---

## 10. DPIA skeleton (GDPR Art. 35)

Mandatory documentation when personal data is processed — that is, as soon as real participants take part. Create the skeleton file:

```bash
cat > DSFA.md <<'EOF'
# Data Protection Impact Assessment — Sovereign AEC Pilot

## 1. Controller
Felix Hitthaler, [address], hitthaler@bimbeam.at

## 2. Purpose of processing
Coordination and documentation data of a construction project (pilot building).

## 3. Data categories
- pubkey (npub) — pseudonymous identity, no real name mandatory
- profile metadata (name, role title) if provided voluntarily
- construction coordination content (BCF topics, comments, IFC models)
- payment data via Lightning (payment hashes, no clear name)
- log entries (weather, deliveries, staff attendance only as a count)

## 4. Recipients / processors
- self-operated strfry relay (local)
- self-operated Blossom server (local)
- self-operated LNbits instance (local)
- for a public pilot: possibly Hetzner / NOI Techpark as a hosting provider with a data processing agreement

## 5. Retention period
- project data: for life (audit / warranty relevant)
- test data: 30 days after the pilot ends

## 6. Data subject rights
- profile deletion: NIP-09 delete (best-effort across relays)
- access: via event filter from the relay DB
- right to be forgotten: hard delete on the own relay DB is possible

## 7. TOM (technical and organisational measures)
- TLS for all connections
- pubkey whitelist on relay + Blossom
- backups encrypted (LUKS)
- server access only via SSH key
- minimal logs

## 8. Risk assessment
- re-identification via pubkey: medium, because participants voluntarily make their clear name public in the profile events
- mitigation: recommend participants use pseudonymous profiles

## 9. Consultation with the supervisory authority
- Italy: Garante per la protezione dei dati personali
- inform before a public pilot start if > 100 records
EOF
```

OpenClaw, please: do NOT publish. It will be finalised together with the pilot partner.

---

## 11. Switch the wallet backend (from FakeWallet to a real one)

**As soon as real sats should flow** — Phoenixd is the easiest:

```bash
# Phoenixd into the stack
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

# Reconfigure LNbits:
sed -i "s|LNBITS_BACKEND_WALLET_CLASS=FakeWallet|LNBITS_BACKEND_WALLET_CLASS=PhoenixdWallet|" lnbits/.env
echo "PHOENIXD_API_ENDPOINT=http://phoenixd:9740" >> lnbits/.env
echo "PHOENIXD_API_PASSWORD=$(openssl rand -hex 32)" >> lnbits/.env

docker compose up -d phoenixd lnbits
```

**Note:** Phoenixd works directly without an explicit channel setup — Acinq manages the channels. Very good for the pilot; for high-load applications use your own LND later.

---

## 12. Set up a public domain (when the pilot must be reachable externally)

Once a domain (e.g. `pilot.bimbeam.at`) points to the server:

```bash
# DNS A record pointing to the server IP, then:
sed -i "s|SAEC_DOMAIN=.*|SAEC_DOMAIN=pilot.bimbeam.at|" .env

# Caddyfile to variant B
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

Caddy automatically obtains Let's Encrypt certificates.

---

## 13. Backups

Volumes are differently sensitive per service.

```bash
# Backup script
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

**Cron recommendation:** daily at 03:00.

```bash
crontab -e
# add:
# 0 3 * * * cd ~/sovereign-aec-backend && ./backup.sh > /var/log/saec-backup.log 2>&1
```

**Important:** the LNbits `.env` contains wallet secrets. Back it up separately (e.g. on a USB stick + safe) as soon as real sats are on it.

---

## 14. Troubleshooting (common cases)

### Relay does not connect (client says "Connection refused")
- `docker compose ps` — is strfry running?
- `docker compose logs strfry --tail=30`
- Port conflict? `ss -tlnp | grep 7777`
- Firewall? `sudo ufw status` — is port 7777 open?

### Blossom rejects upload with 401
- The client's auth event has a wrong signature or is expired (>5 min)
- Set `requireAuth: false` in config.yml temporarily for the test
- Allow list empty = any pubkey OK; if filled → add your own npub

### LNbits shows "connection error" to the wallet
- FakeWallet is OK by default; if Phoenixd: is the container running?
- `docker compose logs lnbits | grep -i wallet`

### Caddy does not obtain a TLS certificate
- DNS not propagated yet? `dig pilot.bimbeam.at`
- Are ports 80 + 443 reachable from outside? Test via `https://check-your-website.server-daten.de`
- Caddy logs: `docker compose logs caddy --tail=50`

---

## 15. Next steps (after a successful setup)

OpenClaw should report to Felix:

1. **Status overview** — all four containers are running, verification tests green.
2. **LNbits user ID** — saved in `.env`, bookmarked in the browser.
3. **Admin pubkey** — entered, can publish events + Blossom uploads.
4. **DSFA.md** — skeleton present, gaps marked for the pilot partner.
5. **Open configuration items** — if something had to be skipped during setup.

Afterwards Felix can:

- open `character.html`, enter relay URL = `ws://localhost:7777`, Blossom URL = `http://localhost:3000`
- open `admin.html`, create the first project
- run `ingest.py` against your own setup for an IFC upload test
- open the LNbits wallet, generate the first test invoice

---

## 16. Pilot target architecture (released 2026-05)

Replaces the laptop + Tailscale setup. Binding, complementing
`identity-architecture.md`. The laptop/Tailscale is dropped for the backend; Tailscale
remains at most an admin access route to the VPS.

### 16.1 Server & storage

- **Hetzner Cloud CX23** (2 vCPU x86, 4 GB RAM, 40 GB, ≈ €4.49/month),
  Ubuntu 24.04 + Docker. EU location (GDPR/DPIA — custodial keys stay in the EU).
- **Hetzner Volume when needed** (~€0.044/GB/month) for Blossom/IFC blobs, only
  attached when blob growth requires it. Keeps large IFC data separate from
  relay DB / LNbits / phoenixd — blob growth can never fill the money/key box.
  Server resize (RAM/CPU) is possible later; x86 chosen because
  ARM↔x86 are not interchangeable.

### 16.2 DNS (domains at World4You; do NOT touch `bimbeam.at` — mail)

Domain split (matches `BRAND.md`): **gemeinwert.com** = brand website
(human audience). **bimcvp.com** = protocol/identity/services
(international, dev/NIP). No 301 — they cross-link. Both via the same
Hetzner Caddy.

| Record | Target |
|---|---|
| `gemeinwert.com` @ / `www`  A | VPS IP (brand website) |
| `bimcvp.com` @ / `www`  A     | VPS IP (protocol hub + NIP-05) |
| `relay.bimcvp.com`  A         | VPS IP |
| `pay.bimcvp.com`    A         | VPS IP |
| `blossom.bimcvp.com` A        | VPS IP |
| `bunker.bimcvp.com` A         | VPS IP (Phase 2) |

NIP-05/Lightning address handles are `name@bimcvp.com` (well-known on the
bimcvp.com apex via Caddy → LNbits `nostrnip5`). Caddy does auto-TLS for all.

### 16.3 Containers on the VPS

- `caddy` — reverse proxy / TLS; serves `gemeinwert.com` (static site) and
  `bimcvp.com` (protocol hub + NIP-05). No GitHub Pages.
- `strfry` **public** → `wss://relay.bimcvp.com`, **write-policy plugin active**
  (only pilot pubkeys, i.e. events with a project `a` tag `30902:<pubkey>:<guid>`;
  cf. the strfry `writePolicy` section). Mandatory before going public.
- `strfry` **private** (optional, initially deferrable) — 2nd container, only
  localhost/tailnet, own DB + write policy. Internal WIP layer (PRINCIPLES §4).
- `lnbits` → `https://pay.bimcvp.com` — **stock, pure wallet engine** (no fork).
  Backend `LNBITS_BACKEND_WALLET_CLASS=PhoenixdWallet` → `http://phoenixd:9740`.
  Extensions active: `usermanager`, `nostrnwc`, `lnurlp`, `nostrnip5`
  (existing `invoices, satspay, splitpayments, cashu` remain). Non-enabled
  extensions are inert — nothing to "strip", no fork.
- `bunker` — NIP-46 signer → `wss://bunker.bimcvp.com`, custodies Tier-1 keys.
  Pilot: `nak bunker` (fiatjaf `nak`); abstracted so Knox/nsec.app can replace it
  without a frontend change. Re-validate the approach at ~5–10 users.
- `blossom` → `https://blossom.bimcvp.com` (blobs on a volume if needed).
- `phoenixd` — LNbits funding, internal only `:9740`. Minimally funded with test sats.

### 16.4 Per-user provisioning (Tier 1)

A thin server-side `provision` glue (the only self-built component, **not
in the public web repo**) creates in one flow: LNbits user+wallet (UserManager API)
→ managed Nostr key in the bunker → Lightning address `name@bimcvp.com`
(lnurlp+nostrnip5 on the bimcvp.com apex, also serves as NIP-05)
→ NWC connection (`nostrnwc`).
The mapping table is identity plumbing only: `lnbits_user_id ↔ npub ↔ bunker_ref ↔
lightning_address` — no roles, no BIM data (project membership stays
event-defined in `kind:30902`). Keystore encrypted, operator key offline →
that is the trust boundary (see `identity-architecture.md`).

**DPIA — bindingly add (section 3 data categories / 4 processors):**
v1 is implemented (`provision` service, server-side signature). To record:
(a) **email addresses** of the members (PII; onboarding + recovery channel),
(b) **encrypted Nostr secret keys** (custodial, AES-256-GCM, master key
offline), (c) `provision`/operator as a **data processor** (can technically
sign for members — limited to the named pilot circle, access logged),
(d) recovery runs via email → email account security is part of the
risk model; magic links are single-use, short-lived, signed. Post-pilot:
export to self-custody / NIP-46 bunker.

**DPIA — relay confidentiality (open decision, add to sections 3/6):**
The public relay only gates writes; **reads are open** → BCF content
is public in cleartext. **Not** permissible for confidential project data.
Direction **decided = Increment B** (per-project content key, custodial,
server-side; A as a stopgap, C/MLS as the end state) — spec in
`relay-confidentiality.md`, **build deferred** (after Bolzano). Until B is in place:
no confidential project data on the public relay; public demos
only with fictional data.

### 16.5 Recovery (short version — details in identity-architecture.md)

Key lost ≠ key compromised. Loss: LNbits login → new bunker token →
**same npub**, the admin can reset the LNbits credential (UserManager), the key remains.
Compromise: new npub + admin re-link in `kind:30902` (Path-C semantics) —
this path stays implemented and tested.

---

*Status: v0.1. Pilot-ready. Production hardening (offsite backups, monitoring, automated updates) in the Phase 2 plan.*
