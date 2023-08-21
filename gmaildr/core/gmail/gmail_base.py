
from typing import Dict, Any
from ..client.gmail_client import GmailClient


class GmailBase:
    """
    Base Gmail class with minimal dependencies.
    
    Only provides basic authentication and client access.
    No dependencies on config, caching, analysis, or other modules.
    """
    
    def __init__(self, *, credentials_file: str, token_file: str, verbose: bool):
        """
        Initialize Gmail connection with minimal dependencies.
        All Gmail classes other than the main one should not have default values for any of the arguments.
        
        Args:
            credentials_file (str): Path to Google OAuth2 credentials file.
            token_file (str): Path to store the authentication token.
            verbose (bool): Whether to show detailed messages. Defaults to False.
        """
        self.verbose = verbose
        
        # Initialize Gmail client with minimal setup
        self.client = GmailClient(
            credentials_file=credentials_file,
            token_file=token_file
        )
        
        # Auto-authenticate
        self._authenticate()
    
    def _authenticate(self) -> None:
        """Authenticate with Gmail automatically."""
        if not self.client.authenticate():
            print("\n" + "="*60)
            print("❌ Gmail Authentication Failed")
            print("="*60)
            print("\nThe authentication process could not complete successfully.")
            print("This usually means:")
            print("  • The credentials file is missing or invalid")
            print("  • The OAuth2 setup was not completed")
            print("  • There was a network connectivity issue")
            print("  • The Gmail API is not enabled")
            print("  • Your account doesn't have permission")
            print()
            print("Please ensure you have:")
            print("  1. A valid credentials.json file in the credentials/ directory")
            print("  2. Gmail API enabled in Google Cloud Console")
            print("  3. An active internet connection")
            print()
            print("💡 Quick Setup:")
            print("  Run: python setup_gmail.py")
            print("  This will guide you through the entire setup process")
            print("="*60)
            raise Exception("Gmail authentication failed. Run 'python setup_gmail.py' to set up credentials.")
    
    def get_api_stats(self) -> Dict[str, Any]:
        """
        Get API usage statistics from the Gmail client.
        
        Returns:
            Dictionary with API usage statistics.
        """
        return self.client.get_api_stats()