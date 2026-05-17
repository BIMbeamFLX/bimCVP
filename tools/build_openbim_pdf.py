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
    color = {"high": HIGH, "very high": HIGH, "medium": MID, "low": LOW, "n/a": NA}.get(level.lower(), NA)
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


def standard_block(name, what, suitability, event, gap_issue, recommendation):
    """Render a standardised block per standard."""
    elems = [H3(name)]
    elems.append(rating_chip(suitability["label"]))
    elems.append(gap(4))
    elems.append(P(f"<b>What it is.</b> {what}"))
    elems.append(P(f"<b>NIP suitability.</b> {suitability['rationale']}"))
    if event:
        elems.append(P(f"<b>Event proposal.</b> {event}"))
    if gap_issue:
        elems.append(P(f"<b>Gaps / problems.</b> {gap_issue}"))
    if recommendation:
        elems.append(P(f"<b>Recommendation.</b> {recommendation}"))
    elems.append(gap(8))
    return KeepTogether(elems)


# ---------- doc ----------
doc = SimpleDocTemplate(
    OUTPUT, pagesize=A4,
    leftMargin=2.0*cm, rightMargin=2.0*cm,
    topMargin=2.0*cm, bottomMargin=2.2*cm,
    title="openBIM standards × Nostr — NIP suitability",
    author="Felix Hitthaler",
)

def on_page(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(MUTED)
    page_text = f"Page {doc.page}"
    canvas.drawString(2.0*cm, 1.2*cm, "openBIM × Nostr — NIP suitability")
    canvas.drawRightString(A4[0]-2.0*cm, 1.2*cm, page_text)
    canvas.restoreState()


story = []

# ---------- Cover ----------
story.append(Spacer(1, 4*cm))
story.append(Paragraph("openBIM standards × Nostr", title))
story.append(Paragraph("Which standards are NIP-ready — and how?", subtitle))
story.append(gap(20))
story.append(P("Research groundwork to identify realistic NIP candidates "
               "at the intersection of the buildingSMART ecosystem and the Nostr protocol. "
               "Goal: a prioritised list of specification pieces that make sense as "
               "standalone NIPs (Nostr Implementation Possibility), "
               "together with event sketches and open questions."))
story.append(gap(30))
story.append(Paragraph("<b>Author</b>&nbsp;&nbsp;Felix Hitthaler", meta))
story.append(Paragraph("<b>As of</b>&nbsp;&nbsp;May 2026", meta))
story.append(Paragraph("<b>Status</b>&nbsp;&nbsp;Discussion draft", meta))
story.append(Paragraph("<b>Reference</b>&nbsp;&nbsp;openbimstandards.org · "
                       "buildingsmart.org · github.com/buildingSMART · "
                       "github.com/openBIMstandards", meta))
story.append(PageBreak())

# ---------- TOC (manual, because simple) ----------
story.append(H1("Contents"))
toc_items = [
    "1. Background and method",
    "2. openBIMstandards.org — incubator inventory",
    "3. buildingSMART portfolio in detail",
    "    3.1 Industry Foundation Classes (IFC)",
    "    3.2 Information Delivery Specification (IDS)",
    "    3.3 BIM Collaboration Format (BCF)",
    "    3.4 buildingSMART Data Dictionary (bSDD)",
    "    3.5 openCDE initiative (Foundation, Documents, Dictionary, BCF APIs)",
    "    3.6 IFC Validation Service",
    "    3.7 Use Case Management (UCM)",
    "    3.8 Information Delivery Manual (IDM)",
    "4. Cross-section — further relevant standards",
    "5. NIP suitability matrix",
    "6. Top candidates — sketches",
    "7. Roadmap proposal",
    "8. Sources",
]
for item in toc_items:
    story.append(P(item, body_left))
story.append(PageBreak())

# ---------- 1. Background ----------
story.append(H1("1. Background and method"))
story.append(P(
    "openBIM is the umbrella term for open, vendor-neutral data-exchange and "
    "coordination standards in construction, driven primarily by buildingSMART International "
    "(bSI) and complementary initiatives. The core standards are IFC (model schema), "
    "IDS (requirements schema), BCF (issue format), bSDD (data dictionary), as well as the "
    "openCDE bundle of REST APIs that specifies common-data-environment functions "
    "vendor-neutrally."))
story.append(P(
    "In parallel there is the community initiative <font color='#0b5394'>openBIMstandards.org</font> "
    "(github.com/openBIMstandards) as an &lsquo;Incubator for agile open BIM standards for the web&rsquo; "
    "— smaller repos for ifcOWL, BimJSON, property-set definitions and model checking. "
    "Activity there has been low since around 2020, but the concepts are conceptually close to "
    "what Nostr-native tooling needs: web-oriented, JSON-friendly, signable, "
    "federatable."))
story.append(P(
    "<b>Method of this study.</b> Each artefact is assessed against four dimensions:"))
story.append(bullets([
    "<b>Data-model fit</b> — can the standard be expressed in Nostr event form (signed JSON, "
    "tags, replaceable semantics) without losing essential semantics?",
    "<b>Identity and authorisation fit</b> — does the authorship model fit npub signatures "
    "and group/badge logic (NIP-29, NIP-58)?",
    "<b>File layer</b> — how is the binary component (IFC, snapshot, attachment) handled?",
    "<b>Decentralisation benefit</b> — is there a real advantage over the status quo "
    "(reduce centralisation, avoid platform lock-in, unlock new workflows)?",
]))
story.append(P(
    "Suitability is classified in three levels: "
    "<b>HIGH</b> (a NIP draft is worthwhile, benefit clear), "
    "<b>MEDIUM</b> (conceivable, but with compromises), "
    "<b>LOW</b> (Nostr is not the right layer here)."))
story.append(P(
    "<b>Scope boundary.</b> BCF was already covered in depth in a separate research document "
    "(BCF-over-Nostr NIP draft). Only a brief classification and "
    "references here."))
story.append(PageBreak())

# ---------- 2. openBIMstandards.org incubator ----------
story.append(H1("2. openBIMstandards.org — incubator inventory"))
story.append(P(
    "The GitHub organisation <font color='#0b5394'>openBIMstandards</font> comprises eight "
    "repos, several of them archived or inactive for years. Conceptually interesting for "
    "Nostr adaptations are three artefacts: ifcOWL, BimJSON and the PSD repository. "
    "modelcheckN3 and the Schependomlaan dataset are method/data showcases and "
    "not themselves objects of standardisation."))

story.append(standard_block(
    "ifcOWL",
    "RDF/OWL ontology variant of IFC, primarily for linked-data applications. "
    "SPARQL-capable, connected to the Semantic Web toolchain.",
    {"label": "LOW",
     "rationale": "Nostr events are JSON streams, not RDF triples. A "
     "full ontology as an event stream would incur high conversion loss "
     "and no practical benefit over the native triple-store stack."},
    None,
    "Different data philosophy (graph DB vs. append log). Reasoner logic not representable.",
    "No dedicated NIP. Touchpoint: JSON-LD in event.content would be "
    "conceivable for linked-data bridges — a generic kind plus "
    "specific tag conventions would suffice for that."))

story.append(standard_block(
    "BimJSON",
    "JSON communication-standard draft for online BIM tools (repo last active 2015). "
    "Idea: simple JSON exchange beyond IFC.",
    {"label": "MEDIUM",
     "rationale": "The format fits in principle, but has no notable "
     "adoption. Reactivation as a Nostr format would be reinvention rather than adaptation."},
    None,
    "Little mindshare, no current maintainer. Definition gaps in geometry and "
    "property sets.",
    "Do not continue standalone. Instead model IFC subset excerpts (e.g. just "
    "spatial structure + selected properties) as purpose-specific events "
    "where that makes sense."))

story.append(standard_block(
    "BIMbots PSD repository",
    "Repository and GraphQL server for Property Set Definitions (PSDs). PSDs are "
    "the templates that give values meaning in IFC (Pset_WallCommon, "
    "Pset_DoorWindow­Glazing­Type etc.).",
    {"label": "HIGH",
     "rationale": "PSDs are small, clearly structured records with their own GUID. "
     "Perfect for parameterized replaceable events: each publisher publishes their "
     "PSDs under their own npub, consumers subscribe selectively."},
    "<font face='Courier'>kind:30821</font> openBIM PSD, d=PSD-GUID. Fields: Name, "
    "DefiningValue, ApplicableClasses, PropertyDefinitions[]. Reference to bSDD via URI tag.",
    "Conflict case of multiple PSD authors with the same name — solvable via namespaces "
    "(npub prefix).",
    "<b>Strong NIP candidate.</b> Small, clear, high practical benefit. Can exist "
    "independently of bSDD and later converge with a bSDD NIP."))

story.append(standard_block(
    "modelcheckN3",
    "Model validation via Notation3 rules on ifcOWL.",
    {"label": "LOW",
     "rationale": "Semantic Web toolchain, same argument as ifcOWL."},
    None,
    "Different data philosophy.",
    "No dedicated NIP."))

story.append(standard_block(
    "Archive-DataSetSchependomlaan",
    "Classic test dataset with IFC + associated data — a methodological showcase, "
    "not a standard.",
    {"label": "N/A", "rationale": "Not a standard, not a NIP subject."},
    None, None,
    "Use as a test vector for IFC and IDS adaptation PoCs."))

story.append(PageBreak())

# ---------- 3. buildingSMART Portfolio ----------
story.append(H1("3. buildingSMART portfolio in detail"))

# 3.1 IFC
story.append(H2("3.1 Industry Foundation Classes (IFC)"))
story.append(rating_chip("LOW (at entity level) / HIGH (at file level)"))
story.append(gap(4))
story.append(P(
    "<b>What it is.</b> A schema-based data model for buildings — STEP physical file "
    "(.ifc), ifcXML, ifcJSON and ifcOWL serialisations. Currently IFC 4.3 as "
    "ISO 16739-1:2024, with IFC 4.4 in preparation (extensions for water/tunnel/industry) "
    "and discussion of IFC 5. Thousands of entity types, geometry + alphanumerics, "
    "typical model size from a few hundred MB to several GB."))
story.append(P(
    "<b>NIP suitability.</b> At entity level (each IfcWall, IfcDoor etc. as its own event) "
    "<b>clearly unsuitable</b>: millions of events per real project, write load, "
    "indexing effort, relay load. At file level (whole model as a blob plus "
    "a metadata event) <b>well suited</b>: fits NIP-94 + Blossom hash + optionally "
    "kind:30904 BCF file reference (see BCF doc) and/or an OpenTimestamps anchor on the "
    "timechain for a notary function. Subset level (e.g. just spatial structure as a treemap "
    "event) would be conceivable for federated model overviews, but is not "
    "standardised and is research rather than NIP material."))
story.append(P(
    "<b>Recommendation.</b> No dedicated IFC NIP. Instead: generic "
    "<font face='Courier'>kind:1063</font> NIP-94 file-metadata events with "
    "IFC-specific tags (<font face='Courier'>schema=IFC4X3</font>, "
    "<font face='Courier'>ifc-project</font>, <font face='Courier'>ifc-site</font>, "
    "<font face='Courier'>ifc-building</font>). Provenance, signature and versioning "
    "follow from the file-reference event."))
story.append(gap(6))

# 3.2 IDS
story.append(H2("3.2 Information Delivery Specification (IDS)"))
story.append(rating_chip("VERY HIGH"))
story.append(gap(4))
story.append(P(
    "<b>What it is.</b> A final bSI standard as IDS 1.0 since June 2024. An XML/XSD-based "
    "format for the computer-interpretable definition of information requirements that "
    "can be checked automatically against IFC models. An IDS file contains "
    "<font face='Courier'>ids:info</font> (Title, Version, Author, Date, Description, "
    "Copyright, IfcVersion, Milestone, License, Purpose) and an "
    "<font face='Courier'>ids:specifications</font> block; per specification an "
    "applicability condition (Entity, Attribute, Classification, Property, Material, "
    "PartOf) plus requirements with cardinality."))
story.append(P(
    "<b>NIP suitability.</b> Very high. IDS files are small (typically a few kB), structured, "
    "have meaningful authorship (client, AHJ, lead designer), unambiguous versions "
    "and are exactly the use case where signed, replicable, versioned events "
    "add value: requirements are published publicly signed, contractors "
    "subscribe, automatic checkers consume."))
story.append(P("<b>Event proposal.</b>"))
story.append(Paragraph(
    "kind:30810 — openBIM IDS Specification (parameterized replaceable, d=spec-guid)<br/>"
    "tags: a (project), ids-version, ifc-version, milestone, status (Draft/Final), "
    "purpose, t (mandatory tags per domain)<br/>"
    "content: JSON representation of the IDS specifications, or the original "
    "ids-XML content 1:1 — round-trip capable.<br/>"
    "<br/>"
    "kind:1180 — IDS Validation Result (regular, immutable)<br/>"
    "tags: e (IDS event), e (IFC file event), x (sha256 of the report), result (pass/fail), "
    "p (validator npub)<br/>"
    "content: summary; full report as a NIP-94 companion event.",
    code))
story.append(P(
    "<b>Gaps / problems.</b> IDS references bSDD URIs for properties — these must "
    "remain resolvable (a mirror cache is advisable). IDS version upgrades (1.0 → 1.1 → "
    "2.0) need clear migration notes in the NIP."))
story.append(P(
    "<b>Recommendation.</b> <b>First-class NIP candidate.</b> Small, powerful, "
    "decentrally publishable — also fits politically with the idea that client requirements "
    "should not be hidden in proprietary portals. An ideal extension of the BCF NIP: "
    "the IDS NIP defines requirements, the BCF NIP documents violations/topics."))
story.append(gap(6))

# 3.3 BCF
story.append(H2("3.3 BIM Collaboration Format (BCF)"))
story.append(rating_chip("HIGH"))
story.append(gap(4))
story.append(P(
    "<b>What it is.</b> A standard for issue and coordination communication in BIM "
    "projects. BCF-XML 3.0 (container .bcfzip) and the BCF API. Topics, comments, "
    "viewpoints, snapshots, IFC element references."))
story.append(P(
    "<b>NIP suitability.</b> High. Already worked out separately as a BCF-over-Nostr "
    "NIP draft — event kinds 30900–30904 (Topic, Viewpoint, Project, Document Ref, "
    "File Ref) plus 1170–1172 (Comment, Audit, Reaction)."))
story.append(P(
    "<b>Recommendation.</b> A standalone NIP, running in parallel to the IDS NIP. Cross-references "
    "between IDS validation-result events and BCF topic events are the natural "
    "bridge (failed validation → automatic BCF topic)."))
story.append(gap(6))

# 3.4 bSDD
story.append(H2("3.4 buildingSMART Data Dictionary (bSDD)"))
story.append(rating_chip("HIGH (conceptually) / MEDIUM (practically)"))
story.append(gap(4))
story.append(P(
    "<b>What it is.</b> A central database for classifications, classes, properties, "
    "values and their translations. REST API. URI-based identity "
    "(<font face='Courier'>https://identifier.buildingsmart.org/uri/...</font>). "
    "Classification systems (Uniclass, OmniClass, ETIM and many more) are maintained there."))
story.append(P(
    "<b>NIP suitability.</b> Conceptually very fitting — federated, signed definitions "
    "are exactly the discipline in which Nostr shines. Practically the value depends on "
    "the consensus layer: a dictionary without a curated single source loses its "
    "purpose. A workable model: each publisher (manufacturer, association, chamber) "
    "publishes their classes under their own npub; consumers choose whom to follow, "
    "aggregator relays deliver curated views."))
story.append(P("<b>Event proposal.</b>"))
story.append(Paragraph(
    "kind:30820 — bSDD Classification System (d=URI)<br/>"
    "kind:30821 — bSDD Class (d=URI)  // here convergent with the BIMbots PSD repository<br/>"
    "kind:30822 — bSDD Property (d=URI)<br/>"
    "kind:30823 — bSDD Value List (d=URI)<br/>"
    "tags: lang (multilingual), version, parent (URI of the parent system), "
    "ifc-mapping (Pset_xyz or directly IfcEntity)<br/>"
    "content: JSON with all localised labels, definitions, synonyms, "
    "units, applicable IFC domain.",
    code))
story.append(P(
    "<b>Gaps / problems.</b> Conflict resolution for competing definitions. "
    "URI preservation when mirroring onto Nostr. Performance with a large class corpus "
    "(Uniclass with tens of thousands of classes → correspondingly many events, index load)."))
story.append(P(
    "<b>Recommendation.</b> A NIP draft makes sense, but first a smaller scope (the PSD repository, "
    "see the 3.4 relatives from section 2) as a preliminary study. A full bSDD mirror as phase 2."))
story.append(gap(6))

# 3.5 openCDE
story.append(H2("3.5 openCDE initiative (Foundation, Documents, Dictionary, BCF APIs)"))
story.append(rating_chip("HIGH"))
story.append(gap(4))
story.append(P(
    "<b>What it is.</b> A bundle of REST APIs as a vendor-neutral CDE-layer spec. "
    "Foundation API (auth, sessions, projects, users), Documents API (documents, "
    "versions, metadata), Dictionary API (connection to bSDD), BCF API (issue tracking)."))
story.append(P("<b>NIP suitability per API.</b>"))
story.append(bullets([
    "<b>Foundation API → HIGH.</b> Projects as <font face='Courier'>kind:30902</font> "
    "(see BCF doc), users as npub with a profile event (NIP-01 kind:0), auth via "
    "NIP-42, authorisation via NIP-29 group membership. A direct replacement at the "
    "protocol level is possible.",
    "<b>Documents API → HIGH.</b> Document records as parameterized replaceable "
    "events (<font face='Courier'>kind:30930</font> openBIM Document Record), files via "
    "NIP-94 + Blossom, versioning via re-publishing the same d-tag, "
    "lifecycle status (WIP/Shared/Published/Archive per ISO 19650) as the tag "
    "<font face='Courier'>iso19650-state</font>.",
    "<b>Dictionary API → HIGH (via the bSDD NIP, see 3.4).</b>",
    "<b>BCF API → HIGH (via the BCF NIP, see 3.3).</b>",
]))
story.append(P(
    "<b>Recommendation.</b> Instead of four separate NIPs, one <b>openCDE bridge NIP</b>: "
    "defines an HTTP adapter pattern that maps openCDE API endpoints onto Nostr events. "
    "This keeps existing tools (ACC, Bimcollab, Solibri) usable without "
    "Nostr patches — the adapter terminates REST on the outside, Nostr on the inside. "
    "A transitional solution with high practical value."))
story.append(P("<b>Event proposal for Documents.</b>"))
story.append(Paragraph(
    "kind:30930 — openBIM Document Record (parameterized replaceable, d=document-guid)<br/>"
    "tags: a (project), iso19650-state (WIP|Shared|Published|Archive), "
    "title, mime, version, x (sha256), url (Blossom), revision, "
    "supersedes (event-id of an earlier record, optional), p (responsible person)<br/>"
    "content: JSON with description, metadata, classification refs.",
    code))
story.append(gap(6))

# 3.6 Validation Service
story.append(H2("3.6 IFC Validation Service"))
story.append(rating_chip("HIGH"))
story.append(gap(4))
story.append(P(
    "<b>What it is.</b> A free central online validator from bSI; checks IFC files "
    "against schema, implementer agreements and MVDs, delivers a structured report. "
    "Currently run as a Strategic Project."))
story.append(P(
    "<b>NIP suitability.</b> High as a Data Vending Machine (NIP-90). Validation is a "
    "well-defined service function with a clear input/output form — a perfect "
    "DVM use case. Several independent validator providers can compete, "
    "a reputation layer emerges from result history and tag/review volume."))
story.append(P("<b>Event proposal.</b>"))
story.append(Paragraph(
    "kind:5901 — IFC Validation Job Request (NIP-90 input)<br/>"
    "tags: i (IFC URL + sha256), schema (IFC4|IFC4X3|IFC4X4), "
    "ids-ref (event-id of an IDS spec, optional), bid (max sats)<br/>"
    "<br/>"
    "kind:6901 — IFC Validation Job Result (NIP-90 output)<br/>"
    "tags: e (request event), result (pass|fail|warning), "
    "report-url, x (sha256 of the report), summary (number of errors/warnings)<br/>"
    "content: JSON summary; full-text report via a NIP-94 companion event.",
    code))
story.append(P(
    "<b>Recommendation.</b> <b>Clear NIP candidate.</b> Combined with the IDS NIP this "
    "creates a decentralised QA network: the client publishes the IDS, the contractor publishes "
    "the IFC + a validator order, several validators bid, the best/fastest "
    "wins, all results are signed and verifiable."))
story.append(gap(6))

# 3.7 UCM
story.append(H2("3.7 Use Case Management (UCM)"))
story.append(rating_chip("HIGH"))
story.append(gap(4))
story.append(P(
    "<b>What it is.</b> An online service for capturing and exchanging use cases — "
    "application scenarios for openBIM workflows with associated IDS/IDM, "
    "domain context, stakeholders, information-exchange schema. Service at "
    "ucm.buildingsmart.org."))
story.append(P(
    "<b>NIP suitability.</b> High. Use-case records are pure metadata objects with "
    "structured fields, well representable as parameterized replaceable events."))
story.append(P("<b>Event proposal.</b>"))
story.append(Paragraph(
    "kind:30840 — openBIM Use Case (parameterized replaceable, d=usecase-id)<br/>"
    "tags: t (domain), stage (construction phase), stakeholders (multiple), "
    "ids-ref, idm-ref, lang<br/>"
    "content: JSON per the UCM data model (title, description, motivation, "
    "preconditions, steps, outcomes, KPIs).",
    code))
story.append(P(
    "<b>Recommendation.</b> A nice secondary NIP — low risk, immediately productive, "
    "can start independently of IDS/BCF and cross-link later."))
story.append(gap(6))

# 3.8 IDM
story.append(H2("3.8 Information Delivery Manual (IDM)"))
story.append(rating_chip("MEDIUM"))
story.append(gap(4))
story.append(P(
    "<b>What it is.</b> A bSI standard for describing business processes and "
    "information requirements that later become technically concrete in IFC and IDS. "
    "BPMN-oriented, rather text-heavy."))
story.append(P(
    "<b>NIP suitability.</b> Medium. IDMs are structured documents, but their value "
    "lies heavily in diagrams and explanations — rather classic publishing. "
    "NIP-23 long-form content (kind:30023) would be sufficient, without a dedicated NIP."))
story.append(P(
    "<b>Recommendation.</b> No dedicated NIP. Use NIP-23 instead, with convention "
    "tags <font face='Courier'>idm-domain</font>, <font face='Courier'>process-bpmn</font> "
    "(hash of the stored BPMN), <font face='Courier'>ifc-version</font>."))
story.append(PageBreak())

# ---------- 4. Cross-section ----------
story.append(H1("4. Cross-section — further relevant standards"))
story.append(P(
    "Beyond the bSI core range there are adjacent standards that, in "
    "practical operation, appear together with IFC/IDS/BCF and should likewise be "
    "assessed for NIP suitability."))

story.append(standard_block(
    "LOIN (DIN EN 17412-1:2020)",
    "Level of Information Need. Defines geometric, alphanumeric and "
    "documentation granularity per information requirement. Established in Germany and "
    "EU-wide as a method for information requirements.",
    {"label": "HIGH",
     "rationale": "Structured metadata, clearly versionable, often closely tied to IDS "
     "and Pset specifications. Ideal as a parameterized replaceable event."},
    "<font face='Courier'>kind:30811</font> openBIM LOIN Definition, d=loin-id. "
    "Tags: a (project), purpose, milestone, ids-ref. content: JSON with the three "
    "LOIN axes.",
    "Keep the interlocking with IDS clean — proposal: the LOIN event references the IDS event, "
    "not the other way around, because LOIN conceptually comes before IDS.",
    "Think of it together with IDS — lends itself to a joint NIP or a closely cooperating "
    "follow-on NIP."))

story.append(standard_block(
    "COBie",
    "Construction-Operations Building Information Exchange. A spreadsheet- or "
    "ifcXML-based handover format for FM data.",
    {"label": "LOW",
     "rationale": "A file format, not a protocol. Handover character (one-off "
     "transfer), no ongoing collaboration."},
    None,
    "Contents are tabular, belong stored as a whole file via NIP-94 + Blossom, "
    "not squeezed into an event schema.",
    "No dedicated NIP. A generic file layer is enough."))

story.append(standard_block(
    "Product Data Templates (ISO 23387, ISO 23386)",
    "Templates for manufacturer product data — structured, multilingual property sets "
    "per product class. The EU Construction Products Regulation (CPR) and the Digital Product Passport "
    "drastically increase the relevance.",
    {"label": "HIGH",
     "rationale": "Manufacturer-signed product data fits npub identity perfectly. "
     "The EU DPP obligation from 2027 makes the use case highly topical. A touchpoint with the "
     "material-passport concept drafted in an earlier discussion."},
    "<font face='Courier'>kind:30850</font> openBIM Product Data Template, d=template-id. "
    "Tags: manufacturer-npub, classification-uri (bSDD), product-category, "
    "lang, valid-from, valid-to. content: JSON per the ISO 23387 data model.",
    "Versioning and revocation on product change — analogous to NIP-58 badge revoke via "
    "NIP-09 delete.",
    "<b>Very strong candidate</b>, because regulatory anchoring (CPR, EU DPP) is now "
    "happening and manufacturers are in motion."))

story.append(standard_block(
    "ISO 19650",
    "A process standard for CDE operation and information management. Defines "
    "states (WIP / Shared / Published / Archive), roles, workflows.",
    {"label": "MEDIUM",
     "rationale": "A process, not a schema. Not directly representable, but very "
     "useful as a tag convention (see 3.5)."},
    None,
    "A workflow engine would be a separate large task — does not belong in the NIP core.",
    "Integrate the tag convention <font face='Courier'>iso19650-state</font> into the Documents/BCF NIP. "
    "No dedicated NIP."))

story.append(standard_block(
    "DIN SPEC 91357 / EN ISO 16484 (BACnet etc.)",
    "Building-automation and twin standards for measurement/control/regulation data. "
    "An operational data layer alongside the static IFC.",
    {"label": "HIGH",
     "rationale": "Publishing live sensor data signed via npub is exactly the "
     "area where Nostr plays out its streaming character. Connects to "
     "ESG/EPBD-recast monitoring (EU Directive 2024/1275)."},
    "<font face='Courier'>kind:1230</font> Building Telemetry (regular, ephemeral-affine). "
    "Tags: device-id (couplable to IfcGUID), unit, point-type, project. content: "
    "compact JSON payload (timestamp, value, quality).",
    "High frequency → relay load. Optional aggregation events (1 min / 1 h average).",
    "A dedicated NIP <b>HVAC telemetry</b> makes sense, couples directly to the HVAC twin "
    "project idea from the Sovereign Engineering roadmap."))

story.append(PageBreak())

# ---------- 5. Matrix ----------
story.append(H1("5. NIP suitability matrix"))
story.append(P(
    "A synoptic view. Sorted by NIP suitability descending. The effort column "
    "estimates roughly: S = one weekend, M = a few weeks, L = several months."))

matrix = [
    ["Standard", "Suitability", "Event kind (proposal)", "Effort", "Killer use case"],
    ["IDS",                       "Very high", "30810 + 1180",          "M", "Sovereign client requirements"],
    ["BCF",                       "High",      "30900–30904 / 1170–72", "M", "Coordination issues without a platform"],
    ["Validation Service",        "High",     "5901 / 6901 (NIP-90)",   "M", "Decentralised QA network"],
    ["Documents (openCDE)",       "High",     "30930",                  "M", "ISO 19650-compliant doc distribution"],
    ["Foundation (openCDE)",      "High",     "—  (NIP-29 + 30902)",   "S", "Project container without a server"],
    ["Use Case Management",       "High",     "30840",                  "S", "Federated use-case library"],
    ["PSD (BIMbots repo)",        "High",     "30821",                  "S", "Manufacturer Pset distribution"],
    ["Product Data Templates",    "High",     "30850",                  "M", "EU DPP connection"],
    ["LOIN (EN 17412)",           "High",     "30811",                  "S", "LOIN as a signed requirement block"],
    ["bSDD",                      "Medium",   "30820–30823",            "L", "Federated data dictionary"],
    ["Telemetry (BACnet bridge)", "High",     "1230",                   "M", "ESG/EPBD monitoring"],
    ["IDM",                       "Medium",   "30023 (NIP-23)",         "S", "Process docs in long-form"],
    ["IFC (file level)",          "High",     "1063 (NIP-94)",          "S", "Model provenance, OTS anchor"],
    ["IFC (entity level)",        "Low",      "—",                       "L", "—"],
    ["ifcOWL",                    "Low",      "—",                       "—", "—"],
    ["BimJSON",                   "Low",      "—",                       "—", "—"],
    ["COBie",                     "Low",      "1063 (NIP-94)",          "S", "Handover attachment"],
    ["ISO 19650",                 "Medium",   "Tag convention",         "S", "States across all NIPs"],
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
# color-code suitability cell
for i, row in enumerate(matrix[1:], start=1):
    rating = row[1].lower()
    if rating in ("very high", "high"):
        c = HIGH
    elif rating == "medium":
        c = MID
    else:
        c = LOW
    tbl_style.append(("TEXTCOLOR", (1,i), (1,i), c))
    tbl_style.append(("FONT", (1,i), (1,i), "Helvetica-Bold", 9))
tbl.setStyle(TableStyle(tbl_style))
story.append(tbl)
story.append(gap(8))
story.append(P(
    "<b>Observation.</b> Suitability concentrates on a small group of "
    "metadata-driven standards (IDS, BCF, UCM, LOIN, PSD/PDT) plus a "
    "DVM-capable service layer (Validation). Model data (IFC) and linked-data "
    "constructs (ifcOWL) are the weakest candidates — which is logical: Nostr "
    "is an event-stream protocol, not a graph store and not a BLOB layer."))

story.append(PageBreak())

# ---------- 6. Top-Kandidaten ----------
story.append(H1("6. Top candidates — sketches"))
story.append(P(
    "Three standards form a coherent minimum viable set that already delivers "
    "value on its own and mutually reinforces: <b>IDS</b>, <b>BCF</b> and "
    "<b>Validation</b>. Plus a fourth, regulatorily strong anchor: <b>Product Data "
    "Templates</b>."))

story.append(H3("6.1 IDS NIP — sovereign requirements"))
story.append(bullets([
    "<b>Scope.</b> Publish IDS 1.0 specs as parameterized replaceable events, "
    "subscribable, signed.",
    "<b>Event kinds.</b> 30810 (spec), 1180 (validation result).",
    "<b>File layer.</b> Inline ids-XML in content for small specs (&lt; 16 kB), otherwise "
    "a Blossom reference + NIP-94.",
    "<b>Authorisation.</b> Publicly publishable; mandatory IDS within a project "
    "via a NIP-29 group channel.",
    "<b>MVP.</b> CLI <font face='Courier'>ids2nostr</font> + web viewer feasible in 2–3 "
    "weeks.",
    "<b>Ecosystem synergy.</b> Connects seamlessly to the BCF NIP: failed validation → "
    "automatic BCF topic with cross-reference.",
]))

story.append(H3("6.2 Validation NIP — DVM for IFC audit"))
story.append(bullets([
    "<b>Scope.</b> IFC validation as a service via NIP-90 (Data Vending Machine).",
    "<b>Event kinds.</b> 5901 (request), 6901 (result), 7000 (payment/feedback).",
    "<b>Providers.</b> Initially 1–2 validators (e.g. the bSI service as a bot, an "
    "independent instance based on the IfcOpenShell validator).",
    "<b>Payment.</b> Lightning, LNbits or the Cashu mint of the DVM operator.",
    "<b>Ecosystem synergy.</b> Consumes IDS specs (3.1) and produces BCF topics (3.3) "
    "on errors. This is the loop that closes a complete openBIM QA workflow without "
    "a central platform.",
]))

story.append(H3("6.3 PDT NIP — product data at the DPP connection"))
story.append(bullets([
    "<b>Scope.</b> Manufacturer property sets as signed events, connectable to ISO 23387 / 23386 "
    "and the EU Digital Product Passport (Regulation 2024/1781, ESPR).",
    "<b>Event kinds.</b> 30850 (template), optionally 30851 (batch/lot-specific data sheet).",
    "<b>Authorisation.</b> Manufacturer npub with a NIP-58 badge from an accredited body.",
    "<b>Practice.</b> Connection to the material-passport concept from the Sovereign Engineering set: "
    "each component gets a PDT reference, can be disassembled and traded.",
    "<b>Political leverage.</b> The EU DPP obligation from 2027 for construction materials is in preparation — "
    "whoever specifies a sovereign alternative now is non-trivially ahead.",
]))

story.append(H3("6.4 Documents NIP — openCDE light"))
story.append(bullets([
    "<b>Scope.</b> Document records (drawings, reports, spec sheets) with versioning and "
    "ISO 19650 state.",
    "<b>Event kind.</b> 30930.",
    "<b>File layer.</b> Blossom + NIP-94.",
    "<b>MVP effort.</b> A weekend project for the core, because it is semantically close to "
    "classic file stores.",
    "<b>Ecosystem synergy.</b> Complements the BCF NIP (issue links a document), "
    "the IDS NIP (specification links referenced documents).",
]))

story.append(PageBreak())

# ---------- 7. Roadmap ----------
story.append(H1("7. Roadmap proposal"))
story.append(P(
    "Order by effort and traction. Phase 1 produces visible results "
    "in 6–8 weeks, phase 2 extends to the full workflow, phase 3 opens up the "
    "regulatory and service-oriented layer."))

story.append(H3("Phase 1 — quick wins (weeks 1–8)"))
story.append(bullets([
    "BCF NIP draft + reference implementation (in progress separately).",
    "IDS NIP draft (kind 30810) + CLI ids2nostr, a demonstrable web viewer.",
    "UCM NIP draft (kind 30840) — smallest risk, quickly publishable as a bSI use-case "
    "mirror.",
    "Documents NIP (kind 30930) as the basis for CDE-lite.",
]))

story.append(H3("Phase 2 — closing the workflow (weeks 9–16)"))
story.append(bullets([
    "Validation NIP (NIP-90 DVM for IFC) — couples IDS + BCF.",
    "LOIN event convention (kind 30811) as an annex to the IDS NIP.",
    "openCDE HTTP adapter: existing tools speak openCDE REST, the adapter terminates "
    "on Nostr events. A transition path for classic BIM teams.",
]))

story.append(H3("Phase 3 — regulation and service layer (weeks 17–28)"))
story.append(bullets([
    "PDT NIP (kind 30850) with ISO 23387/23386 and EU DPP connection; "
    "connection to the material-passport concept.",
    "bSDD NIP (phase 1: classes + properties) — a federated mirror with "
    "a curator-view filter.",
    "HVAC telemetry NIP (kind 1230) for live data from building operation, couples "
    "to ESG/EPBD reporting.",
]))

story.append(H3("Across all phases"))
story.append(bullets([
    "Consensus sounding in the bSI open-source community for each draft, before "
    "the final spec is frozen.",
    "PRs against <font face='Courier'>nostr-protocol/nips</font> with kind-range "
    "reservations.",
    "Test vectors from official bSI repositories for round-trip conformance.",
    "Practical validation on an own construction or renovation project — minimal risk, "
    "a fast reality check.",
]))

story.append(PageBreak())

# ---------- 8. Sources ----------
story.append(H1("8. Sources"))
sources = [
    ("openBIMstandards.org / GitHub", "http://openbimstandards.org/ — github.com/openBIMstandards"),
    ("buildingSMART openBIM overview", "https://www.buildingsmart.org/about/openbim/"),
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
story.append(P("<i>End of the research document. Corrections, additions and PRs welcome.</i>", muted))

# ---------- Build ----------
doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
print(f"OK: {OUTPUT}")
