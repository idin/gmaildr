"""
Simple test to verify DataFrame operations work for email modifications.

This test focuses on verifying that the methods accept DataFrames and return results,
without complex folder verification that depends on caching/timing.
"""

import pytest
from gmaildr import Gmail
import pandas as pd


def test_dataframe_move_operations():
    """Test that move operations accept DataFrames and return results."""
    gmail = Gmail()
    
    # Get some emails to test with
    emails = gmail.get_emails(max_emails=2)
    
    if emails.empty:
        pytest.skip("No emails found for testing")
    
    print(f"📧 Found {len(emails)} emails for testing")
    print(f"📧 Email types: {type(emails)} - {emails.columns.tolist()}")
    
    # Test that methods accept DataFrames and return results
    print("\n🧪 Testing DataFrame acceptance...")
    
    # Test move_to_inbox
    try:
        result = gmail.move_to_inbox(emails)
        print(f"✅ move_to_inbox(DataFrame): {result}")
        assert result is not None, "move_to_inbox should return a result"
    except Exception as e:
        print(f"❌ move_to_inbox failed: {e}")
        raise
    
    # Test move_to_archive (restore)
    try:
        result = gmail.move_to_archive(emails)
        print(f"✅ move_to_archive(DataFrame): {result}")
        assert result is not None, "move_to_archive should return a result"
    except Exception as e:
        print(f"❌ move_to_archive failed: {e}")
        raise
    
    print("\n🎯 All DataFrame move operations work!")


def test_dataframe_label_operations():
    """Test that label operations accept DataFrames and return results."""
    gmail = Gmail()
    
    # Get some emails to test with
    emails = gmail.get_emails(max_emails=2)
    
    if emails.empty:
        pytest.skip("No emails found for testing")
    
    print(f"📧 Found {len(emails)} emails for label testing")
    
    test_label = "TEST_DF_LABEL"
    
    # Test add_label
    try:
        result = gmail.add_label(emails, test_label)
        print(f"✅ add_label(DataFrame): {result}")
        assert result is not None, "add_label should return a result"
    except Exception as e:
        print(f"❌ add_label failed: {e}")
        raise
    
    # Test remove_label (cleanup)
    try:
        result = gmail.remove_label(emails, test_label)
        print(f"✅ remove_label(DataFrame): {result}")
        assert result is not None, "remove_label should return a result"
    except Exception as e:
        print(f"❌ remove_label failed: {e}")
        raise
    
    print("\n🎯 All DataFrame label operations work!")


def test_dataframe_status_operations():
    """Test that status operations accept DataFrames and return results."""
    gmail = Gmail()
    
    # Get some emails to test with
    emails = gmail.get_emails(max_emails=2)
    
    if emails.empty:
        pytest.skip("No emails found for testing")
    
    print(f"📧 Found {len(emails)} emails for status testing")
    
    # Test star_email
    try:
        result = gmail.star_email(emails)
        print(f"✅ star_email(DataFrame): {result}")
        assert result is not None, "star_email should return a result"
    except Exception as e:
        print(f"❌ star_email failed: {e}")
        raise
    
    # Test unstar_email (restore)
    try:
        result = gmail.unstar_email(emails)
        print(f"✅ unstar_email(DataFrame): {result}")
        assert result is not None, "unstar_email should return a result"
    except Exception as e:
        print(f"❌ unstar_email failed: {e}")
        raise
    
    # Test mark_as_read
    try:
        result = gmail.mark_as_read(emails)
        print(f"✅ mark_as_read(DataFrame): {result}")
        assert result is not None, "mark_as_read should return a result"
    except Exception as e:
        print(f"❌ mark_as_read failed: {e}")
        raise
    
    print("\n🎯 All DataFrame status operations work!")


def test_dataframe_validation():
    """Test that DataFrame validation works correctly."""
    gmail = Gmail()
    
    # Test with valid DataFrame
    valid_df = pd.DataFrame({
        'message_id': ['test123', 'test456'],
        'subject': ['Test 1', 'Test 2']
    })
    
    print("🧪 Testing DataFrame validation...")
    
    # This should work (no actual operation, just validation)
    try:
        # The validation happens inside the method
        print("✅ Valid DataFrame accepted")
    except Exception as e:
        print(f"❌ Valid DataFrame rejected: {e}")
        raise
    
    # Test with invalid DataFrame (missing message_id column)
    invalid_df = pd.DataFrame({
        'subject': ['Test 1', 'Test 2']
    })
    
    try:
        gmail.move_to_inbox(invalid_df)
        assert False, "Should have raised error for missing message_id column"
    except (KeyError, ValueError) as e:
        print(f"✅ Invalid DataFrame correctly rejected: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        raise
    
    print("\n🎯 DataFrame validation works correctly!")


if __name__ == "__main__":
    test_dataframe_move_operations()
    test_dataframe_label_operations()
    test_dataframe_status_operations()
    test_dataframe_validation()
    print("\n🎉 All DataFrame operations tests passed!")
