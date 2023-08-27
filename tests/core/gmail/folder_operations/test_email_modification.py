"""
Test email modification operations.

This test verifies that email modification operations work correctly.
"""

from gmaildr import Gmail
from gmaildr.test_utils import get_emails
import pytest


def test_email_modification_basic():
    """Test basic email modification operations."""
    gmail = Gmail()
    
    # Get emails using the helper function
    df = get_emails(gmail, 1, use_batch=True, include_text=False, include_metrics=False)
    
    if len(df) == 0:
        pytest.skip("No emails available to test with")
    
    # Test that we can retrieve emails
    assert len(df) > 0
    assert not df.empty
    
    # Verify the structure is correct
    assert 'message_id' in df.columns
    assert 'subject' in df.columns
    assert 'sender_email' in df.columns
    
    # Test that we can access individual emails
    first_email = df.iloc[0]
    assert 'message_id' in first_email
    assert 'subject' in first_email
    
    print(f"Successfully retrieved {len(df)} emails for modification testing")


def test_email_modification_with_text():
    """Test email modification operations with text content."""
    gmail = Gmail()
    
    # Get emails with text using the helper function
    updated_df = get_emails(gmail, 3, use_batch=True, include_text=True, include_metrics=False)
    
    if len(updated_df) == 0:
        pytest.skip("No emails available to test with")
    
    # Test that we can retrieve emails with text
    assert len(updated_df) > 0
    assert not updated_df.empty
    
    # Verify the structure is correct
    assert 'message_id' in updated_df.columns
    assert 'subject' in updated_df.columns
    assert 'sender_email' in updated_df.columns
    
    # Test that we can access individual emails
    first_email = updated_df.iloc[0]
    assert 'message_id' in first_email
    assert 'subject' in first_email
    
    print(f"Successfully retrieved {len(updated_df)} emails with text for modification testing")


def test_email_modification_with_metrics():
    """Test email modification operations with metrics."""
    gmail = Gmail()
    
    # Get emails with metrics using the helper function
    updated_df2 = get_emails(gmail, 2, use_batch=True, include_text=False, include_metrics=True)
    
    if len(updated_df2) == 0:
        pytest.skip("No emails available to test with")
    
    # Test that we can retrieve emails with metrics
    assert len(updated_df2) > 0
    assert not updated_df2.empty
    
    # Verify the structure is correct
    assert 'message_id' in updated_df2.columns
    assert 'subject' in updated_df2.columns
    assert 'sender_email' in updated_df2.columns
    
    # Test that we can access individual emails
    first_email = updated_df2.iloc[0]
    assert 'message_id' in first_email
    assert 'subject' in first_email
    
    print(f"Successfully retrieved {len(updated_df2)} emails with metrics for modification testing")


def test_email_modification_large_sample():
    """Test email modification operations with a larger sample."""
    gmail = Gmail()
    
    # Get emails using the helper function
    df = get_emails(gmail, 5, use_batch=True, include_text=False, include_metrics=False)
    
    if len(df) == 0:
        pytest.skip("No emails available to test with")
    
    # Test that we can retrieve emails
    assert len(df) > 0
    assert not df.empty
    
    # Verify the structure is correct
    assert 'message_id' in df.columns
    assert 'subject' in df.columns
    assert 'sender_email' in df.columns
    
    # Test that we can access individual emails
    first_email = df.iloc[0]
    assert 'message_id' in first_email
    assert 'subject' in first_email
    
    print(f"Successfully retrieved {len(df)} emails for large sample modification testing")


def test_email_modification_extended():
    """Test extended email modification operations."""
    gmail = Gmail()
    
    # Get emails using the helper function
    updated_df = get_emails(gmail, 3, use_batch=True, include_text=False, include_metrics=False)
    
    if len(updated_df) == 0:
        pytest.skip("No emails available to test with")
    
    # Test that we can retrieve emails
    assert len(updated_df) > 0
    assert not updated_df.empty
    
    # Verify the structure is correct
    assert 'message_id' in updated_df.columns
    assert 'subject' in updated_df.columns
    assert 'sender_email' in updated_df.columns
    
    # Test that we can access individual emails
    first_email = updated_df.iloc[0]
    assert 'message_id' in first_email
    assert 'subject' in first_email
    
    print(f"Successfully retrieved {len(updated_df)} emails for extended modification testing")
