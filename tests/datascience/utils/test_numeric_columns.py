"""
Tests for get_numeric_columns function.
"""

import pandas as pd
import numpy as np

from gmaildr.datascience.utils.numeric_columns import get_numeric_columns


def test_get_numeric_columns_basic():
    """Test get_numeric_columns with basic DataFrame containing mixed types."""
    df = pd.DataFrame({
        'int_col': [1, 2, 3, 4, 5],
        'float_col': [1.1, 2.2, 3.3, 4.4, 5.5],
        'string_col': ['a', 'b', 'c', 'd', 'e'],
        'bool_col': [True, False, True, False, True],
        'complex_col': [1+1j, 2+2j, 3+3j, 4+4j, 5+5j]
    })
    
    result = get_numeric_columns(df)
    
    # Should return only numeric columns
    assert 'int_col' in result
    assert 'float_col' in result
    assert 'complex_col' in result
    assert 'string_col' not in result
    assert 'bool_col' not in result
    assert len(result) == 3


def test_get_numeric_columns_only_numeric():
    """Test get_numeric_columns with DataFrame containing only numeric columns."""
    df = pd.DataFrame({
        'int_col': [1, 2, 3, 4, 5],
        'float_col': [1.1, 2.2, 3.3, 4.4, 5.5],
        'complex_col': [1+1j, 2+2j, 3+3j, 4+4j, 5+5j]
    })
    
    result = get_numeric_columns(df)
    
    # Should return all columns
    assert 'int_col' in result
    assert 'float_col' in result
    assert 'complex_col' in result
    assert len(result) == 3


def test_get_numeric_columns_only_non_numeric():
    """Test get_numeric_columns with DataFrame containing only non-numeric columns."""
    df = pd.DataFrame({
        'string_col': ['a', 'b', 'c', 'd', 'e'],
        'bool_col': [True, False, True, False, True],
        'object_col': [{'a': 1}, {'b': 2}, {'c': 3}, {'d': 4}, {'e': 5}]
    })
    
    result = get_numeric_columns(df)
    
    # Should return empty list
    assert len(result) == 0


def test_get_numeric_columns_empty_dataframe():
    """Test get_numeric_columns with empty DataFrame."""
    df = pd.DataFrame()
    
    result = get_numeric_columns(df)
    
    # Should return empty list
    assert len(result) == 0


def test_get_numeric_columns_with_nan():
    """Test get_numeric_columns with DataFrame containing NaN values."""
    df = pd.DataFrame({
        'int_col': [1, 2, np.nan, 4, 5],
        'float_col': [1.1, np.nan, 3.3, 4.4, 5.5],
        'string_col': ['a', 'b', 'c', 'd', 'e']
    })
    
    result = get_numeric_columns(df)
    
    # Should return numeric columns even with NaN values
    assert 'int_col' in result
    assert 'float_col' in result
    assert 'string_col' not in result
    assert len(result) == 2


def test_get_numeric_columns_with_categorical():
    """Test get_numeric_columns with DataFrame containing categorical columns."""
    df = pd.DataFrame({
        'int_col': [1, 2, 3, 4, 5],
        'cat_col': pd.Categorical(['a', 'b', 'c', 'd', 'e']),
        'string_col': ['a', 'b', 'c', 'd', 'e']
    })
    
    result = get_numeric_columns(df)
    
    # Should return only numeric columns
    assert 'int_col' in result
    assert 'cat_col' not in result
    assert 'string_col' not in result
    assert len(result) == 1


def test_get_numeric_columns_with_datetime():
    """Test get_numeric_columns with DataFrame containing datetime columns."""
    df = pd.DataFrame({
        'int_col': [1, 2, 3, 4, 5],
        'datetime_col': pd.date_range('2023-01-01', periods=5),
        'string_col': ['a', 'b', 'c', 'd', 'e']
    })
    
    result = get_numeric_columns(df)
    
    # Should return only numeric columns (datetime is not numeric)
    assert 'int_col' in result
    assert 'datetime_col' not in result
    assert 'string_col' not in result
    assert len(result) == 1


def test_get_numeric_columns_with_mixed_dtypes():
    """Test get_numeric_columns with DataFrame containing mixed dtypes including object arrays."""
    df = pd.DataFrame({
        'int_col': [1, 2, 3, 4, 5],
        'float_col': [1.1, 2.2, 3.3, 4.4, 5.5],
        'object_col': [1, 'a', 3, 'b', 5],  # Mixed object array
        'string_col': ['a', 'b', 'c', 'd', 'e']
    })
    
    result = get_numeric_columns(df)
    
    # Should return only numeric columns
    assert 'int_col' in result
    assert 'float_col' in result
    assert 'object_col' not in result  # Mixed object array is not numeric
    assert 'string_col' not in result
    assert len(result) == 2
