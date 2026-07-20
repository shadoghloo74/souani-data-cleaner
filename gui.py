import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import os
from data_cleaner import AdvancedDataCleaner

# ضبط المظهر العام للتطبيق
ctk.set_appearance_mode("System")  # الداكن أو الفاتح حسب النظام
ctk.set_default_color_theme("blue")

class DataCleanerGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        # إعدادات النافذة الرئيسية مع التجاوب مع التكبير
        self.title("Souani Data Cleaner v3.3")
        self.geometry("750x700")
        self.resizable(True, True)

        # تهيئة محرك التنظيف الخلفي
        self.cleaner = AdvancedDataCleaner()
        self.selected_file_path = None

        # بناء عناصر الواجهة الرسومية
        self._create_widgets()

    def _create_widgets(self):
        # عنوان التطبيق العلوي
        self.title_label = ctk.CTkLabel(
            self, 
            text="📊 Souani Data Cleaner v3.3 (Professional Edition)", 
            font=ctk.CTkFont(family="Helvetica", size=20, weight="bold")
        )
        self.title_label.pack(pady=15)

        # ------------------ قسم اختيار الملف ------------------
        self.file_frame = ctk.CTkFrame(self)
        self.file_frame.pack(pady=5, padx=25, fill="x")

        self.btn_browse = ctk.CTkButton(
            self.file_frame, 
            text="📂 تصفح واختيار الملف", 
            command=self._browse_file,
            font=ctk.CTkFont(family="Helvetica", size=13, weight="bold")
        )
        self.btn_browse.pack(side="right", padx=10, pady=10)

        self.lbl_file_path = ctk.CTkLabel(
            self.file_frame, 
            text="لم يتم اختيار أي ملف بعد...", 
            anchor="e",
            font=ctk.CTkFont(family="Helvetica", size=12)
        )
        self.lbl_file_path.pack(side="left", fill="x", expand=True, padx=10, pady=10)

        # ------------------ قسم التحليل والمعاينة الذكية ------------------
        self.preview_frame = ctk.CTkFrame(self)
        self.preview_frame.pack(pady=10, padx=25, fill="x")

        self.lbl_preview_title = ctk.CTkLabel(
            self.preview_frame, 
            text="🔍 (المعاينة الأولى) AI تحليل جودة البيانات واقتراحات", 
            font=ctk.CTkFont(family="Helvetica", size=13, weight="bold")
        )
        self.lbl_preview_title.pack(pady=5)

        # ضبط ارتفاع مربع المعاينة بـ 140 ليترك مساحة كافية للأزرار
        self.txt_preview = ctk.CTkTextbox(
            self.preview_frame, 
            height=140,
            font=ctk.CTkFont(family="Courier New", size=12),
            wrap="word"
        )
        self.txt_preview.pack(pady=5, padx=15, fill="x")
        self.txt_preview.configure(state="disabled")

        # ------------------ قسم الخيارات المخصصة ------------------
        self.options_frame = ctk.CTkFrame(self)
        self.options_frame.pack(pady=10, padx=25, fill="x")

        # خيار معالجة الفراغات الرقمية
        self.lbl_missing = ctk.CTkLabel(self.options_frame, text=":معالجة الفراغات الرقمية", font=ctk.CTkFont(family="Helvetica", size=12))
        self.lbl_missing.grid(row=0, column=1, padx=15, pady=8, sticky="e")
        
        self.cmb_missing = ctk.CTkComboBox(self.options_frame, values=["median", "mean", "drop"])
        self.cmb_missing.grid(row=0, column=0, padx=15, pady=8, sticky="w")
        self.cmb_missing.set("median")

        # خيار معالجة القيم الشاذة
        self.lbl_outliers = ctk.CTkLabel(self.options_frame, text=":معالجة القيم الشاذة (Outliers)", font=ctk.CTkFont(family="Helvetica", size=12))
        self.lbl_outliers.grid(row=1, column=1, padx=15, pady=8, sticky="e")
        
        self.cmb_outliers = ctk.CTkComboBox(self.options_frame, values=["keep", "cap", "remove"])
        self.cmb_outliers.grid(row=1, column=0, padx=15, pady=8, sticky="w")
        self.cmb_outliers.set("keep")

        # ------------------ قسم أزرار التنظيف والتشغيل ------------------
        self.actions_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.actions_frame.pack(pady=10, padx=25, fill="x")

        # زر التنظيف الذكي التلقائي بنقرة واحدة
        self.btn_smart_clean = ctk.CTkButton(
            self.actions_frame,
            text="✨ تنظيف ذكي تلقائي (بنقرة واحدة)",
            fg_color="#D4AF37",  # لون ذهبي مميز
            hover_color="#AA8C2C",
            text_color="#000000",
            command=self._run_smart_clean,
            font=ctk.CTkFont(family="Helvetica", size=14, weight="bold")
        )
        self.btn_smart_clean.pack(fill="x", pady=4)

        # زر التنظيف المخصص بالخيارات المحددة
        self.btn_custom_clean = ctk.CTkButton(
            self.actions_frame,
            text="⚙️ تشغيل التنظيف بالخيارات المخصصة",
            fg_color="#2ecc71",
            hover_color="#27ae60",
            command=self._run_custom_clean,
            font=ctk.CTkFont(family="Helvetica", size=13, weight="bold")
        )
        self.btn_custom_clean.pack(fill="x", pady=4)

        # مؤشر التحميل السفلي
        self.progress_bar = ctk.CTkProgressBar(self)
        self.progress_bar.pack(pady=8, padx=25, fill="x")
        self.progress_bar.set(0)

    def _browse_file(self):
        file_types = [("Data Files", "*.xlsx *.csv *.json"), ("Excel Files", "*.xlsx"), ("CSV Files", "*.csv"), ("JSON Files", "*.json")]
        path = filedialog.askopenfilename(title="اختر ملف البيانات لتنظيفه", filetypes=file_types)
        
        if path:
            self.selected_file_path = path
            self.lbl_file_path.configure(text=os.path.basename(path))
            self._update_preview("⏳ جاري تحليل الملف وتوليد الاقتراحات الذكية أولياً...")
            
            # تشغيل المعاينة في الخلفية لضمان عدم تجميد الواجهة
            threading.Thread(target=self._load_file_preview, daemon=True).start()

    def _load_file_preview(self):
        try:
            suggestions = self.cleaner.generate_initial_suggestions(self.selected_file_path)
            self._update_preview(suggestions)
        except Exception as e:
            self._update_preview(f"❌ خطأ أثناء تحليل الملف المختار:\n{str(e)}")

    def _update_preview(self, text):
        self.txt_preview.configure(state="normal")
        self.txt_preview.delete("1.0", tk.END)
        self.txt_preview.insert(tk.END, text)
        self.txt_preview.configure(state="disabled")

    def _run_smart_clean(self):
        if not self.selected_file_path:
            messagebox.showwarning("تنبيه", "الرجاء اختيار ملف بيانات أولاً!")
            return
        
        self._toggle_buttons(False)
        self.progress_bar.start()
        
        # تشغيل التنظيف التلقائي الذكي في خيط معالجة منفصل
        threading.Thread(target=self._process_cleaning, args=(True,), daemon=True).start()

    def _run_custom_clean(self):
        if not self.selected_file_path:
            messagebox.showwarning("تنبيه", "الرجاء اختيار ملف بيانات أولاً!")
            return
        
        self._toggle_buttons(False)
        self.progress_bar.start()
        
        # تشغيل التنظيف المخصص بالخيارات المدخلة
        threading.Thread(target=self._process_cleaning, args=(False,), daemon=True).start()

    def _process_cleaning(self, is_smart):
        try:
            if is_smart:
                output_path = self.cleaner.clean(self.selected_file_path, smart_auto=True)
            else:
                missing_strategy = self.cmb_missing.get()
                outlier_strategy = self.cmb_outliers.get()
                output_path = self.cleaner.clean(
                    self.selected_file_path, 
                    smart_auto=False, 
                    missing_num=missing_strategy, 
                    outliers=outlier_strategy
                )

            self.progress_bar.stop()
            self.progress_bar.set(1)
            self._toggle_buttons(True)
            
            # عرض رسالة نجاح مخصصة للمستخدم
            filename = os.path.basename(output_path)
            messagebox.showinfo(
                "v3.3 اكتملت المعالجة التلقائية", 
                f"تم تنظيف كافة صفحات الملف وتطهير النصوص العربية بنجاح:\n\n - {filename}\n\n📄 لمشاهدة التقرير التفاعلي المحسن توجه لمجلد Reports/"
            )
        except Exception as e:
            self.progress_bar.stop()
            self.progress_bar.set(0)
            self._toggle_buttons(True)
            messagebox.showerror("خطأ في المعالجة", f"عذراً، حدث خطأ أثناء عملية التنظيف:\n{str(e)}")

    def _toggle_buttons(self, state):
        btn_state = "normal" if state else "disabled"
        self.btn_browse.configure(state=btn_state)
        self.btn_smart_clean.configure(state=btn_state)
        self.btn_custom_clean.configure(state=btn_state)

if __name__ == "__main__":
    app = DataCleanerGUI()
    app.mainloop()