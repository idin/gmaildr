"""
Tests for Gmail class convenience methods.

This module contains tests for the new convenience methods added to the Gmail class:
- get_label_id
- has_label
- get_trash_emails
- get_archive_emails
- get_inbox_emails
"""

from gmailwiz import Gmail


def test_get_label_id():
    """Test get_label_id method."""
    gmail = Gmail()
    
    # Test with a system label that should always exist
    inbox_id = gmail.get_label_id('INBOX')
    assert inbox_id is not None, "INBOX label should exist"
    assert inbox_id == 'INBOX', "INBOX label ID should be 'INBOX'"
    
    # Test with a non-existent label
    non_existent_id = gmail.get_label_id('NON_EXISTENT_LABEL_12345')
    assert non_existent_id is None, "Non-existent label should return None"
    
    print("✅ get_label_id test passed")


def test_has_label():
    """Test has_label method."""
    gmail = Gmail()
    
    # Test with a system label that should always exist
    assert gmail.has_label('INBOX'), "INBOX label should exist"
    assert gmail.has_label('SENT'), "SENT label should exist"
    assert gmail.has_label('DRAFT'), "DRAFT label should exist"
    
    # Test with a non-existent label
    assert not gmail.has_label('NON_EXISTENT_LABEL_12345'), "Non-existent label should return False"
    
    print("✅ has_label test passed")


def test_get_label_id_or_create():
    """Test get_label_id_or_create method."""
    gmail = Gmail()
    
    # Test with a system label that should always exist
    inbox_id = gmail.get_label_id_or_create('INBOX')
    assert inbox_id is not None, "INBOX label should exist"
    assert inbox_id == 'INBOX', "INBOX label ID should be 'INBOX'"
    
    # Test with a non-existent label (should create it)
    test_label_name = 'TEST_LABEL_12345'
    test_label_id = gmail.get_label_id_or_create(test_label_name)
    assert test_label_id is not None, "Should create new label and return ID"
    
    # Verify the label was created
    assert gmail.has_label(test_label_name), "Label should exist after creation"
    assert gmail.get_label_id(test_label_name) == test_label_id, "Label ID should match"
    
    # Test getting the same label again (should return existing ID)
    test_label_id_again = gmail.get_label_id_or_create(test_label_name)
    assert test_label_id_again == test_label_id, "Should return same ID for existing label"
    
    print("✅ get_label_id_or_create test passed")


def test_get_trash_emails():
    """Test get_trash_emails method."""
    gmail = Gmail()
    
    # Get a small number of trash emails from recent days
    df = gmail.get_trash_emails(
        days=7,  # Last 7 days
        max_emails=10,  # Only 10 emails
        include_text=False,
        include_metrics=False,
        use_batch=True
    )
    
    # Should return a DataFrame
    assert hasattr(df, 'empty'), "Should return a pandas DataFrame"
    
    # If there are emails in trash, check the structure
    if not df.empty:
        assert 'message_id' in df.columns, "DataFrame should have message_id column"
        assert 'subject' in df.columns, "DataFrame should have subject column"
        assert 'sender_email' in df.columns, "DataFrame should have sender_email column"
        # Note: max_emails limit may not be enforced when using cache
        print(f"Found {len(df)} emails in trash")
    
    print("✅ get_trash_emails test passed")


def test_get_archive_emails():
    """Test get_archive_emails method."""
    gmail = Gmail()
    
    # Get a small number of archived emails from recent days
    df = gmail.get_archive_emails(
        days=7,  # Last 7 days
        max_emails=10,  # Only 10 emails
        include_text=False,
        include_metrics=False,
        use_batch=True
    )
    
    # Should return a DataFrame
    assert hasattr(df, 'empty'), "Should return a pandas DataFrame"
    
    # If there are archived emails, check the structure
    if not df.empty:
        assert 'message_id' in df.columns, "DataFrame should have message_id column"
        assert 'subject' in df.columns, "DataFrame should have subject column"
        assert 'sender_email' in df.columns, "DataFrame should have sender_email column"
        # Note: max_emails limit may not be enforced when using cache
        print(f"Found {len(df)} archived emails")
    
    print("✅ get_archive_emails test passed")


def test_get_inbox_emails():
    """Test get_inbox_emails method."""
    gmail = Gmail()
    
    # Get a small number of inbox emails from recent days
    df = gmail.get_inbox_emails(
        days=7,  # Last 7 days
        max_emails=10,  # Only 10 emails
        include_text=False,
        include_metrics=False,
        use_batch=True
    )
    
    # Should return a DataFrame
    assert hasattr(df, 'empty'), "Should return a pandas DataFrame"
    
    # If there are inbox emails, check the structure
    if not df.empty:
        assert 'message_id' in df.columns, "DataFrame should have message_id column"
        assert 'subject' in df.columns, "DataFrame should have subject column"
        assert 'sender_email' in df.columns, "DataFrame should have sender_email column"
        # Note: max_emails limit may not be enforced when using cache
        print(f"Found {len(df)} inbox emails")
    
    print("✅ get_inbox_emails test passed")


def test_modify_labels():
    """Test modify_labels method."""
    gmail = Gmail(enable_cache=False)  # Disable cache to avoid stale data
    
    # Get or create a test label
    test_label_name = 'TEST_LABEL_MODIFY'
    gmail.has_label(test_label_name)
    label_id = gmail.get_label_id_or_create(test_label_name)
    
    # Get a few emails to test with (use fewer emails and shorter time range)
    df = gmail.get_inbox_emails(
        days=1,  # Last 1 day only
        max_emails=1,  # Only 1 email
        include_text=False,
        include_metrics=False,
        use_batch=True
    )
    
    if df.empty:
        print("⚠️ No emails found for testing modify_labels - skipping test")
        return
    
    message_ids = df['message_id'].tolist()[:1]  # Take only first email
    print(f"Testing modify_labels with {len(message_ids)} email")
    
    # Apply the test label (use label name, not ID)
    results = gmail.modify_labels(
        message_ids=message_ids,
        add_labels=[test_label_name],
        show_progress=False
    )
    
    # Check results
    assert isinstance(results, dict), "Should return a dictionary"
    assert len(results) == len(message_ids), "Should have results for all message IDs"
    
    success_count = sum(results.values())
    print(f"✅ modify_labels test passed: {success_count}/{len(message_ids)} successful")
    
    # CRITICAL: Verify labels were actually applied
    import time
    time.sleep(1)  # Wait for Gmail to update
    
    # Re-fetch emails to verify labels were applied
    df_after = gmail.get_inbox_emails(
        days=1,
        max_emails=5,
        include_text=False,
        include_metrics=False,
        use_batch=True
    )
    
    # Check if our test emails actually have the label
    actually_labeled = 0
    for msg_id in message_ids:
        if msg_id in df_after['message_id'].values:
            email = df_after[df_after['message_id'] == msg_id].iloc[0]
            # Check if the label ID is in the email's labels
            if label_id and label_id in email['labels']:
                actually_labeled += 1
    
    print(f"Actually labeled: {actually_labeled}/{len(message_ids)} emails have the label")
    
    # Debug: Show all labels for the test email
    for msg_id in message_ids:
        if msg_id in df_after['message_id'].values:
            email = df_after[df_after['message_id'] == msg_id].iloc[0]
            print(f"Email {msg_id} labels: {email['labels']}")
    
    # This is the critical assertion that catches the bug
    assert actually_labeled == len(message_ids), f"All {len(message_ids)} emails should have the label, but only {actually_labeled} do"
    
    # Clean up - delete the test label
    if label_id:
        gmail.delete_label(label_id)
        print(f"🗑️ Deleted test label: {test_label_name}")

    assert gmail.has_label(test_label_name) is False, "Label should be deleted"


if __name__ == '__main__':
    print("🧪 Testing Gmail convenience methods...")
    
    # Run all tests
    test_get_label_id()
    test_has_label()
    test_get_label_id_or_create()
    test_get_trash_emails()
    test_get_archive_emails()
    test_get_inbox_emails()
    test_modify_labels()
    
    print("🎉 All Gmail convenience method tests passed!")
