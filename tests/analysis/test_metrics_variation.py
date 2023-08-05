"""
Test that numeric metrics have meaningful variation.

This test ensures that when we analyze emails, the metrics show actual variation
rather than being all zeros or identical values, which would indicate a problem.
"""

import pandas as pd
import numpy as np
from gmailwiz import Gmail


def test_metrics_have_variation():
    """Test that numeric metrics show meaningful variation across emails."""
    
    gmail = Gmail()
    
    # Get emails with metrics (use fewer days to avoid performance issues)
    df = gmail.get_emails(
        days=3, 
        use_batch=True, 
        include_text=True, 
        include_metrics=True
    )
    
    if df.empty:
        print("⚠️  No emails found for testing")
        return
    
    print(f"📧 Analyzing {len(df)} emails for metric variation...")
    
    # Define numeric metric columns to check
    numeric_metrics = [
        'exclamation_count', 'caps_word_count', 'caps_ratio', 
        'promotional_word_ratio', 'external_link_count', 'image_count',
        'html_to_text_ratio', 'link_to_text_ratio', 'automated_email_score'
    ]
    
    # Filter to only include metrics that exist in the dataframe
    available_metrics = [col for col in numeric_metrics if col in df.columns]
    
    if not available_metrics:
        print("⚠️  No numeric metrics found in dataframe")
        return
    
    print(f"📊 Checking {len(available_metrics)} numeric metrics...")
    
    # Check each metric for variation
    problematic_metrics = []
    
    for metric in available_metrics:
        values = df[metric].dropna()  # Remove NaN values
        
        if len(values) == 0:
            problematic_metrics.append(f"{metric}: all NaN values")
            continue
            
        min_val = values.min()
        max_val = values.max()
        
        print(f"   {metric}: min={min_val:.4f}, max={max_val:.4f}")
        
        # Check for problematic patterns
        if min_val == 0 and max_val == 0:
            # Special case for caps_word_count and caps_ratio - it's okay if there are no ALL CAPS words
            if metric in ['caps_word_count', 'caps_ratio']:
                print(f"   ⚠️  {metric}: no ALL CAPS words found (this is acceptable)")
            else:
                problematic_metrics.append(f"{metric}: all values are 0")
        elif min_val == max_val:
            # Special case for caps_ratio - it's okay if it's all zeros when no caps words
            if metric == 'caps_ratio' and min_val == 0:
                print(f"   ⚠️  {metric}: all values are 0 (no caps words found)")
            elif metric == 'caps_word_count' and min_val == 0:
                print(f"   ⚠️  {metric}: all values are 0 (no caps words found)")
            else:
                problematic_metrics.append(f"{metric}: all values are identical ({min_val})")
        elif max_val - min_val < 0.001:  # Very small variation
            problematic_metrics.append(f"{metric}: very small variation ({max_val - min_val:.6f})")
    
    # Report results
    if problematic_metrics:
        print(f"\n❌ Found {len(problematic_metrics)} problematic metrics:")
        for problem in problematic_metrics:
            print(f"   - {problem}")
        raise ValueError(f"Metrics lack meaningful variation: {', '.join(problematic_metrics)}")
    else:
        print(f"\n✅ All {len(available_metrics)} metrics show meaningful variation!")
        
        # Show some statistics
        print(f"\n📈 Metric Statistics Summary:")
        for metric in available_metrics:
            values = df[metric].dropna()
            if len(values) > 0:
                mean_val = values.mean()
                std_val = values.std()
                print(f"   {metric}: mean={mean_val:.4f}, std={std_val:.4f}")


def test_boolean_metrics_have_variation():
    """Test that boolean metrics show variation (not all True or all False)."""
    
    gmail = Gmail()
    
    # Get emails with metrics (use fewer days to avoid performance issues)
    df = gmail.get_emails(
        days=3, 
        use_batch=True, 
        include_text=True, 
        include_metrics=True
    )
    
    if df.empty:
        print("⚠️  No emails found for testing")
        return
    
    # Define boolean metric columns to check
    boolean_metrics = [
        'has_unsubscribe_link', 'has_marketing_language', 'has_legal_disclaimer',
        'has_bulk_email_indicators', 'has_promotional_content', 'has_tracking_pixels'
    ]
    
    # Filter to only include metrics that exist in the dataframe
    available_metrics = [col for col in boolean_metrics if col in df.columns]
    
    if not available_metrics:
        print("⚠️  No boolean metrics found in dataframe")
        return
    
    print(f"📊 Checking {len(available_metrics)} boolean metrics...")
    
    # Check each metric for variation
    problematic_metrics = []
    
    for metric in available_metrics:
        values = df[metric].dropna()
        
        if len(values) == 0:
            problematic_metrics.append(f"{metric}: all NaN values")
            continue
            
        true_count = values.sum()
        false_count = len(values) - true_count
        
        print(f"   {metric}: True={true_count}, False={false_count}")
        
        # Check for problematic patterns
        if true_count == 0:
            problematic_metrics.append(f"{metric}: all values are False")
        elif false_count == 0:
            problematic_metrics.append(f"{metric}: all values are True")
    
    # Report results
    if problematic_metrics:
        print(f"\n❌ Found {len(problematic_metrics)} problematic boolean metrics:")
        for problem in problematic_metrics:
            print(f"   - {problem}")
        raise ValueError(f"Boolean metrics lack variation: {', '.join(problematic_metrics)}")
    else:
        print(f"\n✅ All {len(available_metrics)} boolean metrics show variation!")


def test_email_type_distribution():
    """Test that email types are distributed across different categories."""
    
    gmail = Gmail()
    
    # Get emails with metrics
    df = gmail.get_emails(
        days=10, 
        use_batch=True, 
        include_text=True, 
        include_metrics=True
    )
    
    if df.empty:
        print("⚠️  No emails found for testing")
        return
    
    if 'email_type' not in df.columns:
        print("⚠️  No email_type column found")
        return
    
    # Check email type distribution
    type_counts = df['email_type'].value_counts()
    total_emails = len(df)
    
    print(f"📧 Email type distribution ({total_emails} total emails):")
    for email_type, count in type_counts.items():
        percentage = (count / total_emails) * 100
        print(f"   {email_type}: {count} ({percentage:.1f}%)")
    
    # Check for problematic distribution
    if len(type_counts) == 1:
        only_type = type_counts.index[0]
        raise ValueError(f"All emails classified as '{only_type}' - classification may be broken")
    
    # Check if any type has too high percentage (suspicious)
    for email_type, count in type_counts.items():
        percentage = (count / total_emails) * 100
        if percentage > 95:
            raise ValueError(f"Too many emails classified as '{email_type}' ({percentage:.1f}%) - classification may be biased")
    
    print(f"✅ Email type distribution looks reasonable!")


if __name__ == "__main__":
    print("🧪 Testing metrics variation...")
    test_metrics_have_variation()
    test_boolean_metrics_have_variation()
    test_email_type_distribution()
    print("🎉 All variation tests passed!")
