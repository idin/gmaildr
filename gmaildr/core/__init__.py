"""
Core module for GmailDr.

This module contains the core functionality for Gmail operations.
"""

from .gmail import Gmail
from .gmail_client import GmailClient
from .config import GmailConfig, ConfigManager, setup_logging

__all__ = ['Gmail', 'GmailClient', 'GmailConfig', 'ConfigManager', 'setup_logging']
