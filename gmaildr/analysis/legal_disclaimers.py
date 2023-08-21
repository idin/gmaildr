"""
Detect legal disclaimers in email content.

This module provides functions to identify legal disclaimers and
related text patterns in email content.
"""

import re


def email_has_legal_disclaimer(text: str) -> bool:
    """
    Check if text contains legal disclaimers.
    
    Args:
        text: Text content to analyze
        
    Returns:
        bool: True if legal disclaimers are detected
    """
    legal_patterns = [
        r'terms.*condition',
        r'privacy.*policy',
        r'disclaimer',
        r'confidential',
        r'copyright',
        r'all.*rights.*reserved',
        r'this.*email.*intended'
    ]
    legal_regex = re.compile('|'.join(legal_patterns), re.IGNORECASE)
    return bool(legal_regex.search(text))
