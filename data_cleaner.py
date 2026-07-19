import pandas as pd
import os
import logging
import argparse
import shutil
from datetime import datetime
from pathlib import Path

# إعداد نظام الـ Logging القياسي
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("cleaning_log.txt", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

class AdvancedDataCleaner:
    SUPPORTED_EXTENSIONS = [".csv", ".xlsx", ".xls", ".json"]
    COMMON_NA_VALUES = ["", " ", "nan", "NaN", "none", "None", "null", "Null", "missing", "Missing", "N/A", "n/a", "NA", "-", "--"]

    def __init__(self, numeric_strategy="median"):
        self.numeric_strategy = numeric_strategy
        self.backup_dir = Path("Backup")
        self.backup_dir.mkdir(exist_ok=True)
        self.last_backup = None

    def clean_filename(self, path: Path) -> Path:
        """تنظيف وتوحيد أسماء الملفات استناداً للمقاييس"""
        clean_name = path.name.replace(" ", "_")
        clean_path = path.parent / clean_name
        if path.exists() and path != clean_path:
            os.rename(path, clean_path)
            logging.info(f"تم تنظيف اسم الملف من '{path.name}' إلى '{clean_name}'")
            return clean_path
        return path

    def create_backup(self, file_path: Path):
        """إنشاء نسخة احتياطية في مجلد Backup قبل أي تعديل"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.backup_dir / f"{file_path.stem}_{timestamp}{file_path.suffix}"
        shutil.copy(file_path, backup_file)
        self.last_backup = (file_path, backup_file)
        logging.info(f"تم إنشاء نسخة احتياطية للملف الأصلي في: {backup_file}")

    def undo_last_operation(self):
        """إمكانية استعادة الملف الأصلي (Undo / Restore)"""
        if self.last_backup and self.last_backup[1].exists():
            original, backup = self.last_backup
            shutil.copy(backup, original)
            logging.info(f"تمت استعادة الملف الأصلي بنجاح من النسخة الاحتياطية: {original}")
            return True
        logging.warning("لا توجد عمليات سابقة متاحة للاستعادة.")
        return False

    def generate_html_report(self, report_data):
        """إنشاء تقرير HTML احترافي (Cleaning_Report.html)"""
        html_content = f"""
        <!DOCTYPE html>
        <html lang="ar" dir="rtl">
        <head>
            <meta charset="UTF-8">
            <title>تقرير تنظيف البيانات القياسي</title>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f6f9; color: #333; padding: 20px; }}
                .container {{ max-width: 900px; background: white; margin: auto; padding: 30px; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }}
                h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
                .meta {{ font-size: 0.9em; color: #7f8c8d; margin-bottom: 20px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 20px; background: #fff; }}
                th, td {{ border: 1px solid #ddd; padding: 12px; text-align: right; }}
                th {{ background-color: #3498db; color: white; }}
                tr:nth-child(even) {{ background-color: #f9f9f9; }}
                .badge {{ background: #2ecc71; color: white; padding: 4px 8px; border-radius: 4px; font-size: 0.85em; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>📊 تقرير تنظيف البيانات - Souani Data Cleaner</h1>
                <div class="meta">
                    <p><strong>اسم الملف المعالج:</strong> {report_data['file_name']}</p>
                    <p><strong>وقت التنفيذ الكامل:</strong> {report_data['exec_time']}</p>
                </div>
                <h2>📈 الملخص الإحصائي لكل ورقة (Sheet)</h2>
                <table>
                    <thead>
                        <tr>
                            <th>اسم الورقة / الملف</th>
                            <th>عدد الصفوف</th>
                            <th>عدد الأعمدة</th>
                            <th>التكرارات المحذوفة</th>
                            <th>إجمالي القيم الفارغة المعالجة</th>
                            <th>نوع الاستراتيجية الرقمية</th>
                        </tr>
                    </thead>
                    <tbody>
        """
        for sheet_name, metrics in report_data['sheets'].items():
            html_content += f"""
                        <tr>
                            <td>{sheet_name}</td>
                            <td>{metrics['rows']}</td>
                            <td>{metrics['cols']}</td>
                            <td><span class="badge">{metrics['dup_removed']}</span></td>
                            <td>{metrics['nulls_filled']}</td>
                            <td>{self.numeric_strategy}</td>
                        </tr>
            """
        
        html_content += """
                    </tbody>
                </table>
            </div>
        </body>
        </html>
        """
        with open("Cleaning_Report.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        logging.info("تم تصدير تقرير HTML الاحترافي بنجاح باسم 'Cleaning_Report.html'")

    def process_dataframe(self, df: pd.DataFrame) -> tuple:
        """تنظيف ورقة بيانات واحدة وإرجاع المقاييس والـ DF المنظف"""
        metrics = {"rows": df.shape[0], "cols": df.shape[1], "dup_removed": 0, "nulls_filled": 0}
        
        # 1. إزالة التكرارات
        initial_rows = len(df)
        df.drop_duplicates(inplace=True)
        metrics["dup_removed"] = initial_rows - len(df)

        # 2. تنظيف الأعمدة
        for col in df.columns:
            metrics["nulls_filled"] += int(df[col].isna().sum())
            if df[col].dtype == 'object' or str(df[col].dtype).startswith('str'):
                df[col] = df[col].astype(str).str.strip().replace(["nan", "None", "<NA>", "N/A", ""], pd.NA).fillna("N/A")
            elif 'date' in str(col).lower() or 'time' in str(col).lower():
                try:
                    df[col] = pd.to_datetime(df[col], errors='coerce').dt.strftime("%Y-%m-%d")
                except Exception: pass
            else:
                if self.numeric_strategy == "zero": df[col] = df[col].fillna(0)
                elif self.numeric_strategy == "mean": df[col] = df[col].fillna(df[col].mean())
                elif self.numeric_strategy == "median": df[col] = df[col].fillna(df[col].median())

        return df, metrics

    def clean_single_file(self, file_path: Path) -> dict:
        """تنظيف ملف فردي مع دعم تعدد الـ Sheets لملفات الإكسل"""
        file_path = self.clean_filename(file_path)
        if file_path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
            return None

        self.create_backup(file_path)
        file_ext = file_path.suffix.lower()
        output_path = file_path.parent / f"{file_path.stem}_standardized{file_ext}"
        file_report = {"file_name": file_path.name, "exec_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "sheets": {}}

        try:
            if file_ext in [".xlsx", ".xls"]:
                excel_file = pd.ExcelFile(file_path)
                with pd.ExcelWriter(output_path) as writer:
                    for sheet_name in excel_file.sheet_names:
                        df = pd.read_excel(file_path, sheet_name=sheet_name, na_values=self.COMMON_NA_VALUES)
                        cleaned_df, metrics = self.process_dataframe(df)
                        cleaned_df.to_excel(writer, sheet_name=sheet_name, index=False)
                        file_report["sheets"][sheet_name] = metrics
            else:
                if file_ext == ".csv":
                    df = pd.read_csv(file_path, na_values=self.COMMON_NA_VALUES, encoding="utf-8-sig")
                elif file_ext == ".json":
                    df = pd.read_json(file_path)
                    df.replace(self.COMMON_NA_VALUES, pd.NA, inplace=True)
                
                cleaned_df, metrics = self.process_dataframe(df)
                if file_ext == ".csv": cleaned_df.to_csv(output_path, index=False, encoding="utf-8-sig")
                elif file_ext == ".json": cleaned_df.to_json(output_path, orient='records', indent=4, force_ascii=False)
                file_report["sheets"]["الرئيسية"] = metrics

            logging.info(f"تم حفظ الملف المُنظف بنجاح في: {output_path}")
            return file_report
        except Exception as e:
            logging.error(f"خطأ أثناء معالجة الملف {file_path.name}: {e}")
            return None

    def clean_target(self, target_path: str):
        """دعم معالجة ملف واحد أو مجلد كامل يحتوي على ملفات متعددة"""
        path = Path(target_path)
        if not path.exists():
            logging.error(f"المسار المحدد غير موجود: {target_path}")
            return

        aggregated_report = {"file_name": path.name, "exec_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "sheets": {}}

        if path.is_dir():
            logging.info(f"بدء تنظيف مجلد كامل يحتوي على ملفات متعددة: {path.name}")
            for item in path.iterdir():
                if item.is_file() and item.suffix.lower() in self.SUPPORTED_EXTENSIONS and "standardized" not in item.name:
                    res = self.clean_single_file(item)
                    if res:
                        for sheet_key, metrics in res["sheets"].items():
                            aggregated_report["sheets"][f"{item.name} -> {sheet_key}"] = metrics
        else:
            res = self.clean_single_file(path)
            if res: aggregated_report = res

        if aggregated_report["sheets"]:
            self.generate_html_report(aggregated_report)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Souani Data Cleaner Engine (PRD-PDS-0001)")
    parser.add_argument("target", help="مسار الملف الفردي أو المجلد الكامل لتنظيفه")
    parser.add_argument("--strategy", choices=["zero", "mean", "median", "keep"], default="median", help="استراتيجية تنظيف الأرقام المفقودة")
    args = parser.parse_args()

    cleaner = AdvancedDataCleaner(numeric_strategy=args.strategy)
    cleaner.clean_target(args.target)