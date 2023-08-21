"""
Test transform_sender_features_for_ml function.

This module tests the sender ML transformation functionality to ensure
proper feature engineering and validation.
"""

import pandas as pd
import numpy as np
import pytest
from datetime import datetime, timedelta

from gmaildr import Gmail
from gmaildr.data.sender_dataframe import transform_sender_features_for_ml
from gmaildr.data.columns import SENDER_ML_DF_COLUMNS, SENDER_ML_SHOULD_NOT_HAVE_COLUMNS
from tests.core.gmail.test_get_emails import get_emails


def test_empty_dataframe_raises_error():
    """Test that empty DataFrame raises ValueError."""
    empty_df = pd.DataFrame()
    
    with pytest.raises(ValueError, match="Sender DataFrame is empty"):
        transform_sender_features_for_ml(empty_df)


def test_missing_sender_email_raises_error():
    """Test that missing sender_email column raises KeyError."""
    df = pd.DataFrame({
        'total_emails': [10, 20],
        'unique_subjects': [5, 8]
    })
    
    with pytest.raises(KeyError, match="sender_email"):
        transform_sender_features_for_ml(df)


def test_basic_numeric_features_conversion():
    """Test that basic numeric features are properly converted to float."""
    gmail = Gmail()
    
    # Get real emails using the helper function
    emails = get_emails(gmail=gmail, n=10)
    
    if len(emails) == 0:
        pytest.skip("No emails available to test with")
    
    # Convert to SenderDataFrame to get real sender data
    from gmaildr.data.sender_dataframe.sender_dataframe import SenderDataFrame
    sender_df = SenderDataFrame(emails, gmail=gmail)
    
    if len(sender_df) == 0:
        pytest.skip("No sender data available to test with")
    
    result = transform_sender_features_for_ml(sender_df)
    
    # Check that numeric features are converted to float
    if 'read_ratio' in result.columns:
        assert result['read_ratio'].dtype == 'float64'
    if 'important_ratio' in result.columns:
        assert result['important_ratio'].dtype == 'float64'
    
    # Check that periodic features are properly encoded
    assert 'total_emails_sin' in result.columns
    assert 'total_emails_cos' in result.columns
    assert 'unique_subjects_sin' in result.columns
    assert 'unique_subjects_cos' in result.columns
    assert 'mean_email_size_bytes_sin' in result.columns
    assert 'mean_email_size_bytes_cos' in result.columns
    
    # Check that original periodic features are dropped
    assert 'total_emails' not in result.columns
    assert 'unique_subjects' not in result.columns
    assert 'mean_email_size_bytes' not in result.columns


def test_boolean_features_conversion():
    """Test that boolean features are converted to int."""
    get_emails
    
    result = transform_sender_features_for_ml(df)
    
    # Check that boolean features are converted to int
    assert result['is_role_based_sender'].dtype == 'int64'
    assert result['is_personal_domain'].dtype == 'int64'
    assert result['name_consistency'].dtype == 'int64'
    
    # Check values
    assert result['is_role_based_sender'].iloc[0] == 1
    assert result['is_role_based_sender'].iloc[1] == 0


def test_categorical_features_one_hot_encoding():
    """Test that categorical features are properly one-hot encoded."""
    df = pd.DataFrame({
        'sender_email': ['test1@example.com', 'test2@example.com', 'test3@example.com'],
        'domain': ['gmail.com', 'yahoo.com', 'gmail.com'],
        'most_active_day': ['Monday', 'Tuesday', 'Monday'],
        'subject_primary_language': ['en', 'es', 'en'],
        'text_primary_language': ['en', 'en', 'fr']
    })
    
    result = transform_sender_features_for_ml(df)
    
    # Check that one-hot encoded columns are created
    assert 'domain_gmail.com' in result.columns
    assert 'domain_yahoo.com' in result.columns
    assert 'most_active_day_Monday' in result.columns
    assert 'most_active_day_Tuesday' in result.columns
    assert 'subject_primary_language_en' in result.columns
    assert 'subject_primary_language_es' in result.columns
    assert 'text_primary_language_en' in result.columns
    assert 'text_primary_language_fr' in result.columns
    
    # Check that original categorical columns are dropped
    assert 'domain' not in result.columns
    assert 'most_active_day' not in result.columns
    assert 'subject_primary_language' not in result.columns
    assert 'text_primary_language' not in result.columns


def test_ratio_features_sin_cos_encoding():
    """Test that ratio features are properly encoded with sin/cos."""
    df = pd.DataFrame({
        'sender_email': ['test1@example.com', 'test2@example.com'],
        'weekend_ratio': [0.3, 0.7],
        'business_hours_ratio': [0.8, 0.4],
        'burst_days_ratio': [0.2, 0.6]
    })
    
    result = transform_sender_features_for_ml(df)
    
    # Check that sin/cos encoded columns are created
    assert 'weekend_ratio_sin' in result.columns
    assert 'weekend_ratio_cos' in result.columns
    assert 'business_hours_ratio_sin' in result.columns
    assert 'business_hours_ratio_cos' in result.columns
    assert 'burst_days_ratio_sin' in result.columns
    assert 'burst_days_ratio_cos' in result.columns
    
    # Check that original ratio columns are dropped
    assert 'weekend_ratio' not in result.columns
    assert 'business_hours_ratio' not in result.columns
    assert 'burst_days_ratio' not in result.columns


def test_entropy_features_sin_cos_encoding():
    """Test that entropy features are properly encoded with sin/cos."""
    df = pd.DataFrame({
        'sender_email': ['test1@example.com', 'test2@example.com'],
        'day_of_week_entropy': [1.5, 2.1],
        'hour_of_day_entropy': [2.0, 1.8]
    })
    
    result = transform_sender_features_for_ml(df)
    
    # Check that sin/cos encoded columns are created
    assert 'day_of_week_entropy_sin' in result.columns
    assert 'day_of_week_entropy_cos' in result.columns
    assert 'hour_of_day_entropy_sin' in result.columns
    assert 'hour_of_day_entropy_cos' in result.columns
    
    # Check that original entropy columns are dropped
    assert 'day_of_week_entropy' not in result.columns
    assert 'hour_of_day_entropy' not in result.columns


def test_non_ml_columns_are_dropped():
    """Test that non-ML columns are properly dropped."""
    df = pd.DataFrame({
        'sender_email': ['test1@example.com', 'test2@example.com'],
        'first_email_timestamp': [datetime.now(), datetime.now()],
        'last_email_timestamp': [datetime.now(), datetime.now()],
        'display_name': ['John Doe', 'Jane Smith'],
        'most_common_recipient': ['me@example.com', 'me@example.com'],
        'total_emails': [10, 20],
        'read_ratio': [0.8, 0.6]
    })
    
    result = transform_sender_features_for_ml(df)
    
    # Check that non-ML columns are dropped
    assert 'first_email_timestamp' not in result.columns
    assert 'last_email_timestamp' not in result.columns
    assert 'display_name' not in result.columns
    assert 'most_common_recipient' not in result.columns
    
    # Check that ML columns are kept
    assert 'sender_email' in result.columns
    assert 'read_ratio' in result.columns


def test_validation_ensures_required_columns():
    """Test that the function validates the final DataFrame has required columns."""
    df = pd.DataFrame({
        'sender_email': ['test1@example.com', 'test2@example.com'],
        'total_emails': [10, 20],
        'read_ratio': [0.8, 0.6],
        'is_role_based_sender': [True, False]
    })
    
    result = transform_sender_features_for_ml(df)
    
    # Check that sender_email is present (required column)
    assert 'sender_email' in result.columns
    
    # Check that the result is a pandas DataFrame
    assert isinstance(result, pd.DataFrame)
    assert not result.empty


def test_missing_values_handling():
    """Test that missing values are handled properly."""
    df = pd.DataFrame({
        'sender_email': ['test1@example.com', 'test2@example.com', 'test3@example.com'],
        'total_emails': [10, np.nan, 30],
        'read_ratio': [0.8, 0.6, np.nan],
        'is_role_based_sender': [True, False, True]
    })
    
    result = transform_sender_features_for_ml(df)
    
    # Check that the function doesn't crash with missing values
    assert isinstance(result, pd.DataFrame)
    assert not result.empty
    assert 'sender_email' in result.columns


def test_drop_na_threshold_parameter():
    """Test that drop_na_threshold parameter works correctly."""
    df = pd.DataFrame({
        'sender_email': ['test1@example.com', 'test2@example.com'],
        'total_emails': [10, 20],
        'read_ratio': [0.8, 0.6],
        'mostly_missing_col': [1, np.nan]  # 50% missing
    })
    
    # With default threshold (0.5), mostly_missing_col should be dropped
    result_default = transform_sender_features_for_ml(df)
    assert 'mostly_missing_col' not in result_default.columns
    
    # With higher threshold (0.6), mostly_missing_col should be kept
    result_high_threshold = transform_sender_features_for_ml(df, drop_na_threshold=0.6)
    assert 'mostly_missing_col' in result_high_threshold.columns


def test_comprehensive_transformation():
    """Test a comprehensive transformation with many feature types."""
    df = pd.DataFrame({
        'sender_email': ['test1@example.com', 'test2@example.com', 'test3@example.com'],
        'total_emails': [10, 20, 15],
        'unique_subjects': [5, 8, 6],
        'mean_email_size_bytes': [1024, 2048, 1536],
        'read_ratio': [0.8, 0.6, 0.7],
        'important_ratio': [0.2, 0.1, 0.3],
        'is_role_based_sender': [True, False, True],
        'is_personal_domain': [False, True, False],
        'name_consistency': [True, True, False],
        'domain': ['gmail.com', 'yahoo.com', 'gmail.com'],
        'most_active_day': ['Monday', 'Tuesday', 'Monday'],
        'weekend_ratio': [0.3, 0.7, 0.5],
        'business_hours_ratio': [0.8, 0.4, 0.6],
        'day_of_week_entropy': [1.5, 2.1, 1.8],
        'hour_of_day_entropy': [2.0, 1.8, 2.2]
    })
    
    result = transform_sender_features_for_ml(df)
    
    # Check that all expected transformations occurred
    assert isinstance(result, pd.DataFrame)
    assert not result.empty
    assert 'sender_email' in result.columns
    
    # Check that periodic features are encoded
    assert 'total_emails_sin' in result.columns
    assert 'total_emails_cos' in result.columns
    
    # Check that boolean features are converted
    assert result['is_role_based_sender'].dtype == 'int64'
    
    # Check that categorical features are one-hot encoded
    assert 'domain_gmail.com' in result.columns
    assert 'domain_yahoo.com' in result.columns
    
    # Check that ratio features are encoded
    assert 'weekend_ratio_sin' in result.columns
    assert 'weekend_ratio_cos' in result.columns
    
    # Check that entropy features are encoded
    assert 'day_of_week_entropy_sin' in result.columns
    assert 'day_of_week_entropy_cos' in result.columns
    
    # Check that non-ML columns are not present
    for col in SENDER_ML_SHOULD_NOT_HAVE_COLUMNS:
        assert col not in result.columns
