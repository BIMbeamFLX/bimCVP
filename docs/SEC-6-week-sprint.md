# SEC 6-Week Sprint — ein HTML-Prototyp pro Woche

**Constraint.** Jeder Prototyp ist eine einzelne HTML-Datei (oder eine Hand voll), läuft im Browser, kein Backend. Identität per NIP-07 (Alby, nos2x) oder nsec-Eingabe. Storage via Blossom-URLs. Deploy auf Vercel/Cloudflare Pages in 3 Minuten.

**Parallele Produkt-Schiene (nicht Teil des SE-Sprints).**

- **AdlerHort** — lokaler, GDPR-konformer AI-Datenfilter für Planungsbüros. Ollama/qwen3 + Qdrant + SQLite + FastAPI, eigene Hardware, ISO-19650-aligned. Phase 0 (Dedup) bereit, Phase 1 (Scan & Review) in Entwicklung. Eigenes Geschäftsmodell (FOSS-Core + SaaS-Premium).
- **ZapViz** — Lightning-powered Real-time AI-Art-Installation. StreamDiffusion-Docker + GPU + LNbits + Ollama/Groq. Produkt für Partys/Events, eigener Stack.

Beides läuft parallel, kein Konflikt. SE-Sprint baut den Nostr-/Bauwesen-Layer dünn als HTML-Schicht obendrauf.

**Stack-Skelett für alle 6 Wochen:**

```
<!doctype html>
<html lang="de">
<head>…NDK von CDN, evtl. Chart.js / OTS-JS / marked…</head>
<body>
  <main id="app"></main>
  <script type="module">
    import NDK from "https://esm.sh/@nostr-dev-kit/ndk";
    // 200–500 Zeilen Vanilla JS
  </script>
</body>
</html>
```

Keine Frameworks, kein Bundler, kein Tailwind-Compile. Vanilla DOM + CSS inline.

---

## W1 — citadel-open-content.html

**Konzept in einem Satz.** Eine HTML-Datei, die NIP-23-Artikel von kuratierten AEC/HKLS-npubs aggregiert und als „Open Content"-Sektion in citadel-resources einbettbar macht.

**User Story.** Jemand öffnet citadel-resources.com/open-content. Sieht Live-Feed der letzten 20 NIP-23-Artikel aus der AEC-Tribe, gefiltert nach Tags (HKLS, BIM, Bau, Sanierung, Circular). Klick öffnet den Artikel, npub-Author + Datum sichtbar.

**Event-Kinds.** `kind:30023` (NIP-23 long-form), optional `kind:0` für Author-Profile.

**Curated-List.** JSON-Konstante mit ~10 npubs am Start. Später per NIP-51-Liste extrahierbar.

**Render.** Marked.js für Markdown, Lazy-Load Bilder, Tag-Chips als Filter.

**Deliverable.** Eine `.html`, deploybar als statische Sektion oder PR-fähig gegen citadel-resources.

**Stretch.** Mehrsprachiger Filter (de/en/it), RSS-Export für Embed in andere Sites.

**Risiken.** Leere Feeds wenn npub-Liste schlecht kuratiert. Mitigation: Default-Liste vorab seeden, eigene Artikel als Starter publizieren.

---

## W2 — bcf-quickform.html

**Konzept in einem Satz.** Ein HTML-Formular, das ein BCF-Topic-Event auf Nostr publisht — die kleinste denkbare BCF-Implementation.

**User Story.** Planer öffnet die Seite, loggt sich per Alby ein, füllt Titel/Beschreibung/Status/Priorität/Due-Date aus, klickt Publish. Topic erscheint sofort im Feed darunter. Andere Planer sehen es live.

**Event-Kinds.** `kind:30900` BCF Topic.

**Felder.** Title, Description, bcf-status, bcf-type, bcf-priority, bcf-due, t-Tags, optional Snapshot-URL.

**Feed.** Live-Subscribe auf alle 30900-Events der zuletzt 7 Tage einer kleinen Test-Tribe (NIP-29 group oder fester npub-Set).

**Deliverable.** Eine `.html`, hübsch genug für Demo. Optionale CLI `bcf2nostr.ts` als Beigabe.

**Stretch.** BCF-XML-Import per File-Drop → automatisches Event-Mapping.

**Risiken.** Schlüssel-Handling für nicht-NIP-07-User. Mitigation: nsec-Eingabe als Fallback, mit lauter Warnung.

---

## W3 — bcf-thread.html

**Konzept in einem Satz.** Erweiterung von W2: ein Topic-Detail-View mit Comment-Threading, Status-Audit-Trail und Snapshot-Anzeige — die zweite Hälfte des BCF-Prototyps.

**User Story.** Klick auf Topic in W2-Feed → öffnet Detail-Seite mit Snapshot oben, Beschreibung, Comment-Thread chronologisch, Audit-Trail kollabiert (Status-Wechsel mit Zeit + Autor). Eingabefeld unten für neuen Comment. Status-Dropdown für Berechtigte (= Assignee oder Mod).

**Event-Kinds.** `kind:1170` Comment, `kind:1171` Audit, `kind:30900` Topic (für Status-Replacement).

**Threading.** NIP-10-Marker („root" auf Topic, „reply" auf Parent-Comment).

**Audit-Trail.** Bei Status-Change publisht der Client beides: aktualisiertes 30900 (replaceable) + ein 1171-Event mit `audit-field`/`audit-from`/`audit-to`.

**Deliverable.** Erweiterung der W2-HTML oder zweite Datei `bcf-thread.html`, per `?topic=<naddr>` aufrufbar.

**Stretch.** Reactions (kind:1172) als Quick-Acknowledgments („gesehen", „bearbeite ich").

**Risiken.** Status-Replacement-Race-Conditions bei parallelen Editoren. Mitigation: letzter `created_at` gewinnt, Konflikt sichtbar machen.

---

## W4 — ots-bautagebuch.html

**Konzept in einem Satz.** Tagebucheintrag (Wetter, Personal, Lieferungen, Vorkommnisse) als signiertes Nostr-Event + OpenTimestamps-Anker auf der Bitcoin-Timechain — gerichtsfeste Beweissicherung in einem HTML-Formular.

**User Story.** Bauleiter öffnet ots-bautagebuch.html, loggt sich per Alby ein, füllt Tagesfelder aus (Datum, Projekt, Wetter, Anwesend, Lieferungen, Vorkommnisse, Fotos via Blossom-URL), klickt „Eintrag siegeln". Event wird auf Nostr publisht + OTS-Stamp gegen die Timechain abgesetzt. Nach 1–6 h ist der Stamp finalisiert. Verify-Button zeigt OTS-Proof als JSON-Download + Zertifikatsseite mit Block-Höhe und Block-Hash.

**Event-Kind.** `kind:30960` Bau-Tagebucheintrag (parameterized replaceable, d=`<project-id>-YYYY-MM-DD`).

**Tags.** `a` (Projekt-Ref), `date`, `weather`, `t` (Status: draft/sealed/verified), `ots` (OTS-Proof-Hash nach Upgrade).

**Tech.** `javascript-opentimestamps` für Stamp + Upgrade, NDK für Publish, simples Formular.

**Verify-Workflow.** Eintrag laden → OTS-Proof aus Tag rekonstruieren → gegen Bitcoin-Calendar abgleichen → Block-Höhe + Zeitpunkt anzeigen.

**Deliverable.** Eine `.html`, mit Demo-Eintrag und Verify-Flow.

**Stretch.** Tribe-weite Wettersummary (alle Bautagebücher einer Region aggregiert), Wochenbericht-Export als PDF.

**Risiken.** OTS-Upgrade-Latenz (mehrere Stunden bis Bitcoin-Confirmation). Mitigation: Status-Anzeige „pending → confirmed" mit Auto-Refresh.

**Hebel.** Bautagebücher sind in DACH-Bauverträgen Pflicht-Doku und im Streitfall vor Gericht zentral. Eine kryptographisch gesicherte Variante kostet praktisch nichts und ist juristisch ein starker Vorteil.

---

## W5 — plebbim.html

**Konzept in einem Satz.** Plebeian-Style Bounty-Board für BCF-Issues — jedes offene Topic kann mit Lightning-Zaps gefördert werden, der Resolver kassiert den Pot.

**User Story.** Bauleiter öffnet plebbim.html?tribe=<naddr>. Sieht Karten-Grid offener BCF-Topics, sortiert nach Bounty-Volumen. Jede Karte zeigt Titel, Status, Priorität, Due-Date, kumulierte Sats und einen „Fund this issue"-Button (NIP-57-Zap auf das Topic-Event). Bei Status-Change auf „Resolved" wechselt die Karte in einen anderen Stack und zeigt den Resolver-npub als Empfänger des Pots. Filter: nur funded, nur überfällig, nach t-Tag.

**Event-Kinds.**

- liest `kind:30900` (Topics), `kind:9735` (Zap Receipts auf Topics), `kind:1171` (Status-Changes)
- publisht Zaps via NIP-57-Workflow (Zap-Request kind:9734 → LNURL-Call → Bezahlt → Receipt kind:9735)

**Visualisierung.** Card-Grid mit Progress-Bars für Bounty-Volumen, kleines Bar-Chart oben („top zapped issues this week").

**Deliverable.** Eine `.html`, demobar mit den Testdaten aus W2/W3 und Live-Zaps aus echten Wallets (Alby, Mutiny, Wallet of Satoshi).

**Stretch.** Cashu-Token-Funding als Alternative zu LN, Auto-Mod-Nachricht im NIP-29-Channel bei Bounty-Vergabe, Sankey-View „wer zappt wen am häufigsten".

**Risiken.**

- Zap-Auszahlungs-Logik beim Status-Wechsel — wer kontrolliert die Auszahlung? Für MVP: alle Zaps gehen direkt an den Topic-Autor (sicherer Default), echte Escrow-Logik via Cashu als Phase 2.
- LNbits/Lightning-Setup-Hürde — Mitigation: NIP-07-Wallets (Alby) übernehmen alles.

---

## W6 — Polish + Landing

**Tasks.**

- W1–W5 auf einheitlichen Look bringen (gleiche Typo, Farbpalette, Header, Footer).
- README pro Prototyp (Stack, Live-Link, Code-Link, Demo-GIF).
- Demo-Video pro Prototyp (je 60 s, Loom).
- Ein Übersichts-`index.html` als Landing für alle fünf: Karten-Grid mit Screenshot + 1-Satz-Pitch + „Try it"-Button.
- Domain-Setup: <sec.bimbeam.at> oder <sovereign-aec.io> für die Landing.
- Pitch-Deck (10–12 Slides) für SE-Demo-Day, das die fünf HTML-Demos in Phase-1-/Phase-2-/Phase-3-Erzählung einbettet.

**Kein Bonus-Prototyp mehr** — ots-Bautagebuch ist hochgezogen, plebbim ist drin. W6 ist reine Konsolidierung. Falls ein W1–W5-Stück hakt, ist W6 das Puffer.

---

## Übersicht im Bild

```
Woche  Prototyp                Funktion                         Verzahnung
─────  ─────────────────────   ──────────────────────────────   ─────────────
W1     citadel-open-content    NIP-23-Aggregator                Hülle, Demo-Sektion
W2     bcf-quickform           BCF-Topic publish + feed         Datenquelle
W3     bcf-thread              Comments + Audit                 Vertieft W2
W4     ots-bautagebuch         OTS-Anker auf Timechain          eigenständig
W5     plebbim                 Zap-Bounty auf BCF-Topics        liest W2+W3
W6     polish + landing        Pitch-Ready                      Konsolidierung
```

**Verzahnungs-Pointe.** W2 + W3 + W5 ergeben zusammen einen vollständigen BCF-Workflow mit Anreiz-Schicht. W1 ist Community-Outpost. W4 ist die Beweis-Schicht — eigenständig und unabhängig vom Rest demobar.

---

## Globale Tech-Entscheidungen (ein-für-allemal)

| Aspekt | Entscheidung |
|---|---|
| Sprache | Vanilla JS + ES Modules |
| Nostr-Lib | `@nostr-dev-kit/ndk` von esm.sh |
| UI | Vanilla DOM + CSS, optional Lit-HTML wenn nötig |
| Charts | Chart.js (W5) von Cloudflare CDN |
| Markdown | marked.js (W1) |
| OTS | `javascript-opentimestamps` (W4) |
| Lightning | NIP-57 via NIP-07-Wallet (Alby, Mutiny), kein eigener LNbits-Server |
| Signing | NIP-07 default, nsec-Fallback mit Warnung |
| Storage | Blossom-URLs als Tag-Werte, kein eigener Server |
| Deploy | GitHub Pages oder Cloudflare Pages |
| Domain | <unterprojekt>.bimbeam.at oder example.gh.io/<projekt> |
| Lizenz | MIT |

---

## Open Questions

1. **Repo-Layout.** Ein Monorepo `sec-yolo-bim` mit Unterordnern, oder fünf separate Repos? Empfehlung: Monorepo, weniger CI-Overhead.
2. **Test-Tribe.** Welche NIP-29 group seeden wir für W2/W3/W5? Vorschlag: eine neue, ich kuratiere die ersten 10 npubs (du + 9 andere AEC-Leute).
3. **Bountys in plebbim.** Direkter Zap an Topic-Autor (Default, sicher) oder echte Escrow via Cashu (komplexer, fair für Resolver)?
4. **OTS-Calendar.** Public-Default (calendar.opentimestamps.org) oder eigene Calendar-Instanz? Public reicht für MVP.
5. **Bautagebuch-Kind.** Dedizierter `kind:30960` (mein Vorschlag) oder generischer `kind:1985`-Container mit `bau-tagebuch`-Tag?
6. **Landing-Domain.** Vorschlag: `sec.bimbeam.at` oder neue Domain wie `sovereign-aec.io`?

---

*6-Wochen-Realität: Phase 1 muss demobar sein. Standards-Drafts (BCF-NIP, OTS-Kind, etc.) fallen als Nebenprodukt aus dem Code. AdlerHort und ZapViz bleiben getrennte Schienen — der SE-Sprint baut auf ihnen nicht auf und konkurriert nicht mit ihnen. Lebendes Dokument.*
