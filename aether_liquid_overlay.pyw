#!/usr/bin/env python3
"""
Aether Pulse — Native Desktop & Terminal Floating Liquid-Physics Overlay (`aether_liquid_overlay.py`)
======================================================================================================
Authored by Eloquent (@mjeanhudson-dev)

A frameless, topmost Cupertino-styled desktop HUD that floats over any AI terminal, browser, or IDE
(Claude Code, Google Antigravity, OpenAI Codex CLI, Cursor, Aider, Windsurf, Continue.dev,
GitHub Copilot, OpenHands, T3 Code, Windows Terminal, Chrome):
  1. Ultra-Low Wiggle & Rock-Solid Pinned Stability:
     - Near-zero / 0.0 wiggle when in 'PIN' anchor mode.
     - Subdued, organic micro-currents when in freefloat 'BNC' or 'PAC' modes.
  2. Window Controls (`✕` Close, `—` Minimize, `⚙` Settings Cog):
     - Sleek Cupertino traffic/pill control cluster in top-right header.
     - Minimize hides to system tray; Close exits or docks to tray based on operator setting.
  3. Native Windows System Tray Integration:
     - Real-time tray icon with right-click context menu (Show, Minimize, Settings, Modes, Exit).
     - Single-click tray icon toggles Show / Minimize.
  4. Cupertino Settings Modal Dialog:
     - Accessible via `⚙` cog button or tray menu.
     - Live toggles for: Boundary Modes (Bounce/Pac-Man/Pin), Theme (Dark/Light), Opacity,
       High-Speed Viscous Braking, Wall Splash Particles, Auto-Sense Sensing, and Close Action.
  5. 48-Node Coupled Shallow-Water Liquid Physics + Wall Splashes:
     - Viscous fluid dynamics with wave crests and gravity-affected droplet particles.
  6. Top 10 Ecosystem Harness Detection:
     - Seamless foreground detection across Claude, Antigravity, Codex, Cursor, Aider,
       Windsurf, Continue, Copilot, OpenHands, and T3 Code.
"""

from __future__ import annotations

import ctypes
import json
import math
import os
import random
import sys
import threading
import time
import tkinter as tk
import tkinter.font as tkfont
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import aether_pulse
import aether_pulse_ws

try:
    import pystray
    from PIL import Image
    HAS_TRAY = True
except Exception:
    HAS_TRAY = False

SETTINGS_FILE = "aether_pulse_settings.json"

DEFAULT_SETTINGS = {
    "theme": "dark",
    "boundary_mode": "bounce",
    "overlay_mode": "auto",
    "alpha": 0.96,
    "topmost": True,
    "enable_particles": True,
    "enable_viscous_braking": True,
    "close_to_tray": True,
    "wiggle_intensity": "subdued",  # "none", "subdued", "active"
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
        "button_border": "#3A3A3C",
        "button_hover": "#2C2C2E",
        "close_hover": "#FF453A",
        "divider": "#2C2C2E",
        "fluid_back": "#0D1826",
        "fluid_front": "#13273D",
        "crest_glow": "#388BFF",
        "particle_color": "#E5E5EA",
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
        "button_border": "#D1D1D6",
        "button_hover": "#E5E5EA",
        "close_hover": "#FF3B30",
        "divider": "#E5E5EA",
        "fluid_back": "#DCEAF7",
        "fluid_front": "#C8E1FA",
        "crest_glow": "#0066CC",
        "particle_color": "#0066CC",
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
        self.life -= dt * 2.2
        return self.life > 0.0


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
        self.root.attributes("-topmost", bool(self.settings.get("topmost", True)))
        self.root.attributes("-alpha", float(self.settings.get("alpha", 0.96)))

        # Load native Windows icon
        self.ico_path = os.path.abspath("aether_pulse.ico")
        if os.path.exists(self.ico_path):
            try:
                self.root.iconbitmap(self.ico_path)
            except Exception:
                pass

        palette = THEME_PALETTES[self.theme]
        self.root.configure(bg=palette["bg"])

        self.screen_w = float(max(800, self.root.winfo_screenwidth()))
        self.screen_h = float(max(600, self.root.winfo_screenheight()))

        self.width = 442
        self.height = 116
        self.target_x = 140.0
        self.target_y = 140.0
        self.corner_radius = 24

        self.phys = aether_pulse_ws.create_liquid_physics_state(
            x=self.target_x,
            y=self.target_y,
            num_nodes=48,
            boundary_mode=self.boundary_mode,
            width=float(self.width),
            height=float(self.height),
        )
        # Gentle initial velocity
        if self.boundary_mode != "pin":
            self.phys["vx"] = 32.0
            self.phys["vy"] = 18.0
        self.root.geometry(f"{self.width}x{self.height}+{int(self.target_x)}+{int(self.target_y)}")

        self._init_fonts()

        self.canvas = tk.Canvas(
            self.root,
            width=self.width,
            height=self.height,
            bg=palette["bg"],
            highlightthickness=1,
            highlightbackground=palette["border"],
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

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

        self.canvas.bind("<ButtonPress-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)
        self.canvas.bind("<Motion>", self._on_mouse_move)
        self.canvas.bind("<Leave>", self._on_mouse_leave)

        # Apply native Windows 11 rounded window region
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
                    saved = json.load(f)
                    settings.update(saved)
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
                pystray.MenuItem("⚙ Settings...", lambda: self.root.after(0, self.open_settings_dialog)),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Mode: Auto-Sense", lambda: self._tray_set_mode("auto"), checked=lambda item: self.mode == "auto"),
                pystray.MenuItem("Mode: All 10 Harnesses", lambda: self._tray_set_mode("all"), checked=lambda item: self.mode == "all"),
                pystray.MenuItem("Theme: Dark / Light", lambda: self.root.after(0, self._toggle_theme)),
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
            self._save_settings()
        self.root.after(0, _apply)

    def _minimize_to_tray(self) -> None:
        self.root.withdraw()
        if self.tray_icon:
            try:
                self.tray_icon.notify("Aether Pulse minimized to system tray. Click icon to restore.", "Aether Pulse HUD")
            except Exception:
                pass

    def _restore_from_tray(self) -> None:
        self.root.deiconify()
        self.root.attributes("-topmost", bool(self.settings.get("topmost", True)))
        self.root.update_idletasks()
        self._apply_rounded_window_region()

    def _exit_application(self) -> None:
        if self.tray_icon:
            try:
                self.tray_icon.stop()
            except Exception:
                pass
        self.root.quit()
        self.root.destroy()
        sys.exit(0)

    def _toggle_theme(self) -> None:
        self.theme = "light" if self.theme == "dark" else "dark"
        self.settings["theme"] = self.theme
        self._save_settings()
        palette = THEME_PALETTES[self.theme]
        self.root.configure(bg=palette["bg"])
        self.canvas.configure(bg=palette["bg"], highlightbackground=palette["border"])

    def _on_mouse_move(self, event: tk.Event) -> None:
        body_w = self.width - 56
        old_hover = self._hover_control
        self._hover_control = None

        # Check top-right window controls (y: 6..28)
        if 6 <= event.y <= 28:
            if body_w - 78 <= event.x < body_w - 52:
                self._hover_control = "settings"
            elif body_w - 50 <= event.x < body_w - 26:
                self._hover_control = "minimize"
            elif body_w - 24 <= event.x < body_w - 2:
                self._hover_control = "close"

        if old_hover != self._hover_control:
            self._render()

    def _on_mouse_leave(self, _event: tk.Event) -> None:
        if self._hover_control is not None:
            self._hover_control = None
            self._render()

    def _on_press(self, event: tk.Event) -> None:
        col_w = 56
        btn_x_start = self.width - col_w
        body_w = btn_x_start

        # Check top window control buttons
        if 6 <= event.y <= 28:
            if body_w - 78 <= event.x < body_w - 52:
                self.open_settings_dialog()
                return
            elif body_w - 50 <= event.x < body_w - 26:
                self._minimize_to_tray()
                return
            elif body_w - 24 <= event.x < body_w - 2:
                if self.settings.get("close_to_tray", True) and HAS_TRAY:
                    self._minimize_to_tray()
                else:
                    self._exit_application()
                return

        # Check right-side control column
        if event.x >= btn_x_start:
            section_h = self.height / 3.0
            if event.y < section_h:
                # Top Button: Cycle Mode (Auto -> All -> Top 10 Harnesses)
                self.mode = aether_pulse_ws.next_overlay_mode(self.mode)
                self.settings["overlay_mode"] = self.mode
                self._save_settings()
                mid = len(self.phys["wave_velocities"]) // 2
                self.phys["wave_velocities"][mid] += 48.0
                self._update_height_for_mode()
            elif event.y < section_h * 2.0:
                # Middle Button: Toggle Light / Dark Theme
                self._toggle_theme()
                mid = len(self.phys["wave_velocities"]) // 2
                self.phys["wave_velocities"][mid] -= 32.0
            else:
                # Bottom Button: Cycle Boundary Mode (BNC -> PAC -> PIN)
                self.boundary_mode = aether_pulse_ws.next_boundary_mode(self.boundary_mode)
                self.settings["boundary_mode"] = self.boundary_mode
                self.phys["boundary_mode"] = self.boundary_mode
                self._save_settings()
                mid = len(self.phys["wave_velocities"]) // 2
                self.phys["wave_velocities"][mid] += 36.0
                if self.boundary_mode in ("bounce", "pacman") and math.hypot(self.phys["vx"], self.phys["vy"]) < 20.0:
                    self.phys["vx"] = 48.0
                    self.phys["vy"] = -32.0
                elif self.boundary_mode == "pin":
                    self.phys["vx"] = 0.0
                    self.phys["vy"] = 0.0
            return

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

        if self.boundary_mode == "pin":
            # Rock-solid anchor when pinned: zero throw momentum
            self.phys["vx"] = 0.0
            self.phys["vy"] = 0.0
        else:
            throw_spd = math.hypot(self._throw_vx, self._throw_vy)
            scale = 0.55 if throw_spd < 350.0 else 0.42
            self.phys["vx"] = max(-920.0, min(920.0, self._throw_vx * scale + (36.0 if abs(self._throw_vx) < 20.0 else 0.0)))
            self.phys["vy"] = max(-920.0, min(920.0, self._throw_vy * scale + (-24.0 if abs(self._throw_vy) < 20.0 else 0.0)))

        self.target_x = float(self.phys["x"])
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
        self.height = 244 if self.mode == "all" else 116
        self.phys["height"] = float(self.height)
        self.canvas.config(height=self.height)
        self.root.update_idletasks()
        self._apply_rounded_window_region()

    def _spawn_splash_particles(self, side: str, impulse: float, accent_hex: str) -> None:
        if not self.settings.get("enable_particles", True):
            return
        count = min(20, max(6, int(impulse * 0.15)))
        body_w = self.width - 56
        palette = THEME_PALETTES[self.theme]

        for _ in range(count):
            if side == "left":
                px = random.uniform(2.0, 18.0)
                py = random.uniform(self.height * 0.35, self.height * 0.85)
                vx = random.uniform(25.0, 140.0)
                vy = random.uniform(-220.0, -50.0)
            elif side == "right":
                px = random.uniform(body_w - 18.0, body_w - 2.0)
                py = random.uniform(self.height * 0.35, self.height * 0.85)
                vx = random.uniform(-140.0, -25.0)
                vy = random.uniform(-220.0, -50.0)
            else:
                px = random.uniform(10.0, body_w - 10.0)
                py = random.uniform(self.height * 0.6, self.height - 6.0)
                vx = random.uniform(-70.0, 70.0)
                vy = random.uniform(-180.0, -35.0)

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
        base_y = self.height - (self.height * 0.44 * fill_ratio)
        waves = self.phys["wave_heights"]
        n = len(waves)
        tilt = float(self.phys["tilt_deg"])

        # 1. Back wave layer (parallax depth)
        back_pts = [0, self.height]
        for i, h in enumerate(waves):
            px = (i / max(1, n - 1)) * body_w
            back_h = h * 0.7 + math.sin(float(self.phys["phase"]) * 2.8 + i * 0.28) * 1.8
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

        # 3. Specular liquid meniscus crest line
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

        # 5. Header: Micro-caps uppercase category & harness name
        self.canvas.create_oval(14, 15, 23, 24, fill=active["accent_hex"], outline="")
        badge_text = f"{active['name'].upper()}  ·  {active.get('model_badge', 'AI Coding Engine')}"
        self.canvas.create_text(
            30,
            19,
            anchor="w",
            text=badge_text[:40],
            fill=palette["header"],
            font=(self.font_display, 8, "bold"),
        )

        # 6. Top Window Control Buttons (`⚙`, `—`, `✕`) in header before side column
        # Settings Cog
        cog_bg = palette["button_hover"] if self._hover_control == "settings" else palette["button_bg"]
        self.canvas.create_rectangle(body_w - 78, 8, body_w - 54, 28, fill=cog_bg, outline=palette["button_border"])
        self.canvas.create_text(body_w - 66, 18, text="⚙", fill=palette["primary_text"], font=(self.font_display, 8))

        # Minimize Button
        min_bg = palette["button_hover"] if self._hover_control == "minimize" else palette["button_bg"]
        self.canvas.create_rectangle(body_w - 50, 8, body_w - 26, 28, fill=min_bg, outline=palette["button_border"])
        self.canvas.create_text(body_w - 38, 17, text="—", fill=palette["primary_text"], font=(self.font_display, 9, "bold"))

        # Close Button
        close_bg = palette["close_hover"] if self._hover_control == "close" else palette["button_bg"]
        close_fg = "#FFFFFF" if self._hover_control == "close" else palette["primary_text"]
        self.canvas.create_rectangle(body_w - 22, 8, body_w + 2, 28, fill=close_bg, outline=palette["button_border"])
        self.canvas.create_text(body_w - 10, 18, text="✕", fill=close_fg, font=(self.font_display, 8, "bold"))

        # 7. Primary Metric: Tabular Figures
        metric_str = f"{active['tokens_formatted']} TOK    ${active['cost_usd']:,.2f}    {active['cache_hit_pct']}% HIT"
        self.canvas.create_text(
            14,
            50,
            anchor="w",
            text=metric_str,
            fill=palette["primary_text"],
            font=(self.font_mono, 11, "bold"),
        )

        # 8. Subtitle / Spatial Context Line
        sub_str = f"OVER: {frame['target_label'][:24]}   {frame['boundary_mode_label'].upper()}   SAVED ${active['saved_usd']:,}"
        self.canvas.create_text(
            14,
            80,
            anchor="w",
            text=sub_str,
            fill=palette["secondary_text"],
            font=(self.font_text, 8),
        )

        # 9. If "All 10 Harnesses" drawer is open, render 2-column comparative grid
        if frame["show_all_drawer"]:
            self.canvas.create_line(14, 98, body_w - 14, 98, fill=palette["divider"], width=1)
            y_base = 114
            top_harness_keys = [
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
            col1 = top_harness_keys[:5]
            col2 = top_harness_keys[5:]

            for row_i, (k1, k2) in enumerate(zip(col1, col2)):
                cur_y = y_base + (row_i * 24)

                # Col 1
                h1 = frame["harnesses"].get(k1, active)
                self.canvas.create_oval(14, cur_y - 4, 20, cur_y + 2, fill=h1["accent_hex"], outline="")
                txt1 = f"{h1['short_name'][:10]:<10} {h1['tokens_formatted']:>6} · {h1['cache_hit_pct']}%"
                self.canvas.create_text(
                    24, cur_y, anchor="w", text=txt1, fill=palette["primary_text"], font=(self.font_mono, 8)
                )

                # Col 2
                h2 = frame["harnesses"].get(k2, active)
                col2_x = 206
                self.canvas.create_oval(col2_x, cur_y - 4, col2_x + 6, cur_y + 2, fill=h2["accent_hex"], outline="")
                txt2 = f"{h2['short_name'][:10]:<10} {h2['tokens_formatted']:>6} · {h2['cache_hit_pct']}%"
                self.canvas.create_text(
                    col2_x + 10, cur_y, anchor="w", text=txt2, fill=palette["primary_text"], font=(self.font_mono, 8)
                )

        # 10. Right-Edge 3-Button Control Column
        self.canvas.create_line(body_w, 0, body_w, self.height, fill=palette["divider"], width=1)
        btn_x = body_w + 6
        btn_w = self.width - 6
        h3 = self.height / 3.0

        # Button 1 (Top): Harness Mode Switcher
        self.canvas.create_rectangle(btn_x, 6, btn_w, int(h3 - 2), fill=palette["button_bg"], outline=palette["button_border"])
        self.canvas.create_text(
            body_w + 28,
            int(h3 * 0.35),
            text="≋",
            fill=palette["header"],
            font=(self.font_display, 10, "bold"),
        )
        mode_abbr = self.mode[:4].upper()
        self.canvas.create_text(
            body_w + 28,
            int(h3 * 0.72),
            text=mode_abbr,
            fill=palette["secondary_text"],
            font=(self.font_mono, 7, "bold"),
        )

        # Button 2 (Middle): Light / Dark Theme Switcher
        self.canvas.create_rectangle(btn_x, int(h3 + 2), btn_w, int(h3 * 2.0 - 2), fill=palette["button_bg"], outline=palette["button_border"])
        theme_icon = "☀️" if self.theme == "light" else "🌙"
        theme_label = "LGT" if self.theme == "light" else "DRK"
        self.canvas.create_text(
            body_w + 28,
            int(h3 * 1.35),
            text=theme_icon,
            fill=palette["header"],
            font=(self.font_display, 9),
        )
        self.canvas.create_text(
            body_w + 28,
            int(h3 * 1.72),
            text=theme_label,
            fill="#FF9F0A" if self.theme == "light" else "#5E5CE6",
            font=(self.font_mono, 7, "bold"),
        )

        # Button 3 (Bottom): Boundary Physics Mode (BNC / PAC / PIN)
        self.canvas.create_rectangle(btn_x, int(h3 * 2.0 + 2), btn_w, self.height - 6, fill=palette["button_bg"], outline=palette["button_border"])
        b_tag = BOUNDARY_SHORT.get(self.boundary_mode, "BNC")
        b_color = "#30D158" if self.boundary_mode == "bounce" else ("#FF9F0A" if self.boundary_mode == "pacman" else palette["subtle_text"])
        self.canvas.create_text(
            body_w + 28,
            int(h3 * 2.5),
            text=b_tag,
            fill=b_color,
            font=(self.font_mono, 8, "bold"),
        )

    def open_settings_dialog(self) -> None:
        if self._settings_window and self._settings_window.winfo_exists():
            self._settings_window.lift()
            return

        sw = tk.Toplevel(self.root)
        self._settings_window = sw
        sw.title("Aether Pulse Settings")
        sw.geometry("420x460")
        sw.resizable(False, False)
        sw.attributes("-topmost", True)

        palette = THEME_PALETTES[self.theme]
        sw.configure(bg=palette["bg"])

        # Title
        tk.Label(
            sw,
            text="⚡ Aether Pulse Settings",
            bg=palette["bg"],
            fg=palette["header"],
            font=(self.font_display, 12, "bold"),
        ).pack(anchor="w", padx=20, pady=(16, 8))

        # Container Frame
        container = tk.Frame(sw, bg=palette["bg"])
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=8)

        # 1. Physics Mode Selector
        tk.Label(container, text="BOUNDARY DYNAMICS:", bg=palette["bg"], fg=palette["secondary_text"], font=(self.font_mono, 8, "bold")).pack(anchor="w", pady=(6, 2))
        bmode_var = tk.StringVar(value=self.boundary_mode)
        bframe = tk.Frame(container, bg=palette["bg"])
        bframe.pack(fill=tk.X, pady=(0, 8))
        for bval, blabel in [("bounce", "Bounce Walls (BNC)"), ("pacman", "Pac-Man Wrap (PAC)"), ("pin", "Pinned Anchor (Zero Wiggle)")]:
            tk.Radiobutton(
                bframe,
                text=blabel,
                variable=bmode_var,
                value=bval,
                bg=palette["bg"],
                fg=palette["primary_text"],
                selectcolor=palette["surface"],
                activebackground=palette["bg"],
                font=(self.font_text, 9),
            ).pack(anchor="w")

        # 2. Appearance & Theme
        tk.Label(container, text="VISUAL PALETTE:", bg=palette["bg"], fg=palette["secondary_text"], font=(self.font_mono, 8, "bold")).pack(anchor="w", pady=(6, 2))
        theme_var = tk.StringVar(value=self.theme)
        tframe = tk.Frame(container, bg=palette["bg"])
        tframe.pack(fill=tk.X, pady=(0, 8))
        for tval, tlabel in [("dark", "Obsidian Dark Palette"), ("light", "Cupertino Light Palette")]:
            tk.Radiobutton(
                tframe,
                text=tlabel,
                variable=theme_var,
                value=tval,
                bg=palette["bg"],
                fg=palette["primary_text"],
                selectcolor=palette["surface"],
                activebackground=palette["bg"],
                font=(self.font_text, 9),
            ).pack(anchor="w")

        # 3. Feature Set Checkboxes
        tk.Label(container, text="FEATURE TOGGLES:", bg=palette["bg"], fg=palette["secondary_text"], font=(self.font_mono, 8, "bold")).pack(anchor="w", pady=(6, 2))
        part_var = tk.BooleanVar(value=bool(self.settings.get("enable_particles", True)))
        brake_var = tk.BooleanVar(value=bool(self.settings.get("enable_viscous_braking", True)))
        top_var = tk.BooleanVar(value=bool(self.settings.get("topmost", True)))
        tray_close_var = tk.BooleanVar(value=bool(self.settings.get("close_to_tray", True)))

        tk.Checkbutton(container, text="Wall Splash Wave & Droplet Particles", variable=part_var, bg=palette["bg"], fg=palette["primary_text"], selectcolor=palette["surface"], font=(self.font_text, 9)).pack(anchor="w")
        tk.Checkbutton(container, text="High-Speed Viscous Eddy Braking (>180 px/s)", variable=brake_var, bg=palette["bg"], fg=palette["primary_text"], selectcolor=palette["surface"], font=(self.font_text, 9)).pack(anchor="w")
        tk.Checkbutton(container, text="Always on Top (Topmost Window)", variable=top_var, bg=palette["bg"], fg=palette["primary_text"], selectcolor=palette["surface"], font=(self.font_text, 9)).pack(anchor="w")
        tk.Checkbutton(container, text="Close Button ('✕') Minimizes to System Tray", variable=tray_close_var, bg=palette["bg"], fg=palette["primary_text"], selectcolor=palette["surface"], font=(self.font_text, 9)).pack(anchor="w")

        # 4. Save & Apply
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
                new_pal = THEME_PALETTES[self.theme]
                self.root.configure(bg=new_pal["bg"])
                self.canvas.configure(bg=new_pal["bg"], highlightbackground=new_pal["border"])

            self.settings["enable_particles"] = part_var.get()
            self.settings["enable_viscous_braking"] = brake_var.get()
            self.settings["topmost"] = top_var.get()
            self.settings["close_to_tray"] = tray_close_var.get()

            self.root.attributes("-topmost", bool(top_var.get()))
            self._save_settings()
            sw.destroy()
            self._render()

        btn_row = tk.Frame(sw, bg=palette["bg"])
        btn_row.pack(fill=tk.X, padx=20, pady=(8, 16))

        tk.Button(
            btn_row,
            text="Save & Apply",
            command=_save_and_apply,
            bg="#0066CC",
            fg="#FFFFFF",
            font=(self.font_text, 9, "bold"),
            relief=tk.FLAT,
            padx=14,
            pady=6,
        ).pack(side=tk.RIGHT)

        tk.Button(
            btn_row,
            text="Cancel",
            command=sw.destroy,
            bg=palette["button_bg"],
            fg=palette["primary_text"],
            font=(self.font_text, 9),
            relief=tk.FLAT,
            padx=12,
            pady=6,
        ).pack(side=tk.RIGHT, padx=8)

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
    else:
        AetherLiquidDesktopOverlay().run()
