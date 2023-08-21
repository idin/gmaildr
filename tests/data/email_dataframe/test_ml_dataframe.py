"""
Tests for the ml_dataframe property of EmailDataFrame.

This test verifies that the ml_dataframe property returns a dataframe with the same
number of rows as the original EmailDataFrame.
"""

from gmaildr import Gmail
from tests.core.gmail.test_get_emails import get_emails
import pytest
import pandas as pd
from gmaildr.data.email_dataframe.email_ml_dataframe import Email_ML_DataFrame


def test_debug_columns():
    """
    Debug test to see what columns are available in the test data.
    """
    gmail = Gmail()
    
    # Get some emails using the helper function
    emails = get_emails(gmail=gmail, n=5)
    
    if len(emails) == 0:
        raise ValueError("No emails available to test with")
    
    print(f"Available columns: {list(emails.columns)}")
    print(f"Number of rows: {len(emails)}")
    
    # Check for required columns
    required_columns = ['hour', 'day_of_week', 'sender_local_timestamp']
    for col in required_columns:
        if col in emails.columns:
            print(f"✓ {col} is available")
        else:
            print(f"✗ {col} is missing")


def test_ml_dataframe_preserves_identifiers():
    """
    Test that ml_dataframe preserves message IDs, sender emails, and recipient emails
    in the same order without shuffling.
    
    This test:
    1. Gets some emails from Gmail using the get_emails helper
    2. Creates an EmailDataFrame from those emails
    3. Gets the ml_dataframe property
    4. Verifies that message IDs, sender emails, and recipient emails are preserved
       in the same order as the original dataframe
    """
    gmail = Gmail()
    
    # Get some emails using the helper function
    emails = get_emails(gmail=gmail, n=100)
    
    if len(emails) == 0:
        raise RuntimeError("No emails available to test with")
    
    # Get the ml_dataframe
    ml_df = emails.ml_dataframe
    
    # Verify both dataframes have the same number of rows
    assert len(ml_df) == len(emails), (
        f"ml_dataframe should have same number of rows as original. "
        f"Expected {len(emails)}, got {len(ml_df)}"
    )
    
    # Check that message_id column is preserved
    assert 'message_id' in ml_df.columns, "ml_dataframe should preserve message_id column"
    assert 'sender_email' in ml_df.columns, "ml_dataframe should preserve sender_email column"
    assert 'recipient_email' in ml_df.columns, "ml_dataframe should preserve recipient_email column"

    # ✅ EXPECTED BEHAVIOR: SLICING EMAIL_ML_DATAFRAME RETURNS PANDAS DATAFRAME
    # REASON: Email_ML_DataFrame requires specific columns (like 'hour', 'day_of_week') for ML features
    # When we slice and remove these required columns, the _constructor_from_mgr method detects
    # that the sliced data is no longer a valid ML DataFrame and returns a regular pandas DataFrame
    # THIS IS CORRECT BEHAVIOR - it gracefully degrades instead of failing
    ml_id_df = ml_df[['message_id', 'sender_email', 'recipient_email']]
    
    # Verify the slicing returns a regular pandas DataFrame (not Email_ML_DataFrame)
    assert isinstance(ml_id_df, pd.DataFrame), "Sliced ML DataFrame should return regular pandas DataFrame"
    assert not isinstance(ml_id_df, Email_ML_DataFrame), "Sliced ML DataFrame should NOT be Email_ML_DataFrame when columns are missing"
    
    # Verify the sliced data has the correct columns and data
    assert list(ml_id_df.columns) == ['message_id', 'sender_email', 'recipient_email'], "Sliced DataFrame should have selected columns"
    assert len(ml_id_df) == len(emails), "Sliced DataFrame should preserve row count"
    
    # ✅ COMPARISON: Slice the original EmailDataFrame for comparison
    emails_id_df = emails[['message_id', 'sender_email', 'recipient_email']]
    
    # Verify both sliced dataframes have the same data
    assert ml_id_df.equals(emails_id_df), "Sliced ML DataFrame should preserve same data as sliced original DataFrame"
    
    print(f"Successfully verified that ml_dataframe preserves identifiers for {len(emails)} emails")


def test_ml_dataframe_same_row_count():
    """
    Test that ml_dataframe has the same number of rows as the original EmailDataFrame.
    
    This test:
    1. Gets some emails from Gmail using the get_emails helper
    2. Creates an EmailDataFrame from those emails
    3. Gets the ml_dataframe property
    4. Verifies that both dataframes have the same number of rows
    """
    gmail = Gmail()
    
    # Get some emails using the helper function
    emails = get_emails(gmail=gmail, n=10)
    
    if len(emails) == 0:
        pytest.skip("No emails available to test with")
    
    # Verify we have an EmailDataFrame
    assert hasattr(emails, 'ml_dataframe'), "EmailDataFrame should have ml_dataframe property"
    
    # Get the original row count
    original_row_count = len(emails)
    
    # Get the ml_dataframe
    ml_df = emails.ml_dataframe
    
    # Verify the ml_dataframe has the same number of rows
    ml_row_count = len(ml_df)
    
    assert ml_row_count == original_row_count, (
        f"ml_dataframe should have same number of rows as original. "
        f"Expected {original_row_count}, got {ml_row_count}"
    )
    
    print(f"Successfully verified ml_dataframe has {ml_row_count} rows (same as original)")


def test_ml_dataframe_is_dataframe():
    """
    Test that ml_dataframe returns a proper dataframe object.
    """
    gmail = Gmail()
    
    # Get some emails using the helper function
    emails = get_emails(gmail=gmail, n=5)
    
    if len(emails) == 0:
        pytest.skip("No emails available to test with")
    
    # Get the ml_dataframe
    ml_df = emails.ml_dataframe
    
    # Verify it's a dataframe-like object
    assert hasattr(ml_df, 'columns'), "ml_dataframe should have columns attribute"
    assert hasattr(ml_df, 'iloc'), "ml_dataframe should have iloc attribute"
    assert hasattr(ml_df, 'shape'), "ml_dataframe should have shape attribute"
    
    # Verify it has some columns
    assert len(ml_df.columns) > 0, "ml_dataframe should have at least one column"
    
    print(f"Successfully verified ml_dataframe is a proper dataframe with {len(ml_df.columns)} columns")


def test_ml_dataframe_with_different_email_counts():
    """
    Test ml_dataframe with different numbers of emails to ensure consistency.
    """
    gmail = Gmail()
    
    # Test with different email counts
    test_counts = [1, 3, 5]
    
    for count in test_counts:
        # Get emails using the helper function
        emails = get_emails(gmail=gmail, n=count)
        
        if len(emails) == 0:
            pytest.skip(f"No emails available to test with count {count}")
        
        # Get the ml_dataframe
        ml_df = emails.ml_dataframe
        
        # Verify row count consistency
        assert len(ml_df) == len(emails), (
            f"For {count} emails: ml_dataframe should have same number of rows. "
            f"Expected {len(emails)}, got {len(ml_df)}"
        )
        
        print(f"Successfully verified ml_dataframe consistency for {count} emails")
