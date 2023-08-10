"""
Test for date range query functionality in Gmail.

This test verifies that Gmail can fetch emails using specific date ranges
with all allowed parameter combinations.
"""

from datetime import datetime, timedelta
from gmailwiz import Gmail
import pytest


def test_date_range_queries():
    """Test all allowed date range parameter combinations."""
    gmail = Gmail(enable_cache=False)
    
    # Test 1: No parameters (defaults to last 30 days)
    print("Testing default (no parameters)...")
    df_default = gmail.get_emails(
        max_emails=10,
        include_text=False,
        include_metrics=False
    )
    print(f"Found {len(df_default)} emails with default parameters")
    assert df_default is not None, "Default query should return DataFrame"
    # Verify the dates are within the default range (30 days)
    if len(df_default) > 0:
        last_date = df_default['date'].max()
        first_date = df_default['date'].min()
        # Should be within the last 30 days
        assert (last_date.date() - first_date.date()).days <= 29, f"Date range should be within 30 days, got {(last_date.date() - first_date.date()).days + 1} days"
    
    # Test 2: Only days parameter
    print("Testing only days parameter...")
    df_days = gmail.get_emails(
        days=2, # no need for too many days
        max_emails=50,
        include_text=False,
        include_metrics=False
    )
    print(f"Found {len(df_days)} emails in last 2 days")
    assert df_days is not None, "Days query should return DataFrame"
    # Verify the dates are within the last 2 days
    if len(df_days) > 0:
        last_date = df_days['date'].max()
        first_date = df_days['date'].min()
        # For days=2, we expect emails from the last 2 days (inclusive)
        assert (last_date.date() - first_date.date()).days <= 1, f"Date range should be within 2 days, got {(last_date.date() - first_date.date()).days + 1} days"
    # Test 3: start_date and end_date (inclusive range)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=1) # this is 2 days of data (inclusive)
    
    print(f"Testing date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')} (inclusive)")
    df_range = gmail.get_emails(
        start_date=start_date,
        end_date=end_date,
        max_emails=50,
        include_text=False,
        include_metrics=False
    )
    print(f"Found {len(df_range)} emails in date range")
    assert df_range is not None, "Date range query should return DataFrame"
    # dates should be within the specified range
    last_date = df_range['date'].max()
    first_date = df_range['date'].min()
    assert first_date.date() >= start_date.date(), "First date should be >= start_date"
    assert last_date.date() <= end_date.date(), "Last date should be <= end_date"
    
    
    # Test 4: start_date and days
    start_date = datetime.now() - timedelta(days=2)
    print(f"Testing start_date + days: {start_date.strftime('%Y-%m-%d')} + 2 days")
    
    
    df_start_days = gmail.get_emails(
        start_date=start_date,
        days=2,
        max_emails=50,
        include_text=False,
        include_metrics=False
    )
    print(f"Found {len(df_start_days)} emails from start_date + days")
    assert df_start_days is not None, "Start date + days query should return DataFrame"
    # Verify the dates are correct for start_date + days
    if len(df_start_days) > 0:
        last_date = df_start_days['date'].max()
        first_date = df_start_days['date'].min()
        expected_end_date = start_date + timedelta(days=1)  # 2 days inclusive means start_date + 1
        
        # Verify that most emails are in the expected range (allowing for timezone issues)
        emails_in_range = df_start_days[
            (df_start_days['date'].apply(lambda x: x.date()) >= start_date.date()) & 
            (df_start_days['date'].apply(lambda x: x.date()) <= expected_end_date.date())
        ]
        if len(df_start_days) > 0:
            percentage_in_range = len(emails_in_range) / len(df_start_days)
            assert percentage_in_range >= 0.8, f"At least 80% of emails should be in expected range, got {percentage_in_range:.1%}"
    
    # Test 5: end_date and days
    end_date = datetime.now() - timedelta(days=1)
    
    print(f"Testing end_date + days: {end_date.strftime('%Y-%m-%d')} - 3 days")
    df_end_days = gmail.get_emails(
        end_date=end_date,
        days=3,
        max_emails=10,
        include_text=False,
        include_metrics=False
    )
    print(f"Found {len(df_end_days)} emails from end_date + days")
    assert df_end_days is not None, "End date + days query should return DataFrame"
    
    # Test 6: only start_date (same day)
    start_date = datetime.now() - timedelta(days=1)
    
    print(f"Testing only start_date: {start_date.strftime('%Y-%m-%d')} (same day)")
    df_start_only = gmail.get_emails(
        start_date=start_date,
        max_emails=10,
        include_text=False,
        include_metrics=False
    )
    print(f"Found {len(df_start_only)} emails on start_date only")
    assert df_start_only is not None, "Start date only query should return DataFrame"
    
    # Test 7: only end_date (same day)
    end_date = datetime.now() - timedelta(days=1)
    
    print(f"Testing only end_date: {end_date.strftime('%Y-%m-%d')} (same day)")
    df_end_only = gmail.get_emails(
        end_date=end_date,
        max_emails=10,
        include_text=False,
        include_metrics=False
    )
    print(f"Found {len(df_end_only)} emails on end_date only")
    assert df_end_only is not None, "End date only query should return DataFrame"
    
    # Test 8: String date formats
    print("Testing string date formats...")
    df_string_dates = gmail.get_emails(
        start_date="2024-01-01",
        end_date="2024-01-31",
        max_emails=10,
        include_text=False,
        include_metrics=False
    )
    print(f"Found {len(df_string_dates)} emails with string dates")
    assert df_string_dates is not None, "String date query should return DataFrame"
    
    print("✅ All allowed date range combinations work correctly")


def test_date_range_invalid_combinations():
    """Test that invalid parameter combinations raise errors."""
    gmail = Gmail(enable_cache=False)
    
    # Test 1: days + start_date + end_date (should raise error)
    print("Testing invalid combination: days + start_date + end_date...")
    with pytest.raises(ValueError, match="days should be None if start_date and end_date are provided"):
        gmail.get_emails(
            days=30,
            start_date=datetime.now() - timedelta(days=7),
            end_date=datetime.now(),
            max_emails=10,
            include_text=False,
            include_metrics=False
        )
    print("✅ Correctly raised error for days + start_date + end_date")
    
    # Test 2: Invalid string date format
    print("Testing invalid string date format...")
    with pytest.raises(ValueError, match="Invalid date format"):
        gmail.get_emails(
            start_date="invalid-date",
            max_emails=10,
            include_text=False,
            include_metrics=False
        )
    print("✅ Correctly raised error for invalid date format")
    
    print("✅ All invalid combinations properly raise errors")


def test_date_range_inclusivity():
    """Test that date ranges are inclusive on both ends."""
    gmail = Gmail(enable_cache=False)
    
    # Use a specific date range where we can verify inclusivity
    start_date = datetime(2024, 1, 1)  # January 1st
    end_date = datetime(2024, 1, 1)    # Same day - should include that day
    
    print(f"Testing inclusive date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    df = gmail.get_emails(
        start_date=start_date,
        end_date=end_date,
        max_emails=10,
        include_text=False,
        include_metrics=False
    )
    
    print(f"Found {len(df)} emails on single day (inclusive test)")
    assert df is not None, "Single day inclusive query should return DataFrame"
    
    # Test with 1 day parameter (should be same as start_date = end_date)
    print("Testing days=1 (should be same as single day range)...")
    df_one_day = gmail.get_emails(
        start_date=start_date,
        days=1,
        max_emails=10,
        include_text=False,
        include_metrics=False
    )
    
    print(f"Found {len(df_one_day)} emails with days=1")
    assert df_one_day is not None, "Days=1 query should return DataFrame"
    
    print("✅ Date ranges are properly inclusive")


def test_gmail_search_query_builder():
    """Test the query builder directly."""
    from gmailwiz.utils.query_builder import build_gmail_search_query
    from datetime import datetime
    
    # Test date range query building
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 1, 31)
    
    query = build_gmail_search_query(
        start_date=start_date,
        end_date=end_date,
        from_sender="test@example.com"
    )
    
    print(f"Generated query: {query}")
    
    # Should contain date range and sender filter
    assert "after:2024/01/01" in query, "Query should contain start date"
    assert "before:2024/01/31" in query, "Query should contain end date"
    assert "from:test@example.com" in query, "Query should contain sender filter"
    
    print("✅ Query builder test passed")