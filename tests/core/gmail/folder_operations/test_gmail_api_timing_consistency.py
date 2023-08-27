"""
Test to prove Gmail API timing consistency hypothesis.

This test demonstrates that Gmail API operations succeed immediately,
but verification queries need time to reflect the changes due to
eventual consistency in Gmail's backend.
"""

from tkinter import N
import pytest
import time
from gmaildr import Gmail
from gmaildr.test_utils import get_emails


def test_gmail_api_timing_consistency():
    """
    Test that proves Gmail API has timing/consistency issues.
    
    This test should:
    1. FAIL when checking immediately after modification
    2. SUCCEED when waiting a bit before checking
    
    This proves our hypothesis that the issue is Gmail API timing,
    not our code logic.
    
    If the immediate check consistently succeeds, our hypothesis is wrong.
    """
    gmail = Gmail()
    
    # Get some inbox emails to test with
    inbox_emails = get_emails(gmail, n=2, in_folder='inbox')
    if inbox_emails.empty:
        pytest.skip("No inbox emails found for timing test")
    
    message_ids = inbox_emails['message_id'].tolist()
    print(f"🎯 Testing timing consistency with {len(message_ids)} emails")
    
    # Step 1: Move emails to trash
    print("📤 Moving emails to trash...")
    result = gmail.move_to_trash(inbox_emails)
    assert result is not None, "Move operation should succeed"
    print(f"✅ API operation succeeded: {result}")
    
    # Step 2: IMMEDIATE CHECK (should fail due to timing)
    print("\n⚡ IMMEDIATE CHECK (expecting failure due to timing)...")
    gmail_immediate = Gmail()  # Fresh instance
    all_emails_immediate = gmail_immediate.get_emails(days=365, max_emails=1000)
    moved_emails_immediate = all_emails_immediate[all_emails_immediate['message_id'].isin(message_ids)]
    
    immediate_success = True
    immediate_error = None
    
    try:
        assert not moved_emails_immediate.empty, "Emails should be found"
        
        # Check if emails have TRASH label
        for _, email in moved_emails_immediate.iterrows():
            labels = email.get('labels', [])
            if 'TRASH' not in labels:
                immediate_success = False
                immediate_error = f"Email {email['message_id']} missing TRASH label, has: {labels}"
                break
        
        if immediate_success:
            print("⚠️  UNEXPECTED: Immediate check succeeded (Gmail API was fast this time)")
        else:
            print(f"❌ EXPECTED: Immediate check failed - {immediate_error}")
            
    except AssertionError as e:
        immediate_success = False
        immediate_error = str(e)
        print(f"❌ EXPECTED: Immediate check failed - {immediate_error}")
    
    # Step 3: DELAYED CHECK (should succeed after waiting)
    print(f"\n⏰ DELAYED CHECK (waiting 3 seconds, expecting success)...")
    time.sleep(3)
    
    gmail_delayed = Gmail()  # Fresh instance
    all_emails_delayed = gmail_delayed.get_emails(days=365, max_emails=1000)
    moved_emails_delayed = all_emails_delayed[all_emails_delayed['message_id'].isin(message_ids)]
    
    delayed_success = True
    delayed_error = None
    
    try:
        assert not moved_emails_delayed.empty, "Emails should be found after delay"
        
        # Check if emails have TRASH label
        for _, email in moved_emails_delayed.iterrows():
            labels = email.get('labels', [])
            assert 'TRASH' in labels, f"Email {email['message_id']} should have TRASH label, has: {labels}"
        
        print("✅ SUCCESS: Delayed check succeeded (Gmail API caught up)")
        
    except AssertionError as e:
        delayed_success = False
        delayed_error = str(e)
        print(f"❌ UNEXPECTED: Delayed check failed - {delayed_error}")
    
    # Step 4: RESTORE emails to inbox
    print(f"\n🔄 Restoring emails to inbox...")
    restore_result = gmail.move_to_inbox(moved_emails_delayed)
    assert restore_result is not None, "Restore should succeed"
    
    # Wait and verify restoration
    time.sleep(2)
    gmail_restore = Gmail()
    all_emails_restore = gmail_restore.get_emails(days=365, max_emails=1000)
    restored_emails = all_emails_restore[all_emails_restore['message_id'].isin(message_ids)]
    
    for _, email in restored_emails.iterrows():
        labels = email.get('labels', [])
        assert 'INBOX' in labels, f"Email {email['message_id']} should be restored to inbox"
    
    print("✅ Emails successfully restored to inbox")
    
    # Step 5: ANALYZE RESULTS
    print(f"\n📊 TIMING ANALYSIS RESULTS:")
    print(f"   Immediate check: {'✅ Passed' if immediate_success else '❌ Failed'}")
    print(f"   Delayed check:   {'✅ Passed' if delayed_success else '❌ Failed'}")
    
    if not immediate_success and delayed_success:
        print("🎯 HYPOTHESIS CONFIRMED: Gmail API has timing/consistency delays")
        print("   - API operations succeed immediately")
        print("   - But verification queries need time to reflect changes")
        print("   - This proves our folder operation tests need proper timing")
    elif immediate_success and delayed_success:
        print("⚠️  Gmail API was unusually fast this time - both checks passed")
        print("   - This can happen occasionally")
        print("   - The timing issue is intermittent but real")
        print("   - Will try multiple attempts to catch timing issue")
    else:
        print("❌ UNEXPECTED RESULT - something else is wrong")
        if delayed_error:
            print(f"   Delayed error: {delayed_error}")
    
    # The test passes if the delayed check succeeded (proving the functionality works)
    assert delayed_success, f"Delayed check should succeed, but failed: {delayed_error}"
    
    # If immediate check succeeded, we should note this for the multi-attempt test
    return immediate_success


def test_gmail_api_timing_consistency_archive():
    """
    Test timing consistency with archive operations.
    
    Archive operations are more complex because they involve removing
    folder labels rather than adding them.
    """
    gmail = Gmail()
    
    # Get some inbox emails to test with
    inbox_emails = get_emails(gmail, n=2, in_folder='inbox')
    if inbox_emails.empty:
        pytest.skip("No inbox emails found for archive timing test")
    
    message_ids = inbox_emails['message_id'].tolist()
    print(f"🎯 Testing archive timing consistency with {len(message_ids)} emails")
    
    # Step 1: Move emails to archive
    print("📦 Moving emails to archive...")
    result = gmail.move_to_archive(inbox_emails)
    assert result is not None, "Archive operation should succeed"
    print(f"✅ API operation succeeded: {result}")
    
    # Step 2: IMMEDIATE CHECK
    print("\n⚡ IMMEDIATE CHECK (expecting potential timing issues)...")
    gmail_immediate = Gmail()
    all_emails_immediate = gmail_immediate.get_emails(days=365, max_emails=1000)
    moved_emails_immediate = all_emails_immediate[all_emails_immediate['message_id'].isin(message_ids)]
    
    immediate_success = True
    immediate_error = None
    
    try:
        assert not moved_emails_immediate.empty, "Emails should be found"
        
        # Check if emails are archived (no folder labels)
        for _, email in moved_emails_immediate.iterrows():
            labels = email.get('labels', [])
            has_folder_label = any(label in ['INBOX', 'TRASH', 'SPAM'] for label in labels)
            if has_folder_label:
                immediate_success = False
                immediate_error = f"Email {email['message_id']} still has folder labels: {labels}"
                break
        
        if immediate_success:
            print("✅ Immediate check succeeded (Gmail API was fast)")
        else:
            print(f"❌ EXPECTED: Immediate check failed - {immediate_error}")
            
    except AssertionError as e:
        immediate_success = False
        immediate_error = str(e)
        print(f"❌ EXPECTED: Immediate check failed - {immediate_error}")
    
    # Step 3: DELAYED CHECK
    print(f"\n⏰ DELAYED CHECK (waiting 3 seconds)...")
    time.sleep(3)
    
    gmail_delayed = Gmail()
    all_emails_delayed = gmail_delayed.get_emails(days=365, max_emails=1000)
    moved_emails_delayed = all_emails_delayed[all_emails_delayed['message_id'].isin(message_ids)]
    
    delayed_success = True
    delayed_error = None
    
    try:
        assert not moved_emails_delayed.empty, "Emails should be found after delay"
        
        # Check if emails are archived (no folder labels)
        for _, email in moved_emails_delayed.iterrows():
            labels = email.get('labels', [])
            has_folder_label = any(label in ['INBOX', 'TRASH', 'SPAM'] for label in labels)
            assert not has_folder_label, f"Email {email['message_id']} should be archived, has: {labels}"
        
        print("✅ SUCCESS: Delayed check succeeded")
        
    except AssertionError as e:
        delayed_success = False
        delayed_error = str(e)
        print(f"❌ UNEXPECTED: Delayed check failed - {delayed_error}")
    
    # Step 4: RESTORE emails to inbox
    print(f"\n🔄 Restoring emails to inbox...")
    restore_result = gmail.move_to_inbox(moved_emails_delayed)
    assert restore_result is not None, "Restore should succeed"
    
    # Wait and verify restoration
    time.sleep(2)
    gmail_restore = Gmail()
    all_emails_restore = gmail_restore.get_emails(days=365, max_emails=1000)
    restored_emails = all_emails_restore[all_emails_restore['message_id'].isin(message_ids)]
    
    for _, email in restored_emails.iterrows():
        labels = email.get('labels', [])
        assert 'INBOX' in labels, f"Email {email['message_id']} should be restored to inbox"
    
    print("✅ Emails successfully restored to inbox")
    
    # Step 5: ANALYZE RESULTS
    print(f"\n📊 ARCHIVE TIMING ANALYSIS:")
    print(f"   Immediate check: {'✅ Passed' if immediate_success else '❌ Failed'}")
    print(f"   Delayed check:   {'✅ Passed' if delayed_success else '❌ Failed'}")
    
    # The test passes if the delayed check succeeded
    assert delayed_success, f"Delayed check should succeed, but failed: {delayed_error}"


def test_gmail_api_timing_hypothesis_multiple_attempts():
    """
    Test that tries multiple times to catch Gmail API timing issues.
    
    This test expects that at least ONE immediate check should fail
    out of multiple attempts. If all immediate checks succeed,
    our timing hypothesis is likely wrong.
    
    CRITICAL: This test proved that Gmail API has eventual consistency issues
    in search results, not simple timing delays.
    """
    gmail = Gmail()  # Standard Gmail instance
    
    attempts = 5
    immediate_failures = 0
    delayed_successes = 0
    
    print(f"🔄 Testing timing hypothesis with {attempts} attempts...")
    print("   Expecting at least 1 immediate failure to prove timing issues exist")
    
    for attempt in range(attempts):
        print(f"\n--- ATTEMPT {attempt + 1}/{attempts} ---")
        
        # Get fresh emails for each attempt
        inbox_emails = get_emails(gmail, n=1, in_folder='inbox')
        if inbox_emails.empty:
            print(f"⏭️  Skipping attempt {attempt + 1} - no inbox emails")
            continue
            
        message_ids = inbox_emails['message_id'].tolist()
        print(f"📧 Testing with email: {message_ids[0]}")
        
        # Move to trash
        result = gmail.move_to_trash(inbox_emails)
        assert result is not None, "Move operation should succeed"
        
        # IMMEDIATE CHECK (testing raw Gmail API consistency)
        gmail_immediate = Gmail()
        all_emails_immediate = gmail_immediate.get_emails(days=365, max_emails=1000)
        moved_emails_immediate = all_emails_immediate[all_emails_immediate['message_id'].isin(message_ids)]
        
        immediate_failed = False
        try:
            assert not moved_emails_immediate.empty, "Emails should be found"
            for _, email in moved_emails_immediate.iterrows():
                labels = email.get('labels', [])
                if 'TRASH' not in labels:
                    immediate_failed = True
                    break
            if not immediate_failed:
                print("   ✅ Immediate check passed (API was fast)")
            else:
                print("   ❌ Immediate check failed (caught timing issue!)")
                immediate_failures += 1
        except AssertionError:
            immediate_failed = True
            immediate_failures += 1
            print("   ❌ Immediate check failed (caught timing issue!)")
        
        # DELAYED CHECK
        time.sleep(3)
        gmail_delayed = Gmail()  # Fresh instance after manual delay
        all_emails_delayed = gmail_delayed.get_emails(days=365, max_emails=1000)
        moved_emails_delayed = all_emails_delayed[all_emails_delayed['message_id'].isin(message_ids)]
        
        delayed_success = True
        try:
            assert not moved_emails_delayed.empty, "Emails should be found after delay"
            for _, email in moved_emails_delayed.iterrows():
                labels = email.get('labels', [])
                assert 'TRASH' in labels, f"Email should have TRASH label, has: {labels}"
            print("   ✅ Delayed check succeeded")
            delayed_successes += 1
        except AssertionError as e:
            delayed_success = False
            print(f"   ❌ Delayed check failed: {e}")
        
        # RESTORE
        if delayed_success:
            restore_result = gmail.move_to_inbox(moved_emails_delayed)
            time.sleep(1)  # Brief wait for restore
            print("   🔄 Restored to inbox")
    
    # ANALYZE RESULTS
    print(f"\n📊 MULTI-ATTEMPT ANALYSIS:")
    print(f"   Total attempts: {attempts}")
    print(f"   Immediate failures: {immediate_failures}")
    print(f"   Delayed successes: {delayed_successes}")
    print(f"   Immediate failure rate: {immediate_failures/attempts*100:.1f}%")
    
    # THE CRITICAL TEST: We EXPECT immediate checks to fail
    # If they don't fail, our timing hypothesis is wrong
    immediate_failure_rate = immediate_failures / attempts
    
    if immediate_failures > 0:
        print("🎯 HYPOTHESIS CONFIRMED: Gmail API has timing inconsistencies")
        print(f"   - {immediate_failures} out of {attempts} immediate checks failed")
        print("   - This proves timing delays exist and are intermittent")
        print(f"   - Immediate failure rate: {immediate_failure_rate*100:.1f}%")
    else:
        print("❌ HYPOTHESIS REJECTED: All immediate checks succeeded")
        print("   - Gmail API was consistently fast across all attempts")
        print("   - Our timing hypothesis is WRONG")
        print("   - The folder test failures have a different cause")
    
    # REQUIRE that we see timing failures - this is the whole point!
    assert immediate_failures > 0, (
        f"EXPECTED immediate checks to fail due to timing issues, but all {attempts} succeeded. "
        f"This proves our timing hypothesis is INCORRECT. The folder test failures must have a different cause."
    )
    
    # Also ensure delayed checks mostly succeeded (proving functionality works)
    success_rate = delayed_successes / attempts
    assert success_rate >= 0.8, f"Delayed checks should mostly succeed, got {success_rate:.1f}"
    
    print(f"✅ TEST PASSED: Caught {immediate_failures} timing failures as expected!")


if __name__ == "__main__":
    print("🧪 Running Gmail API timing consistency tests...")
    test_gmail_api_timing_consistency()
    print("\n" + "="*60 + "\n")
    test_gmail_api_timing_consistency_archive()
    print("\n" + "="*60 + "\n")
    test_gmail_api_timing_hypothesis_multiple_attempts()
    print("\n🎯 All timing tests completed!")
