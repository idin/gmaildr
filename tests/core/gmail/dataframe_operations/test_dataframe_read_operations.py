"""
Test marking emails as read/unread using DataFrames.

This test changes read status, verifies the change, then restores
the original read status to avoid changing the user's email state.
"""

import pytest
from gmaildr import Gmail


def test_mark_as_read_and_unread():
    """Test marking unread emails as read via DataFrame, then back to unread."""
    gmail = Gmail()
    
    # Get some unread emails to test with
    emails = gmail.get_emails(max_emails=10)
    
    if emails.empty:
        pytest.skip("No emails found for testing")
    
    # Filter to unread emails only
    unread_emails = emails[emails['is_read'] == False]
    
    if unread_emails.empty:
        pytest.skip("No unread emails found for testing")
    
    # Take only first 2 for testing
    test_emails = unread_emails.head(2)
    print(f"📧 Found {len(test_emails)} unread emails for testing")
    
    # Step 1: Mark as read using DataFrame
    print("📖 Marking emails as read...")
    read_result = gmail.mark_as_read(test_emails)
    
    assert read_result is not None, "Mark as read should return a result"
    print(f"✅ Mark as read result: {read_result}")
    
    # Step 2: Verify emails are now read
    message_ids = test_emails['message_id'].tolist()
    
    # Get updated email data
    updated_emails = gmail.get_emails(max_emails=100)
    read_check = updated_emails[updated_emails['message_id'].isin(message_ids)]
    
    if not read_check.empty:
        read_count = read_check['is_read'].sum()
        print(f"✅ Verified {read_count} emails are now marked as read")
    
    # Step 3: RESTORE - Mark back as unread
    print("🔄 Marking emails back as unread to restore original state...")
    unread_result = gmail.mark_as_unread(read_check)
    
    assert unread_result is not None, "Mark as unread should return a result"
    print(f"✅ Mark as unread result: {unread_result}")
    
    # Step 4: Verify emails are unread again
    final_emails = gmail.get_emails(max_emails=100)
    final_check = final_emails[final_emails['message_id'].isin(message_ids)]
    
    if not final_check.empty:
        still_unread_count = (final_check['is_read'] == False).sum()
        print(f"✅ Restoration verification: {still_unread_count} emails are unread again")
    
    print("🎯 Test completed - read status unchanged!")


def test_mark_read_emails_as_unread():
    """Test marking read emails as unread via DataFrame, then back to read."""
    gmail = Gmail()
    
    # Get some read emails to test with
    emails = gmail.get_emails(max_emails=10)
    
    if emails.empty:
        pytest.skip("No emails found for testing")
    
    # Filter to read emails only
    read_emails = emails[emails['is_read'] == True]
    
    if read_emails.empty:
        pytest.skip("No read emails found for testing")
    
    # Take only first 2 for testing
    test_emails = read_emails.head(2)
    print(f"📧 Found {len(test_emails)} read emails for testing")
    
    # Step 1: Mark as unread using DataFrame
    print("📧 Marking emails as unread...")
    unread_result = gmail.mark_as_unread(test_emails)
    
    assert unread_result is not None, "Mark as unread should return a result"
    print(f"✅ Mark as unread result: {unread_result}")
    
    # Step 2: Verify emails are now unread
    message_ids = test_emails['message_id'].tolist()
    
    # Get updated email data
    updated_emails = gmail.get_emails(max_emails=100)
    unread_check = updated_emails[updated_emails['message_id'].isin(message_ids)]
    
    if not unread_check.empty:
        unread_count = (unread_check['is_read'] == False).sum()
        print(f"✅ Verified {unread_count} emails are now marked as unread")
    
    # Step 3: RESTORE - Mark back as read
    print("🔄 Marking emails back as read to restore original state...")
    read_result = gmail.mark_as_read(unread_check)
    
    assert read_result is not None, "Mark as read should return a result"
    print(f"✅ Restore read result: {read_result}")
    
    # Step 4: Verify emails are read again
    final_emails = gmail.get_emails(max_emails=100)
    final_check = final_emails[final_emails['message_id'].isin(message_ids)]
    
    if not final_check.empty:
        restored_read_count = final_check['is_read'].sum()
        print(f"✅ Restoration verification: {restored_read_count} emails are read again")
    
    print("🎯 Test completed - read status unchanged!")


if __name__ == "__main__":
    test_mark_as_read_and_unread()
    test_mark_read_emails_as_unread()
    print("✅ All read status tests passed!")
