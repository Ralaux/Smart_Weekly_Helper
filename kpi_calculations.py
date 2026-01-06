import pandas as pd
from datetime import datetime, timedelta

def get_monthly_counts(df, mask):
    """
    Helper function to resample filtered data by month over the last 24 months.
    Returns a pandas Series with Month as index and Count as value.
    """
    # Define last 24 months range (ending current month)
    end_date = datetime.now()
    # Normalize to start of month to match resampling usually
    # But explicit 24 months ago range is safer
    start_date = end_date - timedelta(days=365*2)
    
    # Create a full index of months
    # 'MS' is Month Start
    # Normalize to midnight to match resample output
    full_range = pd.date_range(start=start_date, end=end_date, freq='MS', normalize=True)
    
    # Filter data
    filtered_df = df[mask].copy()
    
    # Ensure index is date for resampling
    filtered_df = filtered_df.set_index("Date d'entrée")
    
    # Resample and count
    # Reindex fills missing months with 0
    monthly_counts = filtered_df.resample('MS').size().reindex(full_range, fill_value=0)
    
    return monthly_counts

def count_commerce_projects(df):
    """
    Calculates the monthly counts of rows where 'Type de projet' is 'Commerce'.
    """
    if df is None:
        return pd.Series()
    
    if not pd.api.types.is_datetime64_any_dtype(df["Date d'entrée"]):
        df["Date d'entrée"] = pd.to_datetime(df["Date d'entrée"], errors='coerce')

    # Note: Logic slightly changed, we don't strictly filter >= cutoff inside the mask 
    # if we want the reindex to handle the "Last 24 months" window strictly.
    # But strictly speaking, the data might be older.
    # Let's define the mask for the Category only, then let the helper handle the date window.
    
    df_clean = df.dropna(subset=["Date d'entrée"])
    mask = (df_clean['Type de projet'].str.lower() == 'commerce')
    
    return get_monthly_counts(df_clean, mask)


def count_commerce_projects_smart(df):
    """
    Calculates the monthly counts of rows where 'Type de projet' is 'Commerce'
    AND 'Cce Smart / Euklead / Autres' is 'Smart'.
    """
    if df is None:
        return pd.Series()
    
    if not pd.api.types.is_datetime64_any_dtype(df["Date d'entrée"]):
        df["Date d'entrée"] = pd.to_datetime(df["Date d'entrée"], errors='coerce')
        
    df_clean = df.dropna(subset=["Date d'entrée"])

    mask = (
        (df_clean['Type de projet'].str.lower() == 'commerce') & 
        (df_clean['Cce Smart / Euklead / Autres'].str.lower() == 'smart')
    )
    
    return get_monthly_counts(df_clean, mask)
