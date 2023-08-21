"""
Detect marketing language in email content.

This module provides functions to identify marketing and promotional
language patterns in email content.
"""

import re


def email_has_marketing_language(text: str) -> bool:
    """
    Check if text contains marketing language.
    
    Args:
        text: Text content to analyze
        
    Returns:
        bool: True if marketing language is detected
    """
    marketing_patterns = [
        r'limited.*time',
        r'act.*now',
        r'don\'t.*miss',
        r'exclusive.*offer',
        r'sale.*end',
        r'hurry.*up',
        r'click.*here',
        r'call.*action'
    ]
    marketing_regex = re.compile('|'.join(marketing_patterns), re.IGNORECASE)
    return bool(marketing_regex.search(text))


def email_count_promotional_words(text: str) -> int:
    """
    Count promotional words in text.
    
    Args:
        text: Text content to analyze
        
    Returns:
        int: Number of promotional words found
    """
    promotional_words = [
        'sale', 'discount', 'offer', 'deal', 'free', 'save', 'percent', '%',
        'buy', 'shop', 'purchase', 'order', 'promo', 'special', 'limited',
        'exclusive', 'bonus', 'gift', 'win', 'prize', 'contest', 'coupon'
    ]
    word_pattern = r'\b(' + '|'.join(promotional_words) + r')\b'
    matches = re.findall(word_pattern, text, re.IGNORECASE)
    return len(matches)


def email_has_promotional_content(text: str) -> bool:
    """
    Check if text contains promotional content.
    
    Args:
        text: Text content to analyze
        
    Returns:
        bool: True if promotional content is detected (2+ promotional words)
    """
    return email_count_promotional_words(text) >= 2
