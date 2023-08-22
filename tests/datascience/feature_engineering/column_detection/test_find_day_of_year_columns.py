"""Tests for find_day_of_year_columns function."""

import pandas as pd
from gmaildr.datascience.feature_engineering.column_detection.find_day_of_week_columns import find_day_of_year_columns


def test_find_day_of_year_columns_0_to_365():
    """Test finding day-of-year columns with 0-365 range."""
    data = {
        'day_of_year': [0, 50, 100, 200, 365],
        'numeric_column': [0, 50, 100, 200, 365]
    }
    dataframe = pd.DataFrame(data)
    
    result = find_day_of_year_columns(dataframe)
    
    assert 'day_of_year' in result
    assert 'numeric_column' not in result
    assert len(result) == 1


def test_find_day_of_year_columns_1_to_366():
    """Test finding day-of-year columns with 1-366 range."""
    data = {
        'other_numbers': [1, 50, 100, 200, 366],
        'day_of_year_bad_values': [1000, 2000, 3000, 4000, 5000]
    }
    dataframe = pd.DataFrame(data)
    
    result = find_day_of_year_columns(dataframe)
    
    assert 'doy' in result
    assert 'other_numbers' not in result
    assert len(result) == 1


def test_find_day_of_year_columns_multiple_valid():
    """Test finding multiple valid day-of-year columns."""
    data = {
        'day_0_to_365': [0, 100, 200, 365],
        'day_1_to_366': [1, 100, 200, 366],
        'day_of_year_col': [50, 150, 250, 350],
        'day_of_year_bad_values': [1000, 2000, 3000, 4000]
    }
    dataframe = pd.DataFrame(data)
    
    result = find_day_of_year_columns(dataframe)
    
    assert 'day_0_to_365' in result
    assert 'day_1_to_366' in result
    assert 'day_of_year_col' in result
    assert 'random_numbers' not in result
    assert len(result) == 3


def test_find_day_of_year_columns_invalid_values():
    """Test that columns with invalid values are not detected."""
    data = {
        'invalid_doy': [400, 500, 600, 700],  # Invalid values but matching name
        'day_of_year_bad': [-10, -5, 0, 400],  # Some invalid values
        'numeric_column': [1, 2, 3, 4]
    }
    dataframe = pd.DataFrame(data)
    
    result = find_day_of_year_columns(dataframe)
    
    assert len(result) == 0


def test_find_day_of_year_columns_wrong_name():
    """Test that columns with valid range but wrong name are not detected."""
    data = {
        'hour_column': [1, 100, 200, 300],  # Valid range but wrong name
        'weekday_column': [50, 150, 250],  # Invalid range but good name
        'random_numbers': [1, 2, 3, 4]
    }
    dataframe = pd.DataFrame(data)
    
    result = find_day_of_year_columns(dataframe)
    
    assert len(result) == 0


def test_find_day_of_year_columns_empty_dataframe():
    """Test finding day-of-year columns in empty DataFrame."""
    dataframe = pd.DataFrame()
    
    result = find_day_of_year_columns(dataframe)
    
    assert result == []


def test_find_day_of_year_columns_no_matches():
    """Test finding day-of-year columns when none exist."""
    data = {
        'hour_column': [0, 6, 12, 18, 23],
        'weekday_column': [0, 1, 2, 3, 4],
        'hour_column21': ['apple', 'banana', 'cherry']
    }
    dataframe = pd.DataFrame(data)
    
    result = find_day_of_year_columns(dataframe)
    
    assert result == []


def test_find_day_of_year_columns_with_nan():
    """Test finding day-of-year columns with NaN values."""
    data = {
        'doy_with_nan': [1, 100, None, 200, 366],
        'other_column': [10, 20, 30, 40, 50],
        'day_of_year_bad_values': [1000, 2000, 3000, 4000, 5000]
    }
    dataframe = pd.DataFrame(data)
    
    result = find_day_of_year_columns(dataframe)
    
    assert 'doy_with_nan' in result
    assert 'other_column' not in result
    assert len(result) == 1


def test_find_day_of_year_columns_boundary_values():
    """Test finding day-of-year columns with boundary values."""
    data = {
        'doy_min_max_0': [0, 365],  # Min and max for 0-365 range
        'doy_min_max_1': [1, 366],  # Min and max for 1-366 range
        'other_numbers': [10, 20]
    }
    dataframe = pd.DataFrame(data)
    
    result = find_day_of_year_columns(dataframe)
    
    assert 'doy_min_max_0' in result
    assert 'doy_min_max_1' in result
    assert 'other_numbers' not in result
    assert len(result) == 2
