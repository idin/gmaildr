#!/usr/bin/env python3
"""
GmailWiz Diagnostic Script

This script helps diagnose authentication and setup issues with GmailWiz.
It checks various aspects of your setup and provides specific recommendations.
"""

import os
import sys
import json
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def print_header():
    """Print the diagnostic header."""
    print("\n" + "="*60)
    print("🔍 GmailWiz Diagnostic Tool")
    print("="*60)
    print("This tool will check your GmailWiz setup and identify issues.")
    print("="*60)

def check_credentials_file():
    """Check if credentials file exists and is valid."""
    print("\n🔐 Checking credentials file...")
    
    credentials_file = "credentials/credentials.json"
    
    if not os.path.exists(credentials_file):
        print(f"❌ Credentials file missing: {credentials_file}")
        return False, "Credentials file not found"
    
    try:
        with open(credentials_file, 'r') as f:
            credentials_data = json.load(f)
        
        # Check for different credential file formats
        if 'installed' in credentials_data:
            # Desktop application format
            installed_data = credentials_data['installed']
            required_fields = ['client_id', 'client_secret']
            missing_fields = []
            
            for field in required_fields:
                if field not in installed_data:
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"❌ Invalid credentials file - missing fields in 'installed' section: {missing_fields}")
                return False, f"Missing required fields: {missing_fields}"
            
            print("✅ Credentials file exists and appears valid (Desktop application format)")
            return True, "Credentials file is valid (Desktop format)"
            
        elif 'client_id' in credentials_data and 'client_secret' in credentials_data:
            # Direct format
            print("✅ Credentials file exists and appears valid (Direct format)")
            return True, "Credentials file is valid (Direct format)"
            
        else:
            print("❌ Invalid credentials file - unknown format")
            print("Expected either 'installed' section or direct 'client_id'/'client_secret' fields")
            return False, "Unknown credentials format"
        
    except json.JSONDecodeError:
        print("❌ Invalid JSON in credentials file")
        return False, "Invalid JSON format"
    except Exception as e:
        print(f"❌ Error reading credentials file: {e}")
        return False, f"File read error: {e}"

def check_token_files():
    """Check for existing token files."""
    print("\n🎫 Checking token files...")
    
    token_files = [
        "credentials/token.pickle",
        "credentials/token.json"
    ]
    
    found_tokens = []
    for token_file in token_files:
        if os.path.exists(token_file):
            found_tokens.append(token_file)
            print(f"✅ Found token file: {token_file}")
    
    if not found_tokens:
        print("ℹ️  No token files found (this is normal for first-time setup)")
        return True, "No tokens found"
    
    return True, f"Found {len(found_tokens)} token file(s)"

def check_dependencies():
    """Check if required Python packages are installed."""
    print("\n📦 Checking dependencies...")
    
    required_packages = [
        ('google.auth', 'google-auth'),
        ('google_auth_oauthlib', 'google-auth-oauthlib'),
        ('google_auth_httplib2', 'google-auth-httplib2'),
        ('googleapiclient', 'google-api-python-client'),
        ('pandas', 'pandas')
    ]
    
    missing_packages = []
    
    for import_name, package_name in required_packages:
        try:
            __import__(import_name)
            print(f"✅ {package_name}")
        except ImportError:
            print(f"❌ {package_name} - MISSING")
            missing_packages.append(package_name)
    
    if missing_packages:
        return False, f"Missing packages: {missing_packages}"
    
    return True, "All dependencies installed"

def check_network_connectivity():
    """Check basic network connectivity."""
    print("\n🌐 Checking network connectivity...")
    
    try:
        import urllib.request
        urllib.request.urlopen('https://www.google.com', timeout=5)
        print("✅ Internet connection working")
        return True, "Network connectivity OK"
    except Exception as e:
        print(f"❌ Network connectivity issue: {e}")
        return False, f"Network error: {e}"

def test_gmail_api_access():
    """Test Gmail API access with existing credentials."""
    print("\n📧 Testing Gmail API access...")
    
    try:
        from gmaildr.core.gmail_client import GmailClient
        
        client = GmailClient(
            credentials_file="credentials/credentials.json",
            token_file="credentials/token.pickle"
        )
        
        if client.authenticate():
            # Try to get user profile
            profile = client.get_user_profile()
            if profile:
                email = profile.get('emailAddress', 'Unknown')
                print(f"✅ Gmail API access successful")
                print(f"📧 Connected to: {email}")
                return True, f"Connected to {email}"
            else:
                print("❌ Could not retrieve user profile")
                return False, "Profile retrieval failed"
        else:
            print("❌ Gmail API authentication failed")
            return False, "Authentication failed"
            
    except Exception as e:
        print(f"❌ Gmail API test failed: {e}")
        return False, f"API test error: {e}"

def provide_recommendations(results):
    """Provide specific recommendations based on diagnostic results."""
    print("\n" + "="*60)
    print("💡 Recommendations")
    print("="*60)
    
    issues_found = []
    
    for test_name, (success, message) in results.items():
        if not success:
            issues_found.append((test_name, message))
    
    if not issues_found:
        print("🎉 All checks passed! Your GmailWiz setup appears to be working correctly.")
        print("\nIf you're still having issues, try:")
        print("  1. Restarting your Python environment")
        print("  2. Running: python misc/gmail_setup.py")
        print("  3. Checking the README.md for usage examples")
        return
    
    print(f"🔧 Found {len(issues_found)} issue(s) to address:")
    
    for test_name, message in issues_found:
        print(f"\n📋 {test_name}:")
        
        if test_name == "Credentials File":
            print("  • Run: python misc/gmail_setup.py")
            print("  • Follow the OAuth2 setup instructions")
            print("  • Make sure to download credentials.json from Google Cloud Console")
            
        elif test_name == "Dependencies":
            print("  • Install missing packages:")
            print("    pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client pandas")
            print("  • Or activate your conda environment: conda activate gmail")
            
        elif test_name == "Network Connectivity":
            print("  • Check your internet connection")
            print("  • Try accessing https://www.google.com in your browser")
            print("  • Check if you're behind a firewall or proxy")
            
        elif test_name == "Gmail API Access":
            print("  • Delete existing token files: rm credentials/token.*")
            print("  • Re-authenticate: python misc/gmail_setup.py")
            print("  • Check if Gmail API is enabled in Google Cloud Console")
            print("  • Verify your Google account has Gmail access")
    
    print("\n📖 For detailed setup instructions, see README.md")
    print("🆘 If issues persist, create an issue on GitHub")

def main():
    """Main diagnostic function."""
    print_header()
    
    results = {}
    
    # Run all diagnostic checks
    results["Credentials File"] = check_credentials_file()
    results["Token Files"] = check_token_files()
    results["Dependencies"] = check_dependencies()
    results["Network Connectivity"] = check_network_connectivity()
    
    # Only test Gmail API if credentials are valid
    if results["Credentials File"][0]:
        results["Gmail API Access"] = test_gmail_api_access()
    else:
        results["Gmail API Access"] = (False, "Skipped - credentials invalid")
    
    # Provide recommendations
    provide_recommendations(results)
    
    print("\n" + "="*60)
    print("🔍 Diagnostic Complete")
    print("="*60)

if __name__ == "__main__":
    main()
