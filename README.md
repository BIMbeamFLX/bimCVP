# Gemeinwert / BIM-CVP

**BIM-CVP** is the Common Value Protocol for signed openBIM coordination records.
**Gemeinwert** is the public brand around it.

The project defines a static information website, a structured wiki and an event
model for mapping openBIM workflows to signed Nostr events. The goal is simple:
coordination records should be portable, verifiable and independent from one
software tenant.

## What This Repository Contains

```text
.
├── site/       Static website. Deploy this folder as the web root.
├── modules/    Embeddable browser components for Nostr/BIM-CVP workflows.
├── docs/       Source documentation, standards notes and architecture docs.
├── app/        Local development tools and older HTML prototypes.
├── tools/      CLI utilities for ingest and verification workflows.
├── skills/     Local IFC/IDS audit and classification helpers.
└── ifc/        Local project data placeholder. Real model data is gitignored.
```

The public website is intentionally static. It can be served by any normal web
server, object storage bucket, CDN or GitHub Pages.

## Website

The deployable website lives in [`site/`](site/).

Key entry points:

- [`site/en/index.html`](site/en/index.html) - product-style landing page.
- [`site/en/bim-cvp.html`](site/en/bim-cvp.html) - protocol framing.
- [`site/en/standards.html`](site/en/standards.html) - pinned standards profile.
- [`site/wiki/index.html`](site/wiki/index.html) - structured wiki index.
- [`site/wiki/nostr-mapping/bcf-events.html`](site/wiki/nostr-mapping/bcf-events.html) - BCF to Nostr event mapping.
- [`site/wiki/nostr-mapping/workflow.html`](site/wiki/nostr-mapping/workflow.html) - theoretical end-to-end workflow.
- [`site/wiki/nostr-mapping/alice-bob-max.html`](site/wiki/nostr-mapping/alice-bob-max.html) - worked data-sharing example.

The root [`site/index.html`](site/index.html) redirects to `/en/`.

## Deploy

### Static Web Server

Copy the contents of `site/` to the web server root:

```text
site/index.html
site/en/
site/wiki/
site/assets/
site/docs/
```

No build step is required.

### GitHub Pages

The workflow in [`.github/workflows/pages.yml`](.github/workflows/pages.yml)
uploads `site/` as the Pages artifact.

Repository setup:

1. Open GitHub repository settings.
2. Go to **Pages**.
3. Set source to **GitHub Actions**.
4. Merge to `main`.

The workflow deploys on pushes to `main` when files under `site/**` or the Pages
workflow change.

## Protocol Frame

BIM-CVP keeps existing openBIM standards in place:

| Layer | Standard | Role |
| --- | --- | --- |
| Model | IFC 4.3.2.0 | Building model and object identity. |
| Coordination | BCF 3.0 | Topics, comments, viewpoints and issue state. |
| Requirements | IDS 1.0 | Machine-checkable information requirements. |
| Process | ISO 19650 | Information states, responsibility and approval. |
| Vocabulary | bSDD | Stable classification and property identifiers. |
| Integration | openCDE | Boundary to existing CDE/document systems. |
| Transport | Nostr | Signed events, portable identity and relay distribution. |

BIM-CVP does not replace authoring tools, CDEs or buildingSMART standards. It
adds the missing signed record layer around them.

## Modules

The `modules/` folder contains embeddable browser components for BIM-CVP
workflows. These components are separate from the public website and can be used
by other sites when they need signing, relay publishing or BCF-style interaction.

```html
<script type="module" src="./modules/nostr-cvp/index.js"></script>
```

See [`modules/nostr-cvp/README.md`](modules/nostr-cvp/README.md) for component
usage.

## Local Preview

From the repository root:

```bash
python -m http.server 8765 -d site
```

Open:

```text
http://localhost:8765/en/
```

## Development Checks

The site is static, so the main checks are link integrity, HTTP responses and
JavaScript syntax for the embeddable module.

```bash
node --check modules/nostr-cvp/index.js
git diff --check
```

For a local smoke test, serve `site/` and check:

```text
/en/
/en/bim-cvp.html
/en/pilot.html
/wiki/
/wiki/nostr-mapping/alice-bob-max.html
/wiki/nostr/basics.html
```

## Documentation

Core docs:

- [`docs/PRINCIPLES.md`](docs/PRINCIPLES.md)
- [`docs/BRAND.md`](docs/BRAND.md)
- [`docs/STANDARDS-PROFILE.md`](docs/STANDARDS-PROFILE.md)
- [`docs/KIND-REGISTRY.md`](docs/KIND-REGISTRY.md)
- [`docs/bcf-nostr-nip-research.md`](docs/bcf-nostr-nip-research.md)
- [`docs/BACKEND-SETUP.md`](docs/BACKEND-SETUP.md)
- [`docs/identity-architecture.md`](docs/identity-architecture.md)

The canonical public reading surface is the static website under `site/`.

## License

MIT. See [`LICENSE`](LICENSE).

Content is intended to be reusable with attribution where appropriate.

## Contact

Project and provider context: [www.bimbeam.at](https://www.bimbeam.at)
