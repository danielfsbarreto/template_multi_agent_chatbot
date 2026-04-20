(function () {
  "use strict";

  // ---------------------------------------------------------------------------
  // State
  // ---------------------------------------------------------------------------

  let channels = [];
  let activeChannelId = null;
  let eventSource = null;
  let isWaitingForReply = false;

  // Track event_ids we've already rendered this session to avoid duplicating
  // messages that were both loaded from history AND pushed via SSE.
  const renderedEventIds = new Set();

  // ---------------------------------------------------------------------------
  // DOM refs
  // ---------------------------------------------------------------------------

  const $channelList      = document.getElementById("channel-list");
  const $emptyState       = document.getElementById("empty-state");
  const $chatView         = document.getElementById("chat-view");
  const $chatChannelName  = document.getElementById("chat-channel-name");
  const $messages         = document.getElementById("messages");
  const $typingIndicator  = document.getElementById("typing-indicator");
  const $messageForm      = document.getElementById("message-form");
  const $messageInput     = document.getElementById("message-input");
  const $btnNewChannel    = document.getElementById("btn-new-channel");
  const $btnDeleteChannel = document.getElementById("btn-delete-channel");
  const $modalOverlay     = document.getElementById("modal-overlay");
  const $newChannelForm   = document.getElementById("new-channel-form");
  const $newChannelName   = document.getElementById("new-channel-name");
  const $btnCancelModal   = document.getElementById("btn-cancel-modal");

  // ---------------------------------------------------------------------------
  // API helpers
  // ---------------------------------------------------------------------------

  async function api(path, opts = {}) {
    const res = await fetch(path, {
      headers: { "Content-Type": "application/json" },
      ...opts,
    });
    if (opts.method === "DELETE" && res.status === 204) return null;
    return res.json();
  }

  // ---------------------------------------------------------------------------
  // Channels
  // ---------------------------------------------------------------------------

  async function loadChannels() {
    channels = await api("/api/channels");
    renderChannelList();
  }

  function renderChannelList() {
    $channelList.innerHTML = "";
    channels.forEach((ch) => {
      const li = document.createElement("li");
      li.className = "channel-item" + (ch.id === activeChannelId ? " active" : "");
      li.dataset.id = ch.id;
      li.innerHTML = '<span class="hash">#</span> ' + escapeHtml(ch.name);
      li.addEventListener("click", () => selectChannel(ch.id));
      $channelList.appendChild(li);
    });
  }

  async function selectChannel(channelId) {
    if (activeChannelId === channelId) return;
    activeChannelId = channelId;
    renderedEventIds.clear();
    renderChannelList();

    const ch = await api(`/api/channels/${channelId}`);
    if (!ch || ch.error) return;

    $emptyState.classList.add("hidden");
    $chatView.classList.remove("hidden");
    $chatChannelName.textContent = ch.name;
    $messageInput.placeholder = `Message #${ch.name}`;
    $messages.innerHTML = "";

    (ch.messages || []).forEach((msg) => renderMessage(msg));
    scrollToBottom();
    subscribeSSE(channelId);
    setTyping(false);
  }

  // ---------------------------------------------------------------------------
  // SSE
  // ---------------------------------------------------------------------------

  function subscribeSSE(channelId) {
    if (eventSource) {
      eventSource.close();
      eventSource = null;
    }
    eventSource = new EventSource(`/api/channels/${channelId}/events`);
    eventSource.onmessage = (e) => {
      if (channelId !== activeChannelId) return;
      try {
        const data = JSON.parse(e.data);
        handleSSEEvent(data);
      } catch (_) { /* ignore parse errors */ }
    };
    eventSource.onerror = () => {
      // Browser will auto-reconnect for us
    };
  }

  function handleSSEEvent(data) {
    if (data.type === "message_created" || data.type === "image_generated") {
      const msg = data.message;
      if (!msg) return;

      if (msg.event_id && renderedEventIds.has(msg.event_id)) return;

      renderMessage(msg);
      scrollToBottom();
    } else if (data.type === "flow_started") {
      setTyping(true);
    } else if (data.type === "flow_finished") {
      setTyping(false);
    } else if (data.type === "kickoff_error") {
      setTyping(false);
      showError(data.error || "Kickoff failed");
    }
  }

  // ---------------------------------------------------------------------------
  // Messages
  // ---------------------------------------------------------------------------

  function renderMessage(msg) {
    if (msg.event_id) renderedEventIds.add(msg.event_id);

    const div = document.createElement("div");
    div.className = "message";

    const roleLabel = msg.role === "user" ? "You" : msg.role === "assistant" ? "CrewAI" : "Tool";
    const avatarLetter = msg.role === "user" ? "U" : msg.role === "assistant" ? "A" : "T";
    const ts = formatTimestamp(msg.timestamp);

    let contentHtml = "";
    if (msg.event_type === "image_generated" && msg.image_base64) {
      contentHtml = `<img class="message-image" src="data:image/png;base64,${msg.image_base64}" alt="Generated image" loading="lazy">`;
      if (msg.content) {
        contentHtml = `<div class="message-content">${escapeHtml(msg.content)}</div>` + contentHtml;
      }
    } else {
      contentHtml = `<div class="message-content">${escapeHtml(msg.content)}</div>`;
    }

    div.innerHTML = `
      <div class="message-avatar ${msg.role}">${avatarLetter}</div>
      <div class="message-body">
        <div class="message-header">
          <span class="message-author ${msg.role}">${roleLabel}</span>
          <span class="message-timestamp">${ts}</span>
        </div>
        ${contentHtml}
      </div>
    `;

    $messages.appendChild(div);
  }

  function scrollToBottom() {
    requestAnimationFrame(() => {
      $messages.scrollTop = $messages.scrollHeight;
    });
  }

  function setTyping(show) {
    isWaitingForReply = show;
    $typingIndicator.classList.toggle("hidden", !show);
    if (show) scrollToBottom();
  }

  // ---------------------------------------------------------------------------
  // Send message
  // ---------------------------------------------------------------------------

  $messageForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const content = $messageInput.value.trim();
    if (!content || !activeChannelId) return;

    $messageInput.value = "";
    setTyping(true);

    try {
      await api(`/api/channels/${activeChannelId}/messages`, {
        method: "POST",
        body: JSON.stringify({ content }),
      });
    } catch (err) {
      setTyping(false);
      showError("Failed to send message");
    }
  });

  // ---------------------------------------------------------------------------
  // New channel modal
  // ---------------------------------------------------------------------------

  $btnNewChannel.addEventListener("click", () => {
    $modalOverlay.classList.remove("hidden");
    $newChannelName.value = "";
    $newChannelName.focus();
  });

  $btnCancelModal.addEventListener("click", closeModal);
  $modalOverlay.addEventListener("click", (e) => {
    if (e.target === $modalOverlay) closeModal();
  });

  function closeModal() {
    $modalOverlay.classList.add("hidden");
  }

  $newChannelForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const name = $newChannelName.value.trim();
    if (!name) return;

    closeModal();
    const ch = await api("/api/channels", {
      method: "POST",
      body: JSON.stringify({ name }),
    });
    if (ch && ch.id) {
      await loadChannels();
      selectChannel(ch.id);
    }
  });

  // ---------------------------------------------------------------------------
  // Delete channel
  // ---------------------------------------------------------------------------

  $btnDeleteChannel.addEventListener("click", async () => {
    if (!activeChannelId) return;
    if (!confirm("Delete this channel and all its messages?")) return;

    await api(`/api/channels/${activeChannelId}`, { method: "DELETE" });
    activeChannelId = null;
    if (eventSource) { eventSource.close(); eventSource = null; }

    $chatView.classList.add("hidden");
    $emptyState.classList.remove("hidden");
    await loadChannels();
  });

  // ---------------------------------------------------------------------------
  // Utilities
  // ---------------------------------------------------------------------------

  function escapeHtml(str) {
    if (!str) return "";
    const el = document.createElement("span");
    el.textContent = str;
    return el.innerHTML;
  }

  function formatTimestamp(ts) {
    if (!ts) return "";
    try {
      const d = new Date(ts.includes("T") ? ts : ts + "Z");
      return d.toLocaleString(undefined, {
        month: "short", day: "numeric",
        hour: "2-digit", minute: "2-digit",
      });
    } catch (_) {
      return ts;
    }
  }

  function showError(msg) {
    const el = document.createElement("div");
    el.className = "error-toast";
    el.textContent = msg;
    document.body.appendChild(el);
    setTimeout(() => el.remove(), 5000);
  }

  // ---------------------------------------------------------------------------
  // Init
  // ---------------------------------------------------------------------------

  loadChannels();
})();
