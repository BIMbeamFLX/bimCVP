// bcf.js — exact kind:30900 BCF Topic build / validate / parse.
// Pure: no network, no DOM. Binding spec: docs/KIND-REGISTRY.md.
// (Default value lists; confirm against docs/STANDARDS-PROFILE.md if extended.)

export const STATUSES   = ["Open", "InProgress", "Resolved", "Closed"];
export const TYPES      = ["Issue", "Clash", "RFI", "Information", "Decision"];
export const PRIORITIES = ["Low", "Normal", "High", "Critical"];

const A_RE = /^30902:[0-9a-f]{64}:.+$/;

// buildTopicEvent(fields) -> unsigned Nostr event (kind 30900).
// One UUID v4 is used for d / bcf-guid / content.guid.
export function buildTopicEvent({
  projectRef, pubkey, title, description,
  status = "Open", type = "Issue", priority, dueDate, assigneePubkey
}) {
  if (!A_RE.test(projectRef || "")) throw new Error("invalid projectRef");
  if (!/^[0-9a-f]{64}$/.test(pubkey || "")) throw new Error("invalid pubkey");
  if (!title || !title.trim()) throw new Error("title required");
  if (!STATUSES.includes(status)) throw new Error("invalid status");
  if (!TYPES.includes(type)) throw new Error("invalid type");

  const guid = crypto.randomUUID();
  const nowIso = new Date().toISOString();
  const tags = [
    ["d", guid],
    ["a", projectRef],
    ["bcf-guid", guid],
    ["bcf-version", "3.0"],
    ["bcf-status", status],
    ["s", status],                         // REQUIRED indexed mirror == bcf-status
    ["bcf-type", type],
  ];
  if (priority && PRIORITIES.includes(priority)) tags.push(["bcf-priority", priority]);
  if (assigneePubkey && /^[0-9a-f]{64}$/.test(assigneePubkey)) tags.push(["p", assigneePubkey]);
  tags.push(["client", "bimcvp-webapp/1.0"]);

  const content = {
    title: title.trim(),
    description: (description || "").trim(),
    created_date: nowIso,
    created_author: pubkey,
  };
  if (dueDate) content.due_date = new Date(dueDate).toISOString();

  return {
    kind: 30900,
    created_at: Math.floor(Date.now() / 1000),
    pubkey,
    tags,
    content: JSON.stringify(content),
  };
}

// validateTopicEvent(ev) -> { valid:boolean, errors:string[] }
export function validateTopicEvent(ev) {
  const e = [];
  if (!ev || ev.kind !== 30900) e.push("kind != 30900");
  const tag = (k) => (ev.tags || []).find((t) => t[0] === k)?.[1];
  if (!tag("d")) e.push("missing d");
  if (!A_RE.test(tag("a") || "")) e.push("bad/missing a");
  if (tag("bcf-version") !== "3.0") e.push("bcf-version != 3.0");
  if (!tag("bcf-status")) e.push("missing bcf-status");
  if (tag("s") !== tag("bcf-status")) e.push("s != bcf-status");
  if (!tag("bcf-type")) e.push("missing bcf-type");
  try {
    const c = JSON.parse(ev.content || "{}");
    if (!c.title) e.push("content.title missing");
    if (!c.created_date) e.push("content.created_date missing");
  } catch { e.push("content not JSON"); }
  return { valid: e.length === 0, errors: e };
}

// parseTopic(ev) -> flat object for rendering (never exposes raw pubkey hex in UI)
export function parseTopic(ev) {
  const tag = (k) => (ev.tags || []).find((t) => t[0] === k)?.[1];
  let c = {};
  try { c = JSON.parse(ev.content || "{}"); } catch {}
  return {
    id: tag("d") || ev.id,
    title: c.title || "(untitled)",
    description: c.description || "",
    status: tag("bcf-status") || "Open",
    type: tag("bcf-type") || "Issue",
    priority: tag("bcf-priority") || "",
    createdDate: c.created_date || null,
    createdAt: ev.created_at || 0,
  };
}
