"""
Detect bulk email indicators in email content.

This module provides functions to identify bulk email and automated
message indicators in email content.
"""

import re


def email_has_bulk_email_indicators(text: str) -> bool:
    """
    Check for bulk email indicators.
    
    Args:
        text: Text content to analyze
        
    Returns:
        bool: True if bulk email indicators are detected
    """
    bulk_patterns = [
        r'this.*automated.*message',
        r'do.*not.*reply',
        r'automatically.*generated',
        r'system.*notification',
        r'noreply',
        r'no.reply',
        r'bulk.*mail'
    ]
    bulk_regex = re.compile('|'.join(bulk_patterns), re.IGNORECASE)
    return bool(bulk_regex.search(text))
