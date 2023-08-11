"""
Test to check if text fetching is causing performance issues.
"""

import time
from gmaildr import Gmail


def test_text_fetching_performance():
    """Test if text fetching is the performance bottleneck."""
    
    gmail = Gmail()
    
    print("🚀 Starting text fetching performance test...")
    start_time = time.time()
    
    # Test 1: Get emails without text (should be fast)
    print("📧 Getting emails without text...")
    df_no_text = gmail.get_emails(
        days=1, 
        use_batch=True, 
        include_text=False, 
        include_metrics=False
    )
    no_text_time = time.time() - start_time
    print(f"   ⏱️  Time without text: {no_text_time:.2f}s")
    
    # Test 2: Get emails with text (this is where it might get stuck)
    print("📧 Getting emails with text...")
    text_start_time = time.time()
    df_with_text = gmail.get_emails(
        days=1, 
        use_batch=True, 
        include_text=True, 
        include_metrics=False
    )
    text_time = time.time() - text_start_time
    print(f"   ⏱️  Time with text: {text_time:.2f}s")
    
    # Test 3: Get emails with text and metrics (this is where it gets stuck)
    print("📧 Getting emails with text and metrics...")
    metrics_start_time = time.time()
    df_with_metrics = gmail.get_emails(
        days=1, 
        use_batch=True, 
        include_text=True, 
        include_metrics=True
    )
    metrics_time = time.time() - metrics_start_time
    print(f"   ⏱️  Time with metrics: {metrics_time:.2f}s")
    
    total_time = time.time() - start_time
    print(f"\n⏱️  Total test time: {total_time:.2f}s")
    print(f"   Breakdown:")
    print(f"   - No text: {no_text_time:.2f}s")
    print(f"   - With text: {text_time:.2f}s")
    print(f"   - With metrics: {metrics_time:.2f}s")
    
    # Assert that we got results
    assert not df_no_text.empty, "No emails found without text"
    assert not df_with_text.empty, "No emails found with text"
    assert not df_with_metrics.empty, "No emails found with metrics"
    
    print("✅ Performance test completed successfully")
