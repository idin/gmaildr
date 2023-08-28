"""
Gmail Authentication Manager.

This module handles all OAuth2 authentication logic for Gmail API access,
separated from the main Gmail class for better organization and reusability.
"""

import os
import pickle
import logging
import sys
import time
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
                        sys.stdout.write("\n" + "="*60 + "\n" + "\n"); sys.stdout.flush()
                        sys.stdout.write("🔄 Setup Instructions:\n" + "\n"); sys.stdout.flush()
                        sys.stdout.write("="*60 + "\n" + "\n"); sys.stdout.flush()
                        sys.stdout.write("1. The browser should have opened to Google Cloud Console\n" + "\n"); sys.stdout.flush()
                        sys.stdout.write("2. Follow the steps shown above to create credentials\n" + "\n"); sys.stdout.flush()
                        sys.stdout.write("3. Download the credentials.json file\n" + "\n"); sys.stdout.flush()
                        sys.stdout.write(f"4. Place it in: {self.credentials_file}\n" + "\n"); sys.stdout.flush()
                        sys.stdout.write("\n" + "\n"); sys.stdout.flush()
                        sys.stdout.write("⏳ Waiting for credentials file...\n" + "\n"); sys.stdout.flush()
                        sys.stdout.flush()
                        
                        # Wait for credentials file to appear (check every 2 seconds for up to 5 minutes)
                        max_wait_time = 300  # 5 minutes
                        check_interval = 2  # 2 seconds
                        waited_time = 0
                        
                        while not os.path.exists(self.credentials_file) and waited_time < max_wait_time:
                            time.sleep(check_interval)
                            waited_time += check_interval
                            if waited_time % 10 == 0:  # Show progress every 10 seconds
                                sys.stdout.write(f"   Still waiting... ({waited_time}s elapsed)\n"); sys.stdout.flush()
                        
                        if os.path.exists(self.credentials_file):
                            logger.info("Credentials file found, continuing authentication...")
                        else:
                            sys.stdout.write(f"\n❌ Credentials file not found after waiting {max_wait_time} seconds\n" + "\n"); sys.stdout.flush()
                            sys.stdout.write("Please make sure you downloaded and placed the credentials.json file correctly.\n"); sys.stdout.flush()
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
                            sys.stdout.write("\n" + "="*60 + "\n" + "\n"); sys.stdout.flush()
                            sys.stdout.write("🔑 OAuth2 Client Invalid - Need New Credentials\n" + "\n"); sys.stdout.flush()
                            sys.stdout.write("="*60 + "\n" + "\n"); sys.stdout.flush()
                            sys.stdout.write("Your OAuth2 client was deleted or is invalid.\n" + "\n"); sys.stdout.flush()
                            sys.stdout.write("Let me help you get new credentials...\n"); sys.stdout.flush()
                            
                            # Open browser to credentials page
                            self._open_google_cloud_console()
                            
                            sys.stdout.write("\n📋 Steps to fix:\n" + "\n"); sys.stdout.flush()
                            sys.stdout.write("1. Click on your existing 'Desktop client 1'\n" + "\n"); sys.stdout.flush()
                            sys.stdout.write("2. Click the download button (⬇️) to get new credentials\n")
                            sys.stdout.write("3. Replace your existing credentials.json file\n" + "\n"); sys.stdout.flush()
                            sys.stdout.write(f"4. Place the new file at: {self.credentials_file}\n" + "\n"); sys.stdout.flush()
                            sys.stdout.write("\n" + "\n"); sys.stdout.flush()
                            sys.stdout.write("⏳ Waiting for new credentials file...\n"); sys.stdout.flush()
                            
                            # Wait for new credentials file
                            max_wait_time = 300  # 5 minutes
                            check_interval = 2  # 2 seconds
                            waited_time = 0
                            
                            while not os.path.exists(self.credentials_file) and waited_time < max_wait_time:
                                time.sleep(check_interval)
                                waited_time += check_interval
                                if waited_time % 10 == 0:
                                    sys.stdout.write(f"   Still waiting... ({waited_time}s elapsed)\n"); sys.stdout.flush()
                            
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
                                sys.stdout.write(f"\n❌ New credentials file not found after waiting {max_wait_time} seconds" + "\n"); sys.stdout.flush()
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
                    sys.stdout.write("\n" + "="*60 + "\n"); sys.stdout.flush()
                    sys.stdout.write("🔑 OAuth2 Client Invalid - Need New Credentials" + "\n"); sys.stdout.flush()
                    sys.stdout.write("="*60 + "\n"); sys.stdout.flush()
                    sys.stdout.write("Your OAuth2 client was deleted or is invalid." + "\n"); sys.stdout.flush()
                    sys.stdout.write("Let me help you get new credentials..." + "\n"); sys.stdout.flush()
                    
                    # Open browser to credentials page
                    self._open_google_cloud_console()
                    
                    sys.stdout.write("\n📋 Steps to fix:" + "\n"); sys.stdout.flush()
                    sys.stdout.write("1. Click on your existing 'Desktop client 1'" + "\n"); sys.stdout.flush()
                    sys.stdout.write("2. Click the download button (⬇️) to get new credentials")
                    sys.stdout.write("3. Replace your existing credentials.json file" + "\n"); sys.stdout.flush()
                    sys.stdout.write(f"4. Place the new file at: {self.credentials_file}" + "\n"); sys.stdout.flush()
                    sys.stdout.write( + "\n"); sys.stdout.flush()
                    sys.stdout.write("⏳ Waiting for new credentials file..." + "\n"); sys.stdout.flush()
                    
                    # Wait for new credentials file
                    import time
                    max_wait_time = 300  # 5 minutes
                    check_interval = 2  # 2 seconds
                    waited_time = 0
                    
                    while not os.path.exists(self.credentials_file) and waited_time < max_wait_time:
                        time.sleep(check_interval)
                        waited_time += check_interval
                        if waited_time % 10 == 0:
                            sys.stdout.write(f"   Still waiting... ({waited_time}s elapsed)")
                    
                    if os.path.exists(self.credentials_file):
                        logger.info("New credentials file found, retrying authentication...")
                        # Retry the entire authentication process
                        return self.authenticate()
                    else:
                        sys.stdout.write(f"\n❌ New credentials file not found after waiting {max_wait_time} seconds" + "\n"); sys.stdout.flush()
                        return False, None, None
                else:
                    self._handle_service_error(service_error)
                    return False, None, None
            except Exception as general_error:
                logger.error(f"General authentication error: {general_error}")
                
                # Check if it's an invalid_client error in general exceptions too
                if "invalid_client" in str(general_error).lower():
                    sys.stdout.write("\n" + "="*60 + "\n"); sys.stdout.flush()
                    sys.stdout.write("🔑 OAuth2 Client Invalid - Need New Credentials" + "\n"); sys.stdout.flush()
                    sys.stdout.write("="*60 + "\n"); sys.stdout.flush()
                    sys.stdout.write("Your OAuth2 client was deleted or is invalid." + "\n"); sys.stdout.flush()
                    sys.stdout.write("Let me help you get new credentials..." + "\n"); sys.stdout.flush()
                    
                    # Open browser to credentials page
                    self._open_google_cloud_console()
                    
                    sys.stdout.write("\n📋 Steps to fix:" + "\n"); sys.stdout.flush()
                    sys.stdout.write("1. Click on your existing 'Desktop client 1'" + "\n"); sys.stdout.flush()
                    sys.stdout.write("2. Click the download button (⬇️) to get new credentials")
                    sys.stdout.write("3. Replace your existing credentials.json file" + "\n"); sys.stdout.flush()
                    sys.stdout.write(f"4. Place the new file at: {self.credentials_file}" + "\n"); sys.stdout.flush()
                    sys.stdout.write( + "\n"); sys.stdout.flush()
                    sys.stdout.write("⏳ Waiting for new credentials file..." + "\n"); sys.stdout.flush()
                    
                    # Wait for new credentials file
                    import time
                    max_wait_time = 300  # 5 minutes
                    check_interval = 2  # 2 seconds
                    waited_time = 0
                    
                    while not os.path.exists(self.credentials_file) and waited_time < max_wait_time:
                        time.sleep(check_interval)
                        waited_time += check_interval
                        if waited_time % 10 == 0:
                            sys.stdout.write(f"   Still waiting... ({waited_time}s elapsed)")
                    
                    if os.path.exists(self.credentials_file):
                        logger.info("New credentials file found, retrying authentication...")
                        # Retry the entire authentication process
                        return self.authenticate()
                    else:
                        sys.stdout.write(f"\n❌ New credentials file not found after waiting {max_wait_time} seconds" + "\n"); sys.stdout.flush()
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
        sys.stdout.write("\n" + "="*60 + "\n"); sys.stdout.flush()
        sys.stdout.write("🔐 Gmail API Authentication Setup Required" + "\n"); sys.stdout.flush()
        sys.stdout.write("="*60 + "\n"); sys.stdout.flush()
        sys.stdout.write("\nTo use Gmail Doctor, you need to set up Google OAuth2 credentials." + "\n"); sys.stdout.flush()
        sys.stdout.write("Follow these steps:\n" + "\n"); sys.stdout.flush()
        
        sys.stdout.write("1. 📋 Go to Google Cloud Console:" + "\n"); sys.stdout.flush()
        sys.stdout.write("   https://console.cloud.google.com/" + "\n"); sys.stdout.flush()
        sys.stdout.write( + "\n"); sys.stdout.flush()
        
        sys.stdout.write("2. 🆕 Create a new project or select an existing one" + "\n"); sys.stdout.flush()
        sys.stdout.write( + "\n"); sys.stdout.flush()
        
        sys.stdout.write("3. 🔧 Enable the Gmail API:" + "\n"); sys.stdout.flush()
        sys.stdout.write("   - Go to 'APIs & Services' > 'Library'" + "\n"); sys.stdout.flush()
        sys.stdout.write("   - Search for 'Gmail API'" + "\n"); sys.stdout.flush()
        sys.stdout.write("   - Click on it and press 'Enable'" + "\n"); sys.stdout.flush()
        sys.stdout.write( + "\n"); sys.stdout.flush()
        
        sys.stdout.write("4. 🔑 Create OAuth2 credentials:" + "\n"); sys.stdout.flush()
        sys.stdout.write("   - Go to 'APIs & Services' > 'Credentials'" + "\n"); sys.stdout.flush()
        sys.stdout.write("   - Click 'Create Credentials' > 'OAuth 2.0 Client IDs'" + "\n"); sys.stdout.flush()
        sys.stdout.write("   - Choose 'Desktop application' as the application type" + "\n"); sys.stdout.flush()
        sys.stdout.write("   - Give it a name (e.g., 'Gmail Doctor')")
        sys.stdout.write("   - Click 'Create'" + "\n"); sys.stdout.flush()
        sys.stdout.write( + "\n"); sys.stdout.flush()
        
        sys.stdout.write("5. 📥 Download the credentials:" + "\n"); sys.stdout.flush()
        sys.stdout.write("   - Click the download button (⬇️) next to your new OAuth2 client")
        sys.stdout.write("   - Save the JSON file as 'credentials.json'" + "\n"); sys.stdout.flush()
        sys.stdout.write( + "\n"); sys.stdout.flush()
        
        sys.stdout.write("6. 📁 Place the credentials file:" + "\n"); sys.stdout.flush()
        sys.stdout.write(f"   - Move 'credentials.json' to: {self.credentials_file}" + "\n"); sys.stdout.flush()
        sys.stdout.write( + "\n"); sys.stdout.flush()
        
        sys.stdout.write("7. 🔄 Restart Gmail Doctor:" + "\n"); sys.stdout.flush()
        sys.stdout.write("   - Run your Gmail code again" + "\n"); sys.stdout.flush()
        sys.stdout.write("   - A browser window will open for authentication" + "\n"); sys.stdout.flush()
        sys.stdout.write("   - Follow the prompts to authorize Gmail Doctor" + "\n"); sys.stdout.flush()
        sys.stdout.write( + "\n"); sys.stdout.flush()
        
        sys.stdout.write("📝 Note: You only need to do this setup once." + "\n"); sys.stdout.flush()
        sys.stdout.write("After the first authentication, Gmail Doctor will remember your credentials." + "\n"); sys.stdout.flush()
        sys.stdout.write( + "\n"); sys.stdout.flush()
        sys.stdout.write("="*60 + "\n"); sys.stdout.flush()
        sys.stdout.write("Need help? Check the documentation or create an issue on GitHub." + "\n"); sys.stdout.flush()
        sys.stdout.write("="*60 + "\n" + "\n"); sys.stdout.flush()
    
    def _handle_oauth2_error(self, error: Exception) -> None:
        """
        Handle OAuth2 flow errors with specific guidance.
        
        Args:
            error (Exception): The OAuth2 error that occurred.
        """
        sys.stdout.write("\n" + "="*60 + "\n"); sys.stdout.flush()
        sys.stdout.write("❌ OAuth2 Authentication Error" + "\n"); sys.stdout.flush()
        sys.stdout.write("="*60 + "\n"); sys.stdout.flush()
        sys.stdout.write(f"Error: {error}" + "\n"); sys.stdout.flush()
        sys.stdout.write( + "\n"); sys.stdout.flush()
        sys.stdout.write("This usually means:" + "\n"); sys.stdout.flush()
        sys.stdout.write("  • The credentials file is invalid or corrupted" + "\n"); sys.stdout.flush()
        sys.stdout.write("  • The OAuth2 client ID is incorrect" + "\n"); sys.stdout.flush()
        sys.stdout.write("  • The Gmail API is not enabled in your project" + "\n"); sys.stdout.flush()
        sys.stdout.write("  • Your Google account doesn't have permission" + "\n"); sys.stdout.flush()
        sys.stdout.write( + "\n"); sys.stdout.flush()
        sys.stdout.write("Please check your credentials.json file and try again." + "\n"); sys.stdout.flush()
        sys.stdout.write("="*60 + "\n"); sys.stdout.flush()
    
    def _handle_service_error(self, error: HttpError) -> None:
        """
        Handle Gmail service build/test errors.
        
        Args:
            error (HttpError): The service error that occurred.
        """
        sys.stdout.write("\n" + "="*60 + "\n"); sys.stdout.flush()
        sys.stdout.write("❌ Gmail Service Error" + "\n"); sys.stdout.flush()
        sys.stdout.write("="*60 + "\n"); sys.stdout.flush()
        sys.stdout.write(f"Error: {error}" + "\n"); sys.stdout.flush()
        sys.stdout.write( + "\n"); sys.stdout.flush()
        sys.stdout.write("This usually means:" + "\n"); sys.stdout.flush()
        sys.stdout.write("  • The Gmail API is not enabled in your project" + "\n"); sys.stdout.flush()
        sys.stdout.write("  • Your account doesn't have Gmail access" + "\n"); sys.stdout.flush()
        sys.stdout.write("  • There's a network connectivity issue" + "\n"); sys.stdout.flush()
        sys.stdout.write( + "\n"); sys.stdout.flush()
        sys.stdout.write("Please check your Google Cloud Console settings." + "\n"); sys.stdout.flush()
        sys.stdout.write("="*60 + "\n"); sys.stdout.flush()
    
    def _handle_general_error(self, error: Exception) -> None:
        """
        Handle general authentication errors.
        
        Args:
            error (Exception): The general error that occurred.
        """
        sys.stdout.write("\n" + "="*60 + "\n"); sys.stdout.flush()
        sys.stdout.write("❌ General Authentication Error" + "\n"); sys.stdout.flush()
        sys.stdout.write("="*60 + "\n"); sys.stdout.flush()
        sys.stdout.write(f"Error: {error}" + "\n"); sys.stdout.flush()
        sys.stdout.write( + "\n"); sys.stdout.flush()
        sys.stdout.write("An unexpected error occurred during authentication." + "\n"); sys.stdout.flush()
        sys.stdout.write("Please check your setup and try again." + "\n"); sys.stdout.flush()
        sys.stdout.write("="*60 + "\n"); sys.stdout.flush()
    
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
            sys.stdout.write(f"✅ Created template credentials file: {self.credentials_file}" + "\n"); sys.stdout.flush()
            sys.stdout.write("⚠️  This is just a template - you need to replace it with your actual credentials!" + "\n"); sys.stdout.flush()
        except Exception as e:
            sys.stdout.write(f"❌ Could not create template file: {e}" + "\n"); sys.stdout.flush()
    
    def _open_google_cloud_console(self) -> None:
        """
        Open the browser to Google Cloud Console to help users set up credentials.
        """
        try:
            import webbrowser
            url = "https://console.cloud.google.com/apis/credentials"
            sys.stdout.write(f"🌐 Opening Google Cloud Console: {url}" + "\n"); sys.stdout.flush()
            webbrowser.open(url)
        except Exception as e:
            sys.stdout.write(f"❌ Could not open browser: {e}" + "\n"); sys.stdout.flush()
            sys.stdout.write("Please manually go to: https://console.cloud.google.com/apis/credentials" + "\n"); sys.stdout.flush()
