"""
Tests for parallel metrics processing functionality.

Tests that the parallel version of metrics processing works correctly
and provides performance improvements over the sequential version.
"""

import pytest
import pandas as pd
import time
from gmaildr.analysis.metrics_processor import (
    add_content_metrics_to_dataframe_parallel,
    _analyze_single_email
)


class TestParallelMetrics:
    """Test parallel metrics processing functionality."""
    
    def test_parallel_metrics_basic_functionality(self):
        """Test that parallel metrics processing works correctly."""
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
        result = add_content_metrics_to_dataframe_parallel(df, show_progress=False)
        
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
    
    def test_single_email_analysis(self):
        """Test that single email analysis function works correctly."""
        email_data = {
            'text_content': '<html><body><img src="test.jpg"><a href="https://example.com">Link</a></body></html>',
            'subject': 'Test Email'
        }
        
        result = _analyze_single_email(email_data)
        
        # Check that all expected metrics are present
        expected_metrics = [
            'has_tracking_pixels', 'external_link_count', 'image_count', 
            'html_to_text_ratio', 'link_to_text_ratio'
        ]
        
        for metric in expected_metrics:
            assert metric in result, f"Expected metric {metric} not found in result"
        
        # Check that metrics are calculated correctly
        assert result['external_link_count'] > 0, "Should count external links"
        assert result['image_count'] > 0, "Should count images"
        assert result['html_to_text_ratio'] > 0, "Should calculate HTML ratio"
    
    def test_parallel_metrics_with_custom_columns(self):
        """Test parallel metrics with custom column names."""
        test_data = {
            'body': [
                '<html><body><img src="test.jpg"></body></html>',
                'Plain text content'
            ],
            'title': [
                'Test Email',
                'Another Email'
            ]
        }
        
        df = pd.DataFrame(test_data)
        result = add_content_metrics_to_dataframe_parallel(
            df=df,
            text_column='body',
            subject_column='title',
            show_progress=False
        )
        
        # Check that metrics are calculated
        assert result['image_count'].iloc[0] > 0, "Should count images with custom column names"
        assert result['image_count'].iloc[1] == 0, "Plain text should have zero images"
    
    def test_parallel_metrics_performance(self):
        """Test that parallel processing provides performance benefits."""
        # Create larger dataset for performance testing
        test_data = {
            'text_content': [
                '<html><body><img src="test.jpg"><a href="https://example.com">Link</a></body></html>'
            ] * 50,  # 50 identical emails
            'subject': ['Test Email'] * 50
        }
        
        df = pd.DataFrame(test_data)
        
        # Test with different worker counts
        start_time = time.time()
        result_1 = add_content_metrics_to_dataframe_parallel(
            df=df, 
            max_workers=1, 
            show_progress=False
        )
        time_1_worker = time.time() - start_time
        
        start_time = time.time()
        result_2 = add_content_metrics_to_dataframe_parallel(
            df=df, 
            max_workers=2, 
            show_progress=False
        )
        time_2_workers = time.time() - start_time
        
        # Results should be identical
        pd.testing.assert_frame_equal(result_1, result_2)
        
        # Performance should be better with more workers (though not guaranteed due to overhead)
        print(f"1 worker: {time_1_worker:.3f}s, 2 workers: {time_2_workers:.3f}s")
    
    def test_parallel_metrics_edge_cases(self):
        """Test parallel metrics with edge cases."""
        # Empty DataFrame
        empty_df = pd.DataFrame()
        result_empty = add_content_metrics_to_dataframe_parallel(empty_df, show_progress=False)
        assert len(result_empty) == 0, "Empty DataFrame should return empty result"
        
        # DataFrame with missing columns
        missing_cols_df = pd.DataFrame({'other_column': ['test']})
        result_missing = add_content_metrics_to_dataframe_parallel(missing_cols_df, show_progress=False)
        assert len(result_missing) == 1, "Should handle missing columns gracefully"
        
        # DataFrame with NaN values
        nan_df = pd.DataFrame({
            'text_content': ['<html>test</html>', None, ''],
            'subject': ['Test', None, '']
        })
        result_nan = add_content_metrics_to_dataframe_parallel(nan_df, show_progress=False)
        assert len(result_nan) == 3, "Should handle NaN values gracefully"


def test_parallel_metrics_import():
    """Test that parallel metrics functions can be imported."""
    from gmaildr.analysis.metrics_processor import add_content_metrics_to_dataframe_parallel, _analyze_single_email
    
    # Test that functions exist and are callable
    assert callable(add_content_metrics_to_dataframe_parallel)
    assert callable(_analyze_single_email)
    
    # Test with minimal data
    df = pd.DataFrame({'text_content': ['Test'], 'subject': ['Test']})
    result = add_content_metrics_to_dataframe_parallel(df, show_progress=False)
    
    # Check that all expected columns are present
    expected_columns = [
        'has_unsubscribe_link', 'has_marketing_language', 'has_legal_disclaimer',
        'has_promotional_content', 'has_tracking_pixels', 'has_bulk_email_indicators',
        'external_link_count', 'image_count', 'exclamation_count', 'caps_word_count',
        'html_to_text_ratio', 'link_to_text_ratio', 'caps_ratio', 'promotional_word_ratio'
    ]
    
    for col in expected_columns:
        assert col in result.columns, f"Expected column {col} not found in result"
