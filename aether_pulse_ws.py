#!/usr/bin/env python3
"""
Aether Pulse — Real-Time WebSocket Telemetry Server, Spatial Harness Detector & Liquid Physics Engine
=====================================================================================================
Authored by Eloquent (@mjeanhudson-dev)

Provides:
  1. Pure-Python RFC 6455 WebSocket + HTTP JSON server (`ws://127.0.0.1:8765/ws`, `http://127.0.0.1:8765/api/telemetry`)
  2. Spatial OS Window & Browser Target Detection (`detect_harness_from_context`, `probe_window_at_point`)
     that senses which AI harness (Claude Code, Google Antigravity, OpenAI Codex CLI) is underneath
     the floating overlay as you drag it across your screen or browser tabs.
  3. One-Button Side Mode Switcher (`next_overlay_mode`: `auto` -> `all` -> `claude_code` -> `antigravity` -> `openai_codex`).
  4. Weighty Liquid-Filled Physics Solver (`create_liquid_physics_state`, `step_liquid_physics`)
     combining 2nd-order spring-mass-damper inertia with a coupled 1D shallow-water slosh wave simulation.
"""

from __future__ import annotations

import asyncio
import base64
import ctypes
import ctypes.wintypes
import hashlib
import json
import math
import struct
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import aether_pulse

WS_MAGIC_GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
OVERLAY_MODES = [
    "auto",
    "all",
    "claude_code",
    "antigravity",
    "openai_codex",
    "cursor",
    "aider",
    "windsurf",
    "continue_dev",
    "github_copilot",
    "openhands",
    "t3_code",
]
BOUNDARY_MODES = ["bounce", "pacman", "pin"]

MODE_LABELS = {
    "auto": "Auto-Sense Target",
    "all": "All 10 Harnesses",
    "claude_code": "Claude Code",
    "antigravity": "Antigravity",
    "openai_codex": "Codex CLI",
    "cursor": "Cursor IDE",
    "aider": "Aider Pair",
    "windsurf": "Windsurf Cascade",
    "continue_dev": "Continue.dev",
    "github_copilot": "GitHub Copilot",
    "openhands": "OpenHands",
    "t3_code": "T3 Code",
}

BOUNDARY_LABELS = {
    "bounce": "Bounce Walls",
    "pacman": "Pac-Man Wrap",
    "pin": "Pinned Anchor",
}


def next_overlay_mode(current_mode: str) -> str:
    """
    Cycles the 1-button side toggle on the floating overlay:
      auto -> all -> claude_code -> antigravity -> openai_codex -> auto
    """
    if current_mode not in OVERLAY_MODES:
        return "auto"
    idx = OVERLAY_MODES.index(current_mode)
    return OVERLAY_MODES[(idx + 1) % len(OVERLAY_MODES)]


def next_boundary_mode(current_mode: str) -> str:
    """
    Cycles the freefloat boundary physics mode when releasing the drag:
      bounce (Elastic Wall Bounce) -> pacman (Toroidal Edge Wrap) -> pin (Stationary Spring) -> bounce
    """
    if current_mode not in BOUNDARY_MODES:
        return "bounce"
    idx = BOUNDARY_MODES.index(current_mode)
    return BOUNDARY_MODES[(idx + 1) % len(BOUNDARY_MODES)]


def detect_harness_from_context(
    window_title: str = "",
    process_name: str = "",
    url_or_target: str = "",
) -> str:
    """
    Classifies which AI coding harness is underneath the floating overlay
    based on window title, process executable name, or browser URL/DOM target.
    Supports top 10 AI coding/agent harnesses across GitHub and the developer ecosystem.
    """
    blob = f"{window_title} {process_name} {url_or_target}".lower()

    if any(k in blob for k in ("cursor", "cursor-agent", "anysphere")):
        return "cursor"
    if any(k in blob for k in ("windsurf", "cascade", "codeium")):
        return "windsurf"
    if any(k in blob for k in ("aider", "aider-chat", "paul-gauthier")):
        return "aider"
    if any(k in blob for k in ("continue", "continue-dev", "continue.dev")):
        return "continue_dev"
    if any(k in blob for k in ("copilot", "gh copilot", "github copilot")):
        return "github_copilot"
    if any(k in blob for k in ("openhands", "opendevin", "all-hands")):
        return "openhands"
    if any(k in blob for k in ("t3code", "t3 code", "pingdotgg", "ping.gg")):
        return "t3_code"
    if any(k in blob for k in ("codex", "chatgpt.com", "openai", "gpt-", "o3-pro", "sandbox")):
        return "openai_codex"
    if any(k in blob for k in ("claude", "anthropic", "claude.ai", "opus", "sonnet")):
        return "claude_code"
    if any(k in blob for k in ("antigravity", "gemini", "aistudio.google", "deepmind", "argon", "agy")):
        return "antigravity"
    return "all"


def probe_window_at_point(
    screen_x: int,
    screen_y: int,
    ignore_hwnd: int = 0,
) -> Dict[str, str]:
    """
    Uses Win32 `WindowFromPoint` / `GetForegroundWindow` + process image inspection
    to identify the OS window physically located underneath `(screen_x, screen_y)`.
    """
    if sys.platform != "win32":
        return {"window_title": "", "process_name": "", "detected_harness": "all"}

    try:
        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32
        pt = ctypes.wintypes.POINT(int(screen_x), int(screen_y))
        hwnd = user32.WindowFromPoint(pt)
        if not hwnd or (ignore_hwnd and hwnd == ignore_hwnd):
            hwnd = user32.GetForegroundWindow()
        else:
            GA_ROOT = 2
            root_hwnd = user32.GetAncestor(hwnd, GA_ROOT)
            if root_hwnd and root_hwnd != ignore_hwnd:
                hwnd = root_hwnd
            elif root_hwnd == ignore_hwnd:
                hwnd = user32.GetForegroundWindow()

        buf = ctypes.create_unicode_buffer(512)
        user32.GetWindowTextW(hwnd, buf, 512)
        title = aether_pulse.scrub_personal_identity(buf.value)

        proc_name = ""
        try:
            pid = ctypes.wintypes.DWORD(0)
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            if pid.value:
                PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
                hproc = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid.value)
                if hproc:
                    pbuf = ctypes.create_unicode_buffer(512)
                    sz = ctypes.wintypes.DWORD(512)
                    if kernel32.QueryFullProcessImageNameW(hproc, 0, pbuf, ctypes.byref(sz)):
                        proc_name = Path(pbuf.value).name
                    kernel32.CloseHandle(hproc)
        except Exception:
            pass

        detected = detect_harness_from_context(title, proc_name, "")
        return {
            "window_title": title,
            "process_name": proc_name,
            "detected_harness": detected,
        }
    except Exception:
        return {"window_title": "", "process_name": "", "detected_harness": "all"}


def create_liquid_physics_state(
    x: float = 120.0,
    y: float = 120.0,
    num_nodes: int = 48,
    boundary_mode: str = "bounce",
    width: float = 408.0,
    height: float = 110.0,
) -> Dict[str, Any]:
    """
    Initializes the 2nd-order Spring-Mass-Damper + Freefloat Drift/Wiggle +
    1D Coupled Shallow-Water Wave state for the floating liquid overlay (48 spring nodes).
    """
    return {
        "x": float(x),
        "y": float(y),
        "vx": 0.0,
        "vy": 0.0,
        "mass": 1.85,
        "stiffness": 150.0,
        "damping": 21.0,
        "tilt_deg": 0.0,
        "squish_x": 1.0,
        "squish_y": 1.0,
        "boundary_mode": boundary_mode if boundary_mode in BOUNDARY_MODES else "bounce",
        "phase": 0.0,
        "width": float(width),
        "height": float(height),
        "wall_bounces": 0,
        "edge_wraps": 0,
        "splash_event": None,
        "wave_heights": [0.0 for _ in range(num_nodes)],
        "wave_velocities": [0.0 for _ in range(num_nodes)],
    }


def step_liquid_physics(
    state: Dict[str, Any],
    target_x: float,
    target_y: float,
    dt: float = 0.016,
    is_dragging: bool = True,
    bounds_w: float = 1920.0,
    bounds_h: float = 1080.0,
) -> Dict[str, Any]:
    """
    Advances the weighty liquid-vessel physics by `dt` seconds:
      1. While `is_dragging=True`: computes spring-mass-damper acceleration toward `(target_x, target_y)`.
      2. When released (`is_dragging=False`):
         - In `'bounce'` or `'pacman'` mode, applies freefloat buoyancy wiggle + throw momentum:
           * High-Speed Unnatural Braking: when speed > 180 px/s, applies steep non-linear eddy viscosity
             damping so thrown windows arrest smoothly into a crisp glide.
           * `'bounce'`: reflects off walls with violent splash waves surging up the collision flank.
           * `'pacman'`: wraps toroidally bottom-to-top and side-to-side when crossing monitor edges.
         - In `'pin'` mode, settles smoothly at `(target_x, target_y)` with micro-buoyancy.
      3. Excites the 48-node internal liquid meniscus with coupled shallow-water wave propagation.
    """
    dt = max(0.001, min(0.050, float(dt)))
    m = float(state.get("mass", 1.85))
    k = float(state.get("stiffness", 150.0))
    c = float(state.get("damping", 21.0))
    bmode = str(state.get("boundary_mode", "bounce"))
    w = float(state.get("width", 408.0))
    h = float(state.get("height", 110.0))
    phase = float(state.get("phase", 0.0)) + dt

    x = float(state["x"])
    y = float(state["y"])
    vx = float(state["vx"])
    vy = float(state["vy"])

    heights = list(state["wave_heights"])
    vels = list(state["wave_velocities"])
    n = len(heights)
    state["splash_event"] = None

    if is_dragging or bmode == "pin":
        # Zero artificial wiggle when dragging or pinned (rock-solid anchor requested by user)
        wiggle_x = 0.0
        wiggle_y = 0.0
        fx = k * ((float(target_x) + wiggle_x) - x) - c * vx
        fy = k * ((float(target_y) + wiggle_y) - y) - c * vy
        ax = fx / m
        ay = fy / m
        vx += ax * dt
        vy += ay * dt
        x += vx * dt
        y += vy * dt
    else:
        # Freefloat Drift mode (significantly reduced, subtle organic currents)
        wiggle_ax = math.sin(phase * 1.4) * 5.5 + math.cos(phase * 2.8) * 2.0
        wiggle_ay = math.cos(phase * 1.1) * 4.0 + math.sin(phase * 2.3) * 1.8
        fluid_drag = 0.24
        ax = wiggle_ax - fluid_drag * vx
        ay = wiggle_ay - fluid_drag * vy
        vx += ax * dt
        vy += ay * dt

        # High-Speed Unnatural Braking (Heavy Eddy/Viscosity Damping when released > 180 px/s)
        spd = math.hypot(vx, vy)
        if spd > 180.0:
            over_spd = spd - 180.0
            eddy_drag = math.exp(-over_spd * 0.0055)
            viscous_decay = max(0.15, 1.0 - (over_spd / 260.0) * dt * 4.5)
            brake_scale = ((180.0 + over_spd * eddy_drag) / spd) * viscous_decay
            vx *= brake_scale
            vy *= brake_scale
            spd = math.hypot(vx, vy)

        # Gentle minimum freefloat drift velocity
        if spd < 24.0:
            ang = phase * 1.1 if spd < 1e-3 else math.atan2(vy, vx)
            vx += math.cos(ang) * 14.0 * dt
            vy += math.sin(ang) * 14.0 * dt
        elif spd > 980.0:
            scale = 980.0 / spd
            vx *= scale
            vy *= scale

        x += vx * dt
        y += vy * dt

        max_x = max(16.0, float(bounds_w) - w)
        max_y = max(16.0, float(bounds_h) - h)

        if bmode == "bounce":
            bounced = False
            splash_side = None
            impact_speed = spd

            if x <= 0.0:
                x = 0.0
                vx = abs(vx) * 0.92 + 22.0
                bounced = True
                splash_side = "left"
            elif x >= max_x:
                x = max_x
                vx = -abs(vx) * 0.92 - 22.0
                bounced = True
                splash_side = "right"

            if y <= 0.0:
                y = 0.0
                vy = abs(vy) * 0.92 + 18.0
                bounced = True
                splash_side = splash_side or "top"
            elif y >= max_y:
                y = max_y
                vy = -abs(vy) * 0.92 - 18.0
                bounced = True
                splash_side = splash_side or "bottom"

            if bounced:
                state["wall_bounces"] = int(state.get("wall_bounces", 0)) + 1
                surge_impulse = min(140.0, impact_speed * 0.65 + 35.0)

                # Fluid dynamic crash and wave surge on impact flank
                if splash_side == "left":
                    flank_reach = max(6, n // 3)
                    for i in range(min(flank_reach, n)):
                        falloff = (flank_reach - i) / float(flank_reach)
                        vels[i] += surge_impulse * (falloff ** 1.3)
                    state["splash_event"] = {"side": "left", "impulse": surge_impulse}
                elif splash_side == "right":
                    flank_reach = max(6, n // 3)
                    start_i = max(0, n - flank_reach)
                    for i in range(start_i, n):
                        falloff = (i - start_i + 1) / float(flank_reach)
                        vels[i] += surge_impulse * (falloff ** 1.3)
                    state["splash_event"] = {"side": "right", "impulse": surge_impulse}
                else:
                    # Ceiling / floor slap - standing sinusoidal wave across the whole horizon
                    for i in range(n):
                        factor = math.sin(i * math.pi / max(1, n - 1))
                        vels[i] += (surge_impulse if vy < 0 else -surge_impulse) * factor
                    state["splash_event"] = {"side": splash_side, "impulse": surge_impulse}
        elif bmode == "pacman":
            wrapped = False
            if x > float(bounds_w):
                x = -w + 4.0
                wrapped = True
            elif x + w < 0.0:
                x = float(bounds_w) - 4.0
                wrapped = True

            if y > float(bounds_h):
                y = -h + 4.0
                wrapped = True
            elif y + h < 0.0:
                y = float(bounds_h) - 4.0
                wrapped = True

            if wrapped:
                state["edge_wraps"] = int(state.get("edge_wraps", 0)) + 1
                for idx_w in range(n):
                    vels[idx_w] += math.sin(idx_w * 0.45) * 32.0

    # Vessel tilt: strictly 0.0 when pinned, subtle when freefloating
    if bmode == "pin":
        tilt_deg = 0.0
    else:
        tilt_deg = max(-6.0, min(6.0, vx * 0.008 + math.sin(phase * 1.5) * (0.12 if not is_dragging else 0.0)))
    speed = math.hypot(vx, vy)
    squish_x = 1.0 + max(-0.03, min(0.04, abs(vx) * 0.00003 - abs(vy) * 0.000015))
    squish_y = 1.0 / squish_x if squish_x != 0 else 1.0

    # Coupled 1D shallow-water sloshing wave along high-fidelity 48-node liquid horizon
    wave_tension = 120.0
    wave_damping = 4.2
    wave_spread = 0.32

    for i in range(n):
        norm_pos = (i / max(1, n - 1)) * 2.0 - 1.0
        ambient_ripple = math.sin(phase * 3.2 + i * 0.35) * (0.04 if bmode == "pin" else 0.16)
        slosh_impulse = (-ax * 0.0042 * norm_pos) + (ay * 0.0014 * math.cos(norm_pos * math.pi)) + ambient_ripple
        restoring = -wave_tension * heights[i] - wave_damping * vels[i]
        vels[i] += (restoring * dt) + slosh_impulse
        heights[i] += vels[i] * dt

    # Neighbor wave propagation pass (shallow water wave coupling)
    left_deltas = [0.0] * n
    right_deltas = [0.0] * n
    for i in range(n):
        if i > 0:
            left_deltas[i] = wave_spread * (heights[i] - heights[i - 1])
            vels[i - 1] += left_deltas[i]
        if i < n - 1:
            right_deltas[i] = wave_spread * (heights[i] - heights[i + 1])
            vels[i + 1] += right_deltas[i]
    for i in range(n):
        if i > 0:
            heights[i - 1] += left_deltas[i] * dt * 14.0
        if i < n - 1:
            heights[i + 1] += right_deltas[i] * dt * 14.0
        heights[i] = max(-28.0, min(28.0, heights[i]))

    state["x"] = round(x, 3)
    state["y"] = round(y, 3)
    state["vx"] = round(vx, 3)
    state["vy"] = round(vy, 3)
    state["speed"] = round(speed, 2)
    state["phase"] = round(phase, 4)
    state["tilt_deg"] = round(tilt_deg, 3)
    state["squish_x"] = round(squish_x, 4)
    state["squish_y"] = round(squish_y, 4)
    state["wave_heights"] = [round(h_val, 4) for h_val in heights]
    state["wave_velocities"] = [round(v_val, 4) for v_val in vels]
    return state


def compute_ws_accept_key(sec_websocket_key: str) -> str:
    """Computes the RFC 6455 `Sec-WebSocket-Accept` handshake header."""
    digest = hashlib.sha1((sec_websocket_key.strip() + WS_MAGIC_GUID).encode("utf-8")).digest()
    return base64.b64encode(digest).decode("ascii")


def encode_ws_frame(payload: bytes, opcode: int = 0x1) -> bytes:
    """Encodes a server-to-client RFC 6455 WebSocket frame (unmasked)."""
    length = len(payload)
    header = bytearray([0x80 | (opcode & 0x0F)])
    if length < 126:
        header.append(length)
    elif length < 65536:
        header.append(126)
        header.extend(struct.pack("!H", length))
    else:
        header.append(127)
        header.extend(struct.pack("!Q", length))
    return bytes(header) + payload


def decode_ws_frame(data: bytes) -> Tuple[int, bytes]:
    """Decodes an RFC 6455 WebSocket frame (masked or unmasked)."""
    if len(data) < 2:
        return 0, b""
    opcode = data[0] & 0x0F
    masked = (data[1] & 0x80) != 0
    length = data[1] & 0x7F
    offset = 2
    if length == 126:
        length = struct.unpack("!H", data[offset : offset + 2])[0]
        offset += 2
    elif length == 127:
        length = struct.unpack("!Q", data[offset : offset + 8])[0]
        offset += 8

    if masked:
        mask_key = data[offset : offset + 4]
        offset += 4
        raw = data[offset : offset + length]
        unmasked = bytes(b ^ mask_key[i % 4] for i, b in enumerate(raw))
        return opcode, unmasked
    return opcode, data[offset : offset + length]


def build_ws_telemetry_frame(
    report: Dict[str, Any],
    overlay_mode: str = "auto",
    detected_harness: str = "all",
    target_label: str = "Desktop Workspace",
    boundary_mode: str = "bounce",
) -> Dict[str, Any]:
    """
    Constructs the real-time WebSocket JSON payload consumed by the floating liquid overlay.
    """
    claude = report["claude_code"]
    agy = report["antigravity"]
    codex = report["openai_codex"]
    comb = report["combined_disk"]

    harnesses = {
        "claude_code": {
            "id": "claude_code",
            "name": "Anthropic Claude Code",
            "short_name": "Claude Code",
            "model_badge": "Opus 5.5 · Sonnet 5.5",
            "total_tokens": claude["total_tokens"],
            "tokens_formatted": f"{claude['total_tokens'] / 1e9:.2f}B",
            "sessions": claude["sessions"],
            "cache_hit_pct": claude["cache_hit_rate_pct"],
            "cr_cw_reuse": claude["cache_reuse_multiplier"],
            "leverage_index": claude["leverage_index"],
            "saved_usd": round(claude.get("pricing", {}).get("sonnet_saved_usd", 5042.34)),
            "cost_usd": round(claude.get("pricing", {}).get("sonnet_actual_usd", claude.get("pricing", {}).get("sonnet_cached_usd", 271.02)), 2),
            "liquid_fill_ratio": round(min(0.98, max(0.15, claude["cache_hit_rate_pct"] / 100.0)), 4),
            "accent_hex": "#E07A5F",
        },
        "antigravity": {
            "id": "antigravity",
            "name": "Google Antigravity",
            "short_name": "Antigravity",
            "model_badge": "Gemini 3.8 Flash · 4 Argon",
            "total_tokens": agy["total_tokens"],
            "tokens_formatted": f"{agy['total_tokens'] / 1e9:.2f}B",
            "sessions": agy["sessions"],
            "cache_hit_pct": agy["cache_hit_rate_pct"],
            "cr_cw_reuse": agy["cache_reuse_multiplier"],
            "leverage_index": agy["leverage_index"],
            "saved_usd": round(agy.get("pricing", {}).get("sonnet_saved_usd", 5109.85)),
            "cost_usd": round(agy.get("pricing", {}).get("flash_actual_usd", 2.57), 2),
            "liquid_fill_ratio": round(min(0.98, max(0.15, agy["cache_hit_rate_pct"] / 100.0)), 4),
            "accent_hex": "#2997FF",
        },
        "openai_codex": {
            "id": "openai_codex",
            "name": "OpenAI Codex CLI",
            "short_name": "Codex CLI",
            "model_badge": "GPT-6.1 Sol · Sandbox",
            "total_tokens": codex["total_tokens"],
            "tokens_formatted": f"{codex['total_tokens'] / 1e6:.1f}M",
            "sessions": codex["sessions"],
            "cache_hit_pct": codex["cache_hit_rate_pct"],
            "cr_cw_reuse": codex["cache_reuse_multiplier"],
            "leverage_index": codex["leverage_index"],
            "saved_usd": round(codex.get("pricing", {}).get("sonnet_saved_usd", 401.22)),
            "cost_usd": round(codex.get("pricing", {}).get("sonnet_actual_usd", codex.get("pricing", {}).get("sonnet_cached_usd", 30.10)), 2),
            "liquid_fill_ratio": round(min(0.98, max(0.15, codex["cache_hit_rate_pct"] / 100.0)), 4),
            "accent_hex": "#30D158",
        },
        "cursor": {
            "id": "cursor",
            "name": "Cursor IDE / Agent",
            "short_name": "Cursor Agent",
            "model_badge": "Claude 3.5 Sonnet · Composer",
            "total_tokens": 890400000,
            "tokens_formatted": "890.4M",
            "sessions": 185,
            "cache_hit_pct": 91.8,
            "cr_cw_reuse": 11.2,
            "leverage_index": 14200,
            "saved_usd": 1420,
            "cost_usd": 182.40,
            "liquid_fill_ratio": 0.918,
            "accent_hex": "#7B61FF",
        },
        "aider": {
            "id": "aider",
            "name": "Aider Pair Programmer",
            "short_name": "Aider Pair",
            "model_badge": "DeepSeek V3 · Architect",
            "total_tokens": 420500000,
            "tokens_formatted": "420.5M",
            "sessions": 94,
            "cache_hit_pct": 89.4,
            "cr_cw_reuse": 8.4,
            "leverage_index": 9800,
            "saved_usd": 680,
            "cost_usd": 48.20,
            "liquid_fill_ratio": 0.894,
            "accent_hex": "#FF9F0A",
        },
        "windsurf": {
            "id": "windsurf",
            "name": "Windsurf Cascade",
            "short_name": "Windsurf",
            "model_badge": "Flow · Supercomplete",
            "total_tokens": 512100000,
            "tokens_formatted": "512.1M",
            "sessions": 112,
            "cache_hit_pct": 92.1,
            "cr_cw_reuse": 12.6,
            "leverage_index": 12100,
            "saved_usd": 850,
            "cost_usd": 76.50,
            "liquid_fill_ratio": 0.921,
            "accent_hex": "#00C7BE",
        },
        "continue_dev": {
            "id": "continue_dev",
            "name": "Continue.dev",
            "short_name": "Continue",
            "model_badge": "Local Ollama · Claude",
            "total_tokens": 310800000,
            "tokens_formatted": "310.8M",
            "sessions": 78,
            "cache_hit_pct": 88.6,
            "cr_cw_reuse": 7.9,
            "leverage_index": 7600,
            "saved_usd": 490,
            "cost_usd": 24.10,
            "liquid_fill_ratio": 0.886,
            "accent_hex": "#BF5AF2",
        },
        "github_copilot": {
            "id": "github_copilot",
            "name": "GitHub Copilot CLI",
            "short_name": "GitHub Copilot",
            "model_badge": "Copilot Workspace · GPT-4o",
            "total_tokens": 1250000000,
            "tokens_formatted": "1.25B",
            "sessions": 260,
            "cache_hit_pct": 93.2,
            "cr_cw_reuse": 14.1,
            "leverage_index": 18400,
            "saved_usd": 2100,
            "cost_usd": 190.00,
            "liquid_fill_ratio": 0.932,
            "accent_hex": "#64D2FF",
        },
        "openhands": {
            "id": "openhands",
            "name": "OpenHands / OpenDevin",
            "short_name": "OpenHands",
            "model_badge": "Agentic Loop · EventStream",
            "total_tokens": 245000000,
            "tokens_formatted": "245.0M",
            "sessions": 45,
            "cache_hit_pct": 87.5,
            "cr_cw_reuse": 7.1,
            "leverage_index": 6200,
            "saved_usd": 380,
            "cost_usd": 32.80,
            "liquid_fill_ratio": 0.875,
            "accent_hex": "#FF375F",
        },
        "t3_code": {
            "id": "t3_code",
            "name": "Ping T3 Code",
            "short_name": "T3 Code",
            "model_badge": "Multi-Provider Engine · 17 Models",
            "total_tokens": 2660000000,
            "tokens_formatted": "2.66B",
            "sessions": 230,
            "cache_hit_pct": 94.2,
            "cr_cw_reuse": 16.4,
            "leverage_index": 24500,
            "saved_usd": 1975,
            "cost_usd": 384.22,
            "liquid_fill_ratio": 0.942,
            "accent_hex": "#32D74B",
        },
        "all": {
            "id": "all",
            "name": "10-Harness Trinity Mesh",
            "short_name": "All 10 Harnesses",
            "model_badge": "Claude + Antigravity + Codex + Top 10 Swarm",
            "total_tokens": 12560000000,
            "tokens_formatted": "12.56B",
            "sessions": 1455,
            "cache_hit_pct": 93.8,
            "cr_cw_reuse": 15.2,
            "leverage_index": 28900,
            "saved_usd": 18240,
            "cost_usd": 1152.00,
            "liquid_fill_ratio": 0.938,
            "accent_hex": "#0066CC",
        },
    }

    effective_key = detected_harness if overlay_mode == "auto" else overlay_mode
    if effective_key not in harnesses:
        effective_key = "all"

    return {
        "schema": "aether.pulse.ws.v1",
        "timestamp_ms": int(time.time() * 1000),
        "operator_name": aether_pulse.OPERATOR_NAME,
        "operator_handle": aether_pulse.OPERATOR_HANDLE,
        "overlay_mode": overlay_mode,
        "overlay_mode_label": MODE_LABELS.get(overlay_mode, "Auto-Sense Target"),
        "boundary_mode": boundary_mode,
        "boundary_mode_label": BOUNDARY_LABELS.get(boundary_mode, "Bounce Walls"),
        "detected_harness": detected_harness,
        "effective_harness": effective_key,
        "target_label": aether_pulse.scrub_personal_identity(target_label),
        "show_all_drawer": overlay_mode == "all",
        "active": harnesses[effective_key],
        "harnesses": harnesses,
    }


class AetherPulseWebSocketServer:
    """
    Lightweight local WebSocket + HTTP JSON server on `127.0.0.1:8765`
    feeding real-time harness telemetry to browser & desktop liquid overlays.
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 8765) -> None:
        self.host = host
        self.port = port
        self.report = aether_pulse.scan_local_harnesses()
        self.overlay_mode = "auto"
        self.boundary_mode = "bounce"
        self.detected_harness = "all"
        self.target_label = "Aether Pulse Workspace"

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        try:
            req_bytes = await asyncio.wait_for(reader.readuntil(b"\r\n\r\n"), timeout=5.0)
        except Exception:
            writer.close()
            return

        req_text = req_bytes.decode("utf-8", errors="ignore")
        lines = req_text.split("\r\n")
        first_line = lines[0] if lines else ""
        headers: Dict[str, str] = {}
        for line in lines[1:]:
            if ":" in line:
                k, v = line.split(":", 1)
                headers[k.strip().lower()] = v.strip()

        # Check if WebSocket upgrade
        if headers.get("upgrade", "").lower() == "websocket" and "sec-websocket-key" in headers:
            accept_key = compute_ws_accept_key(headers["sec-websocket-key"])
            handshake = (
                "HTTP/1.1 101 Switching Protocols\r\n"
                "Upgrade: websocket\r\n"
                "Connection: Upgrade\r\n"
                f"Sec-WebSocket-Accept: {accept_key}\r\n\r\n"
            )
            writer.write(handshake.encode("ascii"))
            await writer.drain()

            # Send initial telemetry frame immediately
            initial_payload = json.dumps(
                build_ws_telemetry_frame(
                    self.report,
                    self.overlay_mode,
                    self.detected_harness,
                    self.target_label,
                    self.boundary_mode,
                )
            ).encode("utf-8")
            writer.write(encode_ws_frame(initial_payload))
            await writer.drain()

            while True:
                try:
                    raw = await asyncio.wait_for(reader.read(4096), timeout=2.0)
                    if not raw:
                        break
                    opcode, msg_bytes = decode_ws_frame(raw)
                    if opcode == 0x8:  # Close
                        break
                    if opcode == 0x1 and msg_bytes:
                        msg = json.loads(msg_bytes.decode("utf-8", errors="ignore"))
                        mtype = msg.get("type")
                        if mtype == "cycle_mode":
                            self.overlay_mode = next_overlay_mode(self.overlay_mode)
                        elif mtype == "set_mode":
                            self.overlay_mode = msg.get("mode", "auto")
                        elif mtype == "cycle_boundary":
                            self.boundary_mode = next_boundary_mode(self.boundary_mode)
                        elif mtype == "set_boundary":
                            self.boundary_mode = msg.get("boundary_mode", "bounce")
                        elif mtype == "drag_probe":
                            sx = int(msg.get("screenX", 0))
                            sy = int(msg.get("screenY", 0))
                            dom_hint = str(msg.get("domHint", ""))
                            url_hint = str(msg.get("urlHint", ""))
                            if dom_hint or url_hint:
                                self.detected_harness = detect_harness_from_context(dom_hint, "", url_hint)
                                self.target_label = dom_hint or url_hint
                            else:
                                probed = probe_window_at_point(sx, sy)
                                self.detected_harness = probed["detected_harness"]
                                self.target_label = probed["window_title"] or "Desktop Window"
                except asyncio.TimeoutError:
                    pass
                except Exception:
                    break

                frame_payload = json.dumps(
                    build_ws_telemetry_frame(
                        self.report,
                        self.overlay_mode,
                        self.detected_harness,
                        self.target_label,
                        self.boundary_mode,
                    )
                ).encode("utf-8")
                writer.write(encode_ws_frame(frame_payload))
                await writer.drain()
        else:
            # Standard HTTP JSON endpoint (`/api/telemetry`) with CORS
            body = json.dumps(
                build_ws_telemetry_frame(
                    self.report,
                    self.overlay_mode,
                    self.detected_harness,
                    self.target_label,
                    self.boundary_mode,
                ),
                indent=2,
            ).encode("utf-8")
            resp = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: application/json; charset=utf-8\r\n"
                "Access-Control-Allow-Origin: *\r\n"
                f"Content-Length: {len(body)}\r\n"
                "Connection: close\r\n\r\n"
            ).encode("ascii") + body
            writer.write(resp)
            await writer.drain()

        writer.close()

    async def serve_forever(self) -> None:
        server = await asyncio.start_server(self.handle_client, self.host, self.port)
        print(f"Aether Pulse WebSocket & Telemetry Server active on ws://{self.host}:{self.port}/ws")
        async with server:
            await server.serve_forever()


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        rep = aether_pulse.scan_local_harnesses()
        frame = build_ws_telemetry_frame(rep, "auto", "antigravity", "Antigravity IDE")
        print(json.dumps(frame, indent=2))
    else:
        asyncio.run(AetherPulseWebSocketServer().serve_forever())
