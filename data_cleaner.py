import os
import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import plotly.graph_objects as go
import plotly.io as pio

class AdvancedDataCleaner:
    COMMON_NA_VALUES = ["n/a", "na", "--", "-", "null", "none", "missing", "?", "nan", " ", ""]

    def __init__(self, numeric_strategy="median", outlier_strategy="keep", backup=True, overwrite=False):
        self.numeric_strategy = numeric_strategy
        self.outlier_strategy = outlier_strategy
        self.backup = backup
        self.overwrite = overwrite

    def generate_ai_suggestions(self, df):
        suggestions = []
        total_rows = len(df)
        
        if total_rows == 0:
            return ["⚠️ ملف البيانات فارغ تماماً، لا يوجد شيء لتحليله."]

        missing_counts = df.isna().sum()
        total_missing = missing_counts.sum()
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

        num_cols = df.select_dtypes(include=[np.number]).columns
        outlier_found = False
        for col in num_cols:
            q1 = df[col].quantile(0.25)
            q3 = df[col].quantile(0.75)
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
            if len(outliers) > 0:
                if not outlier_found:
                    suggestions.append("📈 تحليل القيم الشاذة (Outliers):")
                    outlier_found = True
                suggestions.append(f"  • العمود الرقمي '{col}' يحتوي على {len(outliers)} قيمة متطرفة خارج الحدود الطبيعية.")

        return suggestions

    def clean_target(self, path_str):
        path = Path(path_str)
        cleaned_paths = []
        
        if path.is_file():
            cleaned_file = self._clean_single_file(path)
            if cleaned_file:
                cleaned_paths.append(str(cleaned_file))
        else:
            raise ValueError("المسار المحدد ليس ملفاً صالحاً.")
            
        return cleaned_paths

    def _clean_single_file(self, path):
        suffix = path.suffix.lower()
        
        if suffix == ".csv":
            df = pd.read_csv(path, na_values=self.COMMON_NA_VALUES, keep_default_na=True)
        elif suffix in [".xlsx", ".xls"]:
            df = pd.read_excel(path, na_values=self.COMMON_NA_VALUES, keep_default_na=True)
        elif suffix == ".json":
            df = pd.read_json(path)
            df.replace(self.COMMON_NA_VALUES, pd.NA, inplace=True)
        else:
            return None

        initial_rows = len(df)
        initial_missing = int(df.isna().sum().sum())
        
        # 1. إزالة التكرارات
        df.drop_duplicates(inplace=True)
        rows_after_dups = len(df)
        dups_removed = initial_rows - rows_after_dups

        # 2. معالجة القيم المفقودة الرقمية
        num_cols = df.select_dtypes(include=[np.number]).columns
        for col in num_cols:
            if df[col].isna().sum() > 0:
                if self.numeric_strategy == "median":
                    df[col] = df[col].fillna(df[col].median())
                elif self.numeric_strategy == "mean":
                    df[col] = df[col].fillna(df[col].mean())
                elif self.numeric_strategy == "zero":
                    df[col] = df[col].fillna(0)

        # 3. معالجة القيم المفقودة النصية
        obj_cols = df.select_dtypes(include=["object"]).columns
        for col in obj_cols:
            df[col] = df[col].fillna("Unknown")

        # 4. معالجة وحساب القيم الشاذة المتأثرة بالفحص
        outliers_detected = 0
        for col in num_cols:
            q1 = df[col].quantile(0.25)
            q3 = df[col].quantile(0.75)
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            
            mask = (df[col] < lower_bound) | (df[col] > upper_bound)
            outliers_detected += int(mask.sum())
            
            if self.outlier_strategy == "cap":
                df[col] = np.clip(df[col], lower_bound, upper_bound)
            elif self.outlier_strategy == "remove":
                df = df[(df[col] >= lower_bound) & (df[col] <= upper_bound)]

        final_rows = len(df)
        final_missing = int(df.isna().sum().sum())

        out_dir = path.parent
        out_name = f"{path.stem}_standardized{path.suffix}"
        out_path = out_dir / out_name
        
        if suffix == ".csv":
            df.to_csv(out_path, index=False)
        elif suffix in [".xlsx", ".xls"]:
            df.to_excel(out_path, index=False)
        elif suffix == ".json":
            df.to_json(out_path, orient="records", indent=4)

        # توليد لوحة التحكم التفاعلية
        self._generate_interactive_dashboard(
            path.name, initial_rows, final_rows, dups_removed, 
            initial_missing, final_missing, outliers_detected
        )
        
        return out_path

    def _generate_interactive_dashboard(self, filename, initial_rows, final_rows, dups, init_missing, final_missing, outliers):
        os.makedirs("Reports", exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        report_stem = Path(filename).stem

        # 1. رسم بياني تفاعلي لمقارنة حجم الصفوف والقيم المفقودة (قبل وبعد)
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=['عدد الصفوف', 'القيم المفقودة'],
            y=[initial_rows, init_missing],
            name='قبل التنظيف 🛑',
            marker_color='#e74c3c'
        ))
        fig.add_trace(go.Bar(
            x=['عدد الصفوف', 'القيم المفقودة'],
            y=[final_rows, final_missing],
            name='بعد التنظيف القياسي  🟢',
            marker_color='#2ecc71'
        ))
        
        fig.update_layout(
            title=f'مقارنة كفاءة تنظيف البيانات لملف: {filename}',
            barmode='group',
            template='plotly_white',
            font=dict(family="Segoe UI", size=14),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )

        # تحويل الرسم البياني التفاعلي إلى كود HTML مستقل
        plotly_html = pio.to_html(fig, full_html=False, include_plotlyjs='cdn')

        # 2. بناء هيكل الـ HTML الكامل مدمجاً بـ لوحة التحكم التفاعلية
        dashboard_html = f"""<!DOCTYPE html>
<html lang='ar' dir='rtl'>
<head>
<meta charset='UTF-8'>
<meta name='viewport' content='width=device-width, initial-scale=1.0'>
<title>Souani Interactive Dashboard v3.2</title>
<style>
  body {{ font-family: 'Segoe UI', Tahoma, sans-serif; margin:0; background:#f4f7fb; color:#172033; }}
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
  <!-- ملخص البطاقات السريعة -->
  <div class='grid'>
    <div class='card'><span>الأسطر المحذوفة (تكرار)</span><b>{dups}</b></div>
    <div class='card'><span>القيم الشاذة المكتشفة</span><b>{outliers}</b></div>
    <div class='card'><span>حالة الفراغات الرقمية</span><b>{self.numeric_strategy}</b></div>
    <div class='card'><span>إستراتيجية المتطرفات</span><b>{self.outlier_strategy}</b></div>
  </div>

  <!-- الرسم البياني التفاعلي من Plotly -->
  <div class='chart-container'>
    {plotly_html}
  </div>
</main>
<footer>Souani Data Cleaner v3.2 — لوحة تفاعلية مدعومة بـ Plotly</footer>
</body>
</html>"""

        # حفظ التقرير التفاعلي النهائي
        report_path = f"Reports/Dashboard_{report_stem}.html"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(dashboard_html)
            
        # حفظ نسخة الـ JSON التوثيقية كالعادة
        report_data = {
            "file_processed": filename,
            "timestamp": timestamp,
            "initial_rows": initial_rows,
            "final_rows": final_rows,
            "duplicates_removed": dups,
            "outliers_detected": outliers
        }
        with open(f"Reports/report_{report_stem}.json", "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=4, ensure_ascii=False)