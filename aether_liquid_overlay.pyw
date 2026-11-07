#!/usr/bin/env python3
"""
Aether Pulse — Native Desktop & Terminal Floating Liquid-Physics Overlay (`aether_liquid_overlay.py`)
======================================================================================================
Authored by Eloquent (@mjeanhudson-dev)

A frameless, topmost Cupertino-styled desktop HUD that floats over any AI terminal or IDE
(Claude Code, Google Antigravity, OpenAI Codex CLI, T3 Code, Windows Terminal, Chrome):
  1. Weighty Liquid-Filled Drag + Freefloat Drift/Wiggle Physics:
     Uses `aether_pulse_ws.step_liquid_physics` (2nd-order spring-mass-damper + 1D shallow-water
     slosh wave + post-release freefloat buoyancy wiggle).
  2. Switchable Boundary Physics (`Bounce` / `Pac-Man Wrap` / `Pin`):
     - `bounce`: Bounces elastically off monitor walls (bottom/top/left/right) with a liquid splash.
     - `pacman`: Flies through bottom->top and left<->right screen edges like Pac-Man.
     - `pin`: Anchors at the release point with subtle buoyancy.
  3. Continuous Spatial Harness Sensing (Drag + Freefloat):
     Probes `probe_window_at_point` beneath the HUD while dragging AND while drifting/bouncing across
     your desktop, dynamically updating displayed telemetry for whichever harness is underneath.
  4. Dual Side Control Buttons:
     - Top right button `[ ≋ AUTO ]`: Cycles `Auto-Sense` -> `All 3 Harnesses` -> `Claude` -> `Antigravity` -> `Codex`.
     - Bottom right button `[ BNC ]`: Cycles `Bounce Walls` -> `Pac-Man Wrap` -> `Pin Anchor`.
"""

from __future__ import annotations

import sys
import time
import tkinter as tk

import aether_pulse
import aether_pulse_ws

BOUNDARY_SHORT = {
    "bounce": "BNC",
    "pacman": "PAC",
    "pin": "PIN",
}


class AetherLiquidDesktopOverlay:
    def __init__(self) -> None:
        self.report = aether_pulse.scan_local_harnesses()
        self.mode = "auto"
        self.boundary_mode = "bounce"
        self.detected_harness = "all"
        self.target_label = "Desktop Workspace"

        self.root = tk.Tk()
        self.root.title("Aether Pulse Liquid HUD")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.95)
        self.root.configure(bg="#141416")

        self.screen_w = float(max(800, self.root.winfo_screenwidth()))
        self.screen_h = float(max(600, self.root.winfo_screenheight()))

        self.width = 408
        self.height = 110
        self.target_x = 140.0
        self.target_y = 140.0
        self.phys = aether_pulse_ws.create_liquid_physics_state(
            x=self.target_x,
            y=self.target_y,
            num_nodes=11,
            boundary_mode=self.boundary_mode,
            width=float(self.width),
            height=float(self.height),
        )
        # Seed gentle initial freefloat drift so the vessel feels alive immediately
        self.phys["vx"] = 58.0
        self.phys["vy"] = 34.0
        self.root.geometry(f"{self.width}x{self.height}+{int(self.target_x)}+{int(self.target_y)}")

        self.canvas = tk.Canvas(
            self.root,
            width=self.width,
            height=self.height,
            bg="#141416",
            highlightthickness=1,
            highlightbackground="#2C2C2E",
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

        self._tick()

    def _on_press(self, event: tk.Event) -> None:
        # Check if click landed on the right-side control column (x >= width - 52)
        if event.x >= self.width - 52:
            if event.y < self.height // 2:
                self.mode = aether_pulse_ws.next_overlay_mode(self.mode)
                self.phys["wave_velocities"][len(self.phys["wave_velocities"]) // 2] += 44.0
                self._update_height_for_mode()
            else:
                self.boundary_mode = aether_pulse_ws.next_boundary_mode(self.boundary_mode)
                self.phys["boundary_mode"] = self.boundary_mode
                self.phys["wave_velocities"][len(self.phys["wave_velocities"]) // 2] += 36.0
                if self.boundary_mode in ("bounce", "pacman") and abs(self.phys["vx"]) < 25.0:
                    self.phys["vx"] = 68.0
                    self.phys["vy"] = -42.0
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
        # Preserve throw momentum on release so it drifts/wiggles and bounces or Pac-Man wraps
        self.phys["vx"] = max(-820.0, min(820.0, self._throw_vx * 0.55 + (52.0 if abs(self._throw_vx) < 20.0 else 0.0)))
        self.phys["vy"] = max(-820.0, min(820.0, self._throw_vy * 0.55 + (-36.0 if abs(self._throw_vy) < 20.0 else 0.0)))
        self.target_x = float(self.phys["x"])
        self.target_y = float(self.phys["y"])

    def _probe_underneath(self, now: float, force: bool = False) -> None:
        if not force and (now - self._last_probe_t) < 0.14:
            return
        self._last_probe_t = now
        probe_x = int(self.phys["x"] + self.width // 2)
        probe_y = int(self.phys["y"] + self.height + 10)
        probed = aether_pulse_ws.probe_window_at_point(probe_x, probe_y, ignore_hwnd=self.root.winfo_id())
        self.detected_harness = probed["detected_harness"]
        if probed["window_title"]:
            self.target_label = probed["window_title"][:32]
        elif probed.get("process_name"):
            self.target_label = probed["process_name"][:32]

    def _update_height_for_mode(self) -> None:
        self.height = 182 if self.mode == "all" else 110
        self.phys["height"] = float(self.height)
        self.canvas.config(height=self.height)

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

        self.canvas.delete("all")

        # Draw sloshing liquid horizon fill at bottom of vessel
        body_w = self.width - 52
        base_y = self.height - (self.height * 0.42 * fill_ratio)
        pts = [0, self.height]
        waves = self.phys["wave_heights"]
        n = len(waves)
        for i, h in enumerate(waves):
            px = (i / max(1, n - 1)) * body_w
            py = max(12.0, min(self.height - 4.0, base_y + h + (self.phys["tilt_deg"] * ((i - n / 2) * 0.45))))
            pts.extend([px, py])
        pts.extend([body_w, self.height])
        self.canvas.create_polygon(pts, fill="#112233", outline="")

        # Specular liquid meniscus line
        line_pts = pts[2:-2]
        if len(line_pts) >= 4:
            self.canvas.create_line(line_pts, fill=active["accent_hex"], width=2, smooth=True)

        # Header & live harness telemetry
        self.canvas.create_oval(14, 15, 22, 23, fill=active["accent_hex"], outline="")
        self.canvas.create_text(
            28,
            19,
            anchor="w",
            text=f"{active['name']}  ·  {frame['overlay_mode_label']}",
            fill="#F5F5F7",
            font=("Segoe UI Semibold", 9),
        )
        self.canvas.create_text(
            14,
            48,
            anchor="w",
            text=f"{active['tokens_formatted']} tok   ${active['cost_usd']:,.2f}   {active['cache_hit_pct']}% Hit",
            fill="#FFFFFF",
            font=("Consolas", 11, "bold"),
        )
        self.canvas.create_text(
            14,
            78,
            anchor="w",
            text=f"Over: {frame['target_label']}  ·  {frame['boundary_mode_label']}  ·  Saved ${active['saved_usd']:,}",
            fill="#A1A1A6",
            font=("Segoe UI", 8),
        )

        # If "All 3 Harnesses" drawer is open, render comparative rows
        if frame["show_all_drawer"]:
            y_off = 108
            for hkey in ("claude_code", "antigravity", "openai_codex"):
                hinfo = frame["harnesses"][hkey]
                self.canvas.create_oval(16, y_off - 4, 22, y_off + 2, fill=hinfo["accent_hex"], outline="")
                self.canvas.create_text(
                    28,
                    y_off,
                    anchor="w",
                    text=f"{hinfo['short_name']:<12} {hinfo['tokens_formatted']:>7}  ·  ${hinfo['cost_usd']:>6.2f}  ·  {hinfo['cache_hit_pct']}% Hit",
                    fill="#E5E5EA",
                    font=("Consolas", 8),
                )
                y_off += 22

        # Right-Edge Dual Control Column (Top = Harness Mode, Bottom = Bounce / Pac-Man / Pin Physics)
        self.canvas.create_line(body_w, 0, body_w, self.height, fill="#2C2C2E", width=1)
        mid_y = self.height // 2

        # Top button: Harness Mode Switcher
        self.canvas.create_rectangle(
            body_w + 6,
            8,
            self.width - 6,
            mid_y - 3,
            fill="#1C1C1E",
            outline="#3A3A3C",
        )
        self.canvas.create_text(
            body_w + 26,
            mid_y // 2 - 4,
            text="≋",
            fill="#F5F5F7",
            font=("Segoe UI", 11, "bold"),
        )
        self.canvas.create_text(
            body_w + 26,
            mid_y // 2 + 10,
            text=self.mode[:4].upper(),
            fill="#98989F",
            font=("Consolas", 7, "bold"),
        )

        # Bottom button: Boundary Physics Mode (`BNC` / `PAC` / `PIN`)
        self.canvas.create_rectangle(
            body_w + 6,
            mid_y + 3,
            self.width - 6,
            self.height - 8,
            fill="#1C1C1E",
            outline="#3A3A3C",
        )
        b_tag = BOUNDARY_SHORT.get(self.boundary_mode, "BNC")
        b_color = "#30D158" if self.boundary_mode == "bounce" else ("#FF9F0A" if self.boundary_mode == "pacman" else "#98989F")
        self.canvas.create_text(
            body_w + 26,
            mid_y + (self.height - mid_y) // 2,
            text=b_tag,
            fill=b_color,
            font=("Consolas", 8, "bold"),
        )

    def run(self) -> None:
        self.root.mainloop()


if __name__ == "__main__":
    if "--smoke-test" in sys.argv:
        phys = aether_pulse_ws.create_liquid_physics_state(100, 100, boundary_mode="bounce")
        phys["vx"] = 420.0
        phys["vy"] = -260.0
        for _ in range(30):
            aether_pulse_ws.step_liquid_physics(phys, 240, 160, 0.016, is_dragging=False, bounds_w=500.0, bounds_h=300.0)
        print(
            "Desktop Liquid Overlay physics smoke test OK:",
            phys["x"],
            phys["y"],
            phys["tilt_deg"],
            "bounces=",
            phys["wall_bounces"],
        )
    else:
        AetherLiquidDesktopOverlay().run()
