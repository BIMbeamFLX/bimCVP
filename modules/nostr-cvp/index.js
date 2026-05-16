const DEFAULT_RELAYS = "";

function splitRelays(value) {
  return (value || DEFAULT_RELAYS)
    .split(",")
    .map((relay) => relay.trim())
    .filter(Boolean);
}

function uniqueTopicId() {
  if (crypto.randomUUID) {
    return crypto.randomUUID();
  }
  return `topic-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function publishToRelay(relayUrl, event) {
  return new Promise((resolve) => {
    const socket = new WebSocket(relayUrl);
    const timeout = window.setTimeout(() => {
      socket.close();
      resolve({ relay: relayUrl, ok: false, message: "timeout" });
    }, 7000);

    socket.addEventListener("open", () => {
      socket.send(JSON.stringify(["EVENT", event]));
    });

    socket.addEventListener("message", (message) => {
      try {
        const data = JSON.parse(message.data);
        if (data[0] === "OK" && data[1] === event.id) {
          window.clearTimeout(timeout);
          socket.close();
          resolve({ relay: relayUrl, ok: Boolean(data[2]), message: data[3] || "" });
        }
      } catch {
        window.clearTimeout(timeout);
        socket.close();
        resolve({ relay: relayUrl, ok: false, message: "invalid relay response" });
      }
    });

    socket.addEventListener("error", () => {
      window.clearTimeout(timeout);
      resolve({ relay: relayUrl, ok: false, message: "connection error" });
    });
  });
}

class BcfQuickform extends HTMLElement {
  connectedCallback() {
    this.render();
    this.querySelector("form").addEventListener("submit", (event) => this.submit(event));
  }

  render() {
    const heading = this.getAttribute("heading") || "BCF quickform";
    this.innerHTML = `
      <form class="bcf-qf">
        <h3>${heading}</h3>
        <label>
          <span>Title</span>
          <input name="title" required maxlength="120" autocomplete="off" />
        </label>
        <label>
          <span>Description</span>
          <textarea name="description" required></textarea>
        </label>
        <div class="bcf-qf__row">
          <label>
            <span>Status</span>
            <select name="status">
              <option>Open</option>
              <option>InProgress</option>
              <option>Resolved</option>
              <option>Closed</option>
            </select>
          </label>
          <label>
            <span>Type</span>
            <select name="type">
              <option>Issue</option>
              <option>Clash</option>
              <option>RFI</option>
              <option>Information</option>
              <option>Decision</option>
            </select>
          </label>
          <label>
            <span>Priority</span>
            <select name="priority">
              <option>Normal</option>
              <option>Low</option>
              <option>High</option>
              <option>Critical</option>
            </select>
          </label>
        </div>
        <label>
          <span>IFC element GUID, optional</span>
          <input name="guid" autocomplete="off" />
        </label>
        <button type="submit">Sign topic</button>
        <output aria-live="polite"></output>
      </form>
    `;
  }

  async submit(submitEvent) {
    submitEvent.preventDefault();

    const form = submitEvent.currentTarget;
    const button = form.querySelector("button");
    const output = form.querySelector("output");
    const values = Object.fromEntries(new FormData(form).entries());
    const project = this.getAttribute("project");

    if (!project) {
      this.fail("Missing project attribute.");
      return;
    }

    if (!window.nostr || typeof window.nostr.signEvent !== "function") {
      this.fail("No NIP-07 signer found.");
      return;
    }

    button.disabled = true;
    output.value = "Signing...";

    try {
      const topicId = uniqueTopicId();
      const event = await window.nostr.signEvent({
        kind: 30900,
        created_at: Math.floor(Date.now() / 1000),
        tags: [
          ["d", topicId],
          ["a", project],
          ["bcf-guid", topicId],
          ["bcf-version", "3.0"],
          ["title", values.title],
          ["bcf-status", values.status],
          ["s", values.status],
          ["bcf-type", values.type],
          ["bcf-priority", values.priority],
          ["client", "nostr-cvp/0.1"],
          ...(values.guid ? [["ifc", values.guid]] : []),
        ],
        content: JSON.stringify({
          guid: topicId,
          title: values.title,
          description: values.description,
          topic_type: values.type,
          status: values.status,
          priority: values.priority,
          ifc_guid: values.guid || null,
        }),
      });

      this.dispatchEvent(new CustomEvent("bcf-quickform:signed", {
        bubbles: true,
        detail: { event },
      }));

      const relays = splitRelays(this.getAttribute("relays"));
      if (relays.length === 0) {
        output.value = "Signed locally. No relay configured.";
        return;
      }

      output.value = "Publishing...";
      const results = await Promise.all(relays.map((relay) => publishToRelay(relay, event)));
      this.dispatchEvent(new CustomEvent("bcf-quickform:published", {
        bubbles: true,
        detail: { event, results },
      }));

      const ok = results.filter((result) => result.ok).length;
      output.value = `Published to ${ok}/${results.length} relays.`;
    } catch (error) {
      this.fail(error.message || "Signing failed.");
    } finally {
      button.disabled = false;
    }
  }

  fail(message) {
    const output = this.querySelector("output");
    if (output) {
      output.value = message;
    }
    this.dispatchEvent(new CustomEvent("bcf-quickform:error", {
      bubbles: true,
      detail: { error: message },
    }));
  }
}

customElements.define("bcf-quickform", BcfQuickform);
