"""
Test moving emails TO and FROM inbox using DataFrames.

This test moves emails to inbox, verifies the move, then restores them
to their original folders to avoid messing with the user's inbox.
"""

import pytest
from gmaildr import Gmail


def test_move_to_inbox_from_archive():
    """Test moving emails from archive to inbox, then back to archive."""
    gmail = Gmail()
    
    # Get some archived emails
    archived_emails = gmail.get_emails(in_folder='archive', max_emails=2)
    
    if archived_emails.empty:
        pytest.skip("No archived emails found for testing")
    
    print(f"📦 Found {len(archived_emails)} archived emails")
    
    # Record original folder for restoration
    original_folder = 'archive'
    
    # Step 1: Move to inbox using DataFrame
    print("📥 Moving archived emails to inbox...")
    result = gmail.move_to_inbox(archived_emails)
    
    # Verify the move worked
    assert result is not None, "Move to inbox should return a result"
    print(f"✅ Move to inbox result: {result}")
    
    # Step 2: Verify emails are now in inbox
    message_ids = archived_emails['message_id'].tolist()
    
    # NOTE: We avoid folder-based search queries due to Gmail API eventual consistency.
    # Instead, we fetch emails directly and check their labels for reliable verification.
    # See docs/gmail_api_timing_investigation.md for the complete investigation story.
    
    gmail_verify = Gmail()
    all_emails = gmail_verify.get_emails(days=365, max_emails=1000)
    moved_emails = all_emails[all_emails['message_id'].isin(message_ids)]
    
    if moved_emails.empty:
        print("⚠️ Could not find moved emails, trying with fresh Gmail instance...")
        gmail_verify2 = Gmail(enable_cache=False) if hasattr(Gmail, '__init__') else Gmail()
        all_emails = gmail_verify2.get_emails(days=365, max_emails=1000)
        moved_emails = all_emails[all_emails['message_id'].isin(message_ids)]
    
    assert not moved_emails.empty, "Emails should be found after move"
    
    # Check that emails have INBOX label (are in inbox)
    for _, email in moved_emails.iterrows():
        labels = email.get('labels', [])
        has_inbox_label = 'INBOX' in labels
        assert has_inbox_label, f"Email {email['message_id']} should be in inbox (have INBOX label), but has labels: {labels}"
    
    print(f"✅ Verified {len(moved_emails)} emails are now in inbox")
    
    # Step 3: RESTORE - Move back to original folder (archive)
    print("🔄 Restoring emails to archive...")
    restore_result = gmail.move_to_archive(moved_emails)
    
    assert restore_result is not None, "Restore to archive should return a result"
    print(f"✅ Restore to archive result: {restore_result}")
    
    gmail_verify3 = Gmail()
    all_emails = gmail_verify3.get_emails(days=365, max_emails=1000)
    restored_emails = all_emails[all_emails['message_id'].isin(message_ids)]
    
    if restored_emails.empty:
        print("⚠️ Could not find restored emails, trying with fresh Gmail instance...")
        gmail_verify4 = Gmail(enable_cache=False) if hasattr(Gmail, '__init__') else Gmail()
        all_emails = gmail_verify4.get_emails(days=365, max_emails=1000)
        restored_emails = all_emails[all_emails['message_id'].isin(message_ids)]
    
    assert not restored_emails.empty, "Emails should be found after restoration"
    
    # Check that emails are archived (no INBOX, TRASH, or SPAM labels)
    for _, email in restored_emails.iterrows():
        labels = email.get('labels', [])
        has_folder_label = any(label in ['INBOX', 'TRASH', 'SPAM'] for label in labels)
        assert not has_folder_label, f"Email {email['message_id']} should be archived (no folder labels), but has labels: {labels}"
    print(f"✅ Successfully restored {len(restored_emails)} emails to archive")
    
    print("🎯 Test completed - inbox unchanged!")


def test_move_to_inbox_from_trash():
    """Test moving emails from trash to inbox, then back to trash."""
    gmail = Gmail()
    
    # Get some trash emails
    trash_emails = gmail.get_emails(in_folder='trash', max_emails=2)
    
    if trash_emails.empty:
        pytest.skip("No trash emails found for testing")
    
    print(f"🗑️ Found {len(trash_emails)} trash emails")
    
    # Step 1: Move to inbox using DataFrame
    print("📥 Moving trash emails to inbox...")
    result = gmail.move_to_inbox(trash_emails)
    
    assert result is not None, "Move to inbox should return a result"
    print(f"✅ Move to inbox result: {result}")
    
    # Step 2: Verify emails are now in inbox
    message_ids = trash_emails['message_id'].tolist()
    
    # Verify using label-based approach (avoid folder search due to eventual consistency)
    gmail_verify = Gmail()
    all_emails = gmail_verify.get_emails(days=365, max_emails=1000)
    moved_emails = all_emails[all_emails['message_id'].isin(message_ids)]
    
    if moved_emails.empty:
        print("⚠️ Could not find moved emails, trying with fresh Gmail instance...")
        gmail_verify2 = Gmail(enable_cache=False) if hasattr(Gmail, '__init__') else Gmail()
        all_emails = gmail_verify2.get_emails(days=365, max_emails=1000)
        moved_emails = all_emails[all_emails['message_id'].isin(message_ids)]
    
    assert not moved_emails.empty, "Emails should be found after move"
    
    # Check that emails have INBOX label (are in inbox)
    for _, email in moved_emails.iterrows():
        labels = email.get('labels', [])
        has_inbox_label = 'INBOX' in labels
        assert has_inbox_label, f"Email {email['message_id']} should be in inbox (have INBOX label), but has labels: {labels}"
    
    print(f"✅ Verified {len(moved_emails)} emails are now in inbox")
    
    # Step 3: RESTORE - Move back to trash
    print("🔄 Restoring emails to trash...")
    restore_result = gmail.move_to_trash(moved_emails)
    
    assert restore_result is not None, "Restore to trash should return a result"
    print(f"✅ Restore to trash result: {restore_result}")
    
    # Step 4: Verify restoration
    gmail_verify2 = Gmail()
    trash_check = gmail_verify2.get_emails(in_folder='trash', max_emails=100)
    restored_emails = trash_check[trash_check['message_id'].isin(message_ids)]
    
    assert not restored_emails.empty, "Emails should be restored to trash"
    print(f"✅ Successfully restored {len(restored_emails)} emails to trash")
    
    print("🎯 Test completed - inbox unchanged!")


if __name__ == "__main__":
    test_move_to_inbox_from_archive()
    test_move_to_inbox_from_trash()
    print("✅ All inbox tests passed!")
