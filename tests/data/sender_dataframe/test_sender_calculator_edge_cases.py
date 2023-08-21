"""
Tests for edge cases and error handling in sender calculator.
"""

import pytest
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

from gmaildr import Gmail
from gmaildr.data.sender_dataframe import SenderDataFrame, aggregate_emails_by_sender, calculate_entropy, extract_common_keywords, add_additional_features
from gmaildr.data.email_dataframe.email_dataframe import EmailDataFrame
from gmaildr import Gmail
from tests.core.test_data_factory import create_basic_email_dict, create_test_scenarios, get_minimal_email, get_empty_fields_email
from tests.core.gmail.test_get_emails import get_emails

def test_missing_columns():
    """Test handling of missing columns in DataFrame."""
    # Use factory to create minimal but complete email data
    minimal_email = get_minimal_email()
    gmail = Gmail()
    minimal_df = EmailDataFrame([minimal_email], gmail=gmail)
    
    # Should not raise error
    result = aggregate_emails_by_sender(minimal_df)
    assert isinstance(result, SenderDataFrame)
    assert len(result) == 1


def test_null_values():
    """Test handling of null values."""
    # Use factory to create email with null values
    null_email = get_empty_fields_email()
    gmail = Gmail()
    df = EmailDataFrame([null_email], gmail=gmail)
    
    result = aggregate_emails_by_sender(df)
    assert isinstance(result, SenderDataFrame)
    assert len(result) == 1


def test_empty_strings():
    """Test handling of empty strings."""
    # Use factory to create email with empty strings
    empty_email = create_basic_email_dict(
        message_id='msg1',
        sender_name='',
        recipient_name='',
        subject='',
        text_content=''
    )
    gmail = Gmail()
    df = EmailDataFrame([empty_email], gmail=gmail)
    
    result = aggregate_emails_by_sender(df)
    assert isinstance(result, SenderDataFrame)
    assert len(result) == 1


def test_zero_size_emails():
    """Test handling of emails with zero size."""
    scenarios = create_test_scenarios()
    df = EmailDataFrame(scenarios['zero_size_email'])
    
    result = aggregate_emails_by_sender(df)
    assert isinstance(result, SenderDataFrame)
    assert result.iloc[0]['total_size_bytes'] == 0
    assert result.iloc[0]['mean_email_size_bytes'] == 0


def test_single_email_sender():
    """Test sender with only one email."""
    scenarios = create_test_scenarios()
    df = EmailDataFrame(scenarios['single_email'])
    
    result = aggregate_emails_by_sender(df)
    assert isinstance(result, SenderDataFrame)
    assert len(result) == 1
    assert result.iloc[0]['total_emails'] == 1
    assert result.iloc[0]['unique_subjects'] == 1


def test_duplicate_emails():
    """Test handling of duplicate emails."""
    scenarios = create_test_scenarios()
    df = EmailDataFrame(scenarios['duplicate_subjects'])
    
    result = aggregate_emails_by_sender(df)
    assert isinstance(result, SenderDataFrame)
    assert len(result) == 1
    assert result.iloc[0]['total_emails'] == 2
    assert result.iloc[0]['unique_subjects'] == 1  # Only one unique subject
    assert result.iloc[0]['repeated_subject_count'] == 1  # One repeated subject


def test_entropy_edge_cases():
    """Test entropy calculation edge cases."""
    # Empty series
    empty_series = pd.Series([])
    entropy = calculate_entropy(empty_series)
    assert entropy == 0
    
    # Single value
    single_value = pd.Series([1])
    entropy = calculate_entropy(single_value)
    assert entropy == 0
    
    # All same values
    same_values = pd.Series([1, 1, 1, 1, 1])
    entropy = calculate_entropy(same_values)
    assert entropy == 0


def test_extract_keywords_edge_cases():
    """Test keyword extraction edge cases."""
    # Empty list
    keywords = extract_common_keywords([])
    assert keywords == []
    
    # Test with empty list
    keywords = extract_common_keywords([])
    assert keywords == []
    
    # Empty strings
    keywords = extract_common_keywords(['', '', ''])
    assert keywords == []
    
    # Very short words (should be filtered out)
    keywords = extract_common_keywords(['a', 'b', 'c', 'd', 'e'])
    assert keywords == []
    
    # Single word
    keywords = extract_common_keywords(['Hello'])
    assert keywords == ['hello']


def test_add_features_edge_cases():
    """Test adding features with edge cases."""
    # DataFrame with missing columns
    minimal_df = EmailDataFrame([
        {
            'message_id': 'msg1',
            'sender_email': 'test@example.com',
            'sender_name': 'Test Sender',
            'recipient_email': 'user@gmail.com',
            'recipient_name': 'User',
            'subject': 'Test',
            'timestamp': datetime.now(),
            'sender_local_timestamp': datetime.now(),
            'size_bytes': 1024,
        }
    ])
    
    result = add_additional_features(minimal_df)
    assert isinstance(result, EmailDataFrame)
    
    # DataFrame with None values
    none_df = EmailDataFrame([
        {
            'message_id': 'msg2',
            'sender_email': 'test@example.com',
            'sender_name': 'Test Sender',
            'recipient_email': 'user@gmail.com',
            'recipient_name': 'User',
            'subject': None,
            'timestamp': datetime.now(),
            'sender_local_timestamp': None,
            'size_bytes': 1024,
            'text_content': None,
        }
    ])
    
    result = add_additional_features(none_df)
    assert isinstance(result, EmailDataFrame)


def test_temporal_features_edge_cases():
    """Test temporal features with edge cases."""
    # Use factory to create emails with same timestamp
    now = datetime.now()
    same_time_emails = [
        create_basic_email_dict(
            message_id='msg1',
            subject='Test 1',
            timestamp=now,
            sender_local_timestamp=now
        ),
        create_basic_email_dict(
            message_id='msg2',
            subject='Test 2',
            timestamp=now,  # Same time
            sender_local_timestamp=now  # Same time
        )
    ]
    gmail = Gmail()
    df = EmailDataFrame(same_time_emails, gmail=gmail)
    
    result = aggregate_emails_by_sender(df)
    assert isinstance(result, SenderDataFrame)
    assert len(result) == 1
    assert result.iloc[0]['date_range_days'] == 0  # Same day


def test_language_analysis_edge_cases():
    """Test language analysis with edge cases."""
    # Use factory to create email with no language data
    no_language_email = create_basic_email_dict(
        message_id='msg1',
        subject='Test'
        # No language fields - factory provides None defaults
    )
    df = EmailDataFrame([no_language_email])
    
    result = calculate_sender_statistics_from_dataframe(df)
    assert isinstance(result, SenderDataFrame)
    # Should have language fields since factory provides them (even if None)
    assert 'subject_primary_language' in result.columns
    # But the values should be None since we didn't provide language data
    assert result.iloc[0]['subject_primary_language'] is None


def test_recipient_analysis_edge_cases():
    """Test recipient analysis with edge cases."""
    # Use factory to create email with no recipient data
    no_recipient_email = create_basic_email_dict(
        message_id='test_msg_1',
        subject='Test'
        # Factory provides default recipient fields
    )
    df = EmailDataFrame([no_recipient_email])
    
    result = calculate_sender_statistics_from_dataframe(df)
    assert isinstance(result, SenderDataFrame)
    # Should have recipient fields since factory provides them
    assert 'unique_recipients' in result.columns


def test_forwarding_analysis_edge_cases():
    """Test forwarding analysis with edge cases."""
    # Use factory to create email with no forwarding data
    no_forwarding_email = create_basic_email_dict(
        message_id='test_msg_2',
        subject='Test'
        # Factory provides default forwarding fields
    )
    df = EmailDataFrame([no_forwarding_email])
    
    result = calculate_sender_statistics_from_dataframe(df)
    assert isinstance(result, SenderDataFrame)
    # Should have forwarding fields since factory provides them
    assert 'forwarded_emails_count' in result.columns


def test_sender_dataframe_empty():
    """Test SenderDataFrame with empty data."""
    empty_email_df = EmailDataFrame([])
    df = SenderDataFrame(empty_email_df)
    assert isinstance(df, SenderDataFrame)
    assert len(df) == 0


def test_sender_dataframe_no_index():
    """Test SenderDataFrame without index."""
    # Use factory to create proper EmailDataFrame
    email_data = create_basic_email_dict(
        message_id='test_msg_1',
        subject='Test'
    )
    email_df = EmailDataFrame([email_data])
    df = SenderDataFrame(email_df)
    assert isinstance(df, SenderDataFrame)
    assert len(df) == 1
