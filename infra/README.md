> **Sanitised reference.** This is the public, anonymised backend
> deployment. No secrets, placeholder IPs (RFC5737/3849). The real
> `.env`, the NIP-46 bunker keystore and the `provision` glue live
> only on the server and are intentionally NOT in this repo.

# backend-deploy — Gemeinwert / BIM CVP pilot server

Server-side infrastructure bundle. **Never commit this folder to the public web
repo.** Real secrets (`lnbits/.env`, later the bunker keystore) live **only on
the server**. Architecture rationale: `docs/identity-architecture.md` +
`docs/BACKEND-SETUP.md §16` in the public repo.

Domain split (per BRAND.md): **gemeinwert.com** = brand website (DACH, human
audience, static only). **bimcvp.com** = protocol hub: relay, NIP-05 identity
`name@bimcvp.com`, wallet, blossom, dev/NIP docs. No 301 — they cross-link.
Both served by this one Caddy.

Stack: Caddy (TLS) · strfry (public relay) · LNbits (wallet engine) · Blossom
(blobs) · Portainer (container web UI, day-2 ops without SSH).
Phase 2: phoenixd (Lightning) + NIP-46 bunker (Tier-1 identity).

---

## 1. Provision the server (Hetzner)

- Hetzner Cloud, project `bimcvp-pilot`, **add SSH key first**.
- Server: **CX23** (2 vCPU x86 / 4 GB / 40 GB), **Ubuntu 24.04**, location
  Nürnberg or Falkenstein (EU/GDPR). Enable backups (~+€0.90/mo).
- **Cloud Firewall** attached: inbound allow **22, 80, 443** only.
- Note the public IPv4.

## 2. Base hardening (as root, once)

```
apt update && apt upgrade -y
adduser deploy && usermod -aG sudo deploy
# copy your SSH key to deploy, then disable root + password SSH:
#   /etc/ssh/sshd_config -> PermitRootLogin no ; PasswordAuthentication no
systemctl restart ssh
```

Continue as `deploy`. Copy this folder to the server (e.g. `scp -r backend-deploy`
or `git clone` a **private** repo — not the public one).

## 3. DNS — World4You (no domain transfer, just records)

Both domains are fresh `.com` (no mail) → low risk. In the World4You DNS editor.
Server (Hetzner): IPv4 `203.0.113.10` · IPv6 `2001:db8::1`
(the ::1 of the assigned /64 — verify on the box with `ip -6 addr`).
Set TTL = 300 during setup. Add A + AAAA (dual-stack) for each name.

**gemeinwert.com** (brand website only)

| Name | Type | Value |
|------|------|-------|
| `@` | A | `203.0.113.10` |
| `@` | AAAA | `2001:db8::1` |
| `www` | A | `203.0.113.10` |
| `www` | AAAA | `2001:db8::1` |

**bimcvp.com** (protocol / identity / services)

| Name | Type | Value |
|------|------|-------|
| `@` | A | `203.0.113.10` |
| `@` | AAAA | `2001:db8::1` |
| `www` | A | `203.0.113.10` |
| `relay` | A | `203.0.113.10` |
| `relay` | AAAA | `2001:db8::1` |
| `pay` | A | `203.0.113.10` |
| `pay` | AAAA | `2001:db8::1` |
| `blossom` | A | `203.0.113.10` |
| `blossom` | AAAA | `2001:db8::1` |
| `portainer` | A | `203.0.113.10` |
| `bunker` | A | `203.0.113.10` (Phase 2) |

Caddy serves the static site on `gemeinwert.com`, and the protocol hub +
NIP-05 (`name@bimcvp.com`) + services on `bimcvp.com`. No redirect between
them. Do **not** change nameservers or touch `your-mail-domain.tld` (your mail).

## 4. Configure & launch

```
cp .env.example .env                 # set SITE_REPO_URL to the public web repo
cp lnbits/.env.example lnbits/.env   # set FAKE_WALLET_SECRET; chmod 600 done by setup
nano strfry/plugin/whitelist.sh      # add pilot pubkeys (HEX) — relay is PUBLIC
./setup.sh
```

`setup.sh` installs Docker if missing (then re-run after re-login), starts the
stack, and deploys the static site into `./site-root`.

## 5. First-boot & verification

1. `docker compose logs -f caddy` → TLS certs issued for all hostnames (needs
   DNS live first; Let's Encrypt rate limits — get DNS right before retrying).
2. `https://gemeinwert.com` → static site loads (brand).
   `https://bimcvp.com` → protocol hub loads (same site files for now).
3. `wss://relay.bimcvp.com` → a whitelisted pubkey can publish; a
   non-whitelisted one is rejected (`tools/verify.py` from the public repo).
4. `https://pay.bimcvp.com` → LNbits up. Create the superuser, copy its id
   into `lnbits/.env` `LNBITS_ADMIN_USERS`, `docker compose restart lnbits`.
5. Enable extensions in LNbits UI if not auto-installed: usermanager, nostrnwc,
   lnurlp, nostrnip5.
6. NIP-05: confirm where `nostrnip5` serves the well-known JSON. If it is **not**
   at `/.well-known/nostr.json`, adjust that `handle` block in `Caddyfile` to
   rewrite to the real upstream path, then `docker compose restart caddy`.
   Goal: `https://bimcvp.com/.well-known/nostr.json?name=<x>` resolves
   → handles are `name@bimcvp.com`.
7. `https://blossom.bimcvp.com` → up; authenticated upload works.
8. `https://portainer.bimcvp.com` → **set the admin password immediately**
   (first visitor becomes admin — do this within minutes of going live).
   After that: containers, logs, restarts, image updates from the browser.

## 6. Phase 2 — real Lightning (phoenixd)

When the box is stable and you have test sats:
- Uncomment the `phoenixd` service in `docker-compose.yml` (confirm image tag).
- In `lnbits/.env`: `LNBITS_BACKEND_WALLET_CLASS=PhoenixdWallet`,
  `PHOENIXD_API_ENDPOINT=http://phoenixd:9740`, `PHOENIXD_API_PASSWORD=<...>`.
- `docker compose up -d` ; fund minimally (pilot sats only).

## 7. Phase 2 — identity custody (NIP-46 bunker + provision glue)

The Tier-1 custodial path (`identity-architecture.md`). Built next:
- `bunker` service (`nak bunker`, pilot single-key; abstract for Knox later).
- `provision` glue: UserManager + bunker key + lnaddress + NWC + mapping table.
  Server-side only, **encrypted keystore, operator key offline** — this is the
  trust boundary; also extend the DSFA (BACKEND-SETUP §16.4).
Until then: NIP-07 (Tier 2) and throwaway (Tier 3) work without this box.

## 8. Storage growth

When Blossom/IFC blobs grow: attach a **Hetzner Volume**, mount it at
`blossom/data/blobs` (or move the dir there). Keeps big blobs off the main
disk so the money/key box can never fill up.

## 9. Operations

- Day-2 without SSH: `https://portainer.bimcvp.com` — logs, restart a
  container, pull image updates, see status. SSH only needed for the bundle
  files (`.env`, `whitelist.sh`, `deploy-site.sh`).
- Update site: `./deploy-site.sh` (no restart needed).
- Update stack: `docker compose pull && docker compose up -d` (or via Portainer).
- Backups: Hetzner snapshot + back up `lnbits/data`, `strfry/data`,
  `caddy/data` (and later `bunker/keystore`) off-box.
- Add a pilot member to the relay: add their pubkey (hex) to
  `strfry/plugin/whitelist.sh`, `docker compose restart strfry`.

## Security invariants

- This folder ≠ public repo. `.gitignore` blocks secrets if ever git-init'd.
- `lnbits/.env` is `chmod 600`, never leaves the server.
- Only Caddy is publicly exposed (80/443). strfry/lnbits/blossom/phoenixd are
  internal Docker network only.
- Public relay must have the write-policy allowlist populated **before** the
  relay URL is shared.
