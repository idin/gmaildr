import numpy as np
import pandas as pd

def get_numeric_columns(df: pd.DataFrame) -> list[str]:
    """
    Get the numeric columns of a DataFrame without creating a new DataFrame.
    """
    # Get numeric columns by checking dtype.kind directly
    # 'i' = integer, 'f' = float, 'c' = complex
    numeric_cols = [
        col for col in df.columns 
        if df[col].dtype.kind in 'ifc'
    ]
    return numeric_cols