import pandas as pd
from datetime import datetime, timedelta

def get_monthly_counts(df, mask, date_col="Date d'entrée"):
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
    # Use the specified date column
    if date_col not in filtered_df.columns:
         print(f"Warning: Column {date_col} not found for resampling. Returning 0s.")
         return pd.Series(0, index=full_range)

    # Ensure date type
    if not pd.api.types.is_datetime64_any_dtype(filtered_df[date_col]):
        filtered_df[date_col] = pd.to_datetime(filtered_df[date_col], errors='coerce')
    
    # Drop rows with invalid dates in the target column
    filtered_df = filtered_df.dropna(subset=[date_col])

    filtered_df = filtered_df.set_index(date_col)
    
    # Resample and count
    # Reindex fills missing months with 0
    monthly_counts = filtered_df.resample('MS').size().reindex(full_range, fill_value=0)
    
    return monthly_counts

def filter_data(df, project_type, associates=None, categories=None, is_signed=False):
    """
    Filters the DataFrame based on 'Type de projet', optionally 'Associé', 'Catégorie', 
    and 'Signed' status (Etat 1-4).
    """
    if df is None:
        return pd.DataFrame()

    # Create a copy to avoid SettingWithCopy warnings on the original df
    df_clean = df.copy()

    # Pre-processing dates if not already done (good practice to check)
    if not pd.api.types.is_datetime64_any_dtype(df_clean["Date d'entrée"]):
        df_clean["Date d'entrée"] = pd.to_datetime(df_clean["Date d'entrée"], errors='coerce')
    
    # Also ensure Date de signature is datetime if we might need it (though strictly handled in get_monthly_counts now)
    if "Date de signature" in df_clean.columns and not pd.api.types.is_datetime64_any_dtype(df_clean["Date de signature"]):
         df_clean["Date de signature"] = pd.to_datetime(df_clean["Date de signature"], errors='coerce')
    
    # Basic mask: Type de projet
    # Using case insensitive match
    # Handle NaN in Type de projet
    mask = df_clean['Type de projet'].astype(str).str.strip().str.lower() == project_type.lower()

    if associates:
        # Normalize associates list to lower case for comparison
        associates_lower = [a.lower() for a in associates]
        # Normalize column content
        col_associates = df_clean['Associé'].astype(str).str.strip().str.lower()
        mask = mask & col_associates.isin(associates_lower)

    if categories:
        # Normalize categories list to lower case for comparison
        categories_lower = [c.lower() for c in categories]
        # Normalize column content
        # Note: 'Catégorie' column existence should be checked or assumed present based on requirements
        if 'Catégorie' in df_clean.columns:
            col_categories = df_clean['Catégorie'].astype(str).str.strip().str.lower()
            mask = mask & col_categories.isin(categories_lower)
        else:
            # If asking to filter by category but column missing, return empty or warn?
            # Assuming column exists as per requirements. If not, safe to return empty intersection.
            print("Warning: 'Catégorie' column not found.")
            return pd.DataFrame() # returns empty if criteria cannot be met

    if is_signed:
        # Check if ANY of Etat 1, Etat 2, Etat 3, Etat 4 is "Signé"
        # Columns to check
        state_cols = ["Etat 1", "Etat 2", "Etat 3", "Etat 4"]
        # Ensure they exist
        existing_cols = [c for c in state_cols if c in df_clean.columns]
        
        if not existing_cols:
            print("Warning: No 'Etat' columns found for signed check.")
            return pd.DataFrame()

        # Build a mask: any of the columns == "signé" (case insensitive)
        signed_mask = pd.Series(False, index=df_clean.index)
        for col in existing_cols:
            # Check for 'signé' match
            col_is_signed = df_clean[col].astype(str).str.strip().str.lower() == "signé"
            signed_mask = signed_mask | col_is_signed
        
        mask = mask & signed_mask

    return df_clean[mask]

def count_projects(df, project_type, associates=None, categories=None, is_signed=False):
    """
    Calculates monthly counts for a given project type and filtering by associates, categories, or signed status.
    """
    filtered_df = filter_data(df, project_type, associates, categories, is_signed)

    if filtered_df.empty:
         # Return empty series 
         # Need to call get_monthly_counts with empty DF to get zero-filled series with correct index
         # Just creating an empty DF with same columns
         pass 

    # We need a mask for get_monthly_counts relative to filtered_df
    mask = pd.Series(True, index=filtered_df.index)
    
    # Determine which date column to use
    if is_signed:
        target_date_col = "Date de signature"
    else:
        target_date_col = "Date d'entrée"
        
    return get_monthly_counts(filtered_df, mask, date_col=target_date_col)

