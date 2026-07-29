import os, json, random
import pandas as pd
from datetime import datetime, timedelta

folder = "test_datasets"
os.makedirs(folder, exist_ok=True)

# 1) sample_small.csv
small_data = [
    [" Ahmed Ali ", 29, 5000, "2022-01-15"],
    [" Sara Mohamed", None, 6200, "2021-07-20"],
    ["Khaled Hassan ", 35, None, "2020-03-10"],
    [" Mona Said ", 41, 7000, ""],
    ["Omar Adel", 28, 4500, "2023-05-01"],
    [" Laila Samir ", "", 5200, "2022-11-12"],
    ["Hany Mostafa", 33, 5800, "2021-01-30"],
    [" Nour Ahmed ", 26, None, "2024-02-18"],
    ["Youssef Ali ", 39, 8000, None],
    [" Dina Fathy", 31, 6100, "2020-09-09"],
    [" Karim Nabil ", None, 4900, "2023-12-01"],
    [" Salma Tarek", 27, "", "2022-06-15"],
    ["Mahmoud Sami ", 45, 9000, "2019-04-25"],
    [" Rana Hossam ", 30, 5500, "bad-date"],
    [" Tamer Fouad", 38, 7600, "2021-10-10"]
]
pd.DataFrame(small_data, columns=["name", "age", "salary", "join_date"]).to_csv(os.path.join(folder, "sample_small.csv"), index=False, encoding="utf-8-sig")

# 2) sample_excel.xlsx
excel_data = [
    ["Laptop", "Electronics", 1200, "2024-01-15"],
    ["Mouse", "Electronics", 25, "2024-99-99"],
    ["Keyboard", None, 75, "not-a-date"],
    ["Monitor", "Electronics", None, "2024-03-10"],
    ["Chair", "Furniture", 150, "2024-04-01"],
    ["Desk", "Furniture", 300, ""],
    ["Laptop", "Electronics", 1200, "2024-01-15"],
    ["Chair", "Furniture", 150, "2024-04-01"]
]
pd.DataFrame(excel_data, columns=["product", "category", "price", "purchase_date"]).to_excel(os.path.join(folder, "sample_excel.xlsx"), index=False)

# 3) sample_data.json
sales_data = [
    {"sale_id": 1, "customer": "Ahmed", "amount": 250, "quantity": 2},
    {"sale_id": 2, "customer": "Sara", "amount": None, "quantity": 1},
    {"sale_id": 3, "customer": "Omar", "amount": 9999999, "quantity": 5},
    {"sale_id": 4, "customer": None, "amount": 400, "quantity": 3},
    {"sale_id": 5, "customer": "Mona", "amount": -5000, "quantity": 1},
    {"sale_id": 6, "customer": "Khaled", "amount": 120, "quantity": None},
    {"sale_id": 7, "customer": "Laila", "amount": 300, "quantity": 2},
    {"sale_id": 8, "customer": "", "amount": 0, "quantity": 0}
]
with open(os.path.join(folder, "sample_data.json"), "w", encoding="utf-8") as f:
    json.dump(sales_data, f, ensure_ascii=False, indent=4)

# 4) sample_large.csv
names = ["Ahmed", "Sara", "Omar", "Mona", "Khaled", "Laila", "Youssef", "Dina"]
departments = ["HR", "IT", "Finance", "Sales", "Marketing", None]
large_data = []
start_date = datetime(2018, 1, 1)
for i in range(15000):
    random_date = start_date + timedelta(days=random.randint(0, 2500))
    large_data.append({
        "employee_id": i + 1,
        "name": random.choice(names),
        "age": random.choice([random.randint(20, 60), None, "", "unknown"]),
        "department": random.choice(departments),
        "salary": random.choice([random.randint(3000, 15000), None, "", 9999999, -1000]),
        "join_date": random.choice([random_date.strftime("%Y-%m-%d"), "bad-date", "", None])
    })
pd.DataFrame(large_data).to_csv(os.path.join(folder, "sample_large.csv"), index=False, encoding="utf-8-sig")

# 5) sample_dirty_types.xlsx
dirty_types_data = [
    ["Ahmed Ali", 30, 5000, "2022-01-15"],
    ["Sara Mohamed", "thirty two", 6200, "2021-07-20"],
    ["Khaled Hassan", 35, "ألف وخمسمائة", "2020-03-10"],
    ["Mona Said", 41, "seven thousand", "not-a-date"],
    ["Omar Adel", "28 years", 4500, "2023-05-01"],
    ["Laila Samir", 27, None, "2022-11-12"],
    ["Hany Mostafa", None, "6000 USD", "2021-01-30"]
]
pd.DataFrame(dirty_types_data, columns=["name", "age", "salary", "join_date"]).to_excel(os.path.join(folder, "sample_dirty_types.xlsx"), index=False)

# 6) sample_empty.csv
open(os.path.join(folder, "sample_empty.csv"), "w", encoding="utf-8").close()

# 7) sample_empty_headers.xlsx
pd.DataFrame(columns=["name", "age", "salary", "join_date"]).to_excel(os.path.join(folder, "sample_empty_headers.xlsx"), index=False)

print("تم إنشاء مجلد test_datasets وجميع ملفات الاختبار بنجاح 🎉")
