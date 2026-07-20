import os
import json
import logging
import re
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Tuple
from dataclasses import dataclass, field
import plotly.graph_objects as go
import plotly.io as pio

logging.basicConfig(level=logging.INFO, format="%(asctime)s — %(levelname)s — %(message)s")


# ── نموذج تقرير الورقة ─────────────────────────────────────────────────────
@dataclass
class SheetReport:
    file_name: str
    sheet_name: str
    rows_before: int
    rows_after: int
    columns: int
    duplicates_removed: int
    missing_before: int
    missing_after: int
    numeric_columns: List[str] = field(default_factory=list)
    text_columns:    List[str] = field(default_factory=list)
    date_columns:    List[str] = field(default_factory=list)
    outliers_detected: int = 0
    outliers_handled:  int = 0
    suggestions:     List[str] = field(default_factory=list)


# ── المحرك الرئيسي ─────────────────────────────────────────────────────────
class AdvancedDataCleaner:

    COMMON_NA_VALUES = [
        "n/a", "na", "--", "-", "null", "none",
        "missing", "?", "nan", " ", ""
    ]
    SUPPORTED_EXTENSIONS = {".csv", ".xlsx", ".xls", ".json"}
    DATE_KEYWORDS = ["date", "time", "year", "month", "day", "تاريخ", "سنة", "شهر"]
    
    # أنماط علامات التشكيل للغة العربية
    ARABIC_DIACRITICS = re.compile(r'[\u064B-\u0652]')

    def __init__(
        self,
        numeric_strategy: str = "median",
        outlier_strategy: str = "keep",
        backup: bool = True,
        overwrite: bool = False,
        recursive: bool = False,
    ):
        self.numeric_strategy  = numeric_strategy
        self.outlier_strategy  = outlier_strategy
        self.backup            = backup
        self.overwrite         = overwrite
        self.recursive         = recursive
        self.all_reports: List[SheetReport] = []

    # ── توليد الاقتراحات الذكية ────────────────────────────────────────────
    def generate_ai_suggestions(self, df: pd.DataFrame) -> List[str]:
        suggestions = []
        total_rows = len(df)

        if total_rows == 0:
            return ["⚠️ ملف البيانات فارغ تماماً، لا يوجد شيء لتحليله."]

        missing_counts = df.isna().sum()
        total_missing  = missing_counts.sum()
        if total_missing > 0:
            suggestions.append(f"🔍 عثرنا على {total_missing} قيمة مفقودة إجمالاً عبر الأعمدة.")
            for col, count in missing_counts.items():
                if count > 0:
                    pct = (count / total_rows) * 100
                    suggestions.append(f"  • العمود '{col}' يحتوي على {count} فراغ ({pct:.1f}%).")
        else:
            suggestions.append("✅ ممتاز! لا توجد أي قيم مفقودة في هذا الملف.")

        dup_count = df.duplicated().sum()
        if dup_count > 0:
            suggestions.append(f"🗑️ تم رصد {dup_count} سطر مكرر بالكامل. نقترح تصفيتها فوراً.")

        num_cols     = df.select_dtypes(include=[np.number]).columns
        outlier_found = False
        for col in num_cols:
            q1  = df[col].quantile(0.25)
            q3  = df[col].quantile(0.75)
            iqr = q3 - q1
            lb  = q1 - 1.5 * iqr
            ub  = q3 + 1.5 * iqr
            outliers = df[(df[col] < lb) | (df[col] > ub)]
            if len(outliers) > 0:
                if not outlier_found:
                    suggestions.append("📈 تحليل القيم الشاذة (Outliers):")
                    outlier_found = True
                suggestions.append(
                    f"  • العمود الرقمي '{col}' يحتوي على {len(outliers)} قيمة متطرفة."
                )
        return suggestions

    # ── أدوات مساعدة ───────────────────────────────────────────────────────
    def is_date_column(self, col: str) -> bool:
        return any(kw in col.lower() for kw in self.DATE_KEYWORDS)

    def try_clean_date_column(self, df: pd.DataFrame, col: str) -> Tuple[pd.DataFrame, bool]:
        try:
            converted = pd.to_datetime(df[col], errors="coerce", infer_datetime_format=True)
            if converted.notna().mean() >= 0.7:
                df[col] = converted
                return df, True
        except Exception:
            pass
        return df, False

    def clean_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        df.columns = (
            df.columns
            .str.strip()
            .str.replace(r"\s+", "_", regex=True)
            .str.replace(r"[^\w\u0600-\u06FF]", "", regex=True)
        )
        return df

    def clean_numeric_column(self, df: pd.DataFrame, col: str) -> pd.DataFrame:
        if df[col].isna().sum() == 0:
            return df
        if self.numeric_strategy == "median":
            df[col] = df[col].fillna(df[col].median())
        elif self.numeric_strategy == "mean":
            df[col] = df[col].fillna(df[col].mean())
        elif self.numeric_strategy == "zero":
            df[col] = df[col].fillna(0)
        return df

    def _normalize_arabic_text(self, text: str) -> str:
        """تطبيع وتطهير الحروف والنصوص العربية"""
        if pd.isna(text) or not isinstance(text, str):
            return text
        text = self.ARABIC_DIACRITICS.sub('', text)  # إزالة التشكيل
        text = re.sub(r'[أإآ]', 'ا', text)         # توحيد الألف
        text = re.sub(r'ة\b', 'ه', text)           # التاء المربوطة
        text = re.sub(r'ى\b', 'ي', text)           # الألف المقصورة
        text = re.sub(r'[^\w\s\u0600-\u06FF]', '', text) # حذف الرموز الغريبة
        return text.strip()

    def clean_text_column(self, df: pd.DataFrame, col: str) -> pd.DataFrame:
        df[col] = df[col].fillna("Unknown")
        if df[col].dtype == object:
            df[col] = df[col].astype(str).str.strip()
            # تطبيق المعالجة العربية
            df[col] = df[col].apply(self._normalize_arabic_text)
        return df

    def handle_outliers(
        self, df: pd.DataFrame
    ) -> Tuple[pd.DataFrame, int, int]:
        detected = 0
        handled  = 0
        num_cols = df.select_dtypes(include=[np.number]).columns
        for col in num_cols:
            q1  = df[col].quantile(0.25)
            q3  = df[col].quantile(0.75)
            iqr = q3 - q1
            lb  = q1 - 1.5 * iqr
            ub  = q3 + 1.5 * iqr
            mask = (df[col] < lb) | (df[col] > ub)
            count = int(mask.sum())
            detected += count
            if count > 0:
                if self.outlier_strategy == "cap":
                    df[col] = np.clip(df[col], lb, ub)
                    handled += count
                elif self.outlier_strategy == "remove":
                    df = df[~mask].copy()
                    handled += count
        return df, detected, handled

    def create_backup(self, file_path: Path) -> None:
        if not self.backup:
            return
        backup_dir = file_path.parent / "_backup"
        backup_dir.mkdir(exist_ok=True)
        ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
        dest = backup_dir / f"{file_path.stem}_{ts}{file_path.suffix}"
        import shutil
        shutil.copy2(file_path, dest)
        logging.info(f"Backup saved: {dest}")

    def safe_output_path(self, file_path: Path) -> Path:
        out = file_path.parent / f"{file_path.stem}_standardized{file_path.suffix}"
        if not self.overwrite and out.exists():
            ts  = datetime.now().strftime("%Y%m%d_%H%M%S")
            out = file_path.parent / f"{file_path.stem}_standardized_{ts}{file_path.suffix}"
        return out

    def generate_reports(self) -> None:
        """يولّد تقرير HTML تفاعلي مدمج لجميع الأوراق المعالجة."""
        if not self.all_reports:
            return
        r = self.all_reports[0]
        self._generate_interactive_dashboard(
            filename       = r.file_name,
            initial_rows   = r.rows_before,
            final_rows     = r.rows_after,
            dups           = r.duplicates_removed,
            init_missing   = r.missing_before,
            final_missing  = r.missing_after,
            outliers       = r.outliers_detected,
        )

    def process_dataframe(
        self,
        df: pd.DataFrame,
        file_name: str,
        sheet_name: str = "Data",
        smart_auto: bool = False,
    ) -> Tuple[pd.DataFrame, SheetReport]:

        rows_before    = len(df)
        cols_before    = len(df.columns)
        missing_before = int(df.isna().sum().sum())
        suggestions    = self.generate_ai_suggestions(df.copy())

        # ── التنظيف الذكي التلقائي بنقرة واحدة ────────────────────────────
        if smart_auto:
            missing_pct = df.isna().mean() * 100
            for col in list(df.columns):
                if missing_pct[col] >= 80:
                    df.drop(columns=[col], inplace=True)
            self.numeric_strategy = "median"
            self.outlier_strategy = "cap"

        df = self.clean_column_names(df)

        before_dedup     = len(df)
        df               = df.drop_duplicates().copy()
        duplicates_removed = before_dedup - len(df)

        date_columns, numeric_columns, text_columns = [], [], []

        for col in list(df.columns):
            if self.is_date_column(col):
                df, ok = self.try_clean_date_column(df, col)
                if ok:
                    date_columns.append(col)
                    continue
            if pd.api.types.is_numeric_dtype(df[col]):
                df = self.clean_numeric_column(df, col)
                numeric_columns.append(col)
            else:
                converted    = pd.to_numeric(df[col], errors="coerce")
                non_null     = df[col].notna().sum()
                numeric_ratio = converted.notna().sum() / max(non_null, 1)
                if non_null > 0 and numeric_ratio >= 0.85:
                    df[col] = converted
                    df       = self.clean_numeric_column(df, col)
                    numeric_columns.append(col)
                else:
                    df = self.clean_text_column(df, col)
                    text_columns.append(col)

        df, outliers_detected, outliers_handled = self.handle_outliers(df)
        missing_after = int(df.isna().sum().sum())

        report = SheetReport(
            file_name         = file_name,
            sheet_name        = sheet_name,
            rows_before       = rows_before,
            rows_after        = len(df),
            columns           = cols_before,
            duplicates_removed= duplicates_removed,
            missing_before    = missing_before,
            missing_after     = missing_after,
            numeric_columns   = numeric_columns,
            text_columns      = text_columns,
            date_columns      = date_columns,
            outliers_detected = outliers_detected,
            outliers_handled  = outliers_handled,
            suggestions       = suggestions,
        )
        return df, report

    def clean_file(self, file_path: Path, smart_auto: bool = False) -> Optional[Path]:
        file_path = Path(file_path)
        suffix    = file_path.suffix.lower()

        if suffix not in self.SUPPORTED_EXTENSIONS:
            logging.warning(f"Skipped unsupported file: {file_path}")
            return None

        self.create_backup(file_path)
        output_path = self.safe_output_path(file_path)
        logging.info(f"Cleaning file: {file_path}")

        if suffix == ".csv":
            df = pd.read_csv(file_path, na_values=self.COMMON_NA_VALUES, keep_default_na=True)
            cleaned, report = self.process_dataframe(df, file_path.name, "CSV", smart_auto)
            cleaned.to_csv(output_path, index=False, encoding="utf-8-sig")
            self.all_reports.append(report)

        elif suffix in {".xlsx", ".xls"}:
            sheets = pd.read_excel(file_path, sheet_name=None, na_values=self.COMMON_NA_VALUES, keep_default_na=True)
            with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
                for sheet_name, df in sheets.items():
                    cleaned, report = self.process_dataframe(df, file_path.name, str(sheet_name), smart_auto)
                    safe_sheet = str(sheet_name)[:31] or "Sheet1"
                    cleaned.to_excel(writer, sheet_name=safe_sheet, index=False)
                    self.all_reports.append(report)

        elif suffix == ".json":
            df = pd.read_json(file_path)
            df.replace(self.COMMON_NA_VALUES, pd.NA, inplace=True)
            cleaned, report = self.process_dataframe(df, file_path.name, "JSON", smart_auto)
            cleaned.to_json(output_path, orient="records", indent=4, force_ascii=False)
            self.all_reports.append(report)

        logging.info(f"Saved cleaned file: {output_path}")
        return output_path

    def clean_target(self, target_path: str, smart_auto: bool = False) -> List[Path]:
        path = Path(target_path)
        if not path.exists():
            raise FileNotFoundError(f"Target not found: {path}")

        cleaned_files: List[Path] = []
        self.all_reports = []

        if path.is_file():
            out = self.clean_file(path, smart_auto)
            if out:
                cleaned_files.append(out)
        else:
            iterator = path.rglob("*") if self.recursive else path.glob("*")
            for item in iterator:
                if item.is_file() and item.suffix.lower() in self.SUPPORTED_EXTENSIONS:
                    if "standardized" in item.stem.lower():
                        continue
                    out = self.clean_file(item, smart_auto)
                    if out:
                        cleaned_files.append(out)

        if self.all_reports:
            self.generate_reports()

        return cleaned_files

    # ── لوحة التحكم التفاعلية ───────────────────────────────────────────
    def _generate_interactive_dashboard(
        self,
        filename: str,
        initial_rows: int,
        final_rows: int,
        dups: int,
        init_missing: int,
        final_missing: int,
        outliers: int,
    ) -> None:
        os.makedirs("Reports", exist_ok=True)
        timestamp   = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        report_stem = Path(filename).stem

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=["عدد الصفوف", "القيم المفقودة"],
            y=[initial_rows, init_missing],
            name="قبل التنظيف 🛑",
            marker_color="#e74c3c",
        ))
        fig.add_trace(go.Bar(
            x=["عدد الصفوف", "القيم المفقودة"],
            y=[final_rows, final_missing],
            name="بعد التنظيف القياسي 🟢",
            marker_color="#2ecc71",
        ))
        fig.update_layout(
            title=dict(text=f"مقارنة كفاءة تنظيف البيانات لملف: {filename}", x=0.5, xanchor="center"),
            barmode="group",
            template="plotly_white",
            font=dict(family="Segoe UI", size=14),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        plotly_html = pio.to_html(fig, full_html=False, include_plotlyjs="cdn")

        dashboard_html = f"""<!DOCTYPE html>
<html lang='ar' dir='rtl'>
<head>
<meta charset='UTF-8'>
<meta name='viewport' content='width=device-width, initial-scale=1.0'>
<title>Souani Interactive Dashboard v3.2</title>
<style>
  body {{ font-family:'Segoe UI',Tahoma,sans-serif; margin:0; background:#f4f7fb; color:#172033; }}
  header {{ background:linear-gradient(135deg,#0b2545,#0066cc); color:white; padding:25px; text-align:center; }}
  header h1 {{ margin:0; font-size:28px; }}
  main {{ max-width:1100px; margin:24px auto; padding:0 20px; }}
  .grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:15px; margin-bottom:25px; }}
  .card {{ background:white; border-radius:12px; padding:20px; box-shadow:0 6px 15px rgba(0,0,0,.05); border:1px solid #e4ebf3; text-align:center; }}
  .card span {{ color:#617086; font-size:14px; font-weight:bold; }}
  .card b {{ display:block; font-size:32px; color:#0b66c3; margin-top:8px; }}
  .chart-container {{ background:white; border-radius:16px; padding:20px; box-shadow:0 8px 22px rgba(0,0,0,.06); border:1px solid #e4ebf3; margin-bottom:30px; }}
  footer {{ text-align:center; color:#748399; padding:20px; font-size:12px; }}
</style>
</head>
<body>
<header>
  <h1>📊 Souani Data Cleaner — لوحة التحكم التفاعلية</h1>
  <p>تم التوليد الذكي للتقرير في: {timestamp}</p>
</header>
<main>
  <div class='grid'>
    <div class='card'><span>الأسطر المحذوفة (تكرار)</span><b>{dups}</b></div>
    <div class='card'><span>القيم الشاذة المكتشفة</span><b>{outliers}</b></div>
    <div class='card'><span>حالة الفراغات الرقمية</span><b>{self.numeric_strategy}</b></div>
    <div class='card'><span>إستراتيجية المتطرفات</span><b>{self.outlier_strategy}</b></div>
  </div>
  <div class='chart-container'>
    {plotly_html}
  </div>
</main>
<footer>Souani Data Cleaner v3.2 — لوحة تفاعلية مدعومة بـ Plotly</footer>
</body>
</html>"""

        report_path = f"Reports/Dashboard_{report_stem}.html"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(dashboard_html)

        report_data = {
            "file_processed":   filename,
            "timestamp":        timestamp,
            "initial_rows":     initial_rows,
            "final_rows":       final_rows,
            "duplicates_removed": dups,
            "outliers_detected":  outliers,
        }
        with open(f"Reports/report_{report_stem}.json", "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=4, ensure_ascii=False)

        logging.info(f"Dashboard saved: {report_path}")