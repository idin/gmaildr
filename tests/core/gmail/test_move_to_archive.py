"""
Test email move to archive functionality.

This test verifies that emails can be moved to archive correctly.
"""

from gmaildr import Gmail
from tests.core.gmail.test_get_emails import get_emails
import pytest


def test_move_single_email_to_archive():
    """Test moving a single email to archive."""
    gmail = Gmail()
    
    # Get emails from inbox using the helper function
    emails = get_emails(gmail, 1, in_folder='inbox')
    
    if len(emails) == 0:
        pytest.skip("No emails in inbox to test with")
    
    # Get the first email
    email = emails.iloc[0]
    message_id = email['message_id']
    
    # Move to archive
    result = gmail.move_to_archive(message_id)
    
    # Verify the email was moved
    assert result is True or (isinstance(result, dict) and result.get(message_id, False))
    
    # Check that the email is no longer in inbox - REMOVED days parameter as it's not necessary for verification
    updated_emails = get_emails(gmail, 10, in_folder='inbox')
    assert message_id not in updated_emails['message_id'].values
    
    # Check that the email is now in archive - REMOVED days parameter as it's not necessary for verification
    archived_emails = get_emails(gmail, 10, in_folder='archive')
    assert message_id in archived_emails['message_id'].values


def test_move_multiple_emails_to_archive():
    """Test moving multiple emails to archive."""
    gmail = Gmail()
    
    # Get emails from inbox using the helper function
    emails = get_emails(gmail, 2, in_folder='inbox')
    
    if len(emails) < 2:
        pytest.skip("Not enough emails in inbox to test with")
    
    # Get the first two emails
    message_ids = emails.head(2)['message_id'].tolist()
    
    # Move to archive
    result = gmail.move_to_archive(message_ids)
    
    # Verify the emails were moved
    if isinstance(result, dict):
        for message_id in message_ids:
            assert result.get(message_id, False)
    else:
        assert result is True
    
    # Check that the emails are no longer in inbox - REMOVED days parameter as it's not necessary for verification
    updated_emails = get_emails(gmail, 10, in_folder='inbox')
    for message_id in message_ids:
        assert message_id not in updated_emails['message_id'].values
    
    # Check that the emails are now in archive - REMOVED days parameter as it's not necessary for verification
    archived_emails = get_emails(gmail, 10, in_folder='archive')
    for message_id in message_ids:
        assert message_id in archived_emails['message_id'].values


def test_move_to_archive_with_batch():
    """Test moving emails to archive with batch processing."""
    gmail = Gmail()
    
    # Get emails from inbox using the helper function
    emails = get_emails(gmail, 1, in_folder='inbox')
    
    if len(emails) == 0:
        pytest.skip("No emails in inbox to test with")
    
    # Get the first email
    email = emails.iloc[0]
    message_id = email['message_id']
    
    # Move to archive with batch processing
    result = gmail.move_to_archive(message_id, show_progress=True)
    
    # Verify the email was moved
    assert result is True or (isinstance(result, dict) and result.get(message_id, False))
    
    # Check that the email is no longer in inbox - REMOVED days parameter as it's not necessary for verification
    updated_emails = get_emails(gmail, 10, in_folder='inbox')
    assert message_id not in updated_emails['message_id'].values
    
    # Check that the email is now in archive - REMOVED days parameter as it's not necessary for verification
    archived_emails = get_emails(gmail, 10, in_folder='archive')
    assert message_id in archived_emails['message_id'].values


def test_move_to_archive_verification():
    """Test that move_to_archive properly verifies the operation."""
    gmail = Gmail()
    
    # Get emails from inbox using the helper function
    emails = get_emails(gmail, 1, in_folder='inbox')
    
    if len(emails) == 0:
        pytest.skip("No emails in inbox to test with")
    
    # Get the first email
    email = emails.iloc[0]
    message_id = email['message_id']
    
    # Move to archive
    result = gmail.move_to_archive(message_id)
    
    # Verify the email was moved
    assert result is True or (isinstance(result, dict) and result.get(message_id, False))
    
    # Check that the email is no longer in inbox - REMOVED days parameter as it's not necessary for verification
    updated_emails = get_emails(gmail, 10, in_folder='inbox')
    assert message_id not in updated_emails['message_id'].values
    
    # Check that the email is now in archive - REMOVED days parameter as it's not necessary for verification
    archived_emails = get_emails(gmail, 10, in_folder='archive')
    assert message_id in archived_emails['message_id'].values