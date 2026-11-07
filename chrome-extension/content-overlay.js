// Aether Pulse — Content Script: Draggable Liquid-Filled Telemetry Vessel
// Authored by Eloquent (@mjeanhudson-dev)

(async function initAetherLiquidOverlay() {
  if (document.getElementById("aether-ext-liquid-vessel") || document.getElementById("aether-liquid-hud")) {
    return;
  }

  const MODES = ["auto", "all", "claude_code", "antigravity", "openai_codex"];
  const MODE_SHORT = {
    auto: "AUTO",
    all: "ALL 3",
    claude_code: "CLAU",
    antigravity: "AGY",
    openai_codex: "CODX"
  };

  let telemetry = null;
  let overlayMode = "auto";
  let detectedHarness = "all";
  let targetLabel = location.hostname || "Browser Workspace";

  function detectHarnessFromDomAndUrl(clientX, clientY) {
    const el = document.elementFromPoint(clientX, clientY);
    const domText = el ? (el.closest("[data-harness], .panel, tr, section")?.innerText || "").slice(0, 180) : "";
    const blob = `${domText} ${location.hostname} ${document.title}`.toLowerCase();
    if (blob.includes("codex") || blob.includes("chatgpt.com") || blob.includes("openai")) {
      return { harness: "openai_codex", label: "OpenAI Codex / ChatGPT" };
    }
    if (blob.includes("claude") || blob.includes("anthropic")) {
      return { harness: "claude_code", label: "Anthropic Claude Code" };
    }
    if (blob.includes("antigravity") || blob.includes("gemini") || blob.includes("aistudio")) {
      return { harness: "antigravity", label: "Google Antigravity" };
    }
    return { harness: "all", label: location.hostname || "3-Harness Mesh" };
  }

  const vessel = document.createElement("aside");
  vessel.id = "aether-ext-liquid-vessel";
  vessel.setAttribute("role", "region");
  vessel.setAttribute("aria-label", "Aether Pulse Draggable Liquid Telemetry Overlay");

  vessel.innerHTML = `
    <canvas class="aether-liquid-canvas" width="386" height="175"></canvas>
    <div class="aether-vessel-layout">
      <div class="aether-vessel-body">
        <div class="aether-vessel-top">
          <span class="aether-harness-pill">
            <span class="aether-dot" id="aether-ext-dot"></span>
            <span id="aether-ext-name">3-Harness Trinity Mesh</span>
          </span>
          <span id="aether-ext-badge">Auto-Sense</span>
        </div>
        <div class="aether-metrics-row">
          <span class="aether-metric-big" id="aether-ext-hit">94.37% Hit</span>
          <span class="aether-metric-sub" id="aether-ext-vol">4.10B · 26,651 pts</span>
        </div>
        <div class="aether-vessel-foot">
          <span id="aether-ext-target">Target: ${targetLabel}</span>
          <span id="aether-ext-saved">Saved $10,310</span>
        </div>
        <div class="aether-all-drawer" id="aether-ext-drawer"></div>
      </div>
      <button type="button" class="aether-side-btn" id="aether-ext-cycle-btn" title="Click to switch between Auto-Sense, All 3 Harnesses, or Pinned Harness">
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round">
          <path d="M2 5c2-1.5 4 1.5 6 0s4-1.5 6 0M2 8.5c2-1.5 4 1.5 6 0s4-1.5 6 0M2 12c2-1.5 4 1.5 6 0s4-1.5 6 0"/>
        </svg>
        <span class="aether-side-mode-tag" id="aether-ext-mode-tag">AUTO</span>
      </button>
    </div>
  `;
  document.body.appendChild(vessel);

  const canvas = vessel.querySelector(".aether-liquid-canvas");
  const ctx = canvas.getContext("2d");

  // 2nd-Order Spring-Mass-Damper + 1D Coupled Shallow-Water Wave Physics State
  const phys = {
    x: Math.max(24, window.innerWidth - 420),
    y: Math.max(24, window.innerHeight - 160),
    targetX: Math.max(24, window.innerWidth - 420),
    targetY: Math.max(24, window.innerHeight - 160),
    vx: 0,
    vy: 0,
    mass: 1.85,
    stiffness: 150.0,
    damping: 21.0,
    tiltDeg: 0,
    fillRatio: 0.9437,
    accentHex: "#2997FF",
    waveHeights: new Array(11).fill(0),
    waveVelocities: new Array(11).fill(0)
  };

  function updateVesselView() {
    if (!telemetry || !telemetry.harnesses) return;
    const effectiveKey = overlayMode === "auto" ? detectedHarness : overlayMode;
    const active = telemetry.harnesses[effectiveKey] || telemetry.harnesses.all;

    phys.fillRatio = active.liquid_fill_ratio || 0.94;
    phys.accentHex = active.accent_hex || "#2997FF";

    document.getElementById("aether-ext-dot").style.backgroundColor = phys.accentHex;
    document.getElementById("aether-ext-name").textContent = active.name;
    document.getElementById("aether-ext-badge").textContent =
      overlayMode === "auto" ? `Auto · ${active.short_name}` : `Pinned · ${active.short_name}`;
    document.getElementById("aether-ext-hit").textContent = `${active.cache_hit_pct}% Cache`;
    document.getElementById("aether-ext-vol").textContent = `${active.tokens_formatted} · ${active.leverage_index.toLocaleString()} pts`;
    document.getElementById("aether-ext-target").textContent = `Over: ${targetLabel.slice(0, 26)}`;
    document.getElementById("aether-ext-saved").textContent = `Saved $${active.saved_usd.toLocaleString()}`;
    document.getElementById("aether-ext-mode-tag").textContent = MODE_SHORT[overlayMode] || "AUTO";

    vessel.classList.toggle("expanded", overlayMode === "all");
    const drawer = document.getElementById("aether-ext-drawer");
    if (overlayMode === "all") {
      drawer.innerHTML = ["claude_code", "antigravity", "openai_codex"]
        .map((k) => {
          const h = telemetry.harnesses[k];
          return `<div class="aether-drawer-item"><span>${h.short_name}</span><span>${h.tokens_formatted} · ${h.cache_hit_pct}% · ${h.sessions}s</span></div>`;
        })
        .join("");
    }
  }

  // Drag interaction with pointer capture
  let isDragging = false;
  let dragOffsetX = 0;
  let dragOffsetY = 0;

  vessel.addEventListener("pointerdown", (e) => {
    if (e.target.closest("#aether-ext-cycle-btn")) return;
    isDragging = true;
    dragOffsetX = e.clientX - phys.x;
    dragOffsetY = e.clientY - phys.y;
    vessel.setPointerCapture(e.pointerId);
  });

  vessel.addEventListener("pointermove", (e) => {
    if (!isDragging) return;
    phys.targetX = Math.max(8, Math.min(window.innerWidth - 396, e.clientX - dragOffsetX));
    phys.targetY = Math.max(8, Math.min(window.innerHeight - 110, e.clientY - dragOffsetY));

    vessel.style.pointerEvents = "none";
    const sensed = detectHarnessFromDomAndUrl(e.clientX, e.clientY);
    vessel.style.pointerEvents = "auto";
    detectedHarness = sensed.harness;
    targetLabel = sensed.label;
    updateVesselView();
  });

  vessel.addEventListener("pointerup", () => {
    isDragging = false;
  });

  document.getElementById("aether-ext-cycle-btn").addEventListener("click", async (e) => {
    e.stopPropagation();
    const nextIdx = (MODES.indexOf(overlayMode) + 1) % MODES.length;
    overlayMode = MODES[nextIdx];
    phys.waveVelocities[5] += 48.0; // Liquid impulse on click
    updateVesselView();
    try {
      await chrome.runtime.sendMessage({ type: "SET_MODE", mode: overlayMode });
    } catch (_err) {}
  });

  // Load initial telemetry from background SW and optional local WebSocket
  try {
    const res = await chrome.runtime.sendMessage({ type: "GET_TELEMETRY" });
    if (res && res.ok) {
      telemetry = res.telemetry;
      overlayMode = res.overlayMode || "auto";
      vessel.style.display = res.overlayVisible === false ? "none" : "block";
      const sensed = detectHarnessFromDomAndUrl(window.innerWidth / 2, window.innerHeight / 2);
      detectedHarness = sensed.harness;
      targetLabel = sensed.label;
      updateVesselView();
    }
  } catch (_err) {}

  try {
    const ws = new WebSocket("ws://127.0.0.1:8765/ws");
    ws.addEventListener("message", (ev) => {
      try {
        telemetry = JSON.parse(ev.data);
        updateVesselView();
      } catch (_e) {}
    });
  } catch (_err) {}

  // 60fps Spring-Mass-Damper + Shallow-Water Liquid Meniscus Loop
  let lastTime = performance.now();
  function animate(now) {
    const dt = Math.max(0.001, Math.min(0.04, (now - lastTime) / 1000));
    lastTime = now;

    const fx = phys.stiffness * (phys.targetX - phys.x) - phys.damping * phys.vx;
    const fy = phys.stiffness * (phys.targetY - phys.y) - phys.damping * phys.vy;
    const ax = fx / phys.mass;
    const ay = fy / phys.mass;

    phys.vx += ax * dt;
    phys.vy += ay * dt;
    phys.x += phys.vx * dt;
    phys.y += phys.vy * dt;
    phys.tiltDeg = Math.max(-8.5, Math.min(8.5, phys.vx * 0.012));

    const n = phys.waveHeights.length;
    for (let i = 0; i < n; i++) {
      const norm = (i / (n - 1)) * 2 - 1;
      const impulse = -ax * 0.0035 * norm + ay * 0.001 * Math.cos(norm * Math.PI) + Math.sin(now * 0.003 + i * 0.6) * 0.18;
      const restore = -92.0 * phys.waveHeights[i] - 4.6 * phys.waveVelocities[i];
      phys.waveVelocities[i] += restore * dt + impulse;
      phys.waveHeights[i] += phys.waveVelocities[i] * dt;
      phys.waveHeights[i] = Math.max(-14, Math.min(14, phys.waveHeights[i]));
    }

    vessel.style.transform = `translate3d(${phys.x.toFixed(1)}px, ${phys.y.toFixed(1)}px, 0) rotate(${phys.tiltDeg.toFixed(2)}deg)`;

    // Render liquid meniscus inside canvas
    const w = canvas.width;
    const h = canvas.height;
    ctx.clearRect(0, 0, w, h);
    const baseY = h - h * 0.44 * phys.fillRatio;
    ctx.beginPath();
    ctx.moveTo(0, h);
    for (let i = 0; i < n; i++) {
      const px = (i / (n - 1)) * w;
      const py = baseY + phys.waveHeights[i] + phys.tiltDeg * ((i - n / 2) * 0.4);
      ctx.lineTo(px, py);
    }
    ctx.lineTo(w, h);
    ctx.closePath();
    ctx.fillStyle = "rgba(41, 151, 255, 0.13)";
    ctx.fill();

    ctx.beginPath();
    for (let i = 0; i < n; i++) {
      const px = (i / (n - 1)) * w;
      const py = baseY + phys.waveHeights[i] + phys.tiltDeg * ((i - n / 2) * 0.4);
      if (i === 0) ctx.moveTo(px, py);
      else ctx.lineTo(px, py);
    }
    ctx.strokeStyle = phys.accentHex;
    ctx.lineWidth = 1.6;
    ctx.stroke();

    requestAnimationFrame(animate);
  }
  requestAnimationFrame(animate);
})();
