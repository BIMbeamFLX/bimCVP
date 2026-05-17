# webapp — BIM CVP managed onboarding (v1)

Static, framework-free browser artifact. **Separate** from `site/` (own deploy,
later `app.bimcvp.com`). It supersedes the nsec-in-localStorage prototypes in
`app/` (do not use those).

## Principle

The user's Nostr key is **managed server-side** in the NIP-46 **bunker**. This
app **never** sees, stores, or shows an nsec / hex / npub. It only holds a
session-scoped bunker connect token + an ephemeral transport key
(`lib/signer.js`). Reads of the relay are open; signing happens in the bunker.

## Pages

| Page | Purpose |
|---|---|
| `join.html` | Self-enrol from a project code / QR (`?p=CODE`) + email + name → request join link |
| `check-email.html` | "open the one-time link" |
| `login.html` | Magic-link landing (`?token=`) → establish bunker session; or request a sign-in link by email |
| `recover.html` | Email → recovery link → regain access, **same identity** |
| `admin.html` | Project admin: create project (provision signs kind:30902), show code + QR, member list |
| `index.html` | Member home: live BCF-topic feed (open read) + publish a bunker-signed kind:30900 |

## provision API contract (the server must implement exactly this)

Base = `PROVISION_URL` (see `config.js`). JSON.

- `POST /api/enrol` `{projectCode,email,name}` → `202` (emails a one-time link;
  dev-stub logs it). Self-enrol into a project.
- `POST /api/login` `{email}` → `202` (emails a sign-in link).
- `POST /api/recover` `{email}` → `202` (emails a recovery link; **same npub**).
  Always returns 202 (no account-existence oracle).
- `GET /api/session?token=…` → `{ bunkerUri, sessionToken, role }`. One-time,
  short-lived token. `bunkerUri` = NIP-46 connect string to the user's key in
  the bunker. `sessionToken` = bearer for `/api/admin/*`. `role` ∈ {member,admin}.
- `POST /api/admin/project` (Bearer sessionToken, role=admin)
  `{title,description,address}` → `{ projectRef, projectCode }`. Provision
  creates+publishes the kind:30902 project event signed via the admin's bunker
  key, mints a join code.
- `GET /api/admin/members` (Bearer) → `[{name,project,status}]`.

On enrol, provision must also: generate the member key, store it encrypted
(operator key offline), register it in the bunker, create the LNbits user, and
create the member's `name@bimcvp.com` **nostrnip5** entry — the existing
`gen-allow.py` cron then adds the npub to the relay allowlist (≤2 min).

## Run locally

```
cd webapp && python -m http.server 8080
# open http://localhost:8080/
```
(Provision must run / be reachable at `PROVISION_URL`; until then onboarding
calls fail gracefully, but the open-read feed works against the live relay if a
project ref is set in `localStorage["bimcvp.project_ref"]`.)

## Deploy (later)

Static files; later mounted at `app.bimcvp.com` via Caddy. **Not** part of
`deploy-site.sh`. No secrets here — all secrets live server-side in the private
`backend-deploy/provision` service.
