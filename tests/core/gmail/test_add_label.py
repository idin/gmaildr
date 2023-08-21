"""
Test add_label functionality.

This test verifies that labels can be added to emails correctly.
"""

from gmaildr import Gmail
from tests.core.gmail.test_get_emails import get_emails
import pytest


def test_add_label_to_single_email():
    """Test adding a label to a single email."""
    gmail = Gmail()
    
    # Get emails using the helper function
    emails = get_emails(gmail, 1)
    
    if len(emails) == 0:
        pytest.skip("No emails available to test with")
    
    # Get the first email
    email = emails.iloc[0]
    message_id = email['message_id']
    
    # Add a test label
    test_label = "TEST_LABEL_ADD"
    result = gmail.add_label(message_id, test_label)
    
    # Verify the label was added
    assert result is True or (isinstance(result, dict) and result.get(message_id, False))
    
    # Get the label ID for verification
    label_id = gmail.get_label_id(test_label)
    assert label_id is not None, f"Label {test_label} should exist after creation"
    
    # Verify the email now has the label ID
    updated_emails = get_emails(gmail, 50)
    updated_email = updated_emails[updated_emails['message_id'] == message_id]
    
    if len(updated_email) > 0:
        labels = updated_email.iloc[0]['labels']
        assert label_id in labels, f"Label ID {label_id} should be in labels: {labels}"


def test_add_label_to_multiple_emails():
    """Test adding a label to multiple emails."""
    gmail = Gmail()
    
    # Get emails using the helper function
    emails = get_emails(gmail, 2)
    
    if len(emails) < 2:
        pytest.skip("Not enough emails available to test with")
    
    # Get the first two emails
    message_ids = emails.head(2)['message_id'].tolist()
    
    # Add a test label
    test_label = "TEST_LABEL_ADD_MULTIPLE"
    result = gmail.add_label(message_ids, test_label)
    
    # Verify the labels were added
    if isinstance(result, dict):
        for message_id in message_ids:
            assert result.get(message_id, False)
    else:
        assert result is True
    
    # Get the label ID for verification
    label_id = gmail.get_label_id(test_label)
    assert label_id is not None, f"Label {test_label} should exist after creation"
    
    # Verify the emails now have the label ID
    updated_emails = get_emails(gmail, 50)
    
    for message_id in message_ids:
        updated_email = updated_emails[updated_emails['message_id'] == message_id]
        if len(updated_email) > 0:
            labels = updated_email.iloc[0]['labels']
            assert label_id in labels, f"Label ID {label_id} should be in labels: {labels}"


def test_add_multiple_labels():
    """Test adding multiple labels to an email."""
    gmail = Gmail()
    
    # Get emails using the helper function
    emails = get_emails(gmail, 1)
    
    if len(emails) == 0:
        pytest.skip("No emails available to test with")
    
    # Get the first email
    email = emails.iloc[0]
    message_id = email['message_id']
    
    # Add multiple test labels
    test_labels = ["TEST_LABEL_1", "TEST_LABEL_2", "TEST_LABEL_3"]
    result = gmail.add_label(message_id, test_labels)
    
    # Verify the labels were added
    assert result is True or (isinstance(result, dict) and result.get(message_id, False))
    
    # Get the label IDs for verification
    label_ids = []
    for test_label in test_labels:
        label_id = gmail.get_label_id(test_label)
        assert label_id is not None, f"Label {test_label} should exist after creation"
        label_ids.append(label_id)
    
    # Verify the email now has all the label IDs
    updated_emails = get_emails(gmail, 50)
    updated_email = updated_emails[updated_emails['message_id'] == message_id]
    
    if len(updated_email) > 0:
        labels = updated_email.iloc[0]['labels']
        for label_id in label_ids:
            assert label_id in labels, f"Label ID {label_id} should be in labels: {labels}"


def test_add_label_with_progress():
    """Test adding a label with progress bar."""
    gmail = Gmail()
    
    # Get emails using the helper function
    emails = get_emails(gmail, 1)
    
    if len(emails) == 0:
        pytest.skip("No emails available to test with")
    
    # Get the first email
    email = emails.iloc[0]
    message_id = email['message_id']
    
    # Add a test label with progress
    test_label = "TEST_LABEL_PROGRESS"
    result = gmail.add_label(message_id, test_label, show_progress=True)
    
    # Verify the label was added
    assert result is True or (isinstance(result, dict) and result.get(message_id, False))
    
    # Get the label ID for verification
    label_id = gmail.get_label_id(test_label)
    assert label_id is not None, f"Label {test_label} should exist after creation"
    
    # Verify the email now has the label ID
    updated_emails = get_emails(gmail, 50)
    updated_email = updated_emails[updated_emails['message_id'] == message_id]
    
    if len(updated_email) > 0:
        labels = updated_email.iloc[0]['labels']
        assert label_id in labels, f"Label ID {label_id} should be in labels: {labels}"


def test_add_label_verification():
    """Test that add_label properly verifies the operation."""
    gmail = Gmail()
    
    # Get emails using the helper function
    emails = get_emails(gmail, 2)
    
    if len(emails) < 2:
        pytest.skip("Not enough emails available to test with")
    
    # Get the first two emails
    message_ids = emails.head(2)['message_id'].tolist()
    
    # Add a test label
    test_label = "TEST_LABEL_VERIFY"
    result = gmail.add_label(message_ids, test_label)
    
    # Verify the labels were added
    if isinstance(result, dict):
        for message_id in message_ids:
            assert result.get(message_id, False)
    else:
        assert result is True
    
    # Get the label ID for verification
    label_id = gmail.get_label_id(test_label)
    assert label_id is not None, f"Label {test_label} should exist after creation"
    
    # Verify the emails now have the label ID
    updated_emails = get_emails(gmail, 50)
    
    for message_id in message_ids:
        updated_email = updated_emails[updated_emails['message_id'] == message_id]
        if len(updated_email) > 0:
            labels = updated_email.iloc[0]['labels']
            assert label_id in labels, f"Label ID {label_id} should be in labels: {labels}"
    
    # Verify with a larger sample to ensure consistency
    larger_sample = get_emails(gmail, 100)
    for message_id in message_ids:
        if message_id in larger_sample['message_id'].values:
            email_data = larger_sample[larger_sample['message_id'] == message_id].iloc[0]
            assert label_id in email_data['labels'], f"Label ID {label_id} should be in labels: {email_data['labels']}"