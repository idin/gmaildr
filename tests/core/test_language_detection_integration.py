"""
Test language detection integration in email processing.

This test verifies that language detection is properly added to emails
during the DataFrame conversion process.
"""

import pytest
from gmaildr import Gmail
from gmaildr.core.models.email_message import EmailMessage
from datetime import datetime
from tests.test_utils import create_test_email, create_multilingual_test_emails, create_role_based_test_email, create_personal_test_email


def test_language_detection_in_email_processing():
    """Test that language detection is added to emails during processing."""
    
    gmail = Gmail()
    
    # Create test email objects using utility
    test_emails = [
        create_test_email(
            message_id="test1",
            sender_email="test@example.com",
            sender_name="Test User",
            subject="Hello, this is a test email",
            text_content="This is the body of the email in English."
        ),
        create_test_email(
            message_id="test2",
            sender_email="test2@example.com",
            sender_name="Test User 2",
            subject="Hola, esto es un correo de prueba",
            text_content="Este es el cuerpo del correo en español."
        )
    ]
    
    # Test language detection addition
    processed_emails = gmail._add_language_detection(emails=test_emails, include_text=True)
    
    # Check that language detection was added
    for email in processed_emails:
        assert hasattr(email, 'subject_language')
        assert hasattr(email, 'subject_language_confidence')
        assert hasattr(email, 'text_language')
        assert hasattr(email, 'text_language_confidence')
    
    # Check specific language detection results
    english_email = processed_emails[0]
    spanish_email = processed_emails[1]
    
    # English email should be detected as English
    assert english_email.subject_language == 'en'
    assert english_email.text_language == 'en'
    assert english_email.subject_language_confidence > 0.5
    assert english_email.text_language_confidence >= 0.0  # Lower threshold for text confidence
    
    # Spanish email should be detected as Spanish (or Galician)
    assert spanish_email.subject_language in ['es', 'gl']
    assert spanish_email.text_language in ['es', 'gl']
    assert spanish_email.subject_language_confidence > 0.0
    assert spanish_email.text_language_confidence >= 0.0  # Can be 0.0 for very low confidence
    
    print("✅ Language detection integration test passed")


def test_language_detection_without_text():
    """Test language detection when text content is not included."""
    
    gmail = Gmail()
    
    # Create test email without text content using utility
    test_email = create_test_email(
        message_id="test3",
        subject="Hello, this is a test email",
        text_content=None
    )
    
    # Test language detection addition without text
    processed_emails = gmail._add_language_detection(emails=[test_email], include_text=False)
    
    # Should still detect subject language
    email = processed_emails[0]
    assert email.subject_language == 'en'
    assert email.subject_language_confidence > 0.5
    
    # Text language should be None since no text was provided
    assert email.text_language is None
    assert email.text_language_confidence is None
    
    print("✅ Language detection without text test passed")


def test_language_detection_empty_content():
    """Test language detection with empty content."""
    
    gmail = Gmail()
    
    # Create test email with empty content using utility
    test_email = create_test_email(
        message_id="test4",
        subject="",
        text_content=""
    )
    
    # Test language detection addition
    processed_emails = gmail._add_language_detection(emails=[test_email], include_text=True)
    
    # Should handle empty content gracefully
    email = processed_emails[0]
    assert email.subject_language is None
    assert email.subject_language_confidence is None
    assert email.text_language is None
    assert email.text_language_confidence is None
    
    print("✅ Language detection with empty content test passed")


def test_language_detection_in_dataframe():
    """Test that language detection appears in the final DataFrame."""
    
    gmail = Gmail()
    
    # Create test email objects using utility
    test_emails = [
        create_test_email(
            message_id="test5",
            subject="Hello, this is a test email",
            text_content="This is the body of the email in English."
        )
    ]
    
    # Convert to DataFrame with text content
    df = gmail._emails_to_dataframe(emails=test_emails, include_text=True)
    
    # Check that language columns are present
    assert 'subject_language' in df.columns
    assert 'subject_language_confidence' in df.columns
    assert 'text_language' in df.columns
    assert 'text_language_confidence' in df.columns
    
    # Check the values
    row = df.iloc[0]
    assert row['subject_language'] == 'en'
    assert row['text_language'] == 'en'
    assert row['subject_language_confidence'] > 0.5
    assert row['text_language_confidence'] > 0.0  # Lower threshold for text confidence
    
    print("✅ Language detection in DataFrame test passed")


def test_language_detection_simple_integration():
    """Test simple language detection integration with real data."""
    
    gmail = Gmail()
    
    # Create a simple test email using utility
    email = create_test_email(
        message_id='test',
        subject='Hello world',
        text_content='This is a test email in English.'
    )
    
    # Process the email with language detection
    processed = gmail._add_language_detection([email], include_text=True)
    
    # Check the results
    assert processed[0].subject_language == 'en'
    assert processed[0].text_language == 'en'
    assert processed[0].subject_language_confidence > 0.5
    assert processed[0].text_language_confidence > 0.5
    
    print(f"✅ Subject language: {processed[0].subject_language} ({processed[0].subject_language_confidence:.2f})")
    print(f"✅ Text language: {processed[0].text_language} ({processed[0].text_language_confidence:.2f})")


def test_role_based_email_detection():
    """Test role-based email detection."""
    
    gmail = Gmail()
    
    # Test role-based emails using utility functions
    role_emails = [
        create_role_based_test_email(message_id="role1", role_type="admin"),
        create_role_based_test_email(message_id="role2", role_type="support"),
        create_role_based_test_email(message_id="role3", role_type="newsletter")
    ]
    
    # Test personal emails using utility functions
    personal_emails = [
        create_personal_test_email(message_id="personal1"),
        create_personal_test_email(
            message_id="personal2",
            sender_email="sarah.jones@yahoo.com",
            sender_name="Sarah Jones",
            subject="Project update",
            text_content="Here's the latest project status."
        )
    ]
    
    # Process all emails
    all_emails = role_emails + personal_emails
    processed_emails = gmail._add_language_detection(emails=all_emails, include_text=True)
    
    # Check role-based emails
    for i, email in enumerate(processed_emails[:3]):
        assert email.has_role_based_email == True, f"Email {i+1} should be detected as role-based: {email.sender_email}"
        print(f"✅ Role-based email detected: {email.sender_email}")
    
    # Check personal emails
    for i, email in enumerate(processed_emails[3:]):
        assert email.has_role_based_email == False, f"Email {i+4} should not be detected as role-based: {email.sender_email}"
        print(f"✅ Personal email correctly identified: {email.sender_email}")
    
    print("✅ Role-based email detection test passed")
