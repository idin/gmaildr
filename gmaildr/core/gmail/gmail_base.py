
import sys
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
            sys.stdout.write("\n" + "="*60 + "\n"); sys.stdout.flush()
            sys.stdout.write("❌ Gmail Authentication Failed" + "\n"); sys.stdout.flush()
            sys.stdout.write("="*60 + "\n"); sys.stdout.flush()
            sys.stdout.write("\nThe authentication process could not complete successfully." + "\n"); sys.stdout.flush()
            sys.stdout.write("This usually means:" + "\n"); sys.stdout.flush()
            sys.stdout.write("  • The credentials file is missing or invalid" + "\n"); sys.stdout.flush()
            sys.stdout.write("  • The OAuth2 setup was not completed" + "\n"); sys.stdout.flush()
            sys.stdout.write("  • There was a network connectivity issue" + "\n"); sys.stdout.flush()
            sys.stdout.write("  • The Gmail API is not enabled" + "\n"); sys.stdout.flush()
            sys.stdout.write("  • Your account doesn't have permission" + "\n"); sys.stdout.flush()
            sys.stdout.write( + "\n"); sys.stdout.flush()
            sys.stdout.write("Please ensure you have:" + "\n"); sys.stdout.flush()
            sys.stdout.write("  1. A valid credentials.json file in the credentials/ directory" + "\n"); sys.stdout.flush()
            sys.stdout.write("  2. Gmail API enabled in Google Cloud Console" + "\n"); sys.stdout.flush()
            sys.stdout.write("  3. An active internet connection" + "\n"); sys.stdout.flush()
            sys.stdout.write( + "\n"); sys.stdout.flush()
            sys.stdout.write("💡 Quick Setup:" + "\n"); sys.stdout.flush()
            sys.stdout.write("  Run: python setup_gmail.py" + "\n"); sys.stdout.flush()
            sys.stdout.write("  This will guide you through the entire setup process" + "\n"); sys.stdout.flush()
            sys.stdout.write("="*60 + "\n"); sys.stdout.flush()
            raise Exception("Gmail authentication failed. Run 'python setup_gmail.py' to set up credentials.")
    
    def get_api_stats(self) -> Dict[str, Any]:
        """
        Get API usage statistics from the Gmail client.
        
        Returns:
            Dictionary with API usage statistics.
        """
        return self.client.get_api_stats()