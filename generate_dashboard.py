import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio

# Configuration
INPUT_CSV = "kpi_results.csv"
OUTPUT_HTML = "dashboard_kpi_v6.html"

# Colors
C_TOTAL = '#2C3E50' # Dark Blue
C_G1 = '#F39C12'    # Orange
C_G2 = '#2ECC71'    # Green
C_RATIO = '#E74C3C' # Red for ratio line

# 8 Distinct colors for categories
CAT_COLORS = [
    '#E74C3C', '#8E44AD', '#3498DB', '#1ABC9C', 
    '#F1C40F', '#E67E22', '#7F8C8D', '#34495E'
]

TARGET_CATS = [
    "Telecoms", "Energie", "Transports", "Copieurs", 
    "Facilities", "Dechets", "QOFI Location Engins EPI", "Materiel IT"
]

def load_data():
    try:
        return pd.read_csv(INPUT_CSV)
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return None

def get_monthly_columns(df):
    return [c for c in df.columns if c not in ['KPI', 'Total']]

def get_values(df, kpi, months):
    subset = df[df['KPI'] == kpi]
    if subset.empty: return [0]*len(months)
    return subset[months].values.flatten()

def create_portfolio_figure(df, title, kpis_config, months):
    """
    Creates a figure with 2 subplots: Chart (Left) and Table (Right).
    kpis_config: List of tuples (KPI Name, Legend Label, Color, Type='bar'/'line')
    """
    # Create subplots showing chart on left (70%) and table on right (30%)
    fig = make_subplots(
        rows=1, cols=2,
        column_widths=[0.65, 0.35],
        specs=[[{"type": "xy"}, {"type": "table"}]],
        subplot_titles=(title, "Données Brutes")
    )

    # --- 1. Chart (Vertical) ---
    print(f"DEBUG: creating chart for {title}")
    for kpi, label, color, chart_type in kpis_config:
        raw_vals = get_values(df, kpi, months)
        # Force conversion to list of floats
        y_vals = [float(v) for v in raw_vals]
        
        print(f"DEBUG: KPI='{kpi}' Label='{label}' First5_Y={y_vals[:5]}")
        
        if chart_type == 'bar':
            # Explicitly FORCE Vertical: x=months, y=values, orientation='v'
            fig.add_trace(go.Bar(x=months, y=y_vals, name=label, marker_color=color, orientation='v'), row=1, col=1)
        elif chart_type == 'line':
            pass

    # --- 2. Table ---
    header = ["Mois"] + [cfg[1] for cfg in kpis_config]
    
    col_mois = ["<b>Total</b>"] + months
    data_cols = [col_mois]
    
    for kpi, label, _, _ in kpis_config:
        subset = df[df['KPI'] == kpi]
        if not subset.empty:
            total_val = subset['Total'].values[0]
            monthly_vals = subset[months].values.flatten().tolist()
            # Format numbers
            total_val = round(total_val, 2)
            monthly_vals = [round(v, 2) for v in monthly_vals]
            
            col_data = [total_val] + monthly_vals
            data_cols.append(col_data)
        else:
            data_cols.append([0]*(len(months)+1))

    fig.add_trace(go.Table(
        header=dict(values=header, fill_color='#2C3E50', font=dict(color='white', size=11)),
        cells=dict(values=data_cols, fill_color='#ECF0F1', font=dict(color='black', size=10), height=24)
    ), row=1, col=2)

    fig.update_layout(
        height=500,
        barmode='group',
        template="plotly_white",
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(x=0.66, y=1)
    )
    # Ensure standard Y-axis (Low to High)
    fig.update_yaxes(autorange=True, row=1, col=1)
    
    return fig

def create_category_figure(df, title, suffix, months):
    """
    Creates a full-width figure with grouped bars for all 8 categories.
    suffix: 'Commerce', 'Commerce Signe', etc.
    """
    fig = go.Figure()
    
    for i, cat in enumerate(TARGET_CATS):
        kpi_name = f"{cat} {suffix}"
        raw_vals = get_values(df, kpi_name, months)
        y_vals = [float(v) for v in raw_vals]
        
        # Explicitly FORCE Vertical
        fig.add_trace(go.Bar(x=months, y=y_vals, name=cat, marker_color=CAT_COLORS[i], orientation='v'))

    fig.update_layout(
        title_text=title,
        height=500, 
        barmode='group', 
        template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        margin=dict(l=20, r=20, t=50, b=20)
    )
    return fig

def main():
    print("Generating Dashboard V6 (Vertical + Force Float + New File)...")
    df = load_data()
    if df is None: return
    
    months = get_monthly_columns(df)
    
    # --- 1. Commerce Portfolio ---
    # Renamed Groups: Smart / Smart +
    cfg_comm = [
        ("Commerce Total", "Total", C_TOTAL, 'bar'),
        ("Commerce (AC FP PB DDL CA)", "Smart", C_G1, 'bar'),
        ("Commerce (LP DP GP GB PM)", "Smart +", C_G2, 'bar'),
        ("Commerce / 15", "Ratio", C_RATIO, 'none')
    ]
    fig1 = create_portfolio_figure(df, "Portefeuille Commerce", cfg_comm, months)

    # --- 2. Analyse Portfolio ---
    cfg_anal = [
        ("Analyse Total", "Total", C_TOTAL, 'bar'),
        ("Analyse (PB DDL CA)", "Smart", C_G1, 'bar'),
        ("Analyse (LP GB)", "Smart +", C_G2, 'bar')
    ]
    fig2 = create_portfolio_figure(df, "Portefeuille Analyse", cfg_anal, months)

    # --- 3-6. Category Figures ---
    fig3 = create_category_figure(df, "Détail par Catégorie : Commerce", "Commerce", months)
    fig4 = create_category_figure(df, "Détail par Catégorie : Commerce Signé", "Commerce Signe", months)
    fig5 = create_category_figure(df, "Détail par Catégorie : Analyse", "Analyse", months)
    fig6 = create_category_figure(df, "Détail par Catégorie : Analyse Signé", "Analyse Signe", months)

    # --- Generate HTML ---
    # Convert each fig to HTML div
    config = {'responsive': True}
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Dashboard KPI</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
            body {{ font-family: 'Segoe UI', sans-serif; margin: 0; padding: 20px; background-color: #f4f6f6; }}
            h1 {{ text-align: center; color: #2C3E50; margin-bottom: 30px; }}
            .section {{ margin-bottom: 40px; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
            .chart-wrapper {{ width: 100%; }}
        </style>
    </head>
    <body>
        <h1>Tableau de Bord KPI (V6)</h1>
        
        <div class="section">
            {fig1.to_html(full_html=False, include_plotlyjs=False, config=config)}
        </div>
        
        <div class="section">
            {fig2.to_html(full_html=False, include_plotlyjs=False, config=config)}
        </div>
        
        <div class="section">
            {fig3.to_html(full_html=False, include_plotlyjs=False, config=config)}
        </div>
        
        <div class="section">
            {fig4.to_html(full_html=False, include_plotlyjs=False, config=config)}
        </div>
        
        <div class="section">
            {fig5.to_html(full_html=False, include_plotlyjs=False, config=config)}
        </div>
        
        <div class="section">
            {fig6.to_html(full_html=False, include_plotlyjs=False, config=config)}
        </div>
    </body>
    </html>
    """
    
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    print(f"Dashboard V6 saved to {OUTPUT_HTML}")

if __name__ == "__main__":
    main()
