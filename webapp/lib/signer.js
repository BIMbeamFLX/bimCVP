// signer.js — Tier-1 ONLY: NIP-46 remote signer (the bunker).
// The user's Nostr secret key lives server-side in the bunker. This app never
// sees, stores, or displays an nsec/hex/npub. It holds only:
//   - an ephemeral CLIENT transport key (for the NIP-46 channel, not identity)
//   - the bunker connect URI (a capability token issued by provision/login)
// Both are session-scoped (sessionStorage) and cleared on disconnect.
//
// No window.nostr, no throwaway localStorage key (that v1 was rejected):
// managed identity is the whole point.

import { BunkerSigner, parseBunkerInput } from "https://esm.sh/nostr-tools@2.10.4/nip46";
import { generateSecretKey } from "https://esm.sh/nostr-tools@2.10.4/pure";
import { bytesToHex, hexToBytes } from "https://esm.sh/@noble/hashes@1.4.0/utils";

const SS_URI = "bimcvp.bunker_uri";
const SS_CSK = "bimcvp.bunker_csk"; // client transport key (NOT the identity key)

let signer = null;
let cachedPub = null;

function loadClientKey() {
  let hex = sessionStorage.getItem(SS_CSK);
  if (!hex) {
    hex = bytesToHex(generateSecretKey());
    sessionStorage.setItem(SS_CSK, hex);
  }
  return hexToBytes(hex);
}

// connect(bunkerUri): establish the NIP-46 session from a connect URI/token
// (provision issues this after email login — never an nsec).
export async function connect(bunkerUri) {
  const uri = (bunkerUri || sessionStorage.getItem(SS_URI) || "").trim();
  if (!uri) throw new Error("no bunker connection");
  const pointer = await parseBunkerInput(uri);
  if (!pointer) throw new Error("invalid bunker connection");
  const csk = loadClientKey();
  signer = new BunkerSigner(csk, pointer);
  await signer.connect();
  cachedPub = await signer.getPublicKey();
  sessionStorage.setItem(SS_URI, uri);
  return true;
}

// Restore a session on reload (if a bunker URI is still in sessionStorage).
export async function restore() {
  if (!sessionStorage.getItem(SS_URI)) return false;
  try { await connect(); return true; } catch { return false; }
}

export function isConnected() {
  return !!signer && !!cachedPub;
}

// getPublicKey() -> hex (consumed by bcf.js to stamp the event; never shown raw in UI)
export async function getPublicKey() {
  if (!signer) throw new Error("not connected");
  return cachedPub || (cachedPub = await signer.getPublicKey());
}

// signEvent(unsigned) -> signed event. Signing happens IN the bunker.
export async function signEvent(unsigned) {
  if (!signer) throw new Error("not connected");
  return signer.signEvent(unsigned);
}

export function disconnect() {
  try { signer && signer.close && signer.close(); } catch {}
  signer = null;
  cachedPub = null;
  sessionStorage.removeItem(SS_URI);
  sessionStorage.removeItem(SS_CSK);
}
