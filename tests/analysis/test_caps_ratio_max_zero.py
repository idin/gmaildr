"""
Tests for caps_ratio variation across emails.

This module contains tests to ensure that caps_ratio shows meaningful variation
across different emails and is not always zero.
"""

import pandas as pd
from gmaildr.analysis.metrics_processor import add_content_metrics_to_dataframe


def test_caps_ratio_not_zero_for_all_emails():
    """Test that caps_ratio is not zero for all emails in a dataset."""
    # Create test data with mixed content - some with caps, some without
    test_data = {
        'subject': ['URGENT: Meeting Tomorrow', 'Hello world', 'IMPORTANT UPDATE', 'Regular subject'],
        'snippet': ['This is an URGENT message', 'Normal text here', 'CRITICAL information needed', 'Regular snippet'],
        'text_content': ['URGENT meeting at 3 PM', 'Regular email content', 'IMPORTANT: Please respond', 'Normal content']
    }
    
    df = pd.DataFrame(test_data)
    
    # Add metrics
    result_df = add_content_metrics_to_dataframe(df)
    
    # Check if caps_ratio column exists
    assert 'caps_ratio' in result_df.columns, "caps_ratio column should exist"
    
    # Check that caps_ratio is not zero for all emails
    caps_ratios = result_df['caps_ratio'].dropna()
    assert len(caps_ratios) > 0, "Should have some caps_ratio values"
    
    # Check that at least some emails have caps_ratio > 0
    max_caps_ratio = caps_ratios.max()
    assert max_caps_ratio > 0, f"caps_ratio should be greater than 0 for some emails, got max {max_caps_ratio}"
    assert max_caps_ratio < 1, f"caps_ratio should be less than 1, got max {max_caps_ratio}"
    
    # Check that we have variation (not all the same value)
    unique_ratios = caps_ratios.unique()
    assert len(unique_ratios) > 1, f"Should have variation in caps_ratio values, got only {unique_ratios}"


def test_caps_ratio_variation_with_realistic_data():
    """Test caps_ratio variation with more realistic email data."""
    # Create test data simulating real emails with various caps usage
    test_data = {
        'subject': [
            'Meeting tomorrow',  # No caps
            'URGENT: System Down',  # Some caps
            'Hello from Marketing',  # No caps
            'CRITICAL ALERT',  # All caps
            'Weekly Report',  # Some caps
            'normal subject'  # No caps
        ],
        'snippet': [
            'Regular meeting reminder',
            'URGENT system issue detected',
            'Marketing newsletter content',
            'CRITICAL system failure',
            'Weekly performance report',
            'Normal email content'
        ],
        'text_content': [
            'Please attend the meeting tomorrow.',
            'URGENT: The system is down and needs immediate attention.',
            'Here is our latest marketing newsletter.',
            'CRITICAL: System failure detected. Immediate action required.',
            'Weekly report attached for your review.',
            'This is a normal email with regular content.'
        ]
    }
    
    df = pd.DataFrame(test_data)
    
    # Add metrics
    result_df = add_content_metrics_to_dataframe(df)
    
    # Check caps_ratio variation
    caps_ratios = result_df['caps_ratio'].dropna()
    assert len(caps_ratios) > 0, "Should have caps_ratio values"
    
    # Should have some emails with caps_ratio > 0
    max_caps_ratio = caps_ratios.max()
    assert max_caps_ratio > 0, f"Should have some emails with caps_ratio > 0, got max {max_caps_ratio}"
    
    # Should have some emails with caps_ratio = 0
    min_caps_ratio = caps_ratios.min()
    assert min_caps_ratio == 0, f"Should have some emails with caps_ratio = 0, got min {min_caps_ratio}"
    
    # Should have variation
    unique_ratios = caps_ratios.unique()
    assert len(unique_ratios) > 1, f"Should have variation in caps_ratio, got only {unique_ratios}"


if __name__ == '__main__':
    print("🧪 Testing caps_ratio variation across emails...")
    
    # Run all tests
    test_caps_ratio_not_zero_for_all_emails()
    test_caps_ratio_variation_with_realistic_data()
    
    print("🎉 All caps_ratio variation tests passed!")
