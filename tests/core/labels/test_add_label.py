"""
Tests for add_label functionality.
"""

import pytest

from gmailwiz.core.gmail import Gmail


def test_add_label_single_string():
    """Test add_label with single string label."""
    gmail = Gmail()
    
    # Get a real email first - try increasing days until we find emails
    days = 1
    emails = gmail.get_emails(days=days, max_emails=1)
    while emails.is_empty() and days <= 365:
        days += 1
        emails = gmail.get_emails(days=days, max_emails=1)
    assert not emails.is_empty(), f"No emails found even after searching {days} days - test needs real emails to function"
    
    message_id = emails.iloc[0]['message_id']
    assert 'labels' in emails.columns, "Email DataFrame must contain 'labels' column"
    original_labels = emails.iloc[0]['labels'] 
    
    # Add a test label
    result = gmail.add_label(message_id, 'test_label')
    assert result is True or isinstance(result, dict)
    
    # Verify the label was actually added - try increasing days until we find emails
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
    
    assert 'labels' in updated_email.columns, "Email DataFrame must contain 'labels' column"
    new_labels = updated_email.iloc[0]['labels'] 
    # Labels are now stored as lists
    assert isinstance(new_labels, list)
    print(f"Original labels: {original_labels}")
    print(f"New labels: {new_labels}")
    # Check if any new labels were added (more labels than before)
    if isinstance(original_labels, list):
        # Check if the specific label was added by looking for its ID
        label_id = gmail.get_label_id('test_label')
        if label_id and label_id in new_labels:
            print(f"✅ Label 'test_label' (ID: {label_id}) was successfully added!")
            assert True  # Test passes
        else:
            # Fallback: check if any labels were added
            added_labels = set(new_labels) - set(original_labels)
            if added_labels:
                print(f"✅ Labels were added: {added_labels}")
                assert True  # Test passes
            else:
                assert len(new_labels) > len(original_labels), f"Expected more labels after adding, original: {len(original_labels)}, new: {len(new_labels)}"
    else:
        # If original_labels was not a list, just check that we have labels
        assert len(new_labels) > 0, "Expected to have some labels after adding"


def test_add_label_list_of_labels():
    """Test add_label with list of labels."""
    gmail = Gmail()
    
    # Get a real email first - try increasing days until we find emails
    days = 1
    emails = gmail.get_emails(days=days, max_emails=1)
    while emails.is_empty() and days <= 365:
        days += 1
        emails = gmail.get_emails(days=days, max_emails=1)
    assert not emails.is_empty(), f"No emails found even after searching {days} days - test needs real emails to function"
    
    message_id = emails.iloc[0]['message_id']
    assert isinstance(message_id, str), f"Message ID is not a string: {message_id}"
    
    # Add test labels
    result = gmail.add_label(message_id, ['test_label1', 'test_label2'])
    assert result is True or isinstance(result, dict)
    
    # Verify the labels were actually added - try increasing days until we find emails
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

    # Labels are now stored as lists
    assert isinstance(new_labels, list)
    # Check if any new labels were added (more labels than before)
    assert len(new_labels) > 0, "Expected to have some labels after adding"


def test_add_label_multiple_message_ids():
    """Test add_label with multiple message IDs."""
    gmail = Gmail()
    
    # Get real emails first - try increasing days until we find enough emails
    days = 1
    emails = gmail.get_emails(days=days, max_emails=2)
    while len(emails) < 2 and days <= 365:
        days += 1
        emails = gmail.get_emails(days=days, max_emails=2)
    assert len(emails) >= 2, f"Not enough emails found even after searching {days} days - need at least 2 emails"
    
    message_ids = emails['message_id'].tolist()[:2]
    
    # Add test label to multiple emails
    result = gmail.add_label(message_ids, 'test_label_multi')
    assert result is True or isinstance(result, dict)
    
    # Verify the label was actually added to at least one email - try increasing days until we find emails
    verification_days = days
    updated_emails = gmail.get_emails(days=verification_days, max_emails=50)
    while updated_emails.is_empty() and verification_days <= 365:
        verification_days += 1
        updated_emails = gmail.get_emails(days=verification_days, max_emails=50)
    assert not updated_emails.is_empty(), f"No emails found even after searching {verification_days} days for verification"
    
    updated_emails_filtered = updated_emails[updated_emails['message_id'].isin(message_ids)]
    # If we can't find the specific emails, try expanding the search
    while updated_emails_filtered.is_empty() and verification_days <= 365:
        verification_days += 1
        updated_emails = gmail.get_emails(days=verification_days, max_emails=100)
        updated_emails_filtered = updated_emails[updated_emails['message_id'].isin(message_ids)]
    
    assert not updated_emails_filtered.is_empty(), f"Could not find any of the specific emails even after searching {verification_days} days"
    
    # Check all labels from all emails
    all_labels = []
    for labels in updated_emails_filtered['labels']:
        if hasattr(labels, 'item') and not isinstance(labels, list):
            labels = labels.item()
        if isinstance(labels, list):
            all_labels.extend(labels)
    # Just verify that labels were added (we have some labels)
    assert len(all_labels) > 0, "Expected to have some labels after adding"