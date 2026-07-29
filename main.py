#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
Souani Data Cleaner v4.0 LTS (Enterprise Edition)
Build: 4.0.0-lts.20260725
Developer: Souani Technologies
Description: Commercial-Grade Enterprise Data Cleaning & Analytics Engine
===============================================================================
"""
from __future__ import annotations
import argparse
import os
import platform
import sys
import threading
import time
import warnings
import webbrowser
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd

# Suppress pandas date parsing and future deprecation warnings
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=FutureWarning)

try:
    import psutil
except ImportError:
    psutil = None

try:
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk
except ImportError:
    tk = None

# =============================================================================
# Constants & Enterprise Metadata
# =============================================================================
PRODUCT_NAME = "Souani Data Cleaner"
VERSION = "v4.0 LTS"
EDITION = "Enterprise Commercial Edition"
BUILD_NUMBER = "4.0.0-lts.20260725"
COMPANY = "Souani Technologies"
WEBSITE = "https://example.com/souani-technologies"
GITHUB = "https://github.com/souani-technologies/souani-data-cleaner"
LICENSE_NAME = "Proprietary Commercial Enterprise License"

SUPPORTED_EXTENSIONS = {".csv", ".xlsx", ".xls", ".json"}
LARGE_FILE_THRESHOLD_MB = 200

# Enterprise Theme Palette (Dark Theme + Blue + Gold Accent)
THEME_BG_DARK = "#0F172A"       # Deep Slate Dark
THEME_PANEL_BG = "#1E293B"      # Dark Card Background
THEME_CARD_BG = "#334155"       # Inner Card Level
THEME_BLUE_ACCENT = "#0284C7"   # Enterprise Blue Primary
THEME_BLUE_HOVER = "#0369A1"    # Darker Blue Primary
THEME_BLUE_PRESSED = "#075985"  # Pressed State Blue
THEME_GOLD_ACCENT = "#D4AF37"   # Gold Accent
THEME_TEXT_PRIMARY = "#F8FAFC"  # High Contrast Text
THEME_TEXT_MUTED = "#94A3B8"    # Muted Gray Subtitles
THEME_SUCCESS = "#10B981"       # Success Green
THEME_BORDER = "#475569"        # Subtle Border Separator
THEME_BORDER_LIGHT = "#64748B"  # Highlighted Border

# =============================================================================
# Custom Exception
# =============================================================================
class SouaniUserError(Exception):
    """Clean, non-technical user-facing errors."""
    pass

# =============================================================================
# Data Structures
# =============================================================================
@dataclass
class CleaningResult:
    success: bool
    execution_time_sec: float
    rows_before: int
    rows_after: int
    rows_processed: int
    output_location: str
    output_folder: str
    html_report: str
    backup_folder: str
    file_type: str
    file_size_human: str
    processing_speed_rps: float
    memory_usage_str: str
    cleaning_status: str
    recommendations: List[str]
    stats: Dict[str, Any]

# =============================================================================
# Utility Helpers
# =============================================================================
def now_stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def human_size(num: int) -> str:
    size = float(num)
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024.0 or unit == "GB":
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} GB"

def open_path(path: str) -> None:
    if not path or not os.path.exists(path):
        return
    abs_p = os.path.abspath(path)
    if platform.system() == "Windows":
        os.startfile(abs_p)
    elif platform.system() == "Darwin":
        os.system(f'open "{abs_p}"')
    else:
        os.system(f'xdg-open "{abs_p}" >/dev/null 2>&1 &')

# =============================================================================
# Core Engine (UNTOUCHED)
# =============================================================================
class SouaniDataCleanerEngine:
    def _progress(self, callback: Optional[Callable[[int, str], None]], value: int, message: str) -> None:
        if callback:
            callback(max(0, min(100, int(value))), message)

    def _memory_mb(self) -> Optional[float]:
        if not psutil:
            return None
        try:
            return round(psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024, 2)
        except Exception:
            return None

    def _format_memory_usage(self, mem_used: Optional[float]) -> str:
        if mem_used is None:
            return "N/A"
        if mem_used <= 0.0 or mem_used < 1.0:
            return "< 1 MB"
        return f"{mem_used:.2f} MB"

    def validate_file(self, file_path: str) -> Path:
        if not file_path:
            raise SouaniUserError("الرجاء اختيار ملف أولاً لتشغيل عملية التنظيف.")
        path = Path(file_path)
        if not path.exists():
            raise SouaniUserError("الملف المحدد غير موجود أو تم تحريكه من مكانه.")
        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            raise SouaniUserError(f"صيغة الملف غير مدعومة ({path.suffix}). الصيغ المدعومة هي CSV, XLSX, XLS, JSON.")
        if path.stat().st_size == 0:
            raise SouaniUserError("الملف المحدد فارغ ولا يحتوي على أي بيانات.")
        return path

    def load_dataset(self, path: Path) -> Tuple[pd.DataFrame, Optional[str]]:
        ext = path.suffix.lower()
        try:
            if ext == ".csv":
                try:
                    df = pd.read_csv(path, encoding="utf-8-sig")
                except UnicodeDecodeError:
                    try:
                        df = pd.read_csv(path, encoding="latin1")
                    except Exception:
                        raise SouaniUserError("عفواً، فشل قراءة ملف CSV بسبب مشكلة في الترميز (Encoding).")
                except Exception:
                    raise SouaniUserError("ملف CSV غير صالح أو يحتوي على بنية أسطر غير منتظمة.")
                return self._check_df(df, "ملف CSV"), None

            elif ext in {".xlsx", ".xls"}:
                try:
                    excel = pd.ExcelFile(path)
                except Exception:
                    raise SouaniUserError("تعذر فتح ملف Excel. الملف إما تالف أو محمي بكلمة سر.")
                
                valid_sheet = None
                valid_df = None
                for sheet in excel.sheet_names:
                    try:
                        temp_df = pd.read_excel(excel, sheet_name=sheet)
                        if not temp_df.empty and temp_df.dropna(how="all").shape[0] > 0:
                            valid_sheet = sheet
                            valid_df = temp_df
                            break
                    except Exception:
                        continue
                if valid_df is None:
                    raise SouaniUserError("جميع أوراق العمل (Sheets) في ملف Excel فارغة أو محجوبة.")
                return valid_df, valid_sheet

            elif ext == ".json":
                try:
                    df = pd.read_json(path)
                except ValueError:
                    raise SouaniUserError("ملف JSON غير صالح أو يحتوي على بنية نصوص غير متوافقة.")
                except Exception:
                    raise SouaniUserError("حدث خطأ أثناء قراءة هيكل ملف JSON.")
                return self._check_df(df, "ملف JSON"), None
        except SouaniUserError as e:
            raise e
        except Exception:
            raise SouaniUserError("تعذر قراءة الملف المحدد. الرجاء التأكد من سلامته.")

        raise SouaniUserError("صيغة ملف غير مدعومة.")

    def _check_df(self, df: pd.DataFrame, label: str) -> pd.DataFrame:
        if df is None or df.empty or df.dropna(how="all").empty:
            raise SouaniUserError(f"{label} فارغ ولا يحتوي على صفوف بيانات مقبولة.")
        return df

    def detect_outliers_iqr(self, df: pd.DataFrame) -> Dict[str, Tuple[float, float, int]]:
        outliers_info = {}
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            q1 = df[col].quantile(0.25)
            q3 = df[col].quantile(0.75)
            iqr = q3 - q1
            if iqr > 0:
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr
                count = int(((df[col] < lower_bound) | (df[col] > upper_bound)).sum())
                if count > 0:
                    outliers_info[col] = (lower_bound, upper_bound, count)
        return outliers_info

    def _clean_dates(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, int]:
        cleaned_df = df.copy()
        invalid_dates_count = 0
        for col in cleaned_df.columns:
            col_name_lower = str(col).lower()
            if any(k in col_name_lower for k in ['date', 'time', 'tariqh', 'day']):
                original_series = cleaned_df[col]
                null_or_empty_mask = original_series.isna() | (original_series.astype(str).str.strip() == "") | (original_series.astype(str).str.strip().isin(["nan", "None", "NULL", "null", "N/A"]))
                parsed = pd.to_datetime(original_series, errors='coerce')
                
                invalid_mask = (~null_or_empty_mask) & parsed.isna()
                invalid_dates_count += int(invalid_mask.sum())
                formatted_series = parsed.dt.strftime('%Y-%m-%d')
                formatted_series = formatted_series.where(~invalid_mask, "Invalid Date")
                formatted_series = formatted_series.where(~null_or_empty_mask, "Missing Date")
                
                cleaned_df[col] = formatted_series
        return cleaned_df, invalid_dates_count

    def clean_and_export(
        self,
        file_path: str,
        output_dir: Optional[str] = None,
        missing_strategy: str = "median",
        outlier_strategy: str = "cap",
        progress_callback: Optional[Callable[[int, str], None]] = None
    ) -> CleaningResult:
        start_time = time.perf_counter()
        mem_start = self._memory_mb()

        self._progress(progress_callback, 10, "Processing... Validating file and system resources")
        path = self.validate_file(file_path)
        file_size_mb = path.stat().st_size / (1024 * 1024)
        
        self._progress(progress_callback, 25, "Processing... Loading dataset structure into memory")
        df, sheet_name = self.load_dataset(path)
        
        rows_before, cols_before = df.shape
        dupes_before = int(df.duplicated().sum())
        missing_before = int(df.isna().sum().sum())
        outliers_dict = self.detect_outliers_iqr(df)
        total_outliers = sum([v[2] for v in outliers_dict.values()])

        # Step 1: Duplicates & Whitespace & NaNs
        self._progress(progress_callback, 40, "Cleaning... Deduplicating rows and trimming whitespace")
        cleaned_df = df.drop_duplicates().copy()
        for col in cleaned_df.columns:
            if cleaned_df[col].dtype == object or isinstance(cleaned_df[col].dtype, pd.StringDtype):
                cleaned_df[col] = cleaned_df[col].apply(lambda x: x.strip() if isinstance(x, str) else x)
                cleaned_df[col] = cleaned_df[col].replace(["", "nan", "None", "NULL", "null"], np.nan)

        # Step 2: Date Parsing & Formatting
        self._progress(progress_callback, 55, "Cleaning... Standardizing temporal and date attributes")
        cleaned_df, invalid_dates = self._clean_dates(cleaned_df)

        # Step 3: Missing Values
        self._progress(progress_callback, 70, "Cleaning... Imputing missing fields according to selected profile")
        if missing_strategy == "drop":
            cleaned_df = cleaned_df.dropna().copy()
        else:
            for col in cleaned_df.columns:
                if pd.api.types.is_numeric_dtype(cleaned_df[col]):
                    val = cleaned_df[col].median() if missing_strategy == "median" else cleaned_df[col].mean()
                    cleaned_df[col] = cleaned_df[col].fillna(val)
                else:
                    cleaned_df[col] = cleaned_df[col].fillna("N/A")

        # Step 4: Outliers
        self._progress(progress_callback, 82, "Cleaning... Handling statistical outliers (IQR technique)")
        if outlier_strategy != "keep" and outliers_dict:
            for col, (lower_b, upper_b, count) in outliers_dict.items():
                if col in cleaned_df.columns and pd.api.types.is_numeric_dtype(cleaned_df[col]):
                    if outlier_strategy == "cap":
                        cleaned_df[col] = np.clip(cleaned_df[col], lower_b, upper_b)
                    elif outlier_strategy == "remove":
                        cleaned_df = cleaned_df[(cleaned_df[col] >= lower_b) & (cleaned_df[col] <= upper_b)]

        rows_after = len(cleaned_df)

        # Setup Directories
        stamp = now_stamp()
        out_base = Path(output_dir) if output_dir else path.parent / "Souani_Cleaned_Output"
        backup_dir = out_base / "backups"
        out_base.mkdir(parents=True, exist_ok=True)
        backup_dir.mkdir(parents=True, exist_ok=True)

        # Save Backup
        self._progress(progress_callback, 88, "Cleaning... Archiving raw dataset backup")
        backup_path = backup_dir / f"{path.stem}_backup_{stamp}{path.suffix}"
        self._export_by_ext(df, backup_path, path.suffix.lower())

        # Save Cleaned Data
        self._progress(progress_callback, 93, "Generating Report... Exporting enterprise output dataset")
        cleaned_path = out_base / f"{path.stem}_cleaned_{stamp}{path.suffix}"
        self._export_by_ext(cleaned_df, cleaned_path, path.suffix.lower())

        # Recommendations
        recs = self._generate_ai_recommendations(
            dupes_before, missing_before, total_outliers, invalid_dates, file_size_mb
        )

        elapsed = max(time.perf_counter() - start_time, 0.001)
        mem_end = self._memory_mb()
        mem_used = max((mem_end or 0) - (mem_start or 0), 0) if mem_start and mem_end else None
        mem_str = self._format_memory_usage(mem_used)

        stats = {
            "file_name": path.name,
            "rows_before": rows_before,
            "rows_after": rows_after,
            "cols": cols_before,
            "dupes_before": dupes_before,
            "missing_before": missing_before,
            "outliers_found": total_outliers,
            "invalid_dates": invalid_dates,
            "execution_time": round(elapsed, 3),
            "speed_rps": round(rows_before / elapsed, 2),
            "memory_usage": mem_str,
            "file_size": human_size(path.stat().st_size),
            "cleaning_status": "Completed Successfully"
        }

        # Save HTML Report
        self._progress(progress_callback, 97, "Generating Report... Compiling interactive HTML summary")
        html_report_path = out_base / f"{path.stem}_report_{stamp}.html"
        self._generate_html_report(stats, recs, html_report_path)

        self._progress(progress_callback, 100, "Completed.")

        return CleaningResult(
            success=True,
            execution_time_sec=round(elapsed, 3),
            rows_before=rows_before,
            rows_after=rows_after,
            rows_processed=rows_before,
            output_location=str(cleaned_path),
            output_folder=str(out_base),
            html_report=str(html_report_path),
            backup_folder=str(backup_dir),
            file_type=path.suffix.upper().replace(".", ""),
            file_size_human=human_size(path.stat().st_size),
            processing_speed_rps=round(rows_before / elapsed, 2),
            memory_usage_str=mem_str,
            cleaning_status="Completed Successfully",
            recommendations=recs,
            stats=stats
        )

    def _export_by_ext(self, df: pd.DataFrame, target_path: Path, ext: str) -> None:
        if ext == ".csv":
            df.to_csv(target_path, index=False, encoding="utf-8-sig")
        elif ext in {".xlsx", ".xls"}:
            df.to_excel(target_path, index=False)
        elif ext == ".json":
            df.to_json(target_path, orient="records", indent=4, force_ascii=False)

    def _generate_ai_recommendations(self, dupes: int, missing: int, outliers: int, invalid_dates: int, size_mb: float) -> List[str]:
        recs = []
        if dupes > 0:
            recs.append(f"Purged {dupes} exact duplicate rows from dataset core.")
        if missing > 0:
            recs.append(f"Imputed and repaired {missing} null or empty field entries.")
        if outliers > 0:
            recs.append(f"Adjusted {outliers} statistical outliers utilizing IQR thresholds.")
        if invalid_dates > 0:
            recs.append(f"Flagged {invalid_dates} malformed date values with 'Invalid Date'.")
        if size_mb > LARGE_FILE_THRESHOLD_MB:
            recs.append(f"Large File Alert ({size_mb:.1f} MB): Memory optimization recommended for datasets over 500MB.")
        if not recs:
            recs.append("Dataset structure passed all checks cleanly with no adjustments needed.")
        return recs

    def _generate_html_report(self, stats: Dict[str, Any], recs: List[str], report_path: Path) -> None:
        recs_list = "".join([f"<li>{r}</li>" for r in recs])
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{PRODUCT_NAME} - Enterprise Analytics Report</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 40px; }}
        .container {{ max-width: 950px; margin: 0 auto; background: #1e293b; padding: 35px; border-radius: 12px; border: 1px solid #334155; }}
        .header {{ border-bottom: 2px solid #0284c7; padding-bottom: 15px; margin-bottom: 20px; }}
        .header h1 {{ margin: 0; color: #f8fafc; font-size: 2em; }}
        .header p {{ color: #94a3b8; font-size: 0.9em; margin-top: 5px; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }}
        .card {{ background: #334155; padding: 15px; border-radius: 8px; border-left: 4px solid #d4af37; }}
        .card label {{ font-size: 0.8em; color: #94a3b8; display: block; }}
        .card span {{ font-size: 1.3em; font-weight: bold; color: #38bdf8; }}
        ul {{ background: #0f172a; padding: 20px 30px; border-radius: 8px; line-height: 1.8; color: #cbd5e1; }}
        .footer {{ margin-top: 35px; font-size: 0.85em; color: #64748b; text-align: center; border-top: 1px solid #334155; padding-top: 15px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 {PRODUCT_NAME} - Executive Report</h1>
            <p><strong>File:</strong> {stats['file_name']} | <strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        <h3>📈 Executive Performance Summary</h3>
        <div class="grid">
            <div class="card"><label>Status</label><span>{stats['cleaning_status']}</span></div>
            <div class="card"><label>Rows Before</label><span>{stats['rows_before']:,}</span></div>
            <div class="card"><label>Rows After</label><span>{stats['rows_after']:,}</span></div>
            <div class="card"><label>Execution Speed</label><span>{stats['speed_rps']} r/s</span></div>
            <div class="card"><label>Memory Peak</label><span>{stats['memory_usage']}</span></div>
        </div>
        <h3>🤖 Intelligent Recommendations</h3>
        <ul>{recs_list}</ul>
        <div class="footer">
            © {datetime.now().year} {COMPANY}. {EDITION}.
        </div>
    </div>
</body>
</html>"""
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(html)

# =============================================================================
# Refined Enterprise GUI (LTS Polish Release)
# =============================================================================
class AIExecutiveAssistantPanel(ttk.Frame):
    """
    AI Executive Assistant Panel - Refined Enterprise Edition
    """
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(style="Card.TFrame")
        self._build_ui()
        self.set_state_waiting()

    def _build_ui(self):
        self.container = tk.Frame(self, bg=THEME_PANEL_BG, highlightbackground=THEME_BORDER, highlightthickness=1)
        self.container.pack(fill="both", expand=True)

        self.header_frame = tk.Frame(self.container, bg=THEME_PANEL_BG)
        self.header_frame.pack(fill="x", padx=16, pady=(12, 6))
        
        self.lbl_title = tk.Label(
            self.header_frame,
            text="🤖 AI Executive Assistant Panel",
            font=("Segoe UI", 10, "bold"),
            bg=THEME_PANEL_BG,
            fg=THEME_GOLD_ACCENT
        )
        self.lbl_title.pack(side="left")

        self.lbl_badge = tk.Label(
            self.header_frame,
            text="[ STANDBY ]",
            font=("Segoe UI", 8, "bold"),
            bg=THEME_CARD_BG,
            fg=THEME_TEXT_MUTED,
            padx=8,
            pady=3
        )
        self.lbl_badge.pack(side="right")

        self.text_box = tk.Text(
            self.container,
            font=("Segoe UI", 9),
            height=7,
            bg=THEME_BG_DARK,
            fg=THEME_TEXT_PRIMARY,
            relief="flat",
            highlightthickness=0,
            wrap="word",
            padx=12,
            pady=10
        )
        self.text_box.pack(fill="both", expand=True, padx=16, pady=(0, 12))
        self.text_box.config(state=tk.DISABLED)

    def _update_badge(self, text: str, fg_color: str, bg_color: str):
        self.lbl_badge.config(text=text, fg=fg_color, bg=bg_color)

    def _set_content(self, text_content: str):
        self.text_box.config(state=tk.NORMAL)
        self.text_box.delete("1.0", tk.END)
        self.text_box.insert(tk.END, text_content)
        self.text_box.config(state=tk.DISABLED)

    def set_state_waiting(self):
        self._update_badge("[ STANDBY ]", THEME_TEXT_MUTED, THEME_CARD_BG)
        content = (
            "System Ready\n"
            "No dataset loaded.\n\n"
            "Select a CSV, Excel or JSON dataset to begin intelligent analysis."
        )
        self._set_content(content)

    def set_state_dataset_loaded(self, file_name: str, file_size: str):
        self._update_badge("[ DATASET READY ]", THEME_BLUE_ACCENT, THEME_CARD_BG)
        content = (
            f"📋 DATASET LOADED ({file_name})\n"
            f"• File Size: {file_size}\n\n"
            "🔍 Status Overview:\n"
            "  - Ready for Automated Clean & Transformation Sequence.\n"
            "  - Missing value & outlier policies configured."
        )
        self._set_content(content)

    def set_state_completed(self, result: CleaningResult):
        self._update_badge("[ COMPLETED ]", THEME_SUCCESS, THEME_CARD_BG)
        stats = result.stats
        recs = result.recommendations
        recs_formatted = "\n".join([f"  ✔ {r}" for r in recs])
        content = (
            "Cleaning Completed Successfully\n\n"
            f"• Execution Time:         {stats['execution_time']} sec\n"
            f"• Rows Processed:         {stats['rows_before']:,} rows\n"
            f"• Output Saved:           {result.output_location}\n"
            f"• Backup Created:         {result.backup_folder}\n"
            f"• HTML Report Generated:  {result.html_report}\n\n"
            "📊 Intelligent Insights:\n"
            f"{recs_formatted}"
        )
        self._set_content(content)


class SouaniCleanerApp:
    def __init__(self) -> None:
        if tk is None:
            raise RuntimeError("Tkinter library unavailable.")
        self.engine = SouaniDataCleanerEngine()
        self.root = tk.Tk()
        self.root.title(f"{PRODUCT_NAME} {VERSION} - {EDITION}")
        
        self.root.geometry("1020x670")
        self.root.minsize(920, 620)
        self.root.configure(bg=THEME_BG_DARK)

        self.file_path = tk.StringVar()
        self.status_text = tk.StringVar(value="Ready...")
        self.result: Optional[CleaningResult] = None

        self._configure_styles()
        self._build_ui()

    def _configure_styles(self) -> None:
        self.style = ttk.Style(self.root)
        self.style.theme_use("clam")
        
        # Base Typography
        self.style.configure(".", background=THEME_BG_DARK, foreground=THEME_TEXT_PRIMARY, font=("Segoe UI", 9))
        self.style.configure("TFrame", background=THEME_BG_DARK)
        self.style.configure("Card.TFrame", background=THEME_PANEL_BG, relief="flat")
        self.style.configure("InnerCard.TFrame", background=THEME_CARD_BG, relief="flat")
        
        # Combo & Inputs
        self.root.option_add('*TCombobox*Listbox.background', THEME_PANEL_BG)
        self.root.option_add('*TCombobox*Listbox.foreground', THEME_TEXT_PRIMARY)
        self.root.option_add('*TCombobox*Listbox.selectBackground', THEME_BLUE_ACCENT)
        self.style.configure("TCombobox", fieldbackground=THEME_CARD_BG, background=THEME_BORDER, foreground=THEME_TEXT_PRIMARY, padding=4)

        # Progressbar
        self.style.configure("Horizontal.TProgressbar", background=THEME_GOLD_ACCENT, troughcolor=THEME_CARD_BG, borderwidth=0)
        self.style.configure("Vertical.TScrollbar", background=THEME_PANEL_BG, troughcolor=THEME_BG_DARK, borderwidth=0, arrowcolor=THEME_TEXT_MUTED)

    def _build_ui(self) -> None:
        # Header Panel
        header = tk.Frame(self.root, bg=THEME_PANEL_BG, height=65)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        h_content = tk.Frame(header, bg=THEME_PANEL_BG)
        h_content.pack(fill="both", expand=True, padx=20, pady=10)

        titles_f = tk.Frame(h_content, bg=THEME_PANEL_BG)
        titles_f.pack(side="left")
        title_lbl = tk.Label(titles_f, text=f"⚡ {PRODUCT_NAME}", font=("Segoe UI", 13, "bold"), bg=THEME_PANEL_BG, fg=THEME_TEXT_PRIMARY)
        title_lbl.pack(anchor="w")
        sub_lbl = tk.Label(titles_f, text=f"{COMPANY}  |  {EDITION}  |  {VERSION} ({BUILD_NUMBER})", font=("Segoe UI", 8), bg=THEME_PANEL_BG, fg=THEME_GOLD_ACCENT)
        sub_lbl.pack(anchor="w")

        about_btn = self._create_custom_button(
            h_content,
            text="About & License",
            bg_color=THEME_CARD_BG,
            hover_color=THEME_BORDER,
            pressed_color=THEME_BORDER_LIGHT,
            fg_color=THEME_TEXT_PRIMARY,
            command=self.show_about_dialog,
            padding_x=14,
            padding_y=5
        )
        about_btn.pack(side="right", pady=2)

        # Bottom Action Bar
        status_card = tk.Frame(self.root, bg=THEME_PANEL_BG, height=85)
        status_card.pack(fill="x", side="bottom")
        status_card.pack_propagate(False)

        sc_inner = tk.Frame(status_card, bg=THEME_PANEL_BG)
        sc_inner.pack(fill="both", expand=True, padx=20, pady=10)

        p_f = tk.Frame(sc_inner, bg=THEME_PANEL_BG)
        p_f.pack(fill="x", side="top", pady=(0, 6))
        self.lbl_status = tk.Label(p_f, textvariable=self.status_text, font=("Segoe UI", 8, "italic"), bg=THEME_PANEL_BG, fg=THEME_TEXT_MUTED)
        self.lbl_status.pack(anchor="w", pady=(0, 2))
        self.progress = ttk.Progressbar(p_f, style="Horizontal.TProgressbar", mode="determinate")
        self.progress.pack(fill="x")

        btn_f = tk.Frame(sc_inner, bg=THEME_PANEL_BG)
        btn_f.pack(side="right", anchor="e")

        # Bottom Action Buttons
        self.btn_out = self._create_custom_button(
            btn_f,
            text="📂 Open Output Folder",
            bg_color=THEME_CARD_BG,
            hover_color=THEME_BORDER,
            pressed_color=THEME_BORDER_LIGHT,
            fg_color=THEME_TEXT_PRIMARY,
            command=lambda: open_path(self.result.output_folder if self.result else None),
            disabled=True,
            padding_x=12,
            padding_y=4
        )
        self.btn_out.pack(side="left", padx=4)

        self.btn_html = self._create_custom_button(
            btn_f,
            text="📄 Open HTML Report",
            bg_color=THEME_CARD_BG,
            hover_color=THEME_BORDER,
            pressed_color=THEME_BORDER_LIGHT,
            fg_color=THEME_TEXT_PRIMARY,
            command=lambda: webbrowser.open(self.result.html_report if self.result else ""),
            disabled=True,
            padding_x=12,
            padding_y=4
        )
        self.btn_html.pack(side="left", padx=4)

        self.btn_backup = self._create_custom_button(
            btn_f,
            text="💾 Open Backup Folder",
            bg_color=THEME_CARD_BG,
            hover_color=THEME_BORDER,
            pressed_color=THEME_BORDER_LIGHT,
            fg_color=THEME_TEXT_PRIMARY,
            command=lambda: open_path(self.result.backup_folder if self.result else None),
            disabled=True,
            padding_x=12,
            padding_y=4
        )
        self.btn_backup.pack(side="left", padx=4)

        # Main Body Scrollable
        container = tk.Frame(self.root, bg=THEME_BG_DARK)
        container.pack(fill="both", expand=True)

        canvas = tk.Canvas(container, bg=THEME_BG_DARK, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview, style="Vertical.TScrollbar")
        
        self.scrollable_frame = tk.Frame(canvas, bg=THEME_BG_DARK)
        self.scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas_window = canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(canvas_window, width=e.width))
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        main_body = tk.Frame(self.scrollable_frame, bg=THEME_BG_DARK)
        main_body.pack(fill="both", expand=True, padx=20, pady=16)

        # File Selection Card
        f_card = tk.Frame(main_body, bg=THEME_PANEL_BG, highlightbackground=THEME_BORDER, highlightthickness=1)
        f_card.pack(fill="x", pady=(0, 14))
        f_inner = tk.Frame(f_card, bg=THEME_PANEL_BG)
        f_inner.pack(fill="x", padx=16, pady=12)

        tk.Label(f_inner, text="Dataset Source File:", font=("Segoe UI", 9, "bold"), bg=THEME_PANEL_BG, fg=THEME_TEXT_PRIMARY).pack(side="left", padx=(0, 10))
        self.entry_file = tk.Entry(f_inner, textvariable=self.file_path, font=("Consolas", 9), bg=THEME_CARD_BG, fg=THEME_TEXT_PRIMARY, insertbackground="white", relief="flat")
        self.entry_file.pack(side="left", fill="x", expand=True, padx=(0, 12), ipady=4)

        # Browse File Button (15-20% Wider + Effects)
        self.browse_btn = self._create_custom_button(
            f_inner,
            text="Browse File",
            bg_color=THEME_BLUE_ACCENT,
            hover_color=THEME_BLUE_HOVER,
            pressed_color=THEME_BLUE_PRESSED,
            fg_color="#FFFFFF",
            command=self.browse_file,
            padding_x=22,  # 15-20% width increase
            padding_y=5
        )
        self.browse_btn.pack(side="right")

        # Two Columns Split
        split_frame = tk.Frame(main_body, bg=THEME_BG_DARK)
        split_frame.pack(fill="both", expand=True)

        # Left Column (Cleaning Options Panel)
        left_col = tk.Frame(split_frame, bg=THEME_PANEL_BG, width=290, highlightbackground=THEME_BORDER, highlightthickness=1)
        left_col.pack(side="left", fill="y", padx=(0, 14))
        left_col.pack_propagate(False)

        lc_inner = tk.Frame(left_col, bg=THEME_PANEL_BG)
        lc_inner.pack(fill="both", expand=True, padx=16, pady=16)

        tk.Label(lc_inner, text="Cleaning Options", font=("Segoe UI", 10, "bold"), bg=THEME_PANEL_BG, fg=THEME_GOLD_ACCENT).pack(anchor="w", pady=(0, 12))
        
        tk.Label(lc_inner, text="Missing Strategy:", font=("Segoe UI", 8), bg=THEME_PANEL_BG, fg=THEME_TEXT_MUTED).pack(anchor="w")
        self.missing_cb = ttk.Combobox(lc_inner, values=["median", "mean", "drop"], state="readonly", font=("Segoe UI", 9))
        self.missing_cb.set("median")
        self.missing_cb.pack(fill="x", pady=(3, 12))

        tk.Label(lc_inner, text="Outliers Strategy (IQR):", font=("Segoe UI", 8), bg=THEME_PANEL_BG, fg=THEME_TEXT_MUTED).pack(anchor="w")
        self.outlier_cb = ttk.Combobox(lc_inner, values=["cap", "remove", "keep"], state="readonly", font=("Segoe UI", 9))
        self.outlier_cb.set("cap")
        self.outlier_cb.pack(fill="x", pady=(3, 16))

        self.clean_btn = self._create_custom_button(
            lc_inner,
            text="✦  Smart Auto Clean",
            bg_color=THEME_BLUE_ACCENT,
            hover_color=THEME_BLUE_HOVER,
            pressed_color=THEME_BLUE_PRESSED,
            fg_color="#FFFFFF",
            command=self.start_processing_thread,
            padding_x=10,
            padding_y=8
        )
        self.clean_btn.pack(fill="x", pady=(0, 18))

        # Profile Footer Info Box
        profile_box = tk.Frame(lc_inner, bg=THEME_CARD_BG, highlightbackground=THEME_BORDER, highlightthickness=1)
        profile_box.pack(fill="x", side="bottom")
        pb_inner = tk.Frame(profile_box, bg=THEME_CARD_BG)
        pb_inner.pack(fill="x", padx=10, pady=8)

        tk.Label(pb_inner, text="Current Cleaning Profile", font=("Segoe UI", 7, "bold"), bg=THEME_CARD_BG, fg=THEME_GOLD_ACCENT).pack(anchor="w")
        tk.Label(pb_inner, text="Enterprise Default (Balanced Clean)", font=("Segoe UI", 8), bg=THEME_CARD_BG, fg=THEME_TEXT_MUTED).pack(anchor="w")

        # Right Column
        right_col = tk.Frame(split_frame, bg=THEME_BG_DARK)
        right_col.pack(side="right", fill="both", expand=True)

        grid_frame = tk.Frame(right_col, bg=THEME_BG_DARK)
        grid_frame.pack(fill="x", pady=(0, 14))

        self.cards: Dict[str, tk.Label] = {}
        metrics_def = [
            ("Execution Time", "time", 2, 0),
            ("Memory Peak", "memory", 2, 1),
            ("Processing Speed", "speed", 2, 2),
        ]

        for title, key, r, c in metrics_def:
            card = tk.Frame(grid_frame, bg=THEME_CARD_BG, highlightbackground=THEME_BORDER, highlightthickness=1)
            card.grid(row=r, column=c, padx=3, pady=3, sticky="nsew")
            grid_frame.columnconfigure(c, weight=1)

            lbl_t = tk.Label(card, text=title.upper(), font=("Segoe UI", 7, "bold"), bg=THEME_CARD_BG, fg=THEME_TEXT_MUTED)
            lbl_t.pack(anchor="w", padx=8, pady=(4, 1))

            lbl_v = tk.Label(card, text="--", font=("Segoe UI", 10, "bold"), bg=THEME_CARD_BG, fg="#38BDF8")
            lbl_v.pack(anchor="w", padx=8, pady=(0, 4))
            self.cards[key] = lbl_v

        self.ai_panel = AIExecutiveAssistantPanel(right_col)
        self.ai_panel.pack(fill="both", expand=True)

    def _create_custom_button(
        self,
        parent: tk.Widget,
        text: str,
        bg_color: str,
        hover_color: str,
        pressed_color: str,
        fg_color: str,
        command: Callable[[], None],
        disabled: bool = False,
        padding_x: int = 12,
        padding_y: int = 6
    ) -> tk.Frame:
        """Helper button wrapper allowing precise enterprise hover/pressed effects."""
        wrapper = tk.Frame(parent, bg=bg_color, highlightbackground=THEME_BORDER if disabled else bg_color, highlightthickness=1)
        label = tk.Label(
            wrapper,
            text=text,
            font=("Segoe UI", 9, "bold"),
            bg=bg_color,
            fg=THEME_TEXT_MUTED if disabled else fg_color,
            padx=padding_x,
            pady=padding_y,
            cursor="arrow" if disabled else "hand2"
        )
        label.pack(fill="both", expand=True)

        def on_enter(e):
            if not getattr(wrapper, "is_disabled", False):
                wrapper.config(bg=hover_color, highlightbackground=hover_color)
                label.config(bg=hover_color)

        def on_leave(e):
            if not getattr(wrapper, "is_disabled", False):
                wrapper.config(bg=bg_color, highlightbackground=bg_color)
                label.config(bg=bg_color)

        def on_press(e):
            if not getattr(wrapper, "is_disabled", False):
                wrapper.config(bg=pressed_color, highlightbackground=pressed_color)
                label.config(bg=pressed_color)

        def on_release(e):
            if not getattr(wrapper, "is_disabled", False):
                wrapper.config(bg=hover_color, highlightbackground=hover_color)
                label.config(bg=hover_color)
                command()

        label.bind("<Enter>", on_enter)
        label.bind("<Leave>", on_leave)
        label.bind("<ButtonPress-1>", on_press)
        label.bind("<ButtonRelease-1>", on_release)

        wrapper.is_disabled = disabled
        wrapper.set_state = lambda state: self._set_button_state(wrapper, label, state, bg_color, fg_color)
        return wrapper

    def _set_button_state(self, wrapper: tk.Frame, label: tk.Label, state: str, bg_color: str, fg_color: str):
        if state == "disabled":
            wrapper.is_disabled = True
            wrapper.config(bg=THEME_PANEL_BG, highlightbackground=THEME_BORDER)
            label.config(bg=THEME_PANEL_BG, fg=THEME_TEXT_MUTED, cursor="arrow")
        else:
            wrapper.is_disabled = False
            wrapper.config(bg=bg_color, highlightbackground=bg_color)
            label.config(bg=bg_color, fg=fg_color, cursor="hand2")

    def browse_file(self) -> None:
        p = filedialog.askopenfilename(filetypes=[("Data Files", "*.csv;*.xlsx;*.xls;*.json")])
        if p:
            self.file_path.set(p)
            file_path_obj = Path(p)
            size_str = human_size(file_path_obj.stat().st_size) if file_path_obj.exists() else "N/A"
            self.ai_panel.set_state_dataset_loaded(file_path_obj.name, size_str)

    def update_progress(self, val: int, msg: str) -> None:
        self.root.after(0, lambda: (self.progress.configure(value=val), self.status_text.set(msg)))

    def start_processing_thread(self) -> None:
        p = self.file_path.get().strip()
        if not p:
            messagebox.showwarning("Warning", "Please select a dataset file first.")
            return
        
        self.clean_btn.set_state("disabled")
        for k in self.cards:
            self.cards[k].config(text="Processing...", fg=THEME_GOLD_ACCENT)

        threading.Thread(target=self._worker, args=(p,), daemon=True).start()

    def _worker(self, path: str) -> None:
        try:
            res = self.engine.clean_and_export(
                path,
                missing_strategy=self.missing_cb.get(),
                outlier_strategy=self.outlier_cb.get(),
                progress_callback=self.update_progress
            )
            self.result = res
            self.root.after(0, self._on_success)
        except SouaniUserError as e:
            self.root.after(0, lambda: messagebox.showerror("Data Processing Error", str(e)))
            self.root.after(0, lambda: self.status_text.set("Execution Failed."))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("System Error", f"Unexpected error encountered: {str(e)}"))
            self.root.after(0, lambda: self.status_text.set("System Error."))
        finally:
            self.root.after(0, lambda: self.clean_btn.set_state("normal"))

    def _on_success(self) -> None:
        if not self.result:
            return
        
        # Enable Bottom Action Buttons
        self.btn_out.set_state("normal")
        self.btn_html.set_state("normal")
        self.btn_backup.set_state("normal")

        s = self.result.stats

        # Animate Metrics Cards Smoothly
        self._animate_metric("time", f"{s['execution_time']} sec")
        self._animate_metric("memory", s['memory_usage'])
        self._animate_metric("speed", f"{s['speed_rps']} r/s")

        self.ai_panel.set_state_completed(self.result)

    def _animate_metric(self, key: str, final_text: str):
        label = self.cards[key]
        label.config(text=final_text, fg="#38BDF8")

    def show_about_dialog(self) -> None:
        dlg = tk.Toplevel(self.root)
        dlg.title(f"About - {PRODUCT_NAME}")
        dlg.geometry("520x420")
        dlg.configure(bg=THEME_PANEL_BG)
        dlg.resizable(False, False)

        p = tk.Frame(dlg, bg=THEME_PANEL_BG, padx=24, pady=20)
        p.pack(fill="both", expand=True)

        # Header Logo Badge
        logo_frame = tk.Frame(p, bg=THEME_CARD_BG, highlightbackground=THEME_GOLD_ACCENT, highlightthickness=1)
        logo_frame.pack(anchor="w", pady=(0, 10))
        tk.Label(
            logo_frame,
            text=" ⚡ SOUANI TECHNOLOGIES ",
            font=("Segoe UI", 9, "bold"),
            bg=THEME_CARD_BG,
            fg=THEME_GOLD_ACCENT,
            padx=8,
            pady=4
        ).pack()

        tk.Label(p, text=PRODUCT_NAME, font=("Segoe UI", 16, "bold"), bg=THEME_PANEL_BG, fg=THEME_TEXT_PRIMARY).pack(anchor="w")
        tk.Label(p, text=f"Version: {VERSION} | Build: {BUILD_NUMBER}", font=("Segoe UI", 9), bg=THEME_PANEL_BG, fg=THEME_GOLD_ACCENT).pack(anchor="w", pady=(2, 10))
        
        info = (
            f"Edition:        {EDITION}\n"
            f"Developer:      {COMPANY}\n"
            f"License:        {LICENSE_NAME}\n\n"
            f"GitHub Repository:\n  {GITHUB}\n\n"
            f"Official Website (Future Placeholder):\n  {WEBSITE}\n\n"
            f"© {datetime.now().year} {COMPANY}. All rights reserved."
        )
        tk.Label(p, text=info, font=("Consolas", 8), justify="left", bg=THEME_PANEL_BG, fg=THEME_TEXT_MUTED).pack(anchor="w")
        
        close_btn = self._create_custom_button(
            p,
            text="Close",
            bg_color=THEME_CARD_BG,
            hover_color=THEME_BORDER,
            pressed_color=THEME_BORDER_LIGHT,
            fg_color=THEME_TEXT_PRIMARY,
            command=dlg.destroy,
            padding_x=16,
            padding_y=4
        )
        close_btn.pack(anchor="e", pady=(10, 0))

    def run(self) -> None:
        self.root.mainloop()

if __name__ == "__main__":
    app = SouaniCleanerApp()
    app.run()