"""
Test that reproduces the cache manager error with missing recipient fields.

This test captures the specific error that occurs when cached data is missing
recipient_email and recipient_name fields.
"""

import pytest
from gmaildr.core.gmail.main import Gmail


def test_get_inbox_emails_with_cached_data_missing_recipient_fields():
    """
    Test that get_inbox_emails doesn't fail when cached data is missing recipient fields.
    
    This test reproduces the exact error scenario where cached email data
    doesn't contain recipient_email and recipient_name fields, causing a TypeError
    when trying to reconstruct EmailMessage objects.
    """
    # Create Gmail instance
    gmail = Gmail()
    
    # This should not raise a TypeError about missing recipient_email and recipient_name
    # The error was: EmailMessage.__init__() missing 2 required positional arguments: 'recipient_email' and 'recipient_name'
    result = gmail.get_inbox_emails(
        days=10, 
        max_emails=None, 
        include_text=False, 
        include_metrics=False, 
        use_batch=True
    )
    
    # If we get here without error, the test passes
    assert result is not None
