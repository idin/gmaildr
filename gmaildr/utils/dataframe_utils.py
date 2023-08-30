"""
DataFrame utility functions for column validation and checking.
"""

import pandas as pd
from typing import List, Union


def has_all_columns(dataframe: pd.DataFrame, columns: Union[List[str], str]) -> bool:
    """
    Check if a DataFrame has all the specified columns.
    
    Args:
        dataframe: pandas DataFrame to check
        columns: List of column names or single column name to check for
        
    Returns:
        bool: True if DataFrame has all specified columns, False otherwise
        
    Examples:
        >>> df = pd.DataFrame({'a': [1, 2], 'b': [3, 4], 'c': [5, 6]})
        >>> has_all_columns(df, ['a', 'b'])
        True
        >>> has_all_columns(df, ['a', 'x'])
        False
        >>> has_all_columns(df, 'a')
        True
    """
    if isinstance(columns, str):
        columns = [columns]
    
    return all(col in dataframe.columns for col in columns)


def has_none_of_columns(dataframe: pd.DataFrame, columns: Union[List[str], str]) -> bool:
    """
    Check if a DataFrame has none of the specified columns.
    
    Args:
        dataframe: pandas DataFrame to check
        columns: List of column names or single column name to check for
        
    Returns:
        bool: True if DataFrame has none of the specified columns, False otherwise
        
    Examples:
        >>> df = pd.DataFrame({'a': [1, 2], 'b': [3, 4], 'c': [5, 6]})
        >>> has_none_of_columns(df, ['x', 'y'])
        True
        >>> has_none_of_columns(df, ['a', 'x'])
        False
        >>> has_none_of_columns(df, 'x')
        True
    """
    if isinstance(columns, str):
        columns = [columns]
    
    return not any(col in dataframe.columns for col in columns)


def get_missing_columns(dataframe: pd.DataFrame, columns: Union[List[str], str]) -> List[str]:
    """
    Get list of columns that are missing from the DataFrame.
    
    Args:
        dataframe: pandas DataFrame to check
        columns: List of column names or single column name to check for
        
    Returns:
        List[str]: List of column names that are missing from the DataFrame
        
    Examples:
        >>> df = pd.DataFrame({'a': [1, 2], 'b': [3, 4], 'c': [5, 6]})
        >>> get_missing_columns(df, ['a', 'b', 'x', 'y'])
        ['x', 'y']
        >>> get_missing_columns(df, ['a', 'b'])
        []
    """
    if isinstance(columns, str):
        columns = [columns]
    
    return [col for col in columns if col not in dataframe.columns]


def get_existing_columns(dataframe: pd.DataFrame, columns: Union[List[str], str]) -> List[str]:
    """
    Get list of columns that exist in the DataFrame.
    
    Args:
        dataframe: pandas DataFrame to check
        columns: List of column names or single column name to check for
        
    Returns:
        List[str]: List of column names that exist in the DataFrame
        
    Examples:
        >>> df = pd.DataFrame({'a': [1, 2], 'b': [3, 4], 'c': [5, 6]})
        >>> get_existing_columns(df, ['a', 'b', 'x', 'y'])
        ['a', 'b']
        >>> get_existing_columns(df, ['x', 'y'])
        []
    """
    if isinstance(columns, str):
        columns = [columns]
    
    return [col for col in columns if col in dataframe.columns]
