import pandas as pd
import os
import logging
from datetime import datetime
from pathlib import Path

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

    COMMON_NA_VALUES = [
        "", " ", "nan", "NaN", "none", "None", "null", "Null",
        "missing", "Missing", "N/A", "n/a", "NA", "-", "--"
    ]

    def __init__(self, file_path, numeric_strategy="median"):
        """
        numeric_strategy:
        - 'zero'   : fill numeric missing values with 0
        - 'mean'   : fill with column mean
        - 'median' : fill with column median
        - 'keep'   : keep missing values
        """
        self.file_path = Path(file_path)
        self.df = None
        self.file_ext = self.file_path.suffix.lower()
        self.numeric_strategy = numeric_strategy
        self.report = {
            "input_file": str(self.file_path),
            "started_at": datetime.now().astimezone().isoformat(),
            "original_shape": None,
            "final_shape": None,
            "duplicates_removed": 0,
            "columns_processed": [],
            "warnings": []
        }

    def validate_file(self):
        if not self.file_path.exists():
            logging.error(f"الملف غير موجود: {self.file_path}")
            return False

        if self.file_ext not in self.SUPPORTED_EXTENSIONS:
            logging.error(f"صيغة الملف غير مدعومة: {self.file_ext}")
            return False

        return True

    def load_data(self):
        """تحميل البيانات من CSV / Excel / JSON"""
        if not self.validate_file():
            return False

        try:
            if self.file_ext == ".csv":
                self.df = pd.read_csv(
                    self.file_path,
                    keep_default_na=True,
                    na_values=self.COMMON_NA_VALUES,
                    encoding="utf-8-sig"
                )

            elif self.file_ext in [".xlsx", ".xls"]:
                self.df = pd.read_excel(
                    self.file_path,
                    keep_default_na=True,
                    na_values=self.COMMON_NA_VALUES
                )

            elif self.file_ext == ".json":
                self.df = pd.read_json(self.file_path)
                self.df.replace(self.COMMON_NA_VALUES, pd.NA, inplace=True)

            self.report["original_shape"] = self.df.shape
            logging.info(f"تم تحميل الملف بنجاح. الحجم: {self.df.shape}")
            return True

        except UnicodeDecodeError:
            try:
                self.df = pd.read_csv(
                    self.file_path,
                    keep_default_na=True,
                    na_values=self.COMMON_NA_VALUES,
                    encoding="latin1"
                )
                self.report["original_shape"] = self.df.shape
                logging.warning("تم استخدام ترميز latin1 بسبب فشل utf-8.")
                return True
            except Exception as e:
                logging.error(f"فشل تحميل CSV بترميز بديل: {e}")
                return False

        except Exception as e:
            logging.error(f"فشل تحميل الملف: {e}")
            return False

    def clean_column_names(self):
        """توحيد أسماء الأعمدة"""
        original_columns = list(self.df.columns)

        self.df.columns = (
            self.df.columns
            .astype(str)
            .str.strip()
            .str.replace(r"\s+", "_", regex=True)
            .str.replace(r"[^\w_]", "", regex=True)
        )

        if list(self.df.columns) != original_columns:
            logging.info("تم تنظيف وتوحيد أسماء الأعمدة.")

    def remove_duplicates(self):
        initial_rows = len(self.df)
        self.df.drop_duplicates(inplace=True)
        removed = initial_rows - len(self.df)

        self.report["duplicates_removed"] = removed
        if removed:
            logging.info(f"تم حذف {removed} صف مكرر.")

    def is_date_column(self, col):
        name = col.lower()
        return any(keyword in name for keyword in ["date", "time", "created", "updated", "deadline"])

    def clean_dates(self, col):
        before_missing = self.df[col].isna().sum()
        converted = pd.to_datetime(self.df[col], errors="coerce")
        after_missing = converted.isna().sum()

        if after_missing <= before_missing + max(1, int(len(self.df) * 0.3)):
            self.df[col] = converted.dt.strftime("%Y-%m-%d")
            logging.info(f"تم توحيد التاريخ في العمود: {col}")
            return True

        return False

    def clean_text_column(self, col):
        self.df[col] = self.df[col].where(self.df[col].notna(), pd.NA)
        self.df[col] = self.df[col].astype("string").str.strip()
        self.df[col] = self.df[col].replace(
            ["nan", "None", "<NA>", "N/A", ""],
            pd.NA
        )
        self.df[col] = self.df[col].fillna("N/A")

    def clean_numeric_column(self, col):
        self.df[col] = pd.to_numeric(self.df[col], errors="coerce")

        if self.numeric_strategy == "zero":
            self.df[col] = self.df[col].fillna(0)

        elif self.numeric_strategy == "mean":
            self.df[col] = self.df[col].fillna(self.df[col].mean())

        elif self.numeric_strategy == "median":
            self.df[col] = self.df[col].fillna(self.df[col].median())

        elif self.numeric_strategy == "keep":
            pass

        else:
            logging.warning(f"استراتيجية رقمية غير معروفة، تم ترك القيم كما هي: {self.numeric_strategy}")

    def clean_data(self):
        if self.df is None:
            logging.warning("لا توجد بيانات لتنظيفها.")
            return False

        self.clean_column_names()
        self.remove_duplicates()

        for col in self.df.columns:
            processed_as = None

            if self.is_date_column(col):
                if self.clean_dates(col):
                    processed_as = "date"

            if processed_as is None:
                if pd.api.types.is_numeric_dtype(self.df[col]):
                    self.clean_numeric_column(col)
                    processed_as = "numeric"
                else:
                    self.clean_text_column(col)
                    processed_as = "text"

            self.report["columns_processed"].append({
                "column": col,
                "type": processed_as,
                "missing_after": int(self.df[col].isna().sum())
            })

        self.report["final_shape"] = self.df.shape
        self.report["finished_at"] = datetime.now().astimezone().isoformat()
        logging.info("تم تنظيف البيانات بنجاح.")
        return True

    def save_cleaned_data(self):
        if self.df is None:
            return None

        base_path = self.file_path.with_suffix("")
        
        if self.file_ext == ".csv":
            output_path = f"{base_path}_standardized.csv"
            self.df.to_csv(output_path, index=False, encoding="utf-8-sig")

        elif self.file_ext in [".xlsx", ".xls"]:
            output_path = f"{base_path}_standardized.xlsx"
            self.df.to_excel(output_path, index=False)

        elif self.file_ext == ".json":
            output_path = f"{base_path}_standardized.json"
            self.df.to_json(output_path, orient="records", indent=4, force_ascii=False)

        logging.info(f"تم حفظ الملف المنظف في: {output_path}")
        return output_path


if __name__ == "__main__":
    cleaner = AdvancedDataCleaner("data.csv", numeric_strategy="median")

    if cleaner.load_data():
        if cleaner.clean_data():
            cleaner.save_cleaned_data()