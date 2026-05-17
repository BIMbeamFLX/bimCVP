# nodrive — sovereign Drive on the Nostr stack

**Tagline.** A Google-Drive replacement assembled from three existing open-source pieces: hashtree (storage), gitworkshop/NIP-34 (collaboration), FIPS (mesh transport). Identity over Nostr (npub), encryption on by default.

**Status:** discussion sketch, May 2026
**Author:** Felix

---

## Stack

```
┌──────────────────────────────────────────┐
│  nodrive  (Web / Tauri / Mobile)         │  Drive UX, sharing, activity
├──────────────────────────────────────────┤
│  gitworkshop / NIP-34                    │  Version history, issues, comments
├──────────────────────────────────────────┤
│  hashtree                                │  Content-addressed storage,
│                                          │  CHK encryption, Merkle roots on
│                                          │  Nostr, FUSE mount, git transport
├──────────────────────────────────────────┤
│  Nostr  (npub, NIP-29, NIP-44)           │  Identity, groups, keys
├──────────────────────────────────────────┤
│  Internet  (relays / Blossom / WebRTC)
│  + FIPS mesh  (offline-first, local)
└──────────────────────────────────────────┘
```

## What each piece brings

- **hashtree** — the filesystem layer. SHA256-addressed 2 MB chunks, deterministic MessagePack tree nodes, CHK encryption by default, mutable address `npub/tree/path` via Nostr-published roots, FUSE mount, `git-remote-htree`, TS SDK `@hashtree/worker`, Tauri shell `iris-browser`. Actively developed (v0.2.50), maintained by mmalmi / sirius.
- **gitworkshop / NIP-34** — collaboration over Nostr. Repos, issues, PRs, comments as events. For nodrive: versioning and conversation per file or directory.
- **FIPS** — self-organizing mesh transport. Keypair = address, hop-by-hop + end-to-end encryption, IPv6 gateway for legacy apps. Killer use cases: construction site office, field crews, air-gapped setups. Came out of SEC-07 — a direct hook into the SE lineage.

## What needs to be built

1. **Drive UX** — web app on top of `@hashtree/worker`: folder tree, drag-and-drop upload, previews, share.
2. **Share flow** — "share file with npub…" emits a NIP-44 DM carrying the path + CHK key. Recipient sees it under "Shared with me".
3. **Cross-user mounts** — mount someone else's `npub/tree/path` as read-only or read-write.
4. **NIP-34 overlay** — surface issues and comments per file or path.
5. **Sync state + conflict UX** — clear offline / online / syncing indicator, git-merge under the hood.
6. **Optional FIPS bridge** — setup wizard that boots a FIPS daemon and maps nodrive onto the mesh transport.

## MVP path

| Phase | Duration | Scope |
|---|---|---|
| 1 | 4–6 weeks | Web app, single-user drive, internet-only |
| 2 | 4 weeks   | NIP-44 sharing, cross-mount, NIP-34 comments |
| 3 | 4 weeks   | Tauri desktop via iris-browser, FUSE mount |
| 4 | 4 weeks   | FIPS bridge, offline-mesh demo |
| 5 | open      | Mobile via `hashtree-ffi` (Kotlin / Swift via UniFFI) |

## How it ties into the rest of the sovereign-AEC set

nodrive is the storage substrate for the other projects: **OCF / Atelier** attachments, **BCF** IFC refs, **PDT** datasheets, **DVM IFC-Validation** inputs all live in nodrive. Put differently: BCF and OCF are the workflow apps, nodrive is the filesystem, FIPS is the network cable, hashtree is the disk logic.

## Risks

- Three young stacks combined at once — mitigation: stand up hashtree alone first, layer NIP-34 and FIPS on later.
- hashtree currently has 3 stars (solo maintainer). Make direct contact with Martti — you would be the first serious app builder on top.
- CHK encryption is deterministic (good for dedup, side-channel risk for privacy). For highly sensitive files, plan an additional salt layer.
- Conflict resolution on parallel writes — the git layer helps, but the UX still needs to handle it cleanly.

## Naming

`nodrive` — short, anti-SaaS statement, parses as "no-drive" or "Nostr-drive". Check the `nodrive.app` / `nodrive.io` domains.

## Sources

- hashtree — <https://github.com/mmalmi/hashtree>
- Learn FIPS — <https://learn.fips.network>
- GitWorkshop — <https://gitworkshop.dev>
- Sovereign Engineering Projects — <https://sovereignengineering.io/projects>
- NIP-34 (Git over Nostr) — <https://github.com/nostr-protocol/nips/blob/master/34.md>
