"""
Test moving emails TO and FROM archive using DataFrames.

This test moves emails to archive, verifies the move, then restores them
to their original folders to avoid changing the user's email organization.
"""

import pytest
import time
from gmaildr import Gmail


def test_move_to_archive_from_inbox():
    """Test moving emails from inbox to archive, then back to inbox."""
    gmail = Gmail()
    
    # Get some inbox emails
    inbox_emails = gmail.get_emails(in_folder='inbox', max_emails=2)
    
    if inbox_emails.empty:
        pytest.skip("No inbox emails found for testing")
    
    print(f"📥 Found {len(inbox_emails)} inbox emails")
    
    # Step 1: Move to archive using DataFrame
    print("📦 Moving inbox emails to archive...")
    result = gmail.move_to_archive(inbox_emails)
    
    assert result is not None, "Move to archive should return a result"
    print(f"✅ Move to archive result: {result}")
    
    # Step 2: Verify emails are now in archive (check labels directly)
    time.sleep(2)  # Allow cache to update
    gmail_verify = Gmail()
    message_ids = inbox_emails['message_id'].tolist()
    
    # Get the specific emails by ID to check their labels
    all_emails = gmail_verify.get_emails(days=365, max_emails=1000)
    moved_emails = all_emails[all_emails['message_id'].isin(message_ids)]
    
    if moved_emails.empty:
        print("⚠️ Could not find moved emails, trying with fresh Gmail instance...")
        gmail_verify2 = Gmail(enable_cache=False) if hasattr(Gmail, '__init__') else Gmail()
        all_emails = gmail_verify2.get_emails(days=365, max_emails=1000)
        moved_emails = all_emails[all_emails['message_id'].isin(message_ids)]
    
    assert not moved_emails.empty, "Emails should be found after move"
    
    # Check that emails are archived (not in INBOX, TRASH, or SPAM)
    for _, email in moved_emails.iterrows():
        labels = email.get('labels', [])
        has_folder_label = any(label in ['INBOX', 'TRASH', 'SPAM'] for label in labels)
        assert not has_folder_label, f"Email {email['message_id']} should be archived (no folder labels), but has labels: {labels}"
    
    print(f"✅ Verified {len(moved_emails)} emails are now archived (no folder labels)")
    
    # Step 3: RESTORE - Move back to inbox
    print("🔄 Restoring emails to inbox...")
    restore_result = gmail.move_to_inbox(moved_emails)
    
    assert restore_result is not None, "Restore to inbox should return a result"
    print(f"✅ Restore to inbox result: {restore_result}")
    
    # Step 4: Verify restoration (check labels directly)
    time.sleep(2)  # Allow cache to update
    gmail_verify3 = Gmail()
    all_emails_after = gmail_verify3.get_emails(days=365, max_emails=1000)
    restored_emails = all_emails_after[all_emails_after['message_id'].isin(message_ids)]
    
    assert not restored_emails.empty, "Emails should be found after restoration"
    
    # Check that emails are back in inbox (have INBOX label)
    for _, email in restored_emails.iterrows():
        labels = email.get('labels', [])
        assert 'INBOX' in labels, f"Email {email['message_id']} should be in inbox, but has labels: {labels}"
    
    print(f"✅ Successfully restored {len(restored_emails)} emails to inbox")
    
    print("🎯 Test completed - inbox unchanged!")


def test_move_to_archive_from_trash():
    """Test moving emails from trash to archive, then back to trash."""
    gmail = Gmail()
    
    # Get some trash emails
    trash_emails = gmail.get_emails(in_folder='trash', max_emails=2)
    
    if trash_emails.empty:
        pytest.skip("No trash emails found for testing")
    
    print(f"🗑️ Found {len(trash_emails)} trash emails")
    
    # Step 1: Move to archive using DataFrame
    print("📦 Moving trash emails to archive...")
    result = gmail.move_to_archive(trash_emails)
    
    assert result is not None, "Move to archive should return a result"
    print(f"✅ Move to archive result: {result}")
    
    # Step 2: Verify emails are now in archive (check labels directly)
    time.sleep(2)  # Allow cache to update
    gmail_verify = Gmail()
    message_ids = trash_emails['message_id'].tolist()
    
    # Get the specific emails by ID to check their labels
    all_emails = gmail_verify.get_emails(days=365, max_emails=1000)
    moved_emails = all_emails[all_emails['message_id'].isin(message_ids)]
    
    assert not moved_emails.empty, "Emails should be found after move"
    
    # Check that emails are archived (not in INBOX, TRASH, or SPAM)
    for _, email in moved_emails.iterrows():
        labels = email.get('labels', [])
        has_folder_label = any(label in ['INBOX', 'TRASH', 'SPAM'] for label in labels)
        assert not has_folder_label, f"Email {email['message_id']} should be archived (no folder labels), but has labels: {labels}"
    
    print(f"✅ Verified {len(moved_emails)} emails are now archived (no folder labels)")
    
    # Step 3: RESTORE - Move back to trash
    print("🔄 Restoring emails to trash...")
    restore_result = gmail.move_to_trash(moved_emails)
    
    assert restore_result is not None, "Restore to trash should return a result"
    print(f"✅ Restore to trash result: {restore_result}")
    
    # Step 4: Verify restoration (check labels directly)
    time.sleep(2)  # Allow cache to update
    gmail_verify3 = Gmail()
    all_emails_after = gmail_verify3.get_emails(days=365, max_emails=1000)
    restored_emails = all_emails_after[all_emails_after['message_id'].isin(message_ids)]
    
    assert not restored_emails.empty, "Emails should be found after restoration"
    
    # Check that emails are back in trash (have TRASH label)
    for _, email in restored_emails.iterrows():
        labels = email.get('labels', [])
        assert 'TRASH' in labels, f"Email {email['message_id']} should be in trash, but has labels: {labels}"
    
    print(f"✅ Successfully restored {len(restored_emails)} emails to trash")
    
    print("🎯 Test completed - original folders unchanged!")


if __name__ == "__main__":
    test_move_to_archive_from_inbox()
    test_move_to_archive_from_trash()
    print("✅ All archive tests passed!")