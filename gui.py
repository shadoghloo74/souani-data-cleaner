import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import pandas as pd
from pathlib import Path
from data_cleaner import AdvancedDataCleaner

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class SouaniCleanerGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Souani Data Cleaner v3.3 (Professional Edition)")
        self.geometry("750x720")
        self.resizable(False, False)

        self.selected_path = None
        self.cleaner = AdvancedDataCleaner()

        self.title_label = ctk.CTkLabel(
            self, text="📊 Souani Data Cleaner v3.3 🧠",
            font=ctk.CTkFont(family="Segoe UI", size=26, weight="bold")
        )
        self.title_label.pack(pady=15)

        # إطار اختيار الملف
        self.file_frame = ctk.CTkFrame(self)
        self.file_frame.pack(pady=10, padx=40, fill="x")

        self.path_entry = ctk.CTkEntry(
            self.file_frame, 
            placeholder_text="اختر ملفاً لبدء التحليل الذكي والتنظيف...",
            justify="right", 
            font=ctk.CTkFont(family="Segoe UI", size=13),
            corner_radius=10,
            border_width=1,
            fg_color="#fcfcfc"
        )
        self.path_entry.pack(side="right", padx=10, pady=15, expand=True, fill="x")

        self.browse_btn = ctk.CTkButton(
            self.file_frame, text="📂 تصفح", width=100, command=self.browse_target,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            corner_radius=10
        )
        self.browse_btn.pack(side="left", padx=10, pady=15)

        # قسم اقتراحات وقراءة الـ AI
        self.ai_frame = ctk.CTkFrame(self)
        self.ai_frame.pack(pady=10, padx=40, fill="both", expand=True)

        self.ai_title = ctk.CTkLabel(
            self.ai_frame, text="🧠 تحليل جودة البيانات واقتراحات AI (المعاينة الأولى)",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold")
        )
        self.ai_title.pack(pady=(12, 5))

        self.ai_box = ctk.CTkTextbox(
            self.ai_frame, font=ctk.CTkFont(family="Segoe UI", size=12), wrap="word"
        )
        self.ai_box.pack(padx=15, pady=15, fill="both", expand=True)
        self.ai_box.insert("0.0", "الرجاء اختيار ملف بيانات ليقوم المحرك بفحصه أولياً وتقديم النصائح هنا...")

        # قسم خيارات واستراتيجيات المعالجة والتطهير
        self.settings_frame = ctk.CTkFrame(self)
        self.settings_frame.pack(pady=10, padx=40, fill="x")

        # معالجة الفراغات الرقمية
        self.strategy_label = ctk.CTkLabel(
            self.settings_frame, text="معالجة الفراغات الرقمية:",
            font=ctk.CTkFont(family="Segoe UI", size=12)
        )
        self.strategy_label.grid(row=0, column=1, padx=20, pady=10, sticky="e")

        self.strategy_var = ctk.StringVar(value="median")
        self.strategy_menu = ctk.CTkOptionMenu(
            self.settings_frame, values=["median", "mean", "zero", "keep"],
            variable=self.strategy_var, width=140, corner_radius=8
        )
        self.strategy_menu.grid(row=0, column=0, padx=20, pady=10, sticky="w")

        # معالجة البيانات المتطرفة
        self.outlier_label = ctk.CTkLabel(
            self.settings_frame, text="معالجة القيم الشاذة (Outliers):",
            font=ctk.CTkFont(family="Segoe UI", size=12)
        )
        self.outlier_label.grid(row=1, column=1, padx=20, pady=10, sticky="e")

        self.outlier_var = ctk.StringVar(value="keep")
        self.outlier_menu = ctk.CTkOptionMenu(
            self.settings_frame, values=["keep", "cap", "remove"],
            variable=self.outlier_var, width=140, corner_radius=8
        )
        self.outlier_menu.grid(row=1, column=0, padx=20, pady=10, sticky="w")
        
        self.settings_frame.grid_columnconfigure(0, weight=1)
        self.settings_frame.grid_columnconfigure(1, weight=1)

        # شريط الحالة السفلي
        self.status_label = ctk.CTkLabel(
            self, text="جاهز للتحليل الذكي...", text_color="gray",
            font=ctk.CTkFont(family="Segoe UI", size=13)
        )
        self.status_label.pack(pady=5)

        # زر بدء التنظيف
        self.clean_btn = ctk.CTkButton(
            self, text="▶ بدء تنظيف وتطهير البيانات القياسي", height=45,
            fg_color="#2ecc71", hover_color="#27ae60", command=self.start_cleaning_thread,
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            corner_radius=10
        )
        self.clean_btn.pack(pady=10, padx=40, fill="x")

    def browse_target(self):
        target = filedialog.askopenfilename(
            filetypes=[("Data Files", "*.csv *.xlsx *.xls *.json"), ("All Files", "*.*")]
        )
        if target:
            self.selected_path = target
            self.path_entry.delete(0, ctk.END)
            self.path_entry.insert(0, target)
            self.status_label.configure(text="جاري تشغيل تحليل جودة البيانات الأولي...", text_color="#3498db")

            threading.Thread(target=self.run_ai_analysis, args=(target,), daemon=True).start()

    def run_ai_analysis(self, path):
        try:
            path_obj = Path(path)
            suffix = path_obj.suffix.lower()
            
            if suffix == ".csv":
                df = pd.read_csv(path, na_values=AdvancedDataCleaner.COMMON_NA_VALUES, keep_default_na=True)
            elif suffix in [".xlsx", ".xls"]:
                sheets = pd.read_excel(path, sheet_name=None, na_values=AdvancedDataCleaner.COMMON_NA_VALUES, keep_default_na=True)
                first_sheet = list(sheets.keys())[0]
                df = sheets[first_sheet]
            elif suffix == ".json":
                df = pd.read_json(path)
                df.replace(AdvancedDataCleaner.COMMON_NA_VALUES, pd.NA, inplace=True)
            else:
                raise ValueError("صيغة الملف غير مدعومة للمعاينة السريعة.")

            suggestions = self.cleaner.generate_ai_suggestions(df)
            self.after(0, lambda: self.show_ai_suggestions(suggestions))
        except Exception as e:
            self.after(0, lambda: self.show_ai_error(str(e)))

    def show_ai_suggestions(self, suggestions):
        self.ai_box.delete("0.0", ctk.END)
        for sug in suggestions:
            self.ai_box.insert(ctk.END, f"{sug}\n\n")
        self.status_label.configure(text="تم تحليل الصفحة الأولى وتوليد الاقتراحات بنجاح.", text_color="green")

    def show_ai_error(self, error_message):
        self.ai_box.delete("0.0", ctk.END)
        self.ai_box.insert("0.0", f"❌ فشلت المعاينة التلقائية:\n{error_message}\n\n*ملاحظة: يمكنك الاستمرار والضغط على زر التنظيف إذا كان الملف سليماً.")
        self.status_label.configure(text="فشلت معاينة وفحص الملف.", text_color="#e74c3c")

    def start_cleaning_thread(self):
        if not self.selected_path:
            messagebox.showwarning("تنبيه", "الرجاء اختيار ملف بيانات أولاً!")
            return
        self.clean_btn.configure(state="disabled", text="⏳ جاري معالجة المحرك الاحترافي v3.3...")
        self.status_label.configure(text="المحرك يقوم بالتنظيف المتكامل وإصدار تقارير الـ Dashboard التفاعلية...", text_color="#3498db")
        threading.Thread(target=self.run_cleaner_engine, daemon=True).start()

    def run_cleaner_engine(self):
        try:
            engine = AdvancedDataCleaner(
                numeric_strategy=self.strategy_var.get(),
                outlier_strategy=self.outlier_var.get(),
                backup=True,
                overwrite=False
            )
            cleaned_files = engine.clean_target(self.selected_path)
            self.after(0, lambda: self.cleaning_success(cleaned_files))
        except Exception as e:
            self.after(0, lambda: self.cleaning_failed(str(e)))

    def cleaning_success(self, cleaned_files):
        self.clean_btn.configure(state="normal", text="▶ بدء تنظيف وتطهير البيانات القياسي")
        self.status_label.configure(text="🎉 إكتمل التطهير وتوليد لوحة تحكم النصوص العربية!", text_color="#2ecc71")
        
        file_list_str = "\n".join([f"- {Path(f).name}" for f in cleaned_files])
        messagebox.showinfo(
            "اكتملت المعالجة بنجاح v3.3", 
            f"تم تنظيف كافة صفحات الملف وتطهير النصوص العربية بنجاح:\n\n{file_list_str}\n\n📄 توجه لمجلد Reports/ لمشاهدة التقرير التفاعلي المحسن!"
        )

    def cleaning_failed(self, err_msg):
        self.clean_btn.configure(state="normal", text="▶ بدء تنظيف وتطهير البيانات القياسي")
        self.status_label.configure(text="❌ فشل محرك المعالجة المطور.", text_color="#e74c3c")
        messagebox.showerror("خطأ في المحرك v3.3", f"حدثت مشكلة غير متوقعة أثناء التنظيف:\n{err_msg}")

if __name__ == "__main__":
    app = SouaniCleanerGUI()
    app.mainloop()