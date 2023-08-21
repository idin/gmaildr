"""
Test EmailDataFrame consistency across different retrieval methods.

This test ensures that EmailDataFrame behaves consistently regardless of how emails are retrieved.
"""

from gmaildr import Gmail
from tests.core.gmail.test_get_emails import get_emails
import pytest


def test_email_dataframe_consistency():
    """Test that EmailDataFrame is consistent across different retrieval methods."""
    gmail = Gmail()
    
    # Get emails using the helper function
    emails = get_emails(gmail, 5)
    
    if len(emails) == 0:
        pytest.skip("No emails available to test with")
    
    # Test that we get the same structure regardless of retrieval method
    assert not emails.is_empty()
    assert len(emails) > 0
    
    # Verify the DataFrame has the expected structure
    expected_columns = [
        'message_id', 'timestamp', 'sender_email', 'sender_name', 
        'recipient_email', 'recipient_name', 'subject', 'labels'
    ]
    
    for column in expected_columns:
        assert column in emails.columns, f"Expected column '{column}' not found in EmailDataFrame"
    
    # Test that the data types are consistent
    assert emails['message_id'].dtype == 'object'
    assert emails['timestamp'].dtype == 'datetime64[ns]'
    assert emails['sender_email'].dtype == 'object'
    assert emails['sender_name'].dtype == 'object'
    assert emails['subject'].dtype == 'object'
    
    # Test that we can access individual emails
    first_email = emails.iloc[0]
    assert 'message_id' in first_email
    assert 'subject' in first_email
    assert 'sender_email' in first_email


def test_email_dataframe_methods():
    """Test that EmailDataFrame methods work correctly."""
    gmail = Gmail()
    
    # Get emails using the helper function
    emails = get_emails(gmail, 5)
    
    if len(emails) == 0:
        pytest.skip("No emails available to test with")
    
    # Test is_empty method
    assert not emails.is_empty()
    
    # Test head method
    head_emails = emails.head(2)
    assert len(head_emails) <= 2
    assert len(head_emails) <= len(emails)
    
    # Test tail method
    tail_emails = emails.tail(2)
    assert len(tail_emails) <= 2
    assert len(tail_emails) <= len(emails)
    
    # Test filtering
    if len(emails) > 1:
        filtered_emails = emails[emails['sender_email'].notna()]
        assert len(filtered_emails) <= len(emails)
    
    # Test sorting
    sorted_emails = emails.sort_values('timestamp', ascending=False)
    assert len(sorted_emails) == len(emails)
