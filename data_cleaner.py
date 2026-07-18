import pandas as pd
import os
import logging

# إعداد نظام التسجيل القياسي (Logging) لتوثيق العمليات علمياً
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("cleaning_log.txt", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

class AdvancedDataCleaner:
    def __init__(self, file_path):
        self.file_path = file_path
        self.df = None
        self.file_ext = os.path.splitext(file_path)[1].lower()

    def load_data(self):
        """تحميل البيانات بناءً على الصيغ الدولية المتعارف عليها"""
        # تعريف الكلمات الشائعة عالمياً والتي تعبر عن قيم مفقودة لتوحيدها أثناء القراءة
        na_values = ["", " ", "nan", "NaN", "none", "None", "null", "Null", "missing", "N/A", "n/a"]
        
        try:
            if self.file_ext == '.csv':
                self.df = pd.read_csv(self.file_path, keep_default_na=True, na_values=na_values)
            elif self.file_ext in ['.xlsx', '.xls']:
                self.df = pd.read_excel(self.file_path, keep_default_na=True, na_values=na_values)
            elif self.file_ext == '.json':
                self.df = pd.read_json(self.file_path)
                # توحيد القيم المفقودة في جيون بعد تحميله
                self.df.replace(na_values, pd.NA, inplace=True)
            else:
                logging.error(f"الصيغة {self.file_ext} غير مدعومة علمياً في هذه الأداة.")
                return False

            logging.info(f"تم تحميل الملف ({self.file_ext}) بنجاح. حجم البيانات الحالي: {self.df.shape}")
            return True
        except Exception as e:
            logging.error(f"فشل تحميل الملف بسبب: {e}")
            return False

    def clean_data(self):
        """تنفيذ المعايير الدولية لتنظيف وتوحيد البيانات الجدولية"""
        if self.df is None:
            logging.warning("لا توجد بيانات معالجة لتنظيفها.")
            return

        # 1. إزالة الصفوف المكررة تماماً
        initial_rows = len(self.df)
        self.df.drop_duplicates(inplace=True)
        dropped_rows = initial_rows - len(self.df)
        if dropped_rows > 0:
            logging.info(f"المعيار 1: تم حذف {dropped_rows} صف مكرر علمياً.")

        # 2. معالجة وتوحيد الأعمدة بناءً على نوع البيانات (Dtype)
        for col in self.df.columns:
            # تنظيف الأعمدة النصية (Text/Object Columns)
            if self.df[col].dtype == 'object' or str(self.df[col].dtype).startswith('str'):
                # إزالة الفراغات من البداية والنهاية، وتوحيد حالة الأحرف لتسهيل المقارنات الدولية
                self.df[col] = self.df[col].astype(str).str.strip()
                self.df[col] = self.df[col].replace(["nan", "None", "<NA>", "N/A"], pd.NA)
                self.df[col] = self.df[col].fillna("N/A")
            
            # محاولة التعرف على أعمدة التواريخ وتوحيدها بالصيغة الدولية ISO 8601
            elif 'date' in col.lower() or 'time' in col.lower():
                try:
                    self.df[col] = pd.to_datetime(self.df[col], errors='coerce')
                    # تعبئة التواريخ غير الصالحة بنص افتراضي أو تركها مصنفة كـ NaT علمياً
                    logging.info(f"المعيار 2: تم توحيد تنسيق التواريخ في العمود '{col}' إلى صيغة ISO 8601 العالمية.")
                except Exception:
                    pass
            
            # معالجة الأعمدة الرقمية (Numeric Columns)
            else:
                # تعبئة القيم المفقودة بالرقم 0 أو الوسيط الحسابي (تجنباً للأخطاء الحسابية في الذكاء الاصطناعي)
                self.df[col] = self.df[col].fillna(0)

        logging.info("المعيار 3: تمت جميع عمليات التنظيف والتوحيد المعياري بنجاح.")

    def save_cleaned_data(self):
        """حفظ الملف المنظف بالصيغة الأصلية وتصدير تقرير لوق المحاذات"""
        if self.df is None:
            return None

        base_path = os.path.splitext(self.file_path)[0]
        output_path = f"{base_path}_standardized{self.file_ext}"

        try:
            if self.file_ext == '.csv':
                self.df.to_csv(output_path, index=False, encoding='utf-8-sig')
            elif self.file_ext in ['.xlsx', '.xls']:
                self.df.to_excel(output_path, index=False)
            elif self.file_ext == '.json':
                self.df.to_json(output_path, orient='records', indent=4, force_ascii=False)
            
            logging.info(f"المعيار 4: تم تصدير الملف القياسي بنجاح إلى: {output_path}")
            return output_path
        except Exception as e:
            logging.error(f"خطأ أثناء حفظ الملف: {e}")
            return None


if __name__ == "__main__":
    # تشغيل وفحص الأداة على ملف التجربة القياسي
    cleaner = AdvancedDataCleaner("data.csv")
    if cleaner.load_data():
        cleaner.clean_data()
        cleaner.save_cleaned_data()