// Aether Pulse — Content Script: Draggable Liquid-Filled Telemetry Vessel with Freefloat Bounce & Pac-Man Wrap
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

  const BOUNDARY_MODES = ["bounce", "pacman", "pin"];
  const BOUNDARY_SHORT = {
    bounce: "BNC",
    pacman: "PAC",
    pin: "PIN"
  };

  let telemetry = null;
  let overlayMode = "auto";
  let boundaryMode = "bounce";
  let detectedHarness = "all";
  let targetLabel = location.hostname || "Browser Workspace";

  function detectHarnessFromDomAndUrl(clientX, clientY) {
    const cx = Math.max(2, Math.min(window.innerWidth - 2, clientX));
    const cy = Math.max(2, Math.min(window.innerHeight - 2, clientY));
    const el = document.elementFromPoint(cx, cy);
    const domText = el ? (el.closest("[data-harness], .panel, tr, section")?.innerText || "").slice(0, 180) : "";
    const blob = `${domText} ${location.hostname} ${document.title}`.toLowerCase();
    if (blob.includes("codex") || blob.includes("chatgpt.com") || blob.includes("openai") || blob.includes("gpt-6")) {
      return { harness: "openai_codex", label: "OpenAI Codex / ChatGPT" };
    }
    if (blob.includes("claude") || blob.includes("anthropic") || blob.includes("opus")) {
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
          <span id="aether-ext-badge">Auto · Bounce</span>
        </div>
        <div class="aether-metrics-row">
          <span class="aether-metric-big" id="aether-ext-hit">94.37% Hit</span>
          <span class="aether-metric-sub" id="aether-ext-vol">4.10B · 26,651 pts</span>
        </div>
        <div class="aether-vessel-foot">
          <span id="aether-ext-target">Over: ${targetLabel}</span>
          <span id="aether-ext-saved">Saved $10,310</span>
        </div>
        <div class="aether-all-drawer" id="aether-ext-drawer"></div>
      </div>
      <div class="aether-side-col">
        <button type="button" class="aether-side-btn" id="aether-ext-cycle-btn" title="Switch Harness View (Auto-Sense / All 3 / Pinned)">
          <svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round">
            <path d="M2 5c2-1.5 4 1.5 6 0s4-1.5 6 0M2 8.5c2-1.5 4 1.5 6 0s4-1.5 6 0M2 12c2-1.5 4 1.5 6 0s4-1.5 6 0"/>
          </svg>
          <span class="aether-side-mode-tag" id="aether-ext-mode-tag">AUTO</span>
        </button>
        <button type="button" class="aether-side-btn" id="aether-ext-boundary-btn" title="Switch Freefloat Physics: Bounce Walls / Pac-Man Wrap / Pin">
          <span class="aether-side-mode-tag" id="aether-ext-bmode-tag" style="color:#30D158;">BNC</span>
        </button>
      </div>
    </div>
  `;
  document.body.appendChild(vessel);

  const canvas = vessel.querySelector(".aether-liquid-canvas");
  const ctx = canvas.getContext("2d");

  // 2nd-Order Spring-Mass-Damper + Freefloat Drift/Wiggle + Shallow-Water Wave Physics State
  const phys = {
    x: Math.max(24, window.innerWidth - 420),
    y: Math.max(24, window.innerHeight - 160),
    targetX: Math.max(24, window.innerWidth - 420),
    targetY: Math.max(24, window.innerHeight - 160),
    vx: 46.0,
    vy: -28.0,
    phase: 0.0,
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

    const bLabel = boundaryMode === "bounce" ? "Bounce" : boundaryMode === "pacman" ? "Pac-Man" : "Pin";
    document.getElementById("aether-ext-dot").style.backgroundColor = phys.accentHex;
    document.getElementById("aether-ext-name").textContent = active.name;
    document.getElementById("aether-ext-badge").textContent =
      `${overlayMode === "auto" ? "Auto" : "Pinned"} · ${bLabel}`;
    document.getElementById("aether-ext-hit").textContent = `${active.cache_hit_pct}% Cache`;
    document.getElementById("aether-ext-vol").textContent = `${active.tokens_formatted} · ${active.leverage_index.toLocaleString()} pts`;
    document.getElementById("aether-ext-target").textContent = `Over: ${targetLabel.slice(0, 26)}`;
    document.getElementById("aether-ext-saved").textContent = `Saved $${active.saved_usd.toLocaleString()}`;
    document.getElementById("aether-ext-mode-tag").textContent = MODE_SHORT[overlayMode] || "AUTO";

    const bTagEl = document.getElementById("aether-ext-bmode-tag");
    bTagEl.textContent = BOUNDARY_SHORT[boundaryMode] || "BNC";
    bTagEl.style.color = boundaryMode === "bounce" ? "#30D158" : boundaryMode === "pacman" ? "#FF9F0A" : "#98989F";

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

  // Drag interaction with pointer velocity tracking for post-release freefloat momentum
  let isDragging = false;
  let dragOffsetX = 0;
  let dragOffsetY = 0;
  let lastPtrX = 0;
  let lastPtrY = 0;
  let lastPtrT = performance.now();
  let throwVx = 0;
  let throwVy = 0;

  vessel.addEventListener("pointerdown", (e) => {
    if (e.target.closest(".aether-side-btn")) return;
    isDragging = true;
    dragOffsetX = e.clientX - phys.x;
    dragOffsetY = e.clientY - phys.y;
    lastPtrX = e.clientX;
    lastPtrY = e.clientY;
    lastPtrT = performance.now();
    throwVx = 0;
    throwVy = 0;
    vessel.setPointerCapture(e.pointerId);
  });

  vessel.addEventListener("pointermove", (e) => {
    if (!isDragging) return;
    const now = performance.now();
    const dtPtr = Math.max(0.004, (now - lastPtrT) / 1000);
    throwVx = 0.6 * throwVx + 0.4 * ((e.clientX - lastPtrX) / dtPtr);
    throwVy = 0.6 * throwVy + 0.4 * ((e.clientY - lastPtrY) / dtPtr);
    lastPtrX = e.clientX;
    lastPtrY = e.clientY;
    lastPtrT = now;

    phys.targetX = e.clientX - dragOffsetX;
    phys.targetY = e.clientY - dragOffsetY;

    vessel.style.pointerEvents = "none";
    const sensed = detectHarnessFromDomAndUrl(e.clientX, e.clientY);
    vessel.style.pointerEvents = "auto";
    detectedHarness = sensed.harness;
    targetLabel = sensed.label;
    updateVesselView();
  });

  vessel.addEventListener("pointerup", () => {
    if (!isDragging) return;
    isDragging = false;
    phys.vx = Math.max(-720, Math.min(720, throwVx * 0.55 + (Math.abs(throwVx) < 20 ? 48 : 0)));
    phys.vy = Math.max(-720, Math.min(720, throwVy * 0.55 + (Math.abs(throwVy) < 20 ? -32 : 0)));
    phys.targetX = phys.x;
    phys.targetY = phys.y;
  });

  document.getElementById("aether-ext-cycle-btn").addEventListener("click", async (e) => {
    e.stopPropagation();
    overlayMode = MODES[(MODES.indexOf(overlayMode) + 1) % MODES.length];
    phys.waveVelocities[5] += 48.0;
    updateVesselView();
    try {
      await chrome.runtime.sendMessage({ type: "SET_MODE", mode: overlayMode });
    } catch (_err) {}
  });

  document.getElementById("aether-ext-boundary-btn").addEventListener("click", (e) => {
    e.stopPropagation();
    boundaryMode = BOUNDARY_MODES[(BOUNDARY_MODES.indexOf(boundaryMode) + 1) % BOUNDARY_MODES.length];
    phys.waveVelocities[5] += 38.0;
    if (boundaryMode !== "pin" && Math.hypot(phys.vx, phys.vy) < 30) {
      phys.vx = 62.0;
      phys.vy = -38.0;
    }
    updateVesselView();
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

  // 60fps Liquid Physics + Freefloat Drift/Wiggle + Bounce/Pac-Man Loop
  let lastTime = performance.now();
  let lastSenseTime = 0;

  function animate(now) {
    const dt = Math.max(0.001, Math.min(0.04, (now - lastTime) / 1000));
    lastTime = now;
    phys.phase += dt;

    const vesselW = 386;
    const vesselH = overlayMode === "all" ? 175 : 104;
    let ax = 0;
    let ay = 0;

    if (isDragging || boundaryMode === "pin") {
      const fx = phys.stiffness * (phys.targetX - phys.x) - phys.damping * phys.vx;
      const fy = phys.stiffness * (phys.targetY - phys.y) - phys.damping * phys.vy;
      const wiggleX = !isDragging ? Math.sin(phys.phase * 2.4) * 14.0 : 0.0;
      const wiggleY = !isDragging ? Math.cos(phys.phase * 1.9) * 11.0 : 0.0;
      ax = (fx + wiggleX) / phys.mass;
      ay = (fy + wiggleY) / phys.mass;
      phys.vx += ax * dt;
      phys.vy += ay * dt;
      phys.x += phys.vx * dt;
      phys.y += phys.vy * dt;
    } else {
      // Freefloat drift + buoyancy wiggle
      const wiggleAx = Math.sin(phys.phase * 2.6) * 44.0 + Math.cos(phys.phase * 1.3) * 18.0;
      const wiggleAy = Math.cos(phys.phase * 2.1) * 36.0 + Math.sin(phys.phase * 1.7) * 16.0;
      const speedCur = Math.hypot(phys.vx, phys.vy);
      const dragCoeff = speedCur > 68.0 ? 0.32 : 0.02;
      ax = wiggleAx - dragCoeff * phys.vx;
      ay = wiggleAy - dragCoeff * phys.vy;
      phys.vx += ax * dt;
      phys.vy += ay * dt;
      phys.x += phys.vx * dt;
      phys.y += phys.vy * dt;
      phys.targetX = phys.x;
      phys.targetY = phys.y;

      const bw = window.innerWidth;
      const bh = window.innerHeight;
      if (boundaryMode === "bounce") {
        let bounced = false;
        if (phys.x < 8) { phys.x = 8; phys.vx = Math.abs(phys.vx) * 0.92; bounced = true; }
        else if (phys.x + vesselW > bw - 8) { phys.x = bw - vesselW - 8; phys.vx = -Math.abs(phys.vx) * 0.92; bounced = true; }
        if (phys.y < 8) { phys.y = 8; phys.vy = Math.abs(phys.vy) * 0.92; bounced = true; }
        else if (phys.y + vesselH > bh - 8) { phys.y = bh - vesselH - 8; phys.vy = -Math.abs(phys.vy) * 0.92; bounced = true; }
        if (bounced) phys.waveVelocities[5] += phys.vy < 0 ? 36.0 : -36.0;
      } else if (boundaryMode === "pacman") {
        let wrapped = false;
        if (phys.x > bw) { phys.x = -vesselW + 6; wrapped = true; }
        else if (phys.x + vesselW < 0) { phys.x = bw - 6; wrapped = true; }
        if (phys.y > bh) { phys.y = -vesselH + 6; wrapped = true; }
        else if (phys.y + vesselH < 0) { phys.y = bh - 6; wrapped = true; }
        if (wrapped) {
          for (let i = 0; i < phys.waveVelocities.length; i++) {
            phys.waveVelocities[i] += Math.sin(i * 0.9) * 26.0;
          }
        }
      }

      // Continuously sense DOM underneath while drifting
      if (now - lastSenseTime > 180) {
        lastSenseTime = now;
        vessel.style.pointerEvents = "none";
        const sensed = detectHarnessFromDomAndUrl(phys.x + vesselW / 2, phys.y + vesselH / 2);
        vessel.style.pointerEvents = "auto";
        if (sensed.harness !== detectedHarness || sensed.label !== targetLabel) {
          detectedHarness = sensed.harness;
          targetLabel = sensed.label;
          updateVesselView();
        }
      }
    }

    phys.tiltDeg = Math.max(-8.5, Math.min(8.5, phys.vx * 0.012 + Math.sin(phys.phase * 3.1) * 0.5));

    const n = phys.waveHeights.length;
    for (let i = 0; i < n; i++) {
      const norm = (i / (n - 1)) * 2 - 1;
      const impulse = -ax * 0.0035 * norm + ay * 0.001 * Math.cos(norm * Math.PI) + Math.sin(now * 0.003 + i * 0.6) * 0.22;
      const restore = -92.0 * phys.waveHeights[i] - 4.6 * phys.waveVelocities[i];
      phys.waveVelocities[i] += restore * dt + impulse;
      phys.waveHeights[i] += phys.waveVelocities[i] * dt;
      phys.waveHeights[i] = Math.max(-14, Math.min(14, phys.waveHeights[i]));
    }

    vessel.style.transform = `translate3d(${phys.x.toFixed(1)}px, ${phys.y.toFixed(1)}px, 0) rotate(${phys.tiltDeg.toFixed(2)}deg)`;

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
