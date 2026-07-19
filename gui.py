import customtkinter as ctk
from tkinter import filedialog, messagebox
from pathlib import Path
import threading
import os

# استيراد المحرك البرمجي الذكي 
from data_cleaner import AdvancedDataCleaner

# إعداد المظهر العام للواجهة
ctk.set_appearance_mode("System")  
ctk.set_default_color_theme("blue")

class SouaniCleanerGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Souani Data Cleaner v2.0 (PRD-PDS-0001)")
        self.geometry("700x550")
        self.resizable(False, False)

        self.selected_path = None

        # --- عنوان البرنامج العلوي ---
        self.title_label = ctk.CTkLabel(
            self, text="📊 Souani Data Cleaner", 
            font=ctk.CTkFont(family="Segoe UI", size=26, weight="bold")
        )
        self.title_label.pack(pady=20)

        # --- قسم اختيار الملف أو المجلد ---
        self.file_frame = ctk.CTkFrame(self)
        self.file_frame.pack(pady=15, padx=40, fill="x")

        self.path_entry = ctk.CTkEntry(
            self.file_frame, placeholder_text="اختر ملفاً (CSV, Excel, JSON) أو مجلداً كاملاً...", 
            justify="right", font=ctk.CTkFont(family="Segoe UI", size=13)
        )
        self.path_entry.pack(side="right", padx=10, pady=15, expand=True, fill="x")

        self.browse_btn = ctk.CTkButton(
            self.file_frame, text="📂 تصفح", width=100, command=self.browse_target,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold")
        )
        self.browse_btn.pack(side="left", padx=10, pady=15)

        # --- قسم إعدادات التنظيف ---
        self.settings_frame = ctk.CTkFrame(self)
        self.settings_frame.pack(pady=15, padx=40, fill="x")

        self.strategy_label = ctk.CTkLabel(
            self.settings_frame, text="استراتيجية التعامل مع القيم الرقمية الفارغة:",
            font=ctk.CTkFont(family="Segoe UI", size=13)
        )
        self.strategy_label.pack(side="right", padx=20, pady=20)

        self.strategy_var = ctk.StringVar(value="median")
        self.strategy_menu = ctk.CTkOptionMenu(
            self.settings_frame, 
            values=["median", "mean", "zero", "keep"],
            variable=self.strategy_var,
            width=120
        )
        self.strategy_menu.pack(side="left", padx=20, pady=20)

        # --- زر بدء التشغيل والحالة ---
        # التصحيح الذكي للخط المائل باستخدام slant="italic"
        self.status_label = ctk.CTkLabel(
            self, text="جاهز لبدء عملية المعالجة...", text_color="gray",
            font=ctk.CTkFont(family="Segoe UI", size=13, slant="italic")
        )
        self.status_label.pack(pady=10)

        self.clean_btn = ctk.CTkButton(
            self, text="▶ بدء تنظيف وتطهير البيانات", height=45, 
            fg_color="#2ecc71", hover_color="#27ae60", command=self.start_cleaning_thread,
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold")
        )
        self.clean_btn.pack(pady=15, padx=40, fill="x")

        # --- زر استعادة النسخة الاحتياطية (Undo) ---
        self.undo_btn = ctk.CTkButton(
            self, text="↩ استعادة الملف الأصلي المنسوخ احتياطياً (Undo)", 
            fg_color="#e74c3c", hover_color="#c0392b", command=self.trigger_undo,
            font=ctk.CTkFont(family="Segoe UI", size=12)
        )
        self.undo_btn.pack(pady=5)

    def browse_target(self):
        msg = messagebox.askyesno("نوع الهدف", "هل تريد تحديد (ملف فردي)؟ اضغط No لتحديد (مجلد كامل).")
        if msg:
            target = filedialog.askopenfilename(
                filetypes=[("Data Files", "*.csv *.xlsx *.xls *.json"), ("All Files", "*.*")]
            )
        else:
            target = filedialog.askdirectory()

        if target:
            self.selected_path = target
            self.path_entry.delete(0, ctk.END)
            self.path_entry.insert(0, target)
            self.status_label.configure(text="تم تحديد الهدف بنجاح. جاهز للتنظيف.", text_color="green")

    def start_cleaning_thread(self):
        if not self.selected_path:
            messagebox.showwarning("تنبيه", "الرجاء اختيار ملف أو مجلد أولاً!")
            return
        
        self.clean_btn.configure(state="disabled", text="⏳ جاري المعالجة والتنظيف علمياً...")
        self.status_label.configure(text="جاري تنظيف وتوليد التقارير وتحديث الـ Backup...", text_color="#3498db")
        
        threading.Thread(target=self.run_cleaner_engine, daemon=True).start()

    def run_cleaner_engine(self):
        try:
            strategy = self.strategy_var.get()
            self.cleaner = AdvancedDataCleaner(numeric_strategy=strategy)
            self.cleaner.clean_target(self.selected_path)
            self.after(0, self.cleaning_success)
        except Exception as e:
            self.after(0, lambda: self.cleaning_failed(str(e)))

    def cleaning_success(self):
        self.clean_btn.configure(state="normal", text="▶ بدء تنظيف وتطهير البيانات")
        self.status_label.configure(text="🎉 تم التنظيف بنجاح! راجع ملف Cleaning_Report.html", text_color="#2ecc71")
        messagebox.showinfo("نجاح العملية", "تمت معالجة البيانات، تحديث النسخ الاحتياطية، وتوليد تقرير HTML الاحترافي!")

    def cleaning_failed(self, err_msg):
        self.clean_btn.configure(state="normal", text="▶ بدء تنظيف وتطهير البيانات")
        self.status_label.configure(text="❌ فشلت العملية بسبب خطأ في البيانات.", text_color="#e74c3c")
        messagebox.showerror("خطأ في المعالجة", f"حدثت مشكلة أثناء التنظيف:\n{err_msg}")

    def trigger_undo(self):
        if hasattr(self, 'cleaner') and self.cleaner.undo_last_operation():
            messagebox.showinfo("تمت الاستعادة", "تم استرجاع نسخة الملف الأصلية قبل التنظيف بنجاح من مجلد Backup.")
            self.status_label.configure(text="تمت استعادة الملف الأصلي بنجاح.", text_color="orange")
        else:
            messagebox.showwarning("فشل الاستعادة", "لا توجد عمليات تنظيف سابقة في هذه الجلسة يمكن استعادتها.")

if __name__ == "__main__":
    app = SouaniCleanerGUI()
    app.mainloop()