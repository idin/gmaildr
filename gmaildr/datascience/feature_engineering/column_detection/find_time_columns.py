"""Find time columns in a DataFrame."""

from typing import List
import pandas as pd


def find_time_columns(
    dataframe: pd.DataFrame, *,
    include_datetime: bool = True,
    include_time: bool = True,
    check_object_columns: bool = True
) -> List[str]:
    """Find time columns in a DataFrame.
    
    Identifies columns containing time information including datetime
    columns (which contain time components) and pure time columns.
    
    Args:
        dataframe: The input DataFrame to analyze.
        include_datetime: Whether to include datetime dtype columns
            (which contain time components).
        include_time: Whether to include time dtype columns.
        check_object_columns: Whether to check object columns for
            parseable time strings.
    
    Returns:
        List[str]: List of column names identified as containing time.
    
    Raises:
        TypeError: If dataframe is not a pandas DataFrame.
        TypeError: If any boolean parameters are not boolean type.
    """
    if not isinstance(dataframe, pd.DataFrame):
        raise TypeError(f"Expected pandas DataFrame, got {type(dataframe)}")
    
    if not isinstance(include_datetime, bool):
        raise TypeError(f"Expected bool for include_datetime, got {type(include_datetime)}")
    
    if not isinstance(include_time, bool):
        raise TypeError(f"Expected bool for include_time, got {type(include_time)}")
    
    if not isinstance(check_object_columns, bool):
        raise TypeError(f"Expected bool for check_object_columns, got {type(check_object_columns)}")
    
    time_columns = []
    
    for column in dataframe.columns:
        dtype = dataframe[column].dtype
        
        # Check for datetime dtypes (which include time)
        if include_datetime and pd.api.types.is_datetime64_any_dtype(dtype):
            time_columns.append(column)
        # Check for time dtypes
        elif include_time and pd.api.types.is_timedelta64_dtype(dtype):
            time_columns.append(column)
        elif dtype == 'object' and check_object_columns:
            # Check if it's a time column by looking for time patterns
            sample_values = dataframe[column].dropna().head(10)
            if len(sample_values) > 0:
                try:
                    # Try to parse as time
                    parsed_times = pd.to_datetime(sample_values, format='%H:%M:%S', errors='coerce')
                    if parsed_times.isna().sum() < len(sample_values):
                        time_columns.append(column)
                        continue
                    
                    # Try other time formats
                    parsed_times = pd.to_datetime(sample_values, format='%H:%M', errors='coerce')
                    if parsed_times.isna().sum() < len(sample_values):
                        time_columns.append(column)
                except (ValueError, TypeError):
                    continue
    
    return time_columns
