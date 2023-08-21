"""
Test that EmailDataFrame can accept EmailMessage objects directly.

This test verifies that the EmailDataFrame constructor can handle a list of 
EmailMessage objects and automatically convert them to the appropriate format.
"""

from gmaildr.core.models.email_message import EmailMessage
from gmaildr.data.email_dataframe.email_dataframe import EmailDataFrame
from datetime import datetime


def test_email_dataframe_accepts_single_email_message():
    """Test EmailDataFrame can accept a single EmailMessage object in a list."""
    # Create a sample EmailMessage
    email = EmailMessage(
        message_id='test1',
        sender_email='test@example.com',
        sender_name='Test Sender',
        recipient_email='user@gmail.com',
        recipient_name='User',
        subject='Test Subject',
        timestamp=datetime.now(),
        sender_local_timestamp=datetime.now(),
        size_bytes=1024
    )

    # Test creating EmailDataFrame with EmailMessage objects
    df = EmailDataFrame([email])
    
    # Verify the DataFrame was created correctly
    assert df.shape[0] == 1  # One row
    assert 'message_id' in df.columns
    assert 'sender_email' in df.columns
    assert 'subject' in df.columns
    assert df.iloc[0]['message_id'] == 'test1'
    assert df.iloc[0]['sender_email'] == 'test@example.com'
    assert df.iloc[0]['subject'] == 'Test Subject'


def test_email_dataframe_accepts_multiple_email_messages():
    """Test EmailDataFrame can accept multiple EmailMessage objects."""
    # Create multiple EmailMessage objects
    emails = [
        EmailMessage(
            message_id='test1',
            sender_email='sender1@example.com',
            sender_name='Sender One',
            recipient_email='user@gmail.com',
            recipient_name='User',
            subject='First Email',
            timestamp=datetime.now(),
            sender_local_timestamp=datetime.now(),
            size_bytes=1024
        ),
        EmailMessage(
            message_id='test2',
            sender_email='sender2@example.com',
            sender_name='Sender Two',
            recipient_email='user@gmail.com',
            recipient_name='User',
            subject='Second Email',
            timestamp=datetime.now(),
            sender_local_timestamp=datetime.now(),
            size_bytes=2048
        ),
    ]

    # Test creating EmailDataFrame with multiple EmailMessage objects
    df = EmailDataFrame(emails)
    
    # Verify the DataFrame was created correctly
    assert df.shape[0] == 2  # Two rows
    assert 'message_id' in df.columns
    assert df.iloc[0]['message_id'] == 'test1'
    assert df.iloc[1]['message_id'] == 'test2'
    assert df.iloc[0]['sender_email'] == 'sender1@example.com'
    assert df.iloc[1]['sender_email'] == 'sender2@example.com'


def test_email_dataframe_with_email_messages_includes_all_fields():
    """Test that all EmailMessage fields are properly converted to DataFrame columns."""
    email = EmailMessage(
        message_id='test1',
        sender_email='test@example.com',
        sender_name='Test Sender',
        recipient_email='user@gmail.com',
        recipient_name='User',
        subject='Test Subject',
        timestamp=datetime.now(),
        sender_local_timestamp=datetime.now(),
        size_bytes=1024,
        labels=['INBOX', 'IMPORTANT'],
        thread_id='thread123',
        snippet='This is a test email...',
        has_attachments=True,
        is_read=False,
        is_important=True,
        text_content='Full email content here',
        subject_language='en',
        subject_language_confidence=0.95,
        text_language='en',
        text_language_confidence=0.90,
        has_role_based_email=False,
        is_forwarded=False
    )

    df = EmailDataFrame([email])
    
    # Check that key fields are present and correct
    assert df.iloc[0]['message_id'] == 'test1'
    assert df.iloc[0]['sender_email'] == 'test@example.com'
    assert df.iloc[0]['sender_name'] == 'Test Sender'
    assert df.iloc[0]['recipient_email'] == 'user@gmail.com'
    assert df.iloc[0]['recipient_name'] == 'User'
    assert df.iloc[0]['subject'] == 'Test Subject'
    assert df.iloc[0]['size_bytes'] == 1024
    assert df.iloc[0]['labels'] == ['INBOX', 'IMPORTANT']
    assert df.iloc[0]['thread_id'] == 'thread123'
    assert df.iloc[0]['snippet'] == 'This is a test email...'
    assert df.iloc[0]['has_attachments'] == True
    assert df.iloc[0]['is_read'] == False
    assert df.iloc[0]['is_important'] == True
    assert df.iloc[0]['subject_language'] == 'en'
    assert df.iloc[0]['subject_language_confidence'] == 0.95
    assert df.iloc[0]['text_language'] == 'en'
    assert df.iloc[0]['text_language_confidence'] == 0.90
    assert df.iloc[0]['has_role_based_email'] == False
    assert df.iloc[0]['is_forwarded'] == False


def test_email_dataframe_mixed_types_supported():
    """Test that EmailDataFrame gracefully handles mixing EmailMessage objects with dicts."""
    email = EmailMessage(
        message_id='test1',
        sender_email='test@example.com',
        sender_name='Test Sender',
        recipient_email='user@gmail.com',
        recipient_name='User',
        subject='Test Subject',
        timestamp=datetime.now(),
        sender_local_timestamp=datetime.now(),
        size_bytes=1024
    )
    
    email_dict = {
        'message_id': 'test2',
        'sender_email': 'test2@example.com',
        'sender_name': 'Test Sender 2',
        'recipient_email': 'user@gmail.com',
        'recipient_name': 'User',
        'subject': 'Dict Email',
        'timestamp': datetime.now(),
        'sender_local_timestamp': datetime.now(),
        'size_bytes': 512
    }
    
    # Mixing types should work gracefully
    mixed_data = [email, email_dict]
    
    # This should work without errors
    df = EmailDataFrame(mixed_data)
    
    # Verify both rows are present
    assert df.shape[0] == 2
    assert df.iloc[0]['message_id'] == 'test1'
    assert df.iloc[1]['message_id'] == 'test2'
    assert df.iloc[0]['sender_email'] == 'test@example.com'
    assert df.iloc[1]['sender_email'] == 'test2@example.com'


def test_empty_email_message_list():
    """Test EmailDataFrame with empty list of EmailMessage objects."""
    df = EmailDataFrame([])
    
    # Should create empty DataFrame
    assert df.shape[0] == 0
    assert len(df.columns) == 0
