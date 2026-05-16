#!/bin/sh
# strfry write-policy plugin — pilot pubkey allowlist.
# Protocol: one JSON object per stdin line; reply one JSON object per line.
# Accept only events whose author pubkey is on the allowlist below.
# No jq dependency (busybox sed/grep only) — robust on the Alpine strfry image.
#
# EDIT the allowlist, then:  docker compose restart strfry
# Pubkeys are 64-char lowercase HEX (not npub). Convert npub -> hex with
# `nak decode npub1...` or any NIP-19 tool. One per line, '#' comments allowed.

ALLOW='
# --- pilot pubkeys (hex) -------------------------------------------------
# admin / operator:
0000000000000000000000000000000000000000000000000000000000000000
# add pilot participants below:
'

while IFS= read -r line; do
    # event id = first "id":"<64hex>" inside the event object
    id=$(printf '%s' "$line" | sed -n 's/.*"id":"\([0-9a-f]\{64\}\)".*/\1/p' | head -n1)
    pk=$(printf '%s' "$line" | sed -n 's/.*"pubkey":"\([0-9a-f]\{64\}\)".*/\1/p' | head -n1)

    ok=0
    if [ -n "$pk" ]; then
        # exact line match against the allowlist (ignore comments/blank)
        if printf '%s\n' "$ALLOW" | grep -v '^[[:space:]]*#' | grep -qx "$pk"; then
            ok=1
        fi
    fi

    if [ "$ok" = "1" ]; then
        printf '{"id":"%s","action":"accept","msg":""}\n' "$id"
    else
        printf '{"id":"%s","action":"reject","msg":"blocked: not on pilot allowlist"}\n' "$id"
    fi
done
