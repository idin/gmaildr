"""
Test to verify DataFrame cell access types.
"""

import pytest
from gmaildr.core.gmail import Gmail


def test_dataframe_cell_types():
    """Test that accessing single cells from DataFrame returns the correct types."""
    gmail = Gmail()
    
    # Get a real email first - try increasing days until we find emails
    days = 1
    emails = gmail.get_emails(days=days, max_emails=1)
    while emails.empty and days <= 365:
        days += 1
        emails = gmail.get_emails(days=days, max_emails=1)
    assert not emails.empty, f"No emails found even after searching {days} days - test needs real emails to function"
    
    # Test message_id type
    message_id = emails.iloc[0]['message_id']
    print(f"Type of message_id: {type(message_id)}")
    print(f"Value of message_id: {message_id}")
    assert isinstance(message_id, str), f"Expected string, got {type(message_id)}"
    
    # Test labels type
    labels = emails.iloc[0]['labels']
    print(f"Type of labels: {type(labels)}")
    print(f"Value of labels: {labels}")
    assert isinstance(labels, list), f"Expected list, got {type(labels)}"
    
    # Test other columns
    subject = emails.iloc[0]['subject']
    print(f"Type of subject: {type(subject)}")
    assert isinstance(subject, str), f"Expected string, got {type(subject)}"
    
    sender_email = emails.iloc[0]['sender_email']
    print(f"Type of sender_email: {type(sender_email)}")
    assert isinstance(sender_email, str), f"Expected string, got {type(sender_email)}"
    
    # Verify all expected columns exist
    expected_columns = ['message_id', 'sender_email', 'sender_name', 'subject', 'timestamp', 'labels', 'thread_id', 'snippet', 'has_attachments', 'is_read', 'is_important']
    for col in expected_columns:
        assert col in emails.columns, f"Expected column '{col}' not found in DataFrame"
        print(f"Column '{col}' exists and has type: {type(emails.iloc[0][col])}")
