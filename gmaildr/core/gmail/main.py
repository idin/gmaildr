"""
Simple Gmail class for easy email analysis.

This module provides a unified, easy-to-use interface for Gmail analysis.
"""

from typing import Optional, List, Union, Dict
import pandas as pd

from ..config.config import ConfigManager, setup_logging
from ...utils.query_builder import build_gmail_search_query
from .email_analyzer import EmailAnalyzer

"""
Inheritance chain:
GmailBase --> EmailModifier --> LabelOperator --> 
    GmailHelper --> CachedGmail --> EmailOperator --> 
        GmailSizer --> EmailProcessing --> EmailAnalyzer --> Gmail
"""

class Gmail(EmailAnalyzer):
    """
    Simple, unified Gmail analysis class.
    
    This class combines authentication, email retrieval, and analysis
    into a single, easy-to-use interface.
    
    Example:
        gmail = Gmail()
        df = gmail.get_emails(days=30)
        report = gmail.analyze(days=90)
    """
    
    # Default credential file paths - use relative paths that respect working directory
    DEFAULT_CREDENTIALS_FILE = "credentials/credentials.json"
    DEFAULT_TOKEN_FILE = "credentials/token.pickle"
    
    # Folder labels that are mutually exclusive
    FOLDER_LABELS = {'INBOX', 'SPAM', 'TRASH'}
    
    # Note: Archive is not a label - it's the absence of INBOX label
    # When an email has no folder labels, it's considered "archived"
    
    def __init__(
        self, *, 
        credentials_file: str = DEFAULT_CREDENTIALS_FILE, 
        token_file: str = DEFAULT_TOKEN_FILE,
        enable_cache: bool = True, 
        verbose: bool = False
    ):
        """
        Initialize Gmail with cache and analyzer support.
        
        Args:
            credentials_file (str): Path to Google OAuth2 credentials file.
            enable_cache (bool): Whether to enable email caching.
            verbose (bool): Whether to show detailed cache and processing messages.
        """
        
        # Initialize base class (authentication, client, and cache)
        super().__init__(
            credentials_file=credentials_file, 
            token_file=token_file,
            enable_cache=enable_cache, 
            verbose=verbose
        )
        
        # Set up configuration
        self.config_manager = ConfigManager()
        self.config = self.config_manager.get_config()
        setup_logging(self.config, verbose=verbose)
    

        
        # Update client with proper token file from config
        self.client.token_file = self.config.token_file
    
    # ============================================================================
    # EMAIL MODIFICATION METHODS (Convenience wrappers around client methods)
    # ============================================================================
    
    def move_to_trash(self, emails: Union[str, List[str], pd.DataFrame], show_progress: bool = True) -> Union[bool, Dict[str, bool]]:
        """
        Move emails to trash (add TRASH label and remove other folder labels).
        
        Args:
            emails: Single message ID, list of message IDs, or DataFrame with 'message_id' column
            show_progress: Whether to show progress bar
            
        Returns:
            bool or Dict[str, bool]: Success status
        """
        return self.modify_labels(
            emails=emails,
            add_labels=['TRASH'],
            remove_labels=list(self.FOLDER_LABELS - {'TRASH'}),
            show_progress=show_progress
        )
    
    def move_to_inbox(self, emails: Union[str, List[str], pd.DataFrame], show_progress: bool = True) -> Union[bool, Dict[str, bool]]:
        """
        Move emails to inbox (add INBOX label and remove other folder labels).
        
        Args:
            emails: Single message ID, list of message IDs, or DataFrame with 'message_id' column
            show_progress: Whether to show progress bar
            
        Returns:
            bool or Dict[str, bool]: Success status
        """
        return self.modify_labels(
            emails=emails,
            add_labels=['INBOX'],
            remove_labels=list(self.FOLDER_LABELS - {'INBOX'}),
            show_progress=show_progress
        )
    
    def _build_search_query(self, **kwargs) -> str:
        """
        Build a Gmail search query using the query builder utility.
        
        Args:
            **kwargs: Query parameters (days, start_date, end_date, in_folder, etc.)
            
        Returns:
            str: Gmail search query string
        """
        return build_gmail_search_query(**kwargs)
    
    def move_to_archive(self, emails: Union[str, List[str], pd.DataFrame], show_progress: bool = True) -> Union[bool, Dict[str, bool]]:
        """
        Move emails to archive (remove all folder labels).
        
        Args:
            emails: Single message ID, list of message IDs, or DataFrame with 'message_id' column
            show_progress: Whether to show progress bar
            
        Returns:
            bool or Dict[str, bool]: Success status
        """
        return self.modify_labels(
            emails=emails,
            remove_labels=list(self.FOLDER_LABELS),
            show_progress=show_progress
        )
    
    def move_to_spam(self, message_ids: Union[str, List[str]], show_progress: bool = True) -> Union[bool, Dict[str, bool]]:
        """
        Move emails to spam (add SPAM label and remove other folder labels).
        
        Args:
            message_ids: Single message ID or list of message IDs
            show_progress: Whether to show progress bar
            
        Returns:
            bool or Dict[str, bool]: Success status
        """
        return self.modify_labels(
            emails=message_ids,
            add_labels=['SPAM'],
            remove_labels=list(self.FOLDER_LABELS - {'SPAM'}),
            show_progress=show_progress
        )
    
    def add_label(self, emails: Union[str, List[str], pd.DataFrame], label: Union[str, List[str]], show_progress: bool = True) -> Union[bool, Dict[str, bool]]:
        """
        Add label(s) to emails.
        
        Args:
            emails: Single message ID, list of message IDs, or DataFrame with 'message_id' column
            label: Single label name or list of label names
            show_progress: Whether to show progress bar
            
        Returns:
            bool or Dict[str, bool]: Success status
        """
        return self.modify_labels(
            emails=emails,
            add_labels=label,
            show_progress=show_progress
        )
    
    def remove_label(self, emails: Union[str, List[str], pd.DataFrame], label: Union[str, List[str]], show_progress: bool = True) -> Union[bool, Dict[str, bool]]:
        """
        Remove label(s) from emails.
        
        Args:
            emails: Single message ID, list of message IDs, or DataFrame with 'message_id' column
            label: Single label name or list of label names
            show_progress: Whether to show progress bar
            
        Returns:
            bool or Dict[str, bool]: Success status
        """
        return self.modify_labels(
            emails=emails,
            remove_labels=label,
            show_progress=show_progress
        )

    def get_trash_emails(
        self, *,
        days: int = 365,
        max_emails: Optional[int] = None,
        include_text: bool = False,
        include_metrics: bool = False,
        use_batch: bool = True,
        parallelize_text_fetch: bool = False
    ) -> pd.DataFrame:
        """
        Get emails from the trash folder.
        
        Args:
            days: Number of days to look back
            max_emails: Maximum number of emails to retrieve
            include_text: Include email body text content
            include_metrics: Include content analysis metrics
            use_batch: Use Gmail API batch requests for better performance
            parallelize_text_fetch: Parallelize text content fetching
            
        Returns:
            DataFrame containing trash emails
            
        Example:
            >>> df = gmail.get_trash_emails(days=30, max_emails=100)
            >>> print(f"Found {len(df)} emails in trash")
        """
        return self.get_emails(
            days=days,
            max_emails=max_emails,
            in_folder='trash',
            include_text=include_text,
            include_metrics=include_metrics,
            use_batch=use_batch,
            parallelize_text_fetch=parallelize_text_fetch
        )
    
    def get_archive_emails(
        self, *,
        days: int = 365,
        max_emails: Optional[int] = None,
        include_text: bool = False,
        include_metrics: bool = False,
        use_batch: bool = True,
        parallelize_text_fetch: bool = False
    ) -> pd.DataFrame:
        """
        Get emails from the archive (not in inbox).
        
        Args:
            days: Number of days to look back
            max_emails: Maximum number of emails to retrieve
            include_text: Include email body text content
            include_metrics: Include content analysis metrics
            use_batch: Use Gmail API batch requests for better performance
            parallelize_text_fetch: Parallelize text content fetching
            
        Returns:
            DataFrame containing archived emails
            
        Example:
            >>> df = gmail.get_archive_emails(days=30, max_emails=100)
            >>> print(f"Found {len(df)} archived emails")
        """
        return self.get_emails(
            days=days,
            max_emails=max_emails,
            in_folder='archive',
            include_text=include_text,
            include_metrics=include_metrics,
            use_batch=use_batch,
            parallelize_text_fetch=parallelize_text_fetch
        )
    
    def get_inbox_emails(
        self, *,
        days: int = 30,
        max_emails: Optional[int] = None,
        include_text: bool = False,
        include_metrics: bool = False,
        use_batch: bool = True,
        parallelize_text_fetch: bool = False
    ) -> pd.DataFrame:
        """
        Get emails from the inbox.
        
        Args:
            days: Number of days to look back
            max_emails: Maximum number of emails to retrieve
            include_text: Include email body text content
            include_metrics: Include content analysis metrics
            use_batch: Use Gmail API batch requests for better performance
            parallelize_text_fetch: Parallelize text content fetching
            
        Returns:
            DataFrame containing inbox emails
            
        Example:
            >>> df = gmail.get_inbox_emails(days=7, max_emails=50)
            >>> print(f"Found {len(df)} emails in inbox")
        """
        return self.get_emails(
            days=days,
            max_emails=max_emails,
            in_folder='inbox',
            include_text=include_text,
            include_metrics=include_metrics,
            use_batch=use_batch,
            parallelize_text_fetch=parallelize_text_fetch
        )
