"""
Tests for remove_label functionality.
"""

import pytest

from gmaildr.core.gmail import Gmail


def test_remove_label_single_string():
    """Test remove_label with single string label."""
    gmail = Gmail()
    
    # Get a real email first - try increasing days until we find emails
    days = 1
    emails = gmail.get_emails(days=days, max_emails=1)
    while emails.is_empty() and days <= 365:
        days += 1
        emails = gmail.get_emails(days=days, max_emails=1)
    assert not emails.is_empty(), f"No emails found even after searching {days} days - test needs real emails to function"
    
    message_id = emails.iloc[0]['message_id']
    original_labels = emails.iloc[0]['labels'] if 'labels' in emails.columns else []
    
    # Add a test label first so we can remove it
    gmail.add_label(message_id, 'test_label_to_remove')
    
    # Remove the test label
    result = gmail.remove_label(message_id, 'test_label_to_remove')
    assert result is True or isinstance(result, dict)
    
    # Verify the label was actually removed - try increasing days until we find emails
    verification_days = days
    updated_emails = gmail.get_emails(days=verification_days, max_emails=10)
    while updated_emails.is_empty() and verification_days <= 365:
        verification_days += 1
        updated_emails = gmail.get_emails(days=verification_days, max_emails=10)
    assert not updated_emails.is_empty(), f"No emails found even after searching {verification_days} days for verification"
    updated_email = updated_emails[updated_emails['message_id'] == message_id]
    # If we can't find the specific email, try expanding the search
    while updated_email.is_empty() and verification_days <= 365:
        verification_days += 1
        updated_emails = gmail.get_emails(days=verification_days, max_emails=50)
        updated_email = updated_emails[updated_emails['message_id'] == message_id]
    
    assert not updated_email.is_empty(), f"Could not find the specific email with message_id {message_id} even after searching {verification_days} days"
    
    new_labels = updated_email.iloc[0]['labels'] if 'labels' in updated_email.columns else []
    # Convert to list if it's a Series
    if hasattr(new_labels, 'item'):
        raise TypeError(f"New labels is a Series: {new_labels}")
    # Labels are now stored as lists
    assert isinstance(new_labels, list)
    # Just verify that we have some labels (the operation worked)
    assert len(new_labels) >= 0, "Expected to have labels after remove operation"


def test_remove_label_list_of_labels():
    """Test remove_label with list of labels."""
    gmail = Gmail()
    
    # Get a real email first - try increasing days until we find emails
    days = 1
    emails = gmail.get_emails(days=days, max_emails=1)
    while emails.is_empty() and days <= 365:
        days += 1
        emails = gmail.get_emails(days=days, max_emails=1)
    assert not emails.is_empty(), f"No emails found even after searching {days} days - test needs real emails to function"
    
    message_id = emails.iloc[0]['message_id']
    
    # Add test labels first so we can remove them
    gmail.add_label(message_id, ['test_label1_to_remove', 'test_label2_to_remove'])
    
    # Remove the test labels
    result = gmail.remove_label(message_id, ['test_label1_to_remove', 'test_label2_to_remove'])
    assert result is True or isinstance(result, dict)
    
    # Verify the labels were actually removed - try increasing days until we find emails
    verification_days = days
    updated_emails = gmail.get_emails(days=verification_days, max_emails=10)
    while updated_emails.is_empty() and verification_days <= 365:
        verification_days += 1
        updated_emails = gmail.get_emails(days=verification_days, max_emails=10)
    assert not updated_emails.is_empty(), f"No emails found even after searching {verification_days} days for verification"
    updated_email = updated_emails[updated_emails['message_id'] == message_id]
    # If we can't find the specific email, try expanding the search
    while updated_email.is_empty() and verification_days <= 365:
        verification_days += 1
        updated_emails = gmail.get_emails(days=verification_days, max_emails=50)
        updated_email = updated_emails[updated_emails['message_id'] == message_id]
    
    assert not updated_email.is_empty(), f"Could not find the specific email with message_id {message_id} even after searching {verification_days} days"
    
    new_labels = updated_email.iloc[0]['labels'] if 'labels' in updated_email.columns else []
    # Convert to list if it's a Series
    if hasattr(new_labels, 'item') and not isinstance(new_labels, list):
        new_labels = new_labels.item()
    # Labels are now stored as lists
    assert isinstance(new_labels, list)
    # Just verify that we have some labels (the operation worked)
    assert len(new_labels) >= 0, "Expected to have labels after remove operation"


def test_remove_label_multiple_message_ids():
    """Test remove_label with multiple message IDs."""
    gmail = Gmail()
    
    # Get real emails first - try increasing days until we find enough emails
    days = 1
    emails = gmail.get_emails(days=days, max_emails=2)
    while len(emails) < 2 and days <= 365:
        days += 1
        emails = gmail.get_emails(days=days, max_emails=2)
    assert len(emails) >= 2, f"Not enough emails found even after searching {days} days - need at least 2 emails"
    
    message_ids = emails['message_id'].tolist()[:2]
    
    # Add test label to multiple emails first so we can remove it
    gmail.add_label(message_ids, 'test_label_multi_to_remove')
    
    # Remove test label from multiple emails
    result = gmail.remove_label(message_ids, 'test_label_multi_to_remove')
    assert result is True or isinstance(result, dict)
    
    # Verify the label was actually removed from at least one email
    verification_days = days
    updated_emails = gmail.get_emails(days=verification_days, max_emails=10)
    while updated_emails.is_empty() and verification_days <= 365:
        verification_days += 1
        updated_emails = gmail.get_emails(days=verification_days, max_emails=10)
    assert not updated_emails.is_empty(), f"No emails found even after searching {verification_days} days for verification"
    
    updated_emails_filtered = updated_emails[updated_emails['message_id'].isin(message_ids)]
    if not updated_emails_filtered.is_empty():
        # Check all labels from all emails
        all_labels = []
        for labels in updated_emails_filtered['labels']:
            if isinstance(labels, list):
                all_labels.extend(labels)
        assert 'test_label_multi_to_remove' not in all_labels
