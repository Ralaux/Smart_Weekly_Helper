import pandas as pd
import os
import warnings
import kpi_calculations

# Suppress openpyxl warnings about Data Validation extension
warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl')

FILE_PATH = "Fichier sivi Stats cce Smart 12 2025.xlsx"
SHEET_NAME = "Base Stats"
OUTPUT_CSV = "kpi_results.csv"

def load_data(file_path, sheet_name):
    """
    Reads the Excel file and returns the DataFrame.
    """
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        return None

    try:
        # Read columns A through S (0 to 18)
        # Headers are on the second row (index 1)
        df = pd.read_excel(file_path, sheet_name=sheet_name, usecols="A:S", header=1)
        return df
    except Exception as e:
        print(f"An error occurred while loading data: {e}")
        return None

def format_kpi_result(kpi_name, series, total_value=None):
    """
    Helper function to format a monthly series into a dictionary for the results list.
    """
    row = {"KPI": kpi_name}
    # Add monthly columns
    for date, value in series.items():
        col_name = date.strftime("%Y-%m")
        row[col_name] = value
    # Add Total
    if total_value is not None:
        row["Total"] = total_value
    else:
        row["Total"] = series.sum()
    return row

def calculate_all_kpis(df):
    """
    Calculates all KPIs and returns a list of result dictionaries.
    """
    results = []

    # --- Table 1: Commerce ---
    print("\n--- Computing 'Commerce' KPIs ---")
    
    associates_commerce_g1 = ["AC", "FP", "PB", "DDL", "CA"]
    associates_commerce_g2 = ["LP", "DP", "GP", "GB", "PM"]

    # 1. Total Commerce
    commerce_total = kpi_calculations.count_projects(df, "Commerce")
    results.append(format_kpi_result("Commerce Total", commerce_total))
    print(f"Commerce Total (last 24m): {commerce_total.sum()}")

    # 2. Commerce Group 1
    commerce_g1 = kpi_calculations.count_projects(df, "Commerce", associates_commerce_g1)
    results.append(format_kpi_result("Commerce (AC FP PB DDL CA)", commerce_g1))
    print(f"Commerce Group 1 (last 24m): {commerce_g1.sum()}")

    # 3. Commerce Group 2
    commerce_g2 = kpi_calculations.count_projects(df, "Commerce", associates_commerce_g2)
    results.append(format_kpi_result("Commerce (LP DP GP GB PM)", commerce_g2))
    print(f"Commerce Group 2 (last 24m): {commerce_g2.sum()}")

    # 4. Total / 15
    commerce_div_15 = (commerce_total / 15).round(2)
    results.append(format_kpi_result("Commerce / 15", commerce_div_15))
    
    # SPACER
    results.append({"KPI": "SPACE"})

    # --- Table 2: Analyse ---
    print("\n--- Computing 'Analyse' KPIs ---")
    
    associates_analyse_g1 = ["PB", "DDL", "CA"]
    associates_analyse_g2 = ["LP", "GB"]

    # 1. Total Analyse
    analyse_total = kpi_calculations.count_projects(df, "Analyse")
    results.append(format_kpi_result("Analyse Total", analyse_total))
    print(f"Analyse Total (last 24m): {analyse_total.sum()}")

    # 2. Analyse Group 1
    analyse_g1 = kpi_calculations.count_projects(df, "Analyse", associates_analyse_g1)
    results.append(format_kpi_result("Analyse (PB DDL CA)", analyse_g1))
    print(f"Analyse Group 1 (last 24m): {analyse_g1.sum()}")

    # 3. Analyse Group 2
    analyse_g2 = kpi_calculations.count_projects(df, "Analyse", associates_analyse_g2)
    results.append(format_kpi_result("Analyse (LP GB)", analyse_g2))
    print(f"Analyse Group 2 (last 24m): {analyse_g2.sum()}")
    
    # SPACER
    results.append({"KPI": "SPACE"})

    # --- Table 3: Analyse des signatures ---
    print("\n--- Computing 'Signatures' KPIs ---")

    # === Commerce Signé ===
    # 1. Total Commerce Signé
    commerce_signed_total = kpi_calculations.count_projects(df, "Commerce", is_signed=True)
    results.append(format_kpi_result("Commerce Signe Total", commerce_signed_total))
    print(f"Commerce Signé Total (last 24m): {commerce_signed_total.sum()}")

    # 2. Commerce Signé Group 1
    commerce_signed_g1 = kpi_calculations.count_projects(df, "Commerce", associates=associates_commerce_g1, is_signed=True)
    results.append(format_kpi_result("Commerce Signe (AC FP PB DDL CA)", commerce_signed_g1))
    print(f"Commerce Signé Group 1 (last 24m): {commerce_signed_g1.sum()}")

    # 3. Commerce Signé Group 2
    commerce_signed_g2 = kpi_calculations.count_projects(df, "Commerce", associates=associates_commerce_g2, is_signed=True)
    results.append(format_kpi_result("Commerce Signe (LP DP GP GB PM)", commerce_signed_g2))
    print(f"Commerce Signé Group 2 (last 24m): {commerce_signed_g2.sum()}")
    
    # Global Ratio
    ratio_total = (commerce_signed_total / commerce_total.replace(0, 1)).round(2)
    # Calculate Total column for ratio: Total Signed / Total Commerce
    total_val_ratio_total = round(commerce_signed_total.sum() / commerce_total.sum(), 2) if commerce_total.sum() > 0 else 0
    results.append(format_kpi_result("Ratio Signe/Total Commerce", ratio_total, total_value=total_val_ratio_total))

    # Ratio G1
    ratio_g1 = (commerce_signed_g1 / commerce_g1.replace(0, 1)).round(2)
    total_val_ratio_g1 = round(commerce_signed_g1.sum() / commerce_g1.sum(), 2) if commerce_g1.sum() > 0 else 0
    results.append(format_kpi_result("Ratio Signe/Total Commerce (G1)", ratio_g1, total_value=total_val_ratio_g1))
    
    # Ratio G2
    ratio_g2 = (commerce_signed_g2 / commerce_g2.replace(0, 1)).round(2)
    total_val_ratio_g2 = round(commerce_signed_g2.sum() / commerce_g2.sum(), 2) if commerce_g2.sum() > 0 else 0
    results.append(format_kpi_result("Ratio Signe/Total Commerce (G2)", ratio_g2, total_value=total_val_ratio_g2))
    
    # SPACER
    results.append({"KPI": "SPACE"})

    # === Analyse Signé ===
    
    cats_analyse_g1 = ["Télécoms", "Energie", "Transports", "Copieurs", "Facilities", "Nettoyage / Gardiennage", "Déchets"]
    # Based on README: "Category" = "QOFI / Location Engins / EPI" "Matériel IT"
    cats_analyse_g2 = ["QOFI / Location Engins / EPI", "Matériel IT"]

    # 1. Total Analyse Signé
    analyse_signed_total = kpi_calculations.count_projects(df, "Analyse", is_signed=True)
    results.append(format_kpi_result("Analyse Signe Total", analyse_signed_total))
    print(f"Analyse Signé Total (last 24m): {analyse_signed_total.sum()}")

    # 2. Analyse Signé Cat G1
    analyse_signed_g1 = kpi_calculations.count_projects(df, "Analyse", categories=cats_analyse_g1, is_signed=True)
    results.append(format_kpi_result("Analyse Signe (Telecoms Energie...)", analyse_signed_g1))
    print(f"Analyse Signé Cat G1 (last 24m): {analyse_signed_g1.sum()}")

    # 3. Analyse Signé Cat G2
    analyse_signed_g2 = kpi_calculations.count_projects(df, "Analyse", categories=cats_analyse_g2, is_signed=True)
    results.append(format_kpi_result("Analyse Signe (QOFI IT...)", analyse_signed_g2))
    print(f"Analyse Signé Cat G2 (last 24m): {analyse_signed_g2.sum()}")
    
    # SPACER
    results.append({"KPI": "SPACE"})
    
    # --- Table 4: KPIs par Categorie ---
    print("\n--- Computing 'Category' KPIs (Tables) ---")
    
    target_categories = [
        "Télécoms", "Energie", "Transports", "Copieurs", 
        "Facilities", "Déchets", "QOFI / Location Engins / EPI", "Matériel IT"
    ]
    
    # Helper to clean names for CSV (remove accents, etc)
    def clean_name(name):
        return name.replace("é", "e").replace("è", "e").replace("à", "a").replace("/", "").replace("  ", " ").strip()

    # Define the 4 types of metrics to generate
    # Format: (Suffix Name, Project Type, IsSigned)
    metrics_config = [
        ("Commerce", "Commerce", False),
        ("Commerce Signe", "Commerce", True),
        ("Analyse", "Analyse", False),
        ("Analyse Signe", "Analyse", True)
    ]

    # Iterate by Metric Type first (as requested), then by Category
    for suffix, proj_type, is_signed in metrics_config:
        for cat in target_categories:
            cat_clean = clean_name(cat)
            cat_filter = [cat] # Pass as list
            
            kpi_name = f"{cat_clean} {suffix}"
            
            res = kpi_calculations.count_projects(
                df, 
                proj_type, 
                categories=cat_filter, 
                is_signed=is_signed
            )
            results.append(format_kpi_result(kpi_name, res))
        
        # SPACER between each block of 8 categories
        results.append({"KPI": "SPACE"})
        
    print(f"Generated 4 KPIs types x {len(target_categories)} categories = {4 * len(target_categories)} KPIs.")

    return results

def save_results(results, output_excel_path):
    """
    Saves the list of results to an Excel file (for Manual & Dashboard).
    """
    if not results:
        print("No results to save.")
        return

    df_results = pd.DataFrame(results)
    
    # Reorder columns: KPI, then dates sorted, then Total
    cols = df_results.columns.tolist()
    # Filter out columns that are not dates or KPI/Total
    date_cols = sorted([c for c in cols if c not in ["KPI", "Total"]])
    final_cols = ["KPI"] + date_cols + ["Total"]
    
    df_results = df_results[final_cols]
    
    # --- Save Excel (With Spaces) ---
    # Replace "SPACE" in KPI column with empty string
    df_excel = df_results.copy()
    df_excel['KPI'] = df_excel['KPI'].replace('SPACE', '')
    # Fill NaN with empty string for cleaner look
    df_excel = df_excel.fillna('')
    
    df_excel.to_excel(output_excel_path, index=False)
    print(f"Results exported to {output_excel_path}")

def main():
    print("Starting data extraction...")
    df = load_data(FILE_PATH, SHEET_NAME)
    
    if df is not None:
        print("Data loaded successfully.")
        results = calculate_all_kpis(df)
        save_results(results, "Donnees_Brutes_KPI.xlsx")
    else:
        print("Failed to load data.")

if __name__ == "__main__":
    main()
