"""
Count exclamation marks in text.

This module provides functions to count exclamation marks
in email text content.
"""


def email_count_exclamations(text: str) -> int:
    """
    Count exclamation marks in text.
    
    Args:
        text: Text content to analyze
        
    Returns:
        int: Number of exclamation marks found
    """
    return text.count('!')
