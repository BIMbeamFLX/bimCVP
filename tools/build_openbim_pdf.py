# -*- coding: utf-8 -*-
"""
Build the openBIM × Nostr NIP-Fitness Research PDF.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_JUSTIFY, TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle,
    KeepTogether, ListFlowable, ListItem, HRFlowable
)
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

OUTPUT = "/sessions/sweet-lucid-clarke/mnt/outputs/openbim-nostr-nip-fitness.pdf"

# ---------- Styles ----------
ss = getSampleStyleSheet()

INK = colors.HexColor("#1a1a1a")
MUTED = colors.HexColor("#4a4a4a")
ACCENT = colors.HexColor("#0b5394")
RULE = colors.HexColor("#cccccc")

HIGH = colors.HexColor("#2e7d32")
MID = colors.HexColor("#f9a825")
LOW = colors.HexColor("#c62828")
NA = colors.HexColor("#6b6b6b")

base = dict(fontName="Helvetica", fontSize=10.5, leading=15, textColor=INK,
            alignment=TA_JUSTIFY, spaceAfter=6)
body = ParagraphStyle("body", parent=ss["BodyText"], **base)
body_left = ParagraphStyle("body_left", parent=body, alignment=TA_LEFT)
small = ParagraphStyle("small", parent=body, fontSize=9, leading=12, spaceAfter=4)
muted = ParagraphStyle("muted", parent=body, textColor=MUTED, fontSize=9, leading=12)

h1 = ParagraphStyle("h1", parent=ss["Heading1"], fontName="Helvetica-Bold",
                    fontSize=18, leading=22, textColor=ACCENT,
                    spaceBefore=14, spaceAfter=10)
h2 = ParagraphStyle("h2", parent=ss["Heading2"], fontName="Helvetica-Bold",
                    fontSize=14, leading=18, textColor=INK,
                    spaceBefore=12, spaceAfter=8)
h3 = ParagraphStyle("h3", parent=ss["Heading3"], fontName="Helvetica-Bold",
                    fontSize=11.5, leading=15, textColor=INK,
                    spaceBefore=8, spaceAfter=4)

title = ParagraphStyle("title", parent=ss["Title"], fontName="Helvetica-Bold",
                       fontSize=28, leading=34, textColor=ACCENT, alignment=TA_LEFT,
                       spaceAfter=4)
subtitle = ParagraphStyle("subtitle", parent=ss["Normal"], fontName="Helvetica",
                          fontSize=14, leading=18, textColor=MUTED, alignment=TA_LEFT,
                          spaceAfter=12)
meta = ParagraphStyle("meta", parent=ss["Normal"], fontName="Helvetica",
                      fontSize=9, leading=12, textColor=MUTED, alignment=TA_LEFT)

code = ParagraphStyle("code", parent=ss["Code"], fontName="Courier",
                      fontSize=8.5, leading=11, leftIndent=12, rightIndent=12,
                      backColor=colors.HexColor("#f4f4f4"), textColor=INK,
                      borderPadding=6, spaceBefore=6, spaceAfter=6)

bullet = ParagraphStyle("bullet", parent=body, leftIndent=14, bulletIndent=2,
                        spaceAfter=3, alignment=TA_LEFT)

# ---------- helpers ----------
def P(text, style=body):
    return Paragraph(text, style)

def H1(text):
    return Paragraph(text, h1)

def H2(text):
    return Paragraph(text, h2)

def H3(text):
    return Paragraph(text, h3)

def rule():
    return HRFlowable(width="100%", thickness=0.5, color=RULE, spaceBefore=4, spaceAfter=8)

def gap(n=6):
    return Spacer(1, n)

def bullets(items):
    return ListFlowable(
        [ListItem(P(t, bullet), leftIndent=10, value="•", bulletColor=ACCENT) for t in items],
        bulletType="bullet", start="•", leftIndent=12, bulletFontSize=10,
    )

def rating_chip(level):
    color = {"hoch": HIGH, "sehr hoch": HIGH, "mittel": MID, "niedrig": LOW, "n/a": NA}.get(level.lower(), NA)
    tbl = Table([[P(f"<font color='white'><b>{level.upper()}</b></font>", small)]],
                colWidths=[3.6*cm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), color),
        ("BOX", (0,0), (-1,-1), 0, color),
        ("LEFTPADDING", (0,0), (-1,-1), 6),
        ("RIGHTPADDING", (0,0), (-1,-1), 6),
        ("TOPPADDING", (0,0), (-1,-1), 3),
        ("BOTTOMPADDING", (0,0), (-1,-1), 3),
    ]))
    return tbl


def standard_block(name, was, eignung, ereignis, luecke, empfehlung):
    """Render a standardised block per Standard."""
    elems = [H3(name)]
    elems.append(rating_chip(eignung["label"]))
    elems.append(gap(4))
    elems.append(P(f"<b>Was es ist.</b> {was}"))
    elems.append(P(f"<b>NIP-Eignung.</b> {eignung['begruendung']}"))
    if ereignis:
        elems.append(P(f"<b>Ereignis-Vorschlag.</b> {ereignis}"))
    if luecke:
        elems.append(P(f"<b>Lücken / Probleme.</b> {luecke}"))
    if empfehlung:
        elems.append(P(f"<b>Empfehlung.</b> {empfehlung}"))
    elems.append(gap(8))
    return KeepTogether(elems)


# ---------- doc ----------
doc = SimpleDocTemplate(
    OUTPUT, pagesize=A4,
    leftMargin=2.0*cm, rightMargin=2.0*cm,
    topMargin=2.0*cm, bottomMargin=2.2*cm,
    title="openBIM-Standards × Nostr — NIP-Eignung",
    author="Felix Hitthaler",
)

def on_page(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(MUTED)
    page_text = f"Seite {doc.page}"
    canvas.drawString(2.0*cm, 1.2*cm, "openBIM × Nostr — NIP-Eignung")
    canvas.drawRightString(A4[0]-2.0*cm, 1.2*cm, page_text)
    canvas.restoreState()


story = []

# ---------- Cover ----------
story.append(Spacer(1, 4*cm))
story.append(Paragraph("openBIM-Standards × Nostr", title))
story.append(Paragraph("Welche Standards sind NIP-fähig — und wie?", subtitle))
story.append(gap(20))
story.append(P("Research-Vorlauf zur Identifikation realistischer NIP-Kandidaten "
               "im Schnittfeld buildingSMART-Ökosystem und Nostr-Protokoll. "
               "Ziel: priorisierte Liste von Spezifikationsstücken, die als "
               "eigenständige NIPs (Nostr Implementation Possibility) sinnvoll sind, "
               "samt Event-Skizzen und offenen Fragen."))
story.append(gap(30))
story.append(Paragraph("<b>Autor</b>&nbsp;&nbsp;Felix Hitthaler", meta))
story.append(Paragraph("<b>Stand</b>&nbsp;&nbsp;Mai 2026", meta))
story.append(Paragraph("<b>Status</b>&nbsp;&nbsp;Diskussionsentwurf", meta))
story.append(Paragraph("<b>Bezug</b>&nbsp;&nbsp;openbimstandards.org · "
                       "buildingsmart.org · github.com/buildingSMART · "
                       "github.com/openBIMstandards", meta))
story.append(PageBreak())

# ---------- TOC (manuell, weil simpel) ----------
story.append(H1("Inhalt"))
toc_items = [
    "1. Ausgangslage und Methode",
    "2. openBIMstandards.org — Incubator-Bestand",
    "3. buildingSMART-Portfolio im Detail",
    "    3.1 Industry Foundation Classes (IFC)",
    "    3.2 Information Delivery Specification (IDS)",
    "    3.3 BIM Collaboration Format (BCF)",
    "    3.4 buildingSMART Data Dictionary (bSDD)",
    "    3.5 openCDE-Initiative (Foundation, Documents, Dictionary, BCF APIs)",
    "    3.6 IFC Validation Service",
    "    3.7 Use Case Management (UCM)",
    "    3.8 Information Delivery Manual (IDM)",
    "4. Querschnitt — weitere relevante Standards",
    "5. NIP-Eignungs-Matrix",
    "6. Top-Kandidaten — Skizzen",
    "7. Roadmap-Vorschlag",
    "8. Quellen",
]
for item in toc_items:
    story.append(P(item, body_left))
story.append(PageBreak())

# ---------- 1. Ausgangslage ----------
story.append(H1("1. Ausgangslage und Methode"))
story.append(P(
    "openBIM ist der Sammelbegriff für offene, herstellerneutrale Datenaustausch- und "
    "Koordinationsstandards im Bauwesen, getragen primär von buildingSMART International "
    "(bSI) und ergänzenden Initiativen. Die Kern-Standards sind IFC (Modellschema), "
    "IDS (Anforderungsschema), BCF (Issue-Format), bSDD (Datenwörterbuch), sowie das "
    "openCDE-Bündel an REST-APIs, das Common-Data-Environment-Funktionen "
    "herstellerneutral spezifiziert."))
story.append(P(
    "Parallel existiert die Community-Initiative <font color='#0b5394'>openBIMstandards.org</font> "
    "(github.com/openBIMstandards) als &lsquo;Incubator for agile open BIM standards for the web&rsquo; "
    "— kleinere Repos zu ifcOWL, BimJSON, Property-Set-Definitions und Modell-Checking. "
    "Die Aktivität dort ist seit ca. 2020 niedrig, die Konzepte sind aber inhaltlich nahe an "
    "dem, was Nostr-native Tooling braucht: web-orientiert, JSON-affin, signierbar, "
    "föderierbar."))
story.append(P(
    "<b>Methode dieser Untersuchung.</b> Jedes Artefakt wird auf vier Dimensionen geprüft:"))
story.append(bullets([
    "<b>Datenmodell-Fit</b> — lässt sich der Standard in Nostr-Event-Form (signiertes JSON, "
    "Tags, Replacable-Semantik) abbilden, ohne wesentliche Semantik zu verlieren?",
    "<b>Identitäts- und Berechtigungs-Fit</b> — passt das Autorenmodell zu npub-Signaturen "
    "und Group-/Badge-Logik (NIP-29, NIP-58)?",
    "<b>Datei-Layer</b> — wie wird die binäre Komponente (IFC, Snapshot, Anhang) gehandhabt?",
    "<b>Dezentralisierungs-Nutzen</b> — gibt es einen echten Vorteil gegenüber dem Status quo "
    "(Zentralität abbauen, Plattform-Lock-in vermeiden, neue Workflows freischalten)?",
]))
story.append(P(
    "Die Eignung wird in drei Stufen klassifiziert: "
    "<b>HOCH</b> (NIP-Draft lohnt sich, Nutzen klar), "
    "<b>MITTEL</b> (denkbar, aber mit Kompromissen), "
    "<b>NIEDRIG</b> (Nostr ist hier nicht der richtige Layer)."))
story.append(P(
    "<b>Abgrenzung.</b> BCF wurde bereits in einem separaten Research-Dokument "
    "vertieft behandelt (BCF-over-Nostr NIP-Draft). Hier nur kurze Einordnung und "
    "Verweise."))
story.append(PageBreak())

# ---------- 2. openBIMstandards.org Incubator ----------
story.append(H1("2. openBIMstandards.org — Incubator-Bestand"))
story.append(P(
    "Die GitHub-Organisation <font color='#0b5394'>openBIMstandards</font> umfasst acht "
    "Repos, davon mehrere archiviert oder seit Jahren inaktiv. Inhaltlich interessant für "
    "Nostr-Adaptionen sind drei Artefakte: ifcOWL, BimJSON und das PSD-Repository. "
    "modelcheckN3 und der Schependomlaan-Datensatz sind Methoden-/Daten-Showcases und "
    "nicht selbst Standardisierungsgegenstand."))

story.append(standard_block(
    "ifcOWL",
    "RDF/OWL-Ontologie-Variante von IFC, primär für Linked-Data-Anwendungen. "
    "SPARQL-fähig, Verbindung zur Semantic-Web-Toolchain.",
    {"label": "NIEDRIG",
     "begruendung": "Nostr-Events sind JSON-Streams, keine RDF-Tripel. Eine "
     "vollständige Ontologie als Event-Strom hätte hohen Konvertierungsverlust "
     "und keinen Praxisnutzen gegenüber dem nativen Triple-Store-Stack."},
    None,
    "Andere Datenphilosophie (Graph-DB vs. Append-Log). Reasoner-Logik nicht abbildbar.",
    "Kein eigener NIP. Berührungspunkt: JSON-LD im event.content wäre für "
    "Linked-Data-Brücken denkbar — dafür reicht ein generischer Kind plus "
    "spezielle Tag-Konventionen."))

story.append(standard_block(
    "BimJSON",
    "JSON-Kommunikationsstandard-Entwurf für Online-BIM-Tools (Repo zuletzt 2015 aktiv). "
    "Idee: einfacher JSON-Austausch jenseits von IFC.",
    {"label": "MITTEL",
     "begruendung": "Format passt grundsätzlich, hat aber keine nennenswerte "
     "Verbreitung. Reaktivierung als Nostr-Format wäre eher Neuerfindung als Adaption."},
    None,
    "Kaum Mindshare, kein aktueller Maintainer. Definitions-Lücken in Geometrie und "
    "Property-Sets.",
    "Nicht eigenständig weiterführen. Stattdessen IFC-Subset-Excerpts (z. B. nur "
    "Spatial Structure + ausgewählte Properties) als zweckspezifische Events modellieren, "
    "wo das sinnvoll ist."))

story.append(standard_block(
    "BIMbots-PSD-Repository",
    "Repository und GraphQL-Server für Property Set Definitions (PSDs). PSDs sind "
    "die Vorlagen, die in IFC den Werten Bedeutung geben (Pset_WallCommon, "
    "Pset_DoorWindow­Glazing­Type usw.).",
    {"label": "HOCH",
     "begruendung": "PSDs sind kleine, klar strukturierte Records mit eigener GUID. "
     "Perfekt für parameterized replaceable Events: jeder Herausgeber publiziert seine "
     "PSDs unter eigener npub, Konsumenten subscriben gezielt."},
    "<font face='Courier'>kind:30821</font> openBIM-PSD, d=PSD-GUID. Felder: Name, "
    "DefiningValue, ApplicableClasses, PropertyDefinitions[]. Bezug zu bSDD via URI-Tag.",
    "Konflikt-Fall mehrerer PSD-Autoren mit gleichem Namen — über Namensräume "
    "(npub-Prefix) lösbar.",
    "<b>Starker NIP-Kandidat.</b> Klein, klar, hoher Praxisnutzen. Kann unabhängig von "
    "bSDD existieren und sich später mit einem bSDD-NIP zusammenwachsen lassen."))

story.append(standard_block(
    "modelcheckN3",
    "Modell-Validierung über Notation3-Regeln auf ifcOWL.",
    {"label": "NIEDRIG",
     "begruendung": "Semantic-Web-Toolchain, gleiches Argument wie ifcOWL."},
    None,
    "Andere Datenphilosophie.",
    "Kein eigener NIP."))

story.append(standard_block(
    "Archive-DataSetSchependomlaan",
    "Klassisches Test-Dataset mit IFC + dazugehörigen Daten — methodischer Showcase, "
    "kein Standard.",
    {"label": "N/A", "begruendung": "Kein Standard, kein NIP-Gegenstand."},
    None, None,
    "Als Test-Vektor für IFC- und IDS-Adaptions-PoCs verwenden."))

story.append(PageBreak())

# ---------- 3. buildingSMART Portfolio ----------
story.append(H1("3. buildingSMART-Portfolio im Detail"))

# 3.1 IFC
story.append(H2("3.1 Industry Foundation Classes (IFC)"))
story.append(rating_chip("NIEDRIG (auf Entity-Level) / HOCH (auf File-Level)"))
story.append(gap(4))
story.append(P(
    "<b>Was es ist.</b> Schemenbasiertes Datenmodell für Bauwerke — STEP-Physical-File "
    "(.ifc), ifcXML, ifcJSON sowie ifcOWL-Serialisierungen. Aktuell IFC 4.3 als "
    "ISO 16739-1:2024, in Vorbereitung IFC 4.4 (Erweiterungen Wasser/Tunnel/Industrie) "
    "und Diskussion zu IFC 5. Tausende Entity-Typen, Geometrie + Alphanumerik, "
    "typischer Modellumfang einige hundert MB bis mehrere GB."))
story.append(P(
    "<b>NIP-Eignung.</b> Auf Entity-Level (jede IfcWall, IfcDoor etc. als eigenes Event) "
    "<b>klar ungeeignet</b>: Millionen Events pro Realprojekt, Schreiblast, "
    "Indexier-Aufwand, Relay-Last. Auf File-Level (ganzes Modell als Blob plus "
    "Metadaten-Event) <b>gut geeignet</b>: passt zu NIP-94 + Blossom-Hash + optional "
    "kind:30904 BCF-File-Reference (siehe BCF-Doc) und/oder OpenTimestamps-Anker auf der "
    "Timechain für Notarfunktion. Subset-Level (z. B. nur Spatial Structure als Treemap-"
    "Event) wäre für föderierte Modell-Übersichten denkbar, ist aber nicht "
    "standardisiert und eher Forschungs- als NIP-Material."))
story.append(P(
    "<b>Empfehlung.</b> Kein dedizierter IFC-NIP. Stattdessen: generische "
    "<font face='Courier'>kind:1063</font> NIP-94 file-metadata Events mit "
    "IFC-spezifischen Tags (<font face='Courier'>schema=IFC4X3</font>, "
    "<font face='Courier'>ifc-project</font>, <font face='Courier'>ifc-site</font>, "
    "<font face='Courier'>ifc-building</font>). Provenance, Signatur und Versionierung "
    "ergeben sich aus dem File-Reference-Event."))
story.append(gap(6))

# 3.2 IDS
story.append(H2("3.2 Information Delivery Specification (IDS)"))
story.append(rating_chip("SEHR HOCH"))
story.append(gap(4))
story.append(P(
    "<b>Was es ist.</b> Seit Juni 2024 als IDS 1.0 finaler bSI-Standard. XML/XSD-basiertes "
    "Format zur computer-interpretierbaren Definition von Informationsanforderungen, die "
    "automatisch gegen IFC-Modelle geprüft werden können. Eine IDS-Datei enthält "
    "<font face='Courier'>ids:info</font> (Title, Version, Author, Date, Description, "
    "Copyright, IfcVersion, Milestone, License, Purpose) und einen "
    "<font face='Courier'>ids:specifications</font>-Block; pro Spezifikation eine "
    "Anwendbarkeits-Bedingung (Entity, Attribute, Classification, Property, Material, "
    "PartOf) plus Anforderungen mit Kardinalität."))
story.append(P(
    "<b>NIP-Eignung.</b> Sehr hoch. IDS-Files sind klein (typisch wenige kB), strukturiert, "
    "haben sinnvolle Autorschaft (Auftraggeber, AHJ, Generalplaner), eindeutige Versionen "
    "und sind exakt der Use-Case, in dem signierte, replizierbare, versionierte Events "
    "Mehrwert liefern: Anforderungen werden öffentlich signiert publiziert, Auftragnehmer "
    "abonnieren, automatische Checker konsumieren."))
story.append(P("<b>Ereignis-Vorschlag.</b>"))
story.append(Paragraph(
    "kind:30810 — openBIM IDS Specification (parameterized replaceable, d=spec-guid)<br/>"
    "tags: a (project), ids-version, ifc-version, milestone, status (Draft/Final), "
    "purpose, t (Pflicht-Tags je Domäne)<br/>"
    "content: JSON-Repräsentation der IDS-Specifications, oder den ursprünglichen "
    "ids-XML-Inhalt 1:1 — Round-trip-fähig.<br/>"
    "<br/>"
    "kind:1180 — IDS Validation Result (regulär, immutabel)<br/>"
    "tags: e (IDS-Event), e (IFC-File-Event), x (sha256 des Reports), result (pass/fail), "
    "p (Validator-npub)<br/>"
    "content: Zusammenfassung; vollständiger Report als NIP-94-Begleit-Event.",
    code))
story.append(P(
    "<b>Lücken / Probleme.</b> IDS referenziert bSDD-URIs für Properties — die müssen "
    "auflösbar bleiben (Mirror-Cache empfehlenswert). IDS-Versions-Upgrades (1.0 → 1.1 → "
    "2.0) brauchen klare Migrations-Hinweise im NIP."))
story.append(P(
    "<b>Empfehlung.</b> <b>Erstklassiger NIP-Kandidat.</b> Klein, mächtig, dezentral "
    "publizierbar — passt auch politisch zur Idee, dass Auftraggeber-Anforderungen nicht "
    "in proprietären Portalen versteckt liegen sollten. Ideale Erweiterung des BCF-NIPs: "
    "IDS-NIP definiert Anforderungen, BCF-NIP dokumentiert Verstöße/Themen."))
story.append(gap(6))

# 3.3 BCF
story.append(H2("3.3 BIM Collaboration Format (BCF)"))
story.append(rating_chip("HOCH"))
story.append(gap(4))
story.append(P(
    "<b>Was es ist.</b> Standard für Issue- und Koordinationskommunikation in BIM-"
    "Projekten. BCF-XML 3.0 (Container .bcfzip) und BCF-API. Topics, Comments, "
    "Viewpoints, Snapshots, IFC-Element-Referenzen."))
story.append(P(
    "<b>NIP-Eignung.</b> Hoch. Bereits separat ausgearbeitet als BCF-over-Nostr "
    "NIP-Entwurf — Event-Kinds 30900–30904 (Topic, Viewpoint, Project, Document Ref, "
    "File Ref) plus 1170–1172 (Comment, Audit, Reaction)."))
story.append(P(
    "<b>Empfehlung.</b> Eigenständiger NIP, läuft parallel zum IDS-NIP. Querverweise "
    "zwischen IDS-Validation-Result-Events und BCF-Topic-Events sind die natürliche "
    "Brücke (failed Validation → automatischer BCF-Topic)."))
story.append(gap(6))

# 3.4 bSDD
story.append(H2("3.4 buildingSMART Data Dictionary (bSDD)"))
story.append(rating_chip("HOCH (konzeptionell) / MITTEL (praktisch)"))
story.append(gap(4))
story.append(P(
    "<b>Was es ist.</b> Zentrale Datenbank für Klassifikationen, Klassen, Properties, "
    "Werte und ihre Übersetzungen. REST-API. URI-basierte Identität "
    "(<font face='Courier'>https://identifier.buildingsmart.org/uri/...</font>). "
    "Klassifikationssysteme (Uniclass, OmniClass, ETIM u. v. m.) liegen dort gepflegt."))
story.append(P(
    "<b>NIP-Eignung.</b> Konzeptionell sehr passend — föderierte, signierte Definitionen "
    "sind genau die Disziplin, in der Nostr glänzt. Praktisch hängt der Wert vom "
    "Konsens-Layer ab: ein Dictionary ohne kuratierte Single-Source verliert seinen "
    "Zweck. Brauchbares Modell: jeder Herausgeber (Hersteller, Verband, Kammer) "
    "publiziert seine Klassen unter eigener npub; Konsumenten wählen, wem sie folgen, "
    "Aggregator-Relays liefern kuratierte Sichten."))
story.append(P("<b>Ereignis-Vorschlag.</b>"))
story.append(Paragraph(
    "kind:30820 — bSDD Classification System (d=URI)<br/>"
    "kind:30821 — bSDD Class (d=URI)  // hier mit BIMbots-PSD-Repository konvergent<br/>"
    "kind:30822 — bSDD Property (d=URI)<br/>"
    "kind:30823 — bSDD Value List (d=URI)<br/>"
    "tags: lang (mehrsprachig), version, parent (URI des übergeordneten Systems), "
    "ifc-mapping (Pset_xyz oder direkt IfcEntity)<br/>"
    "content: JSON mit allen lokalisierten Bezeichnungen, Definitionen, Synonymen, "
    "Einheiten, applikabler IFC-Domäne.",
    code))
story.append(P(
    "<b>Lücken / Probleme.</b> Konflikt-Resolution bei konkurrierenden Definitionen. "
    "URI-Erhalt bei Spiegelung auf Nostr. Performance bei großem Klassen-Korpus "
    "(Uniclass mit zehntausenden Klassen → entsprechend viele Events, Index-Last)."))
story.append(P(
    "<b>Empfehlung.</b> NIP-Draft sinnvoll, aber zuerst kleineren Scope (PSD-Repository, "
    "siehe 3.4-Verwandte aus 2.0) als Vorstudie. Voller bSDD-Spiegel als Phase 2."))
story.append(gap(6))

# 3.5 openCDE
story.append(H2("3.5 openCDE-Initiative (Foundation, Documents, Dictionary, BCF APIs)"))
story.append(rating_chip("HOCH"))
story.append(gap(4))
story.append(P(
    "<b>Was es ist.</b> Bündel von REST-APIs als herstellerneutrale CDE-Layer-Spec. "
    "Foundation API (Auth, Sessions, Projekte, User), Documents API (Dokumente, "
    "Versionen, Metadaten), Dictionary API (Verbindung zu bSDD), BCF API (Issue-Tracking)."))
story.append(P("<b>NIP-Eignung pro API.</b>"))
story.append(bullets([
    "<b>Foundation API → HOCH.</b> Projekte als <font face='Courier'>kind:30902</font> "
    "(siehe BCF-Doc), User als npub mit Profile-Event (NIP-01 kind:0), Auth via "
    "NIP-42, Berechtigungen via NIP-29 group membership. Direkter Ersatz auf "
    "Protokoll-Ebene möglich.",
    "<b>Documents API → HOCH.</b> Document-Records als parameterized replaceable "
    "Event (<font face='Courier'>kind:30930</font> openBIM Document Record), Files via "
    "NIP-94 + Blossom, Versionierung über erneutes Publish desselben d-Tags, "
    "Lifecycle-Status (WIP/Shared/Published/Archive nach ISO 19650) als Tag "
    "<font face='Courier'>iso19650-state</font>.",
    "<b>Dictionary API → HOCH (via bSDD-NIP, s. 3.4).</b>",
    "<b>BCF API → HOCH (via BCF-NIP, s. 3.3).</b>",
]))
story.append(P(
    "<b>Empfehlung.</b> Statt vier eigene NIPs einen <b>openCDE-Brücken-NIP</b>: "
    "definiert einen HTTP-Adapter-Pattern, der openCDE-API-Endpunkte auf Nostr-Events "
    "abbildet. Damit bleiben bestehende Tools (ACC, Bimcollab, Solibri) ohne "
    "Nostr-Patches nutzbar — der Adapter terminiert REST nach außen, Nostr nach innen. "
    "Übergangslösung mit hohem Praxiswert."))
story.append(P("<b>Ereignis-Vorschlag für Documents.</b>"))
story.append(Paragraph(
    "kind:30930 — openBIM Document Record (parameterized replaceable, d=document-guid)<br/>"
    "tags: a (project), iso19650-state (WIP|Shared|Published|Archive), "
    "title, mime, version, x (sha256), url (Blossom), revision, "
    "supersedes (event-id eines früheren Records, optional), p (Verantwortlicher)<br/>"
    "content: JSON mit Beschreibung, Metadaten, Klassifikation-Refs.",
    code))
story.append(gap(6))

# 3.6 Validation Service
story.append(H2("3.6 IFC Validation Service"))
story.append(rating_chip("HOCH"))
story.append(gap(4))
story.append(P(
    "<b>Was es ist.</b> Kostenloser zentraler Online-Validator von bSI, prüft IFC-Files "
    "gegen Schema, Implementer-Agreements und MVDs, liefert strukturierten Report. "
    "Aktuell als Strategic Project geführt."))
story.append(P(
    "<b>NIP-Eignung.</b> Hoch als Data Vending Machine (NIP-90). Validation ist eine "
    "wohldefinierte Service-Funktion mit klarer Input/Output-Form — perfekter "
    "DVM-Use-Case. Mehrere unabhängige Validator-Provider können konkurrieren, "
    "Reputations-Layer ergibt sich aus Result-History und Tags-/Reviews-Volumen."))
story.append(P("<b>Ereignis-Vorschlag.</b>"))
story.append(Paragraph(
    "kind:5901 — IFC Validation Job Request (NIP-90 input)<br/>"
    "tags: i (IFC-URL + sha256), schema (IFC4|IFC4X3|IFC4X4), "
    "ids-ref (event-id einer IDS-Spec, optional), bid (max sats)<br/>"
    "<br/>"
    "kind:6901 — IFC Validation Job Result (NIP-90 output)<br/>"
    "tags: e (request-event), result (pass|fail|warning), "
    "report-url, x (sha256 des Reports), summary (Anzahl errors/warnings)<br/>"
    "content: JSON-Zusammenfassung; Volltext-Report via NIP-94-Begleit-Event.",
    code))
story.append(P(
    "<b>Empfehlung.</b> <b>Klarer NIP-Kandidat.</b> Kombiniert mit IDS-NIP entsteht "
    "ein dezentrales QA-Netzwerk: Auftraggeber publiziert IDS, Auftragnehmer publiziert "
    "IFC + Validator-Bestellung, mehrere Validatoren bieten, der Beste/Schnellste "
    "gewinnt, alle Ergebnisse sind signiert und nachprüfbar."))
story.append(gap(6))

# 3.7 UCM
story.append(H2("3.7 Use Case Management (UCM)"))
story.append(rating_chip("HOCH"))
story.append(gap(4))
story.append(P(
    "<b>Was es ist.</b> Online-Service zur Erfassung und Austausch von Use Cases — "
    "Anwendungsfällen für openBIM-Workflows mit zugehörigen IDS/IDM, "
    "Domänen-Kontext, Stakeholder, Information-Exchange-Schema. Service unter "
    "ucm.buildingsmart.org."))
story.append(P(
    "<b>NIP-Eignung.</b> Hoch. Use-Case-Records sind reine Metadaten-Objekte mit "
    "strukturierten Feldern, gut abbildbar auf parameterized replaceable Events."))
story.append(P("<b>Ereignis-Vorschlag.</b>"))
story.append(Paragraph(
    "kind:30840 — openBIM Use Case (parameterized replaceable, d=usecase-id)<br/>"
    "tags: t (Domäne), stage (Bauphase), stakeholders (mehrfach), "
    "ids-ref, idm-ref, lang<br/>"
    "content: JSON nach UCM-Datenmodell (Titel, Beschreibung, Motivation, "
    "Vorbedingungen, Schritte, Ergebnisse, KPIs).",
    code))
story.append(P(
    "<b>Empfehlung.</b> Schöner sekundärer NIP — niedriges Risiko, sofort produktiv, "
    "kann unabhängig von IDS/BCF starten und sich später quervernetzen."))
story.append(gap(6))

# 3.8 IDM
story.append(H2("3.8 Information Delivery Manual (IDM)"))
story.append(rating_chip("MITTEL"))
story.append(gap(4))
story.append(P(
    "<b>Was es ist.</b> bSI-Standard zur Beschreibung von Geschäftsprozessen und "
    "Informationsanforderungen, die später in IFC und IDS technisch konkret werden. "
    "BPMN-affin, eher textlastig."))
story.append(P(
    "<b>NIP-Eignung.</b> Mittel. IDMs sind strukturierte Dokumente, deren Wert aber "
    "stark in Diagrammen und Erläuterungen liegt — eher klassisches Publishing. "
    "NIP-23 Long-form-Content (kind:30023) wäre ausreichend, ohne dedizierten NIP."))
story.append(P(
    "<b>Empfehlung.</b> Kein eigener NIP. Stattdessen NIP-23 nutzen, mit Convention-"
    "Tags <font face='Courier'>idm-domain</font>, <font face='Courier'>process-bpmn</font> "
    "(Hash auf hinterlegtes BPMN), <font face='Courier'>ifc-version</font>."))
story.append(PageBreak())

# ---------- 4. Querschnitt ----------
story.append(H1("4. Querschnitt — weitere relevante Standards"))
story.append(P(
    "Über das bSI-Kernsortiment hinaus existieren benachbarte Standards, die im "
    "Praxisbetrieb gemeinsam mit IFC/IDS/BCF auftreten und ebenfalls auf "
    "NIP-Eignung geprüft werden sollten."))

story.append(standard_block(
    "LOIN (DIN EN 17412-1:2020)",
    "Level of Information Need. Definiert geometrische, alphanumerische und "
    "Dokumentations-Granularität pro Informations-Anforderung. In Deutschland und "
    "EU-weit als Methode für Informations­anforderungen etabliert.",
    {"label": "HOCH",
     "begruendung": "Strukturierte Metadaten, klar versionierbar, oft eng mit IDS "
     "und Pset-Vorgaben verknüpft. Ideal als parameterized replaceable Event."},
    "<font face='Courier'>kind:30811</font> openBIM LOIN Definition, d=loin-id. "
    "Tags: a (project), purpose, milestone, ids-ref. content: JSON mit den drei "
    "LOIN-Achsen.",
    "Verzahnung mit IDS sauber halten — Vorschlag: LOIN-Event referenziert das IDS-Event, "
    "nicht umgekehrt, weil LOIN konzeptionell vor IDS kommt.",
    "Mit IDS zusammen denken — bietet sich als gemeinsamer NIP oder eng kooperierender "
    "Folge-NIP an."))

story.append(standard_block(
    "COBie",
    "Construction-Operations Building Information Exchange. Spreadsheet- oder "
    "ifcXML-basiertes Handover-Format für FM-Daten.",
    {"label": "NIEDRIG",
     "begruendung": "Dateiformat, kein Protokoll. Übergabe-Charakter (einmaliger "
     "Transfer), keine laufende Kollaboration."},
    None,
    "Inhalte sind tabellarisch, gehören als ganzes File via NIP-94 + Blossom abgelegt, "
    "nicht in Event-Schema gequetscht.",
    "Kein eigener NIP. Generischer File-Layer reicht."))

story.append(standard_block(
    "Product Data Templates (ISO 23387, ISO 23386)",
    "Templates für Hersteller-Produktdaten — strukturierte, mehrsprachige Property-Sets "
    "pro Produktklasse. EU-Bauproduktenverordnung (CPR) und Digital Product Passport "
    "verstärken die Relevanz drastisch.",
    {"label": "HOCH",
     "begruendung": "Hersteller-signierte Produktdaten passen perfekt zu npub-Identität. "
     "EU-DPP-Pflicht ab 2027 macht den Use-Case hoch-aktuell. Berührungspunkt mit dem "
     "in einer früheren Diskussion entworfenen Material-Pass-Konzept."},
    "<font face='Courier'>kind:30850</font> openBIM Product Data Template, d=template-id. "
    "Tags: manufacturer-npub, classification-uri (bSDD), product-category, "
    "lang, valid-from, valid-to. content: JSON nach ISO-23387-Datenmodell.",
    "Versionierung und Widerruf bei Produktänderung — analog NIP-58-Badge-Revoke per "
    "NIP-09 Delete.",
    "<b>Sehr starker Kandidat</b>, weil regulatorisches Andocken (CPR, EU-DPP) jetzt "
    "erfolgt und Hersteller in Bewegung sind."))

story.append(standard_block(
    "ISO 19650",
    "Prozess-Standard für CDE-Betrieb und Information Management. Definiert "
    "States (WIP / Shared / Published / Archive), Rollen, Workflows.",
    {"label": "MITTEL",
     "begruendung": "Prozess, kein Schema. Direkt nicht abbildbar, aber als "
     "Tag-Convention sehr nützlich (siehe 3.5)."},
    None,
    "Workflow-Engine wäre eigene große Aufgabe — gehört nicht in den NIP-Core.",
    "Tag-Convention <font face='Courier'>iso19650-state</font> im Documents-/BCF-NIP "
    "integrieren. Kein eigener NIP."))

story.append(standard_block(
    "DIN SPEC 91357 / EN ISO 16484 (BACnet u. ä.)",
    "Gebäudeautomations- und Twin-Standards für Mess-/Steuer-/Regel-Daten. "
    "Operative Datenebene neben dem statischen IFC.",
    {"label": "HOCH",
     "begruendung": "Live-Sensordaten signiert via npub publizieren ist genau der "
     "Bereich, in dem Nostr seinen Streaming-Charakter ausspielt. Anknüpfung an "
     "ESG/EPBD-Recast-Monitoring (EU-Richtlinie 2024/1275)."},
    "<font face='Courier'>kind:1230</font> Building Telemetry (regulär, ephemeral-affin). "
    "Tags: device-id (IfcGUID-koppelbar), unit, point-type, project. content: "
    "kompakter JSON-Payload (timestamp, value, quality).",
    "Hohe Frequenz → Relay-Last. Optional Aggregations-Events (1 min / 1 h Mittel).",
    "Eigener NIP <b>HKLS-Telemetrie</b> sinnvoll, koppelt direkt an die HKLS-Twin-"
    "Projekt-Idee aus der Sovereign-Engineering-Roadmap."))

story.append(PageBreak())

# ---------- 5. Matrix ----------
story.append(H1("5. NIP-Eignungs-Matrix"))
story.append(P(
    "Synoptische Sicht. Sortierung nach NIP-Eignung absteigend. Spalte Aufwand "
    "schätzt grob: S = ein Wochenende, M = einige Wochen, L = mehrere Monate."))

matrix = [
    ["Standard", "Eignung", "Event-Kind (Vorschlag)", "Aufwand", "Killer-Use-Case"],
    ["IDS",                       "Sehr hoch", "30810 + 1180",          "M", "Auftraggeber-Anforderungen souverän"],
    ["BCF",                       "Hoch",      "30900–30904 / 1170–72", "M", "Koordinations-Issues ohne Plattform"],
    ["Validation Service",        "Hoch",     "5901 / 6901 (NIP-90)",   "M", "Dezentrales QA-Netzwerk"],
    ["Documents (openCDE)",       "Hoch",     "30930",                  "M", "ISO-19650-konforme Doc-Verteilung"],
    ["Foundation (openCDE)",      "Hoch",     "—  (NIP-29 + 30902)",   "S", "Projekt-Container ohne Server"],
    ["Use Case Management",       "Hoch",     "30840",                  "S", "Föderierte Use-Case-Bibliothek"],
    ["PSD (BIMbots-Repo)",        "Hoch",     "30821",                  "S", "Hersteller-Pset-Verteilung"],
    ["Product Data Templates",    "Hoch",     "30850",                  "M", "EU-DPP-Anbindung"],
    ["LOIN (EN 17412)",           "Hoch",     "30811",                  "S", "LOIN als signierter Anforderungsblock"],
    ["bSDD",                      "Mittel",   "30820–30823",            "L", "Föderiertes Datenwörterbuch"],
    ["Telemetrie (BACnet-Bridge)","Hoch",     "1230",                   "M", "ESG/EPBD-Monitoring"],
    ["IDM",                       "Mittel",   "30023 (NIP-23)",         "S", "Prozess-Doku in Long-form"],
    ["IFC (File-Level)",          "Hoch",     "1063 (NIP-94)",          "S", "Modell-Provenance, OTS-Anker"],
    ["IFC (Entity-Level)",        "Niedrig",  "—",                       "L", "—"],
    ["ifcOWL",                    "Niedrig",  "—",                       "—", "—"],
    ["BimJSON",                   "Niedrig",  "—",                       "—", "—"],
    ["COBie",                     "Niedrig",  "1063 (NIP-94)",          "S", "Handover-Anhang"],
    ["ISO 19650",                 "Mittel",   "Tag-Convention",         "S", "States über alle NIPs hinweg"],
]

tbl = Table(matrix, colWidths=[3.7*cm, 2.0*cm, 4.0*cm, 1.2*cm, 6.0*cm], repeatRows=1)
tbl_style = [
    ("FONT", (0,0), (-1,0), "Helvetica-Bold", 9.5),
    ("BACKGROUND", (0,0), (-1,0), ACCENT),
    ("TEXTCOLOR", (0,0), (-1,0), colors.white),
    ("FONT", (0,1), (-1,-1), "Helvetica", 9),
    ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ("LEFTPADDING", (0,0), (-1,-1), 4),
    ("RIGHTPADDING", (0,0), (-1,-1), 4),
    ("TOPPADDING", (0,0), (-1,-1), 4),
    ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#f6f6f6")]),
    ("GRID", (0,0), (-1,-1), 0.25, RULE),
]
# color-code Eignungs-Zelle
for i, row in enumerate(matrix[1:], start=1):
    rating = row[1].lower()
    if rating in ("sehr hoch", "hoch"):
        c = HIGH
    elif rating == "mittel":
        c = MID
    else:
        c = LOW
    tbl_style.append(("TEXTCOLOR", (1,i), (1,i), c))
    tbl_style.append(("FONT", (1,i), (1,i), "Helvetica-Bold", 9))
tbl.setStyle(TableStyle(tbl_style))
story.append(tbl)
story.append(gap(8))
story.append(P(
    "<b>Beobachtung.</b> Die Eignung verdichtet sich auf eine kleine Gruppe von "
    "Metadaten-getriebenen Standards (IDS, BCF, UCM, LOIN, PSD/PDT) plus einer "
    "DVM-fähigen Service-Schicht (Validation). Modell-Daten (IFC) und Linked-Data-"
    "Konstrukte (ifcOWL) sind die schwächsten Kandidaten — was logisch ist: Nostr "
    "ist ein Event-Stream-Protokoll, kein Graph-Store und kein BLOB-Layer."))

story.append(PageBreak())

# ---------- 6. Top-Kandidaten ----------
story.append(H1("6. Top-Kandidaten — Skizzen"))
story.append(P(
    "Drei Standards bilden ein zusammenhängendes Minimum Viable Set, das für sich allein "
    "schon Nutzen liefert und sich gegenseitig verstärkt: <b>IDS</b>, <b>BCF</b> und "
    "<b>Validation</b>. Plus ein vierter, regulatorisch starker Anker: <b>Product Data "
    "Templates</b>."))

story.append(H3("6.1 IDS-NIP — Souveräne Anforderungen"))
story.append(bullets([
    "<b>Scope.</b> IDS-1.0-Specs als parameterized replaceable Events publizieren, "
    "abonnierbar, signiert.",
    "<b>Event-Kinds.</b> 30810 (Spec), 1180 (Validation-Result).",
    "<b>Datei-Layer.</b> Inline ids-XML in content für kleine Specs (&lt; 16 kB), sonst "
    "Blossom-Referenz + NIP-94.",
    "<b>Berechtigung.</b> Öffentlich publizierbar; Pflicht-IDS innerhalb eines Projekts "
    "via NIP-29-Gruppen-Channel.",
    "<b>MVP.</b> CLI <font face='Courier'>ids2nostr</font> + Web-Viewer in 2–3 Wochen "
    "machbar.",
    "<b>Ökosystem-Synergie.</b> Schließt nahtlos an BCF-NIP an: failed Validation → "
    "automatischer BCF-Topic mit Cross-Reference.",
]))

story.append(H3("6.2 Validation-NIP — DVM für IFC-Audit"))
story.append(bullets([
    "<b>Scope.</b> IFC-Validierung als Service über NIP-90 (Data Vending Machine).",
    "<b>Event-Kinds.</b> 5901 (Request), 6901 (Result), 7000 (Payment/Feedback).",
    "<b>Anbieter.</b> Initial 1–2 Validatoren (z. B. bSI-Service als Bot, eine "
    "unabhängige Instanz auf Basis IFCOpenShell-Validator).",
    "<b>Bezahlung.</b> Lightning, LNbits oder Cashu-Mint des DVM-Operators.",
    "<b>Ökosystem-Synergie.</b> Konsumiert IDS-Specs (3.1) und erzeugt BCF-Topics (3.3) "
    "bei Fehlern. Das ist der Kreis, der einen kompletten openBIM-QA-Workflow ohne "
    "zentrale Plattform schließt.",
]))

story.append(H3("6.3 PDT-NIP — Produktdaten am DPP-Andock"))
story.append(bullets([
    "<b>Scope.</b> Hersteller-Property-Sets als signierte Events, an ISO 23387 / 23386 "
    "und EU Digital Product Passport (Verordnung 2024/1781, ESPR) anschlussfähig.",
    "<b>Event-Kinds.</b> 30850 (Template), optional 30851 (Charge/Lot-spezifisches Datenblatt).",
    "<b>Berechtigung.</b> Hersteller-npub mit NIP-58-Badge von akkreditierter Stelle.",
    "<b>Praxis.</b> Anbindung an Material-Pass-Konzept aus dem Sovereign-Engineering-Set: "
    "jedes Bauteil bekommt PDT-Referenz, kann zerlegt und gehandelt werden.",
    "<b>Politischer Hebel.</b> EU-DPP-Pflicht ab 2027 für Baustoffe in Vorbereitung — "
    "wer jetzt souveräne Alternative spezifiziert, ist nicht-trivial vorne.",
]))

story.append(H3("6.4 Documents-NIP — openCDE light"))
story.append(bullets([
    "<b>Scope.</b> Document Records (Pläne, Berichte, Spec-Sheets) mit Versionierung und "
    "ISO-19650-State.",
    "<b>Event-Kind.</b> 30930.",
    "<b>Datei-Layer.</b> Blossom + NIP-94.",
    "<b>MVP-Aufwand.</b> Wochenend-Projekt für den Kern, weil semantisch nahe an "
    "klassischen File-Stores.",
    "<b>Ökosystem-Synergie.</b> Ergänzt BCF-NIP (Issue verlinkt Document), "
    "IDS-NIP (Specification verlinkt referenzierte Dokumente).",
]))

story.append(PageBreak())

# ---------- 7. Roadmap ----------
story.append(H1("7. Roadmap-Vorschlag"))
story.append(P(
    "Reihenfolge nach Aufwand und Zugkraft. Phase 1 produziert sichtbare Ergebnisse "
    "in 6–8 Wochen, Phase 2 erweitert auf den vollen Workflow, Phase 3 öffnet die "
    "regulatorische und service-orientierte Ebene."))

story.append(H3("Phase 1 — Quick Wins (Wochen 1–8)"))
story.append(bullets([
    "BCF-NIP-Draft + Referenzimplementierung (separat in Arbeit).",
    "IDS-NIP-Draft (kind 30810) + CLI ids2nostr, deminstrierbarer Web-Viewer.",
    "UCM-NIP-Draft (kind 30840) — kleinstes Risiko, schnell publishbar als bSI-Use-Case-"
    "Spiegel.",
    "Documents-NIP (kind 30930) als Basis für CDE-Lite.",
]))

story.append(H3("Phase 2 — Workflow-Schluss (Wochen 9–16)"))
story.append(bullets([
    "Validation-NIP (NIP-90 DVM für IFC) — koppelt IDS + BCF.",
    "LOIN-Event-Convention (kind 30811) als Annex zum IDS-NIP.",
    "OpenCDE-HTTP-Adapter: bestehende Tools sprechen openCDE-REST, Adapter terminiert "
    "auf Nostr-Events. Übergangsweg für klassische BIM-Teams.",
]))

story.append(H3("Phase 3 — Regulatorik und Service-Layer (Wochen 17–28)"))
story.append(bullets([
    "PDT-NIP (kind 30850) mit ISO-23387/23386- und EU-DPP-Andock; "
    "Anbindung an Material-Pass-Konzept.",
    "bSDD-NIP (Phase 1: Klassen + Properties) — föderierter Spiegel mit "
    "Kuratorensicht-Filter.",
    "HKLS-Telemetrie-NIP (kind 1230) für Live-Daten aus dem Gebäudebetrieb, koppelt "
    "an ESG/EPBD-Reporting.",
]))

story.append(H3("Quer durch alle Phasen"))
story.append(bullets([
    "Konsens-Sondierung in der bSI-Open-Source-Community zu jedem Draft, bevor "
    "Final-Spec gefroren wird.",
    "PRs gegen <font face='Courier'>nostr-protocol/nips</font> mit Kind-Bereich-"
    "Reservierungen.",
    "Test-Vektoren aus offiziellen bSI-Repositories für Round-trip-Konformität.",
    "Praxis-Validierung an einem eigenen Bau- oder Sanierungsprojekt — Risikominimal, "
    "schneller Reality-Check.",
]))

story.append(PageBreak())

# ---------- 8. Quellen ----------
story.append(H1("8. Quellen"))
sources = [
    ("openBIMstandards.org / GitHub", "http://openbimstandards.org/ — github.com/openBIMstandards"),
    ("buildingSMART openBIM-Übersicht", "https://www.buildingsmart.org/about/openbim/"),
    ("Industry Foundation Classes (IFC)", "https://www.buildingsmart.org/standards/bsi-standards/industry-foundation-classes/"),
    ("Information Delivery Specification (IDS) 1.0", "https://www.buildingsmart.org/standards/bsi-standards/information-delivery-specification-ids/"),
    ("BIM Collaboration Format (BCF)", "https://www.buildingsmart.org/standards/bsi-standards/bim-collaboration-format/"),
    ("buildingSMART Data Dictionary (bSDD)", "https://www.buildingsmart.org/users/services/buildingsmart-data-dictionary/ — https://bsdd.buildingsmart.org/"),
    ("openCDE-API", "https://github.com/buildingSMART/OpenCDE-API"),
    ("IFC Validation Service", "https://www.buildingsmart.org/users/services/validation-service/"),
    ("Use Case Management (UCM)", "https://ucm.buildingsmart.org/"),
    ("Information Delivery Manual (IDM)", "https://www.buildingsmart.org/standards/bsi-standards/information-delivery-manual/"),
    ("Atlas of Open BIM Standards (Global BIM Network)", "https://globalbim.org/info-collection/atlas-of-open-bim-standards/"),
    ("openBIM Knowledgebase (BIMcert Manual 2024)", "https://openbim-knowledgebase.org/en/docs/bimcert-manual-2024/"),
    ("Nostr Protocol — NIPs", "https://github.com/nostr-protocol/nips"),
    ("DIN EN 17412-1:2020 (LOIN)", "Beuth Verlag / EN-Webshop"),
    ("ISO 23387:2020 (Product Data Templates)", "iso.org/standard/75403.html"),
    ("EU-Verordnung 2024/1781 (ESPR, Digital Product Passport)", "eur-lex.europa.eu"),
    ("EU-Richtlinie 2024/1275 (EPBD-Recast)", "eur-lex.europa.eu"),
]
for name, url in sources:
    story.append(P(f"<b>{name}.</b> {url}", small))

story.append(gap(20))
story.append(P("<i>Ende des Research-Dokuments. Korrekturen, Ergänzungen und PRs willkommen.</i>", muted))

# ---------- Build ----------
doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
print(f"OK: {OUTPUT}")
