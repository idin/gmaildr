"""Tests for encode_day_of_week functions."""

import pandas as pd
import numpy as np
from gmaildr.datascience.feature_engineering.column_conversion.encode_day_of_week import (
    encode_day_of_week_to_sin,
    encode_day_of_week_to_cos,
    encode_day_of_week_to_sin_cos_series,
    encode_day_of_week_to_sin_cos,
    convert_day_of_week_to_int
)


def test_encode_day_of_week_string_values():
    """Test encoding day-of-week with string values."""
    string_values = pd.Series(['monday', 'tuesday', 'wednesday'])
    
    sin_result = encode_day_of_week_to_sin(string_values)
    cos_result = encode_day_of_week_to_cos(string_values)
    
    # Monday=0 should give sin=0, cos=1
    assert abs(sin_result.iloc[0] - 0.0) < 1e-10
    assert abs(cos_result.iloc[0] - 1.0) < 1e-10
    
    # Tuesday=1 should give sin≈0.866, cos≈0.5
    assert abs(sin_result.iloc[1] - 0.8660254037844386) < 1e-10
    assert abs(cos_result.iloc[1] - 0.5) < 1e-10


def test_encode_day_of_week_0_to_6_integers():
    """Test encoding day-of-week with 0-6 integer values."""
    int_0_6 = pd.Series([0, 1, 2, 3, 4, 5, 6])
    
    sin_result = encode_day_of_week_to_sin(int_0_6)
    cos_result = encode_day_of_week_to_cos(int_0_6)
    
    # 0 should give sin=0, cos=1
    assert abs(sin_result.iloc[0] - 0.0) < 1e-10
    assert abs(cos_result.iloc[0] - 1.0) < 1e-10
    
    # Results should be same length as input
    assert len(sin_result) == 7
    assert len(cos_result) == 7


def test_encode_day_of_week_1_to_7_integers():
    """Test encoding day-of-week with 1-7 integer values."""
    int_1_7 = pd.Series([1, 2, 3, 4, 5, 6, 7])
    
    sin_result = encode_day_of_week_to_sin(int_1_7)
    cos_result = encode_day_of_week_to_cos(int_1_7)
    
    # Results should be same length as input
    assert len(sin_result) == 7
    assert len(cos_result) == 7
    
    # Values should be in valid sin/cos range
    assert all(-1 <= val <= 1 for val in sin_result)
    assert all(-1 <= val <= 1 for val in cos_result)


def test_encode_day_of_week_short_names():
    """Test encoding day-of-week with short day names."""
    short_names = pd.Series(['mon', 'tue', 'wed', 'thu', 'fri'])
    
    sin_result = encode_day_of_week_to_sin(short_names)
    cos_result = encode_day_of_week_to_cos(short_names)
    
    assert len(sin_result) == 5
    assert len(cos_result) == 5
    
    # Mon=0 should give sin=0, cos=1
    assert abs(sin_result.iloc[0] - 0.0) < 1e-10
    assert abs(cos_result.iloc[0] - 1.0) < 1e-10


def test_encode_day_of_week_mixed_case():
    """Test encoding day-of-week with mixed case strings."""
    mixed_case = pd.Series(['Monday', 'TUESDAY', 'WeDnEsDay'])
    
    sin_result = encode_day_of_week_to_sin(mixed_case)
    cos_result = encode_day_of_week_to_cos(mixed_case)
    
    assert len(sin_result) == 3
    assert len(cos_result) == 3


def test_encode_day_of_week_with_nan():
    """Test encoding day-of-week with NaN values."""
    values_with_nan = pd.Series(['monday', None, 'wednesday'])
    
    sin_result = encode_day_of_week_to_sin(values_with_nan)
    cos_result = encode_day_of_week_to_cos(values_with_nan)
    
    # NaN should remain NaN
    assert pd.isna(sin_result.iloc[1])
    assert pd.isna(cos_result.iloc[1])
    
    # Other values should be encoded
    assert not pd.isna(sin_result.iloc[0])
    assert not pd.isna(cos_result.iloc[2])


def test_convert_day_of_week_to_int():
    """Test converting day names to integers."""
    day_names = pd.Series(['monday', 'tuesday', 'sunday'])
    
    result = convert_day_of_week_to_int(day_names)
    
    assert result.iloc[0] == 0  # Monday
    assert result.iloc[1] == 1  # Tuesday  
    assert result.iloc[2] == 6  # Sunday


def test_encode_day_of_week_to_sin_cos_series():
    """Test encoding day-of-week to both sin and cos series."""
    values = pd.Series(['monday', 'tuesday', 'wednesday'])
    
    sin_result, cos_result = encode_day_of_week_to_sin_cos_series(values)
    
    assert len(sin_result) == 3
    assert len(cos_result) == 3
    
    # Monday=0 should give sin=0, cos=1
    assert abs(sin_result.iloc[0] - 0.0) < 1e-10
    assert abs(cos_result.iloc[0] - 1.0) < 1e-10


def test_encode_day_of_week_to_sin_cos_dataframe():
    """Test encoding day-of-week in DataFrame."""
    dataframe = pd.DataFrame({
        'day': ['monday', 'tuesday', 'wednesday'],
        'other_col': [1, 2, 3]
    })
    
    result = encode_day_of_week_to_sin_cos(
        dataframe=dataframe,
        column='day',
        drop_original_columns=True,
        in_place=False
    )
    
    # Should have sin and cos columns
    assert 'day_sin' in result.columns
    assert 'day_cos' in result.columns
    
    # Original column should be dropped
    assert 'day' not in result.columns
    
    # Other column should remain
    assert 'other_col' in result.columns
    
    # Should have same number of rows
    assert len(result) == 3


def test_encode_day_of_week_to_sin_cos_dataframe_keep_original():
    """Test encoding day-of-week in DataFrame keeping original column."""
    dataframe = pd.DataFrame({
        'weekday': ['friday', 'saturday', 'sunday']
    })
    
    result = encode_day_of_week_to_sin_cos(
        dataframe=dataframe,
        column='weekday',
        drop_original_columns=False,
        in_place=False
    )
    
    # Should have all columns
    assert 'weekday' in result.columns
    assert 'weekday_sin' in result.columns
    assert 'weekday_cos' in result.columns


def test_encode_day_of_week_to_sin_cos_dataframe_custom_suffixes():
    """Test encoding day-of-week in DataFrame with custom suffixes."""
    dataframe = pd.DataFrame({
        'day_col': ['monday', 'friday']
    })
    
    result = encode_day_of_week_to_sin_cos(
        dataframe=dataframe,
        column='day_col',
        suffixes=('_sine', '_cosine'),
        in_place=False
    )
    
    assert 'day_col_sine' in result.columns
    assert 'day_col_cosine' in result.columns


def test_encode_day_of_week_to_sin_cos_dataframe_in_place():
    """Test encoding day-of-week in DataFrame in place."""
    dataframe = pd.DataFrame({
        'day': ['tuesday', 'thursday']
    })
    
    result = encode_day_of_week_to_sin_cos(
        dataframe=dataframe,
        column='day',
        in_place=True
    )
    
    # Should return None when in_place=True
    assert result is None
    
    # Original dataframe should be modified
    assert 'day_sin' in dataframe.columns
    assert 'day_cos' in dataframe.columns
