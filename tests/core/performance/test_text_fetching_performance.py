"""
Test text fetching performance.

This test measures the performance of different text fetching options.
"""

from gmaildr import Gmail
from gmaildr.test_utils import get_emails
import pytest
import time


def test_text_fetching_performance():
    """Test the performance of different text fetching options."""
    gmail = Gmail()
    
    # Test 1: Get emails without text
    print("📧 Getting emails without text...")
    start_time = time.time()
    df_no_text = get_emails(gmail, 10, include_text=False, include_metrics=False)
    no_text_time = time.time() - start_time
    
    if len(df_no_text) == 0:
        pytest.skip("No emails available to test with")
    
    print(f"✅ Retrieved {len(df_no_text)} emails without text in {no_text_time:.2f}s")
    
    # Test 2: Get emails with text
    print("📧 Getting emails with text...")
    start_time = time.time()
    df_with_text = get_emails(gmail, 10, include_text=True, include_metrics=False)
    with_text_time = time.time() - start_time
    
    print(f"✅ Retrieved {len(df_with_text)} emails with text in {with_text_time:.2f}s")
    
    # Test 3: Get emails with text and metrics
    print("📧 Getting emails with text and metrics...")
    start_time = time.time()
    df_with_metrics = get_emails(gmail, 5, include_text=True, include_metrics=True)
    with_metrics_time = time.time() - start_time
    
    print(f"✅ Retrieved {len(df_with_metrics)} emails with text and metrics in {with_metrics_time:.2f}s")
    
    # Performance analysis
    print("\n📊 Performance Analysis:")
    print(f"📧 Getting emails without text: {no_text_time:.2f}s")
    print(f"📧 Getting emails with text: {with_text_time:.2f}s")
    print(f"📧 Getting emails with text and metrics: {with_metrics_time:.2f}s")
    
    # Verify that all retrievals worked
    assert len(df_no_text) > 0, "Should retrieve emails without text"
    assert len(df_with_text) > 0, "Should retrieve emails with text"
    assert len(df_with_metrics) > 0, "Should retrieve emails with metrics"
    
    # Verify structure
    for df, name in [(df_no_text, "no text"), (df_with_text, "with text"), (df_with_metrics, "with metrics")]:
        assert 'message_id' in df.columns, f"message_id should be in {name} DataFrame"
        assert 'subject' in df.columns, f"subject should be in {name} DataFrame"
        assert 'sender_email' in df.columns, f"sender_email should be in {name} DataFrame"
    
    print("✅ All performance tests completed successfully")
