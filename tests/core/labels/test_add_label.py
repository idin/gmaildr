"""
Tests for add_label functionality.
"""

import pytest

from gmailwiz.core.gmail import Gmail


def test_add_label_single_string():
    """Test add_label with single string label."""
    gmail = Gmail()
    
    # Get a real email first
    emails = gmail.get_emails(days=1, max_emails=1)
    if emails.is_empty():
        pytest.skip("No emails available for testing")
    
    message_id = emails.iloc[0]['message_id']
    original_labels = emails.iloc[0]['labels'] if 'labels' in emails.columns else []
    
    # Add a test label
    result = gmail.add_label(message_id, 'test_label')
    assert result is True or isinstance(result, dict)
    
    # Verify the label was actually added
    updated_emails = gmail.get_emails(days=1, max_emails=1)
    updated_email = updated_emails[updated_emails['message_id'] == message_id]
    if not updated_email.is_empty():
        new_labels = updated_email.iloc[0]['labels'] if 'labels' in updated_email.columns else []
        # Labels are now stored as lists
        assert isinstance(new_labels, list)
        assert 'test_label' in new_labels


def test_add_label_list_of_labels():
    """Test add_label with list of labels."""
    gmail = Gmail()
    
    # Get a real email first
    emails = gmail.get_emails(days=1, max_emails=1)
    if emails.is_empty():
        pytest.skip("No emails available for testing")
    
    message_id = emails.iloc[0]['message_id']
    
    # Add test labels
    result = gmail.add_label(message_id, ['test_label1', 'test_label2'])
    assert result is True or isinstance(result, dict)
    
    # Verify the labels were actually added
    updated_emails = gmail.get_emails(days=1, max_emails=1)
    updated_email = updated_emails[updated_emails['message_id'] == message_id]
    if not updated_email.is_empty():
        new_labels = updated_email.iloc[0]['labels'] if 'labels' in updated_email.columns else []
        # Labels are now stored as lists
        assert isinstance(new_labels, list)
        assert 'test_label1' in new_labels or 'test_label2' in new_labels


def test_add_label_multiple_message_ids():
    """Test add_label with multiple message IDs."""
    gmail = Gmail()
    
    # Get real emails first
    emails = gmail.get_emails(days=1, max_emails=2)
    if len(emails) < 2:
        pytest.skip("Not enough emails available for testing")
    
    message_ids = emails['message_id'].tolist()[:2]
    
    # Add test label to multiple emails
    result = gmail.add_label(message_ids, 'test_label_multi')
    assert result is True or isinstance(result, dict)
    
    # Verify the label was actually added to at least one email
    updated_emails = gmail.get_emails(days=1, max_emails=10)
    updated_emails_filtered = updated_emails[updated_emails['message_id'].isin(message_ids)]
    if not updated_emails_filtered.is_empty():
        # Check all labels from all emails
        all_labels = []
        for labels in updated_emails_filtered['labels']:
            if isinstance(labels, list):
                all_labels.extend(labels)
        assert 'test_label_multi' in all_labels