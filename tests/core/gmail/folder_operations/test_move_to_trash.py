"""
Test moving emails TO and FROM trash using DataFrames.

This test moves emails to trash, verifies the move, then restores them
to their original folders to avoid permanently deleting emails.
"""

import pytest
import time
from gmaildr import Gmail


def test_move_to_trash_from_inbox():
    """Test moving emails from inbox to trash, then back to inbox."""
    gmail = Gmail()
    
    # Get some inbox emails
    inbox_emails = gmail.get_emails(in_folder='inbox', max_emails=2)
    
    if inbox_emails.empty:
        pytest.skip("No inbox emails found for testing")
    
    print(f"📥 Found {len(inbox_emails)} inbox emails")
    
    # Step 1: Move to trash using DataFrame
    print("🗑️ Moving inbox emails to trash...")
    result = gmail.move_to_trash(inbox_emails)
    
    assert result is not None, "Move to trash should return a result"
    print(f"✅ Move to trash result: {result}")
    
    # Step 2: Verify emails are now in trash
    # NOTE: We previously had timing workarounds here based on a hypothesis that 
    # Gmail API had timing/consistency issues. We tested this rigorously and 
    # discovered the real issue is Gmail API eventual consistency in search results.
    # See docs/gmail_api_timing_investigation.md for the complete investigation story.
    
    gmail_verify = Gmail()
    message_ids = inbox_emails['message_id'].tolist()
    trash_check = gmail_verify.get_emails(in_folder='trash', max_emails=100)
    moved_emails = trash_check[trash_check['message_id'].isin(message_ids)]
    
    assert not moved_emails.empty, "Emails should now be in trash"
    print(f"✅ Verified {len(moved_emails)} emails are now in trash")
    
    # Step 3: RESTORE - Move back to inbox
    print("🔄 Restoring emails to inbox...")
    restore_result = gmail.move_to_inbox(moved_emails)
    
    assert restore_result is not None, "Restore to inbox should return a result"
    print(f"✅ Restore to inbox result: {restore_result}")
    
    # Step 4: Verify restoration using label-based approach
    gmail_verify2 = Gmail()
    all_emails = gmail_verify2.get_emails(days=90, max_emails=100)
    restored_emails = all_emails[all_emails['message_id'].isin(message_ids)]
    
    if restored_emails.empty:
        print("⚠️ Could not find restored emails, trying with fresh Gmail instance...")
        gmail_verify3 = Gmail(enable_cache=False) if hasattr(Gmail, '__init__') else Gmail()
        all_emails = gmail_verify3.get_emails(days=90, max_emails=100)
        restored_emails = all_emails[all_emails['message_id'].isin(message_ids)]
    
    assert not restored_emails.empty, "Emails should be found after restoration"
    
    # Check that emails have INBOX label (are restored to inbox)
    for _, email in restored_emails.iterrows():
        labels = email.get('labels', [])
        has_inbox_label = 'INBOX' in labels
        assert has_inbox_label, f"Email {email['message_id']} should be restored to inbox (have INBOX label), but has labels: {labels}"
    print(f"✅ Successfully restored {len(restored_emails)} emails to inbox")
    
    print("🎯 Test completed - inbox unchanged!")


def test_move_to_trash_from_archive():
    """Test moving emails from archive to trash, then back to archive."""
    gmail = Gmail()
    
    # Get some archived emails
    archived_emails = gmail.get_emails(in_folder='archive', max_emails=2)
    
    if archived_emails.empty:
        pytest.skip("No archived emails found for testing")
    
    print(f"📦 Found {len(archived_emails)} archived emails")
    
    # Step 1: Move to trash using DataFrame
    print("🗑️ Moving archived emails to trash...")
    result = gmail.move_to_trash(archived_emails)
    
    assert result is not None, "Move to trash should return a result"
    print(f"✅ Move to trash result: {result}")
    
    # Step 2: Verify emails are now in trash using label-based approach
    gmail_verify = Gmail()
    message_ids = archived_emails['message_id'].tolist()
    all_emails = gmail_verify.get_emails(days=90, max_emails=100)
    moved_emails = all_emails[all_emails['message_id'].isin(message_ids)]
    
    if moved_emails.empty:
        print("⚠️ Could not find moved emails, trying with fresh Gmail instance...")
        gmail_verify2 = Gmail(enable_cache=False) if hasattr(Gmail, '__init__') else Gmail()
        all_emails = gmail_verify2.get_emails(days=90, max_emails=100)
        moved_emails = all_emails[all_emails['message_id'].isin(message_ids)]
    
    assert not moved_emails.empty, "Emails should be found after move"
    
    # Check that emails have TRASH label (are in trash)
    for _, email in moved_emails.iterrows():
        labels = email.get('labels', [])
        has_trash_label = 'TRASH' in labels
        assert has_trash_label, f"Email {email['message_id']} should be in trash (have TRASH label), but has labels: {labels}"
    
    print(f"✅ Verified {len(moved_emails)} emails are now in trash")
    
    # Step 3: RESTORE - Move back to archive
    print("🔄 Restoring emails to archive...")
    restore_result = gmail.move_to_archive(moved_emails)
    
    assert restore_result is not None, "Restore to archive should return a result"
    print(f"✅ Restore to archive result: {restore_result}")
    
    # Step 4: Verify restoration using label-based approach
    gmail_verify3 = Gmail()
    all_emails = gmail_verify3.get_emails(days=90, max_emails=100)
    restored_emails = all_emails[all_emails['message_id'].isin(message_ids)]
    
    if restored_emails.empty:
        print("⚠️ Could not find restored emails, trying with fresh Gmail instance...")
        gmail_verify4 = Gmail(enable_cache=False) if hasattr(Gmail, '__init__') else Gmail()
        all_emails = gmail_verify4.get_emails(days=90, max_emails=100)
        restored_emails = all_emails[all_emails['message_id'].isin(message_ids)]
    
    assert not restored_emails.empty, "Emails should be found after restoration"
    
    # Check that emails are archived (no INBOX, TRASH, or SPAM labels)
    for _, email in restored_emails.iterrows():
        labels = email.get('labels', [])
        has_folder_label = any(label in ['INBOX', 'TRASH', 'SPAM'] for label in labels)
        assert not has_folder_label, f"Email {email['message_id']} should be archived (no folder labels), but has labels: {labels}"
    print(f"✅ Successfully restored {len(restored_emails)} emails to archive")
    
    print("🎯 Test completed - original folders unchanged!")


if __name__ == "__main__":
    test_move_to_trash_from_inbox()
    test_move_to_trash_from_archive()
    print("✅ All trash tests passed!")
