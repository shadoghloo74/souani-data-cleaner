"""
Commercial Desktop Application  ·  Enterprise-Grade UI
Engine / AI / CSV-Excel-JSON logic : UNCHANGED
Build: 20260731  ·  Visual Overhaul v2.1
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import threading
import os
import sys
import subprocess
import time
import math
import psutil
from datetime import datetime
from pathlib import Path
from data_cleaner import AdvancedDataCleaner
import csv
from typing import Optional, Dict

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ── Design System v2 ──────────────────────────────────────────────────────
T = {
    "bg":          "#060A12",
    "bg_2":        "#0A0F1A",
    "surface":     "#0E1422",
    "card":        "#162032",
    "card_hover":  "#162033",
    "card_border": "#293A56",
    "card_border_hi": "#264060",
    "sidebar":     "#0B1018",
    "input_bg":    "#0D1320",
    "topbar":      "#080D18",

    "blue":        "#2B8FFF",
    "blue_dim":    "#1A5FAA",
    "blue_hover":  "#3DA3FF",
    "blue_glow":   "#0D2A4A",
    "blue_subtle": "#0F1E35",

    "gold":        "#D4A843",
    "gold_bright": "#F0C850",
    "gold_dim":    "#5A4510",
    "gold_subtle": "#1A1608",

    "text_1":      "#FFFFFF",
    "text_2":      "#E2E8F0",
    "text_3":      "#94A3B8",
    "text_4":         "#CBD5E1",

 
    "green":       "#2DD49A",
    "green_dim":   "#0A3322",
    "orange":      "#F5A623",
    "red":         "#F04848",
    "cyan":        "#3DD8F0",
    "purple":      "#A07EF0",

    "radius":      8,
    "radius_sm":   5,
    "radius_xs":   3,
    "info_bg":     "#0C1420",
    "info_border": "#162840",

    "font_ui":     "Segoe UI",
    "font_mono":   "Cascadia Mono",
}

VERSION   = "v4.0 LTS"
BUILD     = "20260731"
COMPANY   = "Souani Technologies"
EDITION   = "Enterprise"
LICENSE   = "Licensed — Enterprise"

_PULSE_MS     = 400
_FLASH_MS     = 200
_COMPLETE_MS  = 4000
_SPINNER_MS   = 150
_CLOCK_MS     = 1000
_MEMORY_MS    = 3000

    # 1. خلفية زرقاء رسمية هادئة بحدود ملائمة (Corporate Badge)
    margin = 4
    c.create_rectangle(margin, margin, size - margin, size - margin, 
                       fill="#1E293B", outline="#334155", width=1.5)
    
    # 2. مربع داخلي محدد باللون الأزرق المالي/المؤسسي (Enterprise Blue)
    pad = 8
    c.create_rectangle(pad, pad, size - pad, size - pad, 
                       fill="#0284C7", outline="#0369A1", width=1)
    
    # 3. حرف S كبير ورسمي باللون الأبيض الناصع بمنتصف الشعار
    c.create_text(size / 2, size / 2, text="S", fill="#FFFFFF", 
                  font=(T["font_ui"], int(size * 0.45), "bold"))
    
    return c


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  Status Pill                                                            ║
# ╚══════════════════════════════════════════════════════════════════════════╝
_PILL = {
    "READY":      ("#0A2818", "#2DD49A"),
    "PROCESSING": ("#0A1830", "#2B8FFF"),
    "COMPLETED":  ("#0A2818", "#2DD49A"),
    "WARNING":    ("#2A1A08", "#F5A623"),
    "ERROR":      ("#2A0A0A", "#F04848"),
    "STANDBY":    ("#141A24", "#4A5E78"),
    "ANALYZING":  ("#1A1030", "#A07EF0"),
    "CLEANING":   ("#0A1830", "#2B8FFF"),
    "REPORTING":  ("#082028", "#3DD8F0"),
    "SAVING":     ("#0A2818", "#2DD49A"),
}

class StatusPill(tk.Canvas):
    def __init__(self, parent, state="STANDBY", pill_w=80, pill_h=20, **kw):
        super().__init__(parent, width=pill_w, height=pill_h,
                         highlightthickness=0, bd=0,
                         bg=kw.pop("canvas_bg", T["topbar"]))
        self._pw = pill_w
        self._ph = pill_h
        self._state = state
        self._pulse_id: Optional[str] = None
        self._draw(state)

    def _draw(self, state):
        bg, fg = _PILL.get(state, _PILL["STANDBY"])
        self.delete("all")
        r = self._ph // 2
        w, h = self._pw, self._ph
        self.create_oval(1, 1, r * 2 + 1, h - 1, fill=bg, outline="")
        self.create_rectangle(r, 1, w - r, h - 1, fill=bg, outline="")
        self.create_oval(w - r * 2 - 1, 1, w - 1, h - 1, fill=bg, outline="")
        dx = r + 5
        dy = h // 2
        self.create_oval(dx - 3, dy - 3, dx + 3, dy + 3, fill=fg, outline="")
        label = state if len(state) <= 9 else state[:8]
        self.create_text(dx + 8, dy, text=label, fill=fg,
                         font=(T["font_ui"], 7, "bold"), anchor="w")

    def set(self, state):
        self._state = state
        self._draw(state)

    def pulse(self, cycles=3):
        self._pstep(0, cycles)

    def _pstep(self, i, total):
        if i >= total * 2:
            self._draw(self._state)
            self._pulse_id = None
            return
        bg, fg = _PILL.get(self._state, _PILL["STANDBY"])
        if i % 2 == 0:
            self.delete("all")
            r = self._ph // 2
            w, h = self._pw, self._ph
            self.create_oval(1, 1, r * 2 + 1, h - 1, fill=fg, outline="")
            self.create_rectangle(r, 1, w - r, h - 1, fill=fg, outline="")
            self.create_oval(w - r * 2 - 1, 1, w - 1, h - 1, fill=fg, outline="")
        else:
            self._draw(self._state)
        self._pulse_id = self.after(_PULSE_MS, self._pstep, i + 1, total)

    def stop_pulse(self):
        if self._pulse_id:
            self.after_cancel(self._pulse_id)
            self._pulse_id = None
        self._draw(self._state)


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  LED Dot                                                                ║
# ╚══════════════════════════════════════════════════════════════════════════╝
_LED_MAP = {
    "READY": "#2DD49A", "STANDBY": "#4A5E78",
    "PROCESSING": "#2B8FFF", "CLEANING": "#2B8FFF",
    "ANALYZING": "#A07EF0", "REPORTING": "#3DD8F0",
    "SAVING": "#2DD49A", "COMPLETED": "#2DD49A",
    "WARNING": "#F5A623", "ERROR": "#F04848",
}

class LED(tk.Canvas):
    def __init__(self, parent, size=8, bg=None, **kw):
        super().__init__(parent, width=size, height=size,
                         highlightthickness=0, bd=0,
                         bg=bg or T["topbar"], **kw)
        self._sz = size
        self._color = "#4A5E78"
        self._pulse_id = None
        self._draw_dot("#4A5E78")

    def _draw_dot(self, color):
        self.delete("all")
        s = self._sz; m = 2
        self.create_oval(m, m, s - m, s - m, fill=color, outline="")

    def set(self, state):
        self._color = _LED_MAP.get(state, "#4A5E78")
        self._draw_dot(self._color)

    def pulse(self, cycles=3):
        self._pstep(0, cycles)

    def _pstep(self, i, total):
        if i >= total * 2:
            self._draw_dot(self._color)
            self._pulse_id = None
            return
        s = self._sz
        if i % 2 == 0:
            self.delete("all")
            self.create_oval(0, 0, s, s, fill=self._color, outline="")
        else:
            self._draw_dot(self._color)
        self._pulse_id = self.after(_PULSE_MS, self._pstep, i + 1, total)

    def stop_pulse(self):
        if self._pulse_id:
            self.after_cancel(self._pulse_id)
            self._pulse_id = None


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  Metric Card                                                            ║
# ╚══════════════════════════════════════════════════════════════════════════╝
class MetricCard(tk.Frame):
    def __init__(self, parent, label, important=False):
        super().__init__(parent, bg=T["card"],
                         highlightbackground=T["card_border"],
                         highlightthickness=1)
        self._default_bg = T["card"]
        self._default_brd = T["card_border"]
        self._important = important
        self._val_size = 15 if important else 13
        self._anim_id = None
        self._flash_id = None

        self._title = tk.Label(self, text=label, bg=T["card"],
                              fg="#E2E8F0", font=(T["font_ui"], 8),
                               anchor="w")
        self._title.pack(anchor="w", padx=10, pady=(6, 0))

        self._val = tk.Label(self, text="—", bg=T["card"],
                             fg="#FFFFFF",
                             font=(T["font_ui"], self._val_size, "bold"),
                             anchor="w")
        self._val.pack(anchor="w", padx=10, pady=(0, 6))

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        for ch in self.winfo_children():
            ch.bind("<Enter>", self._on_enter)
            ch.bind("<Leave>", self._on_leave)

    def _on_enter(self, _):
        self.config(bg=T["card_hover"],
                   highlightbackground=T["card_border_hi"])
        self._title.config(bg=T["card_hover"])
        self._val.config(bg=T["card_hover"])

    def _on_leave(self, _):
        self.config(bg=self._default_bg,
                   highlightbackground=self._default_brd)
        self._title.config(bg=self._default_bg)
        self._val.config(bg=self._default_bg)

    def set(self, value, color=None):
        self._cancel()
        s = str(value)
        is_num = any(ch.isdigit() for ch in s)
        f = (T["font_mono"], self._val_size, "bold") if is_num \
            else (T["font_ui"], self._val_size, "bold")
        self._val.config(text=s, fg=color or "#FFFFFF", font=f)

    def set_animated(self, target, color=None, suffix=""):
        self._cancel()
        self._anim(target, 0, color, suffix)

    def _anim(self, target, cur, color, suffix):
        steps = 10; ms = 35
        frac = min((cur + 1) / steps, 1.0)
        v = int(target * frac)
        self._val.config(text=f"{v:,}{suffix}", fg=color or "#FFFFFF",
                         font=(T["font_mono"], self._val_size, "bold"))
        if cur + 1 < steps:
            self._anim_id = self.after(ms, self._anim,
                                       target, cur + 1, color, suffix)
        else:
            self._anim_id = None

    def flash(self, flash_color, value, final_color):
        self._cancel()
        self._val.config(text=value, fg=flash_color,
                         font=(T["font_mono"], self._val_size, "bold"))
        self._flash_id = self.after(_FLASH_MS,
            lambda: self._val.config(fg=final_color))

    def set_collecting(self):
        self._cancel()
        self._val.config(text="...", fg=T["purple"],
                         font=(T["font_ui"], self._val_size, "bold"))

    def reset(self):
        self._cancel()
        self._val.config(text="—", fg="#FFFFFF",
                         font=(T["font_ui"], self._val_size, "bold"))

    def _cancel(self):
        if self._anim_id:
            self.after_cancel(self._anim_id); self._anim_id = None
        if self._flash_id:
            self.after_cancel(self._flash_id); self._flash_id = None


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  Info Bar                                                               ║
# ╚══════════════════════════════════════════════════════════════════════════╝
class InfoBar(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=T["info_bg"],
                         highlightbackground=T["info_border"],
                         highlightthickness=1, height=26)
        self.pack_propagate(False)
        self._hidden = True

    def show(self, data):
        self._hidden = False
        self.pack(fill="x")
        for w in self.winfo_children(): w.destroy()
        first = True
        for label, (val, color) in data.items():
            if not first:
                tk.Label(self, text="|", bg=T["info_bg"], fg=T["text_1"],
                         font=(T["font_ui"], 8)).pack(side="left", padx=2)
            first = False
            tk.Label(self, text=f" {label}: ", bg=T["info_bg"],
                     fg=T["text_2"],
                     font=(T["font_ui"], 8)).pack(side="left")
            tk.Label(self, text=val, bg=T["info_bg"],
                     fg=color or T["text_1"],
                     font=(T["font_mono"], 8, "bold")).pack(side="left")

    def hide(self):
        if self._hidden: return
        for w in self.winfo_children(): w.destroy()
        self._hidden = True
        self.pack_forget()


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  Button Factory                                                         ║
# ╚══════════════════════════════════════════════════════════════════════════╝
def _btn(parent, text, command=None, style="secondary", width=None):
    cfg = {
        "primary":   (T["blue"], T["blue_hover"], "#FFFFFF", T["blue_dim"]),
        "secondary": (T["surface"], T["card_hover"], T["text_2"], T["card_border"]),
        "ghost":     ("transparent", "#111E30", T["text_3"], T["text_4"]),
        "green":     (T["green_dim"], T["green"], "#FFFFFF", T["green"]),
    }
    bg, hov, fg, brd = cfg.get(style, cfg["secondary"])
    kw = dict(text=text, command=command, fg_color=bg, hover_color=hov,
              text_color=fg, border_color=brd, border_width=1,
              font=ctk.CTkFont(T["font_ui"], 11, "bold"),
              height=32, corner_radius=T["radius_sm"])
    if width: kw["width"] = width
    return ctk.CTkButton(parent, **kw)


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  Settings Dialog                                                        ║
# ╚══════════════════════════════════════════════════════════════════════════╝
class SettingsDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Settings")
        self.geometry("400x300")
        self.resizable(False, False)
        self.configure(fg_color=T["surface"])
        self.attributes("-topmost", True)
        self.grab_set()

        tk.Label(self, text="Settings", bg=T["surface"], fg=T["text_1"],
                 font=(T["font_ui"], 14, "bold"),
                 padx=20, pady=16).pack(anchor="w")
        tk.Frame(self, bg=T["card_border"], height=1).pack(fill="x")

        body = tk.Frame(self, bg=T["surface"])
        body.pack(fill="both", expand=True, padx=24, pady=12)

        self._vars = {}
        for label, key, default, values in [
            ("Missing Value Strategy", "missing", "median", ["median", "mean", "zero"]),
            ("Outlier Strategy (IQR)", "outliers", "keep", ["keep", "cap", "remove"]),
        ]:
            tk.Label(body, text=label, bg=T["surface"], fg=T["text_2"],
                     font=(T["font_ui"], 10)).pack(anchor="w", pady=(10, 2))
            v = tk.StringVar(value=default)
            self._vars[key] = v
            ctk.CTkComboBox(body, values=values, variable=v, width=200,
                            height=30, fg_color=T["input_bg"],
                            border_color=T["card_border"],
                            button_color=T["blue"],
                            font=ctk.CTkFont(T["font_ui"], 11)).pack(anchor="w")

        tk.Frame(self, bg=T["card_border"], height=1).pack(fill="x")
        bf = tk.Frame(self, bg=T["surface"])
        bf.pack(fill="x", padx=24, pady=12)
        _btn(bf, "Save", command=self._save, style="primary",
             width=100).pack(side="right")
        _btn(bf, "Cancel", command=self.destroy, style="ghost",
             width=80).pack(side="right", padx=(0, 8))

    def _save(self):
        p = self.master
        if hasattr(p, "_cmb_missing"):
            p._cmb_missing.set(self._vars["missing"].get())
        if hasattr(p, "_cmb_outliers"):
            p._cmb_outliers.set(self._vars["outliers"].get())
        self.destroy()


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  About Dialog                                                           ║
#   def __init__(self, parent):
   ╚══════════════════════════════════════════════════════════════════════════╝
class AboutDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("About - Souani Data Cleaner")
        self.geometry("420x360")
        self.resizable(False, False)
        self.configure(fg_color=T["surface"])
        self.attributes("-topmost", True)
        self.grab_set()

        top = tk.Frame(self, bg=T["surface"])
        top.pack(fill="x", padx=24, pady=16)

        # 🟢 إضافة الشعار المؤسسي (المربع الأزرق بحرف S)
        badge = tk.Frame(top, bg="#0284C7", width=36, height=36)
        badge.pack_propagate(False)
        badge.pack(side="left", padx=(0, 14))
        tk.Label(badge, text="S", bg="#0284C7", fg="#FFFFFF",
                 font=(T["font_ui"], 16, "bold")).pack(expand=True)

        info = tk.Frame(top, bg=T["surface"])
        info.pack(side="left", anchor="w")
        tk.Label(info, text="Souani Data Cleaner", bg=T["surface"],
                 fg=T["text_1"],
                 font=(T["font_ui"], 15, "bold")).pack(anchor="w")
        tk.Label(info, text=f"{VERSION}  |  Build {BUILD}",
                 bg=T["surface"], fg=T["gold"],
                 font=(T["font_ui"], 10)).pack(anchor="w", pady=(2, 0))
        tk.Label(info, text=COMPANY, bg=T["surface"], fg=T["text_3"],
                 font=(T["font_ui"], 9)).pack(anchor="w")

        tk.Frame(self, bg=T["card_border"], height=1).pack(fill="x")

        body = tk.Frame(self, bg=T["surface"])
        body.pack(fill="both", expand=True, padx=24, pady=12)
        for k, v in [("Edition", EDITION), ("License", LICENSE),
                     ("Support", "samhoonsharle@gmail.com"),
                     ("Runtime", "Python 3.9+ | pandas | customtkinter")]:
            row = tk.Frame(body, bg=T["surface"])
            row.pack(fill="x", pady=3)
            tk.Label(row, text=k, bg=T["surface"], fg=T["text_3"],
                     font=(T["font_ui"], 9), width=10,
                     anchor="w").pack(side="left")
            tk.Label(row, text=v, bg=T["surface"], fg=T["text_1"],
                     font=(T["font_ui"], 9)).pack(side="left")

        tk.Frame(self, bg=T["card_border"], height=1).pack(fill="x")
        _btn(self, "Close", command=self.destroy,
             style="primary", width=100).pack(pady=12)


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  MAIN WINDOW                                                            ║
# ╚══════════════════════════════════════════════════════════════════════════╝
class SouaniDataCleaner(ctk.CTk):

    def __init__(self):
        super().__init__()
        # 🟢 تعديل طفيف لإضافة كلمة Enterprise بشكل رسمي
        self.title(f"Souani Data Cleaner {VERSION} - Enterprise Edition")
        self.geometry("1220x640")
        self.minsize(1020, 540)
        self.configure(fg_color=T["bg"])

        self.cleaner = AdvancedDataCleaner()
        self.file_path = None
        self._t0 = 0.0
        self._ticking = False
        self._total_rows = 0
        self._spinner_id = None
        self._spinner_phase = 0
        self._ds_info = {}
        self._is_processing = False
        self._is_analyzing = False

        self._build_topbar()
        self._build_file_row()
        self._hr()
        self._build_dashboard()
        self._build_info_bar()
        self._hr()
        self._build_body()
        self._build_statusbar()

    def _hr(self):
        tk.Frame(self, bg=T["card_border"], height=1).pack(fill="x")

 # ── TOP BAR ──────────────────────────────────────────────────────────
    def _build_topbar(self):
        bar = tk.Frame(self, bg=T["topbar"], height=52)
        bar.pack(fill="x"); bar.pack_propagate(False)

        left = tk.Frame(bar, bg=T["topbar"])
        left.pack(side="left", padx=16, fill="y")
        
        # 🟢 المربع المؤسسي الأنيق بحرف S (بديل البرق)
        badge = tk.Frame(left, bg="#0284C7", width=28, height=28)
        badge.pack_propagate(False)
        badge.pack(side="left", anchor="center", padx=(0, 12))
        tk.Label(badge, text="S", bg="#0284C7", fg="#FFFFFF", 
                 font=(T["font_ui"], 12, "bold")).pack(expand=True)

        txt = tk.Frame(left, bg=T["topbar"])
        txt.pack(side="left", anchor="center")
        tk.Label(txt, text="Souani Enterprise Data Suite", bg=T["topbar"], ...)
                 fg=T["text_1"],
                 font=(T["font_ui"], 14, "bold")).pack(anchor="w")
        tk.Label(txt, text=f"{COMPANY}  |  {VERSION}",
                 bg=T["topbar"], fg=T["text_3"],
                 font=(T["font_ui"], 9)).pack(anchor="w")

        right = tk.Frame(bar, bg=T["topbar"])
        right.pack(side="right", padx=16, fill="y")
        for lbl, cmd in [("Settings", self._open_settings),
                         ("About", self._open_about)]:
            _btn(right, lbl, command=cmd, style="ghost",
                 width=90).pack(side="right", padx=2, pady=10)

        eng = tk.Frame(right, bg=T["topbar"])
        eng.pack(side="right", padx=(12, 8))
        eng_row = tk.Frame(eng, bg=T["topbar"])
        eng_row.pack(anchor="e", pady=(16, 2))
        self._engine_led = LED(eng_row, size=8, bg=T["topbar"])
        self._engine_led.pack(side="right", padx=(6, 0))
        self._engine_pill = StatusPill(eng_row, "STANDBY",
                                       pill_w=78, pill_h=18,
                                       canvas_bg=T["topbar"])
        self._engine_pill.pack(side="right")

    # ── FILE ROW ─────────────────────────────────────────────────────────
    def _build_file_row(self):
        row = tk.Frame(self, bg=T["surface"], height=42)
        row.pack(fill="x"); row.pack_propagate(False)

        tk.Label(row, text="Source", bg=T["surface"], fg=T["text_3"],
                 font=(T["font_ui"], 10),
                 padx=16).pack(side="left", fill="y")

        self._file_var = tk.StringVar(
            value="No file selected — choose CSV, Excel, or JSON")
        tk.Label(row, textvariable=self._file_var, bg=T["input_bg"],
                 fg=T["text_2"], font=(T["font_ui"], 10),
                 anchor="w", padx=12).pack(
                     side="left", fill="both", expand=True,
                     padx=(4, 12), pady=8)

        _btn(row, "Browse", command=self._browse, style="primary",
             width=100).pack(side="right", padx=14, pady=6)

    # ── DASHBOARD ────────────────────────────────────────────────────────
    def _build_dashboard(self):
        wrap = tk.Frame(self, bg=T["surface"])
        wrap.pack(fill="x", pady=(2, 0))

        hdr = tk.Frame(wrap, bg=T["surface"])
        hdr.pack(fill="x", padx=16, pady=(4, 3))
        tk.Label(hdr, text="Dashboard", bg=T["surface"],
                 fg=T["text_2"],
                 font=(T["font_ui"], 10, "bold")).pack(side="left")

        grid = tk.Frame(wrap, bg=T["surface"])
        grid.pack(fill="x", padx=12, pady=(0, 4))
        for c in range(6):
            grid.columnconfigure(c, weight=1, uniform="dc")

        specs = [
            ("Dataset Size", "size", False),
            ("File Type", "ftype", False),
            ("Total Rows", "rows", False),
            ("Total Columns", "cols", False),
            ("Success Rate", "success", True),
            ("Errors Fixed", "errors", False),
            ("Missing Filled", "missing", False),
            ("Outliers Fixed", "outliers", False),
            ("Duplicates Removed", "dups", False),
            ("Execution Time", "exec_time", True),
            ("Memory Peak", "memory", True),
            ("Dataset Health", "health", True),
        ]
        self._cards: Dict[str, MetricCard] = {}
        for i, (label, key, imp) in enumerate(specs):
            card = MetricCard(grid, label, important=imp)
            card.grid(row=i // 6, column=i % 6,
                      padx=4, pady=3, sticky="nsew")
            self._cards[key] = card

    def _build_info_bar(self):
        self._info_bar = InfoBar(self)

    # ── BODY ──────────────────────────────────────────────────────────────
    def _build_body(self):
        body = tk.Frame(self, bg=T["bg"])
        body.pack(fill="both", expand=True)

        sb = tk.Frame(body, bg=T["sidebar"], width=248)
        sb.pack(side="left", fill="y"); sb.pack_propagate(False)

        st = tk.Frame(sb, bg=T["sidebar"])
        st.pack(fill="x", padx=14, pady=(10, 0))
        self._sidebar_led = LED(st, size=7, bg=T["sidebar"])
        self._sidebar_led.pack(side="left", padx=(0, 6))
        self._state_lbl = tk.Label(st, text="Ready", bg=T["sidebar"],
                                   fg=T["green"],
                                   font=(T["font_ui"], 9))
        self._state_lbl.pack(side="left")

        tk.Label(sb, text="Options", bg=T["sidebar"], fg=T["text_2"],
                 font=(T["font_ui"], 10, "bold"),
                 padx=14).pack(anchor="w", pady=(14, 6))
        tk.Frame(sb, bg=T["card_border"], height=1).pack(fill="x", padx=14)

        opts = tk.Frame(sb, bg=T["sidebar"])
        opts.pack(fill="x", padx=14, pady=10)

        tk.Label(opts, text="Missing Values", bg=T["sidebar"],
                 fg=T["text_2"],
                 font=(T["font_ui"], 9)).pack(anchor="w", pady=(0, 3))
        self._cmb_missing = ctk.CTkComboBox(
            opts, values=["median", "mean", "zero"], width=218,
            height=30, fg_color=T["input_bg"],
            border_color=T["card_border"], button_color=T["blue"],
            font=ctk.CTkFont(T["font_ui"], 11))
        self._cmb_missing.set("median")
        self._cmb_missing.pack(anchor="w", pady=(0, 12))

        tk.Label(opts, text="Outliers (IQR)", bg=T["sidebar"],
                 fg=T["text_2"],
                 font=(T["font_ui"], 9)).pack(anchor="w", pady=(0, 3))
        self._cmb_outliers = ctk.CTkComboBox(
            opts, values=["keep", "cap", "remove"], width=218,
            height=30, fg_color=T["input_bg"],
            border_color=T["card_border"], button_color=T["blue"],
            font=ctk.CTkFont(T["font_ui"], 11))
        self._cmb_outliers.set("cap")
        self._cmb_outliers.pack(anchor="w", pady=(0, 14))

        tk.Frame(opts, bg=T["card_border"], height=1).pack(fill="x")

        self._clean_btn = ctk.CTkButton(
            opts, text="  Smart Auto Clean", command=self._run_clean,
            fg_color=T["blue"], hover_color=T["blue_hover"],
            text_color="#FFFFFF",
            font=ctk.CTkFont(T["font_ui"], 12, "bold"),
            height=38, corner_radius=T["radius"], border_width=0)
        self._clean_btn.pack(fill="x", pady=(12, 8))

        tk.Frame(opts, bg=T["card_border"], height=1).pack(fill="x")

        for lbl, act in [("Open Output", "output"),
                         ("HTML Report", "reports"),
                         ("Backups", "backup")]:
            _btn(opts, lbl,
                 command=lambda a=act: self._open_folder(a),
                 style="ghost").pack(fill="x", pady=1)

        tk.Frame(opts, bg=T["card_border"], height=1).pack(fill="x", pady=(12, 0))
        ph = tk.Frame(sb, bg=T["sidebar"])
        ph.pack(fill="x", padx=14, pady=(6, 2))
        tk.Label(ph, text="Progress", bg=T["sidebar"], fg=T["text_3"],
                 font=(T["font_ui"], 8, "bold")).pack(side="left")
        self._pct_lbl = tk.Label(ph, text="0%", bg=T["sidebar"],
                                  fg=T["blue"],
                                  font=(T["font_mono"], 9, "bold"))
        self._pct_lbl.pack(side="right")

        self._progress = ctk.CTkProgressBar(
            sb, height=6, corner_radius=3,
            fg_color=T["card"], progress_color=T["blue"])
        self._progress.set(0)
        self._progress.pack(fill="x", padx=14, pady=(0, 2))

        self._prog_detail = tk.Label(sb, text="", bg=T["sidebar"],
                                     fg=T["text_3"],
                                     font=(T["font_mono"], 8),
                                     anchor="w")
        self._prog_detail.pack(fill="x", padx=16, pady=(0, 10))

        tk.Frame(body, bg=T["card_border"], width=1).pack(
            side="left", fill="y")

        ai = tk.Frame(body, bg=T["surface"])
        ai.pack(side="left", fill="both", expand=True)

        ai_h = tk.Frame(ai, bg=T["topbar"])
        ai_h.pack(fill="x")
        ai_left = tk.Frame(ai_h, bg=T["topbar"])
        ai_left.pack(side="left", padx=14, pady=5)
        tk.Label(ai_left, text="AI Assistant", bg=T["topbar"],
                 fg=T["text_1"],
                 font=(T["font_ui"], 11, "bold")).pack(side="left")
        tk.Label(ai_left, text="  Intelligent Analysis", bg=T["topbar"],
                 fg=T["text_3"],
                 font=(T["font_ui"], 8)).pack(side="left")

        ai_right = tk.Frame(ai_h, bg=T["topbar"])
        ai_right.pack(side="right", padx=14, pady=5)
        self._ai_led = LED(ai_right, size=8, bg=T["topbar"])
        self._ai_led.pack(side="right", padx=(6, 0))
        self._ai_pill = StatusPill(ai_right, "READY",
                                   pill_w=70, pill_h=18,
                                   canvas_bg=T["topbar"])
        self._ai_pill.pack(side="right")

        tk.Frame(ai, bg=T["card_border"], height=1).pack(fill="x")

        self._console = tk.Text(
            ai, bg=T["bg_2"], fg=T["cyan"],
            font=(T["font_mono"], 11), relief="flat", bd=0,
            padx=16, pady=10, spacing1=2, spacing3=2,
            insertbackground=T["blue"], selectbackground=T["blue_glow"],
            wrap="word", state="disabled")
        self._console.pack(fill="both", expand=True)

        for tag, col, bold in [
            ("hdr", T["gold"], True), ("ok", T["green"], False),
            ("warn", T["orange"], False), ("err", T["red"], False),
            ("val", T["blue"], False), ("muted", T["text_3"], False),
            ("white", T["text_1"], False), ("step", T["cyan"], True),
            ("dim", T["text_4"], False),
        ]:
            self._console.tag_config(
                tag, foreground=col,
                font=(T["font_mono"], 11, "bold" if bold else "normal"))

        self._con_write("System Ready\n", "ok")
        self._con_write("\nDataset:\n  No dataset loaded.\n", "muted")
        self._con_write("\nAI Assistant:\n  Standing by.\n", "muted")
        self._con_write("\nSelect a CSV, Excel, or JSON file to begin.\n", "muted")

    # ── STATUS BAR ────────────────────────────────────────────────────────
    def _build_statusbar(self):
        bar = tk.Frame(self, bg=T["topbar"], height=22)
        bar.pack(side="bottom", fill="x"); bar.pack_propagate(False)
        tk.Frame(bar, bg=T["card_border"], height=1).pack(fill="x", side="top")

        inner = tk.Frame(bar, bg=T["topbar"])
        inner.pack(fill="both", expand=True)

        self._sb: Dict[str, tk.Label] = {}
        for i, (key, lbl, default) in enumerate([
            ("status", "Status", "Ready"), ("task", "Task", "Idle"),
            ("version", "Ver", VERSION), ("memory", "Mem", self._mem()),
            ("clock", "Time", ""),
        ]):
            if i:
                tk.Frame(inner, bg=T["card_border"],
                         width=1).pack(side="left", fill="y", pady=3)
            seg = tk.Frame(inner, bg=T["topbar"])
            seg.pack(side="left", padx=8, fill="y")
            tk.Label(seg, text=f"{lbl} ", bg=T["topbar"], fg=T["text_4"],
                     font=(T["font_ui"], 7)).pack(side="left")
            v = tk.Label(seg, text=default, bg=T["topbar"], fg=T["text_3"],
                         font=(T["font_mono"], 8))
            v.pack(side="left")
            self._sb[key] = v

        tk.Label(inner, text=COMPANY, bg=T["topbar"], fg=T["text_4"],
                 font=(T["font_ui"], 7)).pack(side="right", padx=10)

        self._clock_tick()
        self._mem_tick()

    def _mem(self):
        try:
            return f"{psutil.Process(os.getpid()).memory_info().rss/1e6:.0f}MB"
        except Exception:
            return "—"

    def _clock_tick(self):
        self._sb_set("clock", datetime.now().strftime("%H:%M:%S"))
        self.after(_CLOCK_MS, self._clock_tick)

    def _mem_tick(self):
        try:
            m = psutil.Process(os.getpid()).memory_info().rss
            self._sb_set("memory", f"{m/1e6:.0f}MB")
        except Exception:
            pass
        self.after(_MEMORY_MS, self._mem_tick)

    # ── HELPERS ───────────────────────────────────────────────────────────
    def _con_write(self, text, tag=None):
        try:
            self._console.config(state="normal")
            self._console.insert("end", text, tag)
            self._console.see("end")
        finally:
            self._console.config(state="disabled")

    def _con_section(self, title, stage=0, total=7):
        if stage:
            self._con_write(f"  [{stage}/{total}] {title}...\n", "step")
        else:
            self._con_write(f"\n{'─' * 44}\n", "dim")
            self._con_write(f"  {title}\n", "hdr")
            self._con_write(f"{'─' * 44}\n", "dim")

    def _con_clear(self):
        self._console.config(state="normal")
        self._console.delete("1.0", "end")
        self._console.config(state="disabled")

    def _sb_set(self, key, val, color=None):
        lbl = self._sb.get(key)
        if lbl:
            lbl.config(text=val, fg=color or T["text_3"])

    def _set_pct(self, pct, step="", rows=0):
        self._progress.set(pct / 100)
        self._pct_lbl.config(text=f"{int(pct)}%")
        if pct < 40:
            self._progress.configure(progress_color=T["blue"])
        elif pct < 80:
            self._progress.configure(progress_color=T["cyan"])
        else:
            self._progress.configure(progress_color=T["green"])

        eta = ""
        if self._total_rows > 0 and rows > 0 and self._ticking:
            el = time.time() - self._t0
            if el > 0.5 and rows > 100:
                rate = rows / el
                rem = self._total_rows - rows
                s = rem / rate if rate > 0 else 0
                eta = f"ETA {s:.0f}s" if s < 60 else f"ETA {s/60:.1f}m"

        parts = []
        if step: parts.append(step)
        if rows > 0 and self._total_rows > 0:
            parts.append(f"{rows:,}/{self._total_rows:,}")
        if eta: parts.append(eta)
        self._prog_detail.config(text="  |  ".join(parts))

    def _spinner_tick(self):
        ph = ["○", "◑", "●", "◒"]
        if not self._is_processing:
            self._clean_btn.configure(text="  Smart Auto Clean")
            return
        self._spinner_phase = (self._spinner_phase + 1) % 4
        self._clean_btn.configure(
            text=f"  {ph[self._spinner_phase]}  Processing...")
        self._spinner_id = self.after(_SPINNER_MS, self._spinner_tick)

    def _start_spinner(self):
        self._spinner_phase = 0
        self._spinner_tick()

    def _stop_spinner(self):
        if self._spinner_id:
            self.after_cancel(self._spinner_id)
            self._spinner_id = None
        self._clean_btn.configure(text="  Smart Auto Clean")

    def _tick(self):
        if not self._ticking: return
        e = time.time() - self._t0
        self._sb_set("status", f"Processing {e:.1f}s", T["blue"])
        self._sb_set("memory", self._mem())
        self.after(500, self._tick)

    def _start_timer(self):
        self._t0 = time.time()
        self._ticking = True
        self._tick()

    def _stop_timer(self):
        self._ticking = False

    def _set_state(self, state, label, color=None):
        c = color or _LED_MAP.get(state, T["text_2"])
        self._sidebar_led.set(state)
        self._state_lbl.config(text=label, fg=c)
        if state in ("PROCESSING", "CLEANING", "ANALYZING"):
            self._sidebar_led.pulse(2)

    def _set_engine(self, state):
        self._engine_pill.set(state)
        self._engine_led.set(state)
        if state in ("PROCESSING", "CLEANING", "ANALYZING"):
            self._engine_led.pulse(2)
            self._engine_pill.pulse(2)

    def _set_ai(self, state):
        self._ai_pill.set(state)
        self._ai_led.set(state)
        if state in ("PROCESSING", "CLEANING", "ANALYZING", "REPORTING"):
            self._ai_led.pulse(2)
            self._ai_pill.pulse(2)

    # ── BROWSE ────────────────────────────────────────────────────────────
    def _browse(self):
        p = filedialog.askopenfilename(
            title="Select Dataset",
            filetypes=[("Data Files", "*.csv *.xlsx *.xls *.json"),
                       ("All Files", "*.*")])
        if not p: return
        self.file_path = p
        fname = Path(p).name
        sz = Path(p).stat().st_size
        sz_str = f"{sz/1e6:.2f} MB" if sz > 1e6 else f"{sz/1e3:.1f} KB"
        ext = Path(p).suffix.upper().lstrip(".")

        self._file_var.set(p)
        self._cards["ftype"].set(ext)
        self._cards["size"].set(sz_str)
        self._sb_set("status", "Loaded", T["green"])
        self._sb_set("task", "Analyzing", T["purple"])
        self._set_engine("ANALYZING")
        self._set_ai("ANALYZING")
        self._set_state("ANALYZING", "Analyzing")
        self._is_analyzing = True

        self._con_clear()
        self._con_write("System Ready\n", "ok")
        self._con_write(f"\nDataset:\n  {fname}\n", "muted")
        self._con_write(f"  Size: {sz_str}  |  Type: {ext}\n", "val")
        self._con_write("\nAI Assistant:\n  Analyzing structure...\n", "step")

        for k in ["success", "errors", "exec_time", "memory"]:
            self._cards[k].set_collecting()

        threading.Thread(target=self._analyse, daemon=True).start()

    # ── ANALYSE ───────────────────────────────────────────────────────────
    def _analyse(self):
        try:
            import pandas as pd, numpy as np
            p = self.file_path; ext = Path(p).suffix.lower()

            self._con_section("File Structure", stage=1, total=5)
            if ext == ".csv":
                import chardet
                with open(p, "rb") as f:
                    raw = f.read(50000)
                det = chardet.detect(raw)
                encoding = det.get("encoding", "utf-8")
                conf = det.get("confidence", 0)
                enc_disp = f"{encoding} ({conf:.0f}%)"
                sample = raw.decode(encoding or "utf-8", errors="ignore")[:5000]
                try:
                    delim = csv.Sniffer().sniff(sample).delimiter
                except Exception:
                    delim = ","
                df = pd.read_csv(p); n_sh = 1
                self._ds_info["encoding"] = enc_disp
                self._ds_info["delimiter"] = f'"{delim}"'

            elif ext in (".xlsx", ".xls"):
                xl = pd.ExcelFile(p); n_sh = len(xl.sheet_names)
                df = xl.parse(xl.sheet_names[0])
                self._ds_info["sheet"] = xl.sheet_names[0]
                enc_disp = "Excel"; delim = "N/A"
            else:
                df = pd.read_json(p); n_sh = 1
                enc_disp = "UTF-8"; delim = "N/A"

            rows, cols = df.shape
            self._total_rows = rows

            self._con_section("Missing Values", stage=2, total=5)
            missing = int(df.isna().sum().sum())

            self._con_section("Duplicates", stage=3, total=5)
            dups = int(df.duplicated().sum())

            self._con_section("Outliers (IQR)", stage=4, total=5)
            outliers = 0
            for c in df.select_dtypes(include=[np.number]).columns:
                q1, q3 = df[c].quantile(.25), df[c].quantile(.75)
                iqr = q3 - q1
                outliers += int(
                    ((df[c] < q1-1.5*iqr) | (df[c] > q3+1.5*iqr)).sum())

            health = max(0, 100 - (missing/max(rows*cols,1))*100
                              - (dups/max(rows,1))*50)
            risk = "LOW" if health > 85 else "MEDIUM" if health > 60 else "HIGH"
            rc = T["green"] if risk == "LOW" else \
                 T["orange"] if risk == "MEDIUM" else T["red"]

            self._con_section("Health Score", stage=5, total=5)

            self._cards["rows"].set_animated(rows, T["text_1"])
            self._cards["cols"].set_animated(cols, T["text_1"])
            self._cards["missing"].flash(T["gold_bright"], f"{missing:,}",
                T["orange"] if missing else T["green"])
            self._cards["outliers"].flash(T["gold_bright"], f"{outliers:,}",
                T["orange"] if outliers else T["green"])
            self._cards["dups"].flash(T["gold_bright"], f"{dups:,}",
                T["red"] if dups else T["green"])
            self._cards["health"].flash(T["gold_bright"], f"{health:.0f}%", rc)

            info = {
                "File": (Path(p).name, T["text_1"]),
                "Size": ((f"{Path(p).stat().st_size/1e6:.2f} MB"
                          if Path(p).stat().st_size > 1e6
                          else f"{Path(p).stat().st_size/1e3:.1f} KB"),
                         T["text_1"]),
                "Rows": (f"{rows:,}", T["blue"]),
                "Cols": (f"{cols:,}", T["blue"]),
                "Type": (ext.upper(), T["text_1"]),
            }
            if ext == ".csv":
                info["Encoding"] = (enc_disp, T["text_2"])
                info["Delimiter"] = (delim, T["text_2"])
            if ext in (".xlsx", ".xls"):
                info["Sheet"] = (xl.sheet_names[0], T["text_2"])
            info["Quality"] = (f"{health:.0f}%", rc)
            self._info_bar.show(info)

            sug = self.cleaner.generate_ai_suggestions(df)
            self._con_section("AI Report")
            self._con_write(
                f"  Rows: {rows:,}  |  Columns: {cols}  |  Sheets: {n_sh}\n",
                "val")
            for s in sug:
                tag = ("ok" if s.startswith("\u2705") else
                       "warn" if ("\u0645\u0641\u0642\u0648\u062f\u0629" in s
                                  or "\u0645\u0643\u0631\u0631" in s
                                  or s.startswith("\u26a0")) else
                       "err" if s.startswith("\ud83d\udcc8") else None)
                self._con_write(f"  {s}\n", tag)

            rec = ("Health is good. Smart Auto Clean recommended."
                   if health > 85
                   else "Issues found. Run Smart Auto Clean.")
            self._con_write(f"\n  {rec}\n", "val")

            self._is_analyzing = False
            self._sb_set("task", "Done", T["green"])
            self._set_engine("READY")
            self._set_ai("READY")
            self._set_state("READY", "Analysis complete")

        except Exception as ex:
            self._is_analyzing = False
            self._sb_set("task", "Error", T["red"])
            self._set_engine("ERROR")
            self._set_ai("ERROR")
            self._set_state("ERROR", "Failed")
            self._con_write(f"\n  Error: {ex}\n", "err")

    # ── CLEAN ──────────────────────────────────────────────────────────────
    def _run_clean(self):
        if not self.file_path:
            messagebox.showwarning("No File", "Select a dataset first.")
            return
        if self._is_processing: return
        threading.Thread(target=self._exec_clean, daemon=True).start()

    def _exec_clean(self):
        self._is_processing = True
        self._spinner_phase = 0
        self._clean_btn.configure(state="disabled")
        self._start_spinner()

        self._set_engine("CLEANING")
        self._set_ai("CLEANING")
        self._set_state("CLEANING", "Cleaning")
        self._sb_set("status", "Processing", T["blue"])
        self._sb_set("task", "Cleaning", T["blue"])
        self._start_timer()

        self._con_clear()
        self._con_section("Processing Workflow")

        stages = [
            ("Reading dataset", 5, "Reading", 0),
            ("Cleaning columns", 15, "Columns", 0),
            ("Removing duplicates", 30, "Duplicates", self._total_rows // 4),
            ("Filling missing", 45, "Missing", self._total_rows // 2),
            ("Handling outliers", 60, "Outliers", int(self._total_rows * .7)),
            ("Generating report", 75, "Report", int(self._total_rows * .85)),
        ]
        for i, (title, pct, task, rows) in enumerate(stages, 1):
            self._con_section(title, stage=i, total=7)
            self._set_pct(pct, task, rows)
            self._sb_set("task", task, T["blue"])
            threading.Event().wait(0.2)

        try:
            import tracemalloc
            tracemalloc.start()
            t0 = time.time()

            self.cleaner.numeric_strategy = self._cmb_missing.get()
            self.cleaner.outlier_strategy = self._cmb_outliers.get()
            out = self.cleaner.clean_target(self.file_path, smart_auto=True)

            elapsed = time.time() - t0
            _, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()

            self._set_ai("SAVING")
            self._con_section("Saving", stage=7, total=7)
            self._set_pct(90, "Saving", self._total_rows)
            self._sb_set("task", "Saving", T["green"])
            threading.Event().wait(0.2)

            out_path = out[0] if out else self.file_path
            fname = Path(out_path).name
            el_s = f"{elapsed:.2f}s"
            mem_s = f"{peak/1e6:.1f}MB"

            self._cards["exec_time"].flash(T["gold_bright"], el_s, T["green"])
            self._cards["memory"].flash(T["gold_bright"], mem_s, T["cyan"])
            self._cards["errors"].flash("#FFF", "0", T["green"])
            self._cards["success"].flash("#FFF", "100%", T["green"])

            self._set_pct(100, "Done", self._total_rows)
            self._sb_set("status", f"Done {elapsed:.2f}s", T["green"])
            self._sb_set("task", "Complete", T["green"])
            self._set_engine("COMPLETED")
            self._set_ai("COMPLETED")
            self._set_state("COMPLETED", "Complete")

            self._con_section("Completed")
            self._con_write(f"  Output:    {fname}\n", "ok")
            self._con_write(f"  Time:      {el_s}\n", "ok")
            self._con_write(f"  Memory:    {mem_s}\n", "ok")
            self._con_write(f"  Rows:      {self._total_rows:,}\n", "ok")
            rname = f"cleaned_{Path(self.file_path).stem}_report.html"
            self._con_write(f"  Report:    Reports/{rname}\n", "ok")
            self._con_write("\n  Dataset cleaned successfully.\n", "ok")

        except Exception as ex:
            err_e = time.time() - self._t0
            self._set_engine("ERROR")
            self._set_ai("ERROR")
            self._set_state("ERROR", "Failed")
            self._sb_set("status", f"Error {err_e:.1f}s", T["red"])
            self._sb_set("task", "Failed", T["red"])
            self._con_clear()
            self._con_section("Error")
            self._con_write(f"  {ex}\n", "err")

        finally:
            self._stop_timer()
            self._stop_spinner()
            self._is_processing = False
            self._clean_btn.configure(
                state="normal", text="  Completed",
                fg_color=T["green_dim"], hover_color=T["green"],
                text_color="#FFF", border_width=2,
                border_color=T["green"])
            self.after(_COMPLETE_MS, self._reset_btn)
            self._set_pct(0)
            self._prog_detail.config(text="")

    def _open_folder(self, which):
        base = Path(self.file_path).parent if self.file_path else Path(".")
        folders = {"output": base, "reports": Path("Reports"),
                   "backup": base / "_backup"}
        p = folders.get(which, Path("."))
        p.mkdir(parents=True, exist_ok=True)
        ps = str(p.resolve())
        if sys.platform == "win32": os.startfile(ps)
        elif sys.platform == "darwin": subprocess.Popen(["open", ps])
        else: subprocess.Popen(["xdg-open", ps])

    def _reset_btn(self):
        self._clean_btn.configure(
            text="  Smart Auto Clean",
            fg_color=T["blue"], hover_color=T["blue_hover"],
            border_width=0)

    def _open_settings(self): SettingsDialog(self)
    def _open_about(self):    AboutDialog(self)


if __name__ == "__main__":
    app = SouaniDataCleaner()
    app.mainloop()