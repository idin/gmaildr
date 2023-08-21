"""
Gmail Authentication Manager.

This module handles all OAuth2 authentication logic for Gmail API access,
separated from the main Gmail class for better organization and reusability.
"""

import os
import pickle
import logging
from typing import Optional, Tuple, Any
from datetime import datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Gmail API scopes - read and modify access to Gmail
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify'
]

logger = logging.getLogger(__name__)


class GmailAuthManager:
    """
    Manages Gmail OAuth2 authentication independently from the Gmail class.
    
    This class handles all authentication logic including:
    - Loading existing tokens
    - Refreshing expired tokens
    - Guiding users through OAuth2 setup
    - Building the Gmail service
    """
    
    def __init__(self, credentials_file: str, token_file: str):
        """
        Initialize the authentication manager.
        
        Args:
            credentials_file (str): Path to the Google OAuth2 credentials JSON file.
            token_file (str): Path to store the authentication token.
        """
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.credentials = None
        self.service = None
    
    def authenticate(self) -> Tuple[bool, Optional[Any], Optional[object]]:
        """
        Authenticate with Gmail using OAuth2.
        
        Returns:
            Tuple[bool, Optional[Credentials], Optional[object]]: 
                (success, credentials, service)
        """
        try:
            # Load existing token if available
            if os.path.exists(self.token_file):
                with open(self.token_file, 'rb') as token_file_handle:
                    self.credentials = pickle.load(token_file_handle)
            
            # If there are no (valid) credentials available, let the user log in
            if not self.credentials or not self.credentials.valid:
                if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    logger.info("Refreshing existing credentials")
                    try:
                        self.credentials.refresh(Request())
                    except Exception as refresh_error:
                        logger.error(f"Failed to refresh credentials: {refresh_error}")
                        # If refresh fails, we need new credentials
                        self.credentials = None
                
                if not self.credentials:
                    if not os.path.exists(self.credentials_file):
                        logger.error(f"Credentials file not found: {self.credentials_file}")
                        logger.info("Setting up Gmail authentication...")
                        
                        # Create credentials directory if it doesn't exist
                        credentials_dir = os.path.dirname(self.credentials_file)
                        if not os.path.exists(credentials_dir):
                            os.makedirs(credentials_dir)
                            logger.info(f"Created credentials directory: {credentials_dir}")
                        
                        # Guide user through OAuth2 setup
                        self._setup_oauth2_credentials()
                        
                        # Create a template credentials file and guide user
                        self._create_credentials_template()
                        
                        # Open browser to Google Cloud Console
                        self._open_google_cloud_console()
                        
                        # Wait for user to download and place credentials
                        print("\n" + "="*60)
                        print("🔄 Setup Instructions:")
                        print("="*60)
                        print("1. The browser should have opened to Google Cloud Console")
                        print("2. Follow the steps shown above to create credentials")
                        print("3. Download the credentials.json file")
                        print(f"4. Place it in: {self.credentials_file}")
                        print()
                        print("⏳ Waiting for credentials file...")
                        
                        # Wait for credentials file to appear (check every 2 seconds for up to 5 minutes)
                        import time
                        max_wait_time = 300  # 5 minutes
                        check_interval = 2  # 2 seconds
                        waited_time = 0
                        
                        while not os.path.exists(self.credentials_file) and waited_time < max_wait_time:
                            time.sleep(check_interval)
                            waited_time += check_interval
                            if waited_time % 10 == 0:  # Show progress every 10 seconds
                                print(f"   Still waiting... ({waited_time}s elapsed)")
                        
                        if os.path.exists(self.credentials_file):
                            logger.info("Credentials file found, continuing authentication...")
                        else:
                            print(f"\n❌ Credentials file not found after waiting {max_wait_time} seconds")
                            print("Please make sure you downloaded and placed the credentials.json file correctly.")
                            return False, None, None
                    
                    logger.info("Starting OAuth2 flow")
                    try:
                        flow = InstalledAppFlow.from_client_secrets_file(
                            self.credentials_file, SCOPES
                        )
                        self.credentials = flow.run_local_server(port=0)
                    except Exception as oauth_error:
                        logger.error(f"OAuth2 flow failed: {oauth_error}")
                        
                        # Check if it's an invalid_client error
                        if "invalid_client" in str(oauth_error).lower():
                            print("\n" + "="*60)
                            print("🔑 OAuth2 Client Invalid - Need New Credentials")
                            print("="*60)
                            print("Your OAuth2 client was deleted or is invalid.")
                            print("Let me help you get new credentials...")
                            
                            # Open browser to credentials page
                            self._open_google_cloud_console()
                            
                            print("\n📋 Steps to fix:")
                            print("1. Click on your existing 'Desktop client 1'")
                            print("2. Click the download button (⬇️) to get new credentials")
                            print("3. Replace your existing credentials.json file")
                            print(f"4. Place the new file at: {self.credentials_file}")
                            print()
                            print("⏳ Waiting for new credentials file...")
                            
                            # Wait for new credentials file
                            import time
                            max_wait_time = 300  # 5 minutes
                            check_interval = 2  # 2 seconds
                            waited_time = 0
                            
                            while not os.path.exists(self.credentials_file) and waited_time < max_wait_time:
                                time.sleep(check_interval)
                                waited_time += check_interval
                                if waited_time % 10 == 0:
                                    print(f"   Still waiting... ({waited_time}s elapsed)")
                            
                            if os.path.exists(self.credentials_file):
                                logger.info("New credentials file found, retrying authentication...")
                                # Retry the OAuth2 flow with new credentials
                                try:
                                    flow = InstalledAppFlow.from_client_secrets_file(
                                        self.credentials_file, SCOPES
                                    )
                                    self.credentials = flow.run_local_server(port=0)
                                except Exception as retry_error:
                                    logger.error(f"OAuth2 retry failed: {retry_error}")
                                    self._handle_oauth2_error(retry_error)
                                    return False, None, None
                            else:
                                print(f"\n❌ New credentials file not found after waiting {max_wait_time} seconds")
                                return False, None, None
                        else:
                            self._handle_oauth2_error(oauth_error)
                            return False, None, None
                
                # Save the credentials for the next run
                try:
                    with open(self.token_file, 'wb') as token_file_handle:
                        pickle.dump(self.credentials, token_file_handle)
                except Exception as save_error:
                    logger.error(f"Failed to save credentials: {save_error}")
                    # Continue anyway, credentials are still valid in memory
            
            # Build the service
            try:
                self.service = build('gmail', 'v1', credentials=self.credentials)
                # Test the service with a simple API call
                self.service.users().getProfile(userId='me').execute()
                logger.info("Gmail authentication successful")
                return True, self.credentials, self.service
            except HttpError as service_error:
                logger.error(f"Service build/test failed: {service_error}")
                
                # Check if it's an invalid_client error
                if "invalid_client" in str(service_error).lower():
                    print("\n" + "="*60)
                    print("🔑 OAuth2 Client Invalid - Need New Credentials")
                    print("="*60)
                    print("Your OAuth2 client was deleted or is invalid.")
                    print("Let me help you get new credentials...")
                    
                    # Open browser to credentials page
                    self._open_google_cloud_console()
                    
                    print("\n📋 Steps to fix:")
                    print("1. Click on your existing 'Desktop client 1'")
                    print("2. Click the download button (⬇️) to get new credentials")
                    print("3. Replace your existing credentials.json file")
                    print(f"4. Place the new file at: {self.credentials_file}")
                    print()
                    print("⏳ Waiting for new credentials file...")
                    
                    # Wait for new credentials file
                    import time
                    max_wait_time = 300  # 5 minutes
                    check_interval = 2  # 2 seconds
                    waited_time = 0
                    
                    while not os.path.exists(self.credentials_file) and waited_time < max_wait_time:
                        time.sleep(check_interval)
                        waited_time += check_interval
                        if waited_time % 10 == 0:
                            print(f"   Still waiting... ({waited_time}s elapsed)")
                    
                    if os.path.exists(self.credentials_file):
                        logger.info("New credentials file found, retrying authentication...")
                        # Retry the entire authentication process
                        return self.authenticate()
                    else:
                        print(f"\n❌ New credentials file not found after waiting {max_wait_time} seconds")
                        return False, None, None
                else:
                    self._handle_service_error(service_error)
                    return False, None, None
            except Exception as general_error:
                logger.error(f"General authentication error: {general_error}")
                
                # Check if it's an invalid_client error in general exceptions too
                if "invalid_client" in str(general_error).lower():
                    print("\n" + "="*60)
                    print("🔑 OAuth2 Client Invalid - Need New Credentials")
                    print("="*60)
                    print("Your OAuth2 client was deleted or is invalid.")
                    print("Let me help you get new credentials...")
                    
                    # Open browser to credentials page
                    self._open_google_cloud_console()
                    
                    print("\n📋 Steps to fix:")
                    print("1. Click on your existing 'Desktop client 1'")
                    print("2. Click the download button (⬇️) to get new credentials")
                    print("3. Replace your existing credentials.json file")
                    print(f"4. Place the new file at: {self.credentials_file}")
                    print()
                    print("⏳ Waiting for new credentials file...")
                    
                    # Wait for new credentials file
                    import time
                    max_wait_time = 300  # 5 minutes
                    check_interval = 2  # 2 seconds
                    waited_time = 0
                    
                    while not os.path.exists(self.credentials_file) and waited_time < max_wait_time:
                        time.sleep(check_interval)
                        waited_time += check_interval
                        if waited_time % 10 == 0:
                            print(f"   Still waiting... ({waited_time}s elapsed)")
                    
                    if os.path.exists(self.credentials_file):
                        logger.info("New credentials file found, retrying authentication...")
                        # Retry the entire authentication process
                        return self.authenticate()
                    else:
                        print(f"\n❌ New credentials file not found after waiting {max_wait_time} seconds")
                        return False, None, None
                else:
                    self._handle_general_error(general_error)
                    return False, None, None
                
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return False, None, None
    
    def _setup_oauth2_credentials(self) -> None:
        """
        Guide the user through OAuth2 credentials setup.
        
        This method provides step-by-step instructions for setting up
        Google OAuth2 credentials for Gmail API access.
        """
        print("\n" + "="*60)
        print("🔐 Gmail API Authentication Setup Required")
        print("="*60)
        print("\nTo use Gmail Doctor, you need to set up Google OAuth2 credentials.")
        print("Follow these steps:\n")
        
        print("1. 📋 Go to Google Cloud Console:")
        print("   https://console.cloud.google.com/")
        print()
        
        print("2. 🆕 Create a new project or select an existing one")
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
        print("   - Give it a name (e.g., 'Gmail Doctor')")
        print("   - Click 'Create'")
        print()
        
        print("5. 📥 Download the credentials:")
        print("   - Click the download button (⬇️) next to your new OAuth2 client")
        print("   - Save the JSON file as 'credentials.json'")
        print()
        
        print("6. 📁 Place the credentials file:")
        print(f"   - Move 'credentials.json' to: {self.credentials_file}")
        print()
        
        print("7. 🔄 Restart Gmail Doctor:")
        print("   - Run your Gmail code again")
        print("   - A browser window will open for authentication")
        print("   - Follow the prompts to authorize Gmail Doctor")
        print()
        
        print("📝 Note: You only need to do this setup once.")
        print("After the first authentication, Gmail Doctor will remember your credentials.")
        print()
        print("="*60)
        print("Need help? Check the documentation or create an issue on GitHub.")
        print("="*60 + "\n")
    
    def _handle_oauth2_error(self, error: Exception) -> None:
        """
        Handle OAuth2 flow errors with specific guidance.
        
        Args:
            error (Exception): The OAuth2 error that occurred.
        """
        print("\n" + "="*60)
        print("❌ OAuth2 Authentication Error")
        print("="*60)
        print(f"Error: {error}")
        print()
        print("This usually means:")
        print("  • The credentials file is invalid or corrupted")
        print("  • The OAuth2 client ID is incorrect")
        print("  • The Gmail API is not enabled in your project")
        print("  • Your Google account doesn't have permission")
        print()
        print("Please check your credentials.json file and try again.")
        print("="*60)
    
    def _handle_service_error(self, error: HttpError) -> None:
        """
        Handle Gmail service build/test errors.
        
        Args:
            error (HttpError): The service error that occurred.
        """
        print("\n" + "="*60)
        print("❌ Gmail Service Error")
        print("="*60)
        print(f"Error: {error}")
        print()
        print("This usually means:")
        print("  • The Gmail API is not enabled in your project")
        print("  • Your account doesn't have Gmail access")
        print("  • There's a network connectivity issue")
        print()
        print("Please check your Google Cloud Console settings.")
        print("="*60)
    
    def _handle_general_error(self, error: Exception) -> None:
        """
        Handle general authentication errors.
        
        Args:
            error (Exception): The general error that occurred.
        """
        print("\n" + "="*60)
        print("❌ General Authentication Error")
        print("="*60)
        print(f"Error: {error}")
        print()
        print("An unexpected error occurred during authentication.")
        print("Please check your setup and try again.")
        print("="*60)
    
    def get_credentials(self) -> Optional[Any]:
        """
        Get the current credentials.
        
        Returns:
            Optional[Credentials]: The current credentials or None.
        """
        return self.credentials
    
    def get_service(self) -> Optional[object]:
        """
        Get the current Gmail service.
        
        Returns:
            Optional[object]: The current Gmail service or None.
        """
        return self.service
    
    def _create_credentials_template(self) -> None:
        """
        Create a template credentials.json file to help users understand the format.
        """
        template_content = {
            "installed": {
                "client_id": "YOUR_CLIENT_ID_HERE",
                "project_id": "YOUR_PROJECT_ID_HERE",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_secret": "YOUR_CLIENT_SECRET_HERE",
                "redirect_uris": ["http://localhost"]
            }
        }
        
        try:
            with open(self.credentials_file, 'w') as f:
                import json
                json.dump(template_content, f, indent=2)
            print(f"✅ Created template credentials file: {self.credentials_file}")
            print("⚠️  This is just a template - you need to replace it with your actual credentials!")
        except Exception as e:
            print(f"❌ Could not create template file: {e}")
    
    def _open_google_cloud_console(self) -> None:
        """
        Open the browser to Google Cloud Console to help users set up credentials.
        """
        try:
            import webbrowser
            url = "https://console.cloud.google.com/apis/credentials"
            print(f"🌐 Opening Google Cloud Console: {url}")
            webbrowser.open(url)
        except Exception as e:
            print(f"❌ Could not open browser: {e}")
            print("Please manually go to: https://console.cloud.google.com/apis/credentials")
