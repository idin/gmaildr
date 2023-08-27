"""
Test Data Factory

Utility functions for generating consistent test data for EmailMessage and EmailDataFrame
across all test files. This ensures all required fields are present and consistent.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from gmaildr.core.models.email_message import EmailMessage


def create_basic_email_dict(
            message_id="test_msg",
            sender_email="test@example.com",
            sender_name="Test Sender",
            recipient_email="user@gmail.com",
            recipient_name="User",
            subject="Test Subject",
            timestamp: Optional[datetime]=None,
            sender_local_timestamp: Optional[datetime]=None,
            size_bytes: int=1024,
            **kwargs
        ) -> Dict[str, Any]:
    """
    Create a basic email dictionary with all required EmailMessage fields.
    
    Args:
        message_id: Unique message identifier
        sender_email: Email address of sender
        sender_name: Display name of sender
        recipient_email: Email address of recipient
        recipient_name: Display name of recipient
        subject: Email subject line
        timestamp: Email timestamp (defaults to now)
        sender_local_timestamp: Sender's local timestamp (defaults to timestamp)
        size_bytes: Email size in bytes
        **kwargs: Additional fields to override defaults
        
    Returns:
        Dict[str, Any]: Complete email dictionary with all required fields
    """
    if timestamp is None:
        timestamp = datetime.now()
    if sender_local_timestamp is None:
        sender_local_timestamp = timestamp
    
    # Base email with all required EmailMessage fields
    email_dict = {
        'message_id': message_id,
        'sender_email': sender_email,
        'sender_name': sender_name,
        'recipient_email': recipient_email,
        'recipient_name': recipient_name,
        'subject': subject,
        'timestamp': timestamp,
        'sender_local_timestamp': sender_local_timestamp,
        'size_bytes': size_bytes,
        
        # Default fields from EmailMessage dataclass
        'labels': [],
        'thread_id': f'thread_{message_id}',
        'snippet': None,
        'has_attachments': False,
        'is_read': False,
        'is_important': False,
        'is_starred': False,  # Missing field that SenderDataFrame expects
        'text_content': f'This is the text content for {subject}',
        'subject_language': 'en',
        'subject_language_confidence': 0.9,
        'text_language': 'en',
        'text_language_confidence': 0.85,
        'has_role_based_email': False,
        'is_forwarded': False,
        'subject_length_chars': len(subject) if subject else 0,
        'text_length_chars': len(f'This is the text content for {subject}') if subject else 0,
        'in_folder': 'inbox',  # Default to inbox for test data
    }
    
    # Override any fields with provided kwargs
    email_dict.update(kwargs)
    
    return email_dict


def create_email_message(
    message_id: str,
    sender_email: str,
    sender_name: str,
    recipient_email: str,
    recipient_name: str,
    subject: str,
    timestamp: Optional[datetime] = None,
    sender_local_timestamp: Optional[datetime] = None,
    size_bytes: int = 1024,
    **kwargs
) -> EmailMessage:
    """
    Create a complete EmailMessage object with all required fields.
    
    Args:
        Same as create_basic_email_dict
        
    Returns:
        EmailMessage: Complete EmailMessage object
    """
    email_dict = create_basic_email_dict(
            message_id=message_id,
            sender_email=sender_email,
            sender_name=sender_name,
            recipient_email=recipient_email,
            recipient_name=recipient_name,
            subject=subject,
            timestamp=timestamp,
            sender_local_timestamp=sender_local_timestamp,
            size_bytes=size_bytes,
            **kwargs
        )
    
    return EmailMessage(**email_dict)


def create_multiple_emails(
    count: int = 3,
    sender_emails: Optional[List[str]] = None,
    time_spread_hours: int = 24,
    base_timestamp: Optional[datetime] = None,
    **kwargs
) -> List[Dict[str, Any]]:
    """
    Create multiple email dictionaries for testing.
    
    Args:
        count: Number of emails to create
        sender_emails: List of sender emails (cycles through if fewer than count)
        time_spread_hours: Hours to spread emails across
        base_timestamp: Starting timestamp (defaults to now)
        **kwargs: Additional fields to apply to all emails
        
    Returns:
        List[Dict[str, Any]]: List of email dictionaries
    """
    if base_timestamp is None:
        base_timestamp = datetime.now()
    
    if sender_emails is None:
        sender_emails = ["sender1@example.com", "sender2@example.com", "sender3@example.com"]
    
    emails = []
    for i in range(count):
        timestamp = base_timestamp - timedelta(hours=i * (time_spread_hours / count))
        sender_email = sender_emails[i % len(sender_emails)]
        
        email = create_basic_email_dict(
            message_id=f"msg_{i+1}",
            sender_email=sender_email,
            sender_name=f"Sender {i+1}",
            recipient_email="user@gmail.com",
            recipient_name="User",
            subject=f"Test Subject {i+1}",
            timestamp=timestamp,
            sender_local_timestamp=timestamp
        )
        emails.append(email)
    
    return emails


def create_test_scenarios() -> Dict[str, List[Dict[str, Any]]]:
    """
    Create predefined test scenarios for common testing needs.
    
    Returns:
        Dict[str, List[Dict[str, Any]]]: Dictionary of scenario names to email lists
    """
    now = datetime.now()
    
    scenarios = {
        'single_email': [
            create_basic_email_dict(
            message_id='single_msg',
            sender_email='test@example.com',
            sender_name='Test Sender',
            recipient_email='user@gmail.com',
            recipient_name='User',
            subject='Single Email Test'
        )
        ],
        
        'zero_size_email': [
            create_basic_email_dict(
            message_id='zero_size_msg',
            sender_email='test@example.com',
            sender_name='Test Sender',
            recipient_email='user@gmail.com',
            recipient_name='User',
            subject='Zero Size Email',
            size_bytes=0
        )
        ],
        
        'empty_subject': [
            create_basic_email_dict(
            message_id='empty_subject_msg',
            sender_email='test@example.com',
            sender_name='',
            recipient_email='user@gmail.com',
            recipient_name='User',
            subject=''
        )
        ],
        
        'duplicate_subjects': [
            create_basic_email_dict(
            message_id='msg1',
            sender_email="test@example.com",
            sender_name="Test Sender",
            recipient_email="user@gmail.com",
            recipient_name="User",
            subject='Same Subject',
            timestamp=now
        ),
            create_basic_email_dict(
            message_id='msg2',
            sender_email="test@example.com",
            sender_name="Test Sender",
            recipient_email="user@gmail.com",
            recipient_name="User",
            subject='Same Subject',
            timestamp=now + timedelta(hours=1
        )
            )
        ],
        
        'multiple_senders': create_multiple_emails(
            count=5,
            sender_emails=['alice@example.com', 'bob@example.com'],
            time_spread_hours=48
        ),
        
        'role_based_emails': [
            create_basic_email_dict(
            message_id='role_msg1',
            sender_email='support@company.com',
            sender_name='Support Team',
            recipient_email="user@gmail.com",
            recipient_name="User",
            subject='Your ticket #123',
            has_role_based_email=True
        ),
            create_basic_email_dict(
            message_id='role_msg2',
            sender_email='noreply@service.com',
            sender_name='No Reply',
            recipient_email="user@gmail.com",
            recipient_name="User",
            subject='Account notification',
            has_role_based_email=True
        )
        ],
        
        'language_diverse': [
            create_basic_email_dict(
            message_id='lang_msg1',
            sender_email="test@example.com",
            sender_name="Test Sender",
            recipient_email="user@gmail.com",
            recipient_name="User",
            subject='Hello World',
            subject_language='en',
            subject_language_confidence=0.95,
            text_language='en',
            text_language_confidence=0.92
        ),
            create_basic_email_dict(
            message_id='lang_msg2',
            sender_email='french@example.fr',
            sender_name="Test Sender",
            recipient_email="user@gmail.com",
            recipient_name="User",
            subject='Bonjour le monde',
            subject_language='fr',
            subject_language_confidence=0.88,
            text_language='fr',
            text_language_confidence=0.85
        )
        ],
        
        'forwarded_emails': [
            create_basic_email_dict(
            message_id='fwd_msg1',
            sender_email="test@example.com",
            sender_name="Test Sender",
            recipient_email='forwarded@gmail.com',
            recipient_name="User",
            subject='Fwd: Important Message',
            is_forwarded=True
        ),
            create_basic_email_dict(
            message_id='fwd_msg2',
            sender_email="test@example.com",
            sender_name="Test Sender",
            recipient_email="user@gmail.com",
            recipient_name="User",
            subject='Regular Message',
            is_forwarded=False
        )
        ],
        
        'read_status_mixed': [
            create_basic_email_dict(
            message_id='read_msg1',
            sender_email="test@example.com",
            sender_name="Test Sender",
            recipient_email="user@gmail.com",
            recipient_name="User",
            subject='Read Email',
            is_read=True,
            is_important=False
        ),
            create_basic_email_dict(
            message_id='unread_msg1',
            sender_email="test@example.com",
            sender_name="Test Sender",
            recipient_email="user@gmail.com",
            recipient_name="User",
            subject='Unread Important Email',
            is_read=False,
            is_important=True
        )
        ]
    }
    
    return scenarios


# Convenience functions for common test needs
def get_minimal_email() -> Dict[str, Any]:
    """Get a minimal but complete email for basic testing."""
    return create_basic_email_dict(
            message_id="test_msg",
            sender_email="test@example.com",
            sender_name="Test Sender",
            recipient_email="user@gmail.com",
            recipient_name="User",
            subject="Test Subject"
        )


def get_empty_fields_email() -> Dict[str, Any]:
    """Get an email with empty values for optional fields."""
    return create_basic_email_dict(
            message_id="test_msg",
            sender_email="test@example.com",
            sender_name='',
            recipient_email="user@gmail.com",
            recipient_name='',
            subject='',
            text_content='',
            thread_id='',
            snippet=''
        )


def get_full_featured_email() -> Dict[str, Any]:
    """Get an email with all fields populated."""
    return create_basic_email_dict(
            message_id="test_msg",
            sender_email="test@example.com",
            sender_name="Test Sender",
            recipient_email="user@gmail.com",
            recipient_name="User",
            subject='Full Featured Test Email',
            labels=['INBOX', 'IMPORTANT'],
            thread_id='thread_123',
            snippet='This is a test email snippet...',
            has_attachments=True,
            is_read=True,
            is_important=True,
            text_content='This is the full text content of the email for testing purposes.',
            subject_language='en',
            subject_language_confidence=0.95,
            text_language='en',
            text_language_confidence=0.92,
            has_role_based_email=False,
            is_forwarded=False
        )
