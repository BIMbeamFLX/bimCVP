#!/bin/sh
# strfry write-policy plugin — pilot pubkey allowlist + private-layer transport.
# Protocol: one JSON object per stdin line; reply one JSON object per line.
# No jq dependency (busybox sed/grep only) — robust on the Alpine strfry image.
#
# Policy:
#   1. Private-layer transport kinds are ALWAYS accepted (any pubkey). These
#      use ephemeral / gift-wrap keys, so a pubkey allowlist cannot apply to
#      them. The relay only ever sees opaque ciphertext (White Noise / MLS):
#        443  MLS KeyPackage     (NIP-EE)  — lets new members be invited
#        444  MLS Welcome        (NIP-EE)
#        445  MLS Group Message  (NIP-EE)  — ephemeral per-group key
#        1059 NIP-59 Gift Wrap   (Welcome delivery + NIP-17 DM fallback)
#   2. Everything else (BCF/IFC/IDS/public events): author pubkey must be on
#      the pilot allowlist below.
#
# EDIT the allowlist, then:  docker compose restart strfry
# Pubkeys are 64-char lowercase HEX (not npub). npub -> hex: `nak decode npub1…`.

ALLOW='
# --- pilot pubkeys (hex) -------------------------------------------------
# admin / operator:
0000000000000000000000000000000000000000000000000000000000000000
# add pilot participants below:
'

# Private-layer transport kinds (space-padded), accepted regardless of pubkey.
PRIVATE_KINDS=" 443 444 445 1059 "

while IFS= read -r line; do
    id=$(printf '%s' "$line"   | sed -n 's/.*"id":"\([0-9a-f]\{64\}\)".*/\1/p'    | head -n1)
    pk=$(printf '%s' "$line"   | sed -n 's/.*"pubkey":"\([0-9a-f]\{64\}\)".*/\1/p' | head -n1)
    kind=$(printf '%s' "$line" | sed -n 's/.*"kind": *\([0-9]\{1,\}\).*/\1/p'      | head -n1)

    ok=0

    # 1. private-layer transport: always allowed (ephemeral / gift-wrap keys)
    if [ -n "$kind" ]; then
        case "$PRIVATE_KINDS" in
            *" $kind "*) ok=1 ;;
        esac
    fi

    # 2. otherwise: pilot pubkey allowlist
    if [ "$ok" = "0" ] && [ -n "$pk" ]; then
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
