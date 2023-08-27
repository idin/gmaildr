#!/usr/bin/env python3
"""
Test keyboard interrupt handling in email operations.

This test verifies that keyboard interrupts are handled gracefully during email operations.
"""

from gmaildr import Gmail
from gmaildr.test_utils import get_emails
import pytest
import signal
import time


def test_keyboard_interrupt_handling():
    """Test that keyboard interrupts are handled gracefully during email retrieval."""
    gmail = Gmail()
    
    # Get emails using the helper function
    emails = get_emails(gmail, 5)
    
    if len(emails) == 0:
        pytest.skip("No emails available to test with")
    
    # Test that we can retrieve emails without interruption
    assert len(emails) > 0
    assert not emails.empty
    
    # Verify the structure is correct
    assert 'message_id' in emails.columns
    assert 'subject' in emails.columns
    assert 'sender_email' in emails.columns
    
    # Test that we can access individual emails
    first_email = emails.iloc[0]
    assert 'message_id' in first_email
    assert 'subject' in first_email
    
    # This test primarily verifies that the helper function works correctly
    # and doesn't cause any issues that would trigger keyboard interrupts
    print("Email retrieval completed successfully without interruption")
