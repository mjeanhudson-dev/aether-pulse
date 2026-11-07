// Aether Pulse Extension Popup Controller (Manifest V3 CSP compliant)
document.addEventListener("DOMContentLoaded", async () => {
  const statusEl = document.getElementById("daemon-status");
  const buttons = Array.from(document.querySelectorAll("#mode-buttons button"));

  function highlightMode(mode) {
    buttons.forEach((btn) => {
      btn.classList.toggle("active", btn.getAttribute("data-mode") === mode);
    });
  }

  try {
    const res = await chrome.runtime.sendMessage({ type: "GET_TELEMETRY" });
    if (res && res.ok) {
      statusEl.textContent = res.daemonOnline ? "WS Daemon Live" : "Local Snapshot";
      highlightMode(res.overlayMode || "auto");
    }
  } catch (_err) {
    statusEl.textContent = "Ready";
  }

  buttons.forEach((btn) => {
    btn.addEventListener("click", async () => {
      const mode = btn.getAttribute("data-mode");
      highlightMode(mode);
      try {
        await chrome.runtime.sendMessage({ type: "SET_MODE", mode });
      } catch (_e) {}
    });
  });
});
