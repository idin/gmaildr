"""
Test text content retrieval functionality.

This test ensures that email text content is properly extracted and added to the DataFrame.
"""

import pytest
from gmailwiz import Gmail


def test_text_content_is_retrieved():
    """Test that text content is properly retrieved and added to DataFrame."""
    
    gmail = Gmail()
    
    # Get emails with text content
    df = gmail.get_emails(
        days=1, 
        use_batch=True, 
        include_text=True, 
        include_metrics=False
    )
    
    if df.empty:
        pytest.skip("No emails found for testing")
    
    # Check that text_content column exists
    assert 'text_content' in df.columns, "text_content column should be present"
    
    # Check that text content is not all empty
    text_lengths = df['text_content'].str.len()
    assert text_lengths.max() > 0, "At least one email should have text content"
    
    # Check that we have some non-empty text content
    non_empty_count = df['text_content'].notna().sum()
    assert non_empty_count > 0, "Should have some non-empty text content"
    
    print(f"✅ Text content retrieved successfully")
    print(f"   Total emails: {len(df)}")
    print(f"   Emails with text: {non_empty_count}")
    print(f"   Max text length: {text_lengths.max()}")


def test_text_content_has_meaningful_content():
    """Test that retrieved text content has meaningful content."""
    
    gmail = Gmail()
    
    # Get emails with text content
    df = gmail.get_emails(
        days=1, 
        use_batch=True, 
        include_text=True, 
        include_metrics=False
    )
    
    if df.empty:
        pytest.skip("No emails found for testing")
    
    # Get first email with non-empty text content
    non_empty_emails = df[df['text_content'].notna() & (df['text_content'].str.len() > 0)]
    
    if len(non_empty_emails) == 0:
        pytest.skip("No emails with text content found")
    
    sample_email = non_empty_emails.iloc[0]
    text_content = sample_email['text_content']
    
    # Check that text content has reasonable length
    assert len(text_content) > 50, f"Text content should be longer than 50 chars, got {len(text_content)}"
    
    # Check that text content contains some common words
    common_words = ['the', 'and', 'or', 'in', 'on', 'at', 'to', 'for', 'of', 'with']
    text_lower = text_content.lower()
    found_words = [word for word in common_words if word in text_lower]
    
    assert len(found_words) >= 2, f"Text should contain common words, found: {found_words}"
    
    print(f"✅ Text content has meaningful content")
    print(f"   Text length: {len(text_content)}")
    print(f"   Sample: {text_content[:100]}...")


def test_text_content_with_metrics():
    """Test that text content works properly with metrics calculation."""
    
    gmail = Gmail()
    
    # Get emails with text content and metrics
    df = gmail.get_emails(
        days=1, 
        use_batch=True, 
        include_text=True, 
        include_metrics=True
    )
    
    if df.empty:
        pytest.skip("No emails found for testing")
    
    # Check that text_content column exists
    assert 'text_content' in df.columns, "text_content column should be present"
    
    # Check that metrics columns exist
    expected_metrics = [
        'has_unsubscribe_link', 'has_marketing_language', 'has_legal_disclaimer',
        'has_bulk_email_indicators', 'has_promotional_content', 'exclamation_count',
        'caps_word_count', 'caps_ratio', 'promotional_word_ratio'
    ]
    
    for metric in expected_metrics:
        assert metric in df.columns, f"Metric column {metric} should be present"
    
    # Check that metrics are calculated (not all NaN)
    for metric in expected_metrics:
        if metric in df.columns:
            non_null_count = df[metric].notna().sum()
            assert non_null_count > 0, f"Metric {metric} should have non-null values"
    
    print(f"✅ Text content works with metrics calculation")
    print(f"   Total emails: {len(df)}")
    print(f"   Metrics calculated: {len(expected_metrics)}")


if __name__ == "__main__":
    print("🧪 Testing text content retrieval...")
    test_text_content_is_retrieved()
    test_text_content_has_meaningful_content()
    test_text_content_with_metrics()
    print("🎉 All text content tests passed!")
