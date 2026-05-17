#!/usr/bin/env bash
# Pull the static site from the public web repo INTO ./site-root in place.
# Caddy bind-mounts ./site-root at /srv/site.
#
# CRITICAL: never rename/replace ./site-root. A Docker *directory* bind mount
# is bound to the inode at container start; renaming the host dir makes Caddy
# keep serving the old (often deleted) directory -> whole site 404 until a
# Caddy restart. Therefore: rsync IN PLACE. The inode stays stable, the bind
# mount stays valid, and changes go live immediately with no restart.
set -euo pipefail
cd "$(dirname "$0")"

[ -f .env ] && set -a && . ./.env && set +a
: "${SITE_REPO_URL:?set SITE_REPO_URL in .env}"
: "${SITE_REPO_BRANCH:=main}"

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

echo "Cloning $SITE_REPO_URL ($SITE_REPO_BRANCH) ..."
git clone --depth 1 --branch "$SITE_REPO_BRANCH" "$SITE_REPO_URL" "$TMP/repo"

if [ ! -d "$TMP/repo/site" ]; then
    echo "ERROR: site/ not found in repo" >&2
    exit 1
fi

mkdir -p ./site-root
# IN-PLACE sync — NO mv, NO swap. Inode of ./site-root unchanged ->
# Docker bind mount stays valid -> live immediately, no Caddy restart.
rsync -a --delete "$TMP/repo/site/" ./site-root/

echo "Site deployed in place to ./site-root . Live immediately (no restart needed)."
