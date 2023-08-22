"""Tests for is_integer_column function."""

import pandas as pd
import pytest
from gmaildr.datascience.feature_engineering.column_detection.find_integer_columns import is_integer_column


def test_is_integer_column_pure_integers():
    """Test is_integer_column with pure integer values."""
    values = pd.Series([1, 2, 3, 4, 5])
    
    result = is_integer_column(values)
    
    assert result is True


def test_is_integer_column_float_integers():
    """Test is_integer_column with float values that are integers."""
    values = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0])
    
    result = is_integer_column(values)
    
    assert result is True


def test_is_integer_column_mixed_float_integers():
    """Test is_integer_column with mixed float integers and NaN."""
    values = pd.Series([1.0, 2.0, None, 4.0, 5.0])
    
    result = is_integer_column(values)
    
    assert result is True


def test_is_integer_column_non_integers():
    """Test is_integer_column with non-integer float values."""
    values = pd.Series([1.5, 2.3, 3.7, 4.1])
    
    result = is_integer_column(values)
    
    assert result is False


def test_is_integer_column_mixed_integers_and_floats():
    """Test is_integer_column with mix of integers and non-integer floats."""
    values = pd.Series([1.0, 2.5, 3.0, 4.7])
    
    result = is_integer_column(values)
    
    assert result is False


def test_is_integer_column_string_values():
    """Test is_integer_column with string values."""
    values = pd.Series(['1', '2', '3', '4'])
    
    result = is_integer_column(values)
    
    assert result is False


def test_is_integer_column_empty_series():
    """Test is_integer_column with empty series."""
    values = pd.Series([], dtype='float64')
    
    result = is_integer_column(values)
    
    assert result is True


def test_is_integer_column_all_nan():
    """Test is_integer_column with all NaN values."""
    values = pd.Series([None, None, None])
    
    result = is_integer_column(values)
    
    assert result is True


def test_is_integer_column_negative_integers():
    """Test is_integer_column with negative integer values."""
    values = pd.Series([-1, -2, -3, 0, 1, 2])
    
    result = is_integer_column(values)
    
    assert result is True


def test_is_integer_column_negative_float_integers():
    """Test is_integer_column with negative float values that are integers."""
    values = pd.Series([-1.0, -2.0, 0.0, 1.0, 2.0])
    
    result = is_integer_column(values)
    
    assert result is True


def test_is_integer_column_large_numbers():
    """Test is_integer_column with large integer values."""
    values = pd.Series([1000000, 2000000, 3000000])
    
    result = is_integer_column(values)
    
    assert result is True


def test_is_integer_column_boolean_values():
    """Test is_integer_column with boolean values."""
    values = pd.Series([True, False, True, False])
    
    result = is_integer_column(values)
    
    assert result is True  # Booleans are considered integers in pandas


def test_is_integer_column_type_error():
    """Test is_integer_column with invalid input type."""
    with pytest.raises(TypeError, match="Expected pandas Series"):
        is_integer_column([1, 2, 3, 4])


def test_is_integer_column_zero_values():
    """Test is_integer_column with zero values."""
    values = pd.Series([0, 0.0, 0, 0.0])
    
    result = is_integer_column(values)
    
    assert result is True


def test_is_integer_column_scientific_notation():
    """Test is_integer_column with scientific notation that represents integers."""
    values = pd.Series([1e2, 2e1, 3e0])  # 100.0, 20.0, 3.0
    
    result = is_integer_column(values)
    
    assert result is True
