// webapp config — endpoints + project reference helpers.
// Static, no secrets. The managed identity / keys live server-side (bunker);
// this app never sees an nsec.

export const RELAY_URL    = "wss://relay.bimcvp.com";   // public pilot relay (reads open)
export const PROVISION_URL = "https://app.bimcvp.com";  // provision API base (server-side glue); adjust when deployed
export const REGISTER_URL = "https://pay.bimcvp.com";   // LNbits (account / handle)

// Public read-only DEMO project ("Citadel"). Used as the feed fallback when no
// project is configured on the device, so visitors see real signed BCF events
// with zero setup. The pubkey is public (Alice = demo architect, managed
// identity); stable while the keystore volume persists. Pushed by
// provision/dryrun.py. NOT a secret.
export const DEMO_PROJECT_REF =
  "30902:85b543016290835cb4f0b5b6311259ee2caf49f1240bd317f96ab5705216c7f7:citadel-pilot-0001";

const PROJECT_KEY = "bimcvp.project_ref";
// A valid project ref is the addressable coordinate "30902:<64-hex-pubkey>:<id>".
const PROJECT_RE = /^30902:[0-9a-f]{64}:.+$/;

export function getProjectRef() {
  const v = (localStorage.getItem(PROJECT_KEY) || "").trim();
  return PROJECT_RE.test(v) ? v : "";
}

export function setProjectRef(ref) {
  const v = (ref || "").trim();
  if (!PROJECT_RE.test(v)) throw new Error("invalid project ref (expected 30902:<64hex>:<id>)");
  localStorage.setItem(PROJECT_KEY, v);
  return v;
}

export function clearProjectRef() {
  localStorage.removeItem(PROJECT_KEY);
}
