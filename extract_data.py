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

def format_kpi_result(kpi_name, series):
    """
    Helper function to format a monthly series into a dictionary for the results list.
    """
    row = {"KPI": kpi_name}
    # Add monthly columns
    for date, value in series.items():
        col_name = date.strftime("%Y-%m")
        row[col_name] = value
    # Add Total
    row["Total"] = series.sum()
    return row

def calculate_all_kpis(df):
    """
    Calculates all KPIs and returns a list of result dictionaries.
    """
    results = []

    # KPI 1: Commerce Projects (Last 24 months)
    commerce_series = kpi_calculations.count_commerce_projects(df)
    results.append(format_kpi_result("Number of 'Commerce' projects", commerce_series))
    print("-" * 100)
    print(f"Number of 'Commerce' projects (last 24 months): {commerce_series.sum()}")

    # KPI 2: Smart Commerce Projects (Last 24 months)
    smart_commerce_series = kpi_calculations.count_commerce_projects_smart(df)
    results.append(format_kpi_result("Number of 'Commerce' projects (Smart only)", smart_commerce_series))
    print(f"Number of 'Commerce' projects (Smart only) (last 24 months): {smart_commerce_series.sum()}")
    print("-" * 100)

    return results

def save_results(results, output_path):
    """
    Saves the list of results to a CSV file.
    """
    if not results:
        print("No results to save.")
        return

    df_results = pd.DataFrame(results)
    
    # Reorder columns: KPI, then dates sorted, then Total
    cols = df_results.columns.tolist()
    date_cols = sorted([c for c in cols if c not in ["KPI", "Total"]])
    final_cols = ["KPI"] + date_cols + ["Total"]
    
    df_results = df_results[final_cols]
    
    df_results.to_csv(output_path, index=False)
    print(f"Results exported to {output_path}")

def main():
    print("Starting data extraction...")
    df = load_data(FILE_PATH, SHEET_NAME)
    
    if df is not None:
        print("Data loaded successfully.")
        results = calculate_all_kpis(df)
        save_results(results, OUTPUT_CSV)
    else:
        print("Failed to load data.")

if __name__ == "__main__":
    main()