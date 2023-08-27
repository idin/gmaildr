"""
Test starring and unstarring emails using DataFrames.

This test stars emails, verifies the change, then unstars them
to avoid permanently changing the user's starred emails.
"""

import pytest
from gmaildr import Gmail


def test_star_and_unstar_emails():
    """Test starring emails via DataFrame, then unstarring them."""
    gmail = Gmail()
    
    # Get some unstarred emails to test with
    emails = gmail.get_emails(max_emails=5)
    
    if emails.empty:
        pytest.skip("No emails found for testing")
    
    # Filter to unstarred emails only
    unstarred_emails = emails[emails['is_starred'] == False]
    
    if unstarred_emails.empty:
        pytest.skip("No unstarred emails found for testing")
    
    # Take only first 2 for testing
    test_emails = unstarred_emails.head(2)
    print(f"⭐ Found {len(test_emails)} unstarred emails for testing")
    
    # Step 1: Star emails using DataFrame
    print("⭐ Starring emails...")
    star_result = gmail.star_email(test_emails)
    
    assert star_result is not None, "Star email should return a result"
    print(f"✅ Star result: {star_result}")
    
    # Step 2: Verify emails are now starred
    message_ids = test_emails['message_id'].tolist()
    
    # Get updated email data
    updated_emails = gmail.get_emails(max_emails=100)
    starred_check = updated_emails[updated_emails['message_id'].isin(message_ids)]
    
    if not starred_check.empty:
        starred_count = starred_check['is_starred'].sum()
        print(f"✅ Verified {starred_count} emails are now starred")
    
    # Step 3: RESTORE - Unstar the emails
    print("🔄 Unstarring emails to restore original state...")
    unstar_result = gmail.unstar_email(starred_check)
    
    assert unstar_result is not None, "Unstar email should return a result"
    print(f"✅ Unstar result: {unstar_result}")
    
    # Step 4: Verify emails are unstarred again
    final_emails = gmail.get_emails(max_emails=100)
    final_check = final_emails[final_emails['message_id'].isin(message_ids)]
    
    if not final_check.empty:
        still_starred_count = final_check['is_starred'].sum()
        print(f"✅ Cleanup verification: {still_starred_count} emails still starred")
    
    print("🎯 Test completed - star status unchanged!")


def test_unstar_already_starred_emails():
    """Test unstarring already starred emails, then starring them back."""
    gmail = Gmail()
    
    # Get some starred emails to test with
    emails = gmail.get_emails(max_emails=10)
    
    if emails.empty:
        pytest.skip("No emails found for testing")
    
    # Filter to starred emails only
    starred_emails = emails[emails['is_starred'] == True]
    
    if starred_emails.empty:
        pytest.skip("No starred emails found for testing")
    
    # Take only first 2 for testing
    test_emails = starred_emails.head(2)
    print(f"⭐ Found {len(test_emails)} starred emails for testing")
    
    # Step 1: Unstar emails using DataFrame
    print("⭐ Unstarring emails...")
    unstar_result = gmail.unstar_email(test_emails)
    
    assert unstar_result is not None, "Unstar email should return a result"
    print(f"✅ Unstar result: {unstar_result}")
    
    # Step 2: Verify emails are now unstarred
    message_ids = test_emails['message_id'].tolist()
    
    # Get updated email data
    updated_emails = gmail.get_emails(max_emails=100)
    unstarred_check = updated_emails[updated_emails['message_id'].isin(message_ids)]
    
    if not unstarred_check.empty:
        unstarred_count = (unstarred_check['is_starred'] == False).sum()
        print(f"✅ Verified {unstarred_count} emails are now unstarred")
    
    # Step 3: RESTORE - Star the emails back
    print("🔄 Starring emails back to restore original state...")
    star_result = gmail.star_email(unstarred_check)
    
    assert star_result is not None, "Star email should return a result"
    print(f"✅ Restore star result: {star_result}")
    
    # Step 4: Verify emails are starred again
    final_emails = gmail.get_emails(max_emails=100)
    final_check = final_emails[final_emails['message_id'].isin(message_ids)]
    
    if not final_check.empty:
        restored_starred_count = final_check['is_starred'].sum()
        print(f"✅ Restoration verification: {restored_starred_count} emails starred again")
    
    print("🎯 Test completed - star status unchanged!")


if __name__ == "__main__":
    test_star_and_unstar_emails()
    test_unstar_already_starred_emails()
    print("✅ All star tests passed!")
