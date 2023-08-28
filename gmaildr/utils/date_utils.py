"""
Date utilities for Gmail queries.

This module provides functions to handle date range logic for Gmail search queries.
"""

from datetime import date, datetime, timedelta
from typing import Dict, Optional, Union


def parse_date(date_input: Union[datetime, str]) -> datetime:
    """
    Parse date input to datetime object.
    
    Args:
        date_input: Date input as datetime, date, or string in YYYY-MM-DD format
        
    Returns:
        Parsed datetime object
        
    Raises:
        ValueError: If date format is invalid
    """
    if isinstance(date_input, datetime):
        return date_input
    elif isinstance(date_input, date):
        return datetime.combine(date_input, datetime.min.time())
    elif isinstance(date_input, str):
        try:
            return datetime.strptime(date_input, '%Y-%m-%d')
        except ValueError:
            raise ValueError(f"Invalid date format: {date_input}. Use YYYY-MM-DD format.")
    else:
        raise TypeError(f"Invalid date type: {type(date_input)}")

def parse_date_range(
    *,
    days: Optional[int] = None,
    start_date: Optional[Union[datetime, str]] = None,
    end_date: Optional[Union[datetime, str]] = None,
    default_days: int = 30
) -> Dict[str, Union[datetime, int]]:
    """
    Parse date range parameters and return start and end dates.
    
    Acceptable combinations:
    - All None: defaults to last 30 days
    - start_date and end_date: use provided range
    - start_date and days: end_date = start_date + days
    - days and end_date: start_date = end_date - days
    - only start_date: end_date = start_date (same day)
    - only end_date: start_date = end_date (same day)
    
    Args:
        days: Number of days
        start_date: Start date (datetime or string in YYYY-MM-DD format)
        end_date: End date (datetime or string in YYYY-MM-DD format)
        default_days: Default number of days when no parameters provided
        
    Returns:
        Dict with start_date, end_date, and days
        
    Raises:
        ValueError: For invalid combinations or date formats
    """
    # Handle all combinations
    if days is None and start_date is None and end_date is None:
        days = default_days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days - 1)
    
    elif start_date and end_date:
        # Both dates provided
        start_date = parse_date(start_date)
        end_date = parse_date(end_date)
        if days is not None:
            raise ValueError("days should be None if start_date and end_date are provided")
        # we need to calculate days to return at the end
        days = (end_date - start_date).days + 1

    elif start_date and days:
        # Start date + days
        # if 1 day, end_date should be same as start_date
        start_date = parse_date(start_date)
        if days == 1:
            end_date = start_date
        else:
            end_date = start_date + timedelta(days=days - 1)
    
    elif end_date and days:
        # End date + days
        # if 1 day, start_date should be same as end_date
        end_date = parse_date(end_date)
        if days == 1:
            start_date = end_date
        else:
            start_date = end_date - timedelta(days=days - 1)
    
    elif start_date:
        # Only start date
        start_date = parse_date(start_date)
        end_date = start_date
        days = 1
    
    elif end_date:
        # Only end date
        end_date = parse_date(end_date)
        start_date = end_date
        days = 1
    
    elif days:
        # Only days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days - 1)
    
    else:
        raise ValueError("Invalid combination of parameters")
    
    # Ensure start_date <= end_date
    if start_date > end_date:
        start_date, end_date = end_date, start_date
    
    return {
        'start_date': start_date, 
        'end_date': end_date,
        'days': days
    }
