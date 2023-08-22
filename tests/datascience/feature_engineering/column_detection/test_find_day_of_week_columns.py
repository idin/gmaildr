"""Tests for find_day_of_week_columns function."""

import pandas as pd
from gmaildr.datascience.feature_engineering.column_detection.find_day_of_week_columns import find_day_of_week_columns


def test_find_day_of_week_columns_numeric_0_to_6():
    """Test finding day-of-week columns with 0-6 range."""
    data = {
        'day_of_week': [0, 1, 2, 3, 4, 5, 6],
        'day_of_week_2': [1, 1, 2, 3, 4, 5, 7],
        'numeric_column': [0, 1, 2, 3, 4, 5, 6],
        'bad_name': [0, 1, 2, 3, 4, 5, 6],
        'day_of_week_bad_values': [0, 1, 2, 3, 4, 5, 8]
    }
    dataframe = pd.DataFrame(data)
    
    result = find_day_of_week_columns(dataframe)
    
    assert 'day_of_week' in result
    assert 'day_of_week_2' in result  # This is valid 1-7 range
    assert 'numeric_column' not in result  # Wrong name
    assert 'bad_name' not in result  # Wrong name  
    assert 'day_of_week_bad_values' not in result  # Has 8 which is outside both ranges
    assert len(result) == 2


def test_find_day_of_week_columns_numeric_1_to_7():
    """Test finding day-of-week columns with 1-7 range."""
    data = {
        'weekday': [1, 2, 3, 4, 5, 6, 7],
        'week_day_random_numbers': [10, 20, 30, 40, 50, 60, 70],
        'week_DAY_': [0, 1, 2, 3, 4, 5, 6]
    }
    dataframe = pd.DataFrame(data)
    
    result = find_day_of_week_columns(dataframe)
    
    assert 'weekday' in result
    assert 'random_numbers' not in result
    assert len(result) == 1


def test_find_day_of_week_columns_string_full_names():
    """Test finding day-of-week columns with full day names."""
    data = {
        'day_name': ['monday', 'tuesday', 'wednesday', 'thursday', 'friday'],
        'text_column': ['apple', 'banana', 'cherry', 'date', 'elderberry'],
        'another_text_column': ['monday', 'tuesday', 'wednesday', 'thursday', 'friday'],
    }
    dataframe = pd.DataFrame(data)
    
    result = find_day_of_week_columns(dataframe)
    
    assert 'day_name' in result
    assert 'text_column' not in result
    assert len(result) == 1


def test_find_day_of_week_columns_string_abbreviations():
    """Test finding day-of-week columns with day abbreviations."""
    data = {
        'dow': ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'],
        'other_text': ['red', 'blue', 'green', 'yellow', 'orange', 'purple', 'pink'],
        'another_text_column': ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'],
        'day_of_week_bad_values': ['mon', 'tue', 'wed', 'apple', 'fri', 'sat', 'sun']
    }
    dataframe = pd.DataFrame(data)
    
    result = find_day_of_week_columns(dataframe)
    
    assert 'dow' in result
    assert 'other_text' not in result
    assert len(result) == 1


def test_find_day_of_week_columns_multiple_valid():
    """Test finding multiple valid day-of-week columns."""
    data = {
        'day_0_to_6': [0, 1, 2, 3, 4, 5, 6],
        'day_1_to_7': [1, 2, 3, 4, 5, 6, 7],
        'weekday_names': ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'],
        'numeric_column': [100, 200, 300, 400, 500, 600, 700],
        'bad_name_for_column': ['tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    }
    dataframe = pd.DataFrame(data)
    
    result = find_day_of_week_columns(dataframe)
    
    assert 'day_0_to_6' in result
    assert 'day_1_to_7' in result
    assert 'weekday_names' in result
    assert 'numeric_column' not in result
    assert len(result) == 3


def test_find_day_of_week_columns_invalid_values():
    """Test that columns with invalid values are not detected."""
    data = {
        'invalid_weekday': [10, 20, 30, 40, 50],  # Invalid values but matching name
        'day_of_week_invalid': ['apple', 'banana', 'cherry', 'date', 'elderberry'],  # Invalid string values
        'numeric_column': [1, 2, 3, 4, 5]
    }
    dataframe = pd.DataFrame(data)
    
    result = find_day_of_week_columns(dataframe)
    
    assert len(result) == 0


def test_find_day_of_week_columns_empty_dataframe():
    """Test finding day-of-week columns in empty DataFrame."""
    dataframe = pd.DataFrame()
    
    result = find_day_of_week_columns(dataframe)
    
    assert result == []


def test_find_day_of_week_columns_no_matches():
    """Test finding day-of-week columns when none exist."""
    data = {
        'hour_column': [0, 6, 12, 18, 23],
        'month_column': [1, 6, 12, 1, 6],
        'random_text': ['apple', 'banana', 'cherry', 'date', 'elderberry']
    }
    dataframe = pd.DataFrame(data)
    
    result = find_day_of_week_columns(dataframe)
    
    assert result == []


def test_find_day_of_week_columns_with_nan():
    """Test finding day-of-week columns with NaN values."""
    data = {
        'weekday_with_nan': [0, 1, 2, None, 4, 5, 6],
        'other_column': [10, 20, 30, 40, 50, 60, 70]
    }
    dataframe = pd.DataFrame(data)
    
    result = find_day_of_week_columns(dataframe)
    
    assert 'weekday_with_nan' in result
    assert 'other_column' not in result
    assert len(result) == 1
