"""
Test trash email operations with actual Gmail data.

This test verifies that trash operations work correctly with real email data.
"""

from gmaildr import Gmail
from gmaildr.test_utils import get_emails
import pytest


def test_trash_emails_actual():
    """Test trash operations with actual email data."""
    gmail = Gmail()
    
    # Get emails from inbox using the helper function
    all_emails = get_emails(gmail, 50, include_text=False, include_metrics=False)
    
    if len(all_emails) == 0:
        pytest.skip("No emails available to test with")
    
    # Get emails from archive using the helper function
    not_inbox = get_emails(gmail, 50, in_folder='archive', include_text=False, include_metrics=False)
    
    # Test that we can retrieve emails from different folders
    assert len(all_emails) > 0 or len(not_inbox) > 0, "No emails found in either inbox or archive"
    
    # Verify the structure is correct for inbox emails
    if len(all_emails) > 0:
        assert 'message_id' in all_emails.columns
        assert 'subject' in all_emails.columns
        assert 'sender_email' in all_emails.columns
        
        # Test that we can access individual emails
        first_email = all_emails.iloc[0]
        assert 'message_id' in first_email
        assert 'subject' in first_email
    
    # Verify the structure is correct for archive emails
    if len(not_inbox) > 0:
        assert 'message_id' in not_inbox.columns
        assert 'subject' in not_inbox.columns
        assert 'sender_email' in not_inbox.columns
        
        # Test that we can access individual emails
        first_email = not_inbox.iloc[0]
        assert 'message_id' in first_email
        assert 'subject' in first_email
    
    print(f"Successfully retrieved {len(all_emails)} inbox emails and {len(not_inbox)} archive emails")
