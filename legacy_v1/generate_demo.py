import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import generate_dashboard as gd  # Import the module we just refactored
import plotly.io as pio

# Output file
OUTPUT_DEMO_HTML = "demo_dashboard.html"

# Constants for Mock Data
ASSOCIATES_SMART = ["AC", "FP", "PB", "DDL", "CA"]
ASSOCIATES_SMARTPLUS = ["LP", "DP", "GP", "GB", "PM"]

CATEGORIES = [
    "Telecoms", "Energie", "Transports", "Copieurs", 
    "Facilities", "Dechets", "QOFI Location Engins EPI", "Materiel IT"
]

def generate_months(count=24):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365*2)
    month_range = pd.date_range(start=start_date, end=end_date, freq='MS', normalize=True)
    return [d.strftime("%Y-%m") for d in month_range][-count:]

def generate_mock_row(kpi_name, months, min_v=5, max_v=15, is_ratio=False):
    row = {"KPI": kpi_name}
    total = 0
    for m in months:
        if is_ratio:
            val = np.random.uniform(min_v, max_v) # float 0.1 to 0.5
            row[m] = round(val, 2)
            # For ratios, total isn't sum usually, but let's just make it average for demo or sum
            # The dashboard logic takes 'Total' column for table totals. 
            # For ratios, it usually expects a float that it formats as %.
        else:
            val = np.random.randint(min_v, max_v)
            row[m] = val
            total += val
    
    if is_ratio:
        row["Total"] = round(np.mean([row[m] for m in months]), 2)
    else:
        row["Total"] = total
    
    return row

def main():
    print("Generating DEMO Dashboard...")
    
    months = generate_months(24)
    data = []

    # --- 1. Commerce Data ---
    # Smart Group
    row_comm_g1 = generate_mock_row("Commerce (AC FP PB DDL CA)", months, 10, 25)
    data.append(row_comm_g1)
    
    # Smart+ Group
    row_comm_g2 = generate_mock_row("Commerce (LP DP GP GB PM)", months, 5, 15)
    data.append(row_comm_g2)
    
    # Total Commerce (Sum of G1 + G2 roughly)
    row_comm_total = {"KPI": "Commerce Total", "Total": 0}
    for m in months:
        val = row_comm_g1[m] + row_comm_g2[m]
        row_comm_total[m] = val
        row_comm_total["Total"] += val
    data.append(row_comm_total)
    
    # Divide by 15
    row_div15 = {"KPI": "Commerce / 15", "Total": 0}
    for m in months:
        val = round(row_comm_total[m] / 15, 2)
        row_div15[m] = val
    row_div15["Total"] = round(row_comm_total["Total"] / 15, 2)
    data.append(row_div15)

    # --- 2. Analyse Data ---
    row_ana_g1 = generate_mock_row("Analyse (AC FP PB DDL CA)", months, 8, 20)
    data.append(row_ana_g1)
    row_ana_g2 = generate_mock_row("Analyse (LP DP GP GB PM)", months, 2, 8)
    data.append(row_ana_g2)
    
    # --- 3. Signed Data (Commerce) ---
    # Generally lower than commerce input
    row_sign_g1 = generate_mock_row("Commerce Signe (AC FP PB DDL CA)", months, 5, 15)
    data.append(row_sign_g1)
    row_sign_g2 = generate_mock_row("Commerce Signe (LP DP GP GB PM)", months, 2, 8)
    data.append(row_sign_g2)
    
    # Total Signed
    row_sign_total = {"KPI": "Commerce Signe Total", "Total": 0}
    for m in months:
        val = row_sign_g1[m] + row_sign_g2[m]
        row_sign_total[m] = val
        row_sign_total["Total"] += val
    data.append(row_sign_total)
    
    # --- 4. Ratios ---
    # Ratio Total
    data.append(generate_mock_row("Ratio Signe/Total Commerce", months, 0.2, 0.45, is_ratio=True))
    data.append(generate_mock_row("Ratio Signe/Total Commerce (G1)", months, 0.25, 0.50, is_ratio=True))
    data.append(generate_mock_row("Ratio Signe/Total Commerce (G2)", months, 0.15, 0.40, is_ratio=True))

    # --- 5. Analyse Signed ---
    row_ana_sign_g1 = generate_mock_row("Analyse Signe (AC FP PB DDL CA)", months, 4, 12)
    data.append(row_ana_sign_g1)
    row_ana_sign_g2 = generate_mock_row("Analyse Signe (LP DP GP GB PM)", months, 1, 5)
    data.append(row_ana_sign_g2)

    # --- 6. Categories ---
    suffixes = ["Commerce", "Commerce Signe", "Analyse", "Analyse Signe"]
    for suffix in suffixes:
        for cat in CATEGORIES:
            kpi_name = f"{cat} {suffix}"
            data.append(generate_mock_row(kpi_name, months, 0, 8))

    # Create DataFrame
    df = pd.DataFrame(data)

    # --- Generate Figures (Reusing Logic) ---
    print("Generating Figures...")

    # Configs (Duplicated from generate_dashboard to be standalone safe or just explicit)
    # Colors
    C_G1 = gd.C_G1
    C_G2 = gd.C_G2
    C_RATIO = gd.C_RATIO
    
    cfg_comm_chart_only = [
        ("Commerce (AC FP PB DDL CA)", "Smart", C_G1, 'bar'),
        ("Commerce (LP DP GP GB PM)", "Smart +", C_G2, 'bar')
    ]
    
    cfg_comm_signed_chart = [
        ("Commerce Signe (AC FP PB DDL CA)", "Smart", C_G1, 'bar'),
        ("Commerce Signe (LP DP GP GB PM)", "Smart +", C_G2, 'bar')
    ]
    
    cfg_comm_signed_table = [
        ("Ratio Signe/Total Commerce", "Taux de contrats signés", C_RATIO, 'none'),
        ("Ratio Signe/Total Commerce (G1)", "Taux de contrats signés Smart", C_RATIO, 'none'),
        ("Ratio Signe/Total Commerce (G2)", "Taux de contrats signés Smart+", C_RATIO, 'none')
    ]
    
    cfg_anal_chart_only = [
        ("Analyse (AC FP PB DDL CA)", "Smart", C_G1, 'bar'),
        ("Analyse (LP DP GP GB PM)", "Smart +", C_G2, 'bar')
    ]
    
    cfg_anal_signed_chart = [
        ("Analyse Signe (AC FP PB DDL CA)", "Smart", C_G1, 'bar'), 
        ("Analyse Signe (LP DP GP GB PM)", "Smart +", C_G2, 'bar')
    ]

    # Generate Figures
    fig1 = gd.create_simple_figure(df, "Entrées Portefeuille Commerce (DÉMO)", cfg_comm_chart_only, months)
    fig2 = gd.create_mixed_figure(df, "Projets Signés Commerce (DÉMO)", cfg_comm_signed_chart, cfg_comm_signed_table, months, table_total_only=True)
    fig3 = gd.create_simple_figure(df, "Entrées Portefeuille Analyse (DÉMO)", cfg_anal_chart_only, months)
    fig4 = gd.create_simple_figure(df, "Projets Signés Analyse (DÉMO)", cfg_anal_signed_chart, months)
    
    fig5 = gd.create_category_figure(df, "Détail : Entrées Commerce (DÉMO)", "Commerce", months)
    fig6 = gd.create_category_figure(df, "Détail : Signés Commerce (DÉMO)", "Commerce Signe", months)
    fig7 = gd.create_category_figure(df, "Détail : Entrées Analyse (DÉMO)", "Analyse", months)
    fig8 = gd.create_category_figure(df, "Détail : Signés Analyse (DÉMO)", "Analyse Signe", months)

    # --- HTML Generation ---
    config = {'responsive': True}
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Dashboard KPI - DÉMONSTRATION</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
            body {{ font-family: 'Segoe UI', sans-serif; margin: 0; padding: 20px; background-color: #f4f6f6; }}
            h1 {{ text-align: center; color: #E74C3C; margin-bottom: 30px; }}
            .section {{ margin-bottom: 40px; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
            .chart-wrapper {{ width: 100%; }}
            .notice {{ text-align: center; background: #fff3cd; color: #856404; padding: 15px; margin-bottom: 20px; border-radius: 5px; border: 1px solid #ffeeba; }}
        </style>
    </head>
    <body>
        <div class="notice">
            <strong>MODE DÉMONSTRATION</strong><br>
            Ceci est un exemple généré avec des données aléatoires.
        </div>
        
        <h1>Tableau de Bord KPI (DEMO)</h1>
        
        <!-- Commerce -->
        <div class="section">{fig1.to_html(full_html=False, include_plotlyjs=False, config=config)}</div>
        <div class="section">{fig2.to_html(full_html=False, include_plotlyjs=False, config=config)}</div>
        
        <!-- Analyse -->
        <div class="section">{fig3.to_html(full_html=False, include_plotlyjs=False, config=config)}</div>
        <div class="section">{fig4.to_html(full_html=False, include_plotlyjs=False, config=config)}</div>
        
        <!-- Categories -->
        <div class="section">{fig5.to_html(full_html=False, include_plotlyjs=False, config=config)}</div>
        <div class="section">{fig6.to_html(full_html=False, include_plotlyjs=False, config=config)}</div>
        <div class="section">{fig7.to_html(full_html=False, include_plotlyjs=False, config=config)}</div>
        <div class="section">{fig8.to_html(full_html=False, include_plotlyjs=False, config=config)}</div>
    </body>
    </html>
    """
    
    with open(OUTPUT_DEMO_HTML, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    print(f"Demo Dashboard saved to {OUTPUT_DEMO_HTML}")

if __name__ == "__main__":
    main()
