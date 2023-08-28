"""
Test utilities - shared helper functions for all tests.
"""

from datetime import datetime, timedelta
from typing import List, Optional

import pandas as pd

from gmaildr import Gmail

from ..core.models.email_message import EmailMessage


def get_emails(gmail: Gmail, n: int, return_days_used: bool = False, **kwargs):
    """
    Get at least N emails by intelligently increasing the date range.
    
    Args:
        gmail: Gmail instance
        n: Minimum number of emails to retrieve
        return_days_used: If True, return tuple of (emails, days_used)
        **kwargs: Additional filtering parameters (in_folder, from_sender, subject_contains, etc.)
        
    Returns:
        DataFrame containing at least N emails (or all available if less than N)
        If return_days_used=True, returns tuple of (DataFrame, int)
    """
    days = 1
    
    while days <= 365:
        # Get emails for this date range
        # Pass through all additional filters
        emails = gmail.get_emails(days=days, max_emails=n, **kwargs)
        
        if len(emails) >= n:
            result = emails.head(n)
            return (result, days) if return_days_used else result
        
        # Double the days for next iteration (exponential growth)
        days *= 2

    # If we reach here, return whatever we have
    return (emails, days) if return_days_used else emails
        

def create_test_email(
    message_id: str = "test_msg_1",
    sender_email: str = "test@example.com",
    sender_name: str = "Test Sender",
    recipient_email: str = "user@gmail.com",
    recipient_name: str = "User",
    subject: str = "Test Subject",
    text_content: Optional[str] = "This is a test email.",
    timestamp: Optional[datetime] = None,
    size_bytes: int = 1024,
    **kwargs
) -> EmailMessage:
    """
    Create a test EmailMessage with all required parameters.
    
    Args:
        message_id: Unique message identifier
        sender_email: Email address of sender
        sender_name: Display name of sender
        recipient_email: Email address of recipient
        recipient_name: Display name of recipient
        subject: Email subject line
        text_content: Email body text
        timestamp: Email timestamp (defaults to now)
        size_bytes: Email size in bytes
        **kwargs: Additional fields to override defaults
        
    Returns:
        EmailMessage: Complete EmailMessage object
    """
    if timestamp is None:
        timestamp = datetime.now()
    
    return EmailMessage(
        message_id=message_id,
        sender_email=sender_email,
        sender_name=sender_name,
        recipient_email=recipient_email,
        recipient_name=recipient_name,
        subject=subject,
        timestamp=timestamp,
        sender_local_timestamp=timestamp,
        size_bytes=size_bytes,
        text_content=text_content,
        **kwargs
    )


def create_test_emails(
    count: int = 3,
    sender_emails: Optional[List[str]] = None,
    time_spread_hours: int = 24,
    base_timestamp: Optional[datetime] = None,
    **kwargs
) -> List[EmailMessage]:
    """
    Create multiple test EmailMessage objects.
    
    Args:
        count: Number of emails to create
        sender_emails: List of sender emails (cycles through if fewer than count)
        time_spread_hours: Hours to spread emails across
        base_timestamp: Starting timestamp (defaults to now)
        **kwargs: Additional fields to apply to all emails
        
    Returns:
        List[EmailMessage]: List of EmailMessage objects
    """
    if base_timestamp is None:
        base_timestamp = datetime.now()
    
    if sender_emails is None:
        sender_emails = ["sender1@example.com", "sender2@example.com", "sender3@example.com"]
    
    emails = []
    for i in range(count):
        timestamp = base_timestamp - timedelta(hours=i * (time_spread_hours / count))
        sender_email = sender_emails[i % len(sender_emails)]
        
        email = create_test_email(
            message_id=f"msg_{i+1}",
            sender_email=sender_email,
            sender_name=f"Sender {i+1}",
            subject=f"Test Subject {i+1}",
            timestamp=timestamp,
            **kwargs
        )
        emails.append(email)
    
    return emails


def create_role_based_test_email(
    message_id: str = "role_msg_1",
    role_type: str = "admin",
    **kwargs
) -> EmailMessage:
    """
    Create a test email that will be detected as role-based.
    
    Args:
        message_id: Unique message identifier
        role_type: Type of role ('admin', 'support', 'newsletter', 'noreply')
        **kwargs: Additional fields to override defaults
        
    Returns:
        EmailMessage: Role-based EmailMessage object
    """
    role_configs = {
        'admin': {
            'sender_email': 'admin@company.com',
            'sender_name': 'Admin Team',
            'subject': 'System Update',
            'text_content': 'System maintenance scheduled.'
        },
        'support': {
            'sender_email': 'support@company.com',
            'sender_name': 'Support Team',
            'subject': 'Ticket #12345',
            'text_content': 'Your ticket has been resolved.'
        },
        'newsletter': {
            'sender_email': 'newsletter@company.com',
            'sender_name': 'Newsletter',
            'subject': 'Weekly Update',
            'text_content': 'Check out our latest news!'
        },
        'noreply': {
            'sender_email': 'noreply@company.com',
            'sender_name': 'No Reply',
            'subject': 'Account Update',
            'text_content': 'Your account has been updated.'
        }
    }
    
    config = role_configs.get(role_type, role_configs['admin'])
    
    # Merge config with kwargs, giving priority to kwargs
    merged_config = {**config, **kwargs}
    
    return create_test_email(
        message_id=message_id,
        **merged_config
    )


def create_personal_test_email(
    message_id: str = "personal_msg_1",
    **kwargs
) -> EmailMessage:
    """
    Create a test email that will be detected as personal.
    
    Args:
        message_id: Unique message identifier
        **kwargs: Additional fields to override defaults
        
    Returns:
        EmailMessage: Personal EmailMessage object
    """
    # Default personal email config
    personal_config = {
        'sender_email': "john.smith@gmail.com",
        'sender_name': "John Smith",
        'subject': "Meeting tomorrow",
        'text_content': "Hi, can we meet tomorrow?"
    }
    
    # Merge config with kwargs, giving priority to kwargs
    merged_config = {**personal_config, **kwargs}
    
    return create_test_email(
        message_id=message_id,
        **merged_config
    )


def create_multilingual_test_emails() -> List[EmailMessage]:
    """
    Create test emails in different languages.
    
    Returns:
        List[EmailMessage]: List of multilingual EmailMessage objects
    """
    return [
        create_test_email(
            message_id="en_msg",
            sender_email="john@example.com",
            sender_name="John",
            subject="Hello, this is a test email",
            text_content="This is the body of the email in English."
        ),
        create_test_email(
            message_id="es_msg",
            sender_email="maria@example.com",
            sender_name="María",
            subject="Hola, esto es un correo de prueba",
            text_content="Este es el cuerpo del correo en español."
        ),
        create_test_email(
            message_id="fr_msg",
            sender_email="pierre@example.com",
            sender_name="Pierre",
            subject="Bonjour, ceci est un email de test",
            text_content="Ceci est le corps de l'email en français."
        )
    ]


def test_get_emails():
    """
    Test function for get_emails functionality.
    
    Simple test to verify Gmail email retrieval works correctly.
    """
    gmail = Gmail()

    for i in [1, 10, 100]:
        emails = get_emails(gmail, i)
        assert len(emails) == i