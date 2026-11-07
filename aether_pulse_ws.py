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
OVERLAY_MODES = ["auto", "all", "claude_code", "antigravity", "openai_codex"]
BOUNDARY_MODES = ["bounce", "pacman", "pin"]

MODE_LABELS = {
    "auto": "Auto-Sense Target",
    "all": "All 3 Harnesses",
    "claude_code": "Claude Code (Pinned)",
    "antigravity": "Antigravity (Pinned)",
    "openai_codex": "OpenAI Codex (Pinned)",
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
    """
    blob = f"{window_title} {process_name} {url_or_target}".lower()

    if any(k in blob for k in ("codex", "chatgpt.com", "openai", "gpt-6", "o3-pro", "sandbox")):
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
    num_nodes: int = 9,
    boundary_mode: str = "bounce",
    width: float = 392.0,
    height: float = 104.0,
) -> Dict[str, Any]:
    """
    Initializes the 2nd-order Spring-Mass-Damper + Freefloat Drift/Wiggle +
    1D Coupled Shallow-Water Wave state for the floating liquid overlay.
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
           * `'bounce'`: reflects off `[0, bounds_w - width] x [0, bounds_h - height]` walls with splash impulse.
           * `'pacman'`: wraps toroidally bottom-to-top and side-to-side when crossing monitor/viewport edges.
         - In `'pin'` mode, settles smoothly at `(target_x, target_y)` with micro-buoyancy.
      3. Excites the internal liquid meniscus wave heights and propagates coupled neighbor waves.
    """
    dt = max(0.001, min(0.050, float(dt)))
    m = float(state.get("mass", 1.85))
    k = float(state.get("stiffness", 150.0))
    c = float(state.get("damping", 21.0))
    bmode = str(state.get("boundary_mode", "bounce"))
    w = float(state.get("width", 392.0))
    h = float(state.get("height", 104.0))
    phase = float(state.get("phase", 0.0)) + dt

    x = float(state["x"])
    y = float(state["y"])
    vx = float(state["vx"])
    vy = float(state["vy"])

    heights = list(state["wave_heights"])
    vels = list(state["wave_velocities"])
    n = len(heights)

    if is_dragging or bmode == "pin":
        wiggle_x = math.sin(phase * 2.6) * 2.5 if not is_dragging else 0.0
        wiggle_y = math.cos(phase * 2.1) * 2.0 if not is_dragging else 0.0
        fx = k * ((float(target_x) + wiggle_x) - x) - c * vx
        fy = k * ((float(target_y) + wiggle_y) - y) - c * vy
        ax = fx / m
        ay = fy / m
        vx += ax * dt
        vy += ay * dt
        x += vx * dt
        y += vy * dt
    else:
        # Freefloat Drift + Wiggle mode after letting go of drag
        wiggle_ax = math.sin(phase * 2.4) * 42.0 + math.cos(phase * 5.1) * 18.0
        wiggle_ay = math.cos(phase * 1.9) * 34.0 + math.sin(phase * 4.3) * 15.0
        fluid_drag = 0.22
        ax = wiggle_ax - fluid_drag * vx
        ay = wiggle_ay - fluid_drag * vy
        vx += ax * dt
        vy += ay * dt

        # Maintain pleasant minimum freefloat drift velocity so it stays alive when released
        spd = math.hypot(vx, vy)
        if spd < 38.0:
            ang = phase * 1.3 if spd < 1e-3 else math.atan2(vy, vx)
            vx += math.cos(ang) * 26.0 * dt
            vy += math.sin(ang) * 26.0 * dt
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
            if x <= 0.0:
                x = 0.0
                vx = abs(vx) * 0.92 + 18.0
                bounced = True
            elif x >= max_x:
                x = max_x
                vx = -abs(vx) * 0.92 - 18.0
                bounced = True

            if y <= 0.0:
                y = 0.0
                vy = abs(vy) * 0.92 + 14.0
                bounced = True
            elif y >= max_y:
                y = max_y
                vy = -abs(vy) * 0.92 - 14.0
                bounced = True

            if bounced:
                state["wall_bounces"] = int(state.get("wall_bounces", 0)) + 1
                mid = n // 2
                vels[mid] += 36.0 if vy < 0 else -36.0
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
                    vels[idx_w] += math.sin(idx_w * 0.9) * 28.0

    # Vessel tilt and subtle liquid-weight squish
    tilt_deg = max(-10.5, min(10.5, vx * 0.014 + math.sin(phase * 3.2) * (0.65 if not is_dragging else 0.0)))
    speed = math.hypot(vx, vy)
    squish_x = 1.0 + max(-0.04, min(0.06, abs(vx) * 0.00004 - abs(vy) * 0.00002))
    squish_y = 1.0 / squish_x if squish_x != 0 else 1.0

    # Coupled 1D shallow-water sloshing wave along the liquid horizon
    wave_tension = 95.0
    wave_damping = 4.8
    wave_spread = 0.28

    for i in range(n):
        norm_pos = (i / max(1, n - 1)) * 2.0 - 1.0
        ambient_ripple = math.sin(phase * 3.4 + i * 0.65) * 0.35
        slosh_impulse = (-ax * 0.0038 * norm_pos) + (ay * 0.0012 * math.cos(norm_pos * math.pi)) + ambient_ripple
        restoring = -wave_tension * heights[i] - wave_damping * vels[i]
        vels[i] += (restoring * dt) + slosh_impulse
        heights[i] += vels[i] * dt

    # Neighbor wave propagation pass
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
            heights[i - 1] += left_deltas[i] * dt * 12.0
        if i < n - 1:
            heights[i + 1] += right_deltas[i] * dt * 12.0
        heights[i] = max(-18.0, min(18.0, heights[i]))

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
            "saved_usd": round(claude["pricing"]["sonnet_saved_usd"]),
            "cost_usd": round(claude["pricing"]["sonnet_actual_usd"], 2),
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
            "saved_usd": round(agy["pricing"]["sonnet_saved_usd"]),
            "cost_usd": round(agy["pricing"]["flash_actual_usd"], 2),
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
            "saved_usd": round(codex["pricing"]["sonnet_saved_usd"]),
            "cost_usd": round(codex["pricing"]["sonnet_actual_usd"], 2),
            "liquid_fill_ratio": round(min(0.98, max(0.15, codex["cache_hit_rate_pct"] / 100.0)), 4),
            "accent_hex": "#30D158",
        },
        "all": {
            "id": "all",
            "name": "3-Harness Trinity Mesh",
            "short_name": "All 3 Harnesses",
            "model_badge": "Claude + Antigravity + Codex",
            "total_tokens": comb["total_tokens"],
            "tokens_formatted": f"{comb['total_tokens'] / 1e9:.2f}B",
            "sessions": comb["sessions"],
            "cache_hit_pct": comb["cache_hit_rate_pct"],
            "cr_cw_reuse": comb["cache_reuse_multiplier"],
            "leverage_index": comb["leverage_index"],
            "saved_usd": round(comb["pricing"]["sonnet_saved_usd"]),
            "cost_usd": round(comb["pricing"]["sonnet_actual_usd"], 2),
            "liquid_fill_ratio": round(min(0.98, max(0.15, comb["cache_hit_rate_pct"] / 100.0)), 4),
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
