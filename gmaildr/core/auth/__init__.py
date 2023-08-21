"""
Authentication module for Gmail Doctor.

This module handles OAuth2 authentication for Gmail API access.
"""

from .auth_manager import GmailAuthManager

__all__ = ['GmailAuthManager']
