import pandas as pd
import glob
import os
import datetime

# 1. Load Source Data
source_file = "Base stats.xlsx"
print(f"Loading {source_file}...")
df = pd.read_excel(source_file, header=1) # Validated row 2 is header (index 1)

print("\n--- Raw Data Inspection ---")
print("Columns:", df.columns.tolist())
print(f"Total rows: {len(df)}")

# 2. Focus on the discrepancy area: Dec 2025, Commerce
# Legacy found 18, Angular found 5.

target_month_year = "2025-12"
target_type = "commerce"

# 3. Simulate Logic Variants

def normalize_slug(s):
    if not isinstance(s, str): return str(s)
    # Using the same logic as TS: normalize NFD, remove diacritics, lower, trim
    import unicodedata
    s = unicodedata.normalize('NFD', s).encode('ascii', 'ignore').decode("utf-8")
    return s.lower().strip()

print("\n--- Logic Simulation ---")

# Step A: Identify Columns via Slug
col_map = {}
for col in df.columns:
    slug = normalize_slug(col)
    if slug == "type de projet": col_map['type'] = col
    if "date" in slug and "entree" in slug: col_map['date'] = col

print(f"Mapped Columns: {col_map}")

if 'type' not in col_map or 'date' not in col_map:
    print("CRITICAL: Could not map required columns!")
    exit()

# Step B: Filter by Type (Commerce)
# TS Logic: row['type'] === 'commerce'
# Python Logic: row['Type'].lower() == 'commerce'

type_col = col_map['type']
date_col = col_map['date']

df['slug_type'] = df[type_col].apply(normalize_slug)
commerce_subset = df[df['slug_type'] == target_type].copy()
print(f"\nRows matching 'Commerce' type: {len(commerce_subset)}")

# Step C: Analyze Dates in this subset
count_dec_2025_valid = 0
count_dec_2025_invalid = 0
debug_rows = []

print(f"\nAnalyzing Dates for 'Commerce' rows (Target: {target_month_year})...")

for idx, row in commerce_subset.iterrows():
    raw_date = row[date_col]
    
    # 1. Python/Pandas native interpretation (The "Gold Standard" for legacy)
    py_date = pd.to_datetime(raw_date, errors='coerce')
    
    # 2. TS Logic Simulation (Manual Parse + new Date)
    ts_date_valid = False
    ts_reason = "Unknown"
    
    # Simulation of parseDate function in TS
    parsed_date = None
    if isinstance(raw_date, datetime.datetime):
        parsed_date = raw_date
        ts_reason = "Already Date Object"
    elif isinstance(raw_date, str):
        # TS Try 1: new Date(val)
        # Note: In Node/Chrome '20/12/2025' might be Invalid Date depending on locale, 
        # but in many envs it defaults to US MM/DD/YYYY -> Invalid Month 20
        # or it works if system locale matches. 
        # Our custom regex logic:
        if "/" in raw_date:
            parts = raw_date.split('/')
            if len(parts) == 3:
                # Custom TS logic: 'DD/MM/YYYY'
                try:
                    d = int(parts[0])
                    m = int(parts[1]) - 1
                    y = int(parts[2])
                    # Check validity
                    if 1 <= int(parts[1]) <= 12 and 1 <= int(parts[0]) <= 31:
                         parsed_date = datetime.datetime(y, m+1, d)
                         ts_reason = "Custom Regex Match"
                    else:
                        ts_reason = "Regex Match but Invalid range"
                except:
                    ts_reason = "Regex Parse Error"
        
        if parsed_date is None:
             # Try standard
             try:
                 # simple string parse simulation
                 parsed_date = pd.to_datetime(raw_date) 
                 ts_reason = "Standard String Parse"
             except:
                 ts_reason = "Failed String Parse"
                 
    # Check if falls in Dec 2025
    is_dec_25 = False
    if parsed_date is not pd.NaT and parsed_date is not None:
        if parsed_date.year == 2025 and parsed_date.month == 12:
            is_dec_25 = True
    
    if is_dec_25:
        count_dec_2025_valid += 1
    elif py_date.year == 2025 and py_date.month == 12:
        # It WAS Dec 2025 in Python but NOT in our TS sim
        count_dec_2025_invalid += 1
        debug_rows.append({
            'idx': idx,
            'raw_date': raw_date,
            'raw_type': type(raw_date),
            'py_interpret': py_date,
            'ts_interpret': parsed_date,
            'ts_reason': ts_reason
        })

# Analyze the 18 rows that ARE in Dec 2025 according to Python
with open("results.txt", "w", encoding="utf-8") as f:
    f.write("\n--- DEEP DIVE: Dec 2025 Rows ---\n")
    dec_25_rows = commerce_subset[
        (pd.to_datetime(commerce_subset[date_col], errors='coerce').dt.year == 2025) &
        (pd.to_datetime(commerce_subset[date_col], errors='coerce').dt.month == 12)
    ]

    for idx, row in dec_25_rows.iterrows():
        raw_val = row[date_col]
        f.write(f"Row {idx}: Raw='{raw_val}' Type={type(raw_val)}\n")

    f.write(f"Total Dec 2025 rows found: {len(dec_25_rows)}\n")

print("Deep dive done. Check results.txt")

# Test Associates if needed
