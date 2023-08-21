#!/usr/bin/env python3
"""
Gmail Doctor Setup Script

This script helps you set up Gmail Doctor for first-time use.
It will guide you through the OAuth2 credentials setup process.
"""

import os
import sys
import json
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def print_header():
    """Print the setup header."""
    print("\n" + "="*60)
    print("🔐 Gmail Doctor Setup Script")
    print("="*60)
    print("This script will help you set up Gmail Doctor for first-time use.")
    print("="*60)

def check_credentials():
    """Check if credentials file exists and is valid."""
    print("\n🔐 Checking credentials file...")
    
    credentials_file = "credentials/credentials.json"
    
    if os.path.exists(credentials_file):
        try:
            with open(credentials_file, 'r') as f:
                credentials_data = json.load(f)
            
            # Check for different credential file formats
            if 'installed' in credentials_data:
                print(f"✅ Credentials file found and appears valid (Desktop application format)")
                return True, "Credentials file is valid (Desktop format)"
            elif 'client_id' in credentials_data and 'client_secret' in credentials_data:
                print(f"✅ Credentials file found and appears valid (Direct format)")
                return True, "Credentials file is valid (Direct format)"
            else:
                print(f"❌ Credentials file exists but appears invalid")
                return False, "Invalid credentials format"
        except Exception as e:
            print(f"❌ Error reading credentials file: {e}")
            return False, f"File read error: {e}"
    else:
        print(f"❌ Credentials file missing: {credentials_file}")
        return False, "Credentials file not found"

def create_credentials_directory():
    """Create the credentials directory if it doesn't exist."""
    credentials_dir = "credentials"
    if not os.path.exists(credentials_dir):
        os.makedirs(credentials_dir)
        print(f"✅ Created credentials directory: {credentials_dir}")
    else:
        print(f"✅ Credentials directory exists: {credentials_dir}")

def show_setup_instructions():
    """Show step-by-step setup instructions."""
    print("\n" + "="*60)
    print("📋 Gmail API Setup Instructions")
    print("="*60)
    print("\nFollow these steps to set up Gmail API access:\n")
    
    print("1. 📋 Go to Google Cloud Console:")
    print("   https://console.cloud.google.com/")
    print()
    
    print("2. 🆕 Create a new project or select an existing one:")
    print("   - Click on the project dropdown at the top")
    print("   - Click 'New Project' or select existing")
    print("   - Give it a name (e.g., 'GmailWiz')")
    print()
    
    print("3. 🔧 Enable the Gmail API:")
    print("   - Go to 'APIs & Services' > 'Library'")
    print("   - Search for 'Gmail API'")
    print("   - Click on it and press 'Enable'")
    print()
    
    print("4. 🔑 Create OAuth2 credentials:")
    print("   - Go to 'APIs & Services' > 'Credentials'")
    print("   - Click 'Create Credentials' > 'OAuth 2.0 Client IDs'")
    print("   - Choose 'Desktop application' as the application type")
    print("   - Give it a name (e.g., 'GmailWiz')")
    print("   - Click 'Create'")
    print()
    
    print("5. 📥 Download the credentials:")
    print("   - Click the download button (⬇️) next to your new OAuth2 client")
    print("   - Save the JSON file as 'credentials.json'")
    print()
    
    print("6. 📁 Place the credentials file:")
    print("   - Move 'credentials.json' to: credentials/credentials.json")
    print()
    
    print("7. 🔄 Run this setup script again:")
    print("   - python misc/gmail_setup.py")
    print()
    
    print("📝 Note: You only need to do this setup once.")
    print("After the first authentication, GmailWiz will remember your credentials.")
    print("="*60)

def test_authentication():
    """Test the Gmail authentication."""
    print("\n🔐 Testing Gmail authentication...")
    
    try:
        from gmaildr.core.gmail.main import Gmail
        
        # Try to initialize Gmail
        gmail = Gmail(verbose=True)
        
        # Test getting user profile
        profile = gmail.client.get_user_profile()
        if profile:
            email = profile.get('emailAddress', 'Unknown')
            total_messages = profile.get('messagesTotal', 'Unknown')
            print(f"✅ Authentication successful!")
            print(f"📧 Connected to: {email}")
            print(f"📊 Total messages in account: {total_messages:,}" if isinstance(total_messages, int) else f"📊 Total messages: {total_messages}")
            return True
        else:
            print("❌ Could not retrieve user profile")
            return False
            
    except Exception as error:
        print(f"❌ Authentication failed: {error}")
        return False

def provide_next_steps(credentials_valid):
    """Provide specific next steps based on current status."""
    print("\n" + "="*60)
    print("🔄 Next Steps")
    print("="*60)
    
    if credentials_valid:
        print("✅ Your credentials file is valid!")
        print("🔄 Now testing authentication...")
    else:
        print("❌ Credentials file is missing or invalid.")
        print("\n📋 To fix this:")
        print("1. Follow the setup instructions above")
        print("2. Download your credentials.json from Google Cloud Console")
        print("3. Place it in the credentials/ directory")
        print("4. Run this script again: python misc/gmail_setup.py")
        print("\n💡 Need help? Check the README.md file for detailed instructions.")

def main():
    """Main setup function."""
    print_header()
    
    # Create credentials directory
    create_credentials_directory()
    
    # Check if credentials exist and are valid
    credentials_valid, message = check_credentials()
    
    if credentials_valid:
        print("\n🔐 Testing authentication...")
        if test_authentication():
            print("\n" + "="*60)
            print("🎉 GmailWiz Setup Complete!")
            print("="*60)
            print("\n✅ GmailWiz is now ready to use!")
            print("\n📖 Example usage:")
            print("   from gmaildr.core.gmail.main import Gmail")
            print("   gmail = Gmail()")
            print("   emails = gmail.get_emails(days=30)")
            print("   print(f'Found {len(emails)} emails')")
            print("\n🚀 Happy email analyzing!")
            print("="*60)
        else:
            print("\n❌ Authentication test failed.")
            print("Please check your credentials file and try again.")
            provide_next_steps(False)
    else:
        show_setup_instructions()
        provide_next_steps(False)
        print("\n❌ Please complete the setup steps above and run this script again.")

if __name__ == "__main__":
    main()
