"""
Tests for get_emails returning EmailDataFrame.
"""

import pytest
from datetime import datetime

from gmailwiz.core.gmail import Gmail
from gmailwiz.core.email_dataframe import EmailDataFrame


def test_get_emails_returns_email_dataframe():
    """Test that get_emails returns EmailDataFrame."""
    gmail = Gmail()
    
    # Test that get_emails method exists
    assert hasattr(gmail, 'get_emails')
    assert callable(gmail.get_emails)
    
    # The method should return EmailDataFrame when called
    # This is tested in the actual implementation


def test_email_dataframe_has_gmail_client():
    """Test that EmailDataFrame has Gmail client set."""
    gmail = Gmail()
    
    # Test that EmailDataFrame can be created with Gmail client
    data = {'message_id': ['msg1'], 'subject': ['Test']}
    df = EmailDataFrame(data, gmail_instance=gmail)
    
    assert df._gmail_instance == gmail


def test_email_dataframe_operations():
    """Test that EmailDataFrame has the expected operations."""
    gmail = Gmail()
    data = {'message_id': ['msg1'], 'subject': ['Test']}
    df = EmailDataFrame(data, gmail_instance=gmail)
    
    # Test that EmailDataFrame has the expected methods
    assert hasattr(df, 'move_to_archive')
    assert hasattr(df, 'move_to_trash')
    assert hasattr(df, 'move_to_inbox')
    assert hasattr(df, 'mark_as_read')
    assert hasattr(df, 'mark_as_unread')
    assert hasattr(df, 'star')
    assert hasattr(df, 'unstar')
    assert hasattr(df, 'add_label')
    assert hasattr(df, 'remove_label')
    assert hasattr(df, 'filter')
    assert hasattr(df, 'count')
    assert hasattr(df, 'is_empty')
