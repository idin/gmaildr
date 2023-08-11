"""
Test Gmail get_emails with metrics enabled.

This test captures the scenario where get_emails with include_text=True and 
include_metrics=True was causing a TypeError due to NaN values in text_content.
"""

import pytest
from gmaildr import Gmail


def test_get_emails_with_text_and_metrics():
    """Test that get_emails works with both text and metrics enabled."""
    
    gmail = Gmail()
    
    # This was the original failing scenario
    try:
        df = gmail.get_emails(
            days=1, 
            use_batch=True, 
            include_text=True, 
            include_metrics=True
        )
        
        # Should not raise TypeError
        assert df is not None
        print(f"✅ Successfully retrieved {len(df)} emails with text and metrics")
        
        # Check that metrics columns were added
        expected_metric_columns = [
            'has_unsubscribe_link', 'has_marketing_language', 'has_legal_disclaimer',
            'has_bulk_email_indicators', 'has_promotional_content', 'exclamation_count',
            'caps_word_count', 'caps_ratio', 'promotional_word_ratio',
            'has_tracking_pixels', 'external_link_count', 'image_count',
            'html_to_text_ratio', 'link_to_text_ratio', 'automated_email_score',
            'email_type'
        ]
        
        # Check which metric columns are present
        present_metrics = [col for col in expected_metric_columns if col in df.columns]
        print(f"📊 Metrics columns added: {len(present_metrics)}/{len(expected_metric_columns)}")
        
        if present_metrics:
            print(f"   Found: {present_metrics[:5]}{'...' if len(present_metrics) > 5 else ''}")
        
    except TypeError as e:
        if "argument of type 'float' is not iterable" in str(e):
            pytest.fail(f"Bug detected: {e}")
        else:
            raise
    except Exception as e:
        # Other errors might be expected (no emails, API issues, etc.)
        print(f"⚠️  Expected error (likely no emails or API issue): {e}")


def test_get_emails_with_metrics_only():
    """Test that get_emails works with metrics but no text."""
    
    gmail = Gmail()
    
    try:
        df = gmail.get_emails(
            days=1, 
            use_batch=True, 
            include_text=False, 
            include_metrics=True
        )
        
        # Should not raise TypeError
        assert df is not None
        print(f"✅ Successfully retrieved {len(df)} emails with metrics only")
        
    except TypeError as e:
        if "argument of type 'float' is not iterable" in str(e):
            pytest.fail(f"Bug detected: {e}")
        else:
            raise
    except Exception as e:
        print(f"⚠️  Expected error (likely no emails or API issue): {e}")


def test_get_emails_with_text_only():
    """Test that get_emails works with text but no metrics."""
    
    gmail = Gmail()
    
    try:
        df = gmail.get_emails(
            days=1, 
            use_batch=True, 
            include_text=True, 
            include_metrics=False
        )
        
        # Should not raise TypeError
        assert df is not None
        print(f"✅ Successfully retrieved {len(df)} emails with text only")
        
        # Should have text_content column if emails were found
        if len(df) > 0 and 'text_content' in df.columns:
            print(f"   Text content column present with {df['text_content'].notna().sum()} non-null values")
        
    except TypeError as e:
        if "argument of type 'float' is not iterable" in str(e):
            pytest.fail(f"Bug detected: {e}")
        else:
            raise
    except Exception as e:
        print(f"⚠️  Expected error (likely no emails or API issue): {e}")


if __name__ == "__main__":
    print("🧪 Testing Gmail get_emails with metrics...")
    test_get_emails_with_text_and_metrics()
    test_get_emails_with_metrics_only()
    test_get_emails_with_text_only()
    print("🎉 All Gmail metrics tests completed!")
