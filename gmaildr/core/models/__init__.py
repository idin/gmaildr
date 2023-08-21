"""
Data models module for Gmail Doctor.

This module contains data models for emails, senders, and other entities.
"""

from .email_message import EmailMessage
from .sender import Sender

__all__ = ['EmailMessage', 'Sender']
