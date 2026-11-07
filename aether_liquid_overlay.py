#!/usr/bin/env python3
"""
Aether Pulse — Native Desktop & Terminal Floating Liquid-Physics Overlay (`aether_liquid_overlay.py`)
======================================================================================================
Authored by Eloquent (@mjeanhudson-dev)

A frameless, topmost Cupertino-styled desktop HUD that floats over any AI terminal or IDE
(Claude Code, Google Antigravity, OpenAI Codex CLI, Windows Terminal, Chrome):
  1. Weighty Liquid-Filled Drag Physics: Uses `aether_pulse_ws.step_liquid_physics` (2nd-order
     spring-mass-damper + 1D shallow-water slosh wave) so dragging feels physical and fluid.
  2. Real-Time Spatial Harness Detection: Calls `probe_window_at_point` on the window underneath
     the overlay while dragging and dynamically updates the live telemetry readout.
  3. 1-Button Side Mode Switcher: Clicking the right-edge `[ ≋ ]` button cycles through
     `Auto-Sense Target` -> `All 3 Harnesses Drawer` -> `Claude Code` -> `Antigravity` -> `Codex CLI`.
"""

from __future__ import annotations

import sys
import time
import tkinter as tk
from typing import Any, Dict

import aether_pulse
import aether_pulse_ws


class AetherLiquidDesktopOverlay:
    def __init__(self) -> None:
        self.report = aether_pulse.scan_local_harnesses()
        self.mode = "auto"
        self.detected_harness = "all"
        self.target_label = "Desktop Workspace"

        self.root = tk.Tk()
        self.root.title("Aether Pulse Liquid HUD")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.95)
        self.root.configure(bg="#141416")

        self.width = 390
        self.height = 104
        self.target_x = 120.0
        self.target_y = 120.0
        self.phys = aether_pulse_ws.create_liquid_physics_state(
            x=self.target_x,
            y=self.target_y,
            num_nodes=11,
        )
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

        self.canvas.bind("<ButtonPress-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)

        self._tick()

    def _on_press(self, event: tk.Event) -> None:
        # Check if click landed on the right-side 1-Button Mode Switcher (x >= width - 46)
        if event.x >= self.width - 46:
            self.mode = aether_pulse_ws.next_overlay_mode(self.mode)
            # Excite a tactile liquid ripple on button click
            self.phys["wave_velocities"][len(self.phys["wave_velocities"]) // 2] += 42.0
            self._update_height_for_mode()
            return
        self._is_dragging = True
        self._drag_offset_x = event.x
        self._drag_offset_y = event.y

    def _on_drag(self, event: tk.Event) -> None:
        if not self._is_dragging:
            return
        self.target_x = float(self.root.winfo_pointerx() - self._drag_offset_x)
        self.target_y = float(self.root.winfo_pointery() - self._drag_offset_y)

        # Probe the OS window underneath the center of the overlay
        probe_x = int(self.phys["x"] + self.width // 2)
        probe_y = int(self.phys["y"] + self.height + 12)
        probed = aether_pulse_ws.probe_window_at_point(probe_x, probe_y, ignore_hwnd=self.root.winfo_id())
        self.detected_harness = probed["detected_harness"]
        if probed["window_title"]:
            self.target_label = probed["window_title"][:34]

    def _on_release(self, _event: tk.Event) -> None:
        self._is_dragging = False

    def _update_height_for_mode(self) -> None:
        self.height = 178 if self.mode == "all" else 104
        self.canvas.config(height=self.height)

    def _tick(self) -> None:
        now = time.perf_counter()
        dt = now - self._last_t
        self._last_t = now

        aether_pulse_ws.step_liquid_physics(self.phys, self.target_x, self.target_y, dt)
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
        )
        active = frame["active"]
        fill_ratio = float(active["liquid_fill_ratio"])

        self.canvas.delete("all")

        # Draw sloshing liquid horizon fill at bottom of vessel
        base_y = self.height - (self.height * 0.42 * fill_ratio)
        pts = [0, self.height]
        waves = self.phys["wave_heights"]
        n = len(waves)
        for i, h in enumerate(waves):
            px = (i / max(1, n - 1)) * (self.width - 46)
            py = max(12.0, min(self.height - 4.0, base_y + h + (self.phys["tilt_deg"] * ((i - n / 2) * 0.45))))
            pts.extend([px, py])
        pts.extend([self.width - 46, self.height])
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
            text=f"{active['tokens_formatted']} tok   {active['cache_hit_pct']}% Cache   {active['leverage_index']:,} pts",
            fill="#FFFFFF",
            font=("Consolas", 12, "bold"),
        )
        self.canvas.create_text(
            14,
            76,
            anchor="w",
            text=f"Target: {frame['target_label']}  ·  Saved ${active['saved_usd']:,}",
            fill="#A1A1A6",
            font=("Segoe UI", 8),
        )

        # If "All 3 Harnesses" drawer is open, render comparative rows
        if frame["show_all_drawer"]:
            y_off = 104
            for hkey in ("claude_code", "antigravity", "openai_codex"):
                hinfo = frame["harnesses"][hkey]
                self.canvas.create_text(
                    16,
                    y_off,
                    anchor="w",
                    text=f"{hinfo['short_name']:<12} {hinfo['tokens_formatted']:>7}  ·  {hinfo['cache_hit_pct']}% Hit  ·  {hinfo['sessions']} sess",
                    fill="#E5E5EA",
                    font=("Consolas", 9),
                )
                y_off += 22

        # Right-Edge 1-Button Mode Switcher
        self.canvas.create_line(self.width - 46, 0, self.width - 46, self.height, fill="#2C2C2E", width=1)
        self.canvas.create_rectangle(
            self.width - 38,
            12,
            self.width - 8,
            self.height - 12,
            fill="#1C1C1E",
            outline="#3A3A3C",
        )
        self.canvas.create_text(
            self.width - 23,
            self.height // 2 - 8,
            text="≋",
            fill="#F5F5F7",
            font=("Segoe UI", 13, "bold"),
        )
        self.canvas.create_text(
            self.width - 23,
            self.height // 2 + 12,
            text=self.mode[:4].upper(),
            fill="#98989F",
            font=("Consolas", 7, "bold"),
        )

    def run(self) -> None:
        self.root.mainloop()


if __name__ == "__main__":
    if "--smoke-test" in sys.argv:
        phys = aether_pulse_ws.create_liquid_physics_state(100, 100)
        aether_pulse_ws.step_liquid_physics(phys, 240, 160, 0.016)
        print("Desktop Liquid Overlay physics smoke test OK:", phys["x"], phys["y"], phys["tilt_deg"])
    else:
        AetherLiquidDesktopOverlay().run()
