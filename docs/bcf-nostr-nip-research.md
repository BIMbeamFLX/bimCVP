# BCF over Nostr — Research für einen NIP-Draft

**Status:** Research-Vorlauf für ein NIP („BCF — BIM Collaboration over Nostr")
**Autor:** the maintainer (npub tbd) — Diskussionsentwurf
**Stand:** 2026-05-14
**Bezug:** buildingSMART BCF 3.0 (XML + REST API), Nostr Protocol (NIP-01 ff.)

---

## 0. Executive Summary

BCF (BIM Collaboration Format) ist der buildingSMART-Standard für Issue-/Koordinations-Kommunikation in BIM-Projekten und existiert in zwei Ausprägungen: BCF-XML (Container-Format, `.bcfzip`) und BCF-API (REST). Beide setzen heute einen klassischen Server-Client-Stack mit zentraler Autorität voraus (BIMcollab, ACC Issues, Solibri, Trimble Connect, usnap u. a.).

Nostr bietet einen alternativen Transport: signierte Events, npub-basierte Identität, Relay-föderierung, keine Plattform-Hoheit. Dieses Dokument beschreibt, wie BCF verlustfrei auf Nostr-Events abgebildet werden kann, schlägt einen Event-Kind-Bereich, eine Tag-Taxonomie und eine Mapping-Tabelle vor, und identifiziert die Stellen, an denen BCF und Nostr nicht trivial zusammengehen (Berechtigungen, Reihenfolge, Anhänge, Lifecycle).

Ziel ist ein NIP-Draft, der

1. eine eindeutige Repräsentation von BCF-Topics, Viewpoints und Comments als Nostr-Events definiert,
2. einen verlustfreien Round-trip BCF-XML ↔ Nostr ermöglicht,
3. die Identitäts- und Berechtigungslücke pragmatisch (NIP-29 + NIP-58) schließt,
4. Datei-Anhänge (Snapshot, IFC, BimSnippet) sauber über Blossom/NIP-94 löst.

---

## 1. BCF in 5 Minuten

BCF transportiert Koordinationsthemen, nicht Modelle. Ein BCF-Container hat ein Manifest und pro Topic einen Ordner.

**BCF-XML 3.0 — Kernelemente:**

- **Project Markup** (`project.bcfp`, optional): `Project @Guid`, `Name`, `ExtensionSchema` mit Listen für `TopicTypes`, `TopicStatuses`, `Priorities`, `TopicLabels`, `Users`, `SnippetTypes`, `Stages`.
- **Markup pro Topic** (`markup.bcf`):
  - `Header.Files.File` — Referenzen auf zugehörige IFC-Files (`IfcProject`, `IfcSpatialStructureElement`, Hash, Datum, Filename, `@IsExternal`).
  - `Topic @Guid @TopicType @TopicStatus @ServerAssignedId` — Titel, Priorität, Index, Labels, CreationDate, CreationAuthor, ModifiedDate, ModifiedAuthor, DueDate, AssignedTo, Stage, Description, BimSnippet, DocumentReferences, RelatedTopics.
  - `Comments.Comment @Guid` — Date, Author, Comment-Text, Viewpoint-Ref, ModifiedDate, ModifiedAuthor.
  - `Viewpoints.ViewPoint @Guid` — Referenz auf Viewpoint-File und Snapshot.
- **Viewpoint** (`viewpoint.bcfv`):
  - `Components` (`Selection`, `Visibility` mit `DefaultVisibility` und `Exceptions`, `ViewSetupHints`, `Coloring`),
  - `OrthogonalCamera` oder `PerspectiveCamera`,
  - `Lines`, `ClippingPlanes`, `Bitmaps`.
- **Snapshot** (`snapshot.png` o. ä.) — Bildreferenz, im Viewpoint verankert.

**BCF-API:** REST mit Resourcen `projects/{guid}/topics/{guid}/comments`, `viewpoints`, `files`, `documents`, `events`. Authentifizierung über OAuth, Rollenmodell pro Projekt.

**Was BCF nicht ist:** kein Modelltransport (IFC-Aufgabe), keine Aufwandskalkulation, keine Vertragsschicht.

---

## 2. Nostr in 5 Minuten (für BIM-Leser)

- **Identität:** secp256k1-Keypair, öffentliche Form als `npub1…` (bech32). Kein Konto-System.
- **Event:** signiertes JSON mit `id`, `pubkey`, `created_at`, `kind`, `tags[][]`, `content`, `sig`.
- **Kind-Bereiche** (siehe NIP-01):
  - `0–9999` regulär (alle Replicas behalten),
  - `10000–19999` replaceable (nur jüngstes Event pro `pubkey+kind`),
  - `20000–29999` ephemeral (Relays sollen nicht persistieren),
  - `30000–39999` parameterized replaceable (jüngstes pro `pubkey+kind+d-tag`),
  - `40000+` reserviert für weitere Kategorien.
- **Tags:** array von arrays, erstes Element ist Tagname (Konvention: kurz, lowercase).
- **Relays:** WebSocket-Server, push/pull-fähig, frei wählbar. Auth via NIP-42 möglich.
- **Wichtige NIPs für unseren Kontext:** NIP-09 (Delete), NIP-10 (Threading), NIP-17 (DM), NIP-19 (bech32), NIP-23 (Long-form), NIP-29 (Groups), NIP-42 (Auth), NIP-44 (Encryption), NIP-51 (Lists), NIP-58 (Badges), NIP-65 (Relay-Listen), NIP-72 (Communities), NIP-89 (Handler), NIP-94 (File-Metadata), NIP-96 (HTTP-File-Storage), Blossom (Blob-Storage, kein NIP, aber etabliert).

---

## 3. Design-Entscheidungen

Die wichtigsten Weichen, die ein NIP stellen muss:

### 3.1 Topic-Identität: replaceable vs. immutable

BCF-Topics ändern sich (Status, Assignee, Priority). Drei Optionen:

| Option | Vorteile | Nachteile |
|---|---|---|
| A) Topic = parameterized replaceable event (`kind 30900`, `d=topic-guid`) | klare „current state"-Sicht, identisch mit BCF-Semantik | History fehlt, Audit nur über zusätzliche Events |
| B) Topic = immutable event, Updates über separate Patch-Events (`e`-tag) | volle History, append-only | mehrere Events müssen reduziert werden, kompliziert für Clients |
| C) Hybrid: replaceable für „current", parallel immutable Audit-Event je Änderung | beste Welt, Round-trip möglich | doppelte Schreiblast |

**Empfehlung: Option C.** `kind:30900` trägt den aktuellen Zustand (replaceable), `kind:1171` (regulär) ist ein unveränderlicher Audit-Eintrag pro Änderung. Clients ohne Audit-Bedarf konsumieren nur 30900, forensische Tools rekonstruieren History aus 1171.

### 3.2 Comments: dedizierter Kind oder kind:1 mit Tags?

- **kind:1 + Tags:** maximale Reichweite (jeder Nostr-Client zeigt Kommentare), schwächere Semantik.
- **dedizierter kind:1170:** klare Semantik, aber nur BCF-aware Clients rendern.

**Empfehlung: dedizierter `kind:1170`,** zusätzlich Spiegelung als `kind:1`-Reply (optional, mit `nip:42`-tag-Hinweis), wenn der Autor Cross-Posting wünscht. Trade-off zwischen Spec-Sauberkeit und Reichweite explizit lösen.

### 3.3 Viewpoints

Viewpoints sind technisch eigene Artefakte mit eigener GUID, in BCF schon entkoppelt. Logisch parameterized replaceable (`kind:30901`, `d=viewpoint-guid`), referenziert vom Topic via `viewpoint`-Tag. Snapshot ist ein File (NIP-94, siehe 3.5).

### 3.4 Projektkontext

Projekte werden als Container nicht im Topic selbst, sondern als separates Event modelliert:

- **`kind:30902` BCF-Project** (parameterized replaceable, `d=project-guid`) — trägt Projekt-Metadaten, Extension-Schema (Listen für TopicTypes, Statuses, Priorities, Labels, Stages, SnippetTypes), Referenzen auf zugehörige IFC-Files.
- **Topic verweist via `a`-Tag** auf das Project-Event (Format `30902:<pubkey>:<project-guid>`).
- Für mehrnutzer-Projekte: Project-Event wird im Namen einer **NIP-29-Gruppe** publiziert (Group-Schlüssel signiert), nicht im Namen einer Einzelperson. Mitglieder schreiben in den Group-Container und Topics tragen den `h`-Tag der Gruppe.

### 3.5 Anhänge (Snapshot, IFC, BimSnippet, DocumentReference)

Binärdaten gehören nicht in Event-Content. Drei Pfade:

- **Blossom** (sha256-adressiert, simpel, etabliert) — empfohlen für Snapshots, BimSnippets, DocumentReferences.
- **NIP-96 HTTP-File-Storage** — alternativ, wenn Pinning/Quota gewünscht.
- **NIP-94 File-Metadata-Event** — für Provenance und Discovery: jedes File bekommt ein eigenes Event mit `url`, `m` (mime), `x` (sha256), `size`, `dim` etc.

**Empfehlung:** Blob auf Blossom, Discovery + Hash via NIP-94, Reference im Topic/Viewpoint via `e`-tag auf das NIP-94-Event ODER direkt via `imeta`/`x`/`url`-Tag.

### 3.6 Berechtigungen

BCF-API kennt Rollen pro Projekt. Nostr hat keine eingebauten Rollen. Lösung:

- **Gruppe (NIP-29)** definiert Mitgliedschaft + Mod-Rechte am Relay-Layer.
- **Berufliche Verifikation** über NIP-58-Badges, ausgegeben von Kammern/Verbänden (Ingenieurkammer, bvfi, CNI/Albo). Das Badge ist ein attestiertes Event auf den npub, das Clients zur Anzeige des „verified"-Stempels nutzen.
- **Vertragliche Bindung** (Werkvertrag, Berufshaftpflicht) bleibt offchain — siehe Abschnitt 11.

### 3.7 Identifier-Stabilität & Round-trip

BCF-GUIDs (UUID v4) müssen erhalten bleiben. Wir benutzen sie als `d`-Tag-Werte für die replaceable Events, nicht als Event-IDs. Das ist sauber, weil:

- die Nostr-Event-ID aus dem Inhalt deterministisch berechnet wird,
- der `d`-Tag-Wert frei wählbar und stabil über Replacements ist,
- ein BCF-XML-Export trivial die ursprünglichen GUIDs aus `d`-Tags rekonstruiert.

---

## 4. Vorgeschlagener Event-Kind-Bereich

| Kind | Name | Replaceable? | Zweck |
|---|---|---|---|
| `30900` | BCF Topic | parameterized replaceable | aktueller Topic-Zustand |
| `30901` | BCF Viewpoint | parameterized replaceable | Viewpoint-Definition |
| `30902` | BCF Project | parameterized replaceable | Projekt-Metadaten + Extension-Schema |
| `30903` | BCF Document Reference | parameterized replaceable | externes Dokument (DocumentReferences-Pendant) |
| `30904` | BCF File Reference | parameterized replaceable | IFC-/Modell-Datei-Referenz mit Hash, IfcProject, IfcSpatialStructureElement |
| `1170` | BCF Comment | regulär | Kommentar zu Topic oder Viewpoint |
| `1171` | BCF Audit Event | regulär | unveränderlicher Audit-Eintrag (Statuswechsel, Assignee-Change, Priority-Change) |
| `1172` | BCF Reaction | regulär | leichte Bestätigung („gesehen", „bearbeite ich") — orthogonal zu Status |

Begründung des Bereichs: 30900–30999 ist im Block für parameterized replaceable, lässt Raum für künftige BCF-Erweiterungen (etwa LOIN-Anforderungen, Mängel-Klassifikationen, IFC-Issue-Diagnoses), und 1170–1179 hält Comment-/Audit-/Reaction-Familie eng zusammen.

---

## 5. Tag-Taxonomie

| Tag | Werteform | Zweck | Pflicht? |
|---|---|---|---|
| `d` | UUID (BCF-GUID) | Identität replaceable Event | bei 309xx ja |
| `a` | `30902:<pubkey>:<project-guid>` | Projekt-Referenz | bei 30900, 30901, 1170, 1171 ja |
| `h` | NIP-29 group-id | Gruppen-Kontext | falls Projekt in NIP-29-Gruppe |
| `e` | event-id (parent/topic/viewpoint/file) | Verknüpfung | Comment → Topic: ja |
| `p` | pubkey | beteiligte Personen (Assignee, Reporter, Watcher) | wo zutreffend |
| `t` | string | BCF-Label oder freier Tag | optional |
| `bcf-status` | string | aktueller Status (Open, InProgress, Resolved, Closed, …) | bei 30900 ja |
| `bcf-type` | string | TopicType (Issue, Clash, RFI, …) | bei 30900 ja |
| `bcf-priority` | string | Priorität (Low, Normal, High, Critical) | optional |
| `bcf-stage` | string | Projektphase | optional |
| `bcf-due` | unix-ts | DueDate | optional |
| `bcf-index` | int | Index | optional |
| `viewpoint` | event-id | Viewpoint-Referenz für Topic/Comment | optional |
| `snapshot` | url + sha256 | Schnellzugriff auf Snapshot | optional |
| `ifc` | IFC-GUID | referenziertes IFC-Element | mehrfach erlaubt |
| `ifc-file` | event-id (kind 30904) | referenzierte Modelldatei | mehrfach erlaubt |
| `audit-field` | string | bei 1171: welches Feld geändert wurde | bei 1171 ja |
| `audit-from`, `audit-to` | string | alter/neuer Wert | bei 1171 ja |
| `bcf-version` | string | „3.0" — BCF-Schemaversion | bei 30900 ja |
| `client` | string | Erzeuger-Client (analog NIP-89) | optional |

**Konvention:** alle BCF-spezifischen Tags mit `bcf-`-Präfix, damit sie in generischen Nostr-Clients nicht mit Standard-Tags kollidieren.

---

## 6. Vollständige Mapping-Tabelle BCF-XML → Nostr

### 6.1 Project Markup (`project.bcfp`) → `kind:30902`

| BCF | Nostr |
|---|---|
| `Project @Guid` | `d`-Tag |
| `Project.Name` | `content.name` |
| `ExtensionSchema.TopicTypes/Type` | `content.extension.topic_types[]` |
| `ExtensionSchema.TopicStatuses/Status` | `content.extension.topic_statuses[]` |
| `ExtensionSchema.Priorities/Priority` | `content.extension.priorities[]` |
| `ExtensionSchema.TopicLabels/Label` | `content.extension.topic_labels[]` |
| `ExtensionSchema.Stages/Stage` | `content.extension.stages[]` |
| `ExtensionSchema.SnippetTypes/SnippetType` | `content.extension.snippet_types[]` |
| `ExtensionSchema.Users/User` | `content.extension.users[]` (string-Liste, optional + `p`-Tag-Spiegelung) |

### 6.2 Markup → `kind:30900` (Topic)

| BCF | Nostr |
|---|---|
| `Topic @Guid` | `d`-Tag |
| `Topic @ServerAssignedId` | `content.server_assigned_id` |
| `Topic @TopicType` | `bcf-type`-Tag |
| `Topic @TopicStatus` | `bcf-status`-Tag |
| `Topic.Title` | `content.title` |
| `Topic.Priority` | `bcf-priority`-Tag |
| `Topic.Index` | `bcf-index`-Tag |
| `Topic.Labels/Label[]` | `t`-Tags (eins pro Label) |
| `Topic.CreationDate` | `content.created_date` (ISO 8601) + Event-`created_at` als unix-ts |
| `Topic.CreationAuthor` | `content.created_author` (E-Mail oder Klarname) + Event-`pubkey` |
| `Topic.ModifiedDate` | Event-`created_at` der jüngsten Replaceable-Revision |
| `Topic.ModifiedAuthor` | Event-`pubkey` der jüngsten Revision |
| `Topic.DueDate` | `bcf-due`-Tag (unix-ts) + `content.due_date` (ISO 8601) |
| `Topic.AssignedTo` | `p`-Tag mit zusätzlichem 4. Element „assignee" + `content.assigned_to` (E-Mail-Fallback) |
| `Topic.Stage` | `bcf-stage`-Tag |
| `Topic.Description` | `content.description` |
| `Topic.BimSnippet` | `e`-Tag → kind 30903 (Document Reference, type=snippet) |
| `Topic.DocumentReferences/DocumentReference` | `e`-Tag(s) → kind 30903 |
| `Topic.RelatedTopics/RelatedTopic` | `e`-Tag → andere kind:30900 mit Marker „related" |
| `Topic.Comments` | nicht eingebettet — Comments sind eigene Events (kind:1170) mit `e`-Tag auf Topic |
| `Topic.Viewpoints` | `viewpoint`-Tags → kind:30901 |
| `Header.Files/File` | `ifc-file`-Tags → kind:30904 |

### 6.3 Comment → `kind:1170`

| BCF | Nostr |
|---|---|
| `Comment @Guid` | `content.guid` (UUID, beibehalten für Round-trip) — Event-`id` ist Nostr-nativ |
| `Comment.Date` | Event-`created_at` |
| `Comment.Author` | Event-`pubkey` (+ `content.author_email` für Round-trip) |
| `Comment.Comment` | `content.text` |
| `Comment.Viewpoint @Guid` | `viewpoint`-Tag → kind:30901 Event-id |
| `Comment.ModifiedDate` | bei Edit: separates kind:1170-Event mit `e`-Tag „replaces" auf Vorgänger; Original via NIP-09-Delete entfernen (siehe 8.3) |
| `Comment.ModifiedAuthor` | Event-`pubkey` der neuen Version |

### 6.4 Viewpoint → `kind:30901`

| BCF | Nostr |
|---|---|
| `VisualizationInfo @Guid` | `d`-Tag |
| `Components.Selection/Component[]` | `content.components.selection[]` (Liste mit `ifc_guid`, `originating_system`, `authoring_tool_id`) + `ifc`-Tags pro Element |
| `Components.Visibility @DefaultVisibility` | `content.components.visibility.default` |
| `Components.Visibility.Exceptions/Component[]` | `content.components.visibility.exceptions[]` |
| `Components.Visibility.ViewSetupHints` | `content.components.view_setup_hints` (Object) |
| `Components.Coloring/Color[]` | `content.components.coloring[]` |
| `OrthogonalCamera` oder `PerspectiveCamera` | `content.camera` (typed object mit `type`, `view_point`, `direction`, `up_vector`, `view_to_world_scale` / `field_of_view`) |
| `Lines/Line[]` | `content.lines[]` |
| `ClippingPlanes/ClippingPlane[]` | `content.clipping_planes[]` |
| `Bitmaps/Bitmap[]` | `content.bitmaps[]` (mit Blossom-Hash-Referenzen) |
| `snapshot.png` | `snapshot`-Tag (url + sha256) oder `e`-Tag → NIP-94-Event |

### 6.5 IFC-File-Referenz → `kind:30904`

| BCF | Nostr |
|---|---|
| `File @IfcProject` | `content.ifc_project` |
| `File @IfcSpatialStructureElement` | `content.ifc_spatial_structure_element` |
| `File @IsExternal` | `content.is_external` (bool) |
| `File.Filename` | `content.filename` |
| `File.Date` | `content.date` (ISO 8601) |
| `File.Reference` | `content.reference` (url) + `x`-Tag (sha256) |

### 6.6 Document Reference → `kind:30903`

| BCF | Nostr |
|---|---|
| `DocumentReference @Guid` | `d`-Tag |
| `DocumentReference.DocumentGuid` | `content.document_guid` (BCF 3.0) |
| `DocumentReference.Url` | `content.url` |
| `DocumentReference.Description` | `content.description` |

---

## 7. Beispiele

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
  "content": "{\"name\":\"Rückhaltebecken St. Pauli\",\"extension\":{\"topic_types\":[\"Issue\",\"Clash\",\"RFI\"],\"topic_statuses\":[\"Open\",\"InProgress\",\"Resolved\",\"Closed\"],\"priorities\":[\"Low\",\"Normal\",\"High\",\"Critical\"],\"topic_labels\":[\"HKLS\",\"Statik\",\"Architektur\",\"ELT\"],\"stages\":[\"LP3\",\"LP4\",\"LP5\",\"LP6\"],\"snippet_types\":[\"clash\",\"mvd\"],\"users\":[]}}",
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
    ["bcf-version", "3.0"],
    ["bcf-type", "Clash"],
    ["bcf-status", "Open"],
    ["bcf-priority", "High"],
    ["bcf-index", "42"],
    ["bcf-due", "1749600000"],
    ["bcf-stage", "LP4"],
    ["t", "HKLS"],
    ["t", "Statik"],
    ["p", "<assignee-pubkey>", "", "assignee"],
    ["ifc", "0aB1cD2eF3gH4iJ5kL6mN7"],
    ["ifc-file", "<kind-30904-event-id>"],
    ["viewpoint", "<kind-30901-event-id>"],
    ["snapshot", "https://blossom.example/abc123.png", "sha256:abc123…"]
  ],
  "content": "{\"title\":\"Lüftungsleitung kreuzt Hauptträger Achse 4\",\"description\":\"Kollision im Bereich Decke EG bei Achse 4/B. Vorschlag: Lüftung auf -350 mm absenken, Träger-Voute prüfen.\",\"created_date\":\"2026-05-14T08:20:34Z\",\"created_author\":\"planner@example.org\",\"due_date\":\"2026-06-11T00:00:00Z\",\"server_assigned_id\":\"BSP-2026-042\"}",
  "pubkey": "<author-pubkey>",
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
    ["p", "<author-pubkey>"],
    ["viewpoint", "<kind-30901-event-id>"]
  ],
  "content": "{\"text\":\"Träger kann nicht abgesenkt werden, Stahlbau ist freigegeben. Vorschlag: Lüftung über Träger führen, Querschnitt 800x300 → 600x400.\",\"guid\":\"7a9b2c3d-4e5f-9c3b-4a5c-1d6e4a2b8b1f\"}",
  "pubkey": "<statik-pubkey>",
  "id": "<sha256>",
  "sig": "<schnorr-sig>"
}
```

### 7.4 Audit-Event (`kind:1171`)

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
    ["snapshot", "https://blossom.example/abc123.png", "sha256:abc123…"]
  ],
  "content": "{\"camera\":{\"type\":\"perspective\",\"view_point\":{\"x\":12.5,\"y\":-8.3,\"z\":2.6},\"direction\":{\"x\":0.42,\"y\":0.86,\"z\":-0.27},\"up_vector\":{\"x\":0,\"y\":0,\"z\":1},\"field_of_view\":60},\"components\":{\"selection\":[{\"ifc_guid\":\"0aB1cD2eF3gH4iJ5kL6mN7\"}],\"visibility\":{\"default\":true,\"exceptions\":[]}}}",
  "pubkey": "<author-pubkey>",
  "id": "<sha256>",
  "sig": "<schnorr-sig>"
}
```

---

## 8. Verhalten & Algorithmen

### 8.1 Topic-Status: Quelle der Wahrheit

Das jüngste `kind:30900`-Event (per `created_at`, Ties durch lexikografisch kleinste Event-`id` gebrochen — analog NIP-01 für replaceable) ist der aktuelle Zustand. Audit-Events (`kind:1171`) sind erklärend, nicht autoritativ.

Konfliktfall: zwei Replacements mit identischem `created_at` und konfligierenden Werten — Algorithmus wählt deterministisch, aber Clients SOLLEN den Konflikt sichtbar machen und Vorschlag „letzter Autor entscheidet" oder „eskalieren an Mod" anbieten.

### 8.2 Reihenfolge bei Comments

Comments sind kausal sortiert über `created_at`. Replies an Comments (Threading) verwenden NIP-10 Marker („reply"/„root"). BCF kennt kein Threading nativ — wir erweitern hier vorsichtig: ein Comment kann optional einen anderen Comment per `e`-Tag mit Marker „reply" referenzieren; bei BCF-XML-Export wird das auf flache Comment-Liste platt gemacht (Reihenfolge nach `created_at`).

### 8.3 Comment-Edits

Nostr-Events sind unveränderlich. Comment-Edit-Workflow:

1. Autor publiziert neues `kind:1170`-Event mit `e`-Tag-Marker „replaces" auf Vorgänger-Event-id.
2. Autor publiziert NIP-09 Delete (`kind:5`) auf Vorgänger.
3. Clients zeigen jüngste Version, behalten aber alle Versionen lokal im Audit-Cache.

Bei BCF-XML-Export gewinnt die jüngste, `ModifiedDate`/`ModifiedAuthor` werden gesetzt.

### 8.4 Topic-Schließen, -Wiederaufmachen, -Löschen

- Schließen: Status-Replacement auf "Closed". Topic bleibt persistent.
- Wiederaufmachen: Status-Replacement auf "Open" oder "InProgress".
- Löschen: NIP-09 Delete-Event vom Topic-Autor oder Gruppen-Mod; Relays sollen replizieren, müssen aber nicht löschen (eventually consistent). Praxistipp: harte Löschungen vermeiden, lieber Status "Closed" + Label "WONTFIX" oder ähnlich.

### 8.5 Round-trip-Garantien

Implementierungen MÜSSEN folgendes Round-trip-Verhalten zeigen:

1. BCF-XML → Nostr-Events → BCF-XML produziert ein semantisch äquivalentes Output (alle Topic-GUIDs, Viewpoint-GUIDs, Comment-GUIDs unverändert; Reihenfolge der Comments per `created_at`).
2. Nostr-Events → BCF-XML → Nostr-Events ist nicht garantiert kanonisch (Event-IDs ändern sich, weil Inhalt evtl. neu serialisiert wird), aber semantisch äquivalent.

Test-Vektoren: jedes BCF-3.0-Beispiel aus dem offiziellen `bcf-xml`-Repository (buildingSMART) wird mit erwartetem Nostr-Event-Set abgelegt. Siehe Abschnitt 13.

---

## 9. Datei-Layer

### 9.1 Blossom

Empfohlener Default. Server akzeptiert PUT mit Body, antwortet mit `{url, sha256, size, type}`. Client speichert `url` + `sha256` als Tag-Werte.

### 9.2 NIP-94 Begleit-Event

Für jede relevante Datei (Snapshot ≥ 1 MB, IFC, BimSnippet, Document) publiziert der Client ein `kind:1063`-Event:

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
  "content": "Snapshot für Topic Achse 4/B"
}
```

Vorteile: konsistente Provenance, Suchbarkeit, einfacher Mirror auf Sekundär-Blossom.

### 9.3 IFC-Modelle

Große IFC-Files (>200 MB) sind grenzwertig für Blossom. Pragmatisch:

- IFC-File auf privatem Blossom des Projekts (Pinning durch Owner).
- `kind:30904` BCF-File-Reference verlinkt url + sha256.
- Optional: zusätzlich OpenTimestamps-Anker auf der Timechain für Notar-Funktion (siehe „IFC-Notar"-Projekt).

### 9.4 Verschlüsselung

Falls Projekt vertraulich (Sicherheits-Infrastruktur, militärisch, KRITIS):

- Blob-Verschlüsselung clientseitig (AES-256-GCM), Schlüssel im Group-Event (NIP-29) für Mitglieder verfügbar.
- Event-Content (Topic-Description, Comment-Text) optional NIP-44-verschlüsselt; Tag-Werte bleiben Cleartext, müssen entsprechend kuratiert sein.

---

## 10. Beziehung zu bestehenden NIPs

| NIP | Verwendung in BCF-over-Nostr |
|---|---|
| NIP-01 | Basis-Eventformat, replaceable-Semantik |
| NIP-09 | Delete von Topics/Comments |
| NIP-10 | Comment-Threading (Marker „reply"/„root") |
| NIP-17 | optionale private Coordination-DMs (z. B. „Auftraggeber bittet um Rückruf") |
| NIP-19 | Bech32-Encoding für Cross-Tool-Links (`naddr1…` für Topics) |
| NIP-23 | Long-form-Begründungen, gerne als Annex zu Topics (separates Event, via `e`-Tag verlinkt) |
| NIP-29 | Projekt-Container (private Gruppe), Mitgliedschaft, Mod-Rechte |
| NIP-42 | Relay-Auth (Pflicht für nicht-öffentliche Projekt-Relays) |
| NIP-44 | Content-Verschlüsselung bei vertraulichen Projekten |
| NIP-51 | Listen für „beobachtete Topics", „Lesezeichen" |
| NIP-58 | Berufs-Badges (Kammer-Attestation, Zertifizierung) |
| NIP-65 | Relay-Listen pro Planer |
| NIP-72 | öffentliche Tribes / Communities (Bauwesen-DACH, Sovereign Engineering DACH) |
| NIP-89 | Recommended-Apps-Handling (Client-Empfehlungen für unbekannte Kinds) |
| NIP-94 | File-Metadata pro Snapshot / IFC / BimSnippet |
| NIP-96 | optional alternative zum Blossom-Storage |

---

## 11. Gap-Analyse: was BCF kann, Nostr nicht (out-of-the-box)

| BCF-Funktion | Nostr-Lücke | Lösung im NIP |
|---|---|---|
| Rollen pro Projekt (Reviewer, Manager, Read-only) | keine Standardrollen | NIP-29 Mod-Layer + 4. Element in `p`-Tag („role"); für stempelnde Rollen NIP-58 Badge |
| Server-assigned Topic-IDs | nicht zentral | `server_assigned_id` im `content` belassen; Vergabe entweder durch Mod-Bot im Group-Container (deterministisch nach `created_at`) oder freihändig durch Autor |
| Aktivitätslog-Endpoint (BCF-API `/events`) | nicht standardisiert | Audit-Events (`kind:1171`) + Filter `kinds:[1171]`+`#a:[<project>]` |
| Datei-Quota / Pinning | keine Garantie | Blossom mit Bezahl-/Member-Modell; Eigentümer pinnt selbst |
| Permanenz | Relays können löschen | Eigenes Projekt-Relay (strfry, nostr-rs-relay) + OpenTimestamps-Anker für Final-Stände |
| Standardisierte TopicTypes / Statuses | Free-form Tags | Über `kind:30902 ExtensionSchema` projektweise definiert (BCF-Original-Mechanik) |
| Verbindliche Identität | npub ist Pseudonym | Kammern-Badge per NIP-58 + offchain Werkvertrag mit Klarnamen-Bindung |
| Lieferschein/Abnahmedokument | nicht in Nostr | Optional separates Event `kind:30910` „BCF Hand-over" mit kompletter Topic-Liste + OTS-Anker — Erweiterung im NIP empfehlen |

---

## 12. Sicherheits- und Privacy-Modell

### 12.1 Bedrohungsmodell

- **Manipulation:** durch Schnorr-Signatur ausgeschlossen pro Event; Replacement-Reihenfolge muss überwacht werden (siehe 8.1).
- **Repudiation:** ausgeschlossen — jede Aktion signiert.
- **Vertraulichkeit:** Standard Cleartext im Relay. Für sensible Projekte NIP-29 + NIP-44 + Blob-Verschlüsselung.
- **Verfügbarkeit:** Relay-Ausfall → mehrere Relays empfehlen (NIP-65 Outbox-Pattern). Empfohlen: Eigenes Projekt-Relay (Pflicht-Schreiben) + 2 redundante Spiegel.
- **Sybil:** in öffentlichen Tribes über NIP-58-Badges / NIP-72-Mod-Layer.
- **Spam:** Relay-seitig (Allowlist, Auth, PoW NIP-13 optional).

### 12.2 Schlüsselverwaltung

Empfehlung: Planer-npub im Hardware-Signer (Amber/nsec.app/NSec-Bunker). Verbindung zu beruflicher Identität via NIP-58 Badge, ausgegeben von Kammer; Badge ist widerrufbar (NIP-09 Delete vom Aussteller).

### 12.3 Datenschutz (DSGVO, GDPR)

- Comment-Inhalte und Topic-Beschreibungen können personenbezogene Daten enthalten.
- Recht auf Löschung: NIP-09 nur best-effort. Für DSGVO-konforme Projekte: privates Relay mit klarem Operator → Auftragsverarbeitung; öffentliche Tribes nicht für personenbezogene Inhalte verwenden.
- Empfehlung im NIP: Hinweis-Abschnitt „Privacy Considerations" mit obigen Punkten.

---

## 13. Referenzimplementierung & Test-Vektoren

### 13.1 Minimaler Stack für Proof-of-Concept

- Web-Client: Next.js / Astro, `nostr-tools` oder `ndk`, Three.js / xeokit für Viewpoint-Rendering.
- Relay: `nostr-rs-relay` oder `strfry` mit NIP-42, NIP-29-Patch.
- Blob: einer der etablierten Blossom-Server (`blossom-server-rs`).
- Importer/Exporter: TypeScript-CLI `bcf-nostr` mit Subcommands `import <file.bcfzip>` und `export <project-naddr> <out.bcfzip>`.

### 13.2 Test-Vektoren

Für jedes BCF-3.0-Beispiel aus dem `buildingSMART/BCF-XML`-Repo werden abgelegt:

- Eingangs-`.bcfzip`,
- Zielmenge Nostr-Events (kanonisch sortiert, deterministischer `created_at` via Date des BCF),
- Round-trip-Output `.bcfzip` mit Hash-Vergleich der `markup.bcf`-XML-Elemente nach Normalisierung.

Damit ist Konformität messbar.

---

## 14. NIP-Draft-Skelett

Ein konkreter NIP-Draft sollte folgende Sektionen enthalten:

```
NIP-XXX
=======

BCF — BIM Collaboration over Nostr
----------------------------------

`draft` `optional` `author:maintainer`

Abstract
~~~~~~~~
Defines event kinds, tags, and conventions to represent buildingSMART BCF 3.0
issues, comments, viewpoints, projects, and file references on Nostr.

Motivation
~~~~~~~~~~
[ca. 200 Wörter — Bezug auf Plattform-Lock-in, BIM-Koordination, Souveränität,
verlustfreier Austausch]

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
d, a, h, e, p, t, bcf-status, bcf-type, bcf-priority, bcf-stage, bcf-due,
bcf-index, viewpoint, snapshot, ifc, ifc-file, audit-field, audit-from,
audit-to, bcf-version, client

Schema (JSON, BCF 3.0 Mapping)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
[siehe Mapping-Tabelle Abschnitt 6]

Behavior
~~~~~~~~
[8.1–8.5 als normative Klauseln, MUST/SHOULD]

File Handling
~~~~~~~~~~~~~
[NIP-94 / Blossom — Empfehlung, kein Zwang]

Relations to Other NIPs
~~~~~~~~~~~~~~~~~~~~~~~
[Tabelle aus Abschnitt 10]

Security Considerations
~~~~~~~~~~~~~~~~~~~~~~~
[Abschnitt 12]

Test Vectors
~~~~~~~~~~~~
[Link auf Referenz-Repo]
```

---

## 15. Offene Fragen / Diskussions­bedarf

1. **Kind-Bereich:** ist `30900–30904 / 1170–1172` mit der bestehenden Allokationspraxis kompatibel? PR an `nostr-protocol/nips` erforderlich, um die Reservierung zu sichern.
2. **Verhältnis BCF-API ↔ Nostr-NIP:** soll der NIP nur den XML-Container abbilden, oder auch BCF-API-Endpoints semantisch ersetzen? Empfehlung: zunächst XML-paritätisch, API als Folge-NIP.
3. **Zukunft BCF 4.0:** Welche zu erwartenden Felder (z. B. erweiterte LOIN-Referenzen, multi-modale Snapshots) brauchen jetzt schon Reserveraum?
4. **Mod-Layer:** reicht NIP-29 oder ist ein dedizierter NIP für „Project-Roles" sinnvoll, der über reine Group-Mods hinausgeht (Reviewer, Approver, Stamper)?
5. **OpenTimestamps-Integration:** Standardisieren als Tag (`ots`-Tag mit OTS-Proof) oder dem Anwender überlassen? Empfehlung: Standardisieren, weil das einer der stärksten Use-Cases ist.
6. **Localization:** Topic-Beschreibungen mehrsprachig? Vorschlag: `content.title_i18n` als Map, sonst Sprach-Tag `lang`.
7. **Cashu-/Lightning-Hook:** Soll ein Topic optional eine Bounty tragen (Auszahlung bei Status=Resolved)? Andocken an DVM-Logik (NIP-90) als optionaler Begleit-Event. Empfehlung: ja, als optionales Feature außerhalb des Kern-NIP.

---

## 16. Empfohlene nächste Schritte

1. **Konsens-Sondierung in der buildingSMART-Open-Source-Community** (Slack `bsi`, Forum) — frühe Diskussion vermeidet Doppelarbeit.
2. **Nostr-Seite:** Issue im `nostr-protocol/nips`-Repo eröffnen, Kind-Bereich allokieren lassen.
3. **Referenz-Importer/Exporter** als CLI auf GitHub, MIT-Lizenz.
4. **Web-Demo** mit einem öffentlichen Test-Tribe (z. B. „BCF-Test-DACH"), kuratiert.
5. **Test-Vektoren** aus offiziellem `BCF-XML`-Repo automatisiert durch CI laufen lassen.
6. **NIP-Draft als PR** sobald (3) und (5) funktionieren — empirische Validierung vor Spec-Freeze.
7. **Pilotprojekt** mit echtem Bauvorhaben (klein, idealerweise eigenes), um die Praxis zu härten (Round-trip mit Solibri / BIMcollab-Import getestet).

---

## Anhang A: Glossar

- **BCF** — BIM Collaboration Format, buildingSMART-Standard.
- **IFC** — Industry Foundation Classes, offenes Modellaustauschformat.
- **LOIN** — Level of Information Need (DIN EN 17412).
- **Topic** — BCF-Issue mit Metadaten, Comments, Viewpoints.
- **Viewpoint** — Kamera + Sichtbarkeitsstatus + Snapshot.
- **NIP** — Nostr Implementation Possibility, Spec-Erweiterung von Nostr.
- **Replaceable Event** — Nostr-Event-Klasse, von der jüngste Version je `(pubkey, kind[, d-tag])` autoritativ ist.
- **Blossom** — Blob-Storage-Spec für Nostr-Ökosystem (sha256-adressiert).
- **OTS** — OpenTimestamps, Bitcoin-Timechain-basiertes Notar-Protokoll.

## Anhang B: Referenzen

- buildingSMART BCF: https://github.com/buildingSMART/BCF
- buildingSMART BCF-API: https://github.com/buildingSMART/BCF-API
- Nostr NIPs: https://github.com/nostr-protocol/nips
- NDK (Nostr Development Kit): https://github.com/nostr-dev-kit/ndk
- Blossom: https://github.com/hzrd149/blossom
- OpenTimestamps: https://opentimestamps.org

---

*Ende des Research-Dokuments. Diskussion willkommen — PRs an die offene Frage-Liste in Abschnitt 15 zuerst.*
