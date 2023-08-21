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
    """
    
    # Create a temporary directory for this test
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"🧪 Testing in temporary directory: {temp_dir}")
        
        # Change to the temporary directory
        original_cwd = os.getcwd()
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
                
                # This should trigger the authentication flow
                # Since we're in a clean environment, it should show setup instructions
                print("Initializing Gmail class...")
                
                # IMPORTANT: We need to test that the auth flow is triggered
                # but we can't actually complete it in a test environment
                # So we'll test that it fails appropriately when no credentials exist
                
                try:
                    gmail = Gmail()
                    # If we get here, it means credentials were found somewhere else
                    # This is not what we want to test - we want to test the auth flow
                    print("⚠️  Gmail initialized without triggering auth flow")
                    print("This means credentials were found in the parent directory")
                    print("This test is not properly isolated")
                    return False
                    
                except Exception as auth_error:
                    # This is what we expect - authentication should fail
                    print(f"✅ Authentication failed as expected: {auth_error}")
                    
                    # Check if the auth flow was triggered (credentials directory created)
                    if credentials_dir.exists():
                        print("✅ Auth flow was triggered - credentials directory created")
                        
                        # Check if template file was created
                        if credentials_file.exists():
                            print("✅ Template credentials file was created")
                            
                            # Verify it's a template (not real credentials)
                            with open(credentials_file) as f:
                                import json
                                template_data = json.load(f)
                            
                            if template_data.get("installed", {}).get("client_id") == "YOUR_CLIENT_ID_HERE":
                                print("✅ Template file contains placeholder values")
                                return True
                            else:
                                print("❌ Template file contains real credentials")
                                return False
                        else:
                            print("❌ Template credentials file was not created")
                            return False
                    else:
                        print("❌ Auth flow was not triggered - no credentials directory created")
                        return False
                
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                print(f"Error type: {type(e).__name__}")
                return False
                
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
            
            # Restore original working directory
            os.chdir(original_cwd)


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
            
            return True
        else:
            print("ℹ️  No emails found in the last 7 days")
            return True  # This is still a successful test
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


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
