"""
Tests for aggregate_emails_by_sender function.
"""

import pytest
import pandas as pd
from gmaildr.data.sender_dataframe.aggregate_emails_by_sender import aggregate_emails_by_sender
from gmaildr.data.email_dataframe.email_dataframe import EmailDataFrame
from gmaildr.core.gmail import Gmail


def test_aggregate_emails_by_sender_basic():
    """Test basic aggregation functionality."""
    gmail = Gmail()
    email_df = gmail.get_emails(max_emails=10)
    
    result = aggregate_emails_by_sender(email_df)
    
    assert isinstance(result, pd.DataFrame)
    assert 'sender_email' in result.columns
    assert len(result) > 0  # Should have at least one sender
    
    # Check basic features are present
    assert 'total_emails' in result.columns
    assert 'unique_subjects' in result.columns
    assert 'mean_email_size_bytes' in result.columns


def test_aggregate_emails_by_sender_derived_calculations():
    """Test that derived calculations are correct."""
    gmail = Gmail()
    email_df = gmail.get_emails(max_emails=10)
    
    result = aggregate_emails_by_sender(email_df)
    
    # Check derived calculations exist
    assert 'date_range_days' in result.columns
    assert 'emails_per_day' in result.columns
    assert 'recipient_diversity' in result.columns
    assert 'domain' in result.columns
    assert 'is_personal_domain' in result.columns
    assert 'unique_subject_ratio' in result.columns
    
    # Check domain extraction works
    if len(result) > 0:
        first_row = result.iloc[0]
        assert '@' in first_row['sender_email']
        assert '.' in first_row['domain']


def test_aggregate_emails_by_sender_input_types():
    """Test function works with different input types."""
    gmail = Gmail()
    email_df = gmail.get_emails(max_emails=5)
    
    # Test with EmailDataFrame
    result1 = aggregate_emails_by_sender(email_df)
    
    # Test with pandas DataFrame
    df = email_df.dataframe
    result2 = aggregate_emails_by_sender(df)
    
    # Test with list of dicts
    email_list = email_df.to_dict('records')
    result3 = aggregate_emails_by_sender(email_list)
    
    # All should produce the same result
    pd.testing.assert_frame_equal(result1, result2)
    pd.testing.assert_frame_equal(result1, result3)


def test_aggregate_emails_by_sender_error_handling():
    """Test error handling for invalid inputs."""
    # Test with non-email data
    invalid_data = [{'name': 'John', 'age': 30}]
    
    with pytest.raises(TypeError, match="df must be an EmailDataFrame"):
        aggregate_emails_by_sender(invalid_data)
    
    # Test with empty data
    empty_df = EmailDataFrame([])
    result = aggregate_emails_by_sender(empty_df)
    assert len(result) == 0


def test_aggregate_emails_by_sender_feature_columns():
    """Test that all expected feature columns are present."""
    gmail = Gmail()
    email_df = gmail.get_emails(max_emails=10)
    
    result = aggregate_emails_by_sender(email_df)
    
    # Check that all basic features are present
    expected_features = [
        'total_emails', 'unique_subjects', 'first_email_timestamp', 'last_email_timestamp',
        'total_size_bytes', 'mean_email_size_bytes', 'max_email_size_bytes', 'min_email_size_bytes',
        'std_email_size_bytes', 'read_ratio', 'important_ratio', 'starred_ratio',
        'is_role_based_sender', 'unique_threads', 'unique_recipients', 'most_common_recipient',
        'forwarded_emails_count', 'forwarded_emails_ratio', 'name_consistency', 'display_name',
        'name_variations', 'date_range_days', 'emails_per_day', 'recipient_diversity',
        'domain', 'is_personal_domain', 'unique_subject_ratio'
    ]
    
    for feature in expected_features:
        assert feature in result.columns, f"Missing feature: {feature}"


def test_aggregate_emails_by_sender_aggregation_logic():
    """Test that aggregation logic produces correct results."""
    gmail = Gmail()
    email_df = gmail.get_emails(max_emails=20)
    
    result = aggregate_emails_by_sender(email_df)
    
    if len(result) > 0:
        # Check that total_emails is always positive
        assert all(result['total_emails'] > 0)
        
        # Check that unique_subjects <= total_emails
        assert all(result['unique_subjects'] <= result['total_emails'])
        
        # Check that date ranges make sense
        assert all(result['date_range_days'] >= 0)
        
        # Check that emails_per_day is reasonable
        assert all(result['emails_per_day'] >= 0)
        
        # Check that ratios are between 0 and 1
        ratio_columns = ['read_ratio', 'important_ratio', 'starred_ratio', 'forwarded_emails_ratio']
        for col in ratio_columns:
            if col in result.columns:
                assert all((result[col] >= 0) & (result[col] <= 1))
