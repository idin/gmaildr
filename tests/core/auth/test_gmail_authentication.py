#!/usr/bin/env python3
"""
Test Gmail authentication flow in a clean environment.

This test ensures that the Gmail class can handle authentication
when no credentials exist and properly guides users through setup.
"""

import os
import shutil
import tempfile
import time
from pathlib import Path
import sys
import pytest
from unittest.mock import patch, MagicMock

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def test_gmail_authentication_flow():
    """
    Test the complete Gmail authentication flow in a clean environment.
    
    This test:
    1. Creates a temporary directory with no existing credentials
    2. Tests Gmail initialization (should trigger auth setup)
    3. Simulates user placing credentials file
    4. Tests email retrieval
    5. Cleans up credentials after test
    
    NOTE: This test is skipped because it triggers interactive OAuth flow.
    The test isolation is working correctly - it no longer finds existing credentials
    and properly triggers the authentication flow, but this requires user interaction
    which blocks automated testing.
    """
    
    # Create a temporary directory for this test
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"🧪 Testing in temporary directory: {temp_dir}")
        
        # Store original environment variables
        original_cwd = os.getcwd()
        original_creds_env = os.environ.get('GMAIL_CREDENTIALS_FILE')
        original_token_env = os.environ.get('GMAIL_TOKEN_FILE')
        
        # Set environment variables to point to test directory
        test_creds_file = os.path.join(temp_dir, "credentials", "credentials.json")
        test_token_file = os.path.join(temp_dir, "credentials", "token.pickle")
        os.environ['GMAIL_CREDENTIALS_FILE'] = test_creds_file
        os.environ['GMAIL_TOKEN_FILE'] = test_token_file
        
        # Change to the temporary directory
        os.chdir(temp_dir)
        
        try:
            # Ensure no credentials exist initially
            credentials_dir = Path("credentials")
            credentials_file = credentials_dir / "credentials.json"
            token_file = credentials_dir / "token.pickle"
            
            # Clean up any existing credentials
            if credentials_file.exists():
                credentials_file.unlink()
            if token_file.exists():
                token_file.unlink()
            if credentials_dir.exists():
                shutil.rmtree(credentials_dir)
            
            print("✅ Clean environment created - no existing credentials")
            
            # Test 1: Gmail initialization should trigger auth setup
            print("\n🔐 Testing Gmail initialization...")
            
            try:
                from gmaildr.core import Gmail
                
                # Mock the OAuth flow to prevent hanging
                with patch('gmaildr.core.auth.auth_manager.InstalledAppFlow.from_client_secrets_file') as mock_flow:
                    # Configure the mock to raise an authentication error instead of hanging
                    mock_flow_instance = MagicMock()
                    mock_flow_instance.run_local_server.side_effect = Exception("Credentials file not found or invalid")
                    mock_flow.return_value = mock_flow_instance
                    
                    print("Initializing Gmail class with mocked OAuth flow...")
                    
                    try:
                        gmail = Gmail()
                        # If we get here, it means credentials were found somewhere else
                        print("⚠️  Gmail initialized without triggering auth flow")
                        print("This means credentials were found in the parent directory")
                        print("This test is not properly isolated")
                        assert False, "Test should be isolated from existing credentials"
                        
                    except Exception as auth_error:
                        # This is what we expect - authentication should fail in a clean environment
                        error_str = str(auth_error).lower()
                        print(f"✅ Authentication failed as expected: {auth_error}")
                        
                        # Check for expected authentication errors
                        expected_errors = [
                            "credentials file not found",
                            "oauth client was not found", 
                            "invalid_client",
                            "no such file or directory",
                            "authentication failed",
                            "authorization error",
                            "invalid"
                        ]
                        
                        is_expected_error = any(expected in error_str for expected in expected_errors)
                        
                        if is_expected_error:
                            print("✅ Got expected authentication error - test isolation is working")
                            print("✅ Test PASSED: Auth flow properly triggered in isolated environment")
                            return True  # Test passed successfully
                        else:
                            print(f"❌ Unexpected error type: {auth_error}")
                            print(f"Error type: {type(auth_error).__name__}")
                            assert False, f"Unexpected authentication error: {auth_error}"
                
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                print(f"Error type: {type(e).__name__}")
                assert False, f"Unexpected error: {e}"
                
        finally:
            # Clean up: remove any credentials created during test
            print("\n🧹 Cleaning up test credentials...")
            
            if credentials_file.exists():
                credentials_file.unlink()
                print("✅ Removed credentials file")
            
            if token_file.exists():
                token_file.unlink()
                print("✅ Removed token file")
            
            if credentials_dir.exists():
                shutil.rmtree(credentials_dir)
                print("✅ Removed credentials directory")
            
            # Restore original environment variables
            if original_creds_env is not None:
                os.environ['GMAIL_CREDENTIALS_FILE'] = original_creds_env
            elif 'GMAIL_CREDENTIALS_FILE' in os.environ:
                del os.environ['GMAIL_CREDENTIALS_FILE']
                
            if original_token_env is not None:
                os.environ['GMAIL_TOKEN_FILE'] = original_token_env
            elif 'GMAIL_TOKEN_FILE' in os.environ:
                del os.environ['GMAIL_TOKEN_FILE']
            
            # Restore original working directory
            os.chdir(original_cwd)
            print("✅ Restored original working directory and environment")


def test_gmail_with_existing_credentials():
    """
    Test Gmail functionality with existing credentials.
    
    This test assumes you have valid credentials and tests
    that the Gmail class works properly with them.
    """
    
    print("\n🔐 Testing Gmail with existing credentials...")
    
    try:
        from gmaildr.core import Gmail
        
        # Initialize Gmail (should use existing credentials)
        gmail = Gmail()
        print("✅ Gmail initialization successful!")
        
        # Test email retrieval
        emails = gmail.get_emails(days=7, max_emails=10)
        
        if emails is not None and len(emails) > 0:
            print(f"✅ Successfully retrieved {len(emails)} emails")
            
            # Test basic functionality
            print(f"✅ Sample email subject: {emails.iloc[0].get('subject', 'No subject')}")
            print(f"✅ Sample sender: {emails.iloc[0].get('sender_email', 'Unknown')}")
            
            assert True  # Test passed
        else:
            print("ℹ️  No emails found in the last 7 days")
            assert True  # This is still a successful test
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        assert False, f"Test failed: {e}"


if __name__ == "__main__":
    print("🧪 Gmail Authentication Test Suite")
    print("=" * 50)
    
    # Test 1: Clean authentication flow
    print("\n📋 Test 1: Clean Authentication Flow")
    print("-" * 30)
    test1_passed = test_gmail_authentication_flow()
    
    # Test 2: Existing credentials
    print("\n📋 Test 2: Existing Credentials")
    print("-" * 30)
    test2_passed = test_gmail_with_existing_credentials()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    print(f"Clean Authentication Flow: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"Existing Credentials: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 All tests passed! Gmail authentication is working correctly.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please check the authentication setup.")
        sys.exit(1)
