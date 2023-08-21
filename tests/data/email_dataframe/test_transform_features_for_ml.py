"""
Tests for transform_features_for_ml function.

This module tests the email feature transformation functionality.
"""

import pytest
import pandas as pd
from gmaildr import Gmail
from tests.core.gmail.test_get_emails import get_emails
from gmaildr.data.email_dataframe.transform_features_for_ml import transform_email_features_for_ml


def test_transform_features_for_ml_debug():
    """
    Debug test to understand why transform_features_for_ml returns empty DataFrame.
    
    This test:
    1. Gets some emails from Gmail
    2. Creates an EmailDataFrame
    3. Calls transform_email_features_for_ml directly
    4. Debugs what's happening during transformation
    """
    gmail = Gmail()
    
    # Get some emails using the helper function
    emails = get_emails(gmail=gmail, n=5)
    
    if len(emails) == 0:
        pytest.skip("No emails available to test with")
    
    print(f"Original EmailDataFrame has {len(emails)} rows")
    print(f"Columns: {emails.columns.tolist()}")
    
    # Check for required columns
    required_columns = ['hour', 'day_of_week', 'sender_local_timestamp']
    missing_columns = [col for col in required_columns if col not in emails.columns]
    
    if missing_columns:
        print(f"Missing required columns: {missing_columns}")
        pytest.fail(f"EmailDataFrame missing required columns: {missing_columns}")
    
    # Show sample data for debugging
    print("\nSample data for required columns:")
    sample_data = emails[['message_id', 'hour', 'day_of_week', 'sender_local_timestamp']].head()
    print(sample_data)
    
    # Check if the data is actually there
    print(f"\nHour column type: {emails['hour'].dtype}")
    print(f"Hour column values: {emails['hour'].tolist()}")
    print(f"Day of week column type: {emails['day_of_week'].dtype}")
    print(f"Day of week column values: {emails['day_of_week'].tolist()}")
    print(f"Timestamp column type: {emails['sender_local_timestamp'].dtype}")
    print(f"Timestamp column values: {emails['sender_local_timestamp'].tolist()}")
    
    # Call the transformation function directly
    try:
        print("\nCalling transform_email_features_for_ml...")
        print(f"Emails DataFrame empty check: {emails.empty}")
        print(f"Emails DataFrame length: {len(emails)}")
        ml_df = transform_email_features_for_ml(email_df=emails)
        print(f"\nTransformed DataFrame has {len(ml_df)} rows")
        print(f"Transformed columns: {ml_df.columns.tolist()}")
        
        # Verify the transformation worked
        assert len(ml_df) == len(emails), (
            f"Transformed DataFrame should have same number of rows. "
            f"Expected {len(emails)}, got {len(ml_df)}"
        )
        
        print("✅ Transformation successful!")
        
    except Exception as e:
        import traceback
        print(f"❌ Transformation failed with error: {e}")
        print(f"❌ Full traceback:")
        traceback.print_exc()
        pytest.fail(f"Transform function failed: {e}")


def test_transform_features_for_ml_empty_dataframe():
    """
    Test transform_features_for_ml with empty EmailDataFrame.
    """
    # Create empty EmailDataFrame
    empty_df = pd.DataFrame()
    from gmaildr.data.email_dataframe.email_dataframe import EmailDataFrame
    empty_email_df = EmailDataFrame(empty_df)
    
    # Transform empty DataFrame
    result = transform_email_features_for_ml(email_df=empty_email_df)
    
    # Should return empty Email_ML_DataFrame
    assert len(result) == 0, "Empty input should produce empty output"
    print("✅ Empty DataFrame transformation works correctly")


def test_transform_features_for_ml_required_columns():
    """
    Test that transform_features_for_ml handles missing required columns gracefully.
    """
    # Create minimal EmailDataFrame with required columns
    data = get_emails(gmail=Gmail(), n=2)
    
    from gmaildr.data.email_dataframe.email_dataframe import EmailDataFrame
    test_df = EmailDataFrame(pd.DataFrame(data))
    
    # Transform
    result = transform_email_features_for_ml(email_df=test_df)
    
    # Should have same number of rows
    assert len(result) == len(test_df), (
        f"Should preserve row count. Expected {len(test_df)}, got {len(result)}"
    )
    
    # Should have message_id column
    assert 'message_id' in result.columns, "Should preserve message_id column"
    
    print("✅ Minimal DataFrame transformation works correctly")
