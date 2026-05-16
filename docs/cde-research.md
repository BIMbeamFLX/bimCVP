# CDE-Markt-Research für Sovereign AEC

**Zweck.** Lage-Aufnahme des Common-Data-Environment-Marktes mit Fokus auf Provinz-Bozen-Kontext, italienische Regulatorik, große Plattform-Hersteller, kleine/Open-Source-Alternativen und UI-Pattern. Material für Positionierung, Pitch, UI-Design und Pilot-Strategie.

**Stand:** Mai 2026.

---

## 0. Executive Summary

- **Provinz Bozen ist mit einer öffentlichen Vergabe für eine BIM-Plattform unterwegs.** 13 promotorische Stellen (u. a. Consorzio Comuni, STA, IPES, Universität Bozen) bündeln den Bedarf. Ergebnis erwartet Sommer 2026, Betrieb ab 2027. Zielmodell: openBIM, einheitlich für die Provinz. Das ist genau das Zeitfenster, in dem Sovereign AEC sich positionieren muss — entweder als Bieter (vermutlich zu spät und zu klein) oder als ergänzende Open-Source-Schicht.
- **Italien hat die strengste BIM-Pflicht in der EU.** Seit 1. Januar 2025 ist BIM bei öffentlichen Bauaufträgen ab €2 Mio. Pflicht. Atto Organizzativo BIM ist von jeder Stazione Appaltante zu erstellen. Vier BIM-Rollen (Manager, Coordinator, Specialist, CDE Manager) definiert. ACDat = italienischer Begriff für CDE. UNI 11337 (12 Teile) ist die nationale Norm, ISO 19650 als Bezug.
- **CDE-Markt ist dichter als gedacht.** Die fünf Plattform-Hersteller dominieren, aber unter ihnen wächst ein offenstandards-affines Mittelfeld: Catenda Hub (Norwegen, openCDE-nativ), StreamBIM (Norwegen, baustellen-fokussiert), Dalux (Dänemark, 1,7 Mio. Accounts in Europa), Speckle (Open Source, schweizer-britisch), BIMdata.io (Frankreich, Open Source). In Italien dominiert ACCA usBIM, mit 8BIM und Blumatica als kleinere Mitbewerber.
- **UI-Konsens hat sich gebildet.** Drei-Pane-Layout (Nav links, 3D-Viewer mittig, Issue-/Doc-Panel rechts), Cards-Grid für Projekte, BCF-Workflow standardisiert, Mobile-First für Baustelle. Unsere UIs (admin/character/keys) sind grundsätzlich in dieser Richtung, brauchen aber den 3D-Viewer als Mittelpunkt sobald BIM-IFC im Spiel ist.
- **Sovereign-AEC-Lücke ist klar.** Alle untersuchten Plattformen sind entweder (a) proprietär mit Vendor-Lock, oder (b) Open-Source aber CDE-funktional dünn. Niemand kombiniert: signierte Identität + plattformneutrale Speicherung + openBIM-konforme Workflows + sovereigne Infrastruktur. Das ist die Lücke.

---

## 1. Provinz Bozen — der Pilot-Markt

### 1.1 Was läuft gerade

Die Provinz Bozen bereitet eine öffentliche Vergabe für eine zentrale BIM-Plattform vor. Treibende Köpfe: Generaldirektion, Abteilung Vermögen und IT, Casa Clima Agency. Förderer-Kreis 13 Organisationen breit:

- **Consorzio dei Comuni** (Konsortium der Gemeinden)
- **STA — Strutture Trasporto Alto Adige SpA** (Verkehrsinfrastruktur)
- **IPES — Istituto per l'Edilizia Sociale** (Wohnbau)
- **Libera Università di Bolzano** (Freie Universität Bozen)
- Plus weitere Provinz- und Gemeinde-Stellen

**Zeitplan:**
- Vergabe ausgeschrieben: läuft / bald
- Zuschlag erwartet: Sommer 2026
- Betrieb der neuen Plattform: ab 2027

**Erwartetes Einsparpotenzial:** bis 30 % bei den Bauphasen-Kosten, primär durch frühe Kollisions-Prüfung und Energie-Simulationen.

**Position der Provinz Bozen:** zweite italienische Provinz, die einen einheitlichen BIM-Standard für das gesamte Provinzgebiet einführt (erste war Mailand-Lombardei mit eigenen Initiativen). Strategie: openBIM, Interoperabilität, einheitliche Standards für alle PA-Stakeholder.

### 1.2 Ökosystem

- **NOI Techpark Südtirol** — Technologiepark mit drei Forschungsinstituten (Fraunhofer Italia, Eurac Research, Laimburg), vier Fakultäten der UniBZ, 90+ Unternehmen/Startups. Hosting-Kandidat für Pilot-Infrastruktur.
- **Eurac Research** — Forschungseinrichtung mit Schwerpunkt erneuerbare Energie, Klima, smart buildings. Partner im E2I@NOI-Projekt zu "Energetically Intelligent Buildings" mit BIM-Integration. €934k EFRE-gefördert.
- **Casa Clima Agency** — Energie-Zertifizierungsstelle der Provinz, schon BIM-fühlbar.
- **Camera di Commercio Bolzano (Handelskammer)** — eigene BIM-Informationsseite, koordiniert Digitalisierungs-Beratung.

**Implikation:** für den Pilot ist NOI Techpark oder Eurac der naheliegende Hosting-Partner, nicht Bimbeam selbst. Politisch klüger, weil neutral.

### 1.3 Strategische Lesart

Die Provinz wird voraussichtlich an einen großen oder mittleren Anbieter vergeben — Catenda, ACCA usBIM, oder Trimble Connect sind die wahrscheinlichsten Kandidaten. Sovereign AEC sollte nicht versuchen, in dieser Vergabe zu gewinnen. **Stattdessen:** sich als komplementäre Open-Source-Schicht positionieren, die auf der gewählten Plattform draufsitzen oder daneben laufen kann.

Das passt zu zwei Pfaden:
1. **Komplementär-Pilot** auf einem Teilprojekt (Raulassen) parallel zum Hauptvergabe-Lauf — zeigt, was zusätzlich möglich ist
2. **Spezial-Layer** für vertrauliche/sensible Workflows, die die zentrale Plattform aus Vergabe-rechtlichen Gründen nicht abdecken kann (Bid-Verschlüsselung, Lebenszyklus-Doku jenseits der Bauphase, lokal-redundante Backups)

---

## 2. Italienische Regulatorik (DM 312/2021, D.Lgs. 36/2023, UNI 11337)

### 2.1 Rechtsrahmen

**DM 560/2017** ("BIM-Dekret") — eingeführt unter Minister Delrio, definierte Stufenplan zur BIM-Pflicht in der öffentlichen Hand. Geändert durch **DM 312/2021** (Beschleunigung der Zeitleiste).

**D.Lgs. 36/2023** (neues Codice dei Contratti Pubblici) — Allgemeinverbindlich seit 1. Juli 2023. **Allegato I.9** behandelt explizit BIM-Pflicht und "pianificazione della gestione informativa". Ergänzt durch:

- **MIT-Linien-Guida 2026** (neu) — operative Anleitung für Stazioni Appaltanti
- **ANAC-Leitlinien** — Antikorruptions-Behörde, definiert Rollen-Profile und Vergabe-Prozeduren

### 2.2 Schwellenwerte (Stand 2026)

- **Ab 1.1.2025:** BIM-Pflicht für öffentliche Bauten ab €2 Mio. Neubau, €5,38 Mio. Kulturerbe-Eingriffe, €2 Mio. unvollendete Bauten.
- Erwartet weitere Absenkung der Schwellen 2027/2028.

### 2.3 UNI 11337 — italienische BIM-Norm

Zwölf Teile, die ISO 19650 ergänzen und italianisieren:

| Teil | Inhalt |
|---|---|
| UNI 11337-1 | Allgemeines Modell, Lebenszyklus |
| UNI 11337-2 | Begriffe und Definitionen |
| UNI 11337-3 | Modelle, Daten, Informationen |
| UNI 11337-4 | LOD-Stufen (Level of Development) |
| UNI 11337-5 | Informations-Management-Prozess |
| UNI 11337-6 | Capitolato Informativo (= EIR) |
| UNI 11337-7 | Berufsprofile: BIM Manager, BIM Coordinator, BIM Specialist, CDE Manager |
| UNI 11337-8 | Klassifikation |
| UNI 11337-9 | Betriebsphase + BIM Dossier (= Building Logbook) |
| UNI 11337-10 | Sicherheit |
| UNI 11337-12 | Infrastrukturbauten |

**Relevanz für Sovereign AEC:**
- UNI 11337-6 (Capitolato Informativo) entspricht IDS + LOIN. Unsere `kind:30810`/`kind:30811` müssen mit UNI-11337-6-Templates lesen/schreiben können.
- UNI 11337-7 (Berufsprofile) liefert die Rollen-Liste komplementär zu IFC `IfcActorRoleEnum`. Italienische Variante in unseren Rolle-Pickern anbieten.
- UNI 11337-9 (BIM Dossier) ist das italienische Gebäudebuch. Unsere Gebäudebuch-Generator muss die UNI-Struktur unterstützen.

### 2.4 ACDat — Italienische CDE-Definition

Italienischer Begriff: **Ambiente di Condivisione Dati** (ACDat). Definition aus UNI 11337-5: „Umgebung zur organisierten Sammlung und Teilung von Daten zu digitalen Modellen und Ausarbeitungen, bezogen auf ein einzelnes Werk und einen einzelnen Werkkomplex."

Direkt von BS 1192:2007 abgeleitet (UK-Vorläufer von ISO 19650). Funktional identisch mit CDE, terminologisch Italien-spezifisch.

### 2.5 Atto Organizzativo BIM (AOB) — Pflichtdokument der PA

Jede Stazione Appaltante muss ein **Atto Organizzativo BIM** verabschieden, bevor sie BIM-Aufträge ausschreibt. Inhalte:

- Organisationsstruktur, Rollen, Verantwortlichkeiten
- Operative und normative Standards
- Informationsflüsse, Speicherung, Datenaustausch
- Personalfortbildungs-Strategie
- Definition CDE-Manager / BIM Manager / BIM Coordinator / BIM Specialist
- Standards (UNI 11337, ISO 19650, ggf. lokale Ergänzungen)
- Qualitätskontroll-System
- Technologie-Infrastruktur-Anforderungen
- Implementierungs-Cronoprogramm
- LCA / Nachhaltigkeitsmanagement

**Geschäftsmöglichkeit:** Sovereign-AEC-Suite könnte Open-Source-Templates für AOB anbieten — Markdown-Vorlage mit allen Pflichtsektionen, von beliebiger PA übernehmbar, anpassbar. Niedrige Hürde, hoher Nutzen für SMB-Kommunen.

### 2.6 Berufliche Rollen-Definition

Aus UNI 11337-7 und ANAC-Linien-Guida verbindlich:

- **BIM Manager (Stazione Appaltante)** — strategisch, Governance, organisationsweit
- **BIM Coordinator** — projektbezogen, koordiniert Disziplinen
- **BIM Specialist** — operativ, modelliert und pflegt
- **CDE Manager** — Verantwortlich für die ACDat-Plattform, Zugangs-, Versionen- und Datenmanagement

**Anschluss-Punkt:** unsere Rollen-Liste (IfcActorRoleEnum) braucht eine UNI-11337-7-Erweiterung mit den vier italienischen BIM-Rollen. Das ist eine Stunde Arbeit am character.html und admin.html.

---

## 3. Markt-Übersicht große Plattformen (für UI-Pattern-Inspiration)

### 3.1 Autodesk Construction Cloud (ACC) / BIM 360

**Position:** Marktführer, Hochbau-stark, US-Headquarter.
**Stack-Komponenten:** Docs, Build, Cost, Insight, Takeoff, Workshop XR.
**UI-Pattern:** komplex, sehr feature-reich, anpassbare Workflows. Reviews loben Funktionsumfang, kritisieren Komplexität für Einsteiger ("interface too complex, navigation confusing").
**Integration:** tiefste Revit/Civil3D/Navisworks-Integration.
**Weakness:** Subscription-getrieben, hohe Total-Cost-of-Ownership, Daten-Lock-in.

### 3.2 Bentley ProjectWise

**Position:** Infrastruktur-Schwerpunkt, ältere Userbase.
**Stack-Komponenten:** ProjectWise 365 (Cloud), Connection Edition (Desktop).
**UI-Pattern:** klassisch, Datei-Server-orientiert.
**Stärke:** Versionierung, große Ingenieurbüros, lange Bahn/Verkehr-Geschichte.
**Weakness:** UI eher 2010er-Stil, langsame Web-Migration.

### 3.3 Trimble Connect

**Position:** Stark in Stahlbau, Vermessung, Land Surveying. Cross-Plattform-Modell-Aggregation.
**UI-Pattern:** intuitiv, oft als zugänglichste der drei großen gelobt.
**Stärke:** Tekla-Integration, leichte Lernkurve.
**Weakness:** weniger umfassend als ACC bei Doc-Management.

### 3.4 Nemetschek-Gruppe (Bluebeam, Solibri, ArchiCAD)

**Position:** Deutsche Mutter, europäischer Bezug.
**Solibri Anywhere:** kostenlose Browser-Version für IFC-Viewer + BCF.
**Bluebeam:** 2D-PDF-Markup, sehr verbreitet bei US-Generalunternehmern.
**ArchiCAD BIMcloud:** kollaborative Modellbearbeitung, eher Authoring-Tool.

### 3.5 Hexagon (Leica, Smart3D)

**Position:** Vermessung, Punktwolken, Anlagenbau.
**Weniger relevant für klassischen Hochbau-CDE.**

---

## 4. Markt-Übersicht mittelgroße / spezialisierte Plattformen

### 4.1 Dalux (Dänemark)

**Position:** 7 800 Projekte in UK, 1,7 Mio. Accounts in Europa, 55 Büros in 28 Ländern. **Europäischer Marktführer im BIM-CDE-Segment.**
**Module:**
- Dalux Box (CDE mit Shared/Published, ISO 19650-konform)
- Dalux BIM Viewer (schnellster BIM-Viewer laut Architosh)
- Dalux Field (Baustelle, mobile)
- Dalux SiteWalk (helmet-mounted 360°-Kamera für automatische Baustellen-Dokumentation)
**UI-Pattern:** „Hygge"-Redesign 2024 — sauber, freundlich, mobile-first.
**Sprache:** mehrsprachig (DE, IT, EN u. a.).
**Erlöse:** in Italien aktiv, in Südtirol unbekannt.

### 4.2 Catenda Hub (Norwegen — vormals Bimsync)

**Position:** Eindeutig openCDE-positioniert. „The BIM-based Common Data Environment that's open, flexible and easy to use."
**Stärken:**
- Unlimited Users auf jedem Projekt (kein Sitz-Modell)
- Native IFC-Unterstützung
- BCF-Tracking eingebaut
- Open API für Integrationen
- ISO-19650-Compliance built-in
- Mehrsprachig (EN, DE, FR, JP, NL, NO)
**Integrationen:** Revit, ArchiCAD, DDS-CAD, Navisworks, Solibri, Vectorworks, Simplebim, MS Teams, SharePoint, Power BI, Slack, Dropbox, PlanRadar — sehr breit.
**Preismodell:** Pro Projekt, variabel, Demo-buchbar.
**UI-Pattern:** sehr clean, vier Hauptbereiche (Coordinate Design, Manage Information, Work with Everyone, Integrate to Everything).
**Bewertung für Sovereign AEC:** das ist der **nächste Verwandte** unserer Philosophie. Auch openBIM-zentriert, auch standards-treu. Aber Catenda ist proprietär und SaaS. **Wir nehmen uns das UI-Pattern und die Standards-Story als Vorbild.**

### 4.3 StreamBIM (Rendra AS, Norwegen)

**Position:** Baustellen-fokussiert, "made for boots on the ground".
**Userbase:** Skanska, NCC und andere skandinavische Großfirmen.
**Cases:** Ensjø Torg Oslo (630 Wohnungen, 8 Phasen), E136 Breivika-Lerstad (Hauptzufahrtsstraße Ålesund).
**UI-Pattern:** mobile-first, Tablet als Primärgerät, 2D-3D-Toggle.
**Inspiration:** der „IFC-Viewer auf Baustelle"-Aspekt ist genau das, was Sovereign AEC später für Bauleiter-UX braucht.

### 4.4 BIMcollab Cloud (Niederlande, Nemetschek-Tochter)

**Position:** **Issue-Management spezialisiert, kein vollständiger CDE.**
**Stärke:** beste BCF-Workflow-UI auf dem Markt, Best-of-Breed für reine Koordination.
**Schwäche:** braucht externen CDE für die Modelle.
**UI-Pattern:** Topic-zentrisch, Klick auf Issue zoomt in 3D zur Stelle. Filter-/Status-/Assignee-Workflow durchdacht.
**Bewertung:** **das beste BCF-UI auf dem Markt** — direkter Vergleichspunkt für unser BCF-Quickform/Thread-Prototyp.

### 4.5 Revizto

**Position:** Real-time BIM-Koordination + Clash Detection + Issue Tracking. **Nicht** als CDE positioniert.
**UI-Innovation:** 2D-Pläne in 3D-Modell-View integriert. AR-Overlays. Custom Issue Statuses.
**Integration:** ACC, Procore, Box, SharePoint via CDE-Connector. Revit, Navisworks Plugins.

### 4.6 Plannerly

**Position:** BIM Execution Plan (BEP) -fokussiert. Templates für PAS 1192 / ISO 19650 / AIA / BIM Forum.
**Stärke:** AOB-/EIR-Erstellung sehr direkt. Embed-Inhalte aus draw.io, YouTube, Typeform, Google Slides, Matterport.
**Modell-Support:** 80+ Formate inkl. IFC.
**Bewertung:** **Inspiration für unseren Bedarfsplanungs-Workflow**, vor allem die Drag-and-Drop-Template-Logik. Wir würden das Open-Source mit UNI-11337-Templates nachbauen.

### 4.7 Newforma

**Position:** AEC Project Information Management. Email + Files + Conversations zusammen.
**Weniger BIM-zentrisch, mehr generelles AEC-Doc-Management.**

---

## 5. Italienische Plattformen

### 5.1 ACCA usBIM.platform — Marktführer Italien

**Position:** openBIM-Plattform, buildingSMART-zertifiziert, ACCA software (Bagnoli Irpino, Avellino) ist seit Jahrzehnten der dominante italienische Bausoftware-Hersteller.
**Modulares System:**
- usBIM.browser (BIM-Viewer)
- usBIM.pointcloud (Punktwolken)
- usBIM.federation (Modell-Federation)
- usBIM.chat (Kommunikation)
- usBIM.meet (Videokonferenz)
- usBIM.gis (GIS-Integration)
- usBIM.appaltodigitale (öffentliche Vergabe-Spezialvariante)
- usBIM.bridge (BIM + GIS + BMS für Infrastrukturmonitoring)
**Pro PA:** usBIM.appaltodigitale ist explizit für Stazioni Appaltanti, unterstützt OGI (Obiettivi Generali Informativi) und PGI (Piano per la Gestione Informativa).
**Sprache:** primär Italienisch, English.
**Bewertung:** **ist der wahrscheinlichste Bolzano-Vergabe-Gewinner.** Wenn die Provinz an einen italienischen Anbieter geht, ist ACCA naheliegend. Sovereign AEC muss damit koexistieren können, nicht konkurrieren.

### 5.2 8BIM Platform (888SP)

**Position:** ACDat-konform, italienisch, ausgelegt auf Nuovo Codice Appalti.
**Funktionen:** BIM-Modelle öffnen, BCF in openBIM-Standard erzeugen, Aktivitäten/Fristen/Verantwortlichkeiten.
**Größe:** kleiner als ACCA, aber italienisch-spezialisiert.

### 5.3 Blumatica BIM Platform

**Position:** Modulares BIM-Toolset.
**Module:** BIM Federation, IDS Editor, IDS Validator, bSDD, BIM Compare, BIM.4D, BIM.5D, Digital Twin.
**Stärke:** explizit IDS- und bSDD-Integration. Klares openBIM-Bekenntnis.

### 5.4 BIM Leader (Cadline Software)

**Position:** italienische Kollaborations-Plattform.
**Weniger Information öffentlich verfügbar, kleinere Reichweite.**

---

## 6. Open-Source-Alternativen

### 6.1 Speckle Systems

**Position:** Open Source, real-time 3D Data, "the platform for 3D data".
**Stärken:**
- 3D-Viewer mit Sharing-Link / Embed
- Versionshistorie
- Real-time follow-mode
- Modell-Federation
- 3D-Comments pinned to Objects
- 2D-Markup auf 3D-Views
- Dev Mode (JSON-View jedes Objekts)
- White-Label-fähig
- Customizable UI/Branding
**Stack:** Server (.NET/Node), Web-Client, Connectors für Revit/Rhino/Grasshopper/Blender etc.
**Bewertung:** **das stärkste Open-Source-3D-Daten-Tool**, aber kein vollständiger CDE — kein Issue-Tracker, kein Document-Manager im Sinne von ISO 19650. Gut als Viewer + Federation-Layer, ergänzend zu unserem Stack.

### 6.2 BIMserver.org (opensourceBIM)

**Position:** der Pionier des Open-Source-IFC-Servers. Java + Eclipse Modelling Framework. Seit 2009 aktiv.
**Stärken:** model-driven (nicht file-server), IFC-Datenbank, Versioning, Merging.
**Schwächen:** UI veraltet, Stack heavy (Java + EMF), Adoption fast nur akademisch.
**Bewertung:** historisch interessant, für Sovereign AEC nicht direkt verwendbar — aber Konzept-Vorbild.

### 6.3 BIMdata.io (Frankreich)

**Position:** Open-Source-Plattform, white-label-fähig.
**Viewer-Support:** IFC, DWG, PDF, DXF, Punktwolken, JPG.
**Funktionen:** Comments und Annotationen auf Modellen, Mess-Tools, BCF-Management, klar dokumentierte API.
**Bewertung:** **starker Kandidat zum Anbinden statt selbst zu bauen.** Wir könnten den BIMdata-Viewer in unsere UI integrieren statt web-ifc + Three.js selbst zu verkabeln. Wirtschaftlich attraktiv: white-label, Open Source, sieht professionell aus.

### 6.4 IFCWebServer.org

**Position:** kleines openBIM-Tool für IFC-Visualisierung im Web. Hosted Service.
**Weniger Umfang als BIMdata.**

### 6.5 OpenProject BIM-Modul

**Position:** Open-Source-Projektmanagement-Tool (deutsch), seit einigen Jahren mit BIM-Modul.
**Stärken:** ISO-19650-State (WIP/Shared/Published/Archive), BCF-Import/Export, IFC-Viewer via xeokit.
**Bewertung:** für the maintainer's Bürokratie-Toaster-Zielgruppe **interessant als Referenz-UI**, weil es deutsche Sprache, klassische Project-Management-UX und BIM-Integration kombiniert.

### 6.6 xeokit (Library, nicht Plattform)

**Position:** Open-Source-JS-IFC-Viewer (UK, AGPL/Commercial). Schnell, präzise, double-precision coordinates.
**Beziehung zu unserer Stack:** xeokit ist der Konkurrent zu web-ifc. Reifer, aber AGPL-lizenzbedingt vorsichtig zu verwenden bei kommerziellen Erweiterungen.

---

## 7. UI-Pattern-Synthese

Aus allen untersuchten Tools lassen sich folgende konvergente Pattern destillieren — das ist, was Bürokratie-Toaster heute als „normal" erwartet:

### 7.1 Globale Navigation

- **Top-Nav** mit Projekt-Wechsler, Profil-Avatar, Benachrichtigungen, Hilfe.
- **Seitenleiste links** mit Modul-Auswahl: Models, Issues, Documents, Team, Settings.
- **Breadcrumbs** für Tiefen-Navigation.

### 7.2 Projekt-Landing-Page

- **Kachel-Übersicht** statistischer Werte: Modelle, offene Issues, anstehende Genehmigungen, neue Dokumente.
- **Aktivitäts-Feed** rechts oder als zentrale Spalte: wer hat was wann gemacht.
- **Schnellzugriff-Kacheln** für die häufigsten Aktionen.

### 7.3 3D-Viewer-Pane

- **3D-View nimmt 50–70 % der Bildschirmfläche** ein, links Komponenten-Baum (Spatial Structure), rechts Properties-Panel.
- **Toolbar oben**: Pan/Orbit/Zoom, Schnittebene, Hide/Isolate, Sichtbarkeits-Layer.
- **Bottom-Bar**: Modell-Federation-Switch, Layer-Filter.
- **Klick auf Element** → Properties + Optionen „neue Issue hier", „Comment hier".

### 7.4 BCF Issue-Tracker

- **Liste links**: filterbar nach Status, Priority, Assignee, Type, Tag.
- **Detail-Pane rechts**: Topic-Felder, Comment-Thread, Snapshot, Verknüpfte Elemente, Audit-Trail (oft kollabiert).
- **Action-Button** zum Status-Wechsel prominent.
- **Stat-Counter** oben: Open / In Progress / Resolved / Closed mit Donut.

### 7.5 Document-Manager

- **Hierarchischer Folder-Tree** links.
- **File-Liste** mit Sortier-/Filter-Optionen.
- **Versionierung** als „Version 1.0, 1.1, 1.2"-Dropdown pro Datei.
- **ISO-19650-State** als Badge (WIP / Shared / Published / Archive).
- **Workflow-Buttons** für State-Übergang (z. B. „Shared → Published" mit Approval-Multi-Sig).

### 7.6 Member-Admin

- **Mitglieder-Tabelle**: Avatar, Name, Rolle, Company, letzter Login, Aktionen.
- **Rollen-Dropdown** mit vordefinierten Werten (IFC ActorRoleEnum / UNI-11337-7).
- **Invite-Form** primär per Email (klassisch). Sovereign-AEC: per npub.

### 7.7 Mobile / Field

- **Bottom-Tab-Bar** für die wichtigsten Aktionen.
- **3D-View mit Touch-Gesten** für Zoom/Pan.
- **„Photo-Capture mit Annotation"-Workflow** zentral.
- **Offline-Sync-Indikator** prominent (wegen Baustellen-Realität).

### 7.8 Was wir an unseren UIs konkret tunen müssen

Vergleich unserer aktuellen `admin.html` und `character.html` mit dem Industriestandard:

| Aspekt | Status bei uns | Industriestandard | Action |
|---|---|---|---|
| 3D-Viewer-Integration | nicht vorhanden | zentral | nach Backend-Setup direkt integrieren (BIMdata.io oder web-ifc) |
| Projekt-Landing mit Stats | dünn | umfassend | nach Backend-Setup ergänzen |
| BCF-Topic-Liste-View | nicht gebaut | zentral | für Phase 2 vorgesehen |
| Mitglieder-Tabelle | gebaut | Standard | OK |
| Rollen nach IFC + UNI 11337 | nur IFC | beides | UNI-Rollen ergänzen (BIM Manager PA etc.) |
| Mobile-tauglich | responsive | nativer Workflow | Phase 3 |
| Bilingual DE/IT | nein | für Bolzano Pflicht | beim Pilot-Start ergänzen |
| ISO-19650-State-Badges | konzeptionell vorgesehen | Standard | im Document-Modul nachbauen |
| Workflow-Approval-Buttons | nicht gebaut | Standard | für Bauherrenstack-Phase |

---

## 8. Differenzierungs-Linie für Sovereign AEC

Die zentrale Frage: warum sollte jemand uns wählen, wenn Catenda Hub schon openBIM-nativ ist und ACCA usBIM schon italienisch + PA-spezialisiert?

### 8.1 Was uns von Catenda unterscheidet

- **Catenda ist SaaS, wir sind selbst-hostbar.** Für DSGVO-strenge öffentliche Hand relevant.
- **Catenda hat keine kryptographische Signatur-Schicht.** Bei uns ist jede Aktion signiert.
- **Catenda nutzt klassisches User-Account-Modell.** Bei uns ist npub-Identität, die Nutzer kein Passwort verlieren können.
- **Catenda lebt von Subscription.** Wir sind Open Source MIT, keine wiederkehrenden Kosten.

### 8.2 Was uns von ACCA usBIM unterscheidet

- Ähnliche Punkte wie Catenda, plus:
- **ACCA ist sehr proprietäre Software-Suite, alles aus einem Haus.** Wir verkabeln Open-Source-Komponenten (NDK, Blossom, LNbits, web-ifc/BIMdata).
- **ACCA ist primär Italienisch.** Wir sind bilingual DE/IT von Anfang an — Südtiroler Eigenheit.
- **ACCA verwaltet Schlüssel der Plattform.** Wir verwalten gar nichts — Schlüssel beim Nutzer.

### 8.3 Was uns von Speckle unterscheidet

- **Speckle ist 3D-Datenplattform, kein vollständiger CDE.** Kein Issue-Tracker, kein Document-Manager im ISO-19650-Sinne.
- **Speckle ist ohne BIM-Workflow-Logik.** Wir bauen BCF-Topics, IDS-Anforderungen, Gebäudebuch — Workflow-orientiert.
- **Speckle könnte als unser 3D-Viewer-Backend dienen.** Statt zu konkurrieren: integrieren.

### 8.4 Unique Value Proposition (zum Vorzeigen)

> Sovereign AEC ist die einzige openBIM-Plattform, bei der jede Aktion kryptographisch signiert, jede Datei selbst-gehostet, jede Mitgliedschaft signaturen-nachweisbar und der ganze Stack vendor-frei ist. Wir verkabeln reife Open-Source-Komponenten zu einem ISO-19650-konformen Workflow, der ohne Lizenzkosten in jedem Planungsbüro und jeder kleinen Kommune läuft.

### 8.5 Nicht-Ziele

- Wir konkurrieren nicht mit Autodesk/Bentley auf Feature-Tiefe — sie werden 10 Jahre Vorsprung in 3D-Authoring haben.
- Wir konkurrieren nicht mit ACCA usBIM um den Bolzano-Vergabe-Zuschlag — sie sind politisch und logistisch näher.
- Wir bieten kein Cloud-Hosting-Premium-Modell — das macht zu viele Versprechen, die wir im Pilot nicht halten können.

---

## 9. Strategische Implikationen für den Pilot

### 9.1 Pitch-Anpassung

In Italien / Provinz Bozen muss die Sovereign-AEC-Botschaft in italienischen Standards-Bezug eingebettet sein:

- Nicht „BIM Collaboration Format" allein — „BCF, conforme alla UNI 11337-5"
- Nicht „building information modeling" — „BIM secondo D.Lgs. 36/2023"
- Nicht „Anforderungen" — „Capitolato Informativo (UNI 11337-6) e EIR (ISO 19650)"
- Nicht „lifecycle documentation" — „BIM Dossier (UNI 11337-9) e Digital Building Logbook (EPBD 2024/1275)"
- Nicht „BIM Manager" — „BIM Manager PA, BIM Coordinator PA, CDE Manager"

### 9.2 Raulassen-Pilot konkret

- **Sponsor finden**: NOI Techpark als neutraler Host, Eurac als wissenschaftlicher Sparring-Partner. Diese beiden sind die Türöffner — nicht direkt die Provinzverwaltung.
- **Bilingual von Tag 1**: DE und IT. Englisch optional dritte Sprache.
- **AOB-Template Open Source mitliefern**: das ist der einfachste Türöffner für Stazione-Appaltante-Stakeholder.
- **Komplementär positionieren**: explizit „neben" der Provinz-Vergabe-Plattform, nicht „statt".

### 9.3 BIMdata.io als Viewer einbauen

Statt selbst web-ifc + Three.js zu verkabeln, **BIMdata.io white-label** für den Viewer-Layer nutzen. Vorteile:

- Open Source, kein Lizenz-Konflikt
- Reife, schnelle, multi-format
- BCF-Integration eingebaut
- Custom-Branding möglich (white-label)
- Eine Entwickler-Wochen-Arbeit gespart

### 9.4 Plannerly-Inspiration für Bedarfsplanungs-Modul

Wenn Phase 2 (Bauherrenstack) kommt, das Plannerly-UX-Modell als Vorbild nehmen — Drag-and-Drop-Templates für AOB / Capitolato Informativo / EIR. Mit UNI-11337-konformen Templates statt PAS-1192.

### 9.5 Position als Italien-spezialisierter offener Stack

Der Pitch wird nicht „wir sind besser als ACCA" sondern „wir sind der offene Standard-Stack für italienische PA, der ACCA nicht ersetzt, sondern ergänzt durch Souveränität und Open-Source-Lizenz".

---

## 10. UI-Konkurrenz-Tabelle (Quick Reference)

| Plattform | UI-Stärke | UI-Schwäche | openBIM-Affinität | OSS | Italien-Ready |
|---|---|---|---|---|---|
| Autodesk ACC | feature-reich | komplex | mittel | nein | mittelmäßig |
| Trimble Connect | intuitiv | weniger umfassend | mittel | nein | OK |
| Bentley ProjectWise | enterprise-tauglich | UI veraltet | niedrig | nein | OK |
| Dalux Box | modern, mobile-first | Cloud-only | hoch | nein | mehrsprachig |
| Catenda Hub | clean, fokussiert | nur Cloud | sehr hoch (openCDE-nativ) | nein | mehrsprachig DE |
| BIMcollab Cloud | bestes BCF-UI | nicht voll-CDE | hoch | nein | OK |
| StreamBIM | mobile/tablet-fokussiert | weniger Doc-Management | hoch | nein | OK |
| Revizto | 2D-3D-Mix, AR | nicht voll-CDE | mittel | nein | mittelmäßig |
| ACCA usBIM | italianisch | überladen | hoch | nein | sehr hoch |
| 8BIM Platform | italianisch, PA-fokussiert | weniger Reichweite | hoch | nein | sehr hoch |
| Blumatica BIM | IDS + bSDD integriert | kleinere Marke | hoch | nein | hoch |
| Speckle | 3D-Datenplattform-Klassiker | kein CDE-Workflow | mittel | ja | sprache neutral |
| BIMdata.io | multi-format, white-label | weniger Workflow | hoch | ja | sprache neutral |
| BIMserver.org | open-source-Pionier | UI veraltet | hoch | ja | sprache neutral |
| OpenProject BIM | klassisches PM + BIM | weniger 3D-stark | mittel | ja | DE/IT |
| **Sovereign AEC** | signiert, vendor-frei, MIT | UI im Aufbau | sehr hoch | ja | bilingual von Start |

---

## 11. Aktions-Liste

Aus dieser Research konkret abzuleitende nächste Schritte für den Pilot:

1. **UNI-11337-7-Rollen in admin.html und character.html ergänzen**: BIM Manager PA, BIM Coordinator PA, BIM Specialist PA, CDE Manager als zusätzliche Optionen neben IfcActorRoleEnum.
2. **Atto-Organizzativo-BIM-Template** als Markdown-Datei im Repo bereitstellen — Open-Source-Gemeingut für Stazioni Appaltanti, niedrige Hürde, hoher Strategie-Nutzen.
3. **Italienisch als Zweitsprache** in alle Landing/Wissensseiten einbauen — bilingual DE/IT.
4. **BIMdata.io evaluieren** als Viewer-Backend statt eigenem web-ifc-Stack — kann eine Woche Entwicklung sparen.
5. **Speckle-Connector** prüfen — wäre eine elegante Brücke für reife 3D-Datenflüsse.
6. **Pitch-Glossar** anpassen: ACDat, Capitolato Informativo, OGI/PGI, BIM Dossier statt nur englischer Termini.
7. **NOI Techpark + Eurac kontaktieren** für Pilot-Hosting/Sparring-Gespräch.
8. **AOB-konformes Mini-Anschreiben** für Stazioni Appaltanti vorbereiten („wir helfen euch den Atto Organizzativo BIM kostenlos zu erstellen, im Gegenzug pilotieren wir bei einem eurer kleineren Projekte").
9. **Catenda-UI-Pattern** als visuelles Vorbild für unsere admin/project-Views — clean, fokussiert, vier Hauptbereiche.
10. **BIMcollab-BCF-UX** als Vorbild für unsere BCF-Quickform/Thread-Prototypen — Topic-zentrische Navigation, 3D-Sprung-zur-Stelle.

---

## 12. Quellen

- Provinz Bozen, Pressemitteilungen zur BIM-Plattform-Vergabe: [Agenzia Giornalistica Opinione](https://www.agenziagiornalisticaopinione.it/opinionmix/pab-provincia-autonoma-di-bolzano-il-building-information-modeling-trasforma-la-progettazione-edilizia-con-risparmi-fino-al-30/), [PAB-Standard-Mitteilung](https://www.agenziagiornalisticaopinione.it/opinionmix/pab-provincia-autonoma-di-bolzano-la-piattaforma-bim-definisce-i-nuovi-standard-per-la-gestione-del-patrimonio-edilizio/)
- Italienische BIM-Pflicht / Codice Appalti: [BibLus-ACCA](https://biblus.acca.it/nuovo-codice-appalti-il-bim-e-obbligatorio/), [Edilportale 2026](https://www.edilportale.com/news/2026/02/appalti/bim-negli-appalti-pubblici-linee-guida-2026_109260_51.html), [Orbyta](https://orbyta.it/en/insights/bim-2025-requirement-everything-you-need-to-know-to-be-compliant-with-the-regulations/)
- Atto Organizzativo BIM: [id BIM](https://id-bim.it/latto-organizzativo-bim-per-la-pubblica-amministrazione-pilastro-della-digitalizzazione-dei-processi-edilizi-pubblici/), [Ingenio](https://www.ingenio-web.it/articoli/l-atto-organizzativo-adempimento-preliminare-per-l-amministrazione-bim-ready/), [Skeinbim](https://skeinbim.com/bim-e-pa-che-cos-e-atto-organizzativo-bim/)
- UNI 11337 und ACDat: [BibLus-ACCA](https://biblus.acca.it/acdat-ambiente-di-condivisione-dati/), [UNI](https://www.uni.com/conoscere-e-applicare-il-bim-con-la-normazione-la-nuova-brochure-di-uni/), [Würth News](https://news.wuerth.it/metodologia-bim-norma-uni-11337/)
- Plattform-Reviews:
  - Catenda Hub: [Catenda.com](https://catenda.com/bim-solutions-open-standards/catenda-hub-common-data-environment/), [Capterra](https://www.capterra.com/p/197521/Bimsync/)
  - Dalux: [Dalux Box](https://www.dalux.com/products/dalux-box/), [Architosh ToolTalk](https://architosh.com/2025/01/tooltalk-looking-at-dalux-the-worlds-fastest-bim-model-viewer/)
  - StreamBIM: [streambim.com](https://streambim.com/)
  - Revizto: [Architosh 2025](https://architosh.com/2025/08/inside-revizto-global-dominance-with-open-bim-coordination/), [Revizto.com](https://revizto.com/)
  - Plannerly: [plannerly.com](https://plannerly.com/), [Autodesk App Store](https://apps.autodesk.com/BIM360/en/Detail/Index?id=3718265709127811334)
- Italienische Plattformen:
  - usBIM (ACCA): [ACCA Bagno](https://www.acca.it/bim-management-system), [BibLus](https://biblus.acca.it/notizie/dal-bim-alla-gestione-informativa-digitale-negli-appalti-pubblici-corso-online-sulle-nuove-linee-guida-2026/)
  - 8BIM: [888sp.com](https://www.888sp.com/it/8bim-platform/)
  - Blumatica: [Blumatica BIM](https://www.blumatica.it/piattaforma-bim-uni-11337-e-uni-en-iso-19650/)
  - usBIM.appaltodigitale: [Ingenio](https://www.ingenio-web.it/articoli/gestione-digitale-degli-appalti-pubblici-bim-con-acdat-e-usbim-appaltodigitale/)
- Open Source:
  - Speckle: [speckle.systems](https://speckle.systems/), [GitHub](https://github.com/specklesystems), [Architizer](https://tech.architizer.com/listing/speckle.html)
  - BIMdata.io: [BIMdata Platform](https://bimdata.io/en/bimdata-platform/), [Open-Source-Ankündigung](https://medium.com/@bimdata/bimdata-io-platform-now-available-in-open-source-3af7b354d814)
  - BIMserver: [GitHub opensourceBIM](https://github.com/opensourceBIM/BIMserver), [SourceForge](https://sourceforge.net/projects/bimserver.mirror/)
  - xeokit: [xeokit/xeokit-bim-viewer](https://github.com/xeokit/xeokit-bim-viewer)
- NOI Techpark / Eurac: [NOI Techpark](https://noi.bz.it/en), [Eurac E2I@NOI](https://www.eurac.edu/en/institutes-centers/institute-for-renewable-energy/projects/e2inoi)
- Handelskammer Bolzano BIM-Seite: [BIM bei der HK Bozen](https://www.handelskammer.bz.it/it/servizi/digitalizzazione/conoscenze-pratiche/building-information-modeling-bim)
- Markt-Report Europa: [MarketsAndMarkets European BIM 2030](https://www.marketsandmarkets.com/Market-Reports/europe-building-information-modeling-market-80977477.html)

---

*Stand: Mai 2026. Lebendes Dokument — bei Vergabe-Updates (Sommer 2026) und Bolzano-Pilot-Fortschritt aktualisieren.*
