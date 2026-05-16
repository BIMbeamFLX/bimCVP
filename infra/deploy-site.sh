#!/usr/bin/env bash
# Pull the static site from the public web repo into ./site-root,
# which Caddy serves at https://gemeinwert.com .
# Run on the server after the stack is up, and again whenever the site changes.
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
# atomic-ish swap
rsync -a --delete "$TMP/repo/site/" ./site-root.new/
rm -rf ./site-root.old
[ -d ./site-root ] && mv ./site-root ./site-root.old
mv ./site-root.new ./site-root
rm -rf ./site-root.old

echo "Site deployed to ./site-root . Caddy serves it live (no restart needed)."
