"""
Test NaN handling in metrics processor.

This test captures the bug where text_content can be NaN (float) instead of string,
causing TypeError when using 'in' operator.
"""

import pandas as pd
import pytest
import numpy as np
from gmaildr.analysis.metrics_processor import add_content_metrics_to_dataframe


def test_handle_nan_text_content():
    """Test that NaN text_content values are handled properly."""
    
    # Create test data with NaN values in text_content
    test_data = {
        'message_id': ['msg1', 'msg2', 'msg3', 'msg4'],
        'sender_email': ['test1@example.com', 'test2@example.com', 'test3@example.com', 'test4@example.com'],
        'subject': ['Test Subject 1', 'Test Subject 2', 'Test Subject 3', 'Test Subject 4'],
        'text_content': [
            'This is normal text content',
            np.nan,  # This should cause the bug
            '',  # Empty string
            None  # None value
        ]
    }
    
    df = pd.DataFrame(test_data)
    
    # This should not raise TypeError
    try:
        result_df = add_content_metrics_to_dataframe(
            df=df,
            text_column='text_content',
            subject_column='subject',
            show_progress=False
        )
        
        # Should have processed all rows without error
        assert len(result_df) == 4
        print("✅ Successfully handled NaN text_content values")
        
    except TypeError as e:
        if "argument of type 'float' is not iterable" in str(e):
            pytest.fail(f"Bug detected: {e}")
        else:
            raise


def test_handle_nan_subject():
    """Test that NaN subject values are handled properly."""
    
    # Create test data with NaN values in subject
    test_data = {
        'message_id': ['msg1', 'msg2', 'msg3'],
        'sender_email': ['test1@example.com', 'test2@example.com', 'test3@example.com'],
        'subject': [
            'Normal Subject',
            np.nan,  # NaN subject
            ''  # Empty subject
        ],
        'text_content': [
            'Normal text content',
            'Text with <html> tags',
            'Plain text'
        ]
    }
    
    df = pd.DataFrame(test_data)
    
    # This should not raise TypeError
    try:
        result_df = add_content_metrics_to_dataframe(
            df=df,
            text_column='text_content',
            subject_column='subject',
            show_progress=False
        )
        
        # Should have processed all rows without error
        assert len(result_df) == 3
        print("✅ Successfully handled NaN subject values")
        
    except TypeError as e:
        if "argument of type 'float' is not iterable" in str(e):
            pytest.fail(f"Bug detected: {e}")
        else:
            raise


def test_handle_mixed_nan_values():
    """Test handling of various NaN-like values."""
    
    # Create test data with various problematic values
    test_data = {
        'message_id': ['msg1', 'msg2', 'msg3', 'msg4', 'msg5'],
        'sender_email': ['test@example.com'] * 5,
        'subject': [
            'Normal Subject',
            np.nan,
            None,
            '',
            'Subject with <tags>'
        ],
        'text_content': [
            'Normal text',
            np.nan,
            None,
            '',
            'Text with <html> tags and <more> tags'
        ]
    }
    
    df = pd.DataFrame(test_data)
    
    # This should not raise any errors
    try:
        result_df = add_content_metrics_to_dataframe(
            df=df,
            text_column='text_content',
            subject_column='subject',
            show_progress=False
        )
        
        # Should have processed all rows without error
        assert len(result_df) == 5
        print("✅ Successfully handled all types of NaN-like values")
        
    except Exception as e:
        pytest.fail(f"Unexpected error: {e}")


if __name__ == "__main__":
    print("🧪 Testing NaN handling in metrics processor...")
    test_handle_nan_text_content()
    test_handle_nan_subject()
    test_handle_mixed_nan_values()
    print("🎉 All NaN handling tests passed!")
