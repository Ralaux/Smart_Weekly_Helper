import pandas as pd
from datetime import datetime, timedelta
from typing import List, Optional, Union

def get_monthly_counts(
    df: pd.DataFrame, 
    mask: Union[pd.Series, List[bool]], 
    date_col: str = "Date d'entrée"
) -> pd.Series:
    """
    Resample filtered data by month over the last 24 months.

    Args:
        df (pd.DataFrame): The source dataframe.
        mask (pd.Series): Boolean mask to apply before resampling.
        date_col (str): The column name to use for the date index. 
                        Defaults to "Date d'entrée".

    Returns:
        pd.Series: A Series with DatetimeIndex (Monthly Start) and count values.
    """
    # Define last 24 months range (ending current month)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365*2)
    
    # Create a full index of months ('MS' is Month Start)
    full_range = pd.date_range(start=start_date, end=end_date, freq='MS', normalize=True)
    
    # Filter data
    filtered_df = df[mask].copy()
    
    # Check if date column exists
    if date_col not in filtered_df.columns:
         print(f"Warning: Column '{date_col}' not found for resampling. Returning 0s.")
         return pd.Series(0, index=full_range)

    # Ensure date type
    if not pd.api.types.is_datetime64_any_dtype(filtered_df[date_col]):
        filtered_df[date_col] = pd.to_datetime(filtered_df[date_col], errors='coerce')
    
    # Drop rows with invalid dates in the target column
    filtered_df = filtered_df.dropna(subset=[date_col])

    # Set index for resampling
    filtered_df = filtered_df.set_index(date_col)
    
    # Resample and count, reindexing to ensure all months are present
    monthly_counts = filtered_df.resample('MS').size().reindex(full_range, fill_value=0)
    
    return monthly_counts

def filter_data(
    df: pd.DataFrame, 
    project_type: str, 
    associates: Optional[List[str]] = None, 
    categories: Optional[List[str]] = None, 
    is_signed: bool = False
) -> pd.DataFrame:
    """
    Filters the DataFrame based on criteria including project type, associates, 
    categories, and signed status.

    Args:
        df (pd.DataFrame): Input dataframe.
        project_type (str): 'Commerce' or 'Analyse'.
        associates (Optional[List[str]]): List of associate initials/names.
        categories (Optional[List[str]]): List of categories.
        is_signed (bool): If True, filters for projects strictly marked as "Signé".

    Returns:
        pd.DataFrame: Filtered dataframe.
    """
    if df is None:
        return pd.DataFrame()

    df_clean = df.copy()

    # ensure date columns are datetime objects
    date_cols = ["Date d'entrée", "Date de signature"]
    for col in date_cols:
        if col in df_clean.columns and not pd.api.types.is_datetime64_any_dtype(df_clean[col]):
            df_clean[col] = pd.to_datetime(df_clean[col], errors='coerce')
    
    # Filter by Project Type (case insensitive)
    if 'Type de projet' not in df_clean.columns:
        return pd.DataFrame()
        
    mask = df_clean['Type de projet'].astype(str).str.strip().str.lower() == project_type.lower()

    # Filter by Associates
    if associates:
        associates_lower = [a.lower() for a in associates]
        col_associates = df_clean['Associé'].astype(str).str.strip().str.lower()
        mask = mask & col_associates.isin(associates_lower)

    # Filter by Categories
    if categories:
        categories_lower = [c.lower() for c in categories]
        if 'Catégorie' in df_clean.columns:
            col_categories = df_clean['Catégorie'].astype(str).str.strip().str.lower()
            mask = mask & col_categories.isin(categories_lower)
        else:
            print("Warning: 'Catégorie' column not found.")
            return pd.DataFrame()

    # Filter by Signed Status
    if is_signed:
        state_cols = ["Etat 1", "Etat 2", "Etat 3", "Etat 4"]
        existing_cols = [c for c in state_cols if c in df_clean.columns]
        
        if not existing_cols:
            print("Warning: No 'Etat' columns found for signed check.")
            return pd.DataFrame()

        # Check if ANY of the state columns contain "signé"
        signed_mask = pd.Series(False, index=df_clean.index)
        for col in existing_cols:
            col_is_signed = df_clean[col].astype(str).str.strip().str.lower() == "signé"
            signed_mask = signed_mask | col_is_signed
        
        mask = mask & signed_mask

    return df_clean[mask]

def count_projects(
    df: pd.DataFrame, 
    project_type: str, 
    associates: Optional[List[str]] = None, 
    categories: Optional[List[str]] = None, 
    is_signed: bool = False
) -> pd.Series:
    """
    Calculates monthly counts for filtered projects.

    Args:
        df (pd.DataFrame): Input dataframe.
        project_type (str): 'Commerce' or 'Analyse'.
        associates (Optional[List[str]]): List of associates.
        categories (Optional[List[str]]): List of categories.
        is_signed (bool): Whether to look for signed projects only.

    Returns:
        pd.Series: Monthly counts for the last 24 months.
    """
    filtered_df = filter_data(df, project_type, associates, categories, is_signed)

    # If empty, we still pass it to get_monthly_counts to get a zero-filled Series
    # with the correct index range.
    
    # Create a mask of all True for the filtered subset
    mask = pd.Series(True, index=filtered_df.index)
    
    # Select appropriate date column logic
    target_date_col = "Date de signature" if is_signed else "Date d'entrée"
        
    return get_monthly_counts(filtered_df, mask, date_col=target_date_col)
