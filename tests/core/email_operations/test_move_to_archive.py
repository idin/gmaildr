"""
Tests for move_to_archive functionality.
"""

import pytest

from gmaildr.core.gmail import Gmail


def test_move_to_archive_single_message():
    """Test move_to_archive with single message ID."""
    gmail = Gmail()
    
    # Get a real email from inbox first
    emails = gmail.get_emails(days=1, max_emails=1, in_folder='inbox')
    if emails.is_empty():
        pytest.skip("No inbox emails available for testing")
    
    message_id = emails.iloc[0]['message_id']
    
    # Move to archive
    result = gmail.move_to_archive(message_id)
    assert result is True or isinstance(result, dict)
    
    # Verify the email was actually moved to archive
    archived_emails = gmail.get_emails(days=1, max_emails=10, in_folder='archive')
    archived_message_ids = archived_emails['message_id'].tolist()
    assert message_id in archived_message_ids


def test_move_to_archive_multiple_messages():
    """Test move_to_archive with multiple message IDs."""
    gmail = Gmail()
    
    # Get real emails from inbox first
    emails = gmail.get_emails(days=1, max_emails=2, in_folder='inbox')
    if len(emails) < 2:
        pytest.skip("Not enough inbox emails available for testing")
    
    message_ids = emails['message_id'].tolist()[:2]
    
    # Move to archive
    result = gmail.move_to_archive(message_ids)
    assert result is True or isinstance(result, dict)
    
    # Verify the emails were actually moved to archive
    archived_emails = gmail.get_emails(days=1, max_emails=10, in_folder='archive')
    archived_message_ids = archived_emails['message_id'].tolist()
    for message_id in message_ids:
        assert message_id in archived_message_ids


def test_move_to_archive_with_progress():
    """Test move_to_archive with progress bar disabled."""
    gmail = Gmail()
    
    # Get a real email from inbox first
    emails = gmail.get_emails(days=1, max_emails=1, in_folder='inbox')
    if emails.is_empty():
        pytest.skip("No inbox emails available for testing")
    
    message_id = emails.iloc[0]['message_id']
    
    # Move to archive with progress disabled
    result = gmail.move_to_archive(message_id, show_progress=False)
    assert result is True or isinstance(result, dict)
    
    # Verify the email was actually moved to archive
    archived_emails = gmail.get_emails(days=1, max_emails=10, in_folder='archive')
    archived_message_ids = archived_emails['message_id'].tolist()
    assert message_id in archived_message_ids