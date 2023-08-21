"""
Tests for sender statistics calculator.
"""

import pytest
import pandas as pd
from datetime import datetime, timedelta

from gmaildr.data.sender_dataframe.sender_dataframe import SenderDataFrame
from gmaildr.data.email_dataframe.email_dataframe import EmailDataFrame


def create_sample_email_data():
    """Create sample email data for testing."""
    return [
        {
            'message_id': 'msg1',
            'sender_email': 'john@example.com',
            'sender_name': 'John Doe',
            'recipient_email': 'user@gmail.com',
            'recipient_name': 'User',
            'subject': 'Hello there',
            'timestamp': datetime.now() - timedelta(days=1),
            'sender_local_timestamp': datetime.now() - timedelta(days=1, hours=2),
            'size_bytes': 1024,
            'in_folder': 'inbox',
            'is_read': True,
            'is_important': False,
            'is_starred': False,
            'has_role_based_email': False,
            'is_forwarded': False,
            'subject_language': 'en',
            'subject_language_confidence': 0.9,
            'text_language': 'en',
            'text_language_confidence': 0.8,
            'text_content': 'This is a test email content.',
        },
        {
            'message_id': 'msg2',
            'sender_email': 'john@example.com',
            'sender_name': 'John Doe',
            'recipient_email': 'user@gmail.com',
            'recipient_name': 'User',
            'subject': 'Follow up',
            'timestamp': datetime.now() - timedelta(hours=12),
            'sender_local_timestamp': datetime.now() - timedelta(hours=14),
            'size_bytes': 2048,
            'in_folder': 'inbox',
            'is_read': False,
            'is_important': True,
            'is_starred': True,
            'has_role_based_email': False,
            'is_forwarded': False,
            'subject_language': 'en',
            'subject_language_confidence': 0.95,
            'text_language': 'en',
            'text_language_confidence': 0.85,
            'text_content': 'This is another test email with more content.',
        },
        {
            'message_id': 'msg3',
            'sender_email': 'support@company.com',
            'sender_name': 'Support Team',
            'recipient_email': 'user@gmail.com',
            'recipient_name': 'User',
            'subject': 'Your ticket #123',
            'timestamp': datetime.now() - timedelta(hours=6),
            'sender_local_timestamp': datetime.now() - timedelta(hours=8),
            'size_bytes': 512,
            'in_folder': 'inbox',
            'is_read': True,
            'is_important': False,
            'is_starred': False,
            'has_role_based_email': True,
            'is_forwarded': True,
            'subject_language': 'en',
            'subject_language_confidence': 0.88,
            'text_language': 'en',
            'text_language_confidence': 0.92,
            'text_content': 'We have received your support request.',
        }
    ]


def test_sender_dataframe_basic():
    """Test basic SenderDataFrame creation and functionality."""
    sample_emails = create_sample_email_data()
    email_df = EmailDataFrame(sample_emails)
    
    result = SenderDataFrame(email_df)
    
    assert isinstance(result, SenderDataFrame)
    assert len(result) == 2  # Two unique senders
    assert result.index.name == 'sender_email'
    
    # Check john@example.com stats
    john_stats = result.loc['john@example.com']
    assert john_stats['total_emails'] == 2
    assert john_stats['unique_subjects'] == 2
    assert john_stats['mean_email_size_bytes'] == 1536  # (1024 + 2048) / 2
    assert john_stats['is_role_based_sender'] == False
    
    # Check support@company.com stats
    support_stats = result.loc['support@company.com']
    assert support_stats['total_emails'] == 1
    assert support_stats['is_role_based_sender'] == True


def test_sender_dataframe_empty():
    """Test SenderDataFrame with empty EmailDataFrame."""
    empty_df = EmailDataFrame([])
    result = SenderDataFrame(empty_df)
    
    assert isinstance(result, SenderDataFrame)
    assert len(result) == 0


def test_sender_dataframe_class():
    """Test SenderDataFrame class functionality."""
    # Create a simple EmailDataFrame for testing
    test_emails = [
        {
            'message_id': 'test1',
            'sender_email': 'sender1@example.com',
            'sender_name': 'Sender 1',
            'subject': 'Test 1',
            'timestamp': datetime.now(),
            'sender_local_timestamp': datetime.now(),
            'size_bytes': 1024,
            'is_read': True,
            'is_important': False,
            'is_starred': False,
            'has_role_based_email': False,
            'is_forwarded': False,
        },
        {
            'message_id': 'test2',
            'sender_email': 'sender2@example.com',
            'sender_name': 'Sender 2',
            'subject': 'Test 2',
            'timestamp': datetime.now(),
            'sender_local_timestamp': datetime.now(),
            'size_bytes': 2048,
            'is_read': False,
            'is_important': True,
            'is_starred': True,
            'has_role_based_email': True,
            'is_forwarded': False,
        }
    ]
    
    email_df = EmailDataFrame(test_emails)
    df = SenderDataFrame(email_df)
    
    assert isinstance(df, SenderDataFrame)
    assert len(df) == 2
    assert df.index.name == 'sender_email'
    
    # Test that we can access data like a regular DataFrame
    assert 'total_emails' in df.columns
    assert 'mean_email_size_bytes' in df.columns
    assert df['total_emails'].sum() == 2  # Total emails across all senders
