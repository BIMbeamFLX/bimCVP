#!/usr/bin/env bash
# One-time bootstrap on a fresh Hetzner CX23 (Ubuntu 24.04), run as the
# non-root sudo user from inside the backend-deploy/ folder.
set -euo pipefail
cd "$(dirname "$0")"

echo "==> 1/6 Docker present?"
if ! command -v docker >/dev/null 2>&1; then
    echo "Installing Docker ..."
    curl -fsSL https://get.docker.com | sh
    sudo usermod -aG docker "$USER"
    echo "Docker installed. LOG OUT and back in (group change), then re-run setup.sh."
    exit 0
fi
docker compose version >/dev/null 2>&1 || { echo "docker compose plugin missing"; exit 1; }

echo "==> 2/6 Config files present?"
[ -f lnbits/.env ] || { echo "Create lnbits/.env from lnbits/.env.example first."; exit 1; }
[ -f .env ]        || { echo "Create .env from .env.example first (SITE_REPO_URL)."; exit 1; }

echo "==> 3/6 Permissions"
chmod 600 lnbits/.env
chmod +x strfry/plugin/whitelist.sh deploy-site.sh
mkdir -p strfry/data blossom/data lnbits/data caddy/data caddy/config site-root

echo "==> 4/6 Reminder: strfry write-policy allowlist"
echo "    Edit strfry/plugin/whitelist.sh and add your pilot pubkeys (hex)."
echo "    The relay is PUBLIC — without this, nobody (or everybody) can write."

echo "==> 5/6 Pull + start stack"
docker compose pull
docker compose up -d
docker compose ps

echo "==> 6/6 Deploy static site"
./deploy-site.sh || echo "Site deploy skipped/failed — fix .env then run ./deploy-site.sh"

cat <<'NEXT'

Done. Next:
  - DNS (World4You) for BOTH domains must point at this server IP (README §3).
  - Watch TLS issuance:  docker compose logs -f caddy
  - First boot LNbits: open https://pay.bimcvp.com , create superuser,
    put its id in lnbits/.env -> LNBITS_ADMIN_USERS, then:
      docker compose restart lnbits
  - Portainer: open https://portainer.bimcvp.com and SET THE ADMIN PASSWORD
    NOW (first visitor becomes admin). Day-2 ops then run from there.
  - Verify: README §5 checklist.
NEXT
