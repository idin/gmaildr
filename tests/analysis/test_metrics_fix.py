"""
Tests for the metrics fix - ensuring HTML-based metrics are properly calculated.

Tests that external_link_count, image_count, html_to_text_ratio, and other
HTML-based metrics are calculated correctly instead of being hardcoded to zero.
"""

import pytest
import pandas as pd

from gmaildr.analysis.metrics_processor import add_content_metrics_to_dataframe


class TestMetricsFix:
    """Test that HTML-based metrics are properly calculated."""
    
    def test_html_metrics_not_zero(self):
        """Test that HTML metrics are calculated properly, not hardcoded to zero."""
        # Create test data with HTML content
        test_data = {
            'text_content': [
                '<html><body><img src="test.jpg"><a href="https://example.com">Link</a></body></html>',
                '<div><p>Plain text</p><img src="image.png"><a href="http://test.org">Another link</a></div>',
                'Just plain text without HTML'
            ],
            'subject': [
                'Test HTML Email',
                'Mixed Content Email', 
                'Plain Text Email'
            ]
        }
        
        df = pd.DataFrame(test_data)
        result = add_content_metrics_to_dataframe(df, show_progress=False)
        
        # Check that HTML metrics are calculated (not hardcoded to zero)
        # First email should have HTML metrics
        assert result['external_link_count'].iloc[0] > 0, "external_link_count should be calculated"
        assert result['image_count'].iloc[0] > 0, "image_count should be calculated"
        assert result['html_to_text_ratio'].iloc[0] > 0, "html_to_text_ratio should be calculated"
        
        # Second email should also have HTML metrics
        assert result['external_link_count'].iloc[1] > 0, "external_link_count should be calculated"
        assert result['image_count'].iloc[1] > 0, "image_count should be calculated"
        assert result['html_to_text_ratio'].iloc[1] > 0, "html_to_text_ratio should be calculated"
        
        # Third email (plain text) should have zero HTML metrics
        assert result['external_link_count'].iloc[2] == 0, "Plain text should have zero external links"
        assert result['image_count'].iloc[2] == 0, "Plain text should have zero images"
        assert result['html_to_text_ratio'].iloc[2] == 0.0, "Plain text should have zero HTML ratio"
    
    def test_tracking_pixels_detection(self):
        """Test that tracking pixels are properly detected."""
        test_data = {
            'text_content': [
                '<img src="https://tracking.example.com/pixel.gif?user=123" width="1" height="1">',
                '<img src="https://analytics.com/beacon.gif" width="1" height="1">',
                '<img src="normal-image.jpg" width="100" height="100">',
                'Plain text without images'
            ],
            'subject': [
                'Email with tracking pixel',
                'Email with beacon',
                'Email with normal image',
                'Plain text email'
            ]
        }
        
        df = pd.DataFrame(test_data)
        result = add_content_metrics_to_dataframe(df, show_progress=False)
        
        # First two should have tracking pixels detected
        assert result['has_tracking_pixels'].iloc[0] == True, "Should detect tracking pixel"
        assert result['has_tracking_pixels'].iloc[1] == True, "Should detect beacon"
        
        # Last two should not have tracking pixels
        assert result['has_tracking_pixels'].iloc[2] == False, "Normal image should not be flagged"
        assert result['has_tracking_pixels'].iloc[3] == False, "Plain text should not have tracking pixels"
    
    def test_link_counting(self):
        """Test that external links are properly counted."""
        test_data = {
            'text_content': [
                '<a href="https://example.com">Link 1</a><a href="https://test.org">Link 2</a>',
                '<a href="mailto:test@example.com">Email link</a><a href="/relative/path">Relative link</a>',
                '<a href="https://external.com">External</a><a href="https://another.com">Another</a><a href="https://third.com">Third</a>',
                'No links here'
            ],
            'subject': [
                'Email with external links',
                'Email with mixed links',
                'Email with many external links',
                'Email without links'
            ]
        }
        
        df = pd.DataFrame(test_data)
        result = add_content_metrics_to_dataframe(df, show_progress=False)
        
        # Check external link counts
        assert result['external_link_count'].iloc[0] == 2, "Should count 2 external links"
        assert result['external_link_count'].iloc[1] == 0, "Should not count mailto or relative links"
        assert result['external_link_count'].iloc[2] == 3, "Should count 3 external links"
        assert result['external_link_count'].iloc[3] == 0, "Should count 0 external links"
    
    def test_image_counting(self):
        """Test that images are properly counted."""
        test_data = {
            'text_content': [
                '<img src="image1.jpg"><img src="image2.png"><img src="image3.gif">',
                '<img src="single-image.jpg" alt="Test">',
                '<div>No images here</div>',
                'Plain text content'
            ],
            'subject': [
                'Email with multiple images',
                'Email with single image',
                'Email without images',
                'Plain text email'
            ]
        }
        
        df = pd.DataFrame(test_data)
        result = add_content_metrics_to_dataframe(df, show_progress=False)
        
        # Check image counts
        assert result['image_count'].iloc[0] == 3, "Should count 3 images"
        assert result['image_count'].iloc[1] == 1, "Should count 1 image"
        assert result['image_count'].iloc[2] == 0, "Should count 0 images"
        assert result['image_count'].iloc[3] == 0, "Should count 0 images"
    
    def test_html_to_text_ratio(self):
        """Test that HTML to text ratio is calculated correctly."""
        test_data = {
            'text_content': [
                '<html><body><p>Short text</p></body></html>',  # More HTML than text
                '<p>This is a longer text content with more words</p>',  # More text than HTML
                'This is plain text without any HTML tags at all',  # No HTML
                '<div><span><p><strong>Very</strong> <em>nested</em> <a href="#">HTML</a></p></span></div>'  # Lots of HTML
            ],
            'subject': [
                'HTML heavy email',
                'Text heavy email',
                'Plain text email',
                'Complex HTML email'
            ]
        }
        
        df = pd.DataFrame(test_data)
        result = add_content_metrics_to_dataframe(df, show_progress=False)
        
        # Check that ratios are calculated (not zero for HTML emails)
        assert result['html_to_text_ratio'].iloc[0] > 0, "HTML heavy email should have ratio > 0"
        assert result['html_to_text_ratio'].iloc[1] > 0, "Text heavy email should have ratio > 0"
        assert result['html_to_text_ratio'].iloc[2] == 0.0, "Plain text should have ratio = 0"
        assert result['html_to_text_ratio'].iloc[3] > 0, "Complex HTML should have ratio > 0"
    
    def test_link_to_text_ratio(self):
        """Test that link to text ratio is calculated correctly."""
        test_data = {
            'text_content': [
                '<a href="https://example.com">Link</a> Short text',  # 1 link, few words
                'This is a much longer text content with many more words and <a href="https://test.com">one link</a>',  # 1 link, many words
                '<a href="https://link1.com">Link 1</a><a href="https://link2.com">Link 2</a><a href="https://link3.com">Link 3</a> Short text',  # 3 links, few words
                'No links in this text content at all'  # No links
            ],
            'subject': [
                'Email with high link ratio',
                'Email with low link ratio',
                'Email with very high link ratio',
                'Email without links'
            ]
        }
        
        df = pd.DataFrame(test_data)
        result = add_content_metrics_to_dataframe(df, show_progress=False)
        
        # Check that ratios are calculated correctly
        assert result['link_to_text_ratio'].iloc[0] > 0, "Should have link ratio > 0"
        assert result['link_to_text_ratio'].iloc[1] > 0, "Should have link ratio > 0"
        assert result['link_to_text_ratio'].iloc[2] > result['link_to_text_ratio'].iloc[1], "More links should have higher ratio"
        assert result['link_to_text_ratio'].iloc[3] == 0.0, "No links should have ratio = 0"


def test_metrics_processor_import():
    """Test that the metrics processor can be imported and used."""
    from gmaildr.analysis.metrics_processor import add_content_metrics_to_dataframe
    
    # Test that function exists and is callable
    assert callable(add_content_metrics_to_dataframe)
    
    # Test with minimal data
    df = pd.DataFrame({'text_content': ['Test'], 'subject': ['Test']})
    result = add_content_metrics_to_dataframe(df, show_progress=False)
    
    # Check that all expected columns are present
    expected_columns = [
        'has_unsubscribe_link', 'has_marketing_language', 'has_legal_disclaimer',
        'has_promotional_content', 'has_tracking_pixels', 'has_bulk_email_indicators',
        'external_link_count', 'image_count', 'exclamation_count', 'caps_word_count',
        'html_to_text_ratio', 'link_to_text_ratio', 'caps_ratio', 'promotional_word_ratio'
    ]
    
    for col in expected_columns:
        assert col in result.columns, f"Expected column {col} not found in result"
