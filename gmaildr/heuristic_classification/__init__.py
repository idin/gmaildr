"""
Classification module for GmailDr.

This module contains classifiers for categorizing emails into different types
such as marketing, personal, work, spam, etc.
"""

from .marketing_classifier import is_marketing_email
from .newsletter_classifier import is_newsletter_email
from .personal_classifier import is_personal_email
from .social_classifier import is_social_email
from .spam_classifier import is_spam_email
from .work_classifier import is_work_email

__all__ = [
    'is_marketing_email',
    'is_newsletter_email', 
    'is_personal_email',
    'is_social_email',
    'is_spam_email',
    'is_work_email'
]
