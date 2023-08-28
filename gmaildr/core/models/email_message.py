"""
EmailMessage data model for GmailDr.

This module contains the EmailMessage class which represents a single email message
with all relevant metadata for analysis purposes.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class EmailMessage:
    """
    Represents a single email message with relevant metadata.
    
    This class encapsulates all the important information about an email
    that we need for analysis purposes.
    """
    
    message_id: str
    sender_email: str
    recipient_email: str
    subject: str
    timestamp: datetime
    sender_local_timestamp: datetime
    size_bytes: int
    sender_name: Optional[str] = None
    recipient_name: Optional[str] = None
    labels: List[str] = field(default_factory=list)
    thread_id: Optional[str] = None
    snippet: Optional[str] = None
    has_attachments: bool = False
    is_read: bool = False
    is_important: bool = False
    text_content: Optional[str] = None
    subject_language: Optional[str] = None
    subject_language_confidence: Optional[float] = None
    text_language: Optional[str] = None
    text_language_confidence: Optional[float] = None
    has_role_based_email: bool = False
    is_forwarded: bool = False
    
    def to_dict(self, include_text: bool = False) -> Dict[str, Any]:
        """
        Convert the email message to a dictionary representation.
        
        Args:
            include_text: Whether to include text_content in the dictionary
            
        Returns:
            Dict[str, Any]: Dictionary representation of the email message.
        """
        row = {
            'message_id': self.message_id,
            'sender_email': self.sender_email,
            'sender_name': self.sender_name,
            'recipient_email': self.recipient_email,
            'recipient_name': self.recipient_name,
            'subject': self.subject,
            'timestamp': self.timestamp,
            'sender_local_timestamp': self.sender_local_timestamp.replace(tzinfo=None) if self.sender_local_timestamp.tzinfo else self.sender_local_timestamp,
            'size_bytes': self.size_bytes,
            'size_kb': self.size_bytes / 1024,
            'labels': self.labels,
            'thread_id': self.thread_id,
            'snippet': self.snippet,
            'has_attachments': self.has_attachments,
            'is_read': self.is_read,
            'is_important': self.is_important,
            'year': self.timestamp.year,
            'month': self.timestamp.month,
            'day': self.timestamp.day,
            'hour': self.timestamp.hour,
            'day_of_week': self.timestamp.strftime('%A'),
        }
        
        if include_text and self.text_content is not None:
            row['text_content'] = self.text_content
        
        # Add language detection fields
        if self.subject_language is not None:
            row['subject_language'] = self.subject_language
            row['subject_language_confidence'] = self.subject_language_confidence
        
        if self.text_language is not None:
            row['text_language'] = self.text_language
            row['text_language_confidence'] = self.text_language_confidence
        
        # Add role-based email flag
        row['has_role_based_email'] = self.has_role_based_email
        
        # Add forwarding field
        row['is_forwarded'] = self.is_forwarded
        
        # Add starred status derived from labels
        row['is_starred'] = 'STARRED' in self.labels
            
        return row
