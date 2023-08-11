"""
Test for date utility functions.

This test verifies that the parse_date_range function correctly handles
all valid combinations of days, start_date, and end_date parameters.
"""

from datetime import datetime, timedelta
from gmaildr.utils.date_utils import parse_date_range


def test_parse_date_range_all_none():
    """Test when all parameters are None (default to last 30 days)."""
    result = parse_date_range()
    start_date = result['start_date']
    end_date = result['end_date']
    
    # Should default to last 30 days
    expected_end = datetime.now()
    expected_num_days = 30
    
    # Allow 1 second tolerance for timing
    assert abs((end_date - expected_end).total_seconds()) < 1
    
    # count number of days between start_date and end_date
    num_days = (end_date - start_date).days + 1
    assert num_days == expected_num_days


def test_parse_date_range_days_only():
    """Test when only days parameter is provided."""
    result = parse_date_range(days=7)
    start_date = result['start_date']
    end_date = result['end_date']
    
    expected_end = datetime.now()
    expected_start = expected_end - timedelta(days=6)  # days=7 means 7 days inclusive, so 6 days back
    
    assert abs((end_date - expected_end).total_seconds()) < 1  # type: ignore
    assert abs((start_date - expected_start).total_seconds()) < 1  # type: ignore


def test_parse_date_range_start_date_only():
    """Test when only start_date is provided (same day)."""
    test_date = datetime(2024, 1, 15)
    result = parse_date_range(start_date=test_date)
    start_date = result['start_date']
    end_date = result['end_date']
    
    assert start_date == test_date
    assert end_date == test_date

def test_parse_date_range_start_date_str_only():
    """Test when only start_date is provided (same day)."""
    test_date = "2024-01-15"
    result = parse_date_range(start_date=test_date)
    start_date = result['start_date']
    end_date = result['end_date']
    
    expected_date = datetime(2024, 1, 15)
    assert start_date == expected_date
    assert end_date == expected_date

def test_parse_date_range_end_date_only():
    """Test when only end_date is provided (same day)."""
    test_date = datetime(2024, 1, 15)
    result = parse_date_range(end_date=test_date)
    start_date = result['start_date']
    end_date = result['end_date']
    
    assert start_date == test_date
    assert end_date == test_date

def test_parse_date_range_end_date_str_only():
    """Test when only end_date is provided (same day)."""
    test_date = "2024-01-15"
    result = parse_date_range(end_date=test_date)
    start_date = result['start_date']
    end_date = result['end_date']
    
    expected_date = datetime(2024, 1, 15)
    assert start_date == expected_date
    assert end_date == expected_date


def test_parse_date_range_both_dates():
    """Test when both start_date and end_date are provided."""
    start = datetime(2024, 1, 1)
    end = datetime(2024, 1, 31)
    
    result = parse_date_range(start_date=start, end_date=end)
    result_start = result['start_date']
    result_end = result['end_date']
    
    assert result_start == start
    assert result_end == end

def test_parse_date_range_both_dates_str():
    """Test when both start_date and end_date are provided."""
    start = "2024-01-01"
    end = "2024-01-31"
    
    result = parse_date_range(start_date=start, end_date=end)
    result_start = result['start_date']
    result_end = result['end_date']
    
    expected_start = datetime(2024, 1, 1)
    expected_end = datetime(2024, 1, 31)
    assert result_start == expected_start
    assert result_end == expected_end

def test_parse_date_range_start_date_and_days():
    """Test when start_date and days are provided."""
    start = datetime(2024, 1, 1)
    days = 7
    
    result = parse_date_range(start_date=start, days=days)
    result_start = result['start_date']
    result_end = result['end_date']
    
    assert result_start == start
    assert result_end == start + timedelta(days=days - 1)


def test_parse_date_range_end_date_and_days():
    """Test when end_date and days are provided."""
    end = datetime(2024, 1, 31)
    days = 7
    
    result = parse_date_range(end_date=end, days=days)
    result_start = result['start_date']
    result_end = result['end_date']
    
    assert result_end == end
    assert result_start == end - timedelta(days=days - 1)


def test_parse_date_range_string_dates():
    """Test with string date inputs."""
    result = parse_date_range(
        start_date="2024-01-01",
        end_date="2024-01-31"
    )
    start_date = result['start_date']
    end_date = result['end_date']
    
    expected_start = datetime(2024, 1, 1)
    expected_end = datetime(2024, 1, 31)
    
    assert start_date == expected_start
    assert end_date == expected_end


def test_parse_date_range_mixed_types():
    """Test with mixed datetime and string inputs."""
    result = parse_date_range(
        start_date=datetime(2024, 1, 1),
        end_date="2024-01-31"
    )
    start_date = result['start_date']
    end_date = result['end_date']
    
    expected_start = datetime(2024, 1, 1)
    expected_end = datetime(2024, 1, 31)
    
    assert start_date == expected_start
    assert end_date == expected_end


def test_parse_date_range_reversed_dates():
    """Test when start_date is after end_date (should swap them)."""
    result = parse_date_range(
        start_date=datetime(2024, 1, 31),
        end_date=datetime(2024, 1, 1)
    )
    start_date = result['start_date']
    end_date = result['end_date']
    
    expected_start = datetime(2024, 1, 1)
    expected_end = datetime(2024, 1, 31)
    
    assert start_date == expected_start
    assert end_date == expected_end


def test_parse_date_range_invalid_combination():
    """Test that invalid combinations raise ValueError."""
    import pytest
    
    # All three parameters provided
    with pytest.raises(ValueError, match="days should be None if start_date and end_date are provided"):
        parse_date_range(
            days=7,
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 31)
        )


def test_parse_date_range_invalid_string_format():
    """Test that invalid string date formats raise ValueError."""
    import pytest
    
    with pytest.raises(ValueError, match="Invalid date format"):
        parse_date_range(start_date="invalid-date")


def test_parse_date_range_invalid_type():
    """Test that invalid date types raise ValueError."""
    import pytest
    
    with pytest.raises(ValueError, match="Invalid date type"):
        parse_date_range(start_date=123)  # type: ignore # int instead of datetime or str
