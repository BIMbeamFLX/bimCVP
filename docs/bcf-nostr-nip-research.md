# BCF over Nostr — Research for a NIP Draft

**Status:** Research groundwork for a NIP ("BCF — BIM Collaboration over Nostr")
**Author:** Felix (npub tbd) — discussion draft
**Date:** 2026-05-14
**Reference:** buildingSMART BCF 3.0 (XML + REST API), Nostr Protocol (NIP-01 ff.)

---

## 0. Executive Summary

BCF (BIM Collaboration Format) is the buildingSMART standard for issue/coordination communication in BIM projects and exists in two flavours: BCF-XML (container format, `.bcfzip`) and BCF-API (REST). Both currently assume a classic server-client stack with a central authority (BIMcollab, ACC Issues, Solibri, Trimble Connect, usnap and others).

Nostr offers an alternative transport: signed events, npub-based identity, relay federation, no platform sovereignty. This document describes how BCF can be mapped onto Nostr events without loss, proposes an event kind range, a tag taxonomy and a mapping table, and identifies the points where BCF and Nostr do not combine trivially (permissions, ordering, attachments, lifecycle).

The goal is a NIP draft that

1. defines an unambiguous representation of BCF topics, viewpoints and comments as Nostr events,
2. enables a lossless round-trip BCF-XML ↔ Nostr,
3. pragmatically closes the identity and permission gap (NIP-29 + NIP-58),
4. cleanly solves file attachments (snapshot, IFC, BimSnippet) via Blossom/NIP-94.

---

## 1. BCF in 5 minutes

BCF transports coordination topics, not models. A BCF container has a manifest and one folder per topic.

**BCF-XML 3.0 — core elements:**

- **Project Markup** (`project.bcfp`, optional): `Project @Guid`, `Name`, `ExtensionSchema` with lists for `TopicTypes`, `TopicStatuses`, `Priorities`, `TopicLabels`, `Users`, `SnippetTypes`, `Stages`.
- **Markup per topic** (`markup.bcf`):
  - `Header.Files.File` — references to associated IFC files (`IfcProject`, `IfcSpatialStructureElement`, hash, date, filename, `@IsExternal`).
  - `Topic @Guid @TopicType @TopicStatus @ServerAssignedId` — title, priority, index, labels, CreationDate, CreationAuthor, ModifiedDate, ModifiedAuthor, DueDate, AssignedTo, Stage, Description, BimSnippet, DocumentReferences, RelatedTopics.
  - `Comments.Comment @Guid` — Date, Author, comment text, viewpoint ref, ModifiedDate, ModifiedAuthor.
  - `Viewpoints.ViewPoint @Guid` — reference to viewpoint file and snapshot.
- **Viewpoint** (`viewpoint.bcfv`):
  - `Components` (`Selection`, `Visibility` with `DefaultVisibility` and `Exceptions`, `ViewSetupHints`, `Coloring`),
  - `OrthogonalCamera` or `PerspectiveCamera`,
  - `Lines`, `ClippingPlanes`, `Bitmaps`.
- **Snapshot** (`snapshot.png` or similar) — image reference, anchored in the viewpoint.

**BCF-API:** REST with resources `projects/{guid}/topics/{guid}/comments`, `viewpoints`, `files`, `documents`, `events`. Authentication via OAuth, a role model per project.

**What BCF is not:** not model transport (that is IFC's job), no effort costing, no contract layer.

---

## 2. Nostr in 5 minutes (for BIM readers)

- **Identity:** secp256k1 keypair, public form as `npub1…` (bech32). No account system.
- **Event:** signed JSON with `id`, `pubkey`, `created_at`, `kind`, `tags[][]`, `content`, `sig`.
- **Kind ranges** (see NIP-01):
  - `0–9999` regular (all replicas keep them),
  - `10000–19999` replaceable (only the latest event per `pubkey+kind`),
  - `20000–29999` ephemeral (relays should not persist them),
  - `30000–39999` parameterized replaceable (latest per `pubkey+kind+d-tag`),
  - `40000+` reserved for further categories.
- **Tags:** an array of arrays, the first element is the tag name (convention: short, lowercase).
- **Relays:** WebSocket servers, push/pull-capable, freely choosable. Auth via NIP-42 possible.
- **Relevant NIPs for our context:** NIP-09 (Delete), NIP-10 (Threading), NIP-17 (DM), NIP-19 (bech32), NIP-23 (Long-form), NIP-29 (Groups), NIP-42 (Auth), NIP-44 (Encryption), NIP-51 (Lists), NIP-58 (Badges), NIP-65 (Relay lists), NIP-72 (Communities), NIP-89 (Handler), NIP-94 (File metadata), NIP-96 (HTTP file storage), Blossom (blob storage, not a NIP, but established).

---

## 3. Design decisions

The most important choices a NIP must make:

### 3.1 Topic identity: replaceable vs. immutable

BCF topics change (status, assignee, priority). Three options:

| Option | Advantages | Disadvantages |
|---|---|---|
| A) Topic = parameterized replaceable event (`kind 30900`, `d=topic-guid`) | clear "current state" view, identical to BCF semantics | no history, audit only via additional events |
| B) Topic = immutable event, updates via separate patch events (`e`-tag) | full history, append-only | several events must be reduced, complicated for clients |
| C) Hybrid: replaceable for "current", in parallel an immutable audit event per change | best of both, round-trip possible | doubled write load |

**Recommendation: Option C.** `kind:30900` carries the current state (replaceable), `kind:1171` (regular) is an immutable audit entry per change. Clients without an audit need consume only 30900; forensic tools reconstruct history from 1171.

### 3.2 Comments: a dedicated kind or kind:1 with tags?

- **kind:1 + tags:** maximum reach (every Nostr client shows comments), weaker semantics.
- **dedicated kind:1170:** clear semantics, but only BCF-aware clients render it.

**Recommendation: a dedicated `kind:1170`,** additionally mirrored as a `kind:1` reply (optional, with a `nip:42`-tag hint) if the author wants cross-posting. Resolve the trade-off between spec cleanliness and reach explicitly.

### 3.3 Viewpoints

Viewpoints are technically separate artefacts with their own GUID, already decoupled in BCF. We use `kind:30901` with `d=viewpoint-guid` for addressable lookup, but forbid re-publishing the same `d` identity: viewpoints are immutable in the BCF profile. A changed camera, selection, clipping plane or snapshot reference produces a new viewpoint GUID. The snapshot is a file (NIP-94, see 3.5).

### 3.4 Project context

Projects are modelled as containers not in the topic itself but as a separate event:

- **`kind:30902` BCF-Project** (parameterized replaceable, `d=project-guid`) — carries project metadata, extension schema (lists for TopicTypes, Statuses, Priorities, Labels, Stages, SnippetTypes), references to associated IFC files.
- **The topic references the project event via an `a`-tag** (format `30902:<pubkey>:<project-guid>`).
- For multi-user projects: the project event is published in the name of a **NIP-29 group** (signed with the group key), not in the name of an individual. Members write into the group container and topics carry the `h`-tag of the group.

### 3.5 Attachments (snapshot, IFC, BimSnippet, DocumentReference)

Binary data does not belong in event content. Three paths:

- **Blossom** (sha256-addressed, simple, established) — recommended for snapshots, BimSnippets, DocumentReferences.
- **NIP-96 HTTP file storage** — alternative if pinning/quota is desired.
- **NIP-94 file metadata event** — for provenance and discovery: every file gets its own event with `url`, `m` (mime), `x` (sha256), `size`, `dim` etc.

**Recommendation:** the blob on Blossom, discovery + hash via NIP-94, the reference in the topic/viewpoint via an `e`-tag to the NIP-94 event OR directly via an `imeta`/`x`/`url` tag.

### 3.6 Permissions

The BCF-API has roles per project. Nostr has no built-in roles. Solution:

- **A group (NIP-29)** defines membership + mod rights at the relay layer.
- **Professional verification** via NIP-58 badges, issued by chambers/associations (chamber of engineers, bvfi, CNI/Albo). The badge is an attested event on the npub that clients use to display the "verified" stamp.
- **Contractual binding** (work contract, professional liability) stays offchain — see section 11.

### 3.7 Identifier stability & round-trip

BCF GUIDs (UUID v4) must be preserved. We use them as `d`-tag values for the replaceable events, not as event IDs. This is clean because:

- the Nostr event ID is computed deterministically from the content,
- the `d`-tag value is freely choosable and stable across replacements,
- a BCF-XML export trivially reconstructs the original GUIDs from `d` tags.

---

## 4. Proposed event kind range

| Kind | Name | Replaceable? | Purpose |
|---|---|---|---|
| `30900` | BCF Topic | parameterized replaceable | current topic state |
| `30901` | BCF Viewpoint | addressable, no republish | viewpoint definition |
| `30902` | BCF Project | parameterized replaceable | project metadata + extension schema |
| `30903` | BCF Document Reference | parameterized replaceable | external document (DocumentReferences counterpart) |
| `30904` | BCF File Reference | parameterized replaceable | IFC/model file reference with hash, IfcProject, IfcSpatialStructureElement |
| `1170` | BCF Comment | regular | comment on a topic or viewpoint |
| `1171` | BCF Audit Event | regular | immutable audit entry (status change, assignee change, priority change) |
| `1172` | BCF Reaction | regular | lightweight acknowledgement ("seen", "working on it") — orthogonal to status |

Rationale for the range: 30900–30999 is in the block for parameterized replaceable, leaves room for future BCF extensions (e.g. LOIN requirements, defect classifications, IFC issue diagnoses), and 1170–1179 keeps the comment/audit/reaction family tightly together.

---

## 5. Tag taxonomy

| Tag | Value form | Purpose | Required? |
|---|---|---|---|
| `d` | UUID (BCF-GUID) | identity of the replaceable event | for 309xx yes |
| `a` | `30902:<pubkey>:<project-guid>` | project reference | for 30900, 30901, 1170, 1171 yes |
| `h` | NIP-29 group-id | group context | if the project is in a NIP-29 group |
| `e` | event-id (parent/topic/viewpoint/file) | linkage | comment → topic: yes |
| `p` | pubkey | involved people (assignee, reporter, watcher) | where applicable |
| `t` | string | BCF label or free tag | optional |
| `s` | string | indexed mirror of `bcf-status` | for 30900 yes |
| `bcf-guid` | UUID | original BCF GUID for round-trip | for 30900/30901 yes |
| `bcf-status` | string | current status (Open, InProgress, Resolved, Closed, …) | for 30900 yes |
| `bcf-type` | string | TopicType (Issue, Clash, RFI, …) | for 30900 yes |
| `bcf-priority` | string | priority (Low, Normal, High, Critical) | optional |
| `bcf-stage` | string | project phase | optional |
| `bcf-due` | unix-ts | DueDate | optional |
| `bcf-index` | int | index | optional |
| `e` with marker `viewpoint` | event-id | viewpoint reference for a topic/comment | optional |
| `e` with marker `snapshot` | event-id | snapshot reference to kind:1063 | optional |
| `ifc` | IFC-GUID | referenced IFC element | multiple allowed |
| `ifc-file` | event-id (kind 30904) | referenced model file | multiple allowed |
| `audit-field` | string | for 1171: which field changed | for 1171 yes |
| `audit-from`, `audit-to` | string | old/new value | for 1171 yes |
| `bcf-version` | string | "3.0" — BCF schema version | for 30900 yes |
| `client` | string | producing client (analogous to NIP-89) | optional |

**Convention:** all BCF-specific tags use the `bcf-` prefix so they do not collide with standard tags in generic Nostr clients.

---

## 6. Complete mapping table BCF-XML → Nostr

### 6.1 Project Markup (`project.bcfp`) → `kind:30902`

| BCF | Nostr |
|---|---|
| `Project @Guid` | `d`-tag |
| `Project.Name` | `content.name` |
| `ExtensionSchema.TopicTypes/Type` | `content.extension.topic_types[]` |
| `ExtensionSchema.TopicStatuses/Status` | `content.extension.topic_statuses[]` |
| `ExtensionSchema.Priorities/Priority` | `content.extension.priorities[]` |
| `ExtensionSchema.TopicLabels/Label` | `content.extension.topic_labels[]` |
| `ExtensionSchema.Stages/Stage` | `content.extension.stages[]` |
| `ExtensionSchema.SnippetTypes/SnippetType` | `content.extension.snippet_types[]` |
| `ExtensionSchema.Users/User` | `content.extension.users[]` (string list, optional + `p`-tag mirroring) |

### 6.2 Markup → `kind:30900` (Topic)

| BCF | Nostr |
|---|---|
| `Topic @Guid` | `d`-tag |
| `Topic @ServerAssignedId` | `content.server_assigned_id` |
| `Topic @TopicType` | `bcf-type`-tag |
| `Topic @TopicStatus` | `bcf-status`-tag |
| `Topic.Title` | `content.title` |
| `Topic.Priority` | `bcf-priority`-tag |
| `Topic.Index` | `bcf-index`-tag |
| `Topic.Labels/Label[]` | `t`-tags (one per label) |
| `Topic.CreationDate` | `content.created_date` (ISO 8601) + event `created_at` as unix-ts |
| `Topic.CreationAuthor` | `content.created_author` (email or real name) + event `pubkey` |
| `Topic.ModifiedDate` | event `created_at` of the latest replaceable revision |
| `Topic.ModifiedAuthor` | event `pubkey` of the latest revision |
| `Topic.DueDate` | `bcf-due`-tag (unix-ts) + `content.due_date` (ISO 8601) |
| `Topic.AssignedTo` | `p`-tag with an additional 4th element "assignee" + `content.assigned_to` (email fallback) |
| `Topic.Stage` | `bcf-stage`-tag |
| `Topic.Description` | `content.description` |
| `Topic.BimSnippet` | `e`-tag → kind 30903 (Document Reference, type=snippet) |
| `Topic.DocumentReferences/DocumentReference` | `e`-tag(s) → kind 30903 |
| `Topic.RelatedTopics/RelatedTopic` | `e`-tag → other kind:30900 with marker "related" |
| `Topic.Comments` | not embedded — comments are their own events (kind:1170) with an `e`-tag to the topic |
| `Topic.Viewpoints` | `e`-tags with marker `viewpoint` → kind:30901 |
| `Header.Files/File` | `ifc-file`-tags → kind:30904 |

### 6.3 Comment → `kind:1170`

| BCF | Nostr |
|---|---|
| `Comment @Guid` | `content.guid` (UUID, kept for round-trip) — event `id` is Nostr-native |
| `Comment.Date` | event `created_at` |
| `Comment.Author` | event `pubkey` (+ `content.author_email` for round-trip) |
| `Comment.Comment` | `content.text` |
| `Comment.Viewpoint @Guid` | `e`-tag with marker `viewpoint` → kind:30901 event-id |
| `Comment.ModifiedDate` | on edit: a separate kind:1170 event with an `e`-tag "replaces" to the predecessor; remove the original via NIP-09 delete (see 8.3) |
| `Comment.ModifiedAuthor` | event `pubkey` of the new version |

### 6.4 Viewpoint → `kind:30901`

| BCF | Nostr |
|---|---|
| `VisualizationInfo @Guid` | `d`-tag |
| `Components.Selection/Component[]` | `content.components.selection[]` (list with `ifc_guid`, `originating_system`, `authoring_tool_id`) + `ifc`-tags per element |
| `Components.Visibility @DefaultVisibility` | `content.components.visibility.default` |
| `Components.Visibility.Exceptions/Component[]` | `content.components.visibility.exceptions[]` |
| `Components.Visibility.ViewSetupHints` | `content.components.view_setup_hints` (object) |
| `Components.Coloring/Color[]` | `content.components.coloring[]` |
| `OrthogonalCamera` or `PerspectiveCamera` | `content.camera` (typed object with `type`, `view_point`, `direction`, `up_vector`, `view_to_world_scale` / `field_of_view`) |
| `Lines/Line[]` | `content.lines[]` |
| `ClippingPlanes/ClippingPlane[]` | `content.clipping_planes[]` |
| `Bitmaps/Bitmap[]` | `content.bitmaps[]` (with Blossom hash references) |
| `snapshot.png` | `e`-tag with marker `snapshot` → NIP-94 event |

### 6.5 IFC file reference → `kind:30904`

| BCF | Nostr |
|---|---|
| `File @IfcProject` | `content.ifc_project` |
| `File @IfcSpatialStructureElement` | `content.ifc_spatial_structure_element` |
| `File @IsExternal` | `content.is_external` (bool) |
| `File.Filename` | `content.filename` |
| `File.Date` | `content.date` (ISO 8601) |
| `File.Reference` | `content.reference` (url) + `x`-tag (sha256) |

### 6.6 Document Reference → `kind:30903`

| BCF | Nostr |
|---|---|
| `DocumentReference @Guid` | `d`-tag |
| `DocumentReference.DocumentGuid` | `content.document_guid` (BCF 3.0) |
| `DocumentReference.Url` | `content.url` |
| `DocumentReference.Description` | `content.description` |

---

## 7. Examples

### 7.1 Project (`kind:30902`)

```json
{
  "kind": 30902,
  "created_at": 1747200000,
  "tags": [
    ["d", "9c3b4a5c-1d6e-4a2b-8b1f-7a9b2c3d4e5f"],
    ["bcf-version", "3.0"],
    ["h", "proj-rueckhaltebecken-st-pauli"]
  ],
  "content": "{\"name\":\"Retention Basin St. Pauli\",\"extension\":{\"topic_types\":[\"Issue\",\"Clash\",\"RFI\"],\"topic_statuses\":[\"Open\",\"InProgress\",\"Resolved\",\"Closed\"],\"priorities\":[\"Low\",\"Normal\",\"High\",\"Critical\"],\"topic_labels\":[\"HVAC\",\"Structural\",\"Architecture\",\"Electrical\"],\"stages\":[\"LP3\",\"LP4\",\"LP5\",\"LP6\"],\"snippet_types\":[\"clash\",\"mvd\"],\"users\":[]}}",
  "pubkey": "<group-pubkey>",
  "id": "<sha256>",
  "sig": "<schnorr-sig>"
}
```

### 7.2 Topic (`kind:30900`)

```json
{
  "kind": 30900,
  "created_at": 1747201234,
  "tags": [
    ["d", "8b1f7a9b-2c3d-4e5f-9c3b-4a5c1d6e4a2b"],
    ["a", "30902:<group-pubkey>:9c3b4a5c-1d6e-4a2b-8b1f-7a9b2c3d4e5f"],
    ["h", "proj-rueckhaltebecken-st-pauli"],
    ["bcf-guid", "8b1f7a9b-2c3d-4e5f-9c3b-4a5c1d6e4a2b"],
    ["bcf-version", "3.0"],
    ["bcf-type", "Clash"],
    ["bcf-status", "Open"],
    ["s", "Open"],
    ["bcf-priority", "High"],
    ["bcf-index", "42"],
    ["bcf-due", "1749600000"],
    ["bcf-stage", "LP4"],
    ["t", "HVAC"],
    ["t", "Structural"],
    ["p", "<assignee-pubkey>", "", "assignee"],
    ["ifc", "0aB1cD2eF3gH4iJ5kL6mN7"],
    ["ifc-file", "<kind-30904-event-id>"],
    ["e", "<kind-30901-event-id>", "", "viewpoint"],
    ["e", "<nip94-snapshot-event-id>", "", "snapshot"]
  ],
  "content": "{\"title\":\"Ventilation duct crosses main girder on axis 4\",\"description\":\"Clash in the ground-floor ceiling area at axis 4/B. Proposal: lower the ventilation to -350 mm, check the girder haunch.\",\"created_date\":\"2026-05-14T08:20:34Z\",\"created_author\":\"felix@bimbeam.example\",\"due_date\":\"2026-06-11T00:00:00Z\",\"server_assigned_id\":\"BSP-2026-042\"}",
  "pubkey": "<felix-pubkey>",
  "id": "<sha256>",
  "sig": "<schnorr-sig>"
}
```

### 7.3 Comment (`kind:1170`)

```json
{
  "kind": 1170,
  "created_at": 1747203456,
  "tags": [
    ["e", "<topic-event-id>", "", "root"],
    ["a", "30902:<group-pubkey>:9c3b4a5c-1d6e-4a2b-8b1f-7a9b2c3d4e5f"],
    ["h", "proj-rueckhaltebecken-st-pauli"],
    ["p", "<felix-pubkey>"],
    ["e", "<kind-30901-event-id>", "", "viewpoint"]
  ],
  "content": "{\"text\":\"The girder cannot be lowered, the steelwork is already released. Proposal: route the ventilation above the girder, cross-section 800x300 → 600x400.\",\"guid\":\"7a9b2c3d-4e5f-9c3b-4a5c-1d6e4a2b8b1f\"}",
  "pubkey": "<statik-pubkey>",
  "id": "<sha256>",
  "sig": "<schnorr-sig>"
}
```

### 7.4 Audit event (`kind:1171`)

```json
{
  "kind": 1171,
  "created_at": 1747210000,
  "tags": [
    ["e", "<topic-event-id>"],
    ["a", "30902:<group-pubkey>:9c3b4a5c-1d6e-4a2b-8b1f-7a9b2c3d4e5f"],
    ["audit-field", "bcf-status"],
    ["audit-from", "Open"],
    ["audit-to", "InProgress"]
  ],
  "content": "",
  "pubkey": "<assignee-pubkey>",
  "id": "<sha256>",
  "sig": "<schnorr-sig>"
}
```

### 7.5 Viewpoint (`kind:30901`)

```json
{
  "kind": 30901,
  "created_at": 1747201230,
  "tags": [
    ["d", "5c1d6e4a-2b8b-1f7a-9b2c-3d4e5f9c3b4a"],
    ["a", "30902:<group-pubkey>:9c3b4a5c-1d6e-4a2b-8b1f-7a9b2c3d4e5f"],
    ["e", "<nip94-snapshot-event-id>", "", "snapshot"]
  ],
  "content": "{\"camera\":{\"type\":\"perspective\",\"view_point\":{\"x\":12.5,\"y\":-8.3,\"z\":2.6},\"direction\":{\"x\":0.42,\"y\":0.86,\"z\":-0.27},\"up_vector\":{\"x\":0,\"y\":0,\"z\":1},\"field_of_view\":60},\"components\":{\"selection\":[{\"ifc_guid\":\"0aB1cD2eF3gH4iJ5kL6mN7\"}],\"visibility\":{\"default\":true,\"exceptions\":[]}}}",
  "pubkey": "<felix-pubkey>",
  "id": "<sha256>",
  "sig": "<schnorr-sig>"
}
```

---

## 8. Behaviour & algorithms

### 8.1 Topic status: source of truth

The latest `kind:30900` event (by `created_at`, ties broken by the lexicographically smallest event `id` — analogous to NIP-01 for replaceable) is the current state. Audit events (`kind:1171`) are explanatory, not authoritative.

Conflict case: two replacements with an identical `created_at` and conflicting values — the algorithm chooses deterministically, but clients SHOULD make the conflict visible and offer the proposal "last author decides" or "escalate to mod".

### 8.2 Ordering of comments

Comments are causally sorted by `created_at`. Replies to comments (threading) use NIP-10 markers ("reply"/"root"). BCF does not know threading natively — we extend cautiously here: a comment can optionally reference another comment via an `e`-tag with marker "reply"; on BCF-XML export this is flattened to a flat comment list (ordered by `created_at`).

### 8.3 Comment edits

Nostr events are immutable. Comment edit workflow:

1. The author publishes a new `kind:1170` event with an `e`-tag marker "replaces" to the predecessor event-id.
2. The author publishes a NIP-09 delete (`kind:5`) for the predecessor.
3. Clients show the latest version but keep all versions locally in the audit cache.

On BCF-XML export the latest wins, `ModifiedDate`/`ModifiedAuthor` are set.

### 8.4 Closing, reopening, deleting a topic

- Close: status replacement to "Closed". The topic stays persistent.
- Reopen: status replacement to "Open" or "InProgress".
- Delete: NIP-09 delete event from the topic author or a group mod; relays should replicate but need not delete (eventually consistent). Practical tip: avoid hard deletes, prefer status "Closed" + label "WONTFIX" or similar.

### 8.5 Round-trip guarantees

Implementations MUST exhibit the following round-trip behaviour:

1. BCF-XML → Nostr events → BCF-XML produces a semantically equivalent output (all topic GUIDs, viewpoint GUIDs, comment GUIDs unchanged; comment ordering by `created_at`).
2. Nostr events → BCF-XML → Nostr events is not guaranteed canonical (event IDs change because the content may be re-serialised), but it is semantically equivalent.

Test vectors: every BCF 3.0 example from the official `bcf-xml` repository (buildingSMART) is stored with the expected Nostr event set. See section 13.

---

## 9. File layer

### 9.1 Blossom

Recommended default. The server accepts a PUT with a body and answers with `{url, sha256, size, type}`. The client stores `url` + `sha256` as tag values.

### 9.2 NIP-94 companion event

For every relevant file (snapshot ≥ 1 MB, IFC, BimSnippet, document) the client publishes a `kind:1063` event:

```json
{
  "kind": 1063,
  "tags": [
    ["url", "https://blossom.example/abc123.png"],
    ["m", "image/png"],
    ["x", "abc123…"],
    ["size", "184320"],
    ["dim", "1920x1080"],
    ["a", "30902:<group-pubkey>:<project-guid>"]
  ],
  "content": "Snapshot for topic axis 4/B"
}
```

Advantages: consistent provenance, searchability, simple mirror to a secondary Blossom.

### 9.3 IFC models

Large IFC files (>200 MB) are borderline for Blossom. Pragmatically:

- IFC file on the project's private Blossom (pinning by the owner).
- `kind:30904` BCF-File-Reference links url + sha256.
- Optionally: an additional OpenTimestamps anchor on the timechain for a notary function (see the "IFC notary" project).

### 9.4 Encryption

If the project is confidential (security infrastructure, military, critical infrastructure):

- Blob encryption client-side (AES-256-GCM), the key available to members in the group event (NIP-29).
- Event content (topic description, comment text) optionally NIP-44-encrypted; tag values stay cleartext and must be curated accordingly.

---

## 10. Relation to existing NIPs

| NIP | Use in BCF-over-Nostr |
|---|---|
| NIP-01 | base event format, replaceable semantics |
| NIP-09 | delete of topics/comments |
| NIP-10 | comment threading (markers "reply"/"root") |
| NIP-17 | optional private coordination DMs (e.g. "client asks for a callback") |
| NIP-19 | bech32 encoding for cross-tool links (`naddr1…` for topics) |
| NIP-23 | long-form rationales, ideally as an annex to topics (separate event, linked via an `e`-tag) |
| NIP-29 | project container (private group), membership, mod rights |
| NIP-42 | relay auth (mandatory for non-public project relays) |
| NIP-44 | content encryption for confidential projects |
| NIP-51 | lists for "watched topics", "bookmarks" |
| NIP-58 | professional badges (chamber attestation, certification) |
| NIP-65 | relay lists per planner |
| NIP-72 | public tribes / communities (construction sector, Sovereign Engineering) |
| NIP-89 | recommended-apps handling (client recommendations for unknown kinds) |
| NIP-94 | file metadata per snapshot / IFC / BimSnippet |
| NIP-96 | optional alternative to Blossom storage |

---

## 11. Gap analysis: what BCF can do, Nostr cannot (out of the box)

| BCF function | Nostr gap | Solution in the NIP |
|---|---|---|
| Roles per project (reviewer, manager, read-only) | no standard roles | NIP-29 mod layer + 4th element in the `p`-tag ("role"); for stamping roles a NIP-58 badge |
| Server-assigned topic IDs | not central | keep `server_assigned_id` in `content`; assignment either by a mod bot in the group container (deterministic by `created_at`) or freely by the author |
| Activity log endpoint (BCF-API `/events`) | not standardised | audit events (`kind:1171`) + filter `kinds:[1171]`+`#a:[<project>]` |
| File quota / pinning | no guarantee | Blossom with a paid/member model; the owner pins themselves |
| Permanence | relays can delete | own project relay (strfry, nostr-rs-relay) + OpenTimestamps anchor for final states |
| Standardised TopicTypes / Statuses | free-form tags | defined per project via `kind:30902 ExtensionSchema` (original BCF mechanic) |
| Binding identity | npub is a pseudonym | chamber badge via NIP-58 + offchain work contract with real-name binding |
| Delivery note / acceptance document | not in Nostr | optionally a separate event `kind:30910` "BCF Hand-over" with a complete topic list + OTS anchor — recommend this extension in the NIP |

---

## 12. Security and privacy model

### 12.1 Threat model

- **Tampering:** excluded per event by the Schnorr signature; replacement ordering must be monitored (see 8.1).
- **Repudiation:** excluded — every action is signed.
- **Confidentiality:** cleartext in the relay by default. For sensitive projects NIP-29 + NIP-44 + blob encryption.
- **Availability:** relay outage → recommend multiple relays (NIP-65 outbox pattern). Recommended: own project relay (mandatory write) + 2 redundant mirrors.
- **Sybil:** in public tribes via NIP-58 badges / NIP-72 mod layer.
- **Spam:** relay-side (allowlist, auth, PoW NIP-13 optional).

### 12.2 Key management

Recommendation: the planner npub in a hardware signer (Amber/nsec.app/NSec bunker). Connection to professional identity via a NIP-58 badge issued by a chamber; the badge is revocable (NIP-09 delete by the issuer).

### 12.3 Data protection (GDPR)

- Comment content and topic descriptions can contain personal data.
- Right to erasure: NIP-09 is only best-effort. For GDPR-compliant projects: a private relay with a clear operator → data processing agreement; do not use public tribes for personal content.
- Recommendation in the NIP: a "Privacy Considerations" note section with the above points.

---

## 13. Reference implementation & test vectors

### 13.1 Minimal stack for a proof of concept

- Web client: Next.js / Astro, `nostr-tools` or `ndk`, Three.js / xeokit for viewpoint rendering.
- Relay: `nostr-rs-relay` or `strfry` with NIP-42, NIP-29 patch.
- Blob: one of the established Blossom servers (`blossom-server-rs`).
- Importer/exporter: TypeScript CLI `bcf-nostr` with subcommands `import <file.bcfzip>` and `export <project-naddr> <out.bcfzip>`.

### 13.2 Test vectors

For every BCF 3.0 example from the `buildingSMART/BCF-XML` repo, store:

- the input `.bcfzip`,
- the target set of Nostr events (canonically sorted, deterministic `created_at` via the BCF date),
- the round-trip output `.bcfzip` with a hash comparison of the `markup.bcf` XML elements after normalisation.

This makes conformance measurable.

---

## 14. NIP draft skeleton

A concrete NIP draft should contain the following sections:

```
NIP-XXX: BCF over Nostr

BCF — BIM Collaboration over Nostr
----------------------------------

`draft` `optional` `author:felix`

Abstract
~~~~~~~~
Defines event kinds, tags, and conventions to represent buildingSMART BCF 3.0
issues, comments, viewpoints, projects, and file references on Nostr.

Motivation
~~~~~~~~~~
[approx. 200 words — relating to platform lock-in, BIM coordination, sovereignty,
lossless exchange]

Event Kinds
~~~~~~~~~~~
30900 BCF Topic …
30901 BCF Viewpoint …
30902 BCF Project …
30903 BCF Document Reference …
30904 BCF File Reference …
1170 BCF Comment …
1171 BCF Audit Event …

Tags
~~~~
d, a, h, e, p, s, t, bcf-guid, bcf-status, bcf-type, bcf-priority, bcf-stage, bcf-due,
bcf-index, e-marker:viewpoint, e-marker:snapshot, ifc, ifc-file, audit-field, audit-from,
audit-to, bcf-version, client

Schema (JSON, BCF 3.0 Mapping)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
[see the mapping table in section 6]

Behavior
~~~~~~~~
[8.1–8.5 as normative clauses, MUST/SHOULD]

File Handling
~~~~~~~~~~~~~
[NIP-94 / Blossom — recommendation, not mandatory]

Relations to Other NIPs
~~~~~~~~~~~~~~~~~~~~~~~
[table from section 10]

Security Considerations
~~~~~~~~~~~~~~~~~~~~~~~
[section 12]

Test Vectors
~~~~~~~~~~~~
[link to the reference repo]
```

---

## 15. Open questions / discussion needs

1. **Kind range:** is `30900–30904 / 1170–1172` compatible with the existing allocation practice? A PR to `nostr-protocol/nips` is required to secure the reservation.
2. **Relationship BCF-API ↔ Nostr NIP:** should the NIP only map the XML container, or also semantically replace BCF-API endpoints? Recommendation: first XML-parity, the API as a follow-up NIP.
3. **Future BCF 4.0:** which expected fields (e.g. extended LOIN references, multi-modal snapshots) already need reserved space now?
4. **Mod layer:** is NIP-29 sufficient or is a dedicated NIP for "project roles" sensible that goes beyond pure group mods (reviewer, approver, stamper)?
5. **OpenTimestamps integration:** standardise as a tag (`ots`-tag with an OTS proof) or leave it to the user? Recommendation: standardise, because it is one of the strongest use cases.
6. **Localization:** multilingual topic descriptions? Proposal: `content.title_i18n` as a map, otherwise a language tag `lang`.
7. **Cashu/Lightning hook:** should a topic optionally carry a bounty (payout on Status=Resolved)? Hook into DVM logic (NIP-90) as an optional companion event. Recommendation: yes, as an optional feature outside the core NIP.

---

## 16. Recommended next steps

1. **Consensus sounding in the buildingSMART open-source community** (Slack `bsi`, forum) — early discussion avoids duplicate work.
2. **Nostr side:** open an issue in the `nostr-protocol/nips` repo, have the kind range allocated.
3. **Reference importer/exporter** as a CLI on GitHub, MIT licence.
4. **Web demo** with a public test tribe (e.g. "BCF-Test"), curated.
5. **Test vectors** from the official `BCF-XML` repo run automatically through CI.
6. **NIP draft as a PR** once (3) and (5) work — empirical validation before spec freeze.
7. **Pilot project** with a real building project (small, ideally your own) to harden the practice (round-trip tested with Solibri / BIMcollab import).

---

## Appendix A: Glossary

- **BCF** — BIM Collaboration Format, buildingSMART standard.
- **IFC** — Industry Foundation Classes, open model exchange format.
- **LOIN** — Level of Information Need (DIN EN 17412).
- **Topic** — a BCF issue with metadata, comments, viewpoints.
- **Viewpoint** — camera + visibility state + snapshot.
- **NIP** — Nostr Implementation Possibility, a spec extension of Nostr.
- **Replaceable event** — a Nostr event class for which the latest version per `(pubkey, kind[, d-tag])` is authoritative.
- **Blossom** — blob storage spec for the Nostr ecosystem (sha256-addressed).
- **OTS** — OpenTimestamps, a Bitcoin-timechain-based notary protocol.

## Appendix B: References

- buildingSMART BCF: https://github.com/buildingSMART/BCF
- buildingSMART BCF-API: https://github.com/buildingSMART/BCF-API
- Nostr NIPs: https://github.com/nostr-protocol/nips
- NDK (Nostr Development Kit): https://github.com/nostr-dev-kit/ndk
- Blossom: https://github.com/hzrd149/blossom
- OpenTimestamps: https://opentimestamps.org

---

*End of the research document. Discussion welcome — PRs to the open-questions list in section 15 first.*
