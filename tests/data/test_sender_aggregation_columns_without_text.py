"""
Test sender aggregation column validation without text fields.
"""

import pandas as pd
import pytest
from gmaildr import Gmail
from gmaildr.test_utils.get_emails import get_emails
from gmaildr.data.sender_aggregation import (
    aggregate_emails_by_sender, 
    SENDER_DATA_COLUMNS
)
from gmaildr.utils.dataframe_utils import has_all_columns


def test_sender_aggregation_columns_without_text():
    """
    Test that sender aggregation produces exactly the expected columns when no text fields are present.
    """
    gmail = Gmail()
    
    # Get real emails from Gmail without text content
    emails = get_emails(gmail, n=100, include_text=False, include_metrics=False)
    
    if len(emails) < 100:
        pytest.skip(f"Need at least 100 emails for test, got {len(emails)}")
    
    # Perform aggregation
    result = aggregate_emails_by_sender(emails)
    
    # Use utility function to check if all expected columns are present
    assert has_all_columns(result, SENDER_DATA_COLUMNS), (
        f"Result is missing some expected columns from SENDER_DATA_COLUMNS"
    )
    
    # Verify exact column count
    assert len(result.columns) == len(SENDER_DATA_COLUMNS), (
        f"Expected exactly {len(SENDER_DATA_COLUMNS)} columns, got {len(result.columns)}"
    )
    
    print(f"✅ Column validation passed! Result has exactly {len(result.columns)} expected columns")
    print(f"   Processed {len(emails)} emails from {len(result)} unique senders")
