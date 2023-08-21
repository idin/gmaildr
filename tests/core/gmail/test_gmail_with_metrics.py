"""
Test Gmail operations with metrics.

This test verifies that Gmail operations work correctly with metrics enabled.
"""

from gmaildr import Gmail
from tests.core.gmail.test_get_emails import get_emails
import pytest


def test_gmail_with_metrics_basic():
    """Test basic Gmail operations with metrics enabled."""
    gmail = Gmail()
    
    # Get emails with metrics using the helper function
    df = get_emails(gmail, 5, include_metrics=True)
    
    if len(df) == 0:
        pytest.skip("No emails available to test with")
    
    # Test that we can retrieve emails with metrics
    assert len(df) > 0
    assert not df.is_empty()
    
    # Verify the structure is correct
    assert 'message_id' in df.columns
    assert 'subject' in df.columns
    assert 'sender_email' in df.columns
    
    # Test that we can access individual emails
    first_email = df.iloc[0]
    assert 'message_id' in first_email
    assert 'subject' in first_email
    
    print(f"Successfully retrieved {len(df)} emails with metrics")


def test_gmail_with_metrics_and_text():
    """Test Gmail operations with metrics and text enabled."""
    gmail = Gmail()
    
    # Get emails with metrics and text using the helper function
    df = get_emails(gmail, 3, include_metrics=True, include_text=True)
    
    if len(df) == 0:
        pytest.skip("No emails available to test with")
    
    # Test that we can retrieve emails with metrics and text
    assert len(df) > 0
    assert not df.is_empty()
    
    # Verify the structure is correct
    assert 'message_id' in df.columns
    assert 'subject' in df.columns
    assert 'sender_email' in df.columns
    
    # Test that we can access individual emails
    first_email = df.iloc[0]
    assert 'message_id' in first_email
    assert 'subject' in first_email
    
    print(f"Successfully retrieved {len(df)} emails with metrics and text")


def test_gmail_with_metrics_filters():
    """Test Gmail operations with metrics and filters."""
    gmail = Gmail()
    
    # Get emails with metrics and filters using the helper function
    df = get_emails(gmail, 5, include_metrics=True, in_folder='inbox')
    
    if len(df) == 0:
        pytest.skip("No emails available to test with")
    
    # Test that we can retrieve emails with metrics and filters
    assert len(df) > 0
    assert not df.is_empty()
    
    # Verify the structure is correct
    assert 'message_id' in df.columns
    assert 'subject' in df.columns
    assert 'sender_email' in df.columns
    
    # Test that we can access individual emails
    first_email = df.iloc[0]
    assert 'message_id' in first_email
    assert 'subject' in first_email
    
    print(f"Successfully retrieved {len(df)} emails with metrics and filters")
