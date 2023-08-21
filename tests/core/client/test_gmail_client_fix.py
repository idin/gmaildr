"""
Test Gmail client API fixes.

This test verifies that the Gmail client API works correctly after fixes.
"""

from gmaildr import Gmail
from tests.core.gmail.test_get_emails import get_emails
import pytest


def test_gmail_client_basic_operations():
    """Test basic Gmail client operations."""
    gmail = Gmail()
    
    # Get emails using the helper function
    emails = get_emails(gmail, 5)
    
    if len(emails) == 0:
        pytest.skip("No emails available to test with")
    
    # Test that we can retrieve emails
    assert len(emails) > 0
    assert not emails.is_empty()
    
    # Verify the structure is correct
    assert 'message_id' in emails.columns
    assert 'subject' in emails.columns
    assert 'sender_email' in emails.columns
    
    # Test that we can access individual emails
    first_email = emails.iloc[0]
    assert 'message_id' in first_email
    assert 'subject' in first_email
    
    print(f"Successfully retrieved {len(emails)} emails")


def test_gmail_client_with_text():
    """Test Gmail client operations with text content."""
    gmail = Gmail()
    
    # Get emails with text using the helper function
    emails = get_emails(gmail, 3, include_text=True)
    
    if len(emails) == 0:
        pytest.skip("No emails available to test with")
    
    # Test that we can retrieve emails with text
    assert len(emails) > 0
    assert not emails.is_empty()
    
    # Verify the structure is correct
    assert 'message_id' in emails.columns
    assert 'subject' in emails.columns
    assert 'sender_email' in emails.columns
    
    # Test that we can access individual emails
    first_email = emails.iloc[0]
    assert 'message_id' in first_email
    assert 'subject' in first_email
    
    print(f"Successfully retrieved {len(emails)} emails with text content")


def test_gmail_client_with_metrics():
    """Test Gmail client operations with metrics."""
    gmail = Gmail()
    
    # Get emails with metrics using the helper function
    emails = get_emails(gmail, 2, include_metrics=True)
    
    if len(emails) == 0:
        pytest.skip("No emails available to test with")
    
    # Test that we can retrieve emails with metrics
    assert len(emails) > 0
    assert not emails.is_empty()
    
    # Verify the structure is correct
    assert 'message_id' in emails.columns
    assert 'subject' in emails.columns
    assert 'sender_email' in emails.columns
    
    # Test that we can access individual emails
    first_email = emails.iloc[0]
    assert 'message_id' in first_email
    assert 'subject' in first_email
    
    print(f"Successfully retrieved {len(emails)} emails with metrics")
