"""
GmailDr - A powerful Gmail analysis, management, and automation wizard.

This package provides tools to connect to Gmail, analyze email data,
generate statistics about email senders and usage patterns, and automate
email management tasks.
"""

__version__ = "1.1.0"
__author__ = "idin"

from .core import Gmail
from .core.client.gmail_client import GmailClient
from .core.config.config import ConfigManager, setup_logging
from .core.models.email_message import EmailMessage
from .core.models.sender import Sender
from .data import EmailDataFrame
from .data import SenderDataFrame
from .analysis import (
    analyze_email_content,
    detect_language_safe,
    is_english,
    get_language_name,
    process_metrics
)

__all__ = [
    "Gmail",
    "GmailClient",
    "ConfigManager",
    "setup_logging",
    "EmailDataFrame",
    "SenderDataFrame",
    "EmailMessage",
    "Sender",

    "analyze_email_content",
    "detect_language_safe",
    "is_english",
    "get_language_name",
    "process_metrics",
]
