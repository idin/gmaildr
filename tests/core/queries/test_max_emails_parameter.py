"""
Test that max_emails parameter is properly respected in convenience methods.

This test verifies that when max_emails is specified, it's not overridden
by other parameters like days.
"""

from gmaildr import Gmail


def test_max_emails_respected_in_get_trash_emails():
    """Test that max_emails parameter is respected in get_trash_emails."""
    gmail = Gmail()
    
    # Test with a large days value but small max_emails
    df = gmail.get_trash_emails(
        days=1000,  # Large date range
        max_emails=5,  # Small limit
        include_text=False,
        include_metrics=False,
        use_batch=True
    )
    
    # Should respect max_emails limit
    assert len(df) <= 5, f"Expected max 5 emails, got {len(df)}"
    print(f"✅ get_trash_emails respected max_emails=5: found {len(df)} emails")


def test_max_emails_respected_in_get_inbox_emails():
    """Test that max_emails parameter is respected in get_inbox_emails."""
    gmail = Gmail()
    
    # Test with a large days value but small max_emails
    df = gmail.get_inbox_emails(
        days=1000,  # Large date range
        max_emails=3,  # Small limit
        include_text=False,
        include_metrics=False,
        use_batch=True
    )
    
    # Should respect max_emails limit
    assert len(df) <= 3, f"Expected max 3 emails, got {len(df)}"
    print(f"✅ get_inbox_emails respected max_emails=3: found {len(df)} emails")


def test_max_emails_respected_in_get_archive_emails():
    """Test that max_emails parameter is respected in get_archive_emails."""
    gmail = Gmail()
    
    # Test with a large days value but small max_emails
    df = gmail.get_archive_emails(
        days=1000,  # Large date range
        max_emails=2,  # Small limit
        include_text=False,
        include_metrics=False,
        use_batch=True
    )
    
    # Should respect max_emails limit
    assert len(df) <= 2, f"Expected max 2 emails, got {len(df)}"
    print(f"✅ get_archive_emails respected max_emails=2: found {len(df)} emails")


def test_max_emails_respected_in_get_emails_with_filters():
    """Test that max_emails parameter is respected in get_emails with filters."""
    gmail = Gmail()
    
    # Test with filters and max_emails
    df = gmail.get_emails(
        days=1000,  # Large date range
        max_emails=4,  # Small limit
        in_folder='inbox',  # Filter
        include_text=False,
        include_metrics=False,
        use_batch=True
    )
    
    # Should respect max_emails limit
    assert len(df) <= 4, f"Expected max 4 emails, got {len(df)}"
    print(f"✅ get_emails with filters respected max_emails=4: found {len(df)} emails")


def test_max_emails_none_returns_more_emails():
    """Test that max_emails=None returns more emails than a small limit."""
    gmail = Gmail()
    
    # Get emails with a small limit
    df_limited = gmail.get_inbox_emails(
        days=30,
        max_emails=5,
        include_text=False,
        include_metrics=False,
        use_batch=True
    )
    
    # Get emails with no limit
    df_unlimited = gmail.get_inbox_emails(
        days=30,
        max_emails=None,
        include_text=False,
        include_metrics=False,
        use_batch=True
    )
    
    # If there are more than 5 emails in the last 30 days, the unlimited should return more
    if len(df_unlimited) > 5:
        assert len(df_unlimited) > len(df_limited), f"Unlimited should return more emails than limited"
        print(f"✅ max_emails=None returned more emails ({len(df_unlimited)}) than max_emails=5 ({len(df_limited)})")
    else:
        print(f"⚠️  Only {len(df_unlimited)} emails found in last 30 days, so no difference between limited/unlimited")


def test_max_emails_zero_returns_empty():
    """Test that max_emails=0 returns empty DataFrame."""
    gmail = Gmail()
    
    df = gmail.get_inbox_emails(
        days=30,
        max_emails=0,
        include_text=False,
        include_metrics=False,
        use_batch=True
    )
    
    assert len(df) == 0, f"Expected 0 emails with max_emails=0, got {len(df)}"
    print("✅ max_emails=0 correctly returned empty DataFrame")


if __name__ == "__main__":
    print("🧪 Testing max_emails parameter respect...")
    
    test_max_emails_respected_in_get_trash_emails()
    test_max_emails_respected_in_get_inbox_emails()
    test_max_emails_respected_in_get_archive_emails()
    test_max_emails_respected_in_get_emails_with_filters()
    test_max_emails_none_returns_more_emails()
    test_max_emails_zero_returns_empty()
    
    print("\n✅ All max_emails parameter tests passed!")
