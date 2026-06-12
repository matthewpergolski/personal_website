(function () {
  const STORE_KEY = "experience_chat_messages_v1";
  let pending = false;
  function byId(id) {
    return document.getElementById(id);
  }
  function getRoot() {
    return byId("experience-chat");
  }
  function canAutoFocus() {
    return window.matchMedia("(hover: hover) and (pointer: fine)").matches;
  }
  function loadMessages(root) {
    try {
      const saved = sessionStorage.getItem(STORE_KEY);
      if (saved) return JSON.parse(saved);
      return JSON.parse(root.dataset.initial || "[]");
    } catch (_) {
      return [{ role: "assistant", content: "Hi, ask me about this portfolio." }];
    }
  }
  function saveMessages(messages) {
    try {
      sessionStorage.setItem(STORE_KEY, JSON.stringify(messages.slice(-30)));
    } catch (_) {}
  }
  function setStatus(text) {
    const status = byId("chat-status");
    if (status) status.textContent = text || "";
  }
  function transcriptLine(message) {
    const speaker = message.role === "user" ? "You" : "Portfolio assistant";
    return speaker + ": " + (message.content || "").trim();
  }
  function conversationTranscript() {
    return loadMessages(getRoot())
      .filter(function (message) {
        return !message.pending && (message.content || "").trim();
      })
      .map(transcriptLine)
      .join("\\n\\n");
  }
  function fallbackCopyText(text) {
    const area = document.createElement("textarea");
    area.value = text;
    area.setAttribute("readonly", "");
    area.style.position = "fixed";
    area.style.left = "-9999px";
    area.style.top = "0";
    document.body.appendChild(area);
    area.select();
    const copied = document.execCommand("copy");
    document.body.removeChild(area);
    if (!copied) throw new Error("copy failed");
  }
  async function copyConversation() {
    const copy = byId("chat-copy");
    const transcript = conversationTranscript();
    if (!transcript) {
      setStatus("No conversation to copy yet.");
      return;
    }
    try {
      let copied = false;
      if (navigator.clipboard && window.isSecureContext) {
        try {
          await navigator.clipboard.writeText(transcript);
          copied = true;
        } catch (_) {}
      }
      if (!copied) {
        fallbackCopyText(transcript);
      }
      setStatus("Conversation copied to clipboard.");
      if (copy) {
        const label = copy.textContent;
        copy.textContent = "Copied";
        copy.disabled = true;
        window.setTimeout(function () {
          copy.textContent = label || "Copy conversation";
          copy.disabled = false;
        }, 1200);
      }
    } catch (_) {
      setStatus("Clipboard copy was blocked by this browser.");
    }
  }
  function sourceLabel(source) {
    if (!source) return "";
    if (typeof source === "string") return source;
    return source.label || "";
  }
  function sourceSnippet(source) {
    if (!source || typeof source === "string") return "";
    return source.snippet || "";
  }
  function appendMeta(el, message) {
    const sources = (message.sources || []).map(sourceLabel).filter(Boolean);
    const hasMeta = message.providerLabel || message.note || sources.length;
    if (!hasMeta) return;

    const meta = document.createElement("div");
    meta.className = "chat-meta";

    if (message.providerLabel || message.note) {
      const row = document.createElement("div");
      row.className = "chat-meta-row";
      row.textContent = [message.providerLabel, message.note].filter(Boolean).join(" · ");
      meta.appendChild(row);
    }

    if (sources.length) {
      const row = document.createElement("div");
      row.className = "chat-meta-row";
      const label = document.createElement("span");
      label.textContent = "Sources:";
      row.appendChild(label);
      (message.sources || []).forEach(function (source) {
        const chipLabel = sourceLabel(source);
        if (!chipLabel) return;
        const chip = document.createElement("span");
        chip.className = "chat-source-chip";
        chip.textContent = chipLabel;
        const snippet = sourceSnippet(source);
        if (snippet) chip.title = snippet;
        row.appendChild(chip);
      });
      meta.appendChild(row);
    }
    el.appendChild(meta);
  }
  function renderMessages(messages) {
    const box = byId("chat-messages");
    if (!box) return;
    box.innerHTML = "";
    messages.forEach(function (m) {
      const el = document.createElement("div");
      el.className =
        "chat-message " +
        (m.role === "user" ? "user" : "assistant") +
        (m.pending ? " pending" : "");
      el.textContent = m.content || "";
      if (m.role !== "user") appendMeta(el, m);
      box.appendChild(el);
    });
    box.scrollTop = box.scrollHeight;
    const root = getRoot();
    const hasSuggestions = messages.length <= 1;
    if (root) root.classList.toggle("chat-has-suggestions", hasSuggestions);
  }
  function resetChat() {
    const root = getRoot();
    const messages = JSON.parse(root.dataset.initial || "[]");
    pending = false;
    saveMessages(messages);
    renderMessages(messages);
    setStatus("Started a new browser-session chat.");
    fetch("/api/rag/chat/reset", { method: "POST" }).catch(function () {});
    const input = byId("chat-input");
    if (input && canAutoFocus()) input.focus();
  }
  async function submitMessage(text) {
    const form = byId("chat-form");
    const input = byId("chat-input");
    const send = byId("chat-send");
    if (!form || !text.trim() || pending) return;
    pending = true;
    let messages = loadMessages(getRoot());
    messages.push({ role: "user", content: text.trim() });
    saveMessages(messages);
    renderMessages(
      messages.concat([
        { role: "assistant", content: "Looking across the portfolio context...", pending: true },
      ]),
    );
    if (input) input.value = "";
    if (send) {
      send.disabled = true;
      send.textContent = "Sending";
    }
    setStatus("Searching portfolio, resume, and project context...");
    try {
      const res = await fetch(form.dataset.endpoint || "/api/rag/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text.trim() }),
      });
      const data = await res.json();
      messages.push({
        role: "assistant",
        content: data.response || data.error || "I could not answer that yet.",
        sources: data.sources || [],
        provider: data.provider || "",
        providerLabel: data.provider_label || "",
        note: data.model_note || "",
      });
      setStatus(data.provider_label || "Answer returned from portfolio context.");
    } catch (err) {
      messages.push({
        role: "assistant",
        content: "I could not reach the chat service. Please try again in a moment.",
      });
      setStatus("Chat service was unreachable. Your browser-session history is still preserved.");
    } finally {
      pending = false;
      renderMessages(messages);
      saveMessages(messages);
      if (send) {
        send.disabled = false;
        send.textContent = "Send";
      }
      if (input && canAutoFocus()) input.focus();
    }
  }
  function init() {
    const root = getRoot();
    if (!root || root.dataset.ready === "1") return;
    root.dataset.ready = "1";
    const panel = byId("chat-panel");
    const toggle = byId("chat-toggle");
    const close = byId("chat-close");
    const reset = byId("chat-reset");
    const copy = byId("chat-copy");
    const form = byId("chat-form");
    const input = byId("chat-input");
    renderMessages(loadMessages(root));
    if (toggle)
      toggle.addEventListener("click", function () {
        panel && panel.classList.toggle("chat-panel-closed");
      });
    if (close)
      close.addEventListener("click", function () {
        panel && panel.classList.add("chat-panel-closed");
      });
    if (reset) reset.addEventListener("click", resetChat);
    if (copy) copy.addEventListener("click", copyConversation);
    if (form)
      form.addEventListener("submit", function (e) {
        e.preventDefault();
        submitMessage((input && input.value) || "");
      });
    document.querySelectorAll(".chat-suggestion").forEach(function (btn) {
      btn.addEventListener("click", function () {
        submitMessage(btn.dataset.question || btn.textContent || "");
      });
    });
    if (input)
      input.addEventListener("keydown", function (e) {
        if (e.key === "Enter" && !e.shiftKey) {
          e.preventDefault();
          submitMessage(input.value || "");
        }
      });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
