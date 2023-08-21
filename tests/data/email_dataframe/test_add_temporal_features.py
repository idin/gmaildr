"""
Test temporal features functionality.

This module tests the add_temporal_features function that adds time-based
features to email dataframes.
"""

import pytest
import pandas as pd
from datetime import datetime, timedelta
from gmaildr.data.email_dataframe.temporal_features import add_temporal_features
from gmaildr.data.email_dataframe.email_dataframe import EmailDataFrame


def test_add_temporal_features_basic():
    """
    Test basic temporal features addition.
    
    This test verifies that basic temporal features like day_of_week,
    hour_of_day, is_weekend, and is_business_hour are added correctly.
    """
    # Create sample email data
    data = {
        'message_id': ['msg1', 'msg2', 'msg3'],
        'sender_email': ['test@example.com', 'test@example.com', 'test@example.com'],
        'timestamp': [
            datetime(2023, 1, 2, 9, 0, 0),  # Monday 9 AM
            datetime(2023, 1, 7, 18, 0, 0),  # Saturday 6 PM
            datetime(2023, 1, 9, 14, 0, 0)   # Monday 2 PM
        ]
    }
    
    email_df = EmailDataFrame(data)
    
    # Add temporal features
    result_df = add_temporal_features(email_df=email_df, in_place=False)
    
    # Verify new columns were added
    assert 'day_of_week' in result_df.columns
    assert 'hour_of_day' in result_df.columns
    assert 'is_weekend' in result_df.columns
    assert 'is_business_hour' in result_df.columns
    
    # Verify values are correct
    assert result_df.iloc[0]['day_of_week'] == 0  # Monday
    assert result_df.iloc[0]['hour_of_day'] == 9
    assert result_df.iloc[0]['is_weekend'] == False
    assert result_df.iloc[0]['is_business_hour'] == True
    
    assert result_df.iloc[1]['day_of_week'] == 5  # Saturday
    assert result_df.iloc[1]['hour_of_day'] == 18
    assert result_df.iloc[1]['is_weekend'] == True
    assert result_df.iloc[1]['is_business_hour'] == False


def test_add_temporal_features_with_sender_local_timestamp():
    """
    Test temporal features with sender_local_timestamp column.
    
    This test verifies that the function handles sender_local_timestamp
    correctly and calculates time differences properly.
    """
    # Create sample email data with sender_local_timestamp
    data = {
        'message_id': ['msg1', 'msg2'],
        'sender_email': ['test@example.com', 'test@example.com'],
        'timestamp': [
            datetime(2023, 1, 2, 9, 0, 0),
            datetime(2023, 1, 2, 10, 0, 0)
        ],
        'sender_local_timestamp': [
            datetime(2023, 1, 2, 8, 0, 0),  # 1 hour earlier
            datetime(2023, 1, 2, 11, 0, 0)  # 1 hour later
        ]
    }
    
    email_df = EmailDataFrame(data)
    
    # Add temporal features
    result_df = add_temporal_features(email_df=email_df, in_place=False)
    
    # Verify time difference calculation
    assert 'sender_time_difference_hours' in result_df.columns
    assert result_df.iloc[0]['sender_time_difference_hours'] == 1.0  # 9 - 8 = 1 hour
    assert result_df.iloc[1]['sender_time_difference_hours'] == -1.0  # 10 - 11 = -1 hour


def test_add_temporal_features_missing_sender_local_timestamp():
    """
    Test temporal features when sender_local_timestamp is missing.
    
    This test verifies that the function creates sender_local_timestamp
    from timestamp when it's missing.
    """
    # Create sample email data without sender_local_timestamp
    data = {
        'message_id': ['msg1'],
        'sender_email': ['test@example.com'],
        'timestamp': [datetime(2023, 1, 2, 9, 0, 0)]
    }
    
    email_df = EmailDataFrame(data)
    
    # Add temporal features
    result_df = add_temporal_features(email_df=email_df, in_place=False)
    
    # Verify sender_local_timestamp was created from timestamp
    assert 'sender_local_timestamp' in result_df.columns
    assert result_df.iloc[0]['sender_local_timestamp'] == datetime(2023, 1, 2, 9, 0, 0)
    
    # Verify temporal features were added
    assert 'day_of_week' in result_df.columns
    assert 'hour_of_day' in result_df.columns


def test_add_temporal_features_in_place():
    """
    Test temporal features addition in place.
    
    This test verifies that the function modifies the dataframe in place
    when in_place=True.
    """
    # Create sample email data
    data = {
        'message_id': ['msg1'],
        'sender_email': ['test@example.com'],
        'timestamp': [datetime(2023, 1, 2, 9, 0, 0)]
    }
    
    email_df = EmailDataFrame(data)
    original_id = id(email_df)
    
    # Add temporal features in place
    result = add_temporal_features(email_df=email_df, in_place=True)
    
    # Verify the same object was modified
    assert result is None
    assert id(email_df) == original_id
    
    # Verify temporal features were added
    assert 'day_of_week' in email_df.columns
    assert 'hour_of_day' in email_df.columns


def test_add_temporal_features_invalid_input():
    """
    Test temporal features with invalid input.
    
    This test verifies that the function raises appropriate errors
    for invalid input types.
    """
    # Test with regular pandas DataFrame
    regular_df = pd.DataFrame({'message_id': ['msg1']})
    
    with pytest.raises(TypeError, match="email_df must be an instance of EmailDataFrame"):
        add_temporal_features(email_df=regular_df, in_place=False)


def test_add_temporal_features_no_timestamp():
    """
    Test temporal features when timestamp column is missing.
    
    This test verifies that the function handles missing timestamp
    gracefully and doesn't add temporal features.
    """
    # Create sample email data without timestamp
    data = {
        'message_id': ['msg1'],
        'sender_email': ['test@example.com']
    }
    
    email_df = EmailDataFrame(data)
    
    # Add temporal features
    result_df = add_temporal_features(email_df=email_df, in_place=False)
    
    # Verify no temporal features were added
    assert 'day_of_week' not in result_df.columns
    assert 'hour_of_day' not in result_df.columns
    assert 'is_weekend' not in result_df.columns
    assert 'is_business_hour' not in result_df.columns
