from typing import Optional, List, Set, Tuple, Union
import pandas as pd


def include_exclude_columns(
    df: pd.DataFrame, *,
    include_columns: Optional[Union[List[str], Set[str], Tuple[str, ...], str]] = None, 
    exclude_columns: Optional[Union[List[str], Set[str], Tuple[str, ...], str]] = None) -> List[str]:
    """
    Include or exclude columns from a DataFrame.
    Return a list of columns that are included.

    Args:
        df: DataFrame to process
        include_columns: Columns to include (if None, all columns are included)
        exclude_columns: Columns to exclude (if None, no columns are excluded)

    Returns:
        List of columns that are included
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"df must be a pandas DataFrame, got {type(df)}")

    if isinstance(include_columns, str):
        include_columns = [include_columns]
    if isinstance(exclude_columns, str):
        exclude_columns = [exclude_columns]

    all_columns = list(df.columns)

    # If include_columns is None, include all columns
    if include_columns is None:
        include_columns = all_columns
    # If exclude_columns is None, exclude no columns
    if exclude_columns is None:
        exclude_columns = []

    return [col for col in all_columns if col in include_columns and col not in exclude_columns]
