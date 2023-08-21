import pytest
import pandas as pd
from gmaildr.core.gmail import Gmail
from gmaildr.data.email_dataframe.email_dataframe import EmailDataFrame


def test_regular_pandas_dataframe_iterrows():
    """Test if regular pandas DataFrame has the same iterrows issue."""
    # Create a simple regular pandas DataFrame
    df = pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})
    
    # Test iterrows on regular DataFrame
    try:
        iterrows_result = list(df.iterrows())
        print(f"Regular pandas DataFrame iterrows SUCCESS: {len(iterrows_result)} rows")
        assert len(iterrows_result) == 3, f"Expected 3 rows, got {len(iterrows_result)}"
        print("✅ Regular pandas DataFrame iterrows works fine")
    except Exception as e:
        print(f"❌ Regular pandas DataFrame iterrows FAILED: {e}")
        raise


def test_email_dataframe_iterrows():
    """Test if EmailDataFrame has the iterrows issue."""
    gmail = Gmail()
    
    # Get real emails for testing
    days = 1
    emails = gmail.get_emails(days=days, max_emails=3)
    while emails.is_empty() and days <= 365:
        days += 1
        emails = gmail.get_emails(days=days, max_emails=3)
    
    if emails.is_empty():
        pytest.skip("No emails found for testing")
    
    # Test iterrows on EmailDataFrame
    try:
        iterrows_result = list(emails.iterrows())
        print(f"EmailDataFrame iterrows SUCCESS: {len(iterrows_result)} rows")
        assert len(iterrows_result) > 0, "Expected at least 1 row"
        print("✅ EmailDataFrame iterrows works fine")
    except Exception as e:
        print(f"❌ EmailDataFrame iterrows FAILED: {e}")
        raise


def test_comparison_iterrows_behavior():
    """Compare iterrows behavior between regular DataFrame and EmailDataFrame."""
    gmail = Gmail()
    
    # Get real emails for testing
    days = 1
    emails = gmail.get_emails(days=days, max_emails=3)
    while emails.is_empty() and days <= 365:
        days += 1
        emails = gmail.get_emails(days=days, max_emails=3)
    
    if emails.is_empty():
        pytest.skip("No emails found for testing")
    
    # Create regular DataFrame with same data
    regular_df = pd.DataFrame(emails.values, columns=emails.columns, index=emails.index)
    
    print(f"Testing iterrows on {len(emails)} emails...")
    
    # Test both
    try:
        regular_iterrows = list(regular_df.iterrows())
        print(f"✅ Regular DataFrame iterrows: {len(regular_iterrows)} rows")
    except Exception as e:
        print(f"❌ Regular DataFrame iterrows failed: {e}")
        raise
    
    try:
        email_iterrows = list(emails.iterrows())
        print(f"✅ EmailDataFrame iterrows: {len(email_iterrows)} rows")
    except Exception as e:
        print(f"❌ EmailDataFrame iterrows failed: {e}")
        raise
    
    # Compare results
    assert len(regular_iterrows) == len(email_iterrows), f"Row count mismatch: {len(regular_iterrows)} vs {len(email_iterrows)}"
    print("✅ Both DataFrames have same number of rows from iterrows")
