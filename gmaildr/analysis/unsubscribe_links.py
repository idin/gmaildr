"""
Detect unsubscribe links in email content.

This module provides functions to identify unsubscribe links and related
text patterns in email content.
"""

from typing import Optional

from ..utils import match_patterns


def email_has_unsubscribe_link(text: str, html_content: Optional[str] = None) -> bool:
    """
    Check for unsubscribe links or text in email content.
    
    Args:
        text: Plain text content to analyze
        html_content: HTML content to analyze (optional)
        
    Returns:
        bool: True if unsubscribe indicators are found
    """
    simplified_patterns = [
        "unsubscribe",
        "opt out",
        "opt-out",
        "remove list",
        "stop email",
        "manage subscription",
        "email preference",
        "click unsubscribe",
        "unsubscribe here",
        "to unsubscribe",
        "remove email",
        "stop receiving",
        "no longer want",
        "preference center",
        "email settings",
    ]

    if match_patterns(text, simplified_patterns):
        return True

    if html_content and match_patterns(html_content, "unsubscribe"):
        return True

    return False
