#!/usr/bin/env python3
"""
Aether Pulse - AAA Desktop Liquid Floating HUD & Real-Time Telemetry Bar
Author: Eloquent (@mjeanhudson-dev)

Features:
- Pure Tkinter zero-dependency desktop liquid capsule with 100% transparent outer masking.
- Multi-pass optical subpixel anti-aliasing on exterior capsule perimeter.
- Apple macOS circular traffic light controls on the TOP-LEFT (Close, Minimize, Settings).
- AAA Fluid Dynamic Simulation:
    * 100% flat bottom base with precision corner fillets hugging the inner glass capsule.
    * Ultra-high resolution Catmull-Rom cubic spline (470+ continuous points) with ambient occlusion shadow.
    * Multi-layer volumetric rendering: deep undercurrent, radiant primary mass, subsurface caustics.
    * Effervescent agent fizzing bubbles: high-frequency sparkling micro-bubbles when active harnesses run.
    * Dynamic Lava mode: liquid transforms into glowing molten magma when approaching 5-hr limits.
    * Flashing thermal radiation strobe for weekly/monthly quota sentinel alerts.
    * Tangible physical weighiness (3.2 kg mass sensation, heavy inertial glide, and kinetic momentum transfer).
    * Rock-solid pinned anchor with zero wiggle.
- 8 Rich Themes: Obsidian Dark, Cupertino Light, Retro Synthwave, Classical Horology, Windows 95,
  Terminal Matrix, Nuclear Hazard, and Volcanic Lava + Detailed Custom Color Picker.
- 4-button domed tactile side column: [≋ MODE], [🎨 THEME], [BNC/PAC/PIN], and [🌐 WEB DASHBOARD].
- Native System Tray integration with icon and instant restore/minimize.
- Detailed Cupertino Settings modal to customize all features, themes, and dynamics.
"""

from __future__ import annotations

import ctypes
import json
import math
import os
import random
import sys
import time
import tkinter as tk
from tkinter import font as tkfont
from tkinter import colorchooser
import webbrowser
from typing import Any, Dict, List, Optional, Tuple

import aether_pulse
import aether_pulse_ws

# Enable native Per-Monitor High DPI V2 awareness on Windows
if sys.platform == "win32":
    try:
        ctypes.windll.user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
    except Exception:
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except Exception:
            try:
                ctypes.windll.user32.SetProcessDPIAware()
            except Exception:
                pass


try:
    import pystray
    from PIL import Image
    HAS_TRAY = True
except ImportError:
    HAS_TRAY = False

SETTINGS_FILE = os.path.abspath("aether_pulse_settings.json")
DEFAULT_SETTINGS: Dict[str, Any] = {
    "overlay_mode": "auto",
    "boundary_mode": "bounce",
    "theme": "dark",
    "enable_particles": True,
    "enable_bubbles": True,
    "enable_fizz": True,
    "simulate_lava_5hr": True,
    "topmost": True,
    "accounting_lens": "specular",
    "close_to_tray": True,
    "custom_accent": "#0066CC",
    "custom_liquid": "#0E243B",
    "active_subscriptions": ["claude_code", "antigravity", "openai_codex"],
    "custom_tier_name": "",
}

# Humorous subscription-based tier engine
SUBSCRIPTION_TIERS: Dict[int, Dict[str, str]] = {
    1: {"name": "Unoemono", "tagline": "Solo lone wolf with one exhausted token allowance"},
    2: {"name": "Couples Fighting", "tagline": "Two CLIs arguing over who caused the merge conflict"},
    3: {"name": "Trinity", "tagline": "The sacred three-way prompt-caching triangle"},
    4: {"name": "Quap", "tagline": "Four harnesses deep in incoherent multi-model synergy"},
    5: {"name": "Pentagoon", "tagline": "Five subscriptions, certified AI terminal goon squad"},
    6: {"name": "Six-Pack Meltdown", "tagline": "Six subscriptions shredding your monthly compute budget"},
    7: {"name": "Seven Deadly Subs", "tagline": "Seven deadly sins of context bloat and rate limits"},
    8: {"name": "Octo-Chaos", "tagline": "Eight tentacles flailing across every shell session"},
    9: {"name": "Cloud Nine Overdraft", "tagline": "Floating on infinite context while your card declines"},
    10: {"name": "Ten-Ring Circus", "tagline": "The full ten-ring unhinged developer clown show"},
}

AVAILABLE_SUBSCRIPTIONS = [
    ("claude_code", "Claude Code ($20/mo)"),
    ("antigravity", "Google Antigravity ($20/mo)"),
    ("openai_codex", "OpenAI Codex ($20/mo)"),
    ("cursor", "Cursor Pro ($20/mo)"),
    ("windsurf", "Windsurf Cascade ($15/mo)"),
    ("aider", "Aider CLI (API)"),
    ("devin", "Devin ($500/mo)"),
    ("copilot", "GitHub Copilot ($10/mo)"),
    ("perplexity", "Perplexity Pro ($20/mo)"),
    ("t3_code", "Ping T3 Code ($25/mo)"),
]

def get_subscription_tier(count: int, custom_name: str = "") -> Dict[str, str]:
    if custom_name and custom_name.strip():
        return {"name": custom_name.strip(), "tagline": f"Custom User Loadout ({count} Subscriptions)"}
    if count in SUBSCRIPTION_TIERS:
        return SUBSCRIPTION_TIERS[count]
    if count > 10:
        return {"name": f"Incoherent Multiverse ({count})", "tagline": f"{count} subscriptions deep in the simulation"}
    return SUBSCRIPTION_TIERS.get(count, {"name": "Unoemono", "tagline": "Solo lone wolf"})

BOUNDARY_LABELS = {
    "bounce": "Bounce Walls",
    "pacman": "Pac-Man Wrap",
    "pin": "Pinned Anchor",
}

BOUNDARY_SHORT = {
    "bounce": "BNC",
    "pacman": "PAC",
    "pin": "PIN",
}

THEME_ORDER = ["dark", "light", "retro", "classical", "win95", "terminal", "nuclear", "lava"]

THEME_PALETTES: Dict[str, Dict[str, Any]] = {
    "dark": {
        "name": "Obsidian Dark",
        "is_dark": True,
        "mask_bg": "#010101",
        "pill_bg": "#0E0F12",
        "pill_shadow": "#050608",
        "border": "#22242B",
        "border_highlight": "#32353F",
        "header": "#E8E9ED",
        "primary_text": "#F2F3F7",
        "secondary_text": "#828692",
        "subtle_text": "#545762",
        "divider": "#1E2026",
        "button_bg": "#15161B",
        "button_border": "#282A33",
        "button_highlight": "#383B47",
        "button_hover": "#1F2128",
        "fluid_deep": "#081320",
        "fluid_surface": "#10253D",
        "caustic_color": "#28608F",
        "bubble_color": "#3B7BAE",
        "particle_color": "#D2D4DC",
        "ao_shadow": "#020407",
    },
    "light": {
        "name": "Cupertino Light",
        "is_dark": False,
        "mask_bg": "#010101",
        "pill_bg": "#F8F8FA",
        "pill_shadow": "#D6D6DC",
        "border": "#E5E5EA",
        "border_highlight": "#FFFFFF",
        "header": "#1D1D1F",
        "primary_text": "#000000",
        "secondary_text": "#5A5A60",
        "subtle_text": "#8E8E93",
        "divider": "#E5E5EA",
        "button_bg": "#FFFFFF",
        "button_border": "#D1D1D6",
        "button_highlight": "#FFFFFF",
        "button_hover": "#EAEAEF",
        "fluid_deep": "#D6E5F5",
        "fluid_surface": "#C1DCF8",
        "caustic_color": "#9EC4EB",
        "bubble_color": "#2980B9",
        "particle_color": "#0066CC",
        "ao_shadow": "#A0B8D0",
    },
    "retro": {
        "name": "Retro Synthwave",
        "is_dark": True,
        "mask_bg": "#010101",
        "pill_bg": "#140A24",
        "pill_shadow": "#0B0514",
        "border": "#5B168C",
        "border_highlight": "#9922EE",
        "header": "#00F0FF",
        "primary_text": "#FF007F",
        "secondary_text": "#00E5FF",
        "subtle_text": "#AA44FF",
        "divider": "#4C1474",
        "button_bg": "#220F3A",
        "button_border": "#7518B2",
        "button_highlight": "#B02EFF",
        "button_hover": "#36165E",
        "fluid_deep": "#1F0436",
        "fluid_surface": "#580A78",
        "caustic_color": "#00F0FF",
        "bubble_color": "#FF007F",
        "particle_color": "#00F0FF",
        "ao_shadow": "#0C0117",
    },
    "classical": {
        "name": "Classical Horology",
        "is_dark": False,
        "mask_bg": "#010101",
        "pill_bg": "#F5EFE6",
        "pill_shadow": "#D4C7B5",
        "border": "#C4A468",
        "border_highlight": "#FFF8E7",
        "header": "#2C1E14",
        "primary_text": "#2C1E14",
        "secondary_text": "#5C4632",
        "subtle_text": "#8F7354",
        "divider": "#D6C3A1",
        "button_bg": "#FFFFFF",
        "button_border": "#C4A468",
        "button_highlight": "#FFFDF7",
        "button_hover": "#EDE2D2",
        "fluid_deep": "#112E1C",
        "fluid_surface": "#1B4D2F",
        "caustic_color": "#E5C158",
        "bubble_color": "#348253",
        "particle_color": "#C4A468",
        "ao_shadow": "#091A10",
    },
    "win95": {
        "name": "Windows 95",
        "is_dark": False,
        "mask_bg": "#010101",
        "pill_bg": "#C0C0C0",
        "pill_shadow": "#808080",
        "border": "#404040",
        "border_highlight": "#FFFFFF",
        "header": "#000080",
        "primary_text": "#000000",
        "secondary_text": "#000080",
        "subtle_text": "#444444",
        "divider": "#808080",
        "button_bg": "#D4D0C8",
        "button_border": "#808080",
        "button_highlight": "#FFFFFF",
        "button_hover": "#E0DDD5",
        "fluid_deep": "#004040",
        "fluid_surface": "#008080",
        "caustic_color": "#00FFFF",
        "bubble_color": "#00FF80",
        "particle_color": "#000080",
        "ao_shadow": "#002020",
    },
    "terminal": {
        "name": "Terminal Matrix",
        "is_dark": True,
        "mask_bg": "#010101",
        "pill_bg": "#060A06",
        "pill_shadow": "#020402",
        "border": "#133313",
        "border_highlight": "#256625",
        "header": "#00FF66",
        "primary_text": "#00FF66",
        "secondary_text": "#00BB44",
        "subtle_text": "#007722",
        "divider": "#153B15",
        "button_bg": "#0D1E0D",
        "button_border": "#1F4D1F",
        "button_highlight": "#338833",
        "button_hover": "#173617",
        "fluid_deep": "#021A06",
        "fluid_surface": "#083B10",
        "caustic_color": "#00FF66",
        "bubble_color": "#33FF88",
        "particle_color": "#00FF66",
        "ao_shadow": "#010D03",
    },
    "nuclear": {
        "name": "Nuclear Hazard",
        "is_dark": True,
        "mask_bg": "#010101",
        "pill_bg": "#141208",
        "pill_shadow": "#080703",
        "border": "#554400",
        "border_highlight": "#997700",
        "header": "#FFB000",
        "primary_text": "#FFB000",
        "secondary_text": "#CCA000",
        "subtle_text": "#886600",
        "divider": "#443300",
        "button_bg": "#241D09",
        "button_border": "#664E04",
        "button_highlight": "#AA850E",
        "button_hover": "#362C0F",
        "fluid_deep": "#261902",
        "fluid_surface": "#4D3600",
        "caustic_color": "#FFD000",
        "bubble_color": "#FF9900",
        "particle_color": "#FFB000",
        "ao_shadow": "#140D01",
    },
    "lava": {
        "name": "Volcanic Magma",
        "is_dark": True,
        "mask_bg": "#010101",
        "pill_bg": "#140704",
        "pill_shadow": "#0A0302",
        "border": "#5C1605",
        "border_highlight": "#A32B0D",
        "header": "#FFAA00",
        "primary_text": "#FFFFFF",
        "secondary_text": "#FF7733",
        "subtle_text": "#993B14",
        "divider": "#4D1305",
        "button_bg": "#260E08",
        "button_border": "#6B1D0C",
        "button_highlight": "#AD3217",
        "button_hover": "#3D170D",
        "fluid_deep": "#3A0900",
        "fluid_surface": "#881500",
        "caustic_color": "#FFAA00",
        "bubble_color": "#FF4400",
        "particle_color": "#FFCC00",
        "ao_shadow": "#1A0300",
    },
}


class SplashParticle:
    def __init__(self, x: float, y: float, vx: float, vy: float, size: float, color: str) -> None:
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.size = size
        self.color = color
        self.life = 1.0

    def step(self, dt: float, gravity: float = 520.0) -> bool:
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += gravity * dt
        self.life -= dt * 2.4
        return self.life > 0.0


class FluidBubble:
    def __init__(self, x_left: float, x_right: float, height: float) -> None:
        self.x_left = x_left
        self.x_right = x_right
        self.height = height
        self.reset()

    def reset(self) -> None:
        self.x = random.uniform(self.x_left + 14.0, max(self.x_left + 24.0, self.x_right - 14.0))
        self.y = random.uniform(self.height * 0.55, self.height - 12.0)
        self.size = random.uniform(1.2, 2.6)
        self.vy = random.uniform(-16.0, -5.0)
        self.vx = random.uniform(-6.0, 6.0)
        self.phase = random.uniform(0.0, 6.28)

    def step(self, dt: float, surface_y: float) -> None:
        self.phase += dt * 3.0
        self.x += (self.vx + math.sin(self.phase) * 3.5) * dt
        self.y += self.vy * dt
        if self.y <= surface_y + 4.0 or self.x < self.x_left + 8.0 or self.x > self.x_right - 8.0:
            self.reset()


class FizzBubble:
    """High-frequency sparkling effervescent micro-bubble active during agent engagement."""
    def __init__(self, x_left: float, x_right: float, y_floor: float) -> None:
        self.x_left = x_left
        self.x_right = x_right
        self.y_floor = y_floor
        self.reset()

    def reset(self) -> None:
        self.x = random.uniform(self.x_left + 10.0, max(self.x_left + 20.0, self.x_right - 10.0))
        self.y = random.uniform(self.y_floor - 2.0, self.y_floor + 4.0)
        self.size = random.uniform(0.7, 1.8)
        self.vy = random.uniform(-45.0, -85.0)
        self.phase = random.uniform(0.0, 6.28)
        self.flutter_freq = random.uniform(18.0, 32.0)
        self.flutter_amp = random.uniform(1.2, 3.0)
        self.sparkle = random.uniform(0.0, 1.0)

    def step(self, dt: float, surface_y: float) -> bool:
        self.phase += dt * self.flutter_freq
        self.x += math.sin(self.phase) * self.flutter_amp * dt * 40.0
        self.y += self.vy * dt
        if self.y <= surface_y + 2.0:
            self.reset()
            return True  # Pop event at surface
        if self.x < self.x_left + 4.0 or self.x > self.x_right - 4.0:
            self.reset()
        return False


def evaluate_catmull_rom(nodes: List[Tuple[float, float]], steps_per_segment: int = 18) -> List[Tuple[float, float]]:
    """Evaluates smooth C1 Catmull-Rom cubic splines at 470+ points across wave nodes."""
    n = len(nodes)
    if n < 2:
        return list(nodes)
    curve: List[Tuple[float, float]] = []
    for i in range(n - 1):
        p0 = nodes[max(0, i - 1)]
        p1 = nodes[i]
        p2 = nodes[min(n - 1, i + 1)]
        p3 = nodes[min(n - 1, i + 2)]
        for s in range(steps_per_segment):
            t = s / float(steps_per_segment)
            t2 = t * t
            t3 = t2 * t
            x = 0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3)
            y = 0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
            curve.append((round(x, 2), round(y, 2)))
    curve.append((round(nodes[-1][0], 2), round(nodes[-1][1], 2)))
    return curve


def rounded_rect_polygon(x1: float, y1: float, x2: float, y2: float, r: float, steps: int = 24) -> List[float]:
    """Generates high-precision subpixel boundary vertices for antialiased stadium capsule."""
    r = max(1.0, min(r, (x2 - x1) / 2.0, (y2 - y1) / 2.0))
    pts: List[float] = []
    # Top-right arc (pi/2 down to 0)
    cx, cy = x2 - r, y1 + r
    for s in range(steps + 1):
        ang = (math.pi / 2.0) * (1.0 - s / float(steps))
        pts.extend([round(cx + r * math.cos(ang), 2), round(cy - r * math.sin(ang), 2)])
    # Bottom-right arc (0 down to -pi/2)
    cx, cy = x2 - r, y2 - r
    for s in range(steps + 1):
        ang = -(math.pi / 2.0) * (s / float(steps))
        pts.extend([round(cx + r * math.cos(ang), 2), round(cy - r * math.sin(ang), 2)])
    # Bottom-left arc (-pi/2 down to -pi)
    cx, cy = x1 + r, y2 - r
    for s in range(steps + 1):
        ang = -math.pi / 2.0 - (math.pi / 2.0) * (s / float(steps))
        pts.extend([round(cx + r * math.cos(ang), 2), round(cy - r * math.sin(ang), 2)])
    # Top-left arc (pi down to pi/2)
    cx, cy = x1 + r, y1 + r
    for s in range(steps + 1):
        ang = math.pi - (math.pi / 2.0) * (s / float(steps))
        pts.extend([round(cx + r * math.cos(ang), 2), round(cy - r * math.sin(ang), 2)])
    return pts


def build_liquid_mesh_polygon(
    surface_spline: List[Tuple[float, float]],
    x_left: float,
    x_right: float,
    y_floor: float,
    corner_r_left: float = 23.0,
    corner_r_right: float = 3.0,
    corner_steps: int = 32,
) -> List[float]:
    """
    Constructs a true physically-conforming liquid container polygon flush with the vessel:
    1. Perfectly flat horizontal floor: (x_left + r_left, y_floor) -> (x_right - r_right, y_floor)
    2. Subtle corner fillet hugging the bottom-right divider wall base
    3. Vertical right wall flush along the vertical divider (x_right) up to surface meniscus
    4. Smooth Catmull-Rom wave spline across top horizon (traversed right-to-left)
    5. Vertical left wall flush along outer capsule glass (x_left) down to corner fillet
    6. Circular fillet hugging the outer capsule's curved bottom-left glass corner (r_left)
    Result: 100% flat bottom base, flush to glass walls, ZERO weird upward rounding or hammock scooping.
    """
    if corner_r_left <= 0.0 and corner_r_right <= 0.0:
        pts: List[float] = [round(x_left, 2), round(y_floor, 2), round(x_right, 2), round(y_floor, 2)]
        if surface_spline:
            pts.extend([round(x_right, 2), round(surface_spline[-1][1], 2)])
            for sx, sy in reversed(surface_spline):
                pts.extend([round(sx, 2), round(sy, 2)])
            pts.extend([round(x_left, 2), round(surface_spline[0][1], 2)])
        return pts

    pts: List[float] = []
    rl = max(2.0, min(corner_r_left, (x_right - x_left) / 2.0, (y_floor - 20.0) / 2.0))
    rr = max(1.0, min(corner_r_right, 6.0))

    # 1. Flat horizontal floor from left corner fillet to right corner fillet
    pts.extend([round(x_left + rl, 2), round(y_floor, 2)])
    pts.extend([round(x_right - rr, 2), round(y_floor, 2)])

    # 2. Bottom-right corner fillet arc (from -pi/2 up to 0)
    cx_br, cy_br = x_right - rr, y_floor - rr
    for s in range(1, 4):
        ang = -math.pi / 2.0 + (math.pi / 2.0) * (s / 3.0)
        pts.extend([round(cx_br + rr * math.cos(ang), 2), round(cy_br - rr * math.sin(ang), 2)])

    # 3. Surface wave spline traversed from right to left
    for sx, sy in reversed(surface_spline):
        pts.extend([round(sx, 2), round(sy, 2)])

    # 4. Bottom-left circular fillet arc (from -pi down to -pi/2)
    cx_bl, cy_bl = x_left + rl, y_floor - rl
    for s in range(corner_steps + 1):
        ang = -math.pi + (math.pi / 2.0) * (s / float(corner_steps))
        pts.extend([round(cx_bl + rl * math.cos(ang), 2), round(cy_bl - rl * math.sin(ang), 2)])

    return pts


class DomedPillButton(tk.Canvas):
    def __init__(
        self,
        parent: Any,
        text: str,
        command: Any,
        width: int = 120,
        height: int = 34,
        bg_color: str = "#0066CC",
        fg_color: str = "#FFFFFF",
        hover_bg: str = "#0077EE",
        border_color: str = "#0055AA",
        font: Tuple[str, int, str] = ("Segoe UI", 9, "bold"),
        theme: str = "dark",
        container_bg: str = "#121214",
    ) -> None:
        super().__init__(parent, width=width, height=height, bg=container_bg, highlightthickness=0, bd=0)
        self.text = text
        self.command = command
        self.btn_w = width
        self.btn_h = height
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.hover_bg = hover_bg
        self.border_color = border_color
        self.font = font
        self.theme = theme
        self.is_hover = False
        self._render()
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)

    def _render(self) -> None:
        self.delete("all")
        fill = self.hover_bg if self.is_hover else self.bg_color
        r = self.btn_h / 2.0 - 2.0
        pts = rounded_rect_polygon(2, 2, self.btn_w - 2, self.btn_h - 2, r, steps=12)
        self.create_polygon(pts, smooth=False, fill=fill, outline=self.border_color, width=1)
        top_glow = "#FFFFFF" if (self.is_hover or self.theme == "light") else "#505058"
        self.create_line(2 + r * 0.7, 3, self.btn_w - 2 - r * 0.7, 3, fill=top_glow, width=1)
        bottom_shade = "#000000" if self.theme == "dark" else "#A0A0A8"
        self.create_line(2 + r * 0.7, self.btn_h - 3, self.btn_w - 2 - r * 0.7, self.btn_h - 3, fill=bottom_shade, width=1)
        self.create_text(self.btn_w // 2, self.btn_h // 2, text=self.text, fill=self.fg_color, font=self.font)

    def _on_enter(self, _event: tk.Event) -> None:
        self.is_hover = True
        self.config(cursor="hand2")
        self._render()

    def _on_leave(self, _event: tk.Event) -> None:
        self.is_hover = False
        self._render()

    def _on_click(self, _event: tk.Event) -> None:
        if self.command:
            self.command()


class AetherLiquidDesktopOverlay:
    def __init__(self) -> None:
        self.settings = self._load_settings()
        self.report = aether_pulse.scan_local_harnesses()
        self.mode = self.settings.get("overlay_mode", "auto")
        self.boundary_mode = self.settings.get("boundary_mode", "bounce")
        self.theme = self.settings.get("theme", "dark")
        self.detected_harness = "all"
        self.target_label = "Desktop Workspace"
        self.particles: List[SplashParticle] = []
        self._hover_control: Optional[str] = None
        self._settings_window: Optional[tk.Toplevel] = None
        self.tray_icon: Optional[Any] = None

        self.root = tk.Tk()
        self.root.title("Aether Pulse Liquid HUD")
        self.root.overrideredirect(True)
        self.lens = self.settings.get("accounting_lens", "specular")
        self.topmost = bool(self.settings.get("topmost", True))
        self.root.attributes("-topmost", self.topmost)

        # Fully rectangular window for 100% functionality - no transparentcolor bleeding or blue corner artifacts
        self.mask_color = "#0D0E12"
        self.root.configure(bg=self.mask_color)
        # Note: -transparentcolor is omitted so the window is solid without jagged 1-bit color keying

        # Load native Windows icon
        self.ico_path = os.path.abspath("aether_pulse.ico")
        if os.path.exists(self.ico_path):
            try:
                self.root.iconbitmap(self.ico_path)
            except Exception:
                pass

        self.screen_w = float(max(800, self.root.winfo_screenwidth()))
        self.screen_h = float(max(600, self.root.winfo_screenheight()))

        self.width = 448
        self.height = 112
        self.target_x = 140.0
        self.target_y = 140.0
        self.capsule_radius = 0

        self.phys = aether_pulse_ws.create_liquid_physics_state(
            x=self.target_x,
            y=self.target_y,
            num_nodes=48,
            boundary_mode=self.boundary_mode,
            width=float(self.width),
            height=float(self.height),
        )
        if self.boundary_mode != "pin":
            self.phys["vx"] = 28.0
            self.phys["vy"] = 16.0
        self.root.geometry(f"{self.width}x{self.height}+{int(self.target_x)}+{int(self.target_y)}")

        self._init_fonts()

        self.canvas = tk.Canvas(
            self.root,
            width=self.width,
            height=self.height,
            bg=self.mask_color,
            highlightthickness=0,
            bd=0,
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        body_w = self.width - 64
        self.bubbles = [FluidBubble(7.0, body_w - 1.0, self.height) for _ in range(14)]
        self.fizz_bubbles = [FizzBubble(7.0, body_w - 1.0, self.height - 7.0) for _ in range(36)]

        self._drag_offset_x = 0
        self._drag_offset_y = 0
        self._target_drag_x = self.target_x
        self._target_drag_y = self.target_y
        self._hover_harness: Optional[str] = None
        self._is_dragging = False
        self._drag_history: List[Tuple[float, float, float]] = []
        self._last_t = time.perf_counter()
        self._last_probe_t = 0.0

        self.canvas.bind("<ButtonPress-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)
        self.canvas.bind("<Motion>", self._on_mouse_move)
        self.canvas.bind("<Leave>", self._on_mouse_leave)

        # Apply native Windows 11 rounded window region as secondary hardware boundary
        self.root.update_idletasks()
        self._apply_rounded_window_region()

        # Initialize system tray
        self._init_system_tray()

        self._tick()

    def _load_settings(self) -> Dict[str, Any]:
        settings = dict(DEFAULT_SETTINGS)
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                    settings.update(json.load(f))
            except Exception:
                pass
        return settings

    def _save_settings(self) -> None:
        try:
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=2)
        except Exception:
            pass

    def _init_fonts(self) -> None:
        try:
            families = set(tkfont.families(self.root))
        except Exception:
            families = set()

        self.font_display = "Segoe UI Variable Display" if "Segoe UI Variable Display" in families else "Segoe UI"
        self.font_text = "Segoe UI Variable Text" if "Segoe UI Variable Text" in families else "Segoe UI"
        self.font_mono = "Cascadia Code" if "Cascadia Code" in families else ("Consolas" if "Consolas" in families else "Courier")

    def _apply_rounded_window_region(self) -> None:
        if sys.platform != "win32":
            return
        try:
            hwnd = self.root.winfo_id()
            try:
                # DWM Window Corner Preference (Windows 11): 2 = DWMWCP_ROUND
                ctypes.windll.dwmapi.DwmSetWindowAttribute(
                    hwnd, 33, ctypes.byref(ctypes.c_int(2)), ctypes.sizeof(ctypes.c_int)
                )
            except Exception:
                pass
            # Clear window region: 100% unclipped rectangle for maximum functionality and zero corner artifacts
            ctypes.windll.user32.SetWindowRgn(hwnd, None, True)
        except Exception:
            pass

    def _init_system_tray(self) -> None:
        if not HAS_TRAY:
            return
        try:
            icon_img = None
            png_path = "chrome-extension/icons/icon-48.png"
            if os.path.exists(png_path):
                icon_img = Image.open(png_path)
            elif os.path.exists(self.ico_path):
                icon_img = Image.open(self.ico_path)

            if not icon_img:
                icon_img = Image.new("RGBA", (32, 32), color=(0, 102, 204, 255))

            menu = pystray.Menu(
                pystray.MenuItem("Show / Restore HUD", lambda: self.root.after(0, self._restore_from_tray), default=True),
                pystray.MenuItem("Minimize to Tray", lambda: self.root.after(0, self._minimize_to_tray)),
                pystray.MenuItem("🌐 Open Web Dashboard", lambda: self.root.after(0, self._launch_web_dashboard)),
                pystray.MenuItem("⚙ Settings...", lambda: self.root.after(0, self.open_settings_dialog)),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Mode: Auto-Sense", lambda: self._tray_set_mode("auto"), checked=lambda item: self.mode == "auto"),
                pystray.MenuItem("Mode: All 10 Harnesses", lambda: self._tray_set_mode("all"), checked=lambda item: self.mode == "all"),
                pystray.MenuItem("Cycle Theme", lambda: self.root.after(0, self._cycle_theme)),
                pystray.MenuItem("Physics: Bounce Walls", lambda: self._tray_set_boundary("bounce"), checked=lambda item: self.boundary_mode == "bounce"),
                pystray.MenuItem("Physics: Pinned Anchor", lambda: self._tray_set_boundary("pin"), checked=lambda item: self.boundary_mode == "pin"),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Exit Aether Pulse", lambda: self.root.after(0, self._exit_application)),
            )

            self.tray_icon = pystray.Icon("AetherPulse", icon_img, "Aether Pulse Liquid HUD", menu)
            self.tray_icon.run_detached()
        except Exception:
            self.tray_icon = None

    def _tray_set_mode(self, mode: str) -> None:
        def _apply():
            self.mode = mode
            self.settings["overlay_mode"] = mode
            self._save_settings()
            self._update_height_for_mode()
        self.root.after(0, _apply)

    def _tray_set_boundary(self, bmode: str) -> None:
        def _apply():
            self.boundary_mode = bmode
            self.settings["boundary_mode"] = bmode
            self.phys["boundary_mode"] = bmode
            if bmode == "pin":
                self.phys["vx"] = 0.0
                self.phys["vy"] = 0.0
            self._save_settings()
        self.root.after(0, _apply)

    def _minimize_to_tray(self) -> None:
        self.root.withdraw()

    def _restore_from_tray(self) -> None:
        self.root.deiconify()
        self.root.attributes("-topmost", bool(self.settings.get("topmost", True)))
        self.root.update_idletasks()
        self._apply_rounded_window_region()

    def _launch_web_dashboard(self) -> None:
        local_url = "http://127.0.0.1:8765/"
        online_url = "https://mjeanhudson-dev.github.io/aether-pulse/"
        local_file = os.path.abspath("index.html")

        # Prioritize Standalone Native Edge App window for 1:1 desktop studio experience
        edge_candidates = [
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        ]
        edge_bin = next((p for p in edge_candidates if os.path.exists(p)), None)
        if edge_bin:
            try:
                import subprocess
                subprocess.Popen([
                    edge_bin,
                    f"--app={local_url}",
                    "--window-size=1440,900",
                    "--window-position=120,60",
                ])
                return
            except Exception:
                pass

        opened = False
        try:
            import urllib.request
            req = urllib.request.Request("http://127.0.0.1:8765/api/telemetry")
            with urllib.request.urlopen(req, timeout=0.35) as resp:
                if resp.status == 200:
                    webbrowser.open(local_url)
                    opened = True
        except Exception:
            pass

        if not opened:
            try:
                if os.path.exists(local_file):
                    webbrowser.open(f"file:///{local_file.replace(os.sep, '/')}")
                else:
                    webbrowser.open(online_url)
            except Exception:
                webbrowser.open(online_url)

    def _exit_application(self) -> None:
        if self.tray_icon:
            try:
                self.tray_icon.stop()
            except Exception:
                pass
        self.root.quit()
        self.root.destroy()
        sys.exit(0)

    def _toggle_always_on_top(self) -> None:
        cur = bool(self.settings.get("topmost", True))
        self.topmost = not cur
        self.settings["topmost"] = self.topmost
        self.root.attributes("-topmost", self.topmost)
        self._save_settings()
        self._render()

    def _cycle_accounting_lens(self) -> None:
        lenses = ["specular", "secular", "spectacular"]
        cur = self.settings.get("accounting_lens", "specular")
        idx = (lenses.index(cur) + 1) % len(lenses) if cur in lenses else 0
        self.lens = lenses[idx]
        self.settings["accounting_lens"] = self.lens
        self._save_settings()
        mid = len(self.phys["wave_velocities"]) // 2
        self.phys["wave_velocities"][mid] += 32.0
        self._render()

    def _cycle_theme(self) -> None:
        cur_idx = THEME_ORDER.index(self.theme) if self.theme in THEME_ORDER else 0
        next_idx = (cur_idx + 1) % len(THEME_ORDER)
        self.theme = THEME_ORDER[next_idx]
        self.settings["theme"] = self.theme
        self._save_settings()
        self._render()

    def get_active_palette(self) -> Dict[str, Any]:
        p = dict(THEME_PALETTES.get(self.theme, THEME_PALETTES["dark"]))
        if self.settings.get("custom_accent") and self.theme == "custom":
            p["button_highlight"] = self.settings["custom_accent"]
            p["caustic_color"] = self.settings["custom_accent"]
        if self.settings.get("custom_liquid") and self.theme == "custom":
            p["fluid_surface"] = self.settings["custom_liquid"]
        return p

    def _draw_domed_pill(self, x1: float, y1: float, x2: float, y2: float, r: float, fill: str, border: str, is_hover: bool = False) -> None:
        pts = rounded_rect_polygon(x1, y1, x2, y2, r, steps=16)
        self.canvas.create_polygon(pts, smooth=False, fill=fill, outline=border, width=1)
        top_glow = "#FFFFFF" if not self.get_active_palette().get("is_dark", True) else "#38383E"
        self.canvas.create_line(x1 + r * 0.7, y1 + 1, x2 - r * 0.7, y1 + 1, fill=top_glow, width=1)

    def _draw_domed_button(self, x1: float, y1: float, x2: float, y2: float, r: float, fill: str, border: str, is_hover: bool = False) -> None:
        pts = rounded_rect_polygon(x1, y1, x2, y2, r, steps=10)
        self.canvas.create_polygon(pts, smooth=False, fill=fill, outline=border, width=1)
        # 3D Specular highlight rim on top
        is_dark = self.get_active_palette().get("is_dark", True)
        top_glow = "#FFFFFF" if (not is_dark or is_hover) else "#484850"
        self.canvas.create_line(x1 + r * 0.7, y1 + 1, x2 - r * 0.7, y1 + 1, fill=top_glow, width=1)
        # Bottom shadow rim for authentic tactile domed depth
        bottom_shade = "#050507" if is_dark else "#C4C4C8"
        self.canvas.create_line(x1 + r * 0.7, y2 - 1, x2 - r * 0.7, y2 - 1, fill=bottom_shade, width=1)

    def _on_mouse_move(self, event: tk.Event) -> None:
        old_hover = self._hover_control
        self._hover_control = None

        # Check Apple Traffic Light Controls on TOP-LEFT (x: 12..64, y: 11..27)
        if 11 <= event.y <= 27:
            if 12 <= event.x <= 28:
                self._hover_control = "close"
            elif 28 < event.x <= 44:
                self._hover_control = "minimize"
            elif 44 < event.x <= 60:
                self._hover_control = "settings"
            elif event.x <= 64:
                self._hover_control = "traffic_lights"

        # Check Right-Side 5-Button Column (x: body_w + 6 .. width - 10)
        body_w = self.width - 64
        if event.x >= body_w + 6 and event.x <= self.width - 10:
            h5 = (self.height - 28) / 5.0
            if 8 <= event.y <= 8 + h5:
                self._hover_control = "side_mode"
            elif 8 + h5 + 3 <= event.y <= 8 + 2 * h5 + 3:
                self._hover_control = "side_theme"
            elif 8 + 2 * h5 + 6 <= event.y <= 8 + 3 * h5 + 6:
                self._hover_control = "side_physics"
            elif 8 + 3 * h5 + 9 <= event.y <= 8 + 4 * h5 + 9:
                self._hover_control = "side_topmost"
            elif 8 + 4 * h5 + 12 <= event.y <= self.height - 8:
                self._hover_control = "side_web"

        # Check Harness Drawer Rows & 4 KPI Cards when mode == "all"
        old_harness = self._hover_harness
        self._hover_harness = None
        if self.mode == "all" and 112 <= event.y <= 200 and event.x < body_w:
            self._hover_control = "card_kpi"
        elif self.mode == "all" and 218 <= event.y <= 296 and event.x < body_w:
            top_harness_keys = [
                "claude_code", "antigravity", "openai_codex", "cursor", "aider",
                "windsurf", "continue_dev", "github_copilot", "openhands", "t3_code"
            ]
            col1 = top_harness_keys[:5]
            col2 = top_harness_keys[5:]
            row_i = min(4, max(0, int((event.y - 220) // 15)))
            if event.x < (body_w // 2):
                self._hover_harness = col1[row_i]
            else:
                self._hover_harness = col2[row_i]
        elif event.y < 40 and 70 <= event.x <= 260:
            if self.detected_harness and self.detected_harness != "all":
                self._hover_harness = self.detected_harness

        if old_hover != self._hover_control or old_harness != self._hover_harness:
            self._render()

    def _on_mouse_leave(self, _event: tk.Event) -> None:
        changed = False
        if self._hover_control is not None:
            self._hover_control = None
            changed = True
        if self._hover_harness is not None:
            self._hover_harness = None
            changed = True
        if changed:
            self._render()

    def _on_press(self, event: tk.Event) -> None:
        # Check Apple Traffic Lights (Top-Left)
        if 11 <= event.y <= 27:
            if 12 <= event.x <= 28:
                # Red traffic light: Close / Minimize to tray
                if self.settings.get("close_to_tray", True) and HAS_TRAY:
                    self._minimize_to_tray()
                else:
                    self._exit_application()
                return
            elif 28 < event.x <= 44:
                # Amber traffic light: Minimize
                self._minimize_to_tray()
                return
            elif 44 < event.x <= 60:
                # Green traffic light: Settings
                self.open_settings_dialog()
                return

        # Check Right-Side 5-Button Column
        body_w = self.width - 64
        if event.x >= body_w + 6 and event.x <= self.width - 10:
            h5 = (self.height - 28) / 5.0
            if 8 <= event.y <= 8 + h5:
                # Button 1: Mode Switcher
                self.mode = aether_pulse_ws.next_overlay_mode(self.mode)
                self.settings["overlay_mode"] = self.mode
                self._save_settings()
                mid = len(self.phys["wave_velocities"]) // 2
                self.phys["wave_velocities"][mid] += 48.0
                self._update_height_for_mode()
                return
            elif 8 + h5 + 3 <= event.y <= 8 + 2 * h5 + 3:
                # Button 2: Cycle Theme
                self._cycle_theme()
                mid = len(self.phys["wave_velocities"]) // 2
                self.phys["wave_velocities"][mid] -= 32.0
                return
            elif 8 + 2 * h5 + 6 <= event.y <= 8 + 3 * h5 + 6:
                # Button 3: Cycle Boundary Mode
                self.boundary_mode = aether_pulse_ws.next_boundary_mode(self.boundary_mode)
                self.settings["boundary_mode"] = self.boundary_mode
                self.phys["boundary_mode"] = self.boundary_mode
                self._save_settings()
                mid = len(self.phys["wave_velocities"]) // 2
                self.phys["wave_velocities"][mid] += 36.0
                if self.boundary_mode in ("bounce", "pacman") and math.hypot(self.phys["vx"], self.phys["vy"]) < 18.0:
                    self.phys["vx"] = 42.0
                    self.phys["vy"] = -26.0
                elif self.boundary_mode == "pin":
                    self.phys["vx"] = 0.0
                    self.phys["vy"] = 0.0
                return
            elif 8 + 3 * h5 + 9 <= event.y <= 8 + 4 * h5 + 9:
                # Button 4: Dedicated Quick Always-on-Top Toggle
                self._toggle_always_on_top()
                mid = len(self.phys["wave_velocities"]) // 2
                self.phys["wave_velocities"][mid] += 28.0
                return
            elif 8 + 4 * h5 + 12 <= event.y <= self.height - 8:
                # Button 5: Launch Web Dashboard
                self._launch_web_dashboard()
                return

        # Check clicking on metric text or 4 KPI cards to cycle accounting lens
        if 16 <= event.x < body_w and (42 <= event.y <= 92 or (self.mode == "all" and 112 <= event.y <= 200)):
            self._cycle_accounting_lens()
            return

        # Start Dragging with physical weightiness
        self._is_dragging = True
        self._drag_offset_x = event.x
        self._drag_offset_y = event.y
        self._target_drag_x = float(self.phys["x"])
        self._target_drag_y = float(self.phys["y"])
        now = time.perf_counter()
        px = float(self.root.winfo_pointerx())
        py = float(self.root.winfo_pointery())
        self._drag_history = [(now, px, py)]
        self.phys["vx"] = 0.0
        self.phys["vy"] = 0.0

    def _on_drag(self, _event: tk.Event) -> None:
        if not self._is_dragging:
            return
        now = time.perf_counter()
        px = float(self.root.winfo_pointerx())
        py = float(self.root.winfo_pointery())
        self._target_drag_x = px - self._drag_offset_x
        self._target_drag_y = py - self._drag_offset_y
        self._drag_history.append((now, px, py))
        self._drag_history = [s for s in self._drag_history if (now - s[0]) <= 0.160]

    def _on_release(self, _event: tk.Event) -> None:
        if not self._is_dragging:
            return
        self._is_dragging = False
        now = time.perf_counter()

        self._drag_history = [s for s in self._drag_history if (now - s[0]) <= 0.140]
        throw_vx = 0.0
        throw_vy = 0.0

        if len(self._drag_history) >= 2:
            dt = self._drag_history[-1][0] - self._drag_history[0][0]
            time_since_move = now - self._drag_history[-1][0]
            if time_since_move < 0.060 and dt > 0.008:
                dx = self._drag_history[-1][1] - self._drag_history[0][1]
                dy = self._drag_history[-1][2] - self._drag_history[0][2]
                throw_vx = dx / dt
                throw_vy = dy / dt

        if self.boundary_mode == "pin":
            self.phys["vx"] = 0.0
            self.phys["vy"] = 0.0
        else:
            # Sensation of weight: heavy momentum retention
            max_fling = 1200.0
            self.phys["vx"] = max(-max_fling, min(max_fling, throw_vx * 0.94))
            self.phys["vy"] = max(-max_fling, min(max_fling, throw_vy * 0.94))

            fling_spd = math.hypot(throw_vx, throw_vy)
            n_waves = len(self.phys["wave_velocities"])

            # Wave formation directly proportional to fling speed
            wave_surge = min(180.0, fling_spd * 0.28)
            for i in range(n_waves):
                norm = (i / float(max(1, n_waves - 1))) * 2.0 - 1.0
                impulse = -throw_vx * 0.24 * norm + abs(throw_vy) * 0.14 * math.cos(norm * math.pi * 0.5)
                self.phys["wave_velocities"][i] += impulse

            # If let go at high speed (> 240 px/s), launch immediate dynamic splash spray
            if fling_spd > 240.0 and self.settings.get("enable_particles", True):
                accent = aether_pulse_ws.build_ws_telemetry_frame(self.report, self.mode, self.detected_harness)["active"]["accent_hex"]
                side = "left" if throw_vx > 0 else "right"
                self._spawn_splash_particles(side, wave_surge, accent)

        self.target_x = float(self.phys["x"])
        self.target_y = float(self.phys["y"])
        self.target_y = float(self.phys["y"])

    def _probe_underneath(self, now: float, force: bool = False) -> None:
        if not force and (now - self._last_probe_t) < 0.14:
            return
        self._last_probe_t = now
        probe_x = int(self.phys["x"] + self.width // 2)
        probe_y = int(self.phys["y"] + self.height + 12)
        probed = aether_pulse_ws.probe_window_at_point(probe_x, probe_y, ignore_hwnd=self.root.winfo_id())
        self.detected_harness = probed["detected_harness"]
        if probed["window_title"]:
            self.target_label = probed["window_title"][:34]
        elif probed.get("process_name"):
            self.target_label = probed["process_name"][:34]

    def _update_height_for_mode(self) -> None:
        self.height = 328 if self.mode == "all" else 118
        self.phys["height"] = float(self.height)
        self.canvas.config(height=self.height)
        self.root.update_idletasks()
        self._apply_rounded_window_region()

    def _spawn_splash_particles(self, side: str, impulse: float, accent_hex: str) -> None:
        if not self.settings.get("enable_particles", True):
            return
        count = min(22, max(6, int(impulse * 0.16)))
        body_w = self.width - 64
        palette = self.get_active_palette()

        for _ in range(count):
            if side == "left":
                px = random.uniform(12.0, 26.0)
                py = random.uniform(self.height * 0.40, self.height * 0.85)
                vx = random.uniform(35.0, 160.0)
                vy = random.uniform(-240.0, -60.0)
            elif side == "right":
                px = random.uniform(body_w - 26.0, body_w - 12.0)
                py = random.uniform(self.height * 0.40, self.height * 0.85)
                vx = random.uniform(-160.0, -35.0)
                vy = random.uniform(-240.0, -60.0)
            else:
                px = random.uniform(18.0, body_w - 18.0)
                py = random.uniform(self.height * 0.60, self.height - 14.0)
                vx = random.uniform(-80.0, 80.0)
                vy = random.uniform(-190.0, -40.0)

            size = random.uniform(1.8, 3.4)
            color = accent_hex if random.random() > 0.4 else palette["particle_color"]
            self.particles.append(SplashParticle(px, py, vx, vy, size, color))

    def _tick(self) -> None:
        now = time.perf_counter()
        dt = now - self._last_t
        self._last_t = now

        aether_pulse_ws.step_liquid_physics(
            self.phys,
            self.target_x,
            self.target_y,
            dt=dt,
            is_dragging=self._is_dragging,
            bounds_w=self.screen_w,
            bounds_h=self.screen_h,
        )

        # Trigger splash particles on wall bounce if enabled
        splash_event = self.phys.get("splash_event")
        if splash_event and self.settings.get("enable_particles", True):
            side = splash_event.get("side", "left")
            impulse = float(splash_event.get("impulse", 50.0))
            frame_preview = aether_pulse_ws.build_ws_telemetry_frame(
                self.report, self.mode, self.detected_harness, self.target_label, self.boundary_mode
            )
            accent = frame_preview["active"]["accent_hex"]
            self._spawn_splash_particles(side, impulse, accent)

        # Step dynamic splash particles
        alive_particles: List[SplashParticle] = []
        for p in self.particles:
            if p.step(dt):
                alive_particles.append(p)
        self.particles = alive_particles

        # Step volumetric aeration micro-bubbles
        body_w = self.width - 64
        liquid_h = 98.0 if self.mode == "all" else float(self.height)
        base_y = liquid_h - (liquid_h * 0.44 * float(self.phys.get("squish_y", 1.0) * 0.94))
        for b in self.bubbles:
            b.step(dt, base_y)

        # Step effervescent agent fizzing bubbles when active
        is_active_agent = self.detected_harness != "all" or self.settings.get("enable_fizz", True)
        if is_active_agent:
            palette = self.get_active_palette()
            for fb in self.fizz_bubbles:
                popped = fb.step(dt, base_y)
                if popped and random.random() < 0.15 and len(self.particles) < 30:
                    self.particles.append(
                        SplashParticle(fb.x, base_y, random.uniform(-25, 25), random.uniform(-90, -30), random.uniform(1.0, 1.8), palette["bubble_color"])
                    )

        if self._is_dragging:
            curr_x = float(self.phys["x"])
            curr_y = float(self.phys["y"])
            target_x = float(self._target_drag_x)
            target_y = float(self._target_drag_y)

            dx = target_x - curr_x
            dy = target_y - curr_y

            # Heavy magnetic fluid drag-behind lag (alpha = 0.28 per tick)
            # Produces an appealing physical drag behind where the window smoothly trails the cursor
            new_x = curr_x + dx * 0.28
            new_y = curr_y + dy * 0.28

            drag_vx = (new_x - curr_x) / max(0.001, dt)
            drag_vy = (new_y - curr_y) / max(0.001, dt)

            # Fluid wave response to hand drag motion
            n_waves = len(self.phys["wave_velocities"])
            for i in range(n_waves):
                norm = (i / float(max(1, n_waves - 1))) * 2.0 - 1.0
                self.phys["wave_velocities"][i] += -drag_vx * 0.052 * norm + abs(drag_vy) * 0.024 * math.cos(norm * math.pi * 0.5)

            self.phys["x"] = new_x
            self.phys["y"] = new_y
            self.target_x = new_x
            self.target_y = new_y
            cx = int(round(new_x))
            cy = int(round(new_y))
            self.root.geometry(f"{self.width}x{self.height}+{cx}+{cy}")
            self._probe_underneath(now, force=False)
        else:
            self.target_x = float(self.phys["x"])
            self.target_y = float(self.phys["y"])
            self._probe_underneath(now, force=False)
            cx = int(round(self.phys["x"]))
            cy = int(round(self.phys["y"]))
            self.root.geometry(f"{self.width}x{self.height}+{cx}+{cy}")

        self._render()
        self.root.after(16, self._tick)

    def _render(self) -> None:
        frame = aether_pulse_ws.build_ws_telemetry_frame(
            self.report,
            self.mode,
            self.detected_harness,
            self.target_label,
            self.boundary_mode,
        )
        active = frame["active"]
        fill_ratio = float(active["liquid_fill_ratio"])
        palette = self.get_active_palette()

        # Adaptable Sentinel Evaluation:
        # Evaluate which harness governs current liquid physics & sentinel
        if self._hover_harness and self._hover_harness in frame["harnesses"]:
            target_h_data = frame["harnesses"][self._hover_harness]
            target_h_usage = target_h_data.get("usage", {})
            h_label = target_h_data.get("short_name", self._hover_harness)
        elif self.mode != "all" and self.mode in frame["harnesses"]:
            target_h_data = frame["harnesses"][self.mode]
            target_h_usage = target_h_data.get("usage", {})
            h_label = target_h_data.get("short_name", self.mode)
        elif self.detected_harness and self.detected_harness in frame["harnesses"] and self.detected_harness != "all":
            target_h_data = frame["harnesses"][self.detected_harness]
            target_h_usage = target_h_data.get("usage", {})
            h_label = target_h_data.get("short_name", self.detected_harness)
        else:
            target_h_data = active
            target_h_usage = frame.get("usage_sentinel", {})
            h_label = active.get("short_name", "Trinity Mesh")

        # Check Lava Mode: strictly isolated to the evaluated harness
        is_lava_mode = (
            self.theme == "lava"
            or self.settings.get("simulate_lava_5hr", False)
            or target_h_usage.get("is_approaching_5hr", False)
        )
        is_quota_flashing = (
            target_h_usage.get("is_approaching_monthly", False)
            or (self.settings.get("simulate_lava_5hr", False) and self.settings.get("quota_flash", True))
        )

        now = time.perf_counter()
        # Subdued breathing cycle (f = 0.32 Hz, period = 3.1s) instead of jarring high-frequency strobe
        pulse_alpha = 0.45 + 0.55 * (0.5 + 0.5 * math.sin(now * 2.0)) if is_quota_flashing else 1.0

        if is_lava_mode:
            # Subdued warm volcanic magma with rich copper-ember undertones
            active_deep = "#2A0903" if pulse_alpha > 0.5 else "#200602"
            active_surf = "#9E340B" if pulse_alpha > 0.5 else "#852B08"
            active_caust = "#D97B1A"
            active_accent = "#D65A20" if not is_quota_flashing else ("#C94A18" if pulse_alpha > 0.5 else "#DE8222")
            active_bubble = "#CC6618"
        else:
            active_deep = palette["fluid_deep"]
            active_surf = palette["fluid_surface"]
            active_caust = palette["caustic_color"]
            active_accent = active["accent_hex"] if not is_quota_flashing else ("#FF0033" if pulse_alpha > 0.5 else "#FFCC00")
            active_bubble = palette["bubble_color"]

        self.canvas.delete("all")

        # 1. Solid rectangular body filling 100% of the window - zero corner clipping, zero blue masking leaks
        self.canvas.create_rectangle(
            0, 0, self.width, self.height,
            fill=palette["pill_bg"],
            outline=palette["border"],
            width=1,
        )
        # Specular top highlight hairline
        self.canvas.create_line(1, 1, self.width - 1, 1, fill=palette["border_highlight"], width=1)

        body_w = self.width - 64
        is_expanded = frame.get("show_all_drawer", False)
        liquid_h = 98.0 if is_expanded else float(self.height)
        base_y = liquid_h - (liquid_h * 0.44 * fill_ratio)
        waves = self.phys["wave_heights"]
        n = len(waves)
        tilt = float(self.phys["tilt_deg"])

        x_left = 1.0
        x_right = float(body_w)
        y_floor = 98.0 if is_expanded else float(self.height - 1.0)

        # 2. Build Smooth Catmull-Rom Splines (470+ points, zero line breaks)
        deep_nodes: List[Tuple[float, float]] = []
        surface_nodes: List[Tuple[float, float]] = []
        caustic_nodes: List[Tuple[float, float]] = []

        for i, h in enumerate(waves):
            px = x_left + (i / max(1, n - 1)) * (x_right - x_left)
            py_surf = max(14.0, min(y_floor - 4.0, base_y + h + (tilt * ((i - n / 2) * 0.35))))
            surface_nodes.append((px, py_surf))
            deep_h = h * 0.68 + math.sin(float(self.phys["phase"]) * 2.6 + i * 0.28) * 1.8
            py_deep = max(12.0, min(y_floor - 4.0, base_y - 3.5 + deep_h + (tilt * ((i - n / 2) * 0.30))))
            deep_nodes.append((px, py_deep))
            caust_h = h * 0.45 + math.sin(float(self.phys["phase"]) * 3.4 - i * 0.35) * 2.2
            py_caust = max(16.0, min(y_floor - 6.0, base_y + 12.0 + caust_h))
            caustic_nodes.append((px, py_caust))

        surf_spline = evaluate_catmull_rom(surface_nodes, steps_per_segment=18)
        deep_spline = evaluate_catmull_rom(deep_nodes, steps_per_segment=14)
        caust_spline = evaluate_catmull_rom(caustic_nodes, steps_per_segment=12)

        # 3. Layer 1: Deep Volumetric Undercurrent (Flat Crisp Bottom, Zero Curve)
        deep_pts = build_liquid_mesh_polygon(deep_spline, x_left, x_right, y_floor, corner_r_left=0.0, corner_r_right=0.0)
        self.canvas.create_polygon(deep_pts, smooth=False, fill=active_deep, outline="")

        # 4. Layer 2: Primary Radiant Liquid Mass (Flat Crisp Bottom, Zero Curve)
        surf_pts = build_liquid_mesh_polygon(surf_spline, x_left, x_right, y_floor, corner_r_left=0.0, corner_r_right=0.0)
        self.canvas.create_polygon(surf_pts, smooth=False, fill=active_surf, outline="")

        # 5. Layer 3: Subsurface Caustic Refraction Light Rays or Volcanic Magma Veins
        caust_line_pts: List[float] = []
        for sx, sy in caust_spline:
            caust_line_pts.extend([sx, sy])
        if len(caust_line_pts) >= 4:
            self.canvas.create_line(caust_line_pts, fill=active_caust, width=1.0, smooth=False)

        # Whole Liquid Mesh: Thermal Magma Convection Veins and Embers when Lava Active
        if is_lava_mode:
            v1_pts = []
            v2_pts = []
            v3_pts = []
            ph = float(self.phys["phase"])
            for sx, sy in surf_spline:
                y_v1 = min(y_floor - 2.0, sy + 7.5 + 3.8 * math.sin(sx * 0.042 + ph * 4.2))
                v1_pts.extend([sx, y_v1])
                y_v2 = min(y_floor - 2.0, sy + 15.0 + 3.0 * math.cos(sx * 0.072 - ph * 3.1))
                v2_pts.extend([sx, y_v2])
                y_v3 = min(y_floor - 2.0, (sy + y_floor) * 0.5 + 2.2 * math.sin(sx * 0.032 + ph * 2.0))
                v3_pts.extend([sx, y_v3])

            if len(v1_pts) >= 4:
                self.canvas.create_line(v1_pts, fill="#FFAA00", width=1.8, smooth=False)
            if len(v2_pts) >= 4:
                self.canvas.create_line(v2_pts, fill="#FFDD33", width=1.2, smooth=False)
            if len(v3_pts) >= 4:
                self.canvas.create_line(v3_pts, fill="#FF2200", width=2.4, smooth=False)

            if self.settings.get("enable_bubbles", True):
                for i in range(16):
                    ember_x = x_left + ((i * 37 + int(now * 38)) % int(max(10, body_w - x_left)))
                    ember_y = base_y + 4.0 + ((i * 19 + int(now * 26)) % int(max(6, y_floor - base_y - 2.0)))
                    e_r = 1.0 + (i % 3) * 0.6
                    e_col = "#FFF59D" if (i % 3 == 0) else ("#FFD54F" if i % 2 == 0 else "#FF5722")
                    self.canvas.create_oval(ember_x - e_r, ember_y - e_r, ember_x + e_r, ember_y + e_r, fill=e_col, outline="")

        # 6. Layer 4: Floating Bubbles & Effervescent Agent Fizz
        if self.settings.get("enable_bubbles", True):
            for b in self.bubbles:
                r = b.size
                self.canvas.create_oval(b.x - r, b.y - r, b.x + r, b.y + r, fill=active_bubble, outline="")
                self.canvas.create_oval(b.x - r * 0.5, b.y - r * 0.5, b.x - r * 0.1, b.y - r * 0.1, fill="#FFFFFF", outline="")

        # Agent Fizzing micro-bubbles
        is_active_agent = self.detected_harness != "all" or self.settings.get("enable_fizz", True)
        if is_active_agent:
            for fb in self.fizz_bubbles:
                r = fb.size
                self.canvas.create_oval(fb.x - r, fb.y - r, fb.x + r, fb.y + r, fill=active_bubble, outline="")
                if fb.sparkle > 0.4:
                    self.canvas.create_oval(fb.x - r * 0.4, fb.y - r * 0.4, fb.x, fb.y, fill="#FFFFFF", outline="")

        # 7. Layer 5: Ambient Occlusion Shadow Underneath Crest Ribbon
        ao_pts: List[float] = []
        for sx, sy in surf_spline:
            ao_pts.extend([sx, sy + 1.6])
        if len(ao_pts) >= 4:
            self.canvas.create_line(ao_pts, fill=palette["ao_shadow"], width=3.2, smooth=False, capstyle=tk.ROUND, joinstyle=tk.ROUND)

        # 8. Layer 6: Continuous Silky Crest Ribbon & Specular Peak Hairline
        crest_line_pts: List[float] = []
        for sx, sy in surf_spline:
            crest_line_pts.extend([sx, sy])
        if len(crest_line_pts) >= 4:
            self.canvas.create_line(crest_line_pts, fill=active_accent, width=2.4, smooth=False, capstyle=tk.ROUND, joinstyle=tk.ROUND)

            # Continuous specular hairline on positive wave peaks
            specular_pts: List[float] = []
            for sx, sy in surf_spline:
                if sy < base_y:
                    specular_pts.extend([sx, sy - 0.7])
                elif specular_pts and len(specular_pts) >= 4:
                    self.canvas.create_line(specular_pts, fill="#FFFFFF", width=1.0, smooth=False, capstyle=tk.ROUND, joinstyle=tk.ROUND)
                    specular_pts = []
            if len(specular_pts) >= 4:
                self.canvas.create_line(specular_pts, fill="#FFFFFF", width=1.0, smooth=False, capstyle=tk.ROUND, joinstyle=tk.ROUND)

        # 9. Layer 7: Dynamic Splash Droplets
        for p in self.particles:
            r = max(1.0, p.size * p.life)
            self.canvas.create_oval(p.x - r, p.y - r, p.x + r, p.y + r, fill=p.color, outline="")

        # 10. Header: Apple macOS Circular Traffic Lights on TOP-LEFT
        tl_y = 18
        # Red: Close Window
        c_fill = "#FF5F56" if self._hover_control != "close" else "#FF3B30"
        self.canvas.create_oval(14, tl_y - 6, 26, tl_y + 6, fill=c_fill, outline="#E0443E", width=1)
        self.canvas.create_arc(15, tl_y - 5, 25, tl_y + 5, start=45, extent=90, style=tk.ARC, outline="#FFA6A0", width=1)
        if self._hover_control in ("close", "traffic_lights"):
            self.canvas.create_text(20, tl_y, text="✕", fill="#4D0000", font=(self.font_display, 7, "bold"))

        # Amber: Minimize Window
        m_fill = "#FEBC2E" if self._hover_control != "minimize" else "#FF9500"
        self.canvas.create_oval(30, tl_y - 6, 42, tl_y + 6, fill=m_fill, outline="#D89E24", width=1)
        self.canvas.create_arc(31, tl_y - 5, 41, tl_y + 5, start=45, extent=90, style=tk.ARC, outline="#FFEAA0", width=1)
        if self._hover_control in ("minimize", "traffic_lights"):
            self.canvas.create_text(36, tl_y - 1, text="—", fill="#593E00", font=(self.font_display, 8, "bold"))

        # Green: Settings Dialog
        s_fill = "#28C840" if self._hover_control != "settings" else "#30D158"
        self.canvas.create_oval(46, tl_y - 6, 58, tl_y + 6, fill=s_fill, outline="#1FA333", width=1)
        self.canvas.create_arc(47, tl_y - 5, 57, tl_y + 5, start=45, extent=90, style=tk.ARC, outline="#B0F0B8", width=1)
        if self._hover_control in ("settings", "traffic_lights"):
            self.canvas.create_text(52, tl_y, text="⚙", fill="#0D4715", font=(self.font_display, 7, "bold"))

        # Title & Active Badge (Begins at x=72, clean Apple layout)
        self.canvas.create_oval(70, tl_y - 4, 78, tl_y + 4, fill=active_accent, outline="")
        active_subs = self.settings.get("active_subscriptions", ["claude_code", "antigravity", "openai_codex"])
        custom_name = self.settings.get("custom_tier_name", "")
        sub_tier = get_subscription_tier(max(1, len(active_subs)), custom_name)
        tier_title = sub_tier["name"].upper()

        if self.mode == "all" or active.get("id") == "all":
            badge_text = f"✓ ARCHITECT · {tier_title} · {h_label}"
        else:
            badge_text = f"{active['name'].upper()} · {h_label}"

        if is_lava_mode:
            badge_text = f"🔥 SENTINEL · {tier_title}"
            badge_fill = "#FFAA00"
        elif is_quota_flashing:
            badge_text = f"⚠️ CRITICAL STROBE · 92%"
            badge_fill = "#DE8222"
        else:
            badge_fill = palette["header"]

        self.canvas.create_text(
            84,
            tl_y,
            anchor="w",
            text=badge_text[:42],
            fill=badge_fill,
            font=(self.font_display, 8, "bold"),
        )

        # 11. Primary Metric: Tabular Figures with 3-Lens Accounting
        lens = self.settings.get("accounting_lens", "specular")
        if lens == "secular":
            sec_cost = active.get("secular_cost_usd", 20.00)
            metric_str = f"{active['tokens_formatted']} TOK    ${sec_cost:,.2f}/MO FLAT    {active['cache_hit_pct']}% HIT"
            sub_str = f"SECULAR CASH · OVER: {frame['target_label'][:16]} · ZERO EXTRA API"
        elif lens == "spectacular":
            spec_val = active.get("spectacular_usd", active.get("saved_usd", 5110))
            metric_str = f"{active['tokens_formatted']} TOK    ${spec_val:,.0f} WORTH    {active['cache_hit_pct']}% HIT"
            sub_str = f"SPECTACULAR LENS · 45.8M NET CODE YIELD · 2.11B STREAM"
        else: # specular developer API standard
            cost_val = active.get("cost_usd", 244.42)
            metric_str = f"{active['tokens_formatted']} TOK    ${cost_val:,.2f} API    {active['cache_hit_pct']}% HIT"
            sub_str = f"SPECULAR (API) · OVER: {frame['target_label'][:16]} · SAVED ${active['saved_usd']:,}"

        if is_lava_mode:
            sub_str = f"MOLTEN LAVA MODE · SAVED ${active['saved_usd']:,} · 5HR SENTINEL"

        self.canvas.create_text(
            18,
            51,
            anchor="w",
            text=metric_str,
            fill=palette["primary_text"],
            font=(self.font_mono, 10, "bold"),
        )

        self.canvas.create_text(
            18,
            81,
            anchor="w",
            text=sub_str,
            fill=palette["secondary_text"],
            font=(self.font_mono, 7, "bold"),
        )

        # 13. If "All 10 Harnesses" drawer is open, render 4 KPI Cards + 10-Harness Comparative Grid
        if frame["show_all_drawer"]:
            self.canvas.create_line(18, 98, body_w - 18, 98, fill=palette["divider"], width=1)

            # Header over KPI Ledger strip
            self.canvas.create_text(
                18,
                107,
                anchor="w",
                text="TELEMETRY LEDGER · 4-PILLAR SUITE",
                fill=palette["secondary_text"],
                font=(self.font_mono, 7, "bold"),
            )
            self.canvas.create_text(
                body_w - 18,
                107,
                anchor="e",
                text=f"LENS: {lens.upper()}",
                fill=active_accent,
                font=(self.font_mono, 7, "bold"),
            )

            # 4 Glass KPI Cards (2x2 Grid)
            card_col_w = (body_w - 46) // 2
            card_h = 38

            # Values for cards
            lev_val = f"{active.get('leverage_index', '26,967'):,}" if isinstance(active.get('leverage_index'), (int, float)) and active.get('leverage_index') > 100 else "26,967"
            vol_val = f"{active['tokens_formatted']} TOK"
            hit_val = f"{active['cache_hit_pct']}%"
            if lens == "secular":
                sec_v = active.get("secular_cost_usd", 20.0)
                saved_val = f"${sec_v:,.2f}/MO FLAT"
                saved_sub = "Earthly Flat Cash Outlay"
            elif lens == "spectacular":
                spec_v = active.get("spectacular_usd", 12875)
                saved_val = f"${spec_v:,.0f} WORTH"
                saved_sub = "Gross Frontier Market Value"
            else:
                sav_v = active.get("saved_usd", 10924)
                saved_val = f"${sav_v:,} SAVED"
                saved_sub = "Retail API Compute Saved"

            kpi_cards = [
                ("3-PILLAR LEVERAGE", lev_val, "#1 Heavyweight Architect", "#10B981", 18, 116),
                ("VERIFIED 3-HARNESS VOL", vol_val, "524 Sessions across 3 Harnesses", "#0A84FF", 26 + card_col_w, 116),
                ("PROMPT-CACHE HIT RATE", hit_val, "96.7x Peak Reuse · 1.24x Mult", "#BF5AF2", 18, 158),
                ("RETAIL COMPUTE VALUE", saved_val, saved_sub, "#FF9F0A", 26 + card_col_w, 158),
            ]

            card_bg = "#12141A" if palette.get("is_dark", True) else "#EAEAEF"
            card_border = "#2A2E39" if palette.get("is_dark", True) else "#D1D1D6"

            for c_title, c_val, c_sub, c_acc, cx1, cy1 in kpi_cards:
                cx2 = cx1 + card_col_w
                cy2 = cy1 + card_h
                c_pts = rounded_rect_polygon(cx1, cy1, cx2, cy2, 6, steps=8)
                self.canvas.create_polygon(c_pts, smooth=False, fill=card_bg, outline=card_border, width=1)
                self.canvas.create_line(cx1 + 2, cy1 + 6, cx1 + 2, cy2 - 6, fill=c_acc, width=2.5)
                self.canvas.create_text(cx1 + 8, cy1 + 9, anchor="w", text=c_title, fill=palette["secondary_text"], font=(self.font_mono, 6, "bold"))
                self.canvas.create_text(cx1 + 8, cy1 + 22, anchor="w", text=c_val, fill=palette["primary_text"], font=(self.font_mono, 8, "bold"))
                self.canvas.create_text(cx1 + 8, cy1 + 31, anchor="w", text=c_sub[:28], fill=palette["subtle_text"], font=(self.font_display, 5))

            # Divider line below cards
            self.canvas.create_line(18, 202, body_w - 18, 202, fill=palette["divider"], width=1)
            self.canvas.create_text(
                18,
                210,
                anchor="w",
                text="ACTIVE HARNESS LOADOUT (10 HARNESSES)",
                fill=palette["secondary_text"],
                font=(self.font_mono, 6, "bold"),
            )

            # 10-Harness Comparative Grid
            y_base = 222
            top_harness_keys = [
                "claude_code", "antigravity", "openai_codex", "cursor", "aider",
                "windsurf", "continue_dev", "github_copilot", "openhands", "t3_code"
            ]
            col1 = top_harness_keys[:5]
            col2 = top_harness_keys[5:]

            for row_i, (k1, k2) in enumerate(zip(col1, col2)):
                cur_y = y_base + (row_i * 15)
                h1 = frame["harnesses"].get(k1, active)
                self.canvas.create_oval(18, cur_y - 3, 24, cur_y + 3, fill=h1["accent_hex"], outline="")
                txt1 = f"{h1['short_name'][:9]:<9} {h1['tokens_formatted']:>5} · {h1['cache_hit_pct']}%"
                self.canvas.create_text(28, cur_y, anchor="w", text=txt1, fill=palette["primary_text"], font=(self.font_mono, 7))

                h2 = frame["harnesses"].get(k2, active)
                col2_x = 26 + card_col_w
                self.canvas.create_oval(col2_x, cur_y - 3, col2_x + 6, cur_y + 3, fill=h2["accent_hex"], outline="")
                txt2 = f"{h2['short_name'][:9]:<9} {h2['tokens_formatted']:>5} · {h2['cache_hit_pct']}%"
                self.canvas.create_text(col2_x + 10, cur_y, anchor="w", text=txt2, fill=palette["primary_text"], font=(self.font_mono, 7))

            # Footer Metadata Ribbon
            self.canvas.create_text(
                18,
                314,
                anchor="w",
                text="✓ ELOQUENT (@mjeanhudson-dev) · 0.12 H · 663 COMMITS · SHA256: 0aeaf8f9",
                fill=palette["subtle_text"],
                font=(self.font_mono, 6),
            )

        # 14. Right-Edge Domed Tactile Side Buttons (5 Buttons)
        # Vertical divider line
        self.canvas.create_line(body_w, 14, body_w, self.height - 14, fill=palette["divider"], width=1)

        btn_x1 = body_w + 6
        btn_x2 = self.width - 9
        h5 = (self.height - 28) / 5.0

        # Button 1: Mode Switcher (Domed Stadium Pill)
        b1_y1 = 8
        b1_y2 = int(8 + h5)
        b1_fill = palette["button_hover"] if self._hover_control == "side_mode" else palette["button_bg"]
        self._draw_domed_button(btn_x1, b1_y1, btn_x2, b1_y2, 9, b1_fill, palette["button_border"])
        self.canvas.create_text((btn_x1 + btn_x2) // 2, (b1_y1 + b1_y2) // 2 - 4, text="≋", fill=palette["header"], font=(self.font_display, 8, "bold"))
        self.canvas.create_text((btn_x1 + btn_x2) // 2, (b1_y1 + b1_y2) // 2 + 5, text=self.mode[:4].upper(), fill=palette["secondary_text"], font=(self.font_mono, 6, "bold"))

        # Button 2: Theme Switcher (Domed Stadium Pill)
        b2_y1 = int(8 + h5 + 3)
        b2_y2 = int(8 + 2 * h5 + 3)
        b2_fill = palette["button_hover"] if self._hover_control == "side_theme" else palette["button_bg"]
        self._draw_domed_button(btn_x1, b2_y1, btn_x2, b2_y2, 9, b2_fill, palette["button_border"])
        theme_short = self.theme[:3].upper()
        self.canvas.create_text((btn_x1 + btn_x2) // 2, (b2_y1 + b2_y2) // 2 - 4, text="🎨", fill=palette["header"], font=(self.font_display, 8))
        self.canvas.create_text((btn_x1 + btn_x2) // 2, (b2_y1 + b2_y2) // 2 + 5, text=theme_short, fill="#FF9F0A" if not palette.get("is_dark", True) else "#5E5CE6", font=(self.font_mono, 6, "bold"))

        # Button 3: Boundary Physics Mode (Domed Stadium Pill)
        b3_y1 = int(8 + 2 * h5 + 6)
        b3_y2 = int(8 + 3 * h5 + 6)
        b3_fill = palette["button_hover"] if self._hover_control == "side_physics" else palette["button_bg"]
        self._draw_domed_button(btn_x1, b3_y1, btn_x2, b3_y2, 9, b3_fill, palette["button_border"])
        b_tag = BOUNDARY_SHORT.get(self.boundary_mode, "BNC")
        b_color = "#30D158" if self.boundary_mode == "bounce" else ("#FF9F0A" if self.boundary_mode == "pacman" else palette["subtle_text"])
        self.canvas.create_text((btn_x1 + btn_x2) // 2, (b3_y1 + b3_y2) // 2, text=b_tag, fill=b_color, font=(self.font_mono, 7, "bold"))

        # Button 4: Dedicated Quick Always-on-Top Toggle (Domed Stadium Pill)
        b4_y1 = int(8 + 3 * h5 + 9)
        b4_y2 = int(8 + 4 * h5 + 9)
        is_topmost = bool(self.settings.get("topmost", True))
        b4_fill = palette["button_hover"] if self._hover_control == "side_topmost" else (
            ("#133620" if palette.get("is_dark", True) else "#D4F4DD") if is_topmost else palette["button_bg"]
        )
        b4_border = "#30D158" if is_topmost else palette["button_border"]
        self._draw_domed_button(btn_x1, b4_y1, btn_x2, b4_y2, 9, b4_fill, b4_border)
        top_color = "#30D158" if is_topmost else palette["subtle_text"]
        self.canvas.create_text((btn_x1 + btn_x2) // 2, (b4_y1 + b4_y2) // 2 - 4, text="📌", fill=top_color, font=(self.font_display, 7))
        self.canvas.create_text((btn_x1 + btn_x2) // 2, (b4_y1 + b4_y2) // 2 + 5, text="TOP" if is_topmost else "OFF", fill=top_color, font=(self.font_mono, 6, "bold"))

        # Button 5: Quick Launch Web Dashboard (Domed Stadium Pill)
        b5_y1 = int(8 + 4 * h5 + 12)
        b5_y2 = int(self.height - 8)
        b5_fill = "#0066CC" if self._hover_control == "side_web" else palette["button_bg"]
        b5_fg = "#FFFFFF" if self._hover_control == "side_web" else "#0A84FF"
        self._draw_domed_button(btn_x1, b5_y1, btn_x2, b5_y2, 9, b5_fill, palette["button_border"])
        self.canvas.create_text((btn_x1 + btn_x2) // 2, (b5_y1 + b5_y2) // 2 - 4, text="🌐", fill=b5_fg, font=(self.font_display, 8))
        self.canvas.create_text((btn_x1 + btn_x2) // 2, (b5_y1 + b5_y2) // 2 + 5, text="WEB", fill=b5_fg, font=(self.font_mono, 6, "bold"))

    def open_settings_dialog(self) -> None:
        if self._settings_window and self._settings_window.winfo_exists():
            self._settings_window.lift()
            return

        sw = tk.Toplevel(self.root)
        self._settings_window = sw
        sw.title("Aether Pulse Settings")
        sw.geometry("490x850")
        sw.resizable(False, False)
        sw.attributes("-topmost", True)

        palette = self.get_active_palette()
        sw.configure(bg=palette["pill_bg"])

        # Title
        tk.Label(
            sw,
            text="⚡ Aether Pulse Settings",
            bg=palette["pill_bg"],
            fg=palette["header"],
            font=(self.font_display, 13, "bold"),
        ).pack(anchor="w", padx=22, pady=(16, 4))

        container = tk.Frame(sw, bg=palette["pill_bg"])
        container.pack(fill=tk.BOTH, expand=True, padx=22, pady=4)

        # 0. Subscription Loadout & Humorous Tier Engine
        tk.Label(
            container,
            text="ACTIVE SUBSCRIPTIONS (TIER CALCULATOR):",
            bg=palette["pill_bg"],
            fg=palette["secondary_text"],
            font=(self.font_mono, 8, "bold"),
        ).pack(anchor="w", pady=(2, 2))

        sub_grid = tk.Frame(container, bg=palette["pill_bg"])
        sub_grid.pack(fill=tk.X, pady=(0, 2))
        sg_left = tk.Frame(sub_grid, bg=palette["pill_bg"])
        sg_left.pack(side=tk.LEFT, fill=tk.X, expand=True)
        sg_right = tk.Frame(sub_grid, bg=palette["pill_bg"])
        sg_right.pack(side=tk.LEFT, fill=tk.X, expand=True)

        current_active = set(self.settings.get("active_subscriptions", ["claude_code", "antigravity", "openai_codex"]))
        sub_vars: Dict[str, tk.BooleanVar] = {}

        for i, (sk, sname) in enumerate(AVAILABLE_SUBSCRIPTIONS):
            var = tk.BooleanVar(value=(sk in current_active))
            sub_vars[sk] = var
            parent_col = sg_left if i < 5 else sg_right
            cb = tk.Checkbutton(
                parent_col,
                text=sname,
                variable=var,
                bg=palette["pill_bg"],
                fg=palette["primary_text"],
                selectcolor=palette["button_bg"],
                activebackground=palette["pill_bg"],
                font=(self.font_text, 8),
            )
            cb.pack(anchor="w", pady=0)

        # Dynamic Live Tier Card
        tier_card = tk.Frame(container, bg=palette["button_bg"], bd=1, relief=tk.SOLID)
        tier_card.pack(fill=tk.X, pady=(2, 4), padx=2)

        tier_badge_lbl = tk.Label(tier_card, text="", bg=palette["button_bg"], fg=palette["header"], font=(self.font_mono, 9, "bold"))
        tier_badge_lbl.pack(anchor="w", padx=8, pady=(3, 0))

        tier_tag_lbl = tk.Label(tier_card, text="", bg=palette["button_bg"], fg=palette["secondary_text"], font=(self.font_text, 8, "italic"))
        tier_tag_lbl.pack(anchor="w", padx=8, pady=(0, 3))

        alias_frame = tk.Frame(container, bg=palette["pill_bg"])
        alias_frame.pack(fill=tk.X, pady=(0, 4))
        tk.Label(alias_frame, text="Custom Tier Alias (Optional Override):", bg=palette["pill_bg"], fg=palette["secondary_text"], font=(self.font_mono, 8)).pack(anchor="w")

        custom_name_var = tk.StringVar(value=self.settings.get("custom_tier_name", ""))
        alias_ent = tk.Entry(alias_frame, textvariable=custom_name_var, bg=palette["button_bg"], fg=palette["primary_text"], insertbackground=palette["primary_text"], bd=1, relief=tk.SOLID, font=(self.font_text, 9))
        alias_ent.pack(fill=tk.X, pady=(1, 0))

        def _refresh_tier_card(*args):
            sel_count = max(1, sum(1 for v in sub_vars.values() if v.get()))
            c_name = custom_name_var.get().strip()
            t = get_subscription_tier(sel_count, c_name)
            tier_badge_lbl.config(text=f"⚡ Active Tier: {t['name']} ({sel_count} Active Subs)")
            tier_tag_lbl.config(text=f'"{t["tagline"]}"')

        for v in sub_vars.values():
            v.trace_add("write", _refresh_tier_card)
        custom_name_var.trace_add("write", _refresh_tier_card)
        _refresh_tier_card()

        # 1. Physics Mode Selector
        tk.Label(container, text="BOUNDARY DYNAMICS:", bg=palette["pill_bg"], fg=palette["secondary_text"], font=(self.font_mono, 8, "bold")).pack(anchor="w", pady=(4, 2))
        bmode_var = tk.StringVar(value=self.boundary_mode)
        bframe = tk.Frame(container, bg=palette["pill_bg"])
        bframe.pack(fill=tk.X, pady=(0, 6))
        for bval, blabel in [("bounce", "Bounce Walls (Natural Drift & Crashes)"), ("pacman", "Pac-Man Toroidal Edge Wrap"), ("pin", "Pinned Anchor (Rock-Solid Zero Wiggle)")]:
            tk.Radiobutton(
                bframe,
                text=blabel,
                variable=bmode_var,
                value=bval,
                bg=palette["pill_bg"],
                fg=palette["primary_text"],
                selectcolor=palette["button_bg"],
                activebackground=palette["pill_bg"],
                font=(self.font_text, 9),
            ).pack(anchor="w", pady=1)

        # 2. Visual Palette (8 Themes)
        tk.Label(container, text="THEME PALETTES:", bg=palette["pill_bg"], fg=palette["secondary_text"], font=(self.font_mono, 8, "bold")).pack(anchor="w", pady=(4, 2))
        theme_var = tk.StringVar(value=self.theme)
        tframe = tk.Frame(container, bg=palette["pill_bg"])
        tframe.pack(fill=tk.X, pady=(0, 6))

        # 2-column radio grid for 8 themes
        col1 = THEME_ORDER[:4]
        col2 = THEME_ORDER[4:]
        tgrid = tk.Frame(tframe, bg=palette["pill_bg"])
        tgrid.pack(fill=tk.X)
        c1_frame = tk.Frame(tgrid, bg=palette["pill_bg"])
        c1_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        c2_frame = tk.Frame(tgrid, bg=palette["pill_bg"])
        c2_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        for tname in col1:
            p = THEME_PALETTES[tname]
            tk.Radiobutton(
                c1_frame,
                text=p["name"],
                variable=theme_var,
                value=tname,
                bg=palette["pill_bg"],
                fg=palette["primary_text"],
                selectcolor=palette["button_bg"],
                font=(self.font_text, 8),
            ).pack(anchor="w", pady=1)

        for tname in col2:
            p = THEME_PALETTES[tname]
            tk.Radiobutton(
                c2_frame,
                text=p["name"],
                variable=theme_var,
                value=tname,
                bg=palette["pill_bg"],
                fg=palette["primary_text"],
                selectcolor=palette["button_bg"],
                font=(self.font_text, 8),
            ).pack(anchor="w", pady=1)

        # 3. Detailed Color Picking Options
        color_row = tk.Frame(container, bg=palette["pill_bg"])
        color_row.pack(fill=tk.X, pady=(2, 6))

        custom_accent_val = self.settings.get("custom_accent", "#0066CC")
        custom_liquid_val = self.settings.get("custom_liquid", "#0E243B")

        def _pick_accent():
            c = colorchooser.askcolor(title="Choose Custom Accent Color", initialcolor=custom_accent_val)
            if c and c[1]:
                self.settings["custom_accent"] = c[1]

        def _pick_liquid():
            c = colorchooser.askcolor(title="Choose Custom Liquid Color", initialcolor=custom_liquid_val)
            if c and c[1]:
                self.settings["custom_liquid"] = c[1]

        DomedPillButton(color_row, "🎨 Pick Accent", _pick_accent, width=105, height=26, bg_color=palette["button_bg"], fg_color=palette["primary_text"], hover_bg=palette["button_hover"], border_color=palette["button_border"], font=(self.font_text, 8), theme=self.theme, container_bg=palette["pill_bg"]).pack(side=tk.LEFT, padx=(0, 6))
        DomedPillButton(color_row, "🌊 Pick Liquid", _pick_liquid, width=105, height=26, bg_color=palette["button_bg"], fg_color=palette["primary_text"], hover_bg=palette["button_hover"], border_color=palette["button_border"], font=(self.font_text, 8), theme=self.theme, container_bg=palette["pill_bg"]).pack(side=tk.LEFT)

        # 4. Accounting Lens Radio Selector
        tk.Label(container, text="ACCOUNTING LENS (USAGE & WORTH):", bg=palette["pill_bg"], fg=palette["secondary_text"], font=(self.font_mono, 8, "bold")).pack(anchor="w", pady=(4, 2))
        lens_frame = tk.Frame(container, bg=palette["pill_bg"])
        lens_frame.pack(fill=tk.X, pady=2)
        lens_var = tk.StringVar(value=self.settings.get("accounting_lens", "specular"))
        for l_key, l_label in [
            ("specular", "💎 Specular ($244.42 Official Metered Developer API Compute)"),
            ("secular", "👁️ Secular ($20.00/mo Earthly Flat Cash Subscription)"),
            ("spectacular", "⚡ Spectacular ($5,110+ Gross Frontier Market Worth Delivered)"),
        ]:
            tk.Radiobutton(
                lens_frame,
                text=l_label,
                value=l_key,
                variable=lens_var,
                bg=palette["pill_bg"],
                fg=palette["primary_text"],
                selectcolor=palette["button_bg"],
                font=(self.font_text, 8),
            ).pack(anchor="w", pady=1)

        # 5. Feature Set Checkboxes
        tk.Label(container, text="FEATURE TOGGLES:", bg=palette["pill_bg"], fg=palette["secondary_text"], font=(self.font_mono, 8, "bold")).pack(anchor="w", pady=(4, 2))
        fizz_var = tk.BooleanVar(value=bool(self.settings.get("enable_fizz", True)))
        lava_var = tk.BooleanVar(value=bool(self.settings.get("simulate_lava_5hr", False)))
        part_var = tk.BooleanVar(value=bool(self.settings.get("enable_particles", True)))
        top_var = tk.BooleanVar(value=bool(self.settings.get("topmost", True)))
        tray_close_var = tk.BooleanVar(value=bool(self.settings.get("close_to_tray", True)))

        tk.Checkbutton(container, text="Effervescent Agent Fizzing Micro-Bubbles", variable=fizz_var, bg=palette["pill_bg"], fg=palette["primary_text"], selectcolor=palette["button_bg"], font=(self.font_text, 8)).pack(anchor="w", pady=1)
        tk.Checkbutton(container, text="Molten Lava Mode (Simulate 5-Hour Usage Limit)", variable=lava_var, bg=palette["pill_bg"], fg=palette["primary_text"], selectcolor=palette["button_bg"], font=(self.font_text, 8)).pack(anchor="w", pady=1)
        tk.Checkbutton(container, text="Wall Splash Wave & Droplet Particles", variable=part_var, bg=palette["pill_bg"], fg=palette["primary_text"], selectcolor=palette["button_bg"], font=(self.font_text, 8)).pack(anchor="w", pady=1)
        tk.Checkbutton(container, text="Always on Top (Topmost Window)", variable=top_var, bg=palette["pill_bg"], fg=palette["primary_text"], selectcolor=palette["button_bg"], font=(self.font_text, 8)).pack(anchor="w", pady=1)
        tk.Checkbutton(container, text="Close Button ('✕') Minimizes to System Tray", variable=tray_close_var, bg=palette["pill_bg"], fg=palette["primary_text"], selectcolor=palette["button_bg"], font=(self.font_text, 8)).pack(anchor="w", pady=1)

        # 5. Save & Apply (Domed Stadium Pill Buttons)
        def _save_and_apply():
            new_bmode = bmode_var.get()
            new_theme = theme_var.get()

            self.boundary_mode = new_bmode
            self.settings["boundary_mode"] = new_bmode
            self.phys["boundary_mode"] = new_bmode

            if new_bmode == "pin":
                self.phys["vx"] = 0.0
                self.phys["vy"] = 0.0

            if new_theme != self.theme:
                self.theme = new_theme
                self.settings["theme"] = new_theme

            self.settings["enable_fizz"] = fizz_var.get()
            self.settings["simulate_lava_5hr"] = lava_var.get()
            self.settings["enable_particles"] = part_var.get()
            self.settings["topmost"] = top_var.get()
            self.settings["accounting_lens"] = lens_var.get()
            self.lens = lens_var.get()
            self.settings["close_to_tray"] = tray_close_var.get()

            new_active_subs = [sk for sk, v in sub_vars.items() if v.get()]
            self.settings["active_subscriptions"] = new_active_subs if new_active_subs else ["claude_code"]
            self.settings["custom_tier_name"] = custom_name_var.get().strip()

            self.root.attributes("-topmost", bool(top_var.get()))
            self._save_settings()
            sw.destroy()
            self._render()

        btn_row = tk.Frame(sw, bg=palette["pill_bg"])
        btn_row.pack(fill=tk.X, padx=22, pady=(10, 16))

        apply_btn = DomedPillButton(
            btn_row,
            text="Save & Apply",
            command=_save_and_apply,
            width=128,
            height=34,
            bg_color="#0066CC",
            fg_color="#FFFFFF",
            hover_bg="#0077EE",
            border_color="#0055AA",
            font=(self.font_text, 9, "bold"),
            theme=self.theme,
            container_bg=palette["pill_bg"],
        )
        apply_btn.pack(side=tk.RIGHT)

        cancel_btn = DomedPillButton(
            btn_row,
            text="Cancel",
            command=sw.destroy,
            width=90,
            height=34,
            bg_color=palette["button_bg"],
            fg_color=palette["primary_text"],
            hover_bg=palette["button_hover"],
            border_color=palette["button_border"],
            font=(self.font_text, 9),
            theme=self.theme,
            container_bg=palette["pill_bg"],
        )
        cancel_btn.pack(side=tk.RIGHT, padx=10)

    def run(self) -> None:
        self.root.mainloop()


if __name__ == "__main__":
    if "--smoke-test" in sys.argv:
        phys = aether_pulse_ws.create_liquid_physics_state(100, 100, num_nodes=48, boundary_mode="pin")
        for _ in range(40):
            aether_pulse_ws.step_liquid_physics(phys, 100, 100, 0.016, is_dragging=False, bounds_w=500.0, bounds_h=300.0)
        print(
            "Desktop Liquid Overlay physics smoke test (PINNED):",
            f"x={phys['x']}",
            f"y={phys['y']}",
            f"vx={phys['vx']}",
            f"vy={phys['vy']}",
            f"tilt={phys['tilt_deg']}",
            f"bounces={phys['wall_bounces']}",
        )
    elif "--tkinter" in sys.argv or "--legacy" in sys.argv:
        AetherLiquidDesktopOverlay().run()
    else:
        try:
            import launch_hud
            launch_hud.main()
        except Exception:
            AetherLiquidDesktopOverlay().run()
