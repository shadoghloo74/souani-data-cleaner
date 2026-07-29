import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# ================================
# 1. إعداد البيانات الأساسية
# ================================

# أسماء عربية وإنجليزية
first_names = ['أحمد', 'سارة', 'محمد', 'Emma', 'خالد', 'John', 'فاطمة', 'Michael', 'عبدالله', 'Lisa']
last_names = ['العلي', 'Smith', 'الخالد', 'Johnson', 'النعيمي', 'Brown', 'الحسن', 'Wilson', 'المالكي', 'Davis']

# أسماء عربية فقط
cities = ['الرياض', 'جدة', 'الدمام', 'مكة', 'المدينة', 'Abu Dhabi', 'Dubai', 'Kuwait']

# تواريخ بصيغ مختلفة
def generate_random_date():
    formats = ['%Y-%m-%d', '%d/%m/%Y', '%m-%d-%Y', '%d-%b-%Y', '%Y/%m/%d']
    start = datetime(2020, 1, 1)
    end = datetime(2025, 12, 31)
    delta = end - start
    random_days = random.randint(0, delta.days)
    date_obj = start + timedelta(days=random_days)
    return date_obj.strftime(random.choice(formats))

# ================================
# 2. توليد البيانات الأساسية (500 صف)
# ================================

np.random.seed(42)  # لضمان التكرار

data = {
    'ID': range(1, 501),
    'First_Name': np.random.choice(first_names, 500),
    'Last_Name': np.random.choice(last_names, 500),
    'Age': np.random.randint(22, 60, 500),
    'Salary': np.random.randint(3000, 8000, 500),
    'City': np.random.choice(cities, 500),
    'Join_Date': [generate_random_date() for _ in range(500)],
    'Email': [],
    'Phone': [],
    'Department': np.random.choice(['IT', 'HR', 'Finance', 'Marketing', 'المبيعات', 'الدعم'], 500),
    'Performance_Score': np.random.uniform(1.0, 5.0, 500).round(2)
}

# توليد الإيميلز
domains = ['gmail.com', 'yahoo.com', 'company.com', 'outlook.com']
for i in range(500):
    fn = data['First_Name'][i]
    ln = data['Last_Name'][i]
    domain = random.choice(domains)
    data['Email'].append(f'{fn.lower()}.{ln.lower()}@{domain}')

# توليد أرقام الهواتف
for i in range(500):
    data['Phone'].append(f'+966{random.randint(500000000, 599999999)}')

df = pd.DataFrame(data)

# ================================
# 3. إضافة التحديات المتعمدة
# ================================

# --- صفوف مكررة (10% من البيانات) ---
duplicates = df.sample(50).copy()
df = pd.concat([df, duplicates], ignore_index=True)

# --- قيم مفقودة ---
# Age (5% مفقود)
missing_age_idx = df.sample(int(len(df)*0.05)).index
df.loc[missing_age_idx, 'Age'] = np.nan

# Salary (5% مفقود)
missing_salary_idx = df.sample(int(len(df)*0.05)).index
df.loc[missing_salary_idx, 'Salary'] = np.nan

# Email (10% مفقود)
missing_email_idx = df.sample(int(len(df)*0.10)).index
df.loc[missing_email_idx, 'Email'] = np.nan

# City (3% مفقود)
missing_city_idx = df.sample(int(len(df)*0.03)).index
df.loc[missing_city_idx, 'City'] = np.nan

# --- مسافات زائدة في النصوص ---
# First_Name (15% بمسافات زائدة)
whitespace_fn_idx = df.sample(int(len(df)*0.15)).index
df.loc[whitespace_fn_idx, 'First_Name'] = '  ' + df.loc[whitespace_fn_idx, 'First_Name'].astype(str) + '  '

# Email (10% بمسافات)
whitespace_email_idx = df.sample(int(len(df)*0.10)).index
df.loc[whitespace_email_idx, 'Email'] = '  ' + df.loc[whitespace_email_idx, 'Email'].astype(str) + '  '

# --- Outliers في الراتب ---
# إضافة رواتب شاذة (أعلى وأقل بكثير)
outlier_indices = df.sample(8).index
df.loc[outlier_indices[0], 'Salary'] = 1500000  # outlier كبير جداً
df.loc[outlier_indices[1], 'Salary'] = 2000000
df.loc[outlier_indices[2], 'Salary'] = -5000     # قيمة سالبة غير منطقية
df.loc[outlier_indices[3], 'Salary'] = 50000
df.loc[outlier_indices[4], 'Salary'] = 1000000
df.loc[outlier_indices[5], 'Salary'] = 900000
df.loc[outlier_indices[6], 'Salary'] = 30000
df.loc[outlier_indices[7], 'Salary'] = 750000

# --- تواريخ غير صالحة ---
invalid_dates = ['Not Available', 'N/A', '2026-13-45', 'Unknown', '----', '2026/02/30', 'invalid']
invalid_idx = df.sample(6).index
df.loc[invalid_idx, 'Join_Date'] = [random.choice(invalid_dates) for _ in range(6)]

# --- Age غير منطقي ---
df.loc[df.sample(3).index, 'Age'] = 0        # عمر صفر
df.loc[df.sample(2).index, 'Age'] = 300      # عمر غير منطقي

# --- Performance Score غير منطقي ---
outlier_score_idx = df.sample(4).index
df.loc[outlier_score_idx, 'Performance_Score'] = [0, -2, 15, 100]

# ================================
# 4. خلط البيانات عشوائياً
# ================================
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

# ================================
# 5. حفظ الملف
# ================================
output_path = 'dirty_test_dataset.csv'
df.to_csv(output_path, index=False, encoding='utf-8-sig')

print(f"✅ تم إنشاء الملف: {output_path}")
print(f"📊 عدد الصفوف الكلي: {len(df)}")
print(f"📋 عدد الأعمدة: {len(df.columns)}")
print(f"\n🔍 ملخص المشاكل في البيانات:")

# حساب المشاكل
print(f"  - الصفوف المكررة: {df.duplicated().sum()}")
print(f"  - Age مفقود: {df['Age'].isna().sum()}")
print(f"  - Salary مفقود: {df['Salary'].isna().sum()}")
print(f"  - Email مفقود: {df['Email'].isna().sum()}")
print(f"  - City مفقود: {df['City'].isna().sum()}")
print(f"  - رواتب شاذة (>50000 أو <0): {((df['Salary'] > 50000) | (df['Salary'] < 0)).sum()}")
print(f"  - Ages غير منطقية (<1 أو >120): {((df['Age'] < 1) | (df['Age'] > 120)).sum()}")

print(f"\n📂 الأعمدة: {list(df.columns)}")
