"""
Test sender aggregation functionality with text fields.
"""

import pandas as pd
import pytest
from gmaildr import Gmail
from gmaildr.test_utils.get_emails import get_emails
from gmaildr.data.sender_aggregation import aggregate_emails_by_sender, SENDER_DATA_COLUMNS, SENDER_DATA_TEXT_COLUMNS


def test_aggregate_emails_by_sender_with_text():
    """
    Test sender aggregation functionality using real Gmail data with text fields.
    """
    gmail = Gmail()
    
    # Get real emails from Gmail with text content
    emails = get_emails(gmail, n=100, include_text=True, include_metrics=False)
    
    if len(emails) < 100:
        pytest.skip(f"Need at least 100 emails for test, got {len(emails)}")
    
    # Test aggregation with real data (with text fields)
    result = aggregate_emails_by_sender(emails)
    
    # Basic structure assertions
    assert isinstance(result, pd.DataFrame), "Result should be a pandas DataFrame"
    assert not result.empty, "Result should not be empty when input has emails"
    assert 'sender_email' in result.columns, "Result should have sender_email column"
    assert 'total_emails' in result.columns, "Result should have total_emails column"
    
    # Verify aggregation logic
    unique_senders = emails['sender_email'].nunique()
    assert len(result) == unique_senders, f"Should have {unique_senders} rows, one per unique sender"
    
    # Verify total email counts match
    total_emails_input = len(emails)
    total_emails_output = result['total_emails'].sum()
    assert total_emails_input == total_emails_output, "Total email count should be preserved"
    
    # Check that each sender has at least 1 email
    assert result['total_emails'].min() >= 1, "Each sender should have at least 1 email"
    
    # Verify sender_email values are unique
    assert result['sender_email'].nunique() == len(result), "Each sender_email should appear only once"
    
    # Verify we have the expected columns (SENDER_DATA_COLUMNS + SENDER_DATA_TEXT_COLUMNS + sender_email)
    expected_total_columns = len(SENDER_DATA_COLUMNS) + len(SENDER_DATA_TEXT_COLUMNS) + 1  # +1 for sender_email
    assert len(result.columns) == expected_total_columns, f"Expected {expected_total_columns} columns, got {len(result.columns)}"
    
    # Check for all expected columns
    all_expected_columns = SENDER_DATA_COLUMNS + SENDER_DATA_TEXT_COLUMNS
    for col in all_expected_columns:
        assert col in result.columns, f"Expected column '{col}' not found in result"
    
    # Verify text-specific columns are present
    text_specific_columns = ['text_primary_language', 'mean_text_language_confidence', 'text_language_diversity', 
                           'english_text_ratio', 'mean_text_length_chars', 'std_text_length_chars']
    for col in text_specific_columns:
        assert col in result.columns, f"Text-specific column '{col}' should be present when text data is available"
    
    print(f"✅ Sender aggregation test (with text) passed! Processed {len(emails)} emails from {len(result)} unique senders")
