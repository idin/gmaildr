"""
Test the analyze_email_content function.

This module tests the main email content analysis function
that combines all single-purpose analysis functions.
"""

import pytest
from gmaildr.analysis import analyze_email_content


def test_analyze_email_content_empty():
    """Test analyze_email_content with empty content."""
    result = analyze_email_content()
    
    assert result['has_unsubscribe_link'] is False
    assert result['has_marketing_language'] is False
    assert result['has_legal_disclaimer'] is False
    assert result['has_promotional_content'] is False
    assert result['has_tracking_pixels'] is False
    assert result['has_bulk_email_indicators'] is False
    assert result['external_link_count'] == 0
    assert result['image_count'] == 0
    assert result['exclamation_count'] == 0
    assert result['caps_word_count'] == 0
    assert result['html_to_text_ratio'] == 0.0
    assert result['link_to_text_ratio'] == 0.0
    assert result['caps_ratio'] == 0.0
    assert result['promotional_word_ratio'] == 0.0


def test_analyze_email_content_with_unsubscribe():
    """Test analyze_email_content with unsubscribe link."""
    text = "To unsubscribe from our newsletter"
    result = analyze_email_content(text_content=text)
    
    assert result['has_unsubscribe_link'] is True
    assert result['has_marketing_language'] is False
    assert result['has_legal_disclaimer'] is False


def test_analyze_email_content_with_marketing():
    """Test analyze_email_content with marketing language."""
    text = "Limited time offer! Act now before it's gone!"
    result = analyze_email_content(text_content=text)
    
    assert result['has_marketing_language'] is True
    assert result['has_promotional_content'] is True
    assert result['promotional_word_ratio'] > 0.0


def test_analyze_email_content_with_legal():
    """Test analyze_email_content with legal disclaimers."""
    text = "Please read our privacy policy and terms of service"
    result = analyze_email_content(text_content=text)
    
    assert result['has_legal_disclaimer'] is True


def test_analyze_email_content_with_bulk_indicators():
    """Test analyze_email_content with bulk email indicators."""
    text = "This is an automated message. Do not reply."
    result = analyze_email_content(text_content=text)
    
    assert result['has_bulk_email_indicators'] is True


def test_analyze_email_content_with_html():
    """Test analyze_email_content with HTML content."""
    html = '<img src="tracking.gif" width="1" height="1">'
    result = analyze_email_content(html_content=html)
    
    assert result['has_tracking_pixels'] is True
    assert result['image_count'] > 0
    assert result['html_to_text_ratio'] > 0.0


def test_analyze_email_content_with_caps():
    """Test analyze_email_content with capitalized words."""
    text = "URGENT: Please READ this IMPORTANT message"
    result = analyze_email_content(text_content=text)
    
    assert result['caps_word_count'] > 0
    assert result['caps_ratio'] > 0.0


def test_analyze_email_content_with_exclamations():
    """Test analyze_email_content with exclamation marks."""
    text = "Sale! Buy now! Limited time!!!"
    result = analyze_email_content(text_content=text)
    
    assert result['exclamation_count'] == 5  # "Sale!" + "Buy now!" + "Limited time!!!"


def test_analyze_email_content_with_links():
    """Test analyze_email_content with external links."""
    html = '<a href="https://example.com">Click here</a>'
    result = analyze_email_content(html_content=html)
    
    assert result['external_link_count'] == 1
    assert result['link_to_text_ratio'] > 0.0
