# nostr-cvp module

Embeddable Gemeinwert / BIM CVP widgets for static websites.

The module is intentionally framework-free:

- no build step
- no npm dependency
- NIP-07 first
- local preview without a relay
- optional relay publishing when `relays` is configured

## Quick embed

```html
<link rel="stylesheet" href="/modules/nostr-cvp/styles.css" />
<script type="module" src="/modules/nostr-cvp/index.js"></script>

<bcf-quickform
  project="30902:<owner-pubkey>:building-2026"
  relays="wss://relay.example.org"
></bcf-quickform>
```

## Element

### `<bcf-quickform>`

Creates a small signed BCF-topic event.

Attributes:

| Attribute | Required | Purpose |
| --- | --- | --- |
| `project` | yes | Project address written as the Nostr `a` tag, format `30902:<owner-pubkey>:<project-d>` |
| `relays` | no | Comma-separated relay URLs |
| `heading` | no | Visible form heading |

If no relay is configured, the component still signs the event and emits a
`bcf-quickform:signed` browser event. Host pages can store, inspect or forward it.

## Events

The component dispatches:

- `bcf-quickform:signed` with `{ event }`
- `bcf-quickform:published` with `{ event, results }`
- `bcf-quickform:error` with `{ error }`

## Policy

This module owns Nostr interaction only. It must not own the website layout, routing,
brand copy or documentation pages.
