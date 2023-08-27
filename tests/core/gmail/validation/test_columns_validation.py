"""
Test column definitions and validation.

This module tests that the column definitions in columns.py are accurate
and that validation functions work correctly.
"""

import pytest
import pandas as pd
from gmaildr import Gmail
from gmaildr.data.columns import (
    EMAIL_ML_DF_CORE_COLUMNS, 
    EMAIL_ML_DF_OPTIONAL_COLUMNS,
    EMAIL_ML_DF_COLUMNS,
    EMAIL_ML_SHOULD_NOT_HAVE_COLUMNS
)
# Note: These utility functions were moved inline to avoid datascience module dependency
def df_must_have_columns(df, columns):
    """Check if DataFrame has all required columns."""
    missing_columns = [col for col in columns if col not in df.columns]
    if missing_columns:
        raise KeyError(f"DataFrame is missing the following columns: {missing_columns}")
    return True

def df_must_not_have_columns(df, columns):
    """Check if DataFrame does NOT have any forbidden columns."""
    still_has_columns = [col for col in columns if col in df.columns]
    if still_has_columns:
        raise KeyError(f"DataFrame must not have the following columns: {still_has_columns}")
    return True
from gmaildr.test_utils import get_emails


def test_email_ml_columns_consistency():
    """Test that EMAIL_ML_DF_COLUMNS is consistent with core + optional."""
    expected_columns = set(EMAIL_ML_DF_CORE_COLUMNS + EMAIL_ML_DF_OPTIONAL_COLUMNS)
    actual_columns = set(EMAIL_ML_DF_COLUMNS)
    
    assert expected_columns == actual_columns, "EMAIL_ML_DF_COLUMNS should equal core + optional"


def test_no_duplicate_columns():
    """Test that there are no duplicate columns in the definitions."""
    # Check core columns have no duplicates
    assert len(EMAIL_ML_DF_CORE_COLUMNS) == len(set(EMAIL_ML_DF_CORE_COLUMNS))
    
    # Check optional columns have no duplicates
    assert len(EMAIL_ML_DF_OPTIONAL_COLUMNS) == len(set(EMAIL_ML_DF_OPTIONAL_COLUMNS))
    
    # Check no overlap between core and optional
    core_set = set(EMAIL_ML_DF_CORE_COLUMNS)
    optional_set = set(EMAIL_ML_DF_OPTIONAL_COLUMNS)
    overlap = core_set.intersection(optional_set)
    assert len(overlap) == 0, f"Core and optional columns overlap: {overlap}"


def test_df_must_have_columns_success():
    """Test df_must_have_columns with valid DataFrame."""
    df = pd.DataFrame({
        'col1': [1, 2, 3],
        'col2': ['a', 'b', 'c'],
        'col3': [True, False, True]
    })
    
    # Should not raise exception
    result = df_must_have_columns(df, ['col1', 'col2'])
    assert result is True


def test_df_must_have_columns_failure():
    """Test df_must_have_columns with missing columns."""
    df = pd.DataFrame({
        'col1': [1, 2, 3],
        'col2': ['a', 'b', 'c']
    })
    
    # Should raise KeyError for missing column
    with pytest.raises(KeyError, match="missing_col"):
        df_must_have_columns(df, ['col1', 'missing_col'])


def test_df_must_not_have_columns_success():
    """Test df_must_not_have_columns with valid DataFrame."""
    df = pd.DataFrame({
        'col1': [1, 2, 3],
        'col2': ['a', 'b', 'c']
    })
    
    # Should not raise exception
    result = df_must_not_have_columns(df, ['col3', 'col4'])
    assert result is True


def test_df_must_not_have_columns_failure():
    """Test df_must_not_have_columns with forbidden columns."""
    df = pd.DataFrame({
        'col1': [1, 2, 3],
        'forbidden_col': ['a', 'b', 'c']
    })
    
    # Should raise KeyError for forbidden column
    with pytest.raises(KeyError, match="forbidden_col"):
        df_must_not_have_columns(df, ['forbidden_col'])


# ML DataFrame tests removed - ML functionality moved to Ravenclaw package
# Use Ravenclaw for feature engineering and ML preparation
