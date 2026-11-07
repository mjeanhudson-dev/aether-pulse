// Aether Pulse Manifest V3 Background Service Worker
// Authored by Eloquent (@mjeanhudson-dev)
// Follows Chrome Extensions MV3 rules: zero global state, async/await only, chrome.storage persistence.

const DEFAULT_TELEMETRY = {
  schema: "aether.pulse.ws.v1",
  operator_name: "Eloquent",
  operator_handle: "@mjeanhudson-dev",
  overlay_mode: "auto",
  overlay_mode_label: "Auto-Sense Target",
  detected_harness: "all",
  effective_harness: "all",
  target_label: "Browser Harness",
  show_all_drawer: false,
  harnesses: {
    claude_code: {
      id: "claude_code",
      name: "Anthropic Claude Code",
      short_name: "Claude Code",
      model_badge: "Opus 5.5 · Sonnet 5.5",
      tokens_formatted: "2.01B",
      sessions: 91,
      cache_hit_pct: 94.94,
      cr_cw_reuse: 18.8,
      leverage_index: 25890,
      saved_usd: 5054,
      liquid_fill_ratio: 0.9494,
      accent_hex: "#0066CC"
    },
    antigravity: {
      id: "antigravity",
      name: "Google Antigravity",
      short_name: "Antigravity",
      model_badge: "Gemini 3.8 Flash · 4 Argon",
      tokens_formatted: "1.96B",
      sessions: 363,
      cache_hit_pct: 93.66,
      cr_cw_reuse: 14.8,
      leverage_index: 25410,
      saved_usd: 4932,
      liquid_fill_ratio: 0.9366,
      accent_hex: "#2997FF"
    },
    openai_codex: {
      id: "openai_codex",
      name: "OpenAI Codex CLI",
      short_name: "Codex CLI",
      model_badge: "GPT-6.1 Sol · Sandbox",
      tokens_formatted: "129.8M",
      sessions: 62,
      cache_hit_pct: 96.34,
      cr_cw_reuse: 26.3,
      leverage_index: 24980,
      saved_usd: 324,
      liquid_fill_ratio: 0.9634,
      accent_hex: "#30D158"
    },
    all: {
      id: "all",
      name: "3-Harness Trinity Mesh",
      short_name: "All 3 Harnesses",
      model_badge: "Claude + Antigravity + Codex",
      tokens_formatted: "4.10B",
      sessions: 516,
      cache_hit_pct: 94.37,
      cr_cw_reuse: 38.2,
      leverage_index: 26651,
      saved_usd: 10310,
      liquid_fill_ratio: 0.9437,
      accent_hex: "#0066CC"
    }
  }
};

const MODES = ["auto", "all", "claude_code", "antigravity", "openai_codex"];

async function syncTelemetryFromLocalDaemon() {
  try {
    const response = await fetch("http://127.0.0.1:8765/api/telemetry", {
      method: "GET",
      headers: { "Accept": "application/json" }
    });
    if (response.ok) {
      const liveData = await response.json();
      await chrome.storage.local.set({ aetherTelemetry: liveData, daemonOnline: true });
      await chrome.action.setBadgeText({ text: "94%" });
      await chrome.action.setBadgeBackgroundColor({ color: "#0066CC" });
      return liveData;
    }
  } catch (_err) {
    // Local daemon offline; use cached or default telemetry gracefully
  }
  const stored = await chrome.storage.local.get(["aetherTelemetry", "overlayMode"]);
  const base = stored.aetherTelemetry || DEFAULT_TELEMETRY;
  if (stored.overlayMode) {
    base.overlay_mode = stored.overlayMode;
  }
  await chrome.storage.local.set({ aetherTelemetry: base, daemonOnline: false });
  await chrome.action.setBadgeText({ text: "ON" });
  await chrome.action.setBadgeBackgroundColor({ color: "#1D1D1F" });
  return base;
}

chrome.runtime.onInstalled.addListener(async () => {
  await chrome.storage.local.set({
    aetherTelemetry: DEFAULT_TELEMETRY,
    overlayMode: "auto",
    overlayVisible: true
  });
  await chrome.alarms.create("aether-telemetry-poll", { periodInMinutes: 0.5 });
  await syncTelemetryFromLocalDaemon();
});

chrome.alarms.onAlarm.addListener(async (alarm) => {
  if (alarm.name === "aether-telemetry-poll") {
    await syncTelemetryFromLocalDaemon();
  }
});

chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  (async () => {
    try {
      if (message.type === "GET_TELEMETRY") {
        const data = await syncTelemetryFromLocalDaemon();
        const prefs = await chrome.storage.local.get(["overlayMode", "overlayVisible", "daemonOnline"]);
        sendResponse({
          ok: true,
          telemetry: data,
          overlayMode: prefs.overlayMode || "auto",
          overlayVisible: prefs.overlayVisible !== false,
          daemonOnline: Boolean(prefs.daemonOnline)
        });
        return;
      }

      if (message.type === "CYCLE_MODE") {
        const { overlayMode = "auto" } = await chrome.storage.local.get("overlayMode");
        const nextIdx = (MODES.indexOf(overlayMode) + 1) % MODES.length;
        const nextMode = MODES[nextIdx];
        await chrome.storage.local.set({ overlayMode: nextMode });
        sendResponse({ ok: true, overlayMode: nextMode });
        return;
      }

      if (message.type === "SET_MODE") {
        const targetMode = MODES.includes(message.mode) ? message.mode : "auto";
        await chrome.storage.local.set({ overlayMode: targetMode });
        sendResponse({ ok: true, overlayMode: targetMode });
        return;
      }

      if (message.type === "TOGGLE_VISIBILITY") {
        const { overlayVisible = true } = await chrome.storage.local.get("overlayVisible");
        const nextVis = !overlayVisible;
        await chrome.storage.local.set({ overlayVisible: nextVis });
        sendResponse({ ok: true, overlayVisible: nextVis });
        return;
      }

      sendResponse({ ok: false, error: "Unknown message type" });
    } catch (err) {
      sendResponse({ ok: false, error: String(err) });
    }
  })();
  return true;
});
