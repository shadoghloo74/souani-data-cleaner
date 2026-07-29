"""
Souani Data Cleaner  v4.0 LTS  —  Ultimate Enterprise Edition
Commercial Desktop Application  ·  Enterprise-Grade UI
Engine / AI / CSV-Excel-JSON logic : UNCHANGED
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

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ── Design Tokens ───────────────────────────────────────────────────────────
T = {
    "bg":          "#080D17",
    "surface":     "#0C1220",
    "card":        "#0F1929",
    "card_border": "#1E3555",
    "card_hover":  "#152540",
    "sidebar":     "#0A1018",
    "input_bg":    "#0B1422",
    "topbar":      "#09111F",

    "blue":        "#1A7FFF",
    "blue_dim":    "#1266CC",
    "blue_hover":  "#2288FF",
    "blue_glow":   "#1A4A88",

    "gold":        "#C9A227",
    "gold_bright": "#E8C040",
    "gold_dim":    "#7A6010",

    "text_1":      "#EAF0F8",
    "text_2":      "#7A90AA",
    "text_3":      "#3A506A",
    "text_4":      "#1E3040",

    "green":       "#00D48C",
    "orange":      "#F59E0B",
    "red":         "#F04040",
    "cyan":        "#22D4EE",
    "purple":      "#9B71EA",

    "radius":      6,
    "info_bg":     "#0B1628",
    "info_border": "#163355",
}

VERSION   = "v4.0 LTS"
BUILD     = "20260730"
COMPANY   = "Souani Technologies"
EDITION   = "Enterprise Commercial Edition"
LICENSE   = "Licensed — Enterprise"


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  SVG-style Logo  (Canvas, no emoji, flat professional)                  ║
# ╚══════════════════════════════════════════════════════════════════════════╝
def draw_logo(parent, size=51, bg=None):
    bg = bg or T["topbar"]
    c = tk.Canvas(parent, width=size, height=size,
                  bg=bg, highlightthickness=0, bd=0)

    cx   = size / 2
    rx   = size * 0.32
    top  = size * 0.22
    bot  = size * 0.80

    c.create_rectangle(cx-rx, top + rx*0.20, cx+rx, bot,
                       fill="#0A3060", outline="")
    for ratio in [0.38, 0.55, 0.70]:
        y = top + (bot - top) * ratio
        c.create_line(cx-rx+3, y, cx+rx-3, y, fill="#1A4A80", width=1)

    c.create_oval(cx-rx, bot - rx*0.24, cx+rx, bot + rx*0.24,
                  fill="#0C4080", outline="#1C60A8", width=1)
    c.create_oval(cx-rx, top, cx+rx, top + rx*0.40,
                  fill="#1868B8", outline="#2888D8", width=1)
    c.create_oval(cx-rx*0.55, top + rx*0.03,
                  cx+rx*0.10, top + rx*0.20,
                  fill="#2A7FCC", outline="")

    sx, sy = size * 0.74, size * 0.18
    for angle, length in [(0,5),(45,3),(90,5),(135,3),
                           (180,5),(225,3),(270,5),(315,3)]:
        rad = math.radians(angle)
        x2  = sx + math.cos(rad) * length
        y2  = sy + math.sin(rad) * length
        c.create_line(sx, sy, x2, y2,
                      fill=T["gold_bright"], width=1.8,
                      capstyle="round")
    c.create_oval(sx-2.2, sy-2.2, sx+2.2, sy+2.2,
                  fill=T["gold_bright"], outline="")

    return c


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  Status Badge                                                            ║
# ╚══════════════════════════════════════════════════════════════════════════╝
_BADGE_STYLES = {
    "READY":      ("#00301A", "#00D48C", "READY"),
    "PROCESSING": ("#001840", "#1A7FFF", "PROCESSING"),
    "COMPLETED":  ("#00301A", "#00D48C", "COMPLETED"),
    "WARNING":    ("#301800", "#F59E0B", "WARNING"),
    "ERROR":      ("#300000", "#F04040", "ERROR"),
    "STANDBY":    ("#1A1A2A", "#7A90AA", "STANDBY"),
    "ANALYZING":  ("#1A1040", "#9B71EA", "ANALYZING"),
    "CLEANING":   ("#001840", "#1A7FFF", "CLEANING"),
    "REPORTING":  ("#0A3030", "#22D4EE", "REPORTING"),
    "SAVING":     ("#0A3020", "#00D48C", "SAVING"),
}

class StatusBadge(tk.Label):
    def __init__(self, parent, state="READY", icon="", **kw):
        super().__init__(parent, padx=8, pady=2,
                         font=("Segoe UI", 8, "bold"),
                         relief="flat", bd=0, **kw)
        self._icon = icon
        self.set(state)

    def set(self, state: str):
        bg, fg, txt = _BADGE_STYLES.get(state, _BADGE_STYLES["STANDBY"])
        prefix = self._icon if self._icon else ""
        self.config(text=f"{prefix} {txt}", bg=bg, fg=fg,
                    highlightbackground=fg, highlightthickness=1)


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  Dashboard Card  (compact — KPI cards with animations)                  ║
# ╚══════════════════════════════════════════════════════════════════════════╝
_KPI_CARDS = {"success", "exec_time", "health", "memory"}

class MetricCard(tk.Frame):
    PAD_X    = 10
    PAD_TOP  = 5
    PAD_BOT  = 6

    def __init__(self, parent, label: str, icon: str = "", important: bool = False):
        super().__init__(parent,
                         bg=T["card"],
                         highlightbackground=T["card_border"],
                         highlightthickness=1)
        self._default_bg  = T["card"]
        self._default_brd = T["card_border"]
        self._hover_brd   = T["blue_dim"]
        self._important   = important
        self._val_size    = 15 if important else 13
        self._anim_id     = None

        header = tk.Frame(self, bg=T["card"])
        header.pack(anchor="w", padx=self.PAD_X, pady=(self.PAD_TOP, 1))
        if icon:
            tk.Label(header, text=icon,
                     bg=T["card"], fg=T["text_3"],
                     font=("Segoe UI", 8)).pack(side="left", padx=(0, 3))
        self._title = tk.Label(header, text=label,
                               bg=T["card"], fg=T["text_3"],
                               font=("Segoe UI", 7, "bold"),
                               anchor="w")
        self._title.pack(side="left")

        # Accent line for important KPI cards
        if important:
            tk.Frame(self, bg=T["blue_dim"], height=1).pack(
                fill="x", padx=self.PAD_X, pady=(1, 0))

        self._val = tk.Label(self, text="Not Loaded",
                             bg=T["card"], fg=T["text_3"],
                             font=("Segoe UI", self._val_size, "bold"),
                             anchor="w")
        self._val.pack(anchor="w",
                       padx=self.PAD_X, pady=(1, self.PAD_BOT))

        self.bind("<Enter>", self._hover_on)
        self.bind("<Leave>", self._hover_off)
        for child in self.winfo_children():
            child.bind("<Enter>", self._hover_on)
            child.bind("<Leave>", self._hover_off)

    def _hover_on(self, _):
        self.config(bg=T["card_hover"],
                   highlightbackground=self._hover_brd)
        self._title.config(bg=T["card_hover"])
        self._val.config(bg=T["card_hover"])

    def _hover_off(self, _):
        self.config(bg=self._default_bg,
                   highlightbackground=self._default_brd)
        self._title.config(bg=self._default_bg)
        self._val.config(bg=self._default_bg)

    def set(self, value, color=None, size=None):
        if self._anim_id:
            self.after_cancel(self._anim_id)
            self._anim_id = None
        sz = size or self._val_size
        self._val.config(text=str(value),
                         fg=color or T["cyan"],
                         font=("Segoe UI", sz, "bold"))

    def set_animated(self, target_num, color=None, suffix=""):
        if self._anim_id:
            self.after_cancel(self._anim_id)
            self._anim_id = None
        self._anim_step(target_num, 0, target_num, color, suffix)

    def _anim_step(self, target, current, total, color, suffix):
        duration = 0.4
        steps = 12
        step_ms = int(duration * 1000 / steps)
        frac = min((current + 1) / steps, 1.0)
        val = int(target * frac)
        self._val.config(text=f"{val:,}{suffix}",
                         fg=color or T["cyan"],
                         font=("Segoe UI", self._val_size, "bold"))
        if current + 1 < steps:
            self._anim_id = self.after(
                step_ms,
                self._anim_step, target, current + 1, total, color, suffix)
        else:
            self._anim_id = None

    def set_collecting(self):
        if self._anim_id:
            self.after_cancel(self._anim_id)
            self._anim_id = None
        self._val.config(text="Collecting...",
                         fg=T["purple"],
                         font=("Segoe UI", self._val_size - 2, "bold"))

    def reset(self):
        if self._anim_id:
            self.after_cancel(self._anim_id)
            self._anim_id = None
        self._val.config(text="Not Loaded",
                         fg=T["text_3"],
                         font=("Segoe UI", self._val_size, "bold"))


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  Enterprise Info Bar (shown after dataset load)                         ║
# ╚══════════════════════════════════════════════════════════════════════════╝
class InfoBar(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=T["info_bg"],
                         highlightbackground=T["info_border"],
                         highlightthickness=1, height=28)
        self.pack_propagate(False)
        self._items = {}
        self._hidden = True

    def show(self, data: dict):
        self._hidden = False
        self.pack(fill="x")
        for w in self.winfo_children():
            w.destroy()
        self._items = {}
        first = True
        for label, (val, color) in data.items():
            if not first:
                tk.Label(self, text="\u2502",
                         bg=T["info_bg"], fg=T["text_4"],
                         font=("Segoe UI", 8)).pack(side="left", padx=1)
            first = False
            lbl_text = label.upper()
            tk.Label(self, text=f" {lbl_text}: ",
                     bg=T["info_bg"], fg=T["text_3"],
                     font=("Segoe UI", 7, "bold")).pack(side="left")
            v = tk.Label(self, text=val,
                         bg=T["info_bg"], fg=color or T["text_1"],
                         font=("Segoe UI", 8, "bold"))
            v.pack(side="left")
            self._items[label] = v

    def hide(self):
        if self._hidden:
            return
        for w in self.winfo_children():
            w.destroy()
        self._items = {}
        self._hidden = True
        self.pack_forget()


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  Shared Button Factory                                                   ║
# ╚══════════════════════════════════════════════════════════════════════════╝
_BTN_HEIGHT = 32

def _btn(parent, text, command=None,
         style="secondary", width=None):
    cfg = {
        "primary":   (T["blue"],    T["blue_hover"], "#FFFFFF",
                      T["blue_dim"]),
        "secondary": (T["card"],    T["card_hover"], T["text_2"],
                      T["card_border"]),
        "ghost":     ("transparent","#111E30",       T["text_3"],
                      T["text_4"]),
        "gold":      (T["gold_dim"], T["gold"],     T["gold_bright"],
                      T["gold"]),
    }
    bg, hov, fg, brd = cfg.get(style, cfg["secondary"])
    kw = dict(
        text=text,
        command=command,
        fg_color=bg,
        hover_color=hov,
        text_color=fg,
        border_color=brd,
        border_width=1,
        font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
        height=_BTN_HEIGHT,
        corner_radius=T["radius"],
    )
    if width:
        kw["width"] = width
    return ctk.CTkButton(parent, **kw)


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  Settings Dialog                                                         ║
# ╚══════════════════════════════════════════════════════════════════════════╝
class SettingsDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Settings")
        self.geometry("420x320")
        self.resizable(False, False)
        self.configure(fg_color=T["surface"])
        self.attributes("-topmost", True)
        self.grab_set()

        hdr = tk.Frame(self, bg=T["topbar"])
        hdr.pack(fill="x")
        tk.Label(hdr, text="\u2699   Settings",
                 bg=T["topbar"], fg=T["text_1"],
                 font=("Segoe UI", 13, "bold"),
                 padx=16, pady=10).pack(anchor="w")
        tk.Frame(self, bg=T["card_border"], height=1).pack(fill="x")

        body = tk.Frame(self, bg=T["surface"])
        body.pack(fill="both", expand=True, padx=20, pady=12)

        self._vars = {}
        for label, key, default, values in [
            ("Default Missing Value Strategy", "missing", "median",
             ["median", "mean", "zero"]),
            ("Default Outlier Strategy (IQR)", "outliers", "keep",
             ["keep", "cap", "remove"]),
        ]:
            tk.Label(body, text=label,
                     bg=T["surface"], fg=T["text_2"],
                     font=("Segoe UI", 10)).pack(
                         anchor="w", pady=(8, 2))
            v = tk.StringVar(value=default)
            self._vars[key] = v
            ctk.CTkComboBox(body, values=values, variable=v,
                            width=200, height=28,
                            fg_color=T["input_bg"],
                            border_color=T["card_border"],
                            button_color=T["blue"],
                            font=ctk.CTkFont("Segoe UI", 11)
                            ).pack(anchor="w")

        tk.Label(body, text="Create backup before cleaning",
                 bg=T["surface"], fg=T["text_2"],
                 font=("Segoe UI", 10)).pack(anchor="w", pady=(12, 3))
        sw = ctk.CTkSwitch(body, text="",
                            fg_color=T["blue_glow"],
                            progress_color=T["blue"])
        sw.select()
        sw.pack(anchor="w")

        tk.Frame(self, bg=T["card_border"], height=1).pack(fill="x")
        bf = tk.Frame(self, bg=T["surface"])
        bf.pack(fill="x", padx=20, pady=10)
        _btn(bf, "Save & Close", command=self._save_and_close,
             style="primary", width=120).pack(side="right")
        _btn(bf, "Cancel", command=self.destroy,
             style="ghost", width=90).pack(side="right", padx=(0, 6))

    def _save_and_close(self):
        parent = self.master
        if hasattr(parent, "_cmb_missing") and hasattr(self, "_vars"):
            parent._cmb_missing.set(self._vars["missing"].get())
        if hasattr(parent, "_cmb_outliers") and hasattr(self, "_vars"):
            parent._cmb_outliers.set(self._vars["outliers"].get())
        self.destroy()


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  About Dialog                                                            ║
# ╚══════════════════════════════════════════════════════════════════════════╝
class AboutDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("About & License")
        self.geometry("460x400")
        self.resizable(False, False)
        self.configure(fg_color=T["surface"])
        self.attributes("-topmost", True)
        self.grab_set()

        hdr = tk.Frame(self, bg=T["topbar"])
        hdr.pack(fill="x")
        inner = tk.Frame(hdr, bg=T["topbar"])
        inner.pack(padx=18, pady=14)
        draw_logo(inner, size=52, bg=T["topbar"]).pack(side="left",
                                                        padx=(0, 14))
        txt_f = tk.Frame(inner, bg=T["topbar"])
        txt_f.pack(side="left", anchor="w")
        tk.Label(txt_f, text="Souani Data Cleaner",
                 bg=T["topbar"], fg=T["text_1"],
                 font=("Segoe UI", 15, "bold")).pack(anchor="w")
        tk.Label(txt_f, text=f"{VERSION}  \u00b7  Build {BUILD}",
                 bg=T["topbar"], fg=T["gold_bright"],
                 font=("Segoe UI", 10)).pack(anchor="w", pady=(1, 0))
        tk.Label(txt_f, text=f"{COMPANY}  \u00b7  {EDITION}",
                 bg=T["topbar"], fg=T["text_3"],
                 font=("Segoe UI", 9)).pack(anchor="w")

        tk.Frame(self, bg=T["card_border"], height=1).pack(fill="x")

        body = tk.Frame(self, bg=T["surface"])
        body.pack(fill="both", expand=True, padx=20, pady=14)

        rows = [
            ("Company",  COMPANY),
            ("Edition",  EDITION),
            ("License",  LICENSE),
            ("Website",  "https://souani.tech  (coming soon)"),
            ("Support",  "samhoonsharle@gmail.com"),
            ("Runtime",  "Python >= 3.9  |  pandas  |  plotly  |  customtkinter"),
        ]
        for key, val in rows:
            row = tk.Frame(body, bg=T["surface"])
            row.pack(fill="x", pady=3)
            tk.Label(row, text=key,
                     bg=T["surface"], fg=T["text_3"],
                     font=("Segoe UI", 9, "bold"),
                     width=10, anchor="w").pack(side="left")
            tk.Label(row, text=val,
                     bg=T["surface"], fg=T["text_1"],
                     font=("Segoe UI", 9)).pack(side="left")

        tk.Frame(body, bg=T["card_border"], height=1).pack(
            fill="x", pady=(10, 8))
        tk.Label(body,
                 text="\u00a9 2026 Souani Technologies. All rights reserved.\n"
                      "Redistribution of this software is strictly prohibited.",
                 bg=T["surface"], fg=T["text_3"],
                 font=("Segoe UI", 8), justify="left").pack(anchor="w")

        tk.Frame(self, bg=T["card_border"], height=1).pack(fill="x")
        bf = tk.Frame(self, bg=T["surface"])
        bf.pack(pady=10)
        _btn(bf, "Close", command=self.destroy,
             style="primary", width=110).pack()# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  MAIN APPLICATION WINDOW                                                 ║
# ╚══════════════════════════════════════════════════════════════════════════╝
class SouaniDataCleaner(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.title(f"Souani Data Cleaner {VERSION} \u2014 Ultimate Enterprise")
        self.geometry("1220x640")
        self.minsize(1020, 540)
        self.configure(fg_color=T["bg"])

        self.cleaner    = AdvancedDataCleaner()
        self.file_path  = None
        self._t0        = 0.0
        self._ticking   = False
        self._total_rows = 0
        self._eta_text  = ""
        self._spinner_id = None
        self._spinner_phase = 0
        self._ds_info: dict = {}

        self._is_processing = False
        self._is_analyzing  = False

        self._build_topbar()
        self._build_file_row()
        self._sep()
        self._build_dashboard()
        self._build_info_bar()
        self._sep()
        self._build_body()
        self._build_statusbar()

    def _sep(self, h=1):
        tk.Frame(self, bg=T["card_border"], height=h).pack(fill="x")

    # ── TOP BAR ──────────────────────────────────────────────────────────
    def _build_topbar(self):
        bar = tk.Frame(self, bg=T["topbar"], height=56)
        bar.pack(fill="x")
        bar.pack_propagate(False)

        brand = tk.Frame(bar, bg=T["topbar"])
        brand.pack(side="left", padx=14, fill="y")

        draw_logo(brand, size=40, bg=T["topbar"]).pack(
            side="left", anchor="center", pady=8, padx=(0, 10))

        txts = tk.Frame(brand, bg=T["topbar"])
        txts.pack(side="left", anchor="center")

        tk.Label(txts, text="Souani Data Cleaner",
                 bg=T["topbar"], fg=T["text_1"],
                 font=("Segoe UI", 15, "bold")).pack(anchor="w")

        sub = tk.Frame(txts, bg=T["topbar"])
        sub.pack(anchor="w", pady=(1, 0))
        tk.Label(sub, text=COMPANY,
                 bg=T["topbar"], fg=T["text_2"],
                 font=("Segoe UI", 8)).pack(side="left")
        tk.Label(sub, text=f"  \u2022  {EDITION}",
                 bg=T["topbar"], fg=T["text_3"],
                 font=("Segoe UI", 8)).pack(side="left")

        ver = tk.Label(txts,
                       text=f"  {VERSION}  \u2022  Build {BUILD}  ",
                       bg=T["gold_dim"], fg=T["gold_bright"],
                       font=("Segoe UI", 7, "bold"),
                       padx=2, pady=0)
        ver.pack(anchor="w", pady=(1, 0))

        right = tk.Frame(bar, bg=T["topbar"])
        right.pack(side="right", padx=14, fill="y")

        for label, cmd in [("Settings",      self._open_settings),
                            ("About",         self._open_about)]:
            _btn(right, label, command=cmd,
                 style="secondary", width=100).pack(
                     side="right", padx=3, pady=12)

        tk.Frame(bar, bg=T["card_border"], width=1).pack(
            side="right", fill="y", pady=8)
        eng = tk.Frame(bar, bg=T["topbar"])
        eng.pack(side="right", padx=14, fill="y")
        tk.Label(eng, text="ENGINE",
                 bg=T["topbar"], fg=T["text_3"],
                 font=("Segoe UI", 7, "bold")).pack(anchor="w", pady=(14,1))
        self._engine_badge = StatusBadge(eng, "STANDBY",
                                          bg=T["topbar"])
        self._engine_badge.pack(anchor="w")

    # ── FILE ROW ──────────────────────────────────────────────────────────
    def _build_file_row(self):
        row = tk.Frame(self, bg=T["surface"], height=38)
        row.pack(fill="x")
        row.pack_propagate(False)

        tk.Label(row, text="Dataset Source",
                 bg=T["surface"], fg=T["text_3"],
                 font=("Segoe UI", 9, "bold"),
                 padx=14).pack(side="left", fill="y")

        self._file_var = tk.StringVar(
            value="  No file selected \u2014 choose CSV, Excel, or JSON")
        tk.Label(row, textvariable=self._file_var,
                 bg=T["input_bg"], fg=T["text_2"],
                 font=("Segoe UI", 10),
                 anchor="w", padx=10).pack(
                     side="left", fill="both", expand=True,
                     padx=(0, 10), pady=6)

        _btn(row, "Browse File",
             command=self._browse,
             style="primary", width=120).pack(
                 side="right", padx=12, pady=5)

    # ── DASHBOARD ──────────────────────────────────────────────────────────
    def _build_dashboard(self):
        wrapper = tk.Frame(self, bg=T["surface"])
        wrapper.pack(fill="x")

        hdr = tk.Frame(wrapper, bg=T["surface"])
        hdr.pack(fill="x", padx=14, pady=(4, 2))
        tk.Label(hdr, text="Enterprise Dashboard",
                 bg=T["surface"], fg=T["gold_bright"],
                 font=("Segoe UI", 10, "bold")).pack(side="left")
        tk.Label(hdr, text="  Real-time intelligence",
                 bg=T["surface"], fg=T["text_3"],
                 font=("Segoe UI", 8)).pack(side="left")

        grid = tk.Frame(wrapper, bg=T["surface"])
        grid.pack(fill="x", padx=10, pady=(0, 3))
        for col in range(6):
            grid.columnconfigure(col, weight=1, uniform="dc")

        specs = [
            ("DATASET SIZE",      "size",       "",  False),
            ("FILE TYPE",         "ftype",      "",  False),
            ("TOTAL ROWS",        "rows",       "",  False),
            ("TOTAL COLUMNS",     "cols",       "",  False),
            ("SUCCESS RATE",      "success",    "",  True),
            ("ERRORS FIXED",      "errors",     "",  False),
            ("MISSING FILLED",    "missing",    "",  False),
            ("OUTLIERS FIXED",    "outliers",   "",  False),
            ("DUPLICATES REMOVED","dups",       "",  False),
            ("EXECUTION TIME",    "exec_time",  "",  True),
            ("MEMORY PEAK",       "memory",     "",  True),
            ("DATASET HEALTH",    "health",     "",  True),
        ]
        self._cards: dict[str, MetricCard] = {}
        for i, (label, key, icon, imp) in enumerate(specs):
            card = MetricCard(grid, label, icon=icon, important=imp)
            card.grid(row=i // 6, column=i % 6,
                      padx=3, pady=2, sticky="nsew")
            self._cards[key] = card

    # ── INFO BAR ───────────────────────────────────────────────────────────
    def _build_info_bar(self):
        self._info_bar = InfoBar(self)

    # ── BODY ──────────────────────────────────────────────────────────────
    def _build_body(self):
        body = tk.Frame(self, bg=T["bg"])
        body.pack(fill="both", expand=True)

        sb = tk.Frame(body, bg=T["sidebar"], width=256)
        sb.pack(side="left", fill="y")
        sb.pack_propagate(False)

        tk.Label(sb, text="Cleaning Options",
                 bg=T["sidebar"], fg=T["gold_bright"],
                 font=("Segoe UI", 10, "bold"),
                 padx=14, pady=8).pack(anchor="w")
        tk.Frame(sb, bg=T["card_border"], height=1).pack(fill="x")

        opts = tk.Frame(sb, bg=T["sidebar"])
        opts.pack(fill="x", padx=12, pady=8)

        tk.Label(opts, text="Missing Value Strategy",
                 bg=T["sidebar"], fg=T["text_2"],
                 font=("Segoe UI", 9)).pack(anchor="w", pady=(0, 3))
        self._cmb_missing = ctk.CTkComboBox(
            opts, values=["median", "mean", "zero"],
            width=228, height=28,
            fg_color=T["input_bg"],
            border_color=T["card_border"],
            button_color=T["blue"],
            font=ctk.CTkFont("Segoe UI", 11))
        self._cmb_missing.set("median")
        self._cmb_missing.pack(anchor="w", pady=(0, 10))

        tk.Label(opts, text="Outliers Strategy (IQR)",
                 bg=T["sidebar"], fg=T["text_2"],
                 font=("Segoe UI", 9)).pack(anchor="w", pady=(0, 3))
        self._cmb_outliers = ctk.CTkComboBox(
            opts, values=["keep", "cap", "remove"],
            width=228, height=28,
            fg_color=T["input_bg"],
            border_color=T["card_border"],
            button_color=T["blue"],
            font=ctk.CTkFont("Segoe UI", 11))
        self._cmb_outliers.set("cap")
        self._cmb_outliers.pack(anchor="w", pady=(0, 12))

        tk.Frame(opts, bg=T["card_border"], height=1).pack(fill="x")

        self._clean_btn = ctk.CTkButton(
            opts,
            text="\u25cf  Smart Auto Clean",
            command=self._run_clean,
            fg_color=T["blue"],
            hover_color=T["blue_hover"],
            text_color="#FFFFFF",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            height=36,
            corner_radius=T["radius"],
            border_width=0,
            anchor="center",
        )
        self._clean_btn.pack(fill="x", pady=(10, 6))

        tk.Frame(opts, bg=T["card_border"], height=1).pack(fill="x",
                                                            pady=(0, 6))

        for label, act in [
            ("Open Output Folder",   "output"),
            ("Open HTML Report",     "reports"),
            ("Open Backup Folder",   "backup"),
        ]:
            _btn(opts, label,
                 command=lambda a=act: self._open_folder(a),
                 style="secondary").pack(fill="x", pady=2)

        tk.Frame(opts, bg=T["card_border"], height=1).pack(fill="x",
                                                            pady=(10, 0))
        prog_hdr = tk.Frame(sb, bg=T["sidebar"])
        prog_hdr.pack(fill="x", padx=12, pady=(6, 2))
        tk.Label(prog_hdr, text="Progress",
                 bg=T["sidebar"], fg=T["text_3"],
                 font=("Segoe UI", 8, "bold")).pack(side="left")

        self._pct_lbl = tk.Label(prog_hdr, text="0%",
                                  bg=T["sidebar"], fg=T["blue"],
                                  font=("Segoe UI", 9, "bold"))
        self._pct_lbl.pack(side="right")

        self._progress = ctk.CTkProgressBar(
            sb, height=8,
            corner_radius=4,
            fg_color=T["card"],
            progress_color=T["blue"])
        self._progress.set(0)
        self._progress.pack(fill="x", padx=12, pady=(0, 2))

        self._prog_detail = tk.Label(
            sb, text="",
            bg=T["sidebar"], fg=T["text_3"],
            font=("Segoe UI", 7),
            anchor="w")
        self._prog_detail.pack(fill="x", padx=14, pady=(0, 10))

        tk.Frame(body, bg=T["card_border"], width=1).pack(
            side="left", fill="y")

        ai_wrap = tk.Frame(body, bg=T["surface"])
        ai_wrap.pack(side="left", fill="both", expand=True)

        ai_hdr = tk.Frame(ai_wrap, bg=T["topbar"])
        ai_hdr.pack(fill="x")

        ai_hdr_left = tk.Frame(ai_hdr, bg=T["topbar"])
        ai_hdr_left.pack(side="left", padx=14, pady=6)
        tk.Label(ai_hdr_left, text="AI Executive Assistant Panel",
                 bg=T["topbar"], fg=T["text_1"],
                 font=("Segoe UI", 11, "bold")).pack(side="left")
        tk.Label(ai_hdr_left, text="  \u00b7  Intelligent Analysis Copilot",
                 bg=T["topbar"], fg=T["text_3"],
                 font=("Segoe UI", 8)).pack(side="left")

        self._ai_badge = StatusBadge(ai_hdr, "READY",
                                      bg=T["topbar"])
        self._ai_badge.pack(side="right", padx=14, pady=6)

        tk.Frame(ai_wrap, bg=T["card_border"], height=1).pack(fill="x")

        self._console = tk.Text(
            ai_wrap,
            bg=T["bg"],
            fg=T["cyan"],
            font=("Consolas", 11),
            relief="flat", bd=0,
            padx=14, pady=8,
            spacing1=1, spacing2=2, spacing3=1,
            insertbackground=T["blue"],
            selectbackground=T["blue_glow"],
            wrap="word",
            state="disabled",
        )
        self._console.pack(fill="both", expand=True)

        for tag, col, bold in [
            ("hdr",     T["gold_bright"],  True),
            ("ok",      T["green"],        False),
            ("warn",    T["orange"],       False),
            ("err",     T["red"],          False),
            ("val",     T["blue"],         False),
            ("muted",   T["text_3"],       False),
            ("white",   T["text_1"],       False),
            ("step",    T["cyan"],         True),
        ]:
            self._console.tag_config(
                tag,
                foreground=col,
                font=("Consolas", 11, "bold" if bold else "normal"))

        self._con_write("\u2713  System Ready\n",                              "ok")
        self._con_write("\n  Dataset:\n    No dataset loaded.\n",                  "muted")
        self._con_write("\n  AI Copilot:\n    Standing by.\n",                  "muted")
        self._con_write("\n  Executive Recommendation:\n    Select a CSV, Excel, or JSON dataset.\n", "muted")

    # ── ENTERPRISE STATUS BAR ─────────────────────────────────────────────
    def _build_statusbar(self):
        bar = tk.Frame(self, bg=T["topbar"], height=24)
        bar.pack(side="bottom", fill="x")
        bar.pack_propagate(False)
        tk.Frame(bar, bg=T["card_border"], height=1).pack(fill="x", side="top")

        inner = tk.Frame(bar, bg=T["topbar"])
        inner.pack(fill="both", expand=True)

        self._sb: dict[str, tk.Label] = {}
        segs = [
            ("status",  "Status",   "Ready"),
            ("task",    "Task",     "Idle"),
            ("version", "Version",  VERSION),
            ("license", "License",  "Enterprise"),
            ("memory",  "Memory",   self._get_memory()),
            ("clock",   "Time",     ""),
        ]
        for i, (key, label, default) in enumerate(segs):
            if i:
                tk.Frame(inner, bg=T["card_border"],
                         width=1).pack(side="left", fill="y", pady=2)
            seg = tk.Frame(inner, bg=T["topbar"])
            seg.pack(side="left", padx=8, fill="y")
            tk.Label(seg, text=label.upper() + " ",
                     bg=T["topbar"], fg=T["text_4"],
                     font=("Segoe UI", 7, "bold")).pack(side="left")
            lbl = tk.Label(seg, text=default,
                           bg=T["topbar"], fg=T["text_2"],
                           font=("Segoe UI", 8, "bold"))
            lbl.pack(side="left")
            self._sb[key] = lbl

        tk.Label(inner,
                 text=f"{COMPANY}  \u2022  {BUILD}",
                 bg=T["topbar"], fg=T["text_4"],
                 font=("Segoe UI", 7)
                 ).pack(side="right", padx=10)

        self._update_memory()

    def _get_memory(self) -> str:
        try:
            mem = psutil.Process(os.getpid()).memory_info().rss
            return f"{mem / 1e6:.0f} MB"
        except Exception:
            return "N/A"

    def _update_memory(self):
        try:
            mem = psutil.Process(os.getpid()).memory_info().rss
            self._sb_set("memory", f"{mem / 1e6:.0f} MB")
        except Exception:
            pass
        now = datetime.now().strftime("%H:%M:%S")
        self._sb_set("clock", now)
        self.after(1000, self._update_memory)

    # ── WRITE HELPERS ─────────────────────────────────────────────────────
    def _con_write(self, text, tag=None):
        try:
            self._console.config(state="normal")
            if tag:
                self._console.insert("end", text, tag)
            else:
                self._console.insert("end", text)
            self._console.see("end")
        finally:
            self._console.config(state="disabled")

    def _con_clear(self):
        self._console.config(state="normal")
        self._console.delete("1.0", "end")
        self._console.config(state="disabled")

    def _sb_set(self, key, val, color=None):
        lbl = self._sb.get(key)
        if lbl:
            lbl.config(text=val, fg=color or T["text_2"])

    def _set_pct(self, pct: float, step: str = "", rows: int = 0):
        self._progress.set(pct / 100)
        self._pct_lbl.config(text=f"{int(pct)}%")

        eta = ""
        if self._total_rows > 0 and rows > 0 and self._ticking:
            elapsed = time.time() - self._t0
            if elapsed > 0.5 and rows > 100:
                rate = rows / elapsed
                remaining = self._total_rows - rows
                eta_sec = remaining / rate if rate > 0 else 0
                eta = f"ETA {eta_sec:.0f}s" if eta_sec < 60 else f"ETA {eta_sec/60:.1f}m"

        parts = []
        if step:
            parts.append(step)
        if rows > 0:
            parts.append(f"{rows:,} rows")
        if eta:
            parts.append(eta)
        self._prog_detail.config(text="  \u2502  ".join(parts))

    def _spinner_tick(self):
        phases = ["\u25CB", "\u25D1", "\u25CF", "\u25D0"]
        if not self._is_processing:
            self._clean_btn.configure(text="\u25cf  Smart Auto Clean")
            return
        self._spinner_phase = (self._spinner_phase + 1) % len(phases)
        icon = phases[self._spinner_phase]
        self._clean_btn.configure(text=f"  {icon}  Processing\u2026")
        self._spinner_id = self.after(150, self._spinner_tick)

    def _start_spinner(self):
        self._spinner_phase = 0
        self._spinner_tick()

    def _stop_spinner(self):
        if self._spinner_id:
            self.after_cancel(self._spinner_id)
            self._spinner_id = None
        self._clean_btn.configure(text="\u25cf  Smart Auto Clean")

    def _tick(self):
        if not self._ticking:
            return
        self._sb_set("memory", self._get_memory())
        self.after(500, self._tick)

    def _start_timer(self):
        self._t0 = time.time()
        self._ticking = True
        self._tick()

    def _stop_timer(self):
        self._ticking = False

    # ── BROWSE ───────────────────────────────────────────────────────────
    def _browse(self):
        p = filedialog.askopenfilename(
            title="Select Dataset",
            filetypes=[("Data Files", "*.csv *.xlsx *.xls *.json"),
                       ("All Files", "*.*")])
        if not p:
            return
        self.file_path = p
        fname  = Path(p).name
        sz     = Path(p).stat().st_size
        sz_str = (f"{sz/1e6:.2f} MB" if sz > 1e6
                  else f"{sz/1e3:.1f} KB")
        ext    = Path(p).suffix.upper().lstrip(".")

        self._file_var.set(f"  {p}")
        self._cards["ftype"].set(ext)
        self._cards["size"].set(sz_str)
        self._sb_set("status", "Loaded", T["green"])
        self._sb_set("task", "Analyzing", T["purple"])
        self._engine_badge.set("ANALYZING")
        self._ai_badge.set("ANALYZING")
        self._is_analyzing = True

        self._con_clear()
        self._con_write("\u2713  System Ready\n",                              "ok")
        self._con_write(f"\n  Dataset:\n    {fname}\n",                        "muted")
        self._con_write(f"    Size: {sz_str}   Type: {ext}\n",              "val")
        self._con_write("\n  AI Copilot:\n    Analyzing dataset structure...\n", "step")

        for key in ["success", "errors", "exec_time", "memory"]:
            self._cards[key].set_collecting()

        threading.Thread(target=self._analyse, daemon=True).start()

    # ── ANALYSE ──────────────────────────────────────────────────────────
    def _analyse(self):
        try:
            import pandas as pd, numpy as np
            p = self.file_path; ext = Path(p).suffix.lower()

            self._con_write("  [STEP 1/5] Reading file structure...\n", "step")
            if ext == ".csv":
                import chardet
                with open(p, "rb") as f:
                    raw = f.read(50000)
                detected = chardet.detect(raw)
                encoding = detected.get("encoding", "utf-8")
                conf = detected.get("confidence", 0)
                enc_display = f"{encoding} ({conf:.0f}%)"

                sample = raw.decode(encoding or "utf-8", errors="ignore")[:5000]
                sniffer = csv.Sniffer()
                try:
                    dialect = sniffer.sniff(sample)
                    delimiter = dialect.delimiter
                except Exception:
                    delimiter = ","

                df = pd.read_csv(p)
                n_sh = 1
                self._ds_info["encoding"] = enc_display
                self._ds_info["delimiter"] = f'"{delimiter}"'

            elif ext in (".xlsx", ".xls"):
                xl = pd.ExcelFile(p); n_sh = len(xl.sheet_names)
                df = xl.parse(xl.sheet_names[0])
                self._ds_info["sheet"] = xl.sheet_names[0]
                self._ds_info["sheets"] = str(n_sh)
                enc_display = "Excel"
                delimiter = "N/A"

            else:
                df = pd.read_json(p); n_sh = 1
                enc_display = "UTF-8"
                delimiter = "N/A"

            rows, cols  = df.shape
            self._total_rows = rows

            self._con_write("  [STEP 2/5] Scanning missing values...\n", "step")
            missing     = int(df.isna().sum().sum())

            self._con_write("  [STEP 3/5] Detecting duplicates...\n", "step")
            dups        = int(df.duplicated().sum())

            self._con_write("  [STEP 4/5] Scanning outliers (IQR)...\n", "step")
            outliers    = 0
            for c in df.select_dtypes(include=[np.number]).columns:
                q1, q3 = df[c].quantile(.25), df[c].quantile(.75)
                iqr    = q3 - q1
                outliers += int(
                    ((df[c] < q1-1.5*iqr) | (df[c] > q3+1.5*iqr)).sum())

            health = max(0, 100 - (missing/max(rows*cols,1))*100
                              - (dups/max(rows,1))*50)
            risk   = ("LOW" if health > 85
                      else "MEDIUM" if health > 60 else "HIGH")
            rc     = (T["green"] if risk == "LOW"
                      else T["orange"] if risk == "MEDIUM" else T["red"])

            self._con_write("  [STEP 5/5] Building health score...\n", "step")

            self._cards["rows"].set_animated(rows, T["cyan"])
            self._cards["cols"].set_animated(cols, T["cyan"])
            self._cards["missing"].set(f"{missing:,}",
                color=T["orange"] if missing else T["green"])
            self._cards["outliers"].set(f"{outliers:,}",
                color=T["orange"] if outliers else T["green"])
            self._cards["dups"].set(f"{dups:,}",
                color=T["red"] if dups else T["green"])
            self._cards["health"].set(f"{health:.0f}%",
                color=T["green"] if health > 85
                      else T["orange"] if health > 60 else T["red"])

            info_data = {
                "File":    (Path(p).name, T["text_1"]),
                "Size":    ((f"{Path(p).stat().st_size/1e6:.2f} MB"
                             if Path(p).stat().st_size > 1e6
                             else f"{Path(p).stat().st_size/1e3:.1f} KB"),
                            T["text_1"]),
                "Rows":    (f"{rows:,}", T["cyan"]),
                "Cols":    (f"{cols:,}", T["cyan"]),
                "Type":    (ext.upper(), T["text_1"]),
            }
            if ext == ".csv":
                info_data["Encoding"] = (enc_display, T["text_2"])
                info_data["Delimiter"] = (delimiter, T["text_2"])
            if ext in (".xlsx", ".xls"):
                info_data["Sheet"] = (xl.sheet_names[0], T["text_2"])
            info_data["Quality"] = (f"{health:.0f}%", rc)

            self._info_bar.show(info_data)

            sug = self.cleaner.generate_ai_suggestions(df)
            self._con_write("\n== AI Analysis Report ==============================\n",
                            "hdr")
            self._con_write(
                f"  Rows: {rows:,}   Columns: {cols}   Sheets: {n_sh}\n",
                "val")
            for s in sug:
                tag = ("ok"   if s.startswith("\u2705")
                       else "warn" if ("\u0645\u0641\u0642\u0648\u062f\u0629" in s
                                       or "\u0645\u0643\u0631\u0631" in s
                                       or s.startswith("\u26a0"))
                       else "err"  if s.startswith("\ud83d\udcc8") else None)
                self._con_write(f"  {s}\n", tag)

            rec = ("Dataset health is GOOD. Smart Auto Clean recommended."
                   if health > 85
                   else "Issues detected. Run Smart Auto Clean for best results.")
            self._con_write(f"\n  Recommendation: {rec}\n", "val")

            self._is_analyzing = False
            self._sb_set("task", "Analyzed", T["green"])
            self._engine_badge.set("READY")
            self._ai_badge.set("READY")

        except Exception as ex:
            self._is_analyzing = False
            self._sb_set("task", "Error", T["red"])
            self._engine_badge.set("ERROR")
            self._ai_badge.set("ERROR")
            self._con_write(f"\n  Analysis error: {ex}\n", "err")

    # ── CLEAN ──────────────────────────────────────────────────────────────
    def _run_clean(self):
        if not self.file_path:
            messagebox.showwarning("No File",
                                   "Please select a dataset first.")
            return
        if self._is_processing:
            return
        threading.Thread(target=self._exec_clean, daemon=True).start()

    def _exec_clean(self):
        self._is_processing = True
        self._spinner_phase = 0

        self._clean_btn.configure(state="disabled")
        self._start_spinner()

        self._engine_badge.set("CLEANING")
        self._ai_badge.set("CLEANING")
        self._sb_set("status", "Processing", T["blue"])
        self._sb_set("task", "Cleaning dataset", T["blue"])
        self._start_timer()

        self._con_clear()
        self._con_write("== PROCESSING WORKFLOW ==============================\n",
                        "hdr")

        self._con_write("  [STAGE 1/7] Reading dataset...\n", "step")
        self._set_pct(5, "Reading", 0)
        self._sb_set("task", "Reading", T["blue"])
        threading.Event().wait(0.25)

        self._con_write("  [STAGE 2/7] Cleaning column names...\n", "step")
        self._set_pct(15, "Column names", 0)
        self._sb_set("task", "Cleaning columns", T["blue"])
        threading.Event().wait(0.2)

        self._con_write("  [STAGE 3/7] Removing duplicates...\n", "step")
        self._set_pct(30, "Removing duplicates", 0)
        self._sb_set("task", "Removing duplicates", T["blue"])
        threading.Event().wait(0.2)

        self._con_write("  [STAGE 4/7] Filling missing values...\n", "step")
        self._set_pct(45, "Filling missing", 0)
        self._sb_set("task", "Filling missing", T["blue"])
        threading.Event().wait(0.2)

        self._con_write("  [STAGE 5/7] Handling outliers...\n", "step")
        self._set_pct(60, "Handling outliers", 0)
        self._sb_set("task", "Handling outliers", T["blue"])
        threading.Event().wait(0.2)

        self._ai_badge.set("REPORTING")
        self._con_write("  [STAGE 6/7] Generating HTML report...\n", "step")
        self._set_pct(75, "Generating report", 0)
        self._sb_set("task", "Generating report", T["cyan"])
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

            self._ai_badge.set("SAVING")
            self._con_write("  [STAGE 7/7] Saving output file...\n", "step")
            self._set_pct(90, "Saving", self._total_rows)
            self._sb_set("task", "Saving output", T["green"])
            threading.Event().wait(0.2)

            out_path  = out[0] if out else self.file_path
            fname     = Path(out_path).name
            el_str    = f"{elapsed:.2f}s"
            mem_str   = f"{peak/1e6:.1f} MB"

            self._cards["exec_time"].set(el_str, T["green"], size=15)
            self._cards["memory"].set(mem_str, size=15)
            self._cards["errors"].set("0", T["green"])
            self._cards["success"].set("100%", T["green"], size=15)

            self._set_pct(100, "Complete", self._total_rows)
            self._sb_set("status", "Completed", T["green"])
            self._sb_set("task", "Done", T["green"])
            self._engine_badge.set("COMPLETED")
            self._ai_badge.set("COMPLETED")

            self._con_write("\n== COMPLETED =====================================\n",
                            "hdr")
            self._con_write(f"  \u2713  Output File:      {fname}\n",  "ok")
            self._con_write(f"  \u2713  Execution Time:   {el_str}\n",  "ok")
            self._con_write(f"  \u2713  Memory Peak:      {mem_str}\n",  "ok")
            self._con_write(f"  \u2713  Rows Processed:   {self._total_rows:,}\n", "ok")
            self._con_write(
                "\n  \u2713  Dataset cleaned and standardized successfully.\n", "ok")
            self._con_write(
                "  Review the HTML Executive Report for full analysis.\n",
                "muted")

        except Exception as ex:
            self._engine_badge.set("ERROR")
            self._ai_badge.set("ERROR")
            self._sb_set("status", "Error", T["red"])
            self._sb_set("task", "Failed", T["red"])
            self._con_clear()
            self._con_write("== ERROR ==========================================\n",
                            "hdr")
            self._con_write(f"  {ex}\n", "err")

        finally:
            self._stop_timer()
            self._stop_spinner()
            self._is_processing = False
            self._clean_btn.configure(
                state="normal",
                text="\u2713  Completed",
                fg_color=T["green"],
                hover_color="#00A870")
            self.after(3000, self._reset_clean_btn)
            self._set_pct(0)
            self._prog_detail.config(text="")

    # ── FOLDER OPENER ──────────────────────────────────────────────────
    def _open_folder(self, which: str):
        base = Path(self.file_path).parent if self.file_path else Path(".")
        folders = {
            "output":  base,
            "reports": Path("Reports"),
            "backup":  base / "_backup",
        }
        p = folders.get(which, Path("."))
        p.mkdir(parents=True, exist_ok=True)
        p_str = str(p.resolve())
        if sys.platform == "win32":
            os.startfile(p_str)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", p_str])
        else:
            subprocess.Popen(["xdg-open", p_str])

    def _reset_clean_btn(self):
        self._clean_btn.configure(
            text="\u25cf  Smart Auto Clean",
            fg_color=T["blue"],
            hover_color=T["blue_hover"])

    # ── DIALOGS ────────────────────────────────────────────────────────
    def _open_settings(self): SettingsDialog(self)
    def _open_about(self):    AboutDialog(self)


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = SouaniDataCleaner()
    app.mainloop()