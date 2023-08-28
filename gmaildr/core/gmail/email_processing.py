"""
Email processing module for GmailDr.

This module handles email processing operations including:
- Text extraction from emails
- Language detection
- DataFrame conversion
- Role-based email detection
"""

import base64
import logging
from typing import List

import pandas as pd

from ...analysis.language_detector import detect_language_safe
from ..config.config import ROLE_WORDS
from .gmail_sizer import GmailSizer

logger = logging.getLogger(__name__)


class EmailProcessing(GmailSizer):
    """
    Handles email processing operations.
    
    This class provides methods for processing email content,
    extracting text, detecting languages, and converting to DataFrames.
    """
    
    # No constructor needed - inherits from GmailSizer which doesn't need initialization
    
    def add_email_text(self, emails: List, parallelize: bool = False) -> List:
        """
        Add text content to email objects.
        
        Args:
            emails: List of email objects to add text to.
            parallelize: Whether to use parallel processing.
            
        Returns:
            List of email objects with text content added.
        """
        if not emails:
            return emails
        
        if parallelize:
            return self._add_email_text_parallel(emails)
        else:
            return self._add_email_text_sequential(emails)
    
    def _add_email_text_sequential(self, emails: List) -> List:
        """Add text content sequentially."""
        for email in emails:
            try:
                # Use the existing _add_email_text method from EmailOperator
                self._add_email_text([email], parallelize=False)
            except Exception as e:
                logger.warning(f"Failed to get text for email {email.message_id}: {e}")
                email.text_content = ""
        return emails
    
    def _add_email_text_parallel(self, emails: List) -> List:
        """Add text content using parallel processing."""
        # Use the existing _add_email_text method from EmailOperator
        return self._add_email_text(emails, parallelize=True)
    
    @staticmethod
    def extract_email_text(message: dict) -> str:
        """
        Extract text content from Gmail API message.
        
        Args:
            message: Gmail API message object.
            
        Returns:
            Extracted text content.
        """
        def extract_text_from_parts(parts: List[dict]) -> str:
            """
            Extract text content from message parts recursively.
            
            Args:
                parts: List of message parts to extract text from
                
            Returns:
                Extracted text content as string
            """
            text_content = ""
            for part in parts:
                if part.get('mimeType') == 'text/plain':
                    data = part.get('body', {}).get('data', '')
                    if data:
                        try:
                            text_content += base64.urlsafe_b64decode(data).decode('utf-8')
                        except Exception:
                            pass
                elif part.get('mimeType') == 'text/html':
                    # Skip HTML content for now
                    pass
                elif 'parts' in part:
                    text_content += extract_text_from_parts(part['parts'])
            return text_content
        
        payload = message.get('payload', {})
        
        # Handle multipart messages
        if 'parts' in payload:
            return extract_text_from_parts(payload['parts'])
        
        # Handle simple text messages
        if payload.get('mimeType') == 'text/plain':
            data = payload.get('body', {}).get('data', '')
            if data:
                try:
                    return base64.urlsafe_b64decode(data).decode('utf-8')
                except Exception:
                    pass
        
        return ""
    
    def emails_to_dataframe(self, emails: List, include_text: bool = False) -> pd.DataFrame:
        """
        Convert email objects to pandas DataFrame.
        
        Args:
            emails: List of email objects to convert.
            include_text: Whether to include text content in the DataFrame.
            
        Returns:
            DataFrame containing email data.
        """
        if not emails:
            return pd.DataFrame()  # Return empty pandas DataFrame
        
        # Convert emails to dictionaries
        data = []
        for email in emails:
            email_dict = email.to_dict(include_text=include_text)
            data.append(email_dict)
        
        # Create and return pandas DataFrame directly
        return pd.DataFrame(data)
    
    def add_language_detection(self, emails: List, include_text: bool = False) -> List:
        """
        Add language detection to email objects.
        
        Args:
            emails: List of email objects to add language detection to.
            include_text: Whether text content is available for language detection.
            
        Returns:
            List of email objects with language detection added.
        """
        for email in emails:
            # Detect subject language
            if email.subject:
                subject_lang, subject_conf = detect_language_safe(email.subject)
                email.subject_language = subject_lang
                email.subject_language_confidence = subject_conf
            
            # Detect text language if available
            if include_text and email.text_content:
                text_lang, text_conf = detect_language_safe(email.text_content)
                email.text_language = text_lang
                email.text_language_confidence = text_conf
        
        return emails
    
    @staticmethod
    def is_role_based_email(email_address: str) -> bool:
        """
        Check if an email address is role-based (automated/non-human).
        
        Args:
            email_address: Email address to check.
            
        Returns:
            True if the email appears to be role-based, False otherwise.
        """
        if not email_address:
            return False
        
        # Extract local part (before @)
        local_part = email_address.split('@')[0].lower()
        
        # Check if local part contains role words
        for word in ROLE_WORDS:
            if word.lower() in local_part:
                return True
        
        return False
    
    def determine_folder(self, email) -> str:
        """
        Determine which folder an email is in based on its labels.
        
        Args:
            email: Email object to check.
            
        Returns:
            Folder name ('inbox', 'archive', 'spam', 'trash', 'sent', 'drafts').
        """
        labels = email.labels
        
        # Check for folder labels
        if 'INBOX' in labels:
            return 'inbox'
        elif 'SPAM' in labels:
            return 'spam'
        elif 'TRASH' in labels:
            return 'trash'
        elif 'SENT' in labels:
            return 'sent'
        elif 'DRAFT' in labels:
            return 'drafts'
        else:
            # No folder labels means archived
            return 'archive'
