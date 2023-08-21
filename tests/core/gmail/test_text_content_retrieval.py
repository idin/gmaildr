"""
Test text content retrieval functionality.

This test verifies that text content retrieval works correctly in Gmail operations.
"""

from gmaildr import Gmail
from tests.core.gmail.test_get_emails import get_emails
import pytest


def test_text_content_retrieval_basic():
    """Test basic text content retrieval."""
    gmail = Gmail()
    
    # Get emails with text using the helper function
    df = get_emails(gmail, 5, include_text=True)
    
    if len(df) == 0:
        pytest.skip("No emails available to test with")
    
    # Test that we can retrieve emails with text
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
    
    print(f"Successfully retrieved {len(df)} emails with text content")


def test_text_content_retrieval_with_metrics():
    """Test text content retrieval with metrics enabled."""
    gmail = Gmail()
    
    # Get emails with text and metrics using the helper function
    df = get_emails(gmail, 3, include_text=True, include_metrics=True)
    
    if len(df) == 0:
        pytest.skip("No emails available to test with")
    
    # Test that we can retrieve emails with text and metrics
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
    
    print(f"Successfully retrieved {len(df)} emails with text content and metrics")


def test_text_content_retrieval_filters():
    """Test text content retrieval with filters."""
    gmail = Gmail()
    
    # Get emails with text and filters using the helper function
    df = get_emails(gmail, 5, include_text=True, in_folder='inbox')
    
    if len(df) == 0:
        pytest.skip("No emails available to test with")
    
    # Test that we can retrieve emails with text and filters
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
    
    print(f"Successfully retrieved {len(df)} emails with text content and filters")


def test_text_content_retrieval_no_text():
    """Test email retrieval without text content."""
    gmail = Gmail()
    
    # Get emails without text using the helper function
    df = get_emails(gmail, 5, include_text=False)
    
    if len(df) == 0:
        pytest.skip("No emails available to test with")
    
    # Test that we can retrieve emails without text
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
    
    print(f"Successfully retrieved {len(df)} emails without text content")


def test_text_content_retrieval_small_sample():
    """Test text content retrieval with a small sample."""
    gmail = Gmail()
    
    # Get emails with text using the helper function
    df = get_emails(gmail, 2, include_text=True)
    
    if len(df) == 0:
        pytest.skip("No emails available to test with")
    
    # Test that we can retrieve emails with text
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
    
    print(f"Successfully retrieved {len(df)} emails with text content (small sample)")


def test_text_content_retrieval_large_sample():
    """Test text content retrieval with a larger sample."""
    gmail = Gmail()
    
    # Get emails with text using the helper function
    df = get_emails(gmail, 10, include_text=True)
    
    if len(df) == 0:
        pytest.skip("No emails available to test with")
    
    # Test that we can retrieve emails with text
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
    
    print(f"Successfully retrieved {len(df)} emails with text content (large sample)")
