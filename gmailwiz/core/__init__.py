"""
Core GmailWiz functionality.

This module contains the main Gmail client, configuration, and core functionality.
"""

from .gmail import Gmail
from .gmail_client import GmailClient
from .config import ConfigManager, setup_logging

__all__ = [
    "Gmail",
    "GmailClient", 
    "ConfigManager",
    "setup_logging"
]
