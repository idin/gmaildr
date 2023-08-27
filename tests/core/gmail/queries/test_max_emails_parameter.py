"""
Test max_emails parameter functionality.

This test verifies that the max_emails parameter works correctly in email queries.
"""

from gmaildr import Gmail
from gmaildr.test_utils import get_emails
import pytest


def test_max_emails_parameter():
    """Test that max_emails parameter limits the number of emails returned."""
    gmail = Gmail()
    
    # Test with different max_emails values using the helper function
    test_cases = [1, 3, 5, 10]
    
    for max_count in test_cases:
        # Get emails using the helper function
        emails = get_emails(gmail, max_count)
        
        if len(emails) == 0:
            pytest.skip("No emails available to test with")
        
        # Verify that we don't get more emails than requested
        assert len(emails) <= max_count, f"Got {len(emails)} emails but requested max {max_count}"
        
        # Verify the structure is correct
        assert 'message_id' in emails.columns
        assert 'subject' in emails.columns
        assert 'sender_email' in emails.columns
        
        # Test that we can access individual emails
        first_email = emails.iloc[0]
        assert 'message_id' in first_email
        assert 'subject' in first_email
        
        print(f"Successfully retrieved {len(emails)} emails (max requested: {max_count})")
    
    print("All max_emails parameter tests passed")
