"""
Test that EmailDataFrame includes language detection and role-based email columns.
"""

import pytest
from gmaildr import Gmail
from gmaildr.core.models.email_message import EmailMessage
from datetime import datetime
from tests.test_utils import create_test_email, create_role_based_test_email, create_personal_test_email


def test_email_dataframe_has_language_columns():
    """Test that EmailDataFrame includes language detection columns."""
    
    gmail = Gmail()
    
    # Create test email with language detection data using utility
    test_email = create_test_email(
        message_id="test1",
        sender_email="john@example.com",
        sender_name="John Smith",
        subject="Hello world",
        text_content="This is a test email in English.",
        subject_language="en",
        subject_language_confidence=0.8,
        text_language="en",
        text_language_confidence=0.6,
        has_role_based_email=False
    )
    
    # Convert to DataFrame
    df = gmail._emails_to_dataframe(emails=[test_email], include_text=True)
    
    # Check that all expected columns are present
    expected_columns = [
        'subject_language',
        'subject_language_confidence', 
        'text_language',
        'text_language_confidence',
        'has_role_based_email'
    ]
    
    for col in expected_columns:
        assert col in df.columns, f"Column '{col}' should be present in EmailDataFrame"
    
    # Check that the values are correct (language detection runs automatically)
    row = df.iloc[0]
    assert row['subject_language'] == 'en'
    assert row['subject_language_confidence'] > 0.0  # Will be auto-detected
    assert row['text_language'] == 'en'
    assert row['text_language_confidence'] > 0.0  # Will be auto-detected
    assert row['has_role_based_email'] == False
    
    print("✅ EmailDataFrame includes all language detection and role-based email columns")


def test_email_dataframe_role_based_emails():
    """Test that EmailDataFrame correctly handles role-based emails."""
    
    gmail = Gmail()
    
    # Create test emails with different role types using utilities
    test_emails = [
        create_role_based_test_email(
            message_id="role1",
            role_type="admin",
            has_role_based_email=True
        ),
        create_personal_test_email(
            message_id="personal1",
            has_role_based_email=False
        )
    ]
    
    # Convert to DataFrame
    df = gmail._emails_to_dataframe(emails=test_emails, include_text=True)
    
    # Check role-based email detection
    role_emails = df[df['has_role_based_email'] == True]
    personal_emails = df[df['has_role_based_email'] == False]
    
    assert len(role_emails) == 1, "Should have 1 role-based email"
    assert len(personal_emails) == 1, "Should have 1 personal email"
    
    assert role_emails.iloc[0]['sender_email'] == 'admin@company.com'
    assert personal_emails.iloc[0]['sender_email'] == 'john.smith@gmail.com'
    
    print("✅ EmailDataFrame correctly handles role-based email detection")


def test_email_dataframe_language_detection_integration():
    """Test that EmailDataFrame works with automatic language detection."""
    
    gmail = Gmail()
    
    # Create test emails without pre-set language data using utilities
    test_emails = [
        create_test_email(
            message_id="test1",
            sender_email="john@example.com",
            sender_name="John Smith",
            subject="Hello world",
            text_content="This is a test email in English."
        ),
        create_role_based_test_email(
            message_id="test2",
            role_type="support",
            subject="Ticket resolved",
            text_content="Your ticket has been resolved."
        )
    ]
    
    # Convert to DataFrame (this should trigger automatic language detection)
    df = gmail._emails_to_dataframe(emails=test_emails, include_text=True)
    
    # Check that language columns are present and populated
    assert 'subject_language' in df.columns
    assert 'text_language' in df.columns
    assert 'has_role_based_email' in df.columns
    
    # Check that language detection worked
    assert df.iloc[0]['subject_language'] == 'en'  # English subject
    assert df.iloc[1]['has_role_based_email'] == True  # support@ is role-based
    
    print("✅ EmailDataFrame works with automatic language and role detection")
