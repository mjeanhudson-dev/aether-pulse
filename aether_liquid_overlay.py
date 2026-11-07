#!/usr/bin/env python3
"""
Aether Pulse — Native Desktop Floating Liquid-Physics Overlay (`aether_liquid_overlay.py`)
========================================================================================
Authored by Eloquent (@mjeanhudson-dev)

Apple Design Philosophy Restoration:
  1. Authentic Full-Cup Oceanic Liquid Physics:
     Dual-layer volumetric wave (undercurrent parallax depth + primary radiant fluid mass)
     coupled with a smoothed specular crest line and dynamic wall splash particles.
     Weighty inertial tracking (2.6 kg mass feeling, natural drag lag, high-speed viscous eddy braking,
     and rock-solid absolute latch when pinned).
  2. Zero Bottom-Clipping & True Win32 Hardware Rounded Corners:
     Frameless window with CreateRoundRectRgn/SetWindowRgn hardware clipping (24px corner radius)
     without noisy transparency masks or blue corner leakage.
  3. Clean Minimalist Typography & Layout:
     - Top Header: Accent status dot + Active Harness / Tier Title + Boundary State.
     - Hero Metric: Large bold % Cache hit + Tabular tokens, cost, and leverage points.
     - Subtitle: Spatial target context + Retail compute saved.
     - Glowing hairline divider.
     - Comparative Drawer Rows (Claude Code, Google Antigravity, OpenAI Codex) with authentic 3-Lens compute.
  4. Spacious 2-Button Right Control Rail:
     - Top Button: Mode Switcher (≋ AUTO / ALL 3 / CLAU / AGY / CODEX)
     - Bottom Button: Physics Switcher (PIN / BNC / PAC)
  5. Power Features:
     - 1-click accounting lens cycling on metric click (Specular API / Secular Flat Cash / Spectacular Frontier Value).
     - Standalone Desktop Studio launcher on double-click (Edge native --app mode or browser).
     - Cupertino right-click popup context menu for themes, lenses, always-on-top, and settings.
     - System Tray integration.
"""

from __future__ import annotations

import ctypes
from ctypes import wintypes
import json
import math
import os
import random
import subprocess
import sys
import time
import tkinter as tk
from tkinter import font as tkfont
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
    "topmost": True,
    "accounting_lens": "specular",
    "close_to_tray": True,
    "active_subscriptions": ["claude_code", "antigravity", "openai_codex"],
    "custom_tier_name": "",
}

SUBSCRIPTION_TIERS: Dict[int, Dict[str, str]] = {
    1: {"name": "Unoemono", "tagline": "Solo lone wolf with one token allowance"},
    2: {"name": "Couples Fighting", "tagline": "Two CLIs arguing over merge conflicts"},
    3: {"name": "Trinity", "tagline": "The sacred three-way prompt-caching triangle"},
    4: {"name": "Quap", "tagline": "Four harnesses deep in multi-model synergy"},
    5: {"name": "Pentagoon", "tagline": "Five subscriptions, certified AI terminal goon squad"},
    6: {"name": "Six-Pack Meltdown", "tagline": "Six subscriptions shredding your budget"},
    7: {"name": "Seven Deadly Subs", "tagline": "Seven deadly sins of context bloat"},
    8: {"name": "Octo-Chaos", "tagline": "Eight tentacles flailing across every shell session"},
    9: {"name": "Cloud Nine Overdraft", "tagline": "Floating on infinite context while your card declines"},
    10: {"name": "Ten-Ring Circus", "tagline": "The full ten-ring unhinged developer clown show"},
}

BOUNDARY_SHORT = {
    "bounce": "BNC",
    "pacman": "PAC",
    "pin": "PIN",
}

THEME_PALETTES = {
    "dark": {
        "bg": "#121214",
        "surface": "#1A1A1E",
        "border": "#2C2C2E",
        "header": "#F5F5F7",
        "primary_text": "#FFFFFF",
        "secondary_text": "#A1A1A6",
        "subtle_text": "#75757C",
        "button_bg": "#1C1C1E",
        "button_hover": "#2A2A2E",
        "button_border": "#3A3A3C",
        "divider": "#2C2C2E",
        "divider_glow": "#1A365D",
        "fluid_back": "#0D1826",
        "fluid_front": "#13273D",
        "crest_glow": "#388BFF",
        "particle_color": "#E5E5EA",
        "is_dark": True,
    },
    "light": {
        "bg": "#F8F8FA",
        "surface": "#FFFFFF",
        "border": "#E5E5EA",
        "header": "#1D1D1F",
        "primary_text": "#000000",
        "secondary_text": "#5A5A60",
        "subtle_text": "#8E8E93",
        "button_bg": "#FFFFFF",
        "button_hover": "#F0F0F5",
        "button_border": "#D1D1D6",
        "divider": "#E5E5EA",
        "divider_glow": "#BBD7F5",
        "fluid_back": "#DCEAF7",
        "fluid_front": "#C8E1FA",
        "crest_glow": "#0066CC",
        "particle_color": "#0066CC",
        "is_dark": False,
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

    def step(self, dt: float, gravity: float = 480.0) -> bool:
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += gravity * dt
        self.life -= dt * 2.4
        return self.life > 0.0


class AetherLiquidDesktopOverlay:
    def __init__(self) -> None:
        self.settings = self._load_settings()
        self.report = aether_pulse.scan_local_harnesses()
        self.mode = self.settings.get("overlay_mode", "auto")
        self.boundary_mode = self.settings.get("boundary_mode", "bounce")
        self.theme = self.settings.get("theme", "dark")
        if self.theme not in THEME_PALETTES:
            self.theme = "dark"

        self.detected_harness = "all"
        self.target_label = "Desktop Workspace"

        self.root = tk.Tk()
        self.root.title("Aether Pulse Liquid HUD")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", bool(self.settings.get("topmost", True)))
        self.root.attributes("-alpha", 0.96)

        palette = THEME_PALETTES[self.theme]
        self.root.configure(bg=palette["bg"])

        self.screen_w = float(max(800, self.root.winfo_screenwidth()))
        self.screen_h = float(max(600, self.root.winfo_screenheight()))

        self.width = 464
        self.height = 184 if self.mode == "all" else 114
        self.corner_radius = 24

        self.target_x = max(20.0, min(self.screen_w - self.width - 20.0, 140.0))
        self.target_y = max(20.0, min(self.screen_h - self.height - 20.0, 140.0))

        self.phys = aether_pulse_ws.create_liquid_physics_state(
            x=self.target_x,
            y=self.target_y,
            num_nodes=48,
            boundary_mode=self.boundary_mode,
            width=float(self.width),
            height=float(self.height),
        )
        if self.boundary_mode in ("bounce", "pacman"):
            self.phys["vx"] = 46.0
            self.phys["vy"] = 28.0

        self.root.geometry(f"{self.width}x{self.height}+{int(self.target_x)}+{int(self.target_y)}")

        self.canvas = tk.Canvas(
            self.root,
            width=self.width,
            height=self.height,
            bg=palette["bg"],
            highlightthickness=1,
            highlightbackground=palette["border"],
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self._init_fonts()
        self.particles: List[SplashParticle] = []
        self._hover_btn: Optional[str] = None
        self._hover_harness: Optional[str] = None

        self._drag_offset_x = 0
        self._drag_offset_y = 0
        self._is_dragging = False
        self._last_t = time.perf_counter()
        self._last_probe_t = 0.0
        self._last_ptr_x = 0.0
        self._last_ptr_y = 0.0
        self._last_ptr_t = time.perf_counter()
        self._throw_vx = 0.0
        self._throw_vy = 0.0
        self.tray_icon = None

        self.canvas.bind("<ButtonPress-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)
        self.canvas.bind("<Double-Button-1>", self._on_double_click)
        self.canvas.bind("<Button-3>", self._on_right_click)
        self.canvas.bind("<Motion>", self._on_mouse_move)
        self.canvas.bind("<Leave>", self._on_mouse_leave)

        self.root.update_idletasks()
        self._apply_rounded_window_region()
        self._init_system_tray()

        self._tick()

    def _load_settings(self) -> Dict[str, Any]:
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    res = DEFAULT_SETTINGS.copy()
                    res.update(data)
                    return res
            except Exception:
                pass
        return DEFAULT_SETTINGS.copy()

    def _save_settings(self) -> None:
        try:
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=2)
        except Exception:
            pass

    def _init_fonts(self) -> None:
        avail = set(tkfont.families())
        self.font_display = next((f for f in ["SF Pro Display", "Segoe UI Variable Display", "Segoe UI", "Helvetica Neue", "Arial"] if f in avail), "Segoe UI")
        self.font_mono = next((f for f in ["SF Mono", "Cascadia Code", "JetBrains Mono", "Consolas", "Courier New"] if f in avail), "Consolas")

    def _apply_rounded_window_region(self) -> None:
        if sys.platform != "win32":
            return
        try:
            hwnd = self.root.winfo_id()
            try:
                ctypes.windll.dwmapi.DwmSetWindowAttribute(
                    hwnd, 33, ctypes.byref(ctypes.c_int(2)), ctypes.sizeof(ctypes.c_int)
                )
            except Exception:
                pass
            rgn = ctypes.windll.gdi32.CreateRoundRectRgn(
                0, 0, self.width + 1, self.height + 1, self.corner_radius, self.corner_radius
            )
            ctypes.windll.user32.SetWindowRgn(hwnd, rgn, True)
        except Exception:
            pass

    def _init_system_tray(self) -> None:
        if not HAS_TRAY:
            return
        try:
            png_path = "chrome-extension/icons/icon-48.png"
            ico_path = "aether_pulse.ico"
            icon_img = None
            if os.path.exists(png_path):
                icon_img = Image.open(png_path)
            elif os.path.exists(ico_path):
                icon_img = Image.open(ico_path)

            if icon_img:
                menu = pystray.Menu(
                    pystray.MenuItem("Restore Aether HUD", self._restore_from_tray, default=True),
                    pystray.MenuItem("Launch 4K Studio Dashboard", lambda: self._launch_studio()),
                    pystray.MenuItem("Toggle Theme", lambda: self._toggle_theme()),
                    pystray.MenuItem("Exit Aether Pulse", self._exit_application),
                )
                self.tray_icon = pystray.Icon("AetherPulse", icon_img, "Aether Pulse HUD", menu)
                import threading
                threading.Thread(target=self.tray_icon.run, daemon=True).start()
        except Exception:
            pass

    def _restore_from_tray(self) -> None:
        self.root.deiconify()
        self.root.attributes("-topmost", bool(self.settings.get("topmost", True)))
        self.root.update_idletasks()
        self._apply_rounded_window_region()

    def _minimize_to_tray(self) -> None:
        self.root.withdraw()

    def _exit_application(self) -> None:
        if self.tray_icon:
            try:
                self.tray_icon.stop()
            except Exception:
                pass
        self.root.destroy()
        os._exit(0)

    def _toggle_theme(self) -> None:
        self.theme = "light" if self.theme == "dark" else "dark"
        self.settings["theme"] = self.theme
        self._save_settings()
        palette = THEME_PALETTES[self.theme]
        self.root.configure(bg=palette["bg"])
        self.canvas.configure(bg=palette["bg"], highlightbackground=palette["border"])
        self._render()

    def _cycle_accounting_lens(self) -> None:
        order = ["specular", "secular", "spectacular"]
        curr = self.settings.get("accounting_lens", "specular")
        nxt = order[(order.index(curr) + 1) % len(order)] if curr in order else "specular"
        self.settings["accounting_lens"] = nxt
        self._save_settings()
        # Ripple mid-water excitation
        mid = len(self.phys["wave_velocities"]) // 2
        self.phys["wave_velocities"][mid] += 32.0
        self._render()

    def _toggle_always_on_top(self) -> None:
        curr = bool(self.settings.get("topmost", True))
        nxt = not curr
        self.settings["topmost"] = nxt
        self.root.attributes("-topmost", nxt)
        self._save_settings()
        self._render()

    def _launch_studio(self) -> None:
        local_url = "http://127.0.0.1:8765/"
        edge_paths = [
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        ]
        edge_bin = next((p for p in edge_paths if os.path.exists(p)), None)
        if edge_bin:
            try:
                subprocess.Popen([
                    edge_bin,
                    f"--app={local_url}",
                    "--window-size=1440,900",
                    "--window-position=120,60",
                ])
                return
            except Exception:
                pass
        webbrowser.open(local_url)

    def _update_height_for_mode(self) -> None:
        self.height = 184 if self.mode == "all" else 114
        self.phys["height"] = float(self.height)
        self.canvas.config(height=self.height)
        self.root.update_idletasks()
        self._apply_rounded_window_region()

    def _spawn_splash_particles(self, side: str, impulse: float, accent_hex: str) -> None:
        if not self.settings.get("enable_particles", True):
            return
        count = min(18, max(5, int(impulse * 0.14)))
        body_w = self.width - 56
        palette = THEME_PALETTES[self.theme]

        for _ in range(count):
            if side == "left":
                px = random.uniform(8.0, 24.0)
                py = random.uniform(self.height * 0.44, self.height * 0.88)
                vx = random.uniform(30.0, 150.0)
                vy = random.uniform(-220.0, -50.0)
            elif side == "right":
                px = random.uniform(body_w - 24.0, body_w - 8.0)
                py = random.uniform(self.height * 0.44, self.height * 0.88)
                vx = random.uniform(-150.0, -30.0)
                vy = random.uniform(-220.0, -50.0)
            else:
                px = random.uniform(16.0, body_w - 16.0)
                py = random.uniform(self.height * 0.60, self.height - 12.0)
                vx = random.uniform(-70.0, 70.0)
                vy = random.uniform(-180.0, -40.0)

            size = random.uniform(1.6, 3.0)
            color = accent_hex if random.random() > 0.4 else palette["particle_color"]
            self.particles.append(SplashParticle(px, py, vx, vy, size, color))

    def _on_mouse_move(self, event: tk.Event) -> None:
        old_hover = self._hover_btn
        self._hover_btn = None
        body_w = self.width - 56

        if event.x >= body_w:
            mid_y = self.height // 2
            if event.y < mid_y:
                self._hover_btn = "btn_mode"
            else:
                self._hover_btn = "btn_physics"

        old_harness = self._hover_harness
        self._hover_harness = None
        if self.mode == "all" and event.y > 100 and event.x < body_w:
            top_harness_keys = ["claude_code", "antigravity", "openai_codex"]
            row_i = min(2, max(0, int((event.y - 104) // 24)))
            self._hover_harness = top_harness_keys[row_i]

        if old_hover != self._hover_btn or old_harness != self._hover_harness:
            self._render()

    def _on_mouse_leave(self, _event: tk.Event) -> None:
        if self._hover_btn is not None or self._hover_harness is not None:
            self._hover_btn = None
            self._hover_harness = None
            self._render()

    def _on_double_click(self, _event: tk.Event) -> None:
        self._launch_studio()

    def _on_right_click(self, event: tk.Event) -> None:
        palette = THEME_PALETTES[self.theme]
        menu = tk.Menu(self.root, tearoff=0, bg=palette["surface"], fg=palette["primary_text"], activebackground=palette["button_hover"], activeforeground=palette["header"])
        menu.add_command(label="🖥️ Launch 4K Studio Dashboard", command=self._launch_studio)
        menu.add_separator()
        theme_label = "☀️ Switch to Light Mode" if self.theme == "dark" else "🌙 Switch to Dark Mode"
        menu.add_command(label=theme_label, command=self._toggle_theme)
        lens_sub = tk.Menu(menu, tearoff=0, bg=palette["surface"], fg=palette["primary_text"])
        lens_sub.add_command(label="💎 Specular (Developer API Standard)", command=lambda: self._set_lens("specular"))
        lens_sub.add_command(label="👁️ Secular (Flat Monthly Cash Outlay)", command=lambda: self._set_lens("secular"))
        lens_sub.add_command(label="⚡ Spectacular (Frontier Replacement Worth)", command=lambda: self._set_lens("spectacular"))
        menu.add_cascade(label="💎 Accounting Lens", menu=lens_sub)
        menu.add_command(label="📌 Toggle Always On Top", command=self._toggle_always_on_top)
        menu.add_separator()
        menu.add_command(label="✕ Minimize to Tray", command=self._minimize_to_tray)
        menu.add_command(label="⏻ Exit", command=self._exit_application)
        menu.tk_popup(event.x_root, event.y_root)

    def _set_lens(self, lens: str) -> None:
        self.settings["accounting_lens"] = lens
        self._save_settings()
        self._render()

    def _on_press(self, event: tk.Event) -> None:
        body_w = self.width - 56
        if event.x >= body_w:
            mid_y = self.height // 2
            if event.y < mid_y:
                self.mode = aether_pulse_ws.next_overlay_mode(self.mode)
                self.settings["overlay_mode"] = self.mode
                self._save_settings()
                mid = len(self.phys["wave_velocities"]) // 2
                self.phys["wave_velocities"][mid] += 48.0
                self._update_height_for_mode()
            else:
                self.boundary_mode = aether_pulse_ws.next_boundary_mode(self.boundary_mode)
                self.settings["boundary_mode"] = self.boundary_mode
                self.phys["boundary_mode"] = self.boundary_mode
                self._save_settings()
                mid = len(self.phys["wave_velocities"]) // 2
                self.phys["wave_velocities"][mid] += 36.0
                if self.boundary_mode in ("bounce", "pacman") and math.hypot(self.phys["vx"], self.phys["vy"]) < 20.0:
                    self.phys["vx"] = 58.0
                    self.phys["vy"] = -34.0
                elif self.boundary_mode == "pin":
                    self.phys["vx"] = 0.0
                    self.phys["vy"] = 0.0
            return

        # Clicking on the hero metric line cycles accounting lenses
        if 14 <= event.x < body_w and 38 <= event.y <= 62:
            self._cycle_accounting_lens()
            return

        # Start Dragging with authentic weight
        self._is_dragging = True
        self._drag_offset_x = event.x
        self._drag_offset_y = event.y
        self._last_ptr_x = float(self.root.winfo_pointerx())
        self._last_ptr_y = float(self.root.winfo_pointery())
        self._last_ptr_t = time.perf_counter()
        self._throw_vx = 0.0
        self._throw_vy = 0.0

    def _on_drag(self, _event: tk.Event) -> None:
        if not self._is_dragging:
            return
        now = time.perf_counter()
        px = float(self.root.winfo_pointerx())
        py = float(self.root.winfo_pointery())
        dt_ptr = max(0.004, now - self._last_ptr_t)
        inst_vx = (px - self._last_ptr_x) / dt_ptr
        inst_vy = (py - self._last_ptr_y) / dt_ptr
        self._throw_vx = 0.65 * self._throw_vx + 0.35 * inst_vx
        self._throw_vy = 0.65 * self._throw_vy + 0.35 * inst_vy
        self._last_ptr_x = px
        self._last_ptr_y = py
        self._last_ptr_t = now

        self.target_x = px - self._drag_offset_x
        self.target_y = py - self._drag_offset_y
        self._probe_underneath(now, force=True)

    def _on_release(self, _event: tk.Event) -> None:
        if not self._is_dragging:
            return
        self._is_dragging = False
        # Preserve throw momentum so it drifts and bounces naturally
        self.phys["vx"] = max(-820.0, min(820.0, self._throw_vx * 0.55 + (48.0 if abs(self._throw_vx) < 20.0 else 0.0)))
        self.phys["vy"] = max(-820.0, min(820.0, self._throw_vy * 0.55 + (-32.0 if abs(self._throw_vy) < 20.0 else 0.0)))
        self.target_x = float(self.phys["x"])
        self.target_y = float(self.phys["y"])

    def _probe_underneath(self, now: float, force: bool = False) -> None:
        if not force and (now - self._last_probe_t) < 0.16:
            return
        self._last_probe_t = now
        probe_x = int(self.phys["x"] + self.width // 2)
        probe_y = int(self.phys["y"] + self.height + 12)
        probed = aether_pulse_ws.probe_window_at_point(probe_x, probe_y, ignore_hwnd=self.root.winfo_id())
        self.detected_harness = probed["detected_harness"]
        if probed["window_title"]:
            self.target_label = probed["window_title"][:28]
        elif probed.get("process_name"):
            self.target_label = probed["process_name"][:28]

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

        # Trigger kinetic splash particles on wall bounce
        splash = self.phys.get("splash_event")
        if splash:
            active_accent = THEME_PALETTES[self.theme]["crest_glow"]
            self._spawn_splash_particles(splash["side"], splash["impulse"], active_accent)

        # Step dynamic splash particles
        alive_particles = []
        for p in self.particles:
            if p.step(dt):
                alive_particles.append(p)
        self.particles = alive_particles

        if not self._is_dragging:
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
        palette = THEME_PALETTES[self.theme]

        self.canvas.delete("all")

        body_w = self.width - 56
        base_y = 90.0 if not frame.get("show_all_drawer", False) else 96.0
        waves = self.phys["wave_heights"]
        n = len(waves)
        tilt = float(self.phys["tilt_deg"])

        # 1. Back wave layer (translucent parallax depth)
        back_pts = [0, self.height]
        for i, h in enumerate(waves):
            px = (i / max(1, n - 1)) * body_w
            back_h = h * 0.70 + math.sin(float(self.phys["phase"]) * 2.8 + i * 0.28) * 2.2
            py = max(8.0, min(self.height - 2.0, base_y - 4.0 + back_h + (tilt * ((i - n / 2) * 0.38))))
            back_pts.extend([px, py])
        back_pts.extend([body_w, self.height])
        self.canvas.create_polygon(back_pts, fill=palette["fluid_back"], outline="", smooth=True)

        # 2. Front wave layer (primary fluid mass)
        front_pts = [0, self.height]
        for i, h in enumerate(waves):
            px = (i / max(1, n - 1)) * body_w
            py = max(10.0, min(self.height - 2.0, base_y + h + (tilt * ((i - n / 2) * 0.45))))
            front_pts.extend([px, py])
        front_pts.extend([body_w, self.height])
        self.canvas.create_polygon(front_pts, fill=palette["fluid_front"], outline="", smooth=True)

        # 3. Specular liquid meniscus crest line (smoothed wave crest)
        line_pts = front_pts[2:-2]
        if len(line_pts) >= 4:
            self.canvas.create_line(line_pts, fill=active["accent_hex"], width=2.4, smooth=True)

        # 4. Dynamic splash droplet particles
        for p in self.particles:
            r = max(1.0, p.size * p.life)
            self.canvas.create_oval(
                p.x - r,
                p.y - r,
                p.x + r,
                p.y + r,
                fill=p.color,
                outline="",
            )

        # 5. Header Line (y: 19): Accent Dot + Active Harness / Tier Title + Boundary State
        self.canvas.create_oval(14, 15, 23, 24, fill=active["accent_hex"], outline="")
        active_subs = self.settings.get("active_subscriptions", ["claude_code", "antigravity", "openai_codex"])
        custom_name = self.settings.get("custom_tier_name", "")
        sub_tier = SUBSCRIPTION_TIERS.get(len(active_subs), {"name": "Trinity", "tagline": "The sacred three-way triangle"})
        tier_label = custom_name.strip() if custom_name.strip() else sub_tier["name"]

        if self.mode == "all" or active.get("id") == "all":
            header_title = f"3-Harness {tier_label} Mesh"
        else:
            header_title = f"{active['name']} · {tier_label}"

        self.canvas.create_text(
            30,
            19,
            anchor="w",
            text=header_title[:32],
            fill=palette["header"],
            font=(self.font_display, 9, "bold"),
        )

        # Boundary status pill (Pinned · Pin / Drifting · Bounce / Wrapping · Pac-Man)
        if self.boundary_mode == "pin":
            status_text = "Pinned · Pin"
            status_color = "#30D158"
        elif self.boundary_mode == "pacman":
            status_text = "Wrapping · Pac-Man"
            status_color = "#0A84FF"
        else:
            status_text = "Drifting · Bounce"
            status_color = "#FF9F0A"

        self.canvas.create_text(
            body_w - 14,
            19,
            anchor="e",
            text=status_text,
            fill=palette["secondary_text"],
            font=(self.font_display, 8),
        )

        # 6. Hero Metric Line (y: 49): Large % Cache + Tabular Figures
        self.canvas.create_text(
            14,
            49,
            anchor="w",
            text=f"{active['cache_hit_pct']}% Cache",
            fill=palette["primary_text"],
            font=(self.font_display, 13, "bold"),
        )

        # 3-Lens Dynamic Accounting Figures
        lens = self.settings.get("accounting_lens", "specular")
        pts_val = active.get("leverage_index", 26776)
        pts_str = f"{pts_val:,} pts" if isinstance(pts_val, (int, float)) and pts_val > 100 else "26,776 pts"

        if lens == "secular":
            sec_cost = active.get("secular_cost_usd", 20.00)
            cost_str = f"${sec_cost:,.2f}/mo"
        elif lens == "spectacular":
            spec_val = active.get("spectacular_usd", 12875)
            cost_str = f"${spec_val:,.0f} worth"
        else: # specular API standard
            cost_str = f"${active['cost_usd']:,.2f}"

        hero_stats = f"{active['tokens_formatted']} · {cost_str} · {pts_str}"
        self.canvas.create_text(
            body_w - 14,
            49,
            anchor="e",
            text=hero_stats,
            fill=palette["secondary_text"],
            font=(self.font_mono, 8),
        )

        # 7. Subtitle / Spatial Context Line (y: 75)
        self.canvas.create_text(
            14,
            75,
            anchor="w",
            text=f"Over: {frame['target_label'][:24]}",
            fill=palette["secondary_text"],
            font=(self.font_display, 8),
        )
        self.canvas.create_text(
            body_w - 14,
            75,
            anchor="e",
            text=f"Saved ${active['saved_usd']:,}",
            fill=palette["primary_text"],
            font=(self.font_mono, 8, "bold"),
        )

        # 8. Subtle Glowing Hairline Separator (y: 96)
        self.canvas.create_line(14, 96, body_w - 14, 96, fill=palette["divider"], width=1)
        self.canvas.create_line(14, 97, body_w - 14, 97, fill=palette["divider_glow"], width=1)

        # 9. Comparative Drawer Rows (when mode == "all", y: 114 to 174)
        if frame["show_all_drawer"]:
            top_harnesses = [
                ("claude_code", "Claude Code"),
                ("antigravity", "Antigravity"),
                ("openai_codex", "OpenAI Codex"),
            ]
            y_base = 114
            for idx, (hkey, hname) in enumerate(top_harnesses):
                hinfo = frame["harnesses"].get(hkey, active)
                cur_y = y_base + (idx * 24)

                # Accent Dot
                self.canvas.create_oval(14, cur_y - 4, 20, cur_y + 2, fill=hinfo["accent_hex"], outline="")

                # Name
                self.canvas.create_text(
                    28,
                    cur_y,
                    anchor="w",
                    text=hname,
                    fill=palette["primary_text"],
                    font=(self.font_display, 8, "bold"),
                )

                # 3-Lens Cost per harness
                if lens == "secular":
                    h_cost = f"${hinfo.get('secular_cost_usd', 20.0):,.2f}/mo"
                elif lens == "spectacular":
                    h_cost = f"${hinfo.get('spectacular_usd', 4200):,.0f}"
                else:
                    h_cost = f"${hinfo['cost_usd']:,.2f}"

                h_stats = f"{hinfo['tokens_formatted']} · {h_cost} · {hinfo['cache_hit_pct']}%"
                self.canvas.create_text(
                    body_w - 14,
                    cur_y,
                    anchor="e",
                    text=h_stats,
                    fill=palette["secondary_text"],
                    font=(self.font_mono, 8),
                )

        # 10. Right-Edge 2-Button Control Column
        self.canvas.create_line(body_w, 0, body_w, self.height, fill=palette["divider"], width=1)
        btn_x1 = body_w + 6
        btn_x2 = self.width - 6
        mid_y = self.height // 2

        # Button 1 (Top): Harness Mode Switcher (≋ ALL 3 / AUTO)
        b1_fill = palette["button_hover"] if self._hover_btn == "btn_mode" else palette["button_bg"]
        self.canvas.create_rectangle(btn_x1, 6, btn_x2, mid_y - 3, fill=b1_fill, outline=palette["button_border"])
        self.canvas.create_text(
            body_w + 26,
            mid_y // 2 - 5,
            text="≋",
            fill=palette["header"],
            font=(self.font_display, 11, "bold"),
        )
        mode_abbr = "ALL 3" if self.mode == "all" else self.mode[:4].upper()
        self.canvas.create_text(
            body_w + 26,
            mid_y // 2 + 9,
            text=mode_abbr,
            fill=palette["secondary_text"],
            font=(self.font_display, 7, "bold"),
        )

        # Button 2 (Bottom): Boundary Physics Mode (`PIN` / `BNC` / `PAC`)
        b2_fill = palette["button_hover"] if self._hover_btn == "btn_physics" else palette["button_bg"]
        self.canvas.create_rectangle(btn_x1, mid_y + 3, btn_x2, self.height - 6, fill=b2_fill, outline=palette["button_border"])
        b_tag = BOUNDARY_SHORT.get(self.boundary_mode, "BNC")
        b_color = "#30D158" if self.boundary_mode == "pin" else ("#FF9F0A" if self.boundary_mode == "bounce" else "#0A84FF")
        self.canvas.create_text(
            body_w + 26,
            mid_y + (self.height - mid_y) // 2,
            text=b_tag,
            fill=b_color,
            font=(self.font_display, 8, "bold"),
        )


if __name__ == "__main__":
    app = AetherLiquidDesktopOverlay()
    app.root.mainloop()
