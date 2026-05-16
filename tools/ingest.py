#!/usr/bin/env python3
"""
Raulassen Pilot — IFC Ingest v0.2

Uploads each IFC from inventory.csv to a Blossom server, then publishes
a kind:1063 NIP-94 file-metadata event to one or more Nostr relays
with the Blossom URL as `url`-tag.

Dependencies:
    pip install ifcopenshell pynostr requests

Usage:
    export RELAYS="ws://localhost:8080,wss://relay.damus.io"
    export BLOSSOM_URL="http://localhost:3000"
    export PROJECT_GUID="raulassen-pilot-2026"
    python ingest.py <nsec-hex>
"""

import base64
import csv
import hashlib
import json
import os
import sys
import time
from pathlib import Path

import ifcopenshell  # type: ignore
import requests  # type: ignore
from pynostr.event import Event  # type: ignore
from pynostr.key import PrivateKey  # type: ignore
from pynostr.relay_manager import RelayManager  # type: ignore


DEFAULT_RELAYS = ["ws://localhost:8080"]
RELAYS = [
    r.strip()
    for r in os.environ.get("RELAYS", ",".join(DEFAULT_RELAYS)).split(",")
    if r.strip()
]
BLOSSOM_URL = os.environ.get("BLOSSOM_URL", "http://localhost:3000").rstrip("/")
PROJECT_GUID = os.environ.get("PROJECT_GUID", "raulassen-pilot-2026")
PROJECT_REF = f"raulassen-pilot:{PROJECT_GUID}"
BCF_VERSION = "0.1"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def ifc_metadata(path: Path) -> dict:
    ifc = ifcopenshell.open(str(path))
    projects = ifc.by_type("IfcProject")
    project = projects[0] if projects else None
    return {
        "schema": ifc.schema,
        "ifc_project_guid": project.GlobalId if project else "",
        "ifc_project_name": project.Name if project else "",
        "entity_count": len(ifc.by_type("IfcRoot")),
    }


def blossom_upload(path: Path, sk: PrivateKey) -> tuple[str, str]:
    """Upload file to Blossom (BUD-01). Returns (url, sha256)."""
    sha = sha256_file(path)
    size = path.stat().st_size

    auth = Event(
        content=f"Upload {path.name}",
        kind=24242,
        tags=[
            ["t", "upload"],
            ["x", sha],
            ["expiration", str(int(time.time()) + 300)],
            ["size", str(size)],
        ],
    )
    auth.sign(sk.hex())
    auth_b64 = base64.b64encode(json.dumps(auth.to_dict()).encode()).decode()

    with open(path, "rb") as f:
        resp = requests.put(
            f"{BLOSSOM_URL}/upload",
            headers={
                "Authorization": f"Nostr {auth_b64}",
                "Content-Type": "application/x-step",
            },
            data=f,
            timeout=300,
        )
    resp.raise_for_status()
    data = resp.json()
    return data["url"], data["sha256"]


def build_event(
    path: Path, row: dict, blossom_url: str, sha: str, sk: PrivateKey
) -> Event:
    size = path.stat().st_size
    meta = ifc_metadata(path)

    tags = [
        ["url", blossom_url],
        ["m", "application/x-step"],
        ["x", sha],
        ["size", str(size)],
        ["schema", meta["schema"]],
        ["authoring-tool", row["authoring_tool"]],
        ["discipline", row["discipline"]],
        ["a", PROJECT_REF],
        ["ifc-project", meta["ifc_project_guid"]],
        ["filename", path.name],
        ["bcf-version", BCF_VERSION],
        ["client", "raulassen-ingest/0.0.2"],
    ]

    content = json.dumps(
        {
            "ifc_project_name": meta["ifc_project_name"],
            "entity_count": meta["entity_count"],
            "notes": row.get("notes", ""),
        },
        ensure_ascii=False,
    )

    event = Event(content=content, kind=1063, tags=tags)
    event.sign(sk.hex())
    return event


def publish(event: Event, relays: list[str]) -> None:
    rm = RelayManager(timeout=6)
    for r in relays:
        rm.add_relay(r)
    rm.open_connections()
    time.sleep(1)
    rm.publish_event(event)
    rm.run_sync()
    time.sleep(2)
    rm.close_connections()


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: python ingest.py <nsec-hex>")
        return 1

    sk = PrivateKey.from_hex(sys.argv[1])
    print(f"npub:    {sk.public_key.bech32()}")
    print(f"project: {PROJECT_REF}")
    print(f"blossom: {BLOSSOM_URL}")
    print(f"relays:  {RELAYS}")
    print()

    inv = Path("inventory.csv")
    if not inv.exists():
        print("inventory.csv missing")
        return 2

    with open(inv) as f:
        reader = csv.DictReader(f)
        for row in reader:
            p = Path(row["path"])
            if not p.exists():
                print(f"SKIP {p} (not found)")
                continue
            print(f"INGEST {p.name}")
            try:
                print("  uploading to Blossom…")
                url, sha = blossom_upload(p, sk)
            except Exception as e:
                print(f"  ! Blossom upload failed: {e}")
                continue
            print(f"  -> url    {url}")
            print(f"  -> sha256 {sha}")
            try:
                print("  publishing kind:1063…")
                ev = build_event(p, row, url, sha, sk)
                publish(ev, RELAYS)
            except Exception as e:
                print(f"  ! relay publish failed: {e}")
                continue
            print(f"  -> event  {ev.id}")
            print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
