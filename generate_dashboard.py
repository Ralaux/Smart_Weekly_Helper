import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio

# Configuration
INPUT_DATA = "Donnees_Brutes_KPI.xlsx"
OUTPUT_HTML = "dashboard_kpi.html"

# Colors
C_TOTAL = '#2C3E50' # Dark Blue
C_G1 = '#2C3E50'    # Blue (User Preference)
C_G2 = '#5B80A4'    # Light Blue (User Preference)
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
        # Load Excel
        df = pd.read_excel(INPUT_DATA)
        # Filter out empty spacer rows (where KPI is empty string or NaN)
        df = df[df['KPI'].notna() & (df['KPI'] != '')]
        return df
    except Exception as e:
        print(f"Error loading Data: {e}")
        return None

def get_monthly_columns(df):
    return [c for c in df.columns if c not in ['KPI', 'Total']]

def get_values(df, kpi, months):
    subset = df[df['KPI'] == kpi]
    if subset.empty: return [0]*len(months)
    return subset[months].values.flatten()

def create_table_trace(df, kpis_config, months, total_only=False):
    """Helper to generate a Table trace"""
    header = ["Mois"] + [cfg[1] for cfg in kpis_config]
    
    if total_only:
        col_mois = ["<b>Total</b>"]
    else:
        col_mois = ["<b>Total</b>"] + months
        
    data_cols = [col_mois]
    
    for kpi, label, _, _ in kpis_config:
        subset = df[df['KPI'] == kpi]
        if not subset.empty:
            total_val = subset['Total'].values[0]
            
            # Formatting logic
            is_ratio = "Ratio" in kpi
            
            # Format Total
            if is_ratio:
                try:
                    tv = float(total_val)
                    total_val_fmt = f"{round(tv * 100)}%"
                except: total_val_fmt = total_val
            else:
                total_val_fmt = round(total_val, 2)
            
            if total_only:
                col_data = [total_val_fmt]
            else:
                monthly_vals = subset[months].values.flatten().tolist()
                # Format Monthly
                if is_ratio:
                    try:
                        monthly_vals = [f"{round(float(v)*100)}%" for v in monthly_vals]
                    except: pass
                else:
                    monthly_vals = [round(v, 2) for v in monthly_vals]
                
                col_data = [total_val_fmt] + monthly_vals
            
            data_cols.append(col_data)
        else:
            count = 1 if total_only else len(months)+1
            data_cols.append([0]*count)
            
    return go.Table(
        header=dict(values=header, fill_color='#2C3E50', font=dict(color='white', size=10)),
        cells=dict(values=data_cols, fill_color='#ECF0F1', font=dict(color='black', size=9), height=24)
    )

def create_simple_figure(df, title, kpis_config, months, show_legend=True):
    """
    Creates a simple figure with 1 row, 1 col (Full Width Chart).
    Used for: Portfolio Inputs, Analyse Signed, Categories.
    """
    fig = make_subplots(rows=1, cols=1, subplot_titles=(title,))
    
    for kpi, label, color, chart_type in kpis_config:
        raw_vals = get_values(df, kpi, months)
        y_vals = [float(v) for v in raw_vals]
        if chart_type == 'bar':
            fig.add_trace(go.Bar(x=months, y=y_vals, name=label, marker_color=color, orientation='v', showlegend=show_legend), row=1, col=1)

    fig.update_layout(
        height=500, 
        barmode='stack', # Default to stack, category uses group (override usually or pass arg)
        template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=1.15, xanchor="left", x=0), # V23: Left + Higher
        margin=dict(l=20, r=20, t=140, b=50) # V23: Increased top margin
    )
    
    # Correct X-axes
    fig.update_xaxes(type='category', tickmode='linear', dtick=1, tickangle=-45, row=1, col=1)
    fig.update_yaxes(autorange=True, row=1, col=1)
    
    return fig

def create_mixed_figure(df, title, chart_config, table_config, months, table_total_only=False):
    """
    Creates a figure with Chart (Left) + Table (Right).
    Used for: Commerce Signed (with Ratios).
    """
    fig = make_subplots(
        rows=1, cols=2,
        column_widths=[0.65, 0.35],
        specs=[[{"type": "xy"}, {"type": "table"}]],
        subplot_titles=(title, "Ratios")
    )
    
    # Chart
    for kpi, label, color, chart_type in chart_config:
        raw_vals = get_values(df, kpi, months)
        y_vals = [float(v) for v in raw_vals]
        if chart_type == 'bar':
            fig.add_trace(go.Bar(x=months, y=y_vals, name=label, marker_color=color, orientation='v', showlegend=True), row=1, col=1)
            
    # Table
    table_trace = create_table_trace(df, table_config, months, total_only=table_total_only)
    fig.add_trace(table_trace, row=1, col=2)
    
    fig.update_layout(
        height=500, 
        barmode='stack',
        template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=1.15, xanchor="left", x=0), # V23: Left + Higher
        margin=dict(l=20, r=20, t=140, b=50) # V23: Increased top margin
    )
    
    fig.update_xaxes(type='category', tickmode='linear', dtick=1, tickangle=-45, row=1, col=1)
    fig.update_yaxes(autorange=True, row=1, col=1)
    
    return fig

def create_category_figure(df, title, suffix, months):
    """
    Creates a figure with 1 row:
    Row 1: Chart (Grouped Bars for 8 cats)
    (Table removed in V20)
    """
    fig = make_subplots(
        rows=1, cols=1,
        subplot_titles=(title,)
    )
    
    # --- 1. Chart (Top) ---
    for i, cat in enumerate(TARGET_CATS):
        kpi_name = f"{cat} {suffix}"
        raw_vals = get_values(df, kpi_name, months)
        y_vals = [float(v) for v in raw_vals]
        
        # Explicitly FORCE Vertical
        fig.add_trace(go.Bar(x=months, y=y_vals, name=cat, marker_color=CAT_COLORS[i], orientation='v'), row=1, col=1)

    fig.update_layout(
        height=500, 
        barmode='group', 
        template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=1.15, xanchor="left", x=0), # V23: Left + Higher
        margin=dict(l=20, r=20, t=140, b=50) # V23: Increased top margin
    )
    
    # Correct X-axis
    fig.update_xaxes(type='category', tickmode='linear', dtick=1, tickangle=-45, row=1, col=1)
    
    return fig

def main():
    print("Generating Dashboard V23 (Left Legends, More Spacing)...")
    df = load_data()
    if df is None: return
    
    months = get_monthly_columns(df)
    
    # --- 1. Commerce Portfolio ---
    # Full config for Table (Brut)
    cfg_comm_table_raw = [
        ("Commerce Total", "Total", C_TOTAL, 'bar'),
        ("Commerce (AC FP PB DDL CA)", "Smart", C_G1, 'bar'),
        ("Commerce (LP DP GP GB PM)", "Smart +", C_G2, 'bar'),
        ("Commerce / 15", "Ratio", C_RATIO, 'none')
    ]
    
    # Subset config for Stacked Chart (Only Smart and Smart+)
    cfg_comm_chart_only = [
        ("Commerce (AC FP PB DDL CA)", "Smart", C_G1, 'bar'),
        ("Commerce (LP DP GP GB PM)", "Smart +", C_G2, 'bar')
    ]
    
    # V18 Update: Separate configs for Chart and Table
    
    # 1. COMMERCE: Signed Chart (Bars) + Signed Table (Ratios Only)
    cfg_comm_signed_chart = [
        ("Commerce Signe (AC FP PB DDL CA)", "Smart", C_G1, 'bar'),   # V21: Renamed to Smart
        ("Commerce Signe (LP DP GP GB PM)", "Smart +", C_G2, 'bar')   # V21: Renamed to Smart +
    ]
    # Ratios for table
    cfg_comm_signed_table = [
        ("Ratio Signe/Total Commerce", "Taux de contrats signés", C_RATIO, 'none'),
        ("Ratio Signe/Total Commerce (G1)", "Taux de contrats signés Smart", C_RATIO, 'none'),
        ("Ratio Signe/Total Commerce (G2)", "Taux de contrats signés Smart+", C_RATIO, 'none')
    ]
    
    # V22: Generate 4 Separate Figures for Portfolios
    
    # 1. Commerce Input
    fig1 = create_simple_figure(df, "Entrées Portefeuille Commerce", cfg_comm_chart_only, months)
    
    # 2. Commerce Signed (Mixed Layout)
    fig2 = create_mixed_figure(df, "Projets Signés (Commerce)", cfg_comm_signed_chart, cfg_comm_signed_table, months, table_total_only=True)

    # --- 2. Analyse Portfolio ---
    cfg_anal_chart_only = [
        ("Analyse (PB DDL CA)", "Smart", C_G1, 'bar'),
        ("Analyse (LP GB)", "Smart +", C_G2, 'bar')
    ]
    
    cfg_anal_signed_chart = [
        ("Analyse Signe (Telecoms Energie...)", "Smart", C_G1, 'bar'), 
        ("Analyse Signe (QOFI IT...)", "Smart +", C_G2, 'bar')
    ]

    # 3. Analyse Input
    fig3 = create_simple_figure(df, "Entrées Portefeuille Analyse", cfg_anal_chart_only, months)

    # 4. Analyse Signed (Full Layout - Simple Figure)
    fig4 = create_simple_figure(df, "Projets Signés (Analyse)", cfg_anal_signed_chart, months)

    # --- Categories ---
    fig5 = create_category_figure(df, "Détail par Catégories : Entrées Portefeuille Commerce", "Commerce", months)
    fig6 = create_category_figure(df, "Détail par Catégories : Projets signés", "Commerce Signe", months)
    fig7 = create_category_figure(df, "Détail par Catégories : Entrées Portefeuille Analyse", "Analyse", months)
    fig8 = create_category_figure(df, "Détail par Catégories : Projets signés", "Analyse Signe", months)

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
        <h1>Tableau de Bord KPI</h1>
        
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
    
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    print(f"Dashboard V22 saved to {OUTPUT_HTML} (Split Figures)")

if __name__ == "__main__":
    main()
