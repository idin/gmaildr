"""
Test to verify Gmail client fix for TypeError in _convert_api_response_to_email_message.

This test ensures that the Gmail client can fetch emails without encountering
the TypeError that was caused by incorrect method call arguments.
"""

from gmaildr import Gmail


def test_gmail_client_fetch_emails():
    """Test that Gmail client can fetch emails without TypeError."""
    gmail = Gmail(enable_cache=False)
    
    # Try to fetch a small number of emails
    df = gmail.get_emails(
        days=1, 
        max_emails=5, 
        include_text=False, 
        include_metrics=False
    )
    
    # Should not raise TypeError
    assert df is not None, "DataFrame should not be None"
    print(f"Successfully fetched {len(df)} emails")


def test_gmail_client_with_cache():
    """Test that Gmail client works with cache enabled."""
    gmail = Gmail(enable_cache=True)
    
    # Try to fetch emails with cache
    df = gmail.get_emails(
        days=1, 
        max_emails=3, 
        include_text=False, 
        include_metrics=False
    )
    
    # Should not raise TypeError
    assert df is not None, "DataFrame should not be None"
    print(f"Successfully fetched {len(df)} emails with cache")


def test_gmail_client_batch_processing():
    """Test that batch processing works correctly."""
    gmail = Gmail(enable_cache=False)
    
    # Try to fetch emails with batch processing
    df = gmail.get_emails(
        days=1, 
        max_emails=10, 
        include_text=False, 
        include_metrics=False,
        use_batch=True
    )
    
    # Should not raise TypeError
    assert df is not None, "DataFrame should not be None"
    print(f"Successfully fetched {len(df)} emails with batch processing")
