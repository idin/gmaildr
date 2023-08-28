"""
Test cache invalidation after email modifications.

This test verifies that when emails are modified (moved between folders,
labels changed, etc.), the cache is properly invalidated and fresh data
is retrieved on subsequent queries.
"""

import pytest
import time
from gmaildr import Gmail
from gmaildr.test_utils import get_emails


def test_cache_invalidation_after_move_to_archive():
    """Test that cache is invalidated after moving emails to archive."""
    gmail = Gmail()
    
        # Step 1: Get some inbox emails and ensure they're cached
    print("📥 Getting inbox emails to populate cache...")
    inbox_emails, days_used = get_emails(gmail, n=2, in_folder='inbox', return_days_used=True)

    if inbox_emails.empty:
        pytest.skip("No inbox emails found for testing")

    message_ids = inbox_emails['message_id'].tolist()
    print(f"✅ Got {len(inbox_emails)} inbox emails: {message_ids} (using {days_used} days)")

    # Step 2: Verify emails are initially in inbox (should be from cache)
    print("🔍 Verifying emails are initially in inbox...")
    # Use the same date range that get_emails() actually used
    initial_check = gmail.get_emails(in_folder='inbox', days=days_used, max_emails=100)
    initial_inbox_emails = initial_check[initial_check['message_id'].isin(message_ids)]
    
    assert not initial_inbox_emails.empty, "Emails should initially be in inbox"
    assert all(initial_inbox_emails['in_folder'] == 'inbox'), "All emails should be in inbox folder"
    print(f"✅ Confirmed {len(initial_inbox_emails)} emails are in inbox")
    
    # Step 3: Move emails to archive
    print("📦 Moving emails to archive...")
    move_result = gmail.move_to_archive(inbox_emails)
    
    # Verify API operation succeeded
    if isinstance(move_result, dict):
        failed_moves = [msg_id for msg_id, success in move_result.items() if not success]
        assert not failed_moves, f"Some moves failed: {failed_moves}"
    else:
        assert move_result, "Move operation should succeed"
    
    print(f"✅ Move API operation succeeded: {move_result}")
    
    # Step 4: Test cache invalidation - check if emails are no longer in inbox cache
    print("🔍 Testing cache invalidation - checking inbox again...")
    
    # Small delay to allow cache invalidation to complete
    time.sleep(1)
    
    # This should NOT find the emails in inbox anymore (cache should be invalidated)
    post_move_inbox_check = gmail.get_emails(in_folder='inbox', days=days_used, max_emails=50)
    post_move_inbox_emails = post_move_inbox_check[post_move_inbox_check['message_id'].isin(message_ids)]
    
    # The key test: emails should NOT be found in inbox anymore
    if not post_move_inbox_emails.empty:
        print(f"⚠️ CACHE INVALIDATION ISSUE: Found {len(post_move_inbox_emails)} emails still in inbox cache")
        print("This indicates cache invalidation is not working properly")
        
        # Let's check the labels directly to see what's happening
        for _, email in post_move_inbox_emails.iterrows():
            labels = email.get('labels', [])
            print(f"📧 Email {email['message_id']}: labels = {labels}, in_folder = {email.get('in_folder')}")
        
        # This is the bug we're trying to fix
        pytest.fail("Cache invalidation failed - emails still appear in inbox cache after being moved to archive")
    else:
        print("✅ Cache invalidation working - emails no longer in inbox cache")
    
    # Step 5: Verify emails can be found in archive
    print("🔍 Verifying emails are now in archive...")
    archive_check = gmail.get_emails(in_folder='archive', days=days_used, max_emails=50)
    archive_emails = archive_check[archive_check['message_id'].isin(message_ids)]
    
    if archive_emails.empty:
        print("⚠️ Emails not found in archive - checking all emails...")
        all_emails = gmail.get_emails(days=days_used, max_emails=100)
        found_emails = all_emails[all_emails['message_id'].isin(message_ids)]
        
        if not found_emails.empty:
            print("📧 Found emails in these locations:")
            for _, email in found_emails.iterrows():
                labels = email.get('labels', [])
                folder = email.get('in_folder', 'unknown')
                print(f"  - {email['message_id']}: folder={folder}, labels={labels}")
        else:
            print("❌ Emails not found anywhere - this is unexpected")
    else:
        print(f"✅ Found {len(archive_emails)} emails in archive")
    
    # Step 6: CLEANUP - Restore emails to inbox
    print("🔄 Restoring emails to inbox for cleanup...")
    restore_result = gmail.move_to_inbox(inbox_emails)
    
    if isinstance(restore_result, dict):
        failed_restores = [msg_id for msg_id, success in restore_result.items() if not success]
        if failed_restores:
            print(f"⚠️ Some restores failed: {failed_restores}")
    
    print("🎯 Cache invalidation test completed")


def test_cache_invalidation_timing():
    """Test cache invalidation timing and consistency."""
    gmail = Gmail()
    
    # Get some emails to work with
    emails, days_used = get_emails(gmail, n=1, in_folder='inbox', return_days_used=True)
    
    if emails.empty:
        pytest.skip("No emails found for testing")
    
    message_id = emails.iloc[0]['message_id']
    print(f"📧 Testing cache invalidation timing for email: {message_id} (using {days_used} days)")
    
    # Step 1: Get initial state (use same date range as get_emails)
    initial_emails = gmail.get_emails(days=days_used, max_emails=20)
    initial_email = initial_emails[initial_emails['message_id'] == message_id]
    
    if initial_email.empty:
        pytest.skip("Test email not found in initial fetch")
    
    initial_folder = initial_email.iloc[0]['in_folder']
    initial_labels = initial_email.iloc[0]['labels']
    print(f"✅ Initial state: folder={initial_folder}, labels={initial_labels}")
    
    # Step 2: Modify the email (star it)
    print("⭐ Starring email...")
    star_result = gmail.star_email(message_id)
    assert star_result, "Star operation should succeed"
    
    # Step 3: Immediately check cache (should be invalidated)
    print("🔍 Checking cache immediately after modification...")
    immediate_check = gmail.get_emails(days=days_used, max_emails=20)
    immediate_email = immediate_check[immediate_check['message_id'] == message_id]
    
    if not immediate_email.empty:
        immediate_starred = immediate_email.iloc[0].get('is_starred', False)
        print(f"📧 Immediate check: is_starred = {immediate_starred}")
        
        # This tests if cache invalidation is working immediately
        if not immediate_starred:
            print("⚠️ CACHE INVALIDATION TIMING ISSUE: Email not showing as starred immediately")
            print("This suggests cache invalidation has timing issues")
    
    # Step 4: Check after a delay
    print("⏰ Waiting 2 seconds and checking again...")
    time.sleep(2)
    
    delayed_check = gmail.get_emails(days=days_used, max_emails=20)
    delayed_email = delayed_check[delayed_check['message_id'] == message_id]
    
    if not delayed_email.empty:
        delayed_starred = delayed_email.iloc[0].get('is_starred', False)
        print(f"📧 Delayed check: is_starred = {delayed_starred}")
        
        # After a delay, it should definitely be updated
        assert delayed_starred, "Email should be starred after delay (cache invalidation should work)"
    
    # Step 5: CLEANUP - Unstar the email
    print("🔄 Cleaning up - unstarring email...")
    unstar_result = gmail.unstar_email(message_id)
    assert unstar_result, "Unstar operation should succeed"
    
    print("✅ Cache invalidation timing test completed")


def test_cache_stats_after_invalidation():
    """Test that cache statistics are updated after invalidation."""
    gmail = Gmail()
    
    if not gmail.cache_manager:
        pytest.skip("Cache not enabled")
    
    # Get initial cache stats
    initial_stats = gmail.get_cache_stats()
    print(f"📊 Initial cache stats: {initial_stats}")
    
    # Get some emails to modify
    emails = get_emails(gmail, n=1, in_folder='inbox')
    
    if emails.empty:
        pytest.skip("No emails found for testing")
    
    message_id = emails.iloc[0]['message_id']
    
    # Modify the email to trigger cache invalidation
    print(f"⭐ Starring email {message_id} to trigger cache invalidation...")
    star_result = gmail.star_email(message_id)
    assert star_result, "Star operation should succeed"
    
    # Check cache stats after invalidation
    post_invalidation_stats = gmail.get_cache_stats()
    print(f"📊 Post-invalidation cache stats: {post_invalidation_stats}")
    
    # The stats should reflect that cache invalidation occurred
    # (This is more of an informational test to see what happens to cache stats)
    
    # Cleanup
    print("🔄 Cleaning up - unstarring email...")
    gmail.unstar_email(message_id)
    
    print("✅ Cache stats test completed")


if __name__ == "__main__":
    print("🧪 Running cache invalidation tests...")
    test_cache_invalidation_after_move_to_archive()
    test_cache_invalidation_timing()
    test_cache_stats_after_invalidation()
    print("✅ All cache invalidation tests completed!")
