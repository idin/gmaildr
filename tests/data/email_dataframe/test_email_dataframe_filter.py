"""
Tests for EmailDataFrame filter method.

This module tests the filter method comprehensively to ensure it handles
all edge cases correctly, including list/tuple values, single values,
and various data types.
"""

import pytest
import pandas as pd
from datetime import datetime
from gmaildr.data.email_dataframe.email_dataframe import EmailDataFrame # this should not be an issue. IF it is the issue is in the package itself and should be fixed.


def test_filter_single_condition():
    """Test filtering with a single condition."""

    # iMPoRTANT: because we want to know exactly what is going on with the filters, we need to control the data, therefore we don't use get_emails for this particular test
    data = {
        'message_id': ['msg1', 'msg2', 'msg3', 'msg4'],
        'subject': ['Test 1', 'Test 2', 'Test 3', 'Test 4'],
        'is_read': [True, False, True, False],
        'sender_email': ['sender1@test.com', 'sender2@test.com', 'sender1@test.com', 'sender3@test.com']
    }
    df = EmailDataFrame(data)
    
    # Filter by boolean condition
    filtered = df.filter(is_read=True)
    assert len(filtered) == 2
    assert all(filtered['is_read'] == True)
    assert filtered['message_id'].tolist() == ['msg1', 'msg3']
    
    # Filter by string condition
    filtered = df.filter(sender_email='sender1@test.com')
    assert len(filtered) == 2
    assert all(filtered['sender_email'] == 'sender1@test.com')


def test_filter_multiple_conditions():
    """Test filtering with multiple conditions."""
    data = {
        'message_id': ['msg1', 'msg2', 'msg3', 'msg4'],
        'subject': ['Test 1', 'Test 2', 'Test 3', 'Test 4'],
        'is_read': [True, False, True, False],
        'sender_email': ['sender1@test.com', 'sender2@test.com', 'sender1@test.com', 'sender3@test.com']
    }
    df = EmailDataFrame(data)
    
    # Filter by multiple conditions
    filtered = df.filter(is_read=True, sender_email='sender1@test.com')
    assert len(filtered) == 2
    assert all(filtered['is_read'] == True)
    assert all(filtered['sender_email'] == 'sender1@test.com')


def test_filter_list_condition():
    """Test filtering with list/tuple conditions."""
    data = {
        'message_id': ['msg1', 'msg2', 'msg3', 'msg4'],
        'subject': ['Test 1', 'Test 2', 'Test 3', 'Test 4'],
        'sender_email': ['sender1@test.com', 'sender2@test.com', 'sender1@test.com', 'sender3@test.com']
    }
    df = EmailDataFrame(data)
    
    # Filter by list condition
    filtered = df.filter(sender_email=['sender1@test.com', 'sender2@test.com'])
    assert len(filtered) == 3
    assert all(email in ['sender1@test.com', 'sender2@test.com'] for email in filtered['sender_email'])
    
    # Filter by tuple condition
    filtered = df.filter(sender_email=('sender1@test.com', 'sender3@test.com'))
    assert len(filtered) == 3
    assert all(email in ['sender1@test.com', 'sender3@test.com'] for email in filtered['sender_email'])


def test_filter_numeric_conditions():
    """Test filtering with numeric conditions."""
    data = {
        'message_id': ['msg1', 'msg2', 'msg3', 'msg4'],
        'subject': ['Test 1', 'Test 2', 'Test 3', 'Test 4'],
        'size_bytes': [1024, 2048, 1024, 4096],
        'priority': [1, 2, 1, 3]
    }
    df = EmailDataFrame(data)
    
    # Filter by numeric condition
    filtered = df.filter(size_bytes=1024)
    assert len(filtered) == 2
    assert all(filtered['size_bytes'] == 1024)
    
    # Filter by numeric list condition
    filtered = df.filter(priority=[1, 2])
    assert len(filtered) == 3
    assert all(priority in [1, 2] for priority in filtered['priority'])


def test_filter_mixed_conditions():
    """Test filtering with mixed data types."""
    data = {
        'message_id': ['msg1', 'msg2', 'msg3', 'msg4'],
        'subject': ['Test 1', 'Test 2', 'Test 3', 'Test 4'],
        'is_read': [True, False, True, False],
        'sender_email': ['sender1@test.com', 'sender2@test.com', 'sender1@test.com', 'sender3@test.com'],
        'size_bytes': [1024, 2048, 1024, 4096]
    }
    df = EmailDataFrame(data)
    
    # Filter by mixed conditions
    filtered = df.filter(
        is_read=True,
        sender_email=['sender1@test.com', 'sender2@test.com'],
        size_bytes=1024
    )
    assert len(filtered) == 2  # Both msg1 and msg3 should match
    assert 'msg1' in filtered['message_id'].values
    assert 'msg3' in filtered['message_id'].values
    assert isinstance(filtered, EmailDataFrame)


def test_filter_empty_result():
    """Test filtering that results in empty DataFrame."""
    data = {
        'message_id': ['msg1', 'msg2', 'msg3'],
        'subject': ['Test 1', 'Test 2', 'Test 3'],
        'is_read': [True, False, True],
        'sender_email': ['sender1@test.com', 'sender2@test.com', 'sender1@test.com']
    }
    df = EmailDataFrame(data)
    
    # Filter that should return empty result
    filtered = df.filter(is_read=True, sender_email='sender2@test.com')
    assert len(filtered) == 0
    assert isinstance(filtered, EmailDataFrame)


def test_filter_nonexistent_column():
    """Test filtering with non-existent column (should be ignored)."""
    data = {
        'message_id': ['msg1', 'msg2', 'msg3'],
        'subject': ['Test 1', 'Test 2', 'Test 3'],
        'is_read': [True, False, True]
    }
    df = EmailDataFrame(data)
    
    # Filter with non-existent column should not affect the result
    filtered = df.filter(is_read=True, nonexistent_column='value')
    assert len(filtered) == 2
    assert all(filtered['is_read'] == True)


def test_filter_empty_dataframe():
    """Test filtering on empty DataFrame."""
    data = {
        'message_id': [],
        'subject': [],
        'is_read': []
    }
    df = EmailDataFrame(data)
    
    # Filter on empty DataFrame should return empty DataFrame
    filtered = df.filter(is_read=True)
    assert len(filtered) == 0
    assert isinstance(filtered, EmailDataFrame)


def test_filter_chaining():
    """Test chaining multiple filter operations."""
    data = {
        'message_id': ['msg1', 'msg2', 'msg3', 'msg4'],
        'subject': ['Test 1', 'Test 2', 'Test 3', 'Test 4'],
        'is_read': [True, False, True, False],
        'sender_email': ['sender1@test.com', 'sender2@test.com', 'sender1@test.com', 'sender3@test.com']
    }
    df = EmailDataFrame(data)
    
    # Chain multiple filters
    filtered1 = df.filter(is_read=True)
    filtered2 = filtered1.filter(sender_email='sender1@test.com')
    
    assert len(filtered1) == 2
    assert len(filtered2) == 2
    assert all(filtered2['is_read'] == True)
    assert all(filtered2['sender_email'] == 'sender1@test.com')


def test_filter_preserves_dataframe_type():
    """Test that filter method preserves EmailDataFrame type."""
    data = {
        'message_id': ['msg1', 'msg2', 'msg3'],
        'subject': ['Test 1', 'Test 2', 'Test 3'],
        'is_read': [True, False, True]
    }
    df = EmailDataFrame(data)
    
    # Filter should return EmailDataFrame, not regular DataFrame
    filtered = df.filter(is_read=True)
    assert isinstance(filtered, EmailDataFrame)
    assert type(filtered) == EmailDataFrame  # Should be exactly EmailDataFrame, not base DataFrame


def test_filter_with_gmail_instance():
    """Test that filter preserves gmail instance."""
    # Create a mock gmail instance
    class MockGmail:
        pass
    
    gmail = MockGmail()
    data = {
        'message_id': ['msg1', 'msg2', 'msg3'],
        'subject': ['Test 1', 'Test 2', 'Test 3'],
        'is_read': [True, False, True]
    }
    df = EmailDataFrame(data, gmail=gmail)
    
    # Filter should preserve gmail instance
    filtered = df.filter(is_read=True)
    assert filtered._gmail_instance == gmail
