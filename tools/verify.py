#!/usr/bin/env python3
"""
Raulassen Pilot — Verify Read-Back

Subscribes to relay(s), prints all kind:1063 events authored by the
given npub. Confirms that ingest.py actually pushed events through.

Dependencies:
    pip install pynostr

Usage:
    export RELAYS="ws://localhost:8080,wss://relay.damus.io"
    python verify.py <npub or hex-pubkey>
"""

import os
import sys
import time

from pynostr.filters import Filters, FiltersList  # type: ignore
from pynostr.key import PublicKey  # type: ignore
from pynostr.relay_manager import RelayManager  # type: ignore


RELAYS = [
    r.strip()
    for r in os.environ.get("RELAYS", "ws://localhost:8080").split(",")
    if r.strip()
]


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: python verify.py <npub or hex-pubkey>")
        return 1

    arg = sys.argv[1]
    if arg.startswith("npub"):
        pubkey_hex = PublicKey.from_npub(arg).hex()
    else:
        pubkey_hex = arg

    print(f"pubkey: {pubkey_hex}")
    print(f"relays: {RELAYS}")
    print()

    rm = RelayManager(timeout=6)
    for r in RELAYS:
        rm.add_relay(r)
    rm.open_connections()
    time.sleep(1)

    fl = FiltersList([Filters(authors=[pubkey_hex], kinds=[1063], limit=100)])
    rm.add_subscription_on_all_relays("verify", fl)
    rm.run_sync()
    time.sleep(3)

    rows = []
    while rm.message_pool.has_events():
        msg = rm.message_pool.get_event()
        e = msg.event
        tag = {t[0]: t[1] for t in e.tags if len(t) >= 2}
        rows.append(
            {
                "filename": tag.get("filename", "?"),
                "tool": tag.get("authoring-tool", "?"),
                "discipline": tag.get("discipline", "?"),
                "size": tag.get("size", "?"),
                "url": tag.get("url", "?"),
                "x": tag.get("x", "?")[:12] + "…",
            }
        )

    if not rows:
        print("(no events found — check relays + pubkey)")
    else:
        for r in rows:
            print(
                f"{r['filename']:42s} {r['tool']:9s} {r['discipline']:11s} "
                f"{r['size']:>12s}b  sha256:{r['x']}"
            )
            print(f"   url: {r['url']}")
        print()
        print(f"total: {len(rows)} events")

    rm.close_connections()
    return 0


if __name__ == "__main__":
    sys.exit(main())
