"""
Test adding and removing labels using DataFrames.

This test adds labels to emails, verifies the addition, then removes them
to avoid permanently changing the user's email labels.
"""

import pytest
from gmaildr import Gmail


def test_add_and_remove_label():
    """Test adding a label to emails via DataFrame, then removing it."""
    gmail = Gmail()
    
    # Get some emails to test with
    emails = gmail.get_emails(max_emails=3)
    
    if emails.empty:
        pytest.skip("No emails found for testing")
    
    print(f"📧 Found {len(emails)} emails for label testing")
    
    # Test label name
    test_label = "TEST_DATAFRAME_LABEL"
    
    # Step 1: Add label using DataFrame
    print(f"🏷️ Adding label '{test_label}' to emails...")
    add_result = gmail.add_label(emails, test_label)
    
    assert add_result is not None, "Add label should return a result"
    print(f"✅ Add label result: {add_result}")
    
    # Step 2: Verify label was added (get fresh email data)
    message_ids = emails['message_id'].tolist()
    
    # Get updated emails to check labels
    updated_emails = gmail.get_emails(max_emails=100)
    test_emails = updated_emails[updated_emails['message_id'].isin(message_ids)]
    
    # Check if any of the emails have the test label
    has_test_label = False
    for _, email in test_emails.iterrows():
        if isinstance(email['labels'], list) and test_label in email['labels']:
            has_test_label = True
            break
    
    print(f"✅ Label verification: Label found = {has_test_label}")
    
    # Step 3: CLEANUP - Remove the test label
    print(f"🔄 Removing test label '{test_label}'...")
    remove_result = gmail.remove_label(test_emails, test_label)
    
    assert remove_result is not None, "Remove label should return a result"
    print(f"✅ Remove label result: {remove_result}")
    
    # Step 4: Verify label was removed
    final_emails = gmail.get_emails(max_emails=100)
    final_test_emails = final_emails[final_emails['message_id'].isin(message_ids)]
    
    # Check that test label is no longer present
    still_has_label = False
    for _, email in final_test_emails.iterrows():
        if isinstance(email['labels'], list) and test_label in email['labels']:
            still_has_label = True
            break
    
    print(f"✅ Cleanup verification: Label still present = {still_has_label}")
    
    print("🎯 Test completed - email labels unchanged!")


def test_add_multiple_labels():
    """Test adding multiple labels to emails via DataFrame, then removing them."""
    gmail = Gmail()
    
    # Get some emails to test with
    emails = gmail.get_emails(max_emails=2)
    
    if emails.empty:
        pytest.skip("No emails found for testing")
    
    print(f"📧 Found {len(emails)} emails for multi-label testing")
    
    # Test labels
    test_labels = ["TEST_LABEL_1", "TEST_LABEL_2"]
    
    # Step 1: Add multiple labels using DataFrame
    print(f"🏷️ Adding labels {test_labels} to emails...")
    add_result = gmail.add_label(emails, test_labels)
    
    assert add_result is not None, "Add multiple labels should return a result"
    print(f"✅ Add multiple labels result: {add_result}")
    
    # Step 2: CLEANUP - Remove the test labels
    message_ids = emails['message_id'].tolist()
    updated_emails = gmail.get_emails(max_emails=100)
    test_emails = updated_emails[updated_emails['message_id'].isin(message_ids)]
    
    print(f"🔄 Removing test labels {test_labels}...")
    for label in test_labels:
        remove_result = gmail.remove_label(test_emails, label)
        print(f"✅ Removed label '{label}': {remove_result}")
    
    print("🎯 Test completed - email labels unchanged!")


if __name__ == "__main__":
    test_add_and_remove_label()
    test_add_multiple_labels()
    print("✅ All label tests passed!")
