"""
Analyze email content comprehensively.

This module provides a main function that combines all single-purpose
analysis functions to provide comprehensive email content analysis.
"""

import re
from typing import Dict, Any, Optional

# Import all analysis functions
from .unsubscribe_links import email_has_unsubscribe_link
from .marketing_language import email_has_marketing_language, email_has_promotional_content
from .legal_disclaimers import email_has_legal_disclaimer
from .bulk_email_indicators import email_has_bulk_email_indicators
from .tracking_pixels import email_has_tracking_pixels
from .count_external_links import email_count_external_links
from .count_images import email_count_images
from .count_exclamations import email_count_exclamations
from .count_caps_words import email_count_caps_words
from .calculate_text_ratios import (
    email_calculate_html_ratio,
    email_calculate_link_ratio,
    email_calculate_caps_ratio,
    email_calculate_promotional_ratio
)


def analyze_email_content(
    text_content: Optional[str] = None,
    html_content: Optional[str] = None,
    subject: Optional[str] = None
) -> Dict[str, Any]:
    """
    Analyze email content comprehensively and return all metrics.
    
    Args:
        text_content: Plain text content of email
        html_content: HTML content of email
        subject: Email subject line
        
    Returns:
        Dict[str, Any]: Dictionary containing all analysis metrics
    """
    # Combine all available text for analysis
    combined_text = _combine_text(
        text_content=text_content,
        html_content=html_content,
        subject=subject
    )
    
    if not combined_text:
        return _get_empty_metrics()
    
    # Calculate flags
    has_unsubscribe_link = email_has_unsubscribe_link(
        text=combined_text,
        html_content=html_content
    )
    has_marketing_language = email_has_marketing_language(combined_text)
    has_legal_disclaimer = email_has_legal_disclaimer(combined_text)
    has_promotional_content = email_has_promotional_content(combined_text)
    has_tracking_pixels = email_has_tracking_pixels(html_content)
    has_bulk_email_indicators = email_has_bulk_email_indicators(combined_text)
    
    # Calculate counts
    external_link_count = email_count_external_links(html_content)
    image_count = email_count_images(html_content)
    exclamation_count = email_count_exclamations(combined_text)
    caps_word_count = email_count_caps_words(combined_text)
    
    # Calculate ratios
    html_to_text_ratio = email_calculate_html_ratio(text_content, html_content)
    link_to_text_ratio = email_calculate_link_ratio(combined_text, html_content)
    caps_ratio = email_calculate_caps_ratio(text=combined_text)
    promotional_word_ratio = email_calculate_promotional_ratio(text=combined_text)
    
    return {
        # Flags
        'has_unsubscribe_link': has_unsubscribe_link,
        'has_marketing_language': has_marketing_language,
        'has_legal_disclaimer': has_legal_disclaimer,
        'has_promotional_content': has_promotional_content,
        'has_tracking_pixels': has_tracking_pixels,
        'has_bulk_email_indicators': has_bulk_email_indicators,
        
        # Counts
        'external_link_count': external_link_count,
        'image_count': image_count,
        'exclamation_count': exclamation_count,
        'caps_word_count': caps_word_count,
        
        # Ratios
        'html_to_text_ratio': round(html_to_text_ratio, 3),
        'link_to_text_ratio': round(link_to_text_ratio, 3),
        'caps_ratio': round(caps_ratio, 3),
        'promotional_word_ratio': round(promotional_word_ratio, 3),
    }


def _get_empty_metrics() -> Dict[str, Any]:
    """Return empty metrics dictionary."""
    return {
        'has_unsubscribe_link': False,
        'has_marketing_language': False,
        'has_legal_disclaimer': False,
        'has_promotional_content': False,
        'has_tracking_pixels': False,
        'has_bulk_email_indicators': False,
        'external_link_count': 0,
        'image_count': 0,
        'exclamation_count': 0,
        'caps_word_count': 0,
        'html_to_text_ratio': 0.0,
        'link_to_text_ratio': 0.0,
        'caps_ratio': 0.0,
        'promotional_word_ratio': 0.0,
    }


def _combine_text(
    text_content: Optional[str], 
    html_content: Optional[str], 
    subject: Optional[str]
) -> str:
    """Combine all available text content for analysis."""
    parts = []
    
    if subject:
        parts.append(subject)
    if text_content:
        parts.append(text_content)
    if html_content:
        # Extract text from HTML (simple approach)
        clean_html = re.sub(r'<[^>]+>', ' ', html_content)
        parts.append(clean_html)
        
    return ' '.join(parts)
