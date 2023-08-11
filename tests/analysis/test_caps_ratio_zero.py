"""
Test to check if caps_ratio is always zero.
"""

import pandas as pd
from gmaildr.analysis.metrics_processor import add_content_metrics_to_dataframe


def test_caps_ratio_not_always_zero():
    """Test that caps_ratio is not always zero with text containing caps."""
    # Create test data with ALL CAPS words
    test_data = {
        'subject': ['URGENT: Meeting Tomorrow', 'Hello World', 'IMPORTANT UPDATE'],
        'snippet': ['This is an URGENT message', 'Normal text here', 'CRITICAL information needed'],
        'text_content': ['URGENT meeting at 3 PM', 'Regular email content', 'IMPORTANT: Please respond']
    }
    
    df = pd.DataFrame(test_data)
    
    # Add metrics
    result_df = add_content_metrics_to_dataframe(df)
    
    # Check if caps_ratio column exists
    assert 'caps_ratio' in result_df.columns, "caps_ratio column should exist"
    
    # Check if any caps_ratio values are greater than 0
    caps_ratios = result_df['caps_ratio'].dropna()
    assert len(caps_ratios) > 0, "Should have some caps_ratio values"
    
    # Check if at least one value is greater than 0
    max_caps_ratio = caps_ratios.max()
    assert max_caps_ratio > 0, f"caps_ratio should be greater than 0, got {max_caps_ratio}"
