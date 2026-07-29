import os
import json
import pandas as pd
import numpy as np

class AdvancedDataCleaner:
    def __init__(self):
        pass

    def clean_data(self, file_path, missing_strategy="median", outlier_strategy="keep"):
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.csv':
            df = pd.read_csv(file_path)
        elif ext in ['.xlsx', '.xls']:
            df = pd.read_excel(file_path)
        elif ext == '.json':
            df = pd.read_json(file_path)
        else:
            raise ValueError(f"صيغة الملف غير مدعومة: {ext}")

        # حماية ضد الملفات الفارغة
        if df.empty:
            raise ValueError("الملف المحدد فارغ ولا يحتوي على أي بيانات!")

        report = []

        # 1. إزالة المكررات
        df = df.drop_duplicates()

        # 2. معالجة القيم المفقودة
        if missing_strategy == "drop":
            df = df.dropna()
        else:
            # للأعمدة الرقمية
            num_cols = df.select_dtypes(include=[np.number]).columns
            for col in num_cols:
                if df[col].notnull().any(): # التأكد من وجود قيمة واحدة على الأقل
                    val = df[col].median() if missing_strategy == "median" else df[col].mean()
                    df[col] = df[col].fillna(val)

            # للأعمدة النصية وغير الرقمية
            other_cols = df.select_dtypes(exclude=[np.number]).columns
            for col in other_cols:
                df[col] = df[col].fillna("N/A")

        # 3. معالجة Outliers
        if outlier_strategy in ["cap", "remove"]:
            num_cols = df.select_dtypes(include=[np.number]).columns
            for col in num_cols:
                q1 = df[col].quantile(0.25)
                q3 = df[col].quantile(0.75)
                iqr = q3 - q1
                if iqr > 0:
                    lower_bound = q1 - 1.5 * iqr
                    upper_bound = q3 + 1.5 * iqr
                    if outlier_strategy == "cap":
                        df[col] = np.clip(df[col], lower_bound, upper_bound)
                    elif outlier_strategy == "remove":
                        df = df[(df[col] >= lower_bound) & (df[col] <= upper_bound)]

        # إرجاع الجدول النظيف والتقرير
        return df, report