// relay.js — raw WebSocket Nostr client. No SDK relay layer (PRINCIPLES §1:
// thin glue). Separate sockets for publish vs subscribe so a rejected publish
// never tears down the readable feed.

// publish(url, signedEvent) -> { ok:boolean, reason:string }
// ok=true ONLY on ["OK", id, true, ""]. Any non-affirmative outcome
// (explicit false-OK, NOTICE, timeout, socket error) -> ok=false.
export function publish(url, ev, { timeoutMs = 7000 } = {}) {
  return new Promise((resolve) => {
    let done = false;
    const finish = (ok, reason) => {
      if (done) return;
      done = true;
      try { ws.close(); } catch {}
      resolve({ ok, reason: reason || "" });
    };
    let ws;
    try { ws = new WebSocket(url); } catch (e) { return finish(false, "socket error"); }
    const t = setTimeout(() => finish(false, "timeout"), timeoutMs);
    ws.onopen = () => ws.send(JSON.stringify(["EVENT", ev]));
    ws.onerror = () => { clearTimeout(t); finish(false, "socket error"); };
    ws.onclose = () => { clearTimeout(t); finish(false, "closed before OK"); };
    ws.onmessage = (m) => {
      let d; try { d = JSON.parse(m.data); } catch { return; }
      if (d[0] === "OK" && d[1] === ev.id) {
        clearTimeout(t);
        finish(d[2] === true, d[2] === true ? "" : (d[3] || "rejected"));
      } else if (d[0] === "NOTICE") {
        clearTimeout(t);
        finish(false, d[1] || "notice");
      }
    };
  });
}

// subscribe(url, filter, {onEvent, onEose}) -> { close() }
// Auto-reconnects with capped backoff. Filter is sent verbatim.
export function subscribe(url, filter, { onEvent, onEose } = {}) {
  let ws, closed = false, backoff = 1000;
  const subId = "s" + Math.random().toString(36).slice(2, 10);
  function open() {
    if (closed) return;
    try { ws = new WebSocket(url); } catch { return retry(); }
    ws.onopen = () => { backoff = 1000; ws.send(JSON.stringify(["REQ", subId, filter])); };
    ws.onmessage = (m) => {
      let d; try { d = JSON.parse(m.data); } catch { return; }
      if (d[0] === "EVENT" && d[1] === subId && onEvent) onEvent(d[2]);
      else if (d[0] === "EOSE" && d[1] === subId && onEose) onEose();
    };
    ws.onclose = () => retry();
    ws.onerror = () => { try { ws.close(); } catch {} };
  }
  function retry() {
    if (closed) return;
    setTimeout(open, backoff);
    backoff = Math.min(backoff * 2, 30000);
  }
  open();
  return {
    close() {
      closed = true;
      try { ws.send(JSON.stringify(["CLOSE", subId])); ws.close(); } catch {}
    }
  };
}
