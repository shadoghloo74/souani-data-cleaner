import pandas as pd
import os

class DataCleaner:
    def __init__(self, file_path):
        self.file_path = file_path
        self.df = None
        self.file_ext = os.path.splitext(file_path)[1].lower()

    def load_data(self):
        """تحميل البيانات بناءً على نوع الملف"""
        try:
            if self.file_ext == '.csv':
                self.df = pd.read_csv(self.file_path)
            elif self.file_ext in ['.xlsx', '.xls']:
                self.df = pd.read_excel(self.file_path)
            elif self.file_ext == '.json':
                self.df = pd.read_json(self.file_path)
            else:
                print(f"عذرًا، الصيغة {self.file_ext} غير مدعومة حاليًا.")
                return False

            print(f"تم تحميل ملف ({self.file_ext}) بنجاح.")
            return True

        except Exception as e:
            print(f"خطأ في تحميل الملف: {e}")
            return False

    def clean_data(self):
        """تنفيذ عمليات التنظيف الأساسية"""
        if self.df is None:
            print("لا يوجد بيانات لتنظيفها.")
            return

        self.df.drop_duplicates(inplace=True)

        for col in self.df.columns:
            if self.df[col].dtype == 'object' or str(self.df[col].dtype).startswith('str'):
                self.df[col] = self.df[col].fillna("N/A").astype(str).str.strip()
                self.df[col] = self.df[col].replace(["nan", "None", ""], "N/A")
            else:
                self.df[col] = self.df[col].fillna(0)

        print("تمت عمليات التنظيف بنجاح.")

    def save_cleaned_data(self):
        """حفظ الملف المنظف"""
        if self.df is None:
            return None

        base_path = os.path.splitext(self.file_path)[0]

        if self.file_ext == '.csv':
            output_path = f"{base_path}_cleaned.csv"
            self.df.to_csv(output_path, index=False)

        elif self.file_ext in ['.xlsx', '.xls']:
            output_path = f"{base_path}_cleaned.xlsx"
            self.df.to_excel(output_path, index=False)

        elif self.file_ext == '.json':
            output_path = f"{base_path}_cleaned.json"
            self.df.to_json(output_path, orient='records', indent=4, force_ascii=False)

        print(f"تم حفظ الملف المُنظف في: {output_path}")
        return output_path


if __name__ == "__main__":
    cleaner = DataCleaner("data.csv")
    if cleaner.load_data():
        cleaner.clean_data()
        cleaner.save_cleaned_data()