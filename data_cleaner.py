import pandas as pd
import numpy as np
from pathlib import Path
import os
import shutil

class AdvancedDataCleaner:
    def __init__(self, numeric_strategy="median"):
        self.numeric_strategy = numeric_strategy
        self.backup_dir = Path("Backup")
        self.backup_dir.mkdir(exist_ok=True)
        self.last_backup = None
        self.last_target_path = None

    def generate_ai_suggestions(self, df):
        """
        تحليل ذكي Rule-Based لتقديم اقتراحات جودة البيانات المحسّنة وآمنة تماماً.
        """
        suggestions = []

        if df is None or df.empty:
            return ["⚠️ لا توجد بيانات كافية لتحليل الجودة."]

        total_rows = len(df)
        total_cols = len(df.columns)

        suggestions.append(f"📊 تم تحليل ملف يحتوي على {total_rows} صف و {total_cols} عمود.")

        # 1. فحص القيم المفقودة
        missing_counts = df.isnull().sum()
        missing_percentages = df.isnull().mean() * 100

        for col in df.columns:
            missing_count = int(missing_counts[col])
            pct = float(missing_percentages[col])

            if pct >= 80:
                suggestions.append(
                    f"🚨 العمود '{col}' يحتوي على {pct:.1f}% قيم مفقودة ({missing_count} قيمة). قد يكون من الأفضل حذفه."
                )
            elif pct >= 50:
                suggestions.append(
                    f"⚠️ العمود '{col}' يحتوي على {pct:.1f}% قيم مفقودة. راجعه قبل الاعتماد عليه في التحليل."
                )
            elif pct > 0:
                suggestions.append(
                    f"💡 العمود '{col}' يحتوي على {pct:.1f}% قيم فارغة ({missing_count} قيمة). سيتم التعامل معها حسب استراتيجية التنظيف."
                )

        # 2. فحص التكرارات
        duplicate_count = int(df.duplicated().sum())
        if duplicate_count > 0:
            suggestions.append(
                f"👥 يوجد {duplicate_count} صف مكرر بالكامل. إزالتها ستساعد على تحسين دقة التحليل."
            )

        # 3. فحص القيم الشاذة للأعمدة الرقمية
        numeric_cols = df.select_dtypes(include=["number"]).columns

        for col in numeric_cols:
            series = df[col].dropna()

            if len(series) < 10:
                continue

            q1 = series.quantile(0.25)
            q3 = series.quantile(0.75)
            iqr = q3 - q1

            if iqr == 0:
                continue

            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr

            outlier_count = int(((series < lower_bound) | (series > upper_bound)).sum())

            if outlier_count > 0:
                pct = (outlier_count / len(series)) * 100
                suggestions.append(
                    f"🚨 العمود الرقمي '{col}' يحتوي على {outlier_count} قيمة شاذة ({pct:.1f}%). راجعها قبل التحليل المالي أو الإحصائي."
                )

        # 4. فحص الأعمدة النصية ذات القيم المتنوعة جدًا
        text_cols = df.select_dtypes(include=["object", "string"]).columns

        for col in text_cols:
            unique_count = df[col].nunique(dropna=True)

            if total_rows > 0:
                unique_ratio = unique_count / total_rows

                if unique_ratio > 0.9 and total_rows >= 20:
                    suggestions.append(
                        f"🔎 العمود النصي '{col}' يحتوي على قيم فريدة كثيرة جدًا. قد يكون معرفًا ID أو بيانات تحتاج مراجعة."
                    )

        if len(suggestions) == 1:
            suggestions.append("✨ تهانينا! البيانات تبدو نظيفة جدًا ولا توجد ملاحظات حرجة.")

        return suggestions

    def create_backup(self, file_path):
        """توليد نسخة احتياطية مشفرة زمنياً للملف الأصلي"""
        path = Path(file_path)
        if path.is_file():
            timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"data_{timestamp}.csv"
            backup_path = self.backup_dir / backup_name
            shutil.copy(path, backup_path)
            self.last_backup = backup_path
            self.last_target_path = path

    def clean_target(self, target_path):
        path = Path(target_path)
        if path.is_file():
            self.create_backup(path)
            
            # قراءة البيانات حسب النوع
            if path.suffix == '.csv':
                df = pd.read_csv(path)
            elif path.suffix in ['.xlsx', '.xls']:
                df = pd.read_excel(path)
            elif path.suffix == '.json':
                df = pd.read_json(path)
            else:
                raise ValueError("امتداد الملف غير مدعوم حالياً!")

            # الفحص وتوليد اقتراحات الـ AI قبل البدء بالتنظيف الفعلي
            ai_suggestions = self.generate_ai_suggestions(df.copy())

            # عمليات التنظيف والمعالجة الأساسية
            # 1. إزالة التكرارات
            df.drop_duplicates(inplace=True)

            # 2. ملء القيم الفارغة في الأعمدة الرقمية حسب الاستراتيجية المختارة
            numeric_cols = df.select_dtypes(include=['number']).columns
            for col in numeric_cols:
                if df[col].isnull().any():
                    if self.numeric_strategy == "median":
                        df[col].fillna(df[col].median(), inplace=True)
                    elif self.numeric_strategy == "mean":
                        df[col].fillna(df[col].mean(), inplace=True)
                    elif self.numeric_strategy == "zero":
                        df[col].fillna(0, inplace=True)

            # حفظ الملف النظيف مكانه
            if path.suffix == '.csv':
                df.to_csv(path, index=False)
            elif path.suffix in ['.xlsx', '.xls']:
                df.to_excel(path, index=False)
            elif path.suffix == '.json':
                df.to_json(path, orient='records', indent=4)

            # توليد تقرير HTML يتضمن اقتراحات الـ AI
            self.generate_html_report(path.name, ai_suggestions)
            
        elif path.is_dir():
            for sub_file in path.glob("*.*"):
                if sub_file.suffix in ['.csv', '.xlsx', '.xls', '.json']:
                    self.clean_target(sub_file)

    def generate_html_report(self, filename, ai_suggestions):
        """توليد تقرير HTML متكامل واحترافي مدعوم بـ AI"""
        suggestions_html = "".join([f"<li>{sug}</li>" for sug in ai_suggestions])
        
        report_content = f"""
        <!DOCTYPE html>
        <html lang="ar" dir="rtl">
        <head>
            <meta charset="UTF-8">
            <title>تقرير تطهير جودة البيانات الذكي</title>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f5f6fa; color: #333; margin: 30px; }}
                .container {{ max-width: 800px; background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); margin: auto; }}
                h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
                .meta {{ font-size: 14px; color: #7f8c8d; margin-bottom: 20px; }}
                .ai-box {{ background-color: #ebf5fb; border-right: 5px solid #3498db; padding: 15px; border-radius: 6px; margin-bottom: 20px; }}
                .ai-box h3 {{ margin-top: 0; color: #2980b9; }}
                ul {{ padding-right: 20px; line-height: 1.8; }}
                li {{ margin-bottom: 8px; }}
                .footer {{ margin-top: 30px; text-align: center; font-size: 12px; color: #95a5a6; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>📊 تقرير جودة وتطهير البيانات الذكي</h1>
                <div class="meta">الملف المعالج: <strong>{filename}</strong> | تاريخ المعالجة: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
                
                <div class="ai-box">
                    <h3>🧠 التقرير الإحصائي واقتراحات الذكاء الاصطناعي (AI):</h3>
                    <ul>
                        {suggestions_html}
                    </ul>
                </div>
                
                <p>✅ تم تطبيق قواعد التنظيف الآلي، تحديث الفراغات الرقمية بنجاح، وتأمين وحذف الملفات المكررة بالكامل.</p>
                <div class="footer">Souani Data Cleaner v3.0 (PRD-PDS-0001) - جميع الحقوق محفوظة لشركتك الناشئة.</div>
            </div>
        </body>
        </html>
        """
        with open("Cleaning_Report.html", "w", encoding="utf-8") as f:
            f.write(report_content)

    def undo_last_operation(self):
        """التراجع الفوري واستعادة الملف الأصلي"""
        if self.last_backup and self.last_backup.is_file() and self.last_target_path:
            shutil.copy(self.last_backup, self.last_target_path)
            return True
        return False