"""
Tests for remove_label functionality.
"""

import pytest

from gmailwiz.core.gmail import Gmail


def test_remove_label_single_string():
    """Test remove_label with single string label."""
    gmail = Gmail()
    
    # Get a real email first
    emails = gmail.get_emails(days=1, max_emails=1)
    if emails.is_empty():
        pytest.skip("No emails available for testing")
    
    message_id = emails.iloc[0]['message_id']
    original_labels = emails.iloc[0]['labels'] if 'labels' in emails.columns else []
    
    # Add a test label first so we can remove it
    gmail.add_label(message_id, 'test_label_to_remove')
    
    # Remove the test label
    result = gmail.remove_label(message_id, 'test_label_to_remove')
    assert result is True or isinstance(result, dict)
    
    # Verify the label was actually removed
    updated_emails = gmail.get_emails(days=1, max_emails=1)
    updated_email = updated_emails[updated_emails['message_id'] == message_id]
    if not updated_email.is_empty():
        new_labels = updated_email.iloc[0]['labels'] if 'labels' in updated_email.columns else []
        # Labels are now stored as lists
        assert isinstance(new_labels, list)
        assert 'test_label_to_remove' not in new_labels


def test_remove_label_list_of_labels():
    """Test remove_label with list of labels."""
    gmail = Gmail()
    
    # Get a real email first
    emails = gmail.get_emails(days=1, max_emails=1)
    if emails.is_empty():
        pytest.skip("No emails available for testing")
    
    message_id = emails.iloc[0]['message_id']
    
    # Add test labels first so we can remove them
    gmail.add_label(message_id, ['test_label1_to_remove', 'test_label2_to_remove'])
    
    # Remove the test labels
    result = gmail.remove_label(message_id, ['test_label1_to_remove', 'test_label2_to_remove'])
    assert result is True or isinstance(result, dict)
    
    # Verify the labels were actually removed
    updated_emails = gmail.get_emails(days=1, max_emails=1)
    updated_email = updated_emails[updated_emails['message_id'] == message_id]
    if not updated_email.is_empty():
        new_labels = updated_email.iloc[0]['labels'] if 'labels' in updated_email.columns else []
        # Labels are now stored as lists
        assert isinstance(new_labels, list)
        assert 'test_label1_to_remove' not in new_labels
        assert 'test_label2_to_remove' not in new_labels


def test_remove_label_multiple_message_ids():
    """Test remove_label with multiple message IDs."""
    gmail = Gmail()
    
    # Get real emails first
    emails = gmail.get_emails(days=1, max_emails=2)
    if len(emails) < 2:
        pytest.skip("Not enough emails available for testing")
    
    message_ids = emails['message_id'].tolist()[:2]
    
    # Add test label to multiple emails first so we can remove it
    gmail.add_label(message_ids, 'test_label_multi_to_remove')
    
    # Remove test label from multiple emails
    result = gmail.remove_label(message_ids, 'test_label_multi_to_remove')
    assert result is True or isinstance(result, dict)
    
    # Verify the label was actually removed from at least one email
    updated_emails = gmail.get_emails(days=1, max_emails=10)
    updated_emails_filtered = updated_emails[updated_emails['message_id'].isin(message_ids)]
    if not updated_emails_filtered.is_empty():
        # Check all labels from all emails
        all_labels = []
        for labels in updated_emails_filtered['labels']:
            if isinstance(labels, list):
                all_labels.extend(labels)
        assert 'test_label_multi_to_remove' not in all_labels
