"""Find date columns in a DataFrame."""

from typing import List
import pandas as pd


def is_date_column(values: pd.Series) -> bool:
    """Check if a column contains date/datetime values.
    
    Args:
        values: Series containing the column values
        
    Returns:
        bool: True if column contains date/datetime values, False otherwise
        
    Raises:
        TypeError: If values is not a pandas Series
    """
    if not isinstance(values, pd.Series):
        raise TypeError(f"Expected pandas Series, got {type(values)}")
    
    return pd.api.types.is_datetime64_any_dtype(values.dtype)


def find_date_columns(dataframe: pd.DataFrame) -> List[str]:
    """Find columns that contain date/datetime values.
    
    Args:
        dataframe: DataFrame to analyze
        
    Returns:
        List[str]: List of column names that contain date/datetime values
        
    Raises:
        TypeError: If dataframe is not a pandas DataFrame
    """
    if not isinstance(dataframe, pd.DataFrame):
        raise TypeError(f"Expected pandas DataFrame, got {type(dataframe)}")
    
    date_columns = []
    
    for column in dataframe.columns:
        if is_date_column(values=dataframe[column]):
            date_columns.append(column)
    
    return date_columns