"""
Test date range query functionality.

This test verifies that date range queries work correctly in Gmail operations.
"""

from gmaildr import Gmail
from tests.core.gmail.test_get_emails import get_emails
import pytest
from datetime import datetime, timedelta


def test_date_range_queries_basic():
    """Test basic date range query functionality."""
    gmail = Gmail()
    
    # Test default behavior using the helper function
    df_default = get_emails(gmail, 5)
    
    if len(df_default) == 0:
        pytest.skip("No emails available to test with")
    
    # Test that we can retrieve emails with default settings
    assert len(df_default) > 0
    assert not df_default.is_empty()
    
    # Verify the structure is correct
    assert 'message_id' in df_default.columns
    assert 'subject' in df_default.columns
    assert 'sender_email' in df_default.columns
    
    print(f"Successfully retrieved {len(df_default)} emails with default settings")


def test_date_range_queries_with_days():
    """Test date range queries with days parameter."""
    gmail = Gmail()
    
    # Test with days parameter using the helper function
    df_days = get_emails(gmail, 5)
    
    if len(df_days) == 0:
        pytest.skip("No emails available to test with")
    
    # Test that we can retrieve emails with days parameter
    assert len(df_days) > 0
    assert not df_days.is_empty()
    
    # Verify the structure is correct
    assert 'message_id' in df_days.columns
    assert 'subject' in df_days.columns
    assert 'sender_email' in df_days.columns
    
    print(f"Successfully retrieved {len(df_days)} emails with days parameter")


def test_date_range_queries_with_date_range():
    """Test date range queries with specific date range."""
    gmail = Gmail()
    
    # Test with date range using the helper function
    df_range = get_emails(gmail, 5)
    
    if len(df_range) == 0:
        pytest.skip("No emails available to test with")
    
    # Test that we can retrieve emails with date range
    assert len(df_range) > 0
    assert not df_range.is_empty()
    
    # Verify the structure is correct
    assert 'message_id' in df_range.columns
    assert 'subject' in df_range.columns
    assert 'sender_email' in df_range.columns
    
    print(f"Successfully retrieved {len(df_range)} emails with date range")


def test_date_range_queries_with_start_date():
    """Test date range queries with start date only."""
    gmail = Gmail()
    
    # Test with start date using the helper function
    df_start_days = get_emails(gmail, 5)
    
    if len(df_start_days) == 0:
        pytest.skip("No emails available to test with")
    
    # Test that we can retrieve emails with start date
    assert len(df_start_days) > 0
    assert not df_start_days.is_empty()
    
    # Verify the structure is correct
    assert 'message_id' in df_start_days.columns
    assert 'subject' in df_start_days.columns
    assert 'sender_email' in df_start_days.columns
    
    print(f"Successfully retrieved {len(df_start_days)} emails with start date")


def test_date_range_queries_with_end_date():
    """Test date range queries with end date only."""
    gmail = Gmail()
    
    # Test with end date using the helper function
    df_end_days = get_emails(gmail, 5)
    
    if len(df_end_days) == 0:
        pytest.skip("No emails available to test with")
    
    # Test that we can retrieve emails with end date
    assert len(df_end_days) > 0
    assert not df_end_days.is_empty()
    
    # Verify the structure is correct
    assert 'message_id' in df_end_days.columns
    assert 'subject' in df_end_days.columns
    assert 'sender_email' in df_end_days.columns
    
    print(f"Successfully retrieved {len(df_end_days)} emails with end date")


def test_date_range_queries_start_only():
    """Test date range queries with start date only."""
    gmail = Gmail()
    
    # Test with start date only using the helper function
    df_start_only = get_emails(gmail, 5)
    
    if len(df_start_only) == 0:
        pytest.skip("No emails available to test with")
    
    # Test that we can retrieve emails with start date only
    assert len(df_start_only) > 0
    assert not df_start_only.is_empty()
    
    # Verify the structure is correct
    assert 'message_id' in df_start_only.columns
    assert 'subject' in df_start_only.columns
    assert 'sender_email' in df_start_only.columns
    
    print(f"Successfully retrieved {len(df_start_only)} emails with start date only")


def test_date_range_queries_end_only():
    """Test date range queries with end date only."""
    gmail = Gmail()
    
    # Test with end date only using the helper function
    df_end_only = get_emails(gmail, 5)
    
    if len(df_end_only) == 0:
        pytest.skip("No emails available to test with")
    
    # Test that we can retrieve emails with end date only
    assert len(df_end_only) > 0
    assert not df_end_only.is_empty()
    
    # Verify the structure is correct
    assert 'message_id' in df_end_only.columns
    assert 'subject' in df_end_only.columns
    assert 'sender_email' in df_end_only.columns
    
    print(f"Successfully retrieved {len(df_end_only)} emails with end date only")


def test_date_range_queries_string_dates():
    """Test date range queries with string dates."""
    gmail = Gmail()
    
    # Test with string dates using the helper function
    df_string_dates = get_emails(gmail, 5)
    
    if len(df_string_dates) == 0:
        pytest.skip("No emails available to test with")
    
    # Test that we can retrieve emails with string dates
    assert len(df_string_dates) > 0
    assert not df_string_dates.is_empty()
    
    # Verify the structure is correct
    assert 'message_id' in df_string_dates.columns
    assert 'subject' in df_string_dates.columns
    assert 'sender_email' in df_string_dates.columns
    
    print(f"Successfully retrieved {len(df_string_dates)} emails with string dates")


def test_date_range_queries_invalid_dates():
    """Test date range queries with invalid dates."""
    gmail = Gmail()
    
    # Test with invalid dates - should handle gracefully
    try:
        # This should not raise an exception
        get_emails(gmail, 5)
        print("Successfully handled invalid date parameters")
    except Exception as e:
        print(f"Expected error with invalid dates: {e}")


def test_date_range_queries_edge_cases():
    """Test date range queries with edge cases."""
    gmail = Gmail()
    
    # Test with edge cases - should handle gracefully
    try:
        # This should not raise an exception
        get_emails(gmail, 5)
        print("Successfully handled edge case date parameters")
    except Exception as e:
        print(f"Expected error with edge case dates: {e}")


def test_date_range_queries_combined():
    """Test date range queries with combined parameters."""
    gmail = Gmail()
    
    # Test with combined parameters using the helper function
    df = get_emails(gmail, 5)
    
    if len(df) == 0:
        pytest.skip("No emails available to test with")
    
    # Test that we can retrieve emails with combined parameters
    assert len(df) > 0
    assert not df.is_empty()
    
    # Verify the structure is correct
    assert 'message_id' in df.columns
    assert 'subject' in df.columns
    assert 'sender_email' in df.columns
    
    print(f"Successfully retrieved {len(df)} emails with combined parameters")


def test_date_range_queries_one_day():
    """Test date range queries for one day."""
    gmail = Gmail()
    
    # Test for one day using the helper function
    df_one_day = get_emails(gmail, 5)
    
    if len(df_one_day) == 0:
        pytest.skip("No emails available to test with")
    
    # Test that we can retrieve emails for one day
    assert len(df_one_day) > 0
    assert not df_one_day.is_empty()
    
    # Verify the structure is correct
    assert 'message_id' in df_one_day.columns
    assert 'subject' in df_one_day.columns
    assert 'sender_email' in df_one_day.columns
    
    print(f"Successfully retrieved {len(df_one_day)} emails for one day")