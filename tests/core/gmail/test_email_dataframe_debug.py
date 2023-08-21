"""
Debug test to understand EmailDataFrame issues.
"""

import pytest
from gmaildr.core.gmail import Gmail


def test_get_emails_returns_email_dataframe():
    """Debug test to check what get_emails returns."""
    gmail = Gmail()
    emails = gmail.get_emails(days=1, max_emails=1)
    
    print(f'Type: {type(emails)}')
    print(f'Empty: {emails.empty}')
    print(f'Length: {len(emails)}')
    print(f'Columns: {list(emails.columns)}')
    
    # Check if it's an EmailDataFrame
    from gmaildr.data import EmailDataFrame
    assert isinstance(emails, EmailDataFrame), f"Expected EmailDataFrame, got {type(emails)}"
    
    # Check if it has the is_empty method
    assert hasattr(emails, 'is_empty'), "EmailDataFrame should have is_empty method"
    
    # Test the is_empty method
    is_empty_result = emails.is_empty()
    print(f'is_empty() result: {is_empty_result}')
    assert isinstance(is_empty_result, bool), "is_empty() should return a boolean"


def test_empty_dataframe_behavior():
    """Test behavior when no emails are found."""
    gmail = Gmail()
    
    # Try to get emails from a very short time period to potentially get empty result
    emails = gmail.get_emails(days=1, max_emails=1)
    
    print(f'Type: {type(emails)}')
    print(f'Empty: {emails.empty}')
    print(f'Length: {len(emails)}')
    print(f'Columns: {list(emails.columns)}')
    
    # Even if empty, it should still be an EmailDataFrame
    from gmaildr.data import EmailDataFrame
    assert isinstance(emails, EmailDataFrame), f"Expected EmailDataFrame, got {type(emails)}"
    
    # Check if it has the is_empty method
    assert hasattr(emails, 'is_empty'), "EmailDataFrame should have is_empty method"
    
    # Test the is_empty method
    is_empty_result = emails.is_empty()
    print(f'is_empty() result: {is_empty_result}')
    assert isinstance(is_empty_result, bool), "is_empty() should return a boolean"


def test_empty_email_dataframe_creation():
    """Test creating empty EmailDataFrame directly."""
    from gmaildr.data import EmailDataFrame
    from gmaildr.core.gmail import Gmail
    
    # Create a Gmail instance for the test
    gmail = Gmail()
    
    # Test creating empty EmailDataFrame
    empty_df = EmailDataFrame(gmail=gmail)
    print(f'Empty EmailDataFrame Type: {type(empty_df)}')
    print(f'Empty EmailDataFrame Empty: {empty_df.empty}')
    print(f'Empty EmailDataFrame Length: {len(empty_df)}')
    print(f'Empty EmailDataFrame Columns: {list(empty_df.columns)}')
    
    assert isinstance(empty_df, EmailDataFrame), f"Expected EmailDataFrame, got {type(empty_df)}"
    assert hasattr(empty_df, 'is_empty'), "EmailDataFrame should have is_empty method"
    
    # Test the is_empty method
    is_empty_result = empty_df.is_empty()
    print(f'is_empty() result: {is_empty_result}')
    assert isinstance(is_empty_result, bool), "is_empty() should return a boolean"
    assert is_empty_result == True, "Empty DataFrame should return True for is_empty()"


def test_empty_email_dataframe_from_empty_list():
    """Test creating EmailDataFrame from empty list."""
    from gmaildr.data import EmailDataFrame
    from gmaildr.core.gmail import Gmail
    
    # Create a Gmail instance for the test
    gmail = Gmail()
    
    # Test creating EmailDataFrame from empty list
    empty_df = EmailDataFrame([], gmail=gmail)
    print(f'Empty List EmailDataFrame Type: {type(empty_df)}')
    print(f'Empty List EmailDataFrame Empty: {empty_df.empty}')
    print(f'Empty List EmailDataFrame Length: {len(empty_df)}')
    print(f'Empty List EmailDataFrame Columns: {list(empty_df.columns)}')
    
    assert isinstance(empty_df, EmailDataFrame), f"Expected EmailDataFrame, got {type(empty_df)}"
    assert hasattr(empty_df, 'is_empty'), "EmailDataFrame should have is_empty method"
    
    # Test the is_empty method
    is_empty_result = empty_df.is_empty()
    print(f'is_empty() result: {is_empty_result}')
    assert isinstance(is_empty_result, bool), "is_empty() should return a boolean"
    assert is_empty_result == True, "Empty DataFrame should return True for is_empty()"
