"""Tests for find_hour_of_day_columns function."""

import pandas as pd
from gmaildr.datascience.feature_engineering.column_detection.find_day_of_week_columns import find_hour_of_day_columns


def test_find_hour_of_day_columns_0_to_23():
    """Test finding hour-of-day columns with 0-23 range."""
    data = {
        'hour_of_day': [0, 6, 12, 18, 23],
        'hour_of_day2': [100, 200, 300, 400, 500],
        'numbers': [0, 1, 2, 3, 4]
    }
    dataframe = pd.DataFrame(data)
    
    result = find_hour_of_day_columns(dataframe)
    
    assert 'hour_of_day' in result
    assert 'numeric_column' not in result
    assert len(result) == 1


def test_find_hour_of_day_columns_1_to_24():
    """Test finding hour-of-day columns with 1-24 range."""
    data = {
        'hour': [1, 6, 12, 18, 24],
        'hour2': [100, 200, 300, 400, 500]
    }
    dataframe = pd.DataFrame(data)
    
    result = find_hour_of_day_columns(dataframe)
    
    assert 'hour' in result
    assert 'other_numbers' not in result
    assert len(result) == 1


def test_find_hour_of_day_columns_hod_abbreviation():
    """Test finding hour-of-day columns with 'hod' abbreviation."""
    data = {
        'hod': [0, 12, 23],
        'hod_2': [1000, 2000, 3000]
    }
    dataframe = pd.DataFrame(data)
    
    result = find_hour_of_day_columns(dataframe)
    
    assert 'hod' in result
    assert 'random_column' not in result
    assert len(result) == 1


def test_find_hour_of_day_columns_multiple_valid():
    """Test finding multiple valid hour-of-day columns."""
    data = {
        'hour_24_format': [0, 6, 12, 18, 23],
        'hour_12_format': [1, 6, 12, 6, 11],
        'hod_column': [0, 12, 23],
        'numeric_column': [100, 200, 300]
    }
    dataframe = pd.DataFrame(data)
    
    result = find_hour_of_day_columns(dataframe)
    
    assert 'hour_24_format' in result
    assert 'hour_12_format' in result
    assert 'hod_column' in result
    assert 'numeric_column' not in result
    assert len(result) == 3


def test_find_hour_of_day_columns_invalid_values():
    """Test that columns with invalid values are not detected."""
    data = {
        'invalid_hour': [25, 30, 35, 40],  # Invalid values but matching name
        'hour_of_day_bad': [-5, 0, 12, 25],  # Some invalid values
        'numeric_column': [1, 2, 3, 4]
    }
    dataframe = pd.DataFrame(data)
    
    result = find_hour_of_day_columns(dataframe)
    
    assert len(result) == 0


def test_find_hour_of_day_columns_wrong_name():
    """Test that columns with valid range but wrong name are not detected."""
    data = {
        'day_column': [1, 6, 12, 18, 23],  # Valid range but wrong name
        'weekday_column': [0, 6, 12, 18],  # Valid range but wrong name
        'random_numbers': [1, 2, 3, 4, 5]
    }
    dataframe = pd.DataFrame(data)
    
    result = find_hour_of_day_columns(dataframe)
    
    assert len(result) == 0


def test_find_hour_of_day_columns_empty_dataframe():
    """Test finding hour-of-day columns in empty DataFrame."""
    dataframe = pd.DataFrame()
    
    result = find_hour_of_day_columns(dataframe)
    
    assert result == []


def test_find_hour_of_day_columns_no_matches():
    """Test finding hour-of-day columns when none exist."""
    data = {
        'day_column': [1, 100, 200, 300],
        'weekday_column': [0, 1, 2, 3, 4],
        'text_column': ['morning', 'noon', 'evening']
    }
    dataframe = pd.DataFrame(data)
    
    result = find_hour_of_day_columns(dataframe)
    
    assert result == []


def test_find_hour_of_day_columns_with_nan():
    """Test finding hour-of-day columns with NaN values."""
    data = {
        'hour_with_nan': [0, 6, None, 18, 23],
        'other_column': [10, 20, 30, 40, 50]
    }
    dataframe = pd.DataFrame(data)
    
    result = find_hour_of_day_columns(dataframe)
    
    assert 'hour_with_nan' in result
    assert 'other_column' not in result
    assert len(result) == 1


def test_find_hour_of_day_columns_boundary_values():
    """Test finding hour-of-day columns with boundary values."""
    data = {
        'hour_0_23': [0, 23],  # Min and max for 0-23 range
        'hour_1_24': [1, 24],  # Min and max for 1-24 range
        'other_numbers': [100, 200]
    }
    dataframe = pd.DataFrame(data)
    
    result = find_hour_of_day_columns(dataframe)
    
    assert 'hour_0_23' in result
    assert 'hour_1_24' in result
    assert 'other_numbers' not in result
    assert len(result) == 2


def test_find_hour_of_day_columns_single_value():
    """Test finding hour-of-day columns with single valid value."""
    data = {
        'hour_single': [12],  # Single valid hour value
        'other_single': [100]  # Single value but not hour-related name
    }
    dataframe = pd.DataFrame(data)
    
    result = find_hour_of_day_columns(dataframe)
    
    assert 'hour_single' in result
    assert 'other_single' not in result
    assert len(result) == 1
