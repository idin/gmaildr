"""
Calculate text ratios and proportions.

This module provides functions to calculate various ratios and proportions
in email text content, such as caps ratio, promotional word ratio, etc.
"""

import re
from typing import Optional


# Import dependencies
from .count_caps_words import email_count_caps_words
from .marketing_language import email_count_promotional_words


def email_calculate_caps_ratio(text: str) -> float:
    """
    Calculate ratio of uppercase words to total words.
    
    Args:
        text: Text content to analyze
        
    Returns:
        float: Ratio of caps words to total words (0.0 to 1.0)
    """
    caps_count = email_count_caps_words(text)
    total_words = len(text.split())
    
    if total_words == 0:
        return 0.0
        
    return caps_count / total_words


def email_calculate_promotional_ratio(text: str) -> float:
    """
    Calculate ratio of promotional words to total words.
    
    Args:
        text: Text content to analyze
        
    Returns:
        float: Ratio of promotional words to total words (0.0 to 1.0)
    """
    promo_count = email_count_promotional_words(text)
    total_words = len(re.findall(r'\b\w+\b', text))
    
    if total_words == 0:
        return 0.0
        
    return promo_count / total_words


def email_calculate_html_ratio(text_content: Optional[str], html_content: Optional[str]) -> float:
    """
    Calculate ratio of HTML to text content.
    
    Args:
        text_content: Plain text content
        html_content: HTML content
        
    Returns:
        float: Ratio of HTML to text content
    """
    if not html_content:
        return 0.0
        
    html_len = len(html_content)
    text_len = len(text_content) if text_content else 0
    
    if text_len == 0:
        return 1.0
        
    return min(html_len / text_len, 10.0)  # Cap at 10.0


def email_calculate_link_ratio(text: str, html_content: Optional[str]) -> float:
    """
    Calculate ratio of links to total text.
    
    Args:
        text: Text content
        html_content: HTML content
        
    Returns:
        float: Ratio of links to total words
    """
    from .count_external_links import email_count_external_links
    
    link_count = email_count_external_links(html_content)
    word_count = len(text.split())
    
    if word_count == 0:
        return 0.0
        
    return min(link_count / word_count, 1.0)  # Cap at 1.0
