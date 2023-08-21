import pandas as pd
from typing import List


def df_must_have_columns(df: pd.DataFrame, columns: List[str]) -> bool:
    """
    Check if a DataFrame has all the required columns.
    
    Args:
        df: DataFrame to check
        columns: List of column names that must be present
        
    Returns:
        True if all columns are present
        
    Raises:
        KeyError: If any required columns are missing
    """
    missing_columns = [col for col in columns if col not in df.columns]
    if missing_columns:
        raise KeyError(f"DataFrame is missing the following columns: {missing_columns}")
    return True


def df_must_not_have_columns(df: pd.DataFrame, columns: List[str]) -> bool:
    """
    Check if a DataFrame does NOT have any of the forbidden columns.
    
    Args:
        df: DataFrame to check
        columns: List of column names that must NOT be present
        
    Returns:
        True if none of the forbidden columns are present
        
    Raises:
        KeyError: If any forbidden columns are found
    """
    still_has_columns = [col for col in columns if col in df.columns]
    if still_has_columns:
        raise KeyError(f"DataFrame must not have the following columns: {still_has_columns}")
    return True
