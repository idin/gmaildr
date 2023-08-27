"""
Test remove_label functionality.

This test verifies that labels can be removed from emails correctly.
"""

from gmaildr import Gmail
from gmaildr.test_utils import get_emails
import pytest


def test_remove_label_from_single_email():
    """Test removing a label from a single email."""
    gmail = Gmail()
    
    # Get emails using the helper function
    emails = get_emails(gmail, 1)
    
    if len(emails) == 0:
        pytest.skip("No emails available to test with")
    
    # Get the first email
    email = emails.iloc[0]
    message_id = email['message_id']
    
    # Add a test label first
    test_label = "TEST_LABEL_REMOVE"
    gmail.add_label(message_id, test_label)
    
    # Remove the test label
    result = gmail.remove_label(message_id, test_label)
    
    # Verify the label was removed
    assert result is True or (isinstance(result, dict) and result.get(message_id, False))
    
    # Verify the email no longer has the label - REMOVED days parameter as it's not necessary for verification
    updated_emails = get_emails(gmail, 10)
    updated_email = updated_emails[updated_emails['message_id'] == message_id]
    
    if len(updated_email) > 0:
        labels = updated_email.iloc[0]['labels']
        assert test_label not in labels


def test_remove_label_from_multiple_emails():
    """Test removing a label from multiple emails."""
    gmail = Gmail()
    
    # Get emails using the helper function
    emails = get_emails(gmail, 2)
    
    if len(emails) < 2:
        pytest.skip("Not enough emails available to test with")
    
    # Get the first two emails
    message_ids = emails.head(2)['message_id'].tolist()
    
    # Add a test label first
    test_label = "TEST_LABEL_REMOVE_MULTIPLE"
    gmail.add_label(message_ids, test_label)
    
    # Remove the test label
    result = gmail.remove_label(message_ids, test_label)
    
    # Verify the labels were removed
    if isinstance(result, dict):
        for message_id in message_ids:
            assert result.get(message_id, False)
    else:
        assert result is True
    
    # Verify the emails no longer have the label - REMOVED days parameter as it's not necessary for verification
    updated_emails = get_emails(gmail, 10)
    
    for message_id in message_ids:
        updated_email = updated_emails[updated_emails['message_id'] == message_id]
        if len(updated_email) > 0:
            labels = updated_email.iloc[0]['labels']
            assert test_label not in labels


def test_remove_multiple_labels():
    """Test removing multiple labels from an email."""
    gmail = Gmail()
    
    # Get emails using the helper function
    emails = get_emails(gmail, 1)
    
    if len(emails) == 0:
        pytest.skip("No emails available to test with")
    
    # Get the first email
    email = emails.iloc[0]
    message_id = email['message_id']
    
    # Add multiple test labels first
    test_labels = ["TEST_LABEL_REMOVE_1", "TEST_LABEL_REMOVE_2", "TEST_LABEL_REMOVE_3"]
    gmail.add_label(message_id, test_labels)
    
    # Remove the test labels
    result = gmail.remove_label(message_id, test_labels)
    
    # Verify the labels were removed
    assert result is True or (isinstance(result, dict) and result.get(message_id, False))
    
    # Verify the email no longer has any of the labels - REMOVED days parameter as it's not necessary for verification
    updated_emails = get_emails(gmail, 10)
    updated_email = updated_emails[updated_emails['message_id'] == message_id]
    
    if len(updated_email) > 0:
        labels = updated_email.iloc[0]['labels']
        for test_label in test_labels:
            assert test_label not in labels


def test_remove_label_with_progress():
    """Test removing a label with progress bar."""
    gmail = Gmail()
    
    # Get emails using the helper function
    emails = get_emails(gmail, 1)
    
    if len(emails) == 0:
        pytest.skip("No emails available to test with")
    
    # Get the first email
    email = emails.iloc[0]
    message_id = email['message_id']
    
    # Add a test label first
    test_label = "TEST_LABEL_REMOVE_PROGRESS"
    gmail.add_label(message_id, test_label)
    
    # Remove the test label with progress
    result = gmail.remove_label(message_id, test_label, show_progress=True)
    
    # Verify the label was removed
    assert result is True or (isinstance(result, dict) and result.get(message_id, False))
    
    # Verify the email no longer has the label - REMOVED days parameter as it's not necessary for verification
    updated_emails = get_emails(gmail, 10)
    updated_email = updated_emails[updated_emails['message_id'] == message_id]
    
    if len(updated_email) > 0:
        labels = updated_email.iloc[0]['labels']
        assert test_label not in labels


def test_remove_label_verification():
    """Test that remove_label properly verifies the operation."""
    gmail = Gmail()
    
    # Get emails using the helper function
    emails = get_emails(gmail, 2)
    
    if len(emails) < 2:
        pytest.skip("Not enough emails available to test with")
    
    # Get the first two emails
    message_ids = emails.head(2)['message_id'].tolist()
    
    # Add a test label first
    test_label = "TEST_LABEL_REMOVE_VERIFY"
    gmail.add_label(message_ids, test_label)
    
    # Remove the test label
    result = gmail.remove_label(message_ids, test_label)
    
    # Verify the labels were removed
    if isinstance(result, dict):
        for message_id in message_ids:
            assert result.get(message_id, False)
    else:
        assert result is True
    
    # Verify the emails no longer have the label - REMOVED days parameter as it's not necessary for verification
    updated_emails = get_emails(gmail, 10)
    
    for message_id in message_ids:
        updated_email = updated_emails[updated_emails['message_id'] == message_id]
        if len(updated_email) > 0:
            labels = updated_email.iloc[0]['labels']
            assert test_label not in labels
    
    # Verify with a larger sample to ensure consistency - REMOVED days parameter as it's not necessary for verification
    larger_sample = get_emails(gmail, 50)
    for message_id in message_ids:
        if message_id in larger_sample['message_id'].values:
            email_data = larger_sample[larger_sample['message_id'] == message_id].iloc[0]
            assert test_label not in email_data['labels']


def test_remove_label_multiple_emails_verification():
    """Test removing labels from multiple emails with verification."""
    gmail = Gmail()
    
    # Get emails using the helper function
    emails = get_emails(gmail, 2)
    
    if len(emails) < 2:
        pytest.skip("Not enough emails available to test with")
    
    # Get the first two emails
    message_ids = emails.head(2)['message_id'].tolist()
    
    # Add a test label first
    test_label = "TEST_LABEL_REMOVE_MULTI_VERIFY"
    gmail.add_label(message_ids, test_label)
    
    # Remove the test label
    result = gmail.remove_label(message_ids, test_label)
    
    # Verify the labels were removed
    if isinstance(result, dict):
        for message_id in message_ids:
            assert result.get(message_id, False)
    else:
        assert result is True
    
    # Verify the emails no longer have the label - REMOVED days parameter as it's not necessary for verification
    updated_emails = get_emails(gmail, 10)
    
    for message_id in message_ids:
        updated_email = updated_emails[updated_emails['message_id'] == message_id]
        if len(updated_email) > 0:
            labels = updated_email.iloc[0]['labels']
            assert test_label not in labels
