"""
Debug tests for constructor methods to understand pandas behavior.
"""

import pytest
import pandas as pd
from gmaildr.core.gmail import Gmail
from gmaildr.data.email_dataframe.email_dataframe import EmailDataFrame


def test_regular_dataframe_constructor_methods():
    """Test what regular DataFrame's constructor methods return."""
    df = pd.DataFrame({'a': [1, 2, 3], 'b': ['x', 'y', 'z']})
    
    print(f"Regular DataFrame _constructor_sliced: {df._constructor_sliced}")
    print(f"Type: {type(df._constructor_sliced)}")
    
    # Test if it's callable
    assert callable(df._constructor_sliced), f"Regular DataFrame _constructor_sliced should be callable, got {type(df._constructor_sliced)}"
    
    # Test if it creates Series objects
    series = df._constructor_sliced([1, 2, 3], index=['a', 'b', 'c'], name='test')
    assert isinstance(series, pd.Series), f"Should create Series, got {type(series)}"
    
    print(f"Created Series: {series}")
    print(f"Series type: {type(series)}")


def test_email_dataframe_constructor_methods():
    """Test what EmailDataFrame's constructor methods return."""
    gmail = Gmail()
    data = {'message_id': ['msg1', 'msg2'], 'subject': ['Test 1', 'Test 2']}
    df = EmailDataFrame(data, gmail=gmail)
    
    # Don't print the DataFrame directly to avoid __repr__ issues
    print(f"EmailDataFrame _constructor_sliced type: {type(df._constructor_sliced)}")
    print(f"Is callable: {callable(df._constructor_sliced)}")
    
    # Test if it's callable
    assert callable(df._constructor_sliced), f"EmailDataFrame _constructor_sliced should be callable, got {type(df._constructor_sliced)}"
    
    # Test if it creates Series objects
    series = df._constructor_sliced([1, 2, 3], index=['a', 'b', 'c'], name='test')
    assert isinstance(series, pd.Series), f"Should create Series, got {type(series)}"
    
    print(f"Created Series: {series}")
    print(f"Series type: {type(series)}")


def test_constructor_methods_comparison():
    """Compare constructor methods between regular DataFrame and EmailDataFrame."""
    # Regular DataFrame
    regular_df = pd.DataFrame({'a': [1, 2, 3], 'b': ['x', 'y', 'z']})
    
    # EmailDataFrame
    gmail = Gmail()
    data = {'message_id': ['msg1', 'msg2'], 'subject': ['Test 1', 'Test 2']}
    email_df = EmailDataFrame(data, gmail=gmail)
    
    print("=== Regular DataFrame ===")
    print(f"_constructor_sliced type: {type(regular_df._constructor_sliced)}")
    print(f"Is callable: {callable(regular_df._constructor_sliced)}")
    assert regular_df._constructor_sliced == pd.Series, f"Regular DataFrame _constructor_sliced should be pd.Series, got {regular_df._constructor_sliced}"
    
    print("\n=== EmailDataFrame ===")
    print(f"_constructor_sliced type: {type(email_df._constructor_sliced)}")
    print(f"Is callable: {callable(email_df._constructor_sliced)}")
    assert email_df._constructor_sliced == pd.Series, f"EmailDataFrame _constructor_sliced should be pd.Series, got {email_df._constructor_sliced}"
    
    # Test if they behave the same way
    regular_series = regular_df._constructor_sliced([1, 2, 3], index=['a', 'b', 'c'], name='test')
    email_series = email_df._constructor_sliced([1, 2, 3], index=['a', 'b', 'c'], name='test')
    
    assert isinstance(regular_series, pd.Series), f"Regular DataFrame should create Series, got {type(regular_series)}"
    assert isinstance(email_series, pd.Series), f"EmailDataFrame should create Series, got {type(email_series)}"
    
    print(f"\nRegular Series: {regular_series}")
    print(f"Email Series: {email_series}")
    assert isinstance(regular_series, pd.Series), f"Regular DataFrame should create Series, got {type(regular_series)}"
    assert isinstance(email_series, pd.Series), f"EmailDataFrame should create Series, got {type(email_series)}"


def test_iterrows_behavior():
    """Test iterrows behavior to understand the __finalize__ issue."""
    # Regular DataFrame
    regular_df = pd.DataFrame({'a': [1, 2, 3], 'b': ['x', 'y', 'z']})
    
    print("=== Regular DataFrame iterrows ===")
    for idx, row in regular_df.iterrows():
        print(f"Index: {idx}, Row: {row}, Type: {type(row)}")
        # Check if row has __finalize__ method
        if hasattr(row, '__finalize__'):
            print(f"  Has __finalize__: {row.__finalize__}")
        else:
            print(f"  No __finalize__ method")
        break  # Just test first row
    
    # EmailDataFrame
    gmail = Gmail()
    data = {'message_id': ['msg1', 'msg2'], 'subject': ['Test 1', 'Test 2']}
    email_df = EmailDataFrame(data, gmail=gmail)
    
    print("\n=== EmailDataFrame iterrows ===")
    try:
        for idx, row in email_df.iterrows():
            print(f"Index: {idx}, Row: {row}, Type: {type(row)}")
            # Check if row has __finalize__ method
            if hasattr(row, '__finalize__'):
                print(f"  Has __finalize__: {row.__finalize__}")
            else:
                print(f"  No __finalize__ method")
            break  # Just test first row
    except Exception as e:
        print(f"Error in EmailDataFrame iterrows: {e}")
        print(f"Error type: {type(e)}")


def test_message_id_column_slicing():
    """Test that slicing the message_id column returns a pandas Series."""
    gmail = Gmail()
    data = {'message_id': ['msg1', 'msg2', 'msg3'], 'subject': ['Test 1', 'Test 2', 'Test 3']}
    email_df = EmailDataFrame(data, gmail=gmail)
    
    print("=== Testing message_id column slicing ===")
    
    # Test slicing message_id column
    message_id_series = email_df['message_id']
    print(f"message_id column type: {type(message_id_series)}")
    print(f"message_id column: {message_id_series}")
    assert isinstance(message_id_series, pd.Series), f"message_id column should be pd.Series, got {type(message_id_series)}"
    
    # Test slicing other columns
    subject_series = email_df['subject']
    print(f"subject column type: {type(subject_series)}")
    print(f"subject column: {subject_series}")
    assert isinstance(subject_series, pd.Series), f"subject column should be pd.Series, got {type(subject_series)}"
    
    # Test that both columns return regular pandas Series
    assert isinstance(message_id_series, pd.Series), f"message_id column should be pd.Series, got {type(message_id_series)}"
    assert isinstance(subject_series, pd.Series), f"subject column should be pd.Series, got {type(subject_series)}"
    
    # Test that the Series contain the expected data
    assert message_id_series.tolist() == ['msg1', 'msg2', 'msg3'], "message_id series should contain correct data"
    assert subject_series.tolist() == ['Test 1', 'Test 2', 'Test 3'], "subject series should contain correct data"
    
    print("✓ message_id column slicing test completed")


def test_constructor_sliced_method():
    """Test the _constructor_sliced method directly."""
    gmail = Gmail()
    data = {'message_id': ['msg1', 'msg2'], 'subject': ['Test 1', 'Test 2']}
    email_df = EmailDataFrame(data, gmail=gmail)
    
    print("=== Testing _constructor_sliced method ===")
    
    # Test _constructor_sliced for message_id
    message_id_constructor = email_df._constructor_sliced('message_id')
    print(f"_constructor_sliced('message_id'): {message_id_constructor}")
    print(f"Type: {type(message_id_constructor)}")
    assert isinstance(message_id_constructor, pd.Series), f"message_id should return pd.Series, got {type(message_id_constructor)}"
    
    # Test _constructor_sliced for other columns
    subject_constructor = email_df._constructor_sliced('subject')
    print(f"_constructor_sliced('subject'): {subject_constructor}")
    print(f"Type: {type(subject_constructor)}")
    assert isinstance(subject_constructor, pd.Series), f"subject should return pd.Series, got {type(subject_constructor)}"
    
    # message_id should return EmailSeries (once implemented)
    # assert message_id_constructor == EmailSeries, f"message_id should return EmailSeries, got {message_id_constructor}"
    
    # Other columns should return pd.Series
    assert isinstance(subject_constructor, pd.Series), f"subject should return pd.Series, got {type(subject_constructor)}"
    
    print("✓ _constructor_sliced method test completed")


def test_pandas_column_access_methods():
    """Test to understand how pandas handles column access."""
    import pandas as pd
    
    df = pd.DataFrame({'a': [1, 2, 3], 'b': ['x', 'y', 'z']})
    
    print("=== Testing pandas column access methods ===")
    
    # Find methods containing 'getitem'
    getitem_methods = [m for m in dir(df) if 'getitem' in m.lower()]
    print(f"Methods containing 'getitem': {getitem_methods}")
    
    # Test what happens when we access a column
    column_a = df['a']
    print(f"Column 'a' type: {type(column_a)}")
    print(f"Column 'a': {column_a}")
    
    # Check if there's a __getitem__ method
    if hasattr(df, '__getitem__'):
        print(f"__getitem__ method exists: {df.__getitem__}")
    else:
        print("No __getitem__ method found")
    
    # Test if we can call __getitem__ directly
    try:
        column_a_direct = df.__getitem__('a')
        print(f"Direct __getitem__('a') type: {type(column_a_direct)}")
        assert type(column_a_direct) == type(column_a), f"Direct __getitem__ should return same type as df['a']"
    except Exception as e:
        print(f"Error calling __getitem__ directly: {e}")
    
    print("✓ pandas column access methods test completed")
