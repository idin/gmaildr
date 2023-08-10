"""
Tests for EmailDataFrame functionality.
"""

import pytest
import pandas as pd
from datetime import datetime

from gmailwiz.core.gmail import Gmail
from gmailwiz.core.email_dataframe import EmailDataFrame


def test_email_dataframe_creation():
    """Test EmailDataFrame creation and basic functionality."""
    data = {
        'message_id': ['msg1', 'msg2', 'msg3'],
        'subject': ['Test 1', 'Test 2', 'Test 3'],
        'sender': ['sender1@test.com', 'sender2@test.com', 'sender3@test.com'],
        'date': [datetime.now()] * 3,
        'is_read': [True, False, True]
    }
    
    df = EmailDataFrame(data)
    assert isinstance(df, EmailDataFrame)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 3
    assert 'message_id' in df.columns


def test_email_dataframe_with_gmail_client():
    """Test EmailDataFrame with Gmail client."""
    mock_gmail = Gmail()  # Using real Gmail instance for testing
    data = {'message_id': ['msg1'], 'subject': ['Test']}
    
    df = EmailDataFrame(data, gmail_client=mock_gmail)
    assert df._gmail_client == mock_gmail


def test_set_gmail_client():
    """Test setting Gmail client after creation."""
    mock_gmail = Gmail()
    data = {'message_id': ['msg1'], 'subject': ['Test']}
    
    df = EmailDataFrame(data)
    result = df.set_gmail_client(mock_gmail)
    
    assert df._gmail_client == mock_gmail
    assert result is df  # Should return self for chaining


def test_get_message_ids():
    """Test extracting message IDs from DataFrame."""
    data = {'message_id': ['msg1', 'msg2'], 'subject': ['Test 1', 'Test 2']}
    df = EmailDataFrame(data)
    
    message_ids = df._get_message_ids()
    assert message_ids == ['msg1', 'msg2']


def test_get_message_ids_missing_column():
    """Test error when message_id column is missing."""
    data = {'subject': ['Test 1'], 'sender': ['sender@test.com']}
    df = EmailDataFrame(data)
    
    with pytest.raises(ValueError, match="DataFrame must contain 'message_id' column"):
        df._get_message_ids()


def test_check_gmail_client_not_set():
    """Test error when Gmail client is not set."""
    data = {'message_id': ['msg1'], 'subject': ['Test']}
    df = EmailDataFrame(data)
    
    with pytest.raises(ValueError, match="Gmail client not set"):
        df._check_gmail_client()


def test_filter_method():
    """Test filter method."""
    data = {
        'message_id': ['msg1', 'msg2', 'msg3'],
        'subject': ['Test 1', 'Test 2', 'Test 3'],
        'is_read': [True, False, True],
        'sender': ['sender1@test.com', 'sender2@test.com', 'sender1@test.com']
    }
    df = EmailDataFrame(data)
    
    # Filter by single condition
    filtered = df.filter(is_read=True)
    assert len(filtered) == 2
    assert all(filtered['is_read'] == True)
    
    # Filter by multiple conditions
    filtered = df.filter(is_read=True, sender='sender1@test.com')
    assert len(filtered) == 2
    
    # Filter by list condition
    filtered = df.filter(sender=['sender1@test.com', 'sender2@test.com'])
    assert len(filtered) == 3


def test_count_and_is_empty():
    """Test count and is_empty methods."""
    data = {'message_id': ['msg1', 'msg2'], 'subject': ['Test 1', 'Test 2']}
    df = EmailDataFrame(data)
    
    assert df.count() == 2
    assert df.is_empty() is False
    
    empty_df = EmailDataFrame({'message_id': [], 'subject': []})
    assert empty_df.count() == 0
    assert empty_df.is_empty() is True
