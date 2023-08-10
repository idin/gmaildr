"""
Simple Gmail class for easy email analysis.

This module provides a unified, easy-to-use interface for Gmail analysis.
"""

from datetime import datetime, timedelta
from typing import Optional, List, Union, Literal, Dict, Any
import pandas as pd
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import base64

from .gmail_client import GmailClient
from ..analysis.email_analyzer import EmailAnalyzer
from ..analysis.metrics_service import MetricsService
from .config import ConfigManager, setup_logging
from ..utils.query_builder import build_gmail_search_query
from ..utils.progress import EmailProgressTracker
from ..utils.query_builder import build_gmail_search_query


class Gmail:
    """
    Simple, unified Gmail analysis class.
    
    This class combines authentication, email retrieval, and analysis
    into a single, easy-to-use interface.
    
    Example:
        gmail = Gmail()
        df = gmail.get_emails(days=30)
        report = gmail.analyze(days=90)
    """
    
    def __init__(self, *, credentials_file: str = "credentials.json", enable_cache: bool = True):
        """
        Initialize Gmail connection.
        
        Args:
            credentials_file (str): Path to Google OAuth2 credentials file.
            enable_cache (bool): Whether to enable email caching.
        """
        # Set up configuration
        self.config_manager = ConfigManager()
        self.config = self.config_manager.get_config()
        setup_logging(self.config)
        
        # Initialize Gmail client
        self.client = GmailClient(
            credentials_file=credentials_file,
            token_file=self.config.token_file
        )
        
        # Initialize analyzer
        self.analyzer = EmailAnalyzer(self.client)
        
        # Initialize cache manager if caching is enabled
        self.cache_manager = None
        if enable_cache:
            # CIRCULAR IMPORT: Cannot import at top level due to circular dependency
            from ..caching import EmailCacheManager
            self.cache_manager = EmailCacheManager()
        
        # Auto-authenticate
        self._authenticate()
    
    def _authenticate(self) -> None:
        """Authenticate with Gmail automatically."""
        if not self.client.authenticate():
            raise Exception("Gmail authentication failed. Check your credentials file.")
    
    @staticmethod  
    def _build_search_query(
        *,
        days: int,
        from_sender: Optional[Union[str, List[str]]] = None,
        subject_contains: Optional[str] = None,
        subject_does_not_contain: Optional[str] = None,
        has_attachment: Optional[bool] = None,
        is_unread: Optional[bool] = None,
        is_important: Optional[bool] = None,
        in_folder: Optional[Literal['inbox', 'archive', 'spam', 'trash', 'drafts', 'sent']] = None,
        is_starred: Optional[bool] = None
    ) -> str:
        """
        Build Gmail search query from filter parameters.
        
        Args:
            days: Number of days to search back from.
            from_sender: Filter by sender email address(es).
            subject_contains: Filter by text in subject line.
            subject_does_not_contain: Filter by text not in subject line.
            has_attachment: Filter by attachment presence.
            is_unread: Filter by read/unread status.
            is_important: Filter by importance.
            in_folder: Filter by folder.
            is_starred: Filter by starred status.
            
        Returns:
            str: Gmail search query string.
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Build Gmail search query
        query_parts = []
        query_parts.append(f"after:{start_date.strftime('%Y/%m/%d')}")
        query_parts.append(f"before:{end_date.strftime('%Y/%m/%d')}")
        
        if from_sender:
            if isinstance(from_sender, str):
                query_parts.append(f"from:{from_sender}")
            elif isinstance(from_sender, list):
                # Gmail doesn't support OR with |, so we need to use OR syntax
                sender_queries = [f"from:{sender}" for sender in from_sender]
                query_parts.append(f"({' OR '.join(sender_queries)})")
        
        if subject_contains:
            # Convert & and | to Gmail's AND and OR syntax
            gmail_subject = subject_contains.replace('&', ' AND ').replace('|', ' OR ')
            query_parts.append(f"subject:({gmail_subject})")
        
        if subject_does_not_contain:
            # Convert & and | to Gmail's AND and OR syntax, then use NOT
            gmail_subject = subject_does_not_contain.replace('&', ' AND ').replace('|', ' OR ')
            query_parts.append(f"subject:(NOT ({gmail_subject}))")
        
        if has_attachment is True:
            query_parts.append("has:attachment")
        elif has_attachment is False:
            query_parts.append("-has:attachment")
        
        if is_unread is True:
            query_parts.append("is:unread")
        elif is_unread is False:
            query_parts.append("-is:unread")
        
        if is_important is True:
            query_parts.append("is:important")
        elif is_important is False:
            query_parts.append("-is:important")
        
        # Folder filter
        if in_folder:
            if in_folder == 'archive':
                query_parts.append("-in:inbox")  # Archive means not in inbox
            else:
                query_parts.append(f"in:{in_folder}")
        
        # Starred filter
        if is_starred is True:
            query_parts.append("is:starred")
        elif is_starred is False:
            query_parts.append("-is:starred")
        
        return " ".join(query_parts)
    
    def get_emails(
        self, *,
        days: Optional[int] = None,
        start_date: Optional[Union[datetime, str]] = None,
        end_date: Optional[Union[datetime, str]] = None,
        max_emails: Optional[int] = None,
        from_sender: Optional[Union[str, List[str]]] = None,
        subject_contains: Optional[str] = None,
        subject_does_not_contain: Optional[str] = None,
        has_attachment: Optional[bool] = None,
        is_unread: Optional[bool] = None,
        is_important: Optional[bool] = None,
        in_folder: Optional[Literal['inbox', 'archive', 'spam', 'trash', 'drafts', 'sent']] = None,
        is_starred: Optional[bool] = None,
        include_text: bool = False,
        include_metrics: bool = False,
        use_batch: bool = True,
        parallelize_text_fetch: bool = False
    ) -> pd.DataFrame:
        """
        Get emails as a pandas DataFrame with filtering options.
        
        Args:
            days (Optional[int]): Number of days to retrieve emails from (default: 30, handled by query builder).
                SHOULD BE NONE if start_date and end_date are provided otherwise raises ValueError
            start_date (Optional[Union[datetime, str]]): Start date for email search.
            end_date (Optional[Union[datetime, str]]): End date for email search.
            max_emails (Optional[int]): Maximum number of emails to retrieve.
            from_sender (Optional[Union[str, List[str]]]): Filter by sender email address(es).
            subject_contains (Optional[str]): Filter by text in subject line.
                Example: subject_contains = "Amazon & (order | tracking)"
            subject_does_not_contain (Optional[str]): Filter by text not in subject line.
                Example: subject_does_not_contain = "Amazon & (order | tracking)"
            has_attachment (Optional[bool]): Filter by attachment presence.
            is_unread (Optional[bool]): Filter by read/unread status.
            is_important (Optional[bool]): Filter by importance.
            in_folder (Optional[Literal]): Filter by folder.
                Options: 'inbox', 'archive', 'spam', 'trash', 'drafts', 'sent'
            is_starred (Optional[bool]): Filter by starred status.
            include_text (bool): Include email body text content.
            include_metrics (bool): Include content analysis metrics (requires include_text=True).
            use_batch (bool): Use Gmail API batch requests for better performance.
            
        Returns:
            pd.DataFrame: DataFrame containing filtered email data.
        """
        # Check if any filters are being used (excluding date range)
        has_filters = any([
            from_sender, subject_contains, subject_does_not_contain, 
            has_attachment is not None, is_unread is not None, 
            is_important is not None, in_folder, is_starred is not None
        ])
        
        # Set default max_emails: no limit when using filters, 1000 when using defaults only
        # Always respect user's explicit max_emails parameter
        if max_emails is None:
            max_emails = None if has_filters else 1000
        
        # Build search query using shared utility
        
        query = build_gmail_search_query(
            days=days,
            start_date=start_date,
            end_date=end_date,
            from_sender=from_sender,
            subject_contains=subject_contains,
            subject_does_not_contain=subject_does_not_contain,
            has_attachment=has_attachment,
            is_unread=is_unread,
            is_important=is_important,
            in_folder=in_folder,
            is_starred=is_starred
        )
        
        # Get message IDs using the query
        message_ids = self.client.search_messages(query=query, max_results=max_emails)
        
        if not message_ids:
            from .email_dataframe import EmailDataFrame
            return EmailDataFrame(gmail_instance=self)
        
        # Use cache manager if available, otherwise fall back to direct API calls
        if self.cache_manager:
            return self.cache_manager.get_emails_with_cache(
                gmail_client=self.client,
                gmail_instance=self,
                days=days,
                start_date=start_date,
                end_date=end_date,
                max_emails=max_emails,
                include_text=include_text,
                include_metrics=include_metrics,
                use_batch=use_batch,
                parallelize_text_fetch=parallelize_text_fetch,
                from_sender=from_sender,
                subject_contains=subject_contains,
                subject_does_not_contain=subject_does_not_contain,
                has_attachment=has_attachment,
                is_unread=is_unread,
                is_important=is_important,
                in_folder=in_folder,
                is_starred=is_starred
            )
        else:
            # Fall back to direct API calls (original implementation)
            # Get detailed email information
            emails = []
            for batch in self.client.get_messages_batch(message_ids=message_ids, batch_size=25, use_api_batch=use_batch):
                emails.extend(batch)
            
            # Validate include_metrics requires include_text
            if include_metrics and not include_text:
                raise ValueError("include_metrics=True requires include_text=True")
            
            # Add email text content if requested (separate process)
            if include_text:
                emails = self._add_email_text(emails=emails, parallelize=parallelize_text_fetch)
            
            # Convert to DataFrame (main progress bar should complete here)
            df = self._emails_to_dataframe(emails=emails, include_text=include_text)
            
            # Add content analysis metrics if requested (separate process)
            if include_metrics and include_text:
                df = MetricsService.process_metrics(
                    df=df, 
                    include_metrics=include_metrics, 
                    include_text=include_text, 
                    show_progress=True
                )
            
            return df
    
    def get_api_stats(self) -> Dict[str, Any]:
        """
        Get API usage statistics from the Gmail client.
        
        Returns:
            Dictionary with API usage statistics.
        """
        return self.client.get_api_stats()
    
    def get_cache_access_stats(self) -> Dict[str, Any]:
        """
        Get cache access statistics.
        
        Returns:
            Dictionary with cache access statistics.
        """
        if self.cache_manager:
            return self.cache_manager.get_cache_access_stats()
        else:
            return {
                'cache_hits': 0,
                'cache_misses': 0,
                'cache_writes': 0,
                'cache_updates': 0,
                'total_requests': 0,
                'hit_rate_percent': 0.0,
                'cache_enabled': False
            }
    
    def analyze(
        self, *,
        days: int = 30, 
        max_emails: Optional[int] = None
    ):
        """
        Run comprehensive email analysis.
        
        Args:
            days (int): Number of days to analyze.
            max_emails (int): Maximum number of emails to analyze.
            
        Returns:
            AnalysisReport: Complete analysis report.
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        return self.analyzer.analyze_emails_from_date_range(
            start_date=start_date,
            end_date=end_date,
            max_emails=max_emails,
            batch_size=100
        )
    
    def top_senders(self, *, limit: int = 10, days: int = 30) -> List:
        """
        Get top email senders.
        
        Args:
            limit (int): Number of top senders to return.
            days (int): Number of days to analyze.
            
        Returns:
            List: List of top senders with their statistics.
        """
        report = self.analyze(days=days)
        return report.get_top_senders_by_count(limit)
    
    def storage_analysis(self, days: int = 30) -> dict:
        """
        Get storage usage analysis.
        
        Args:
            days (int): Number of days to analyze.
            
        Returns:
            dict: Storage analysis results.
        """
        # Need to run analysis first to populate cache
        self.analyze(days=days)
        return self.analyzer.get_storage_analysis()
    
    def temporal_analysis(self, days: int = 30) -> dict:
        """
        Get temporal email patterns.
        
        Args:
            days (int): Number of days to analyze.
            
        Returns:
            dict: Temporal analysis results.
        """
        # Need to run analysis first to populate cache
        self.analyze(days=days)
        return self.analyzer.get_temporal_analysis()
    
    @property
    def email(self) -> str:
        """Get the connected Gmail email address."""
        profile = self.client.get_user_profile()
        return profile.get('emailAddress', 'Unknown') if profile else 'Unknown'
    
    @property
    def total_messages(self) -> int:
        """Get total number of messages in the Gmail account."""
        profile = self.client.get_user_profile()
        return profile.get('messagesTotal', 0) if profile else 0
    
    def _add_email_text(self, emails: List, parallelize: bool = False) -> List:
        """
        Add email body text content to email objects.
        
        Args:
            emails (List): List of email message objects.
            use_batch (bool): Whether to use parallel processing for batch mode.
            
        Returns:
            List: List of emails with text content added.
        """
        if not parallelize:
            # Sequential processing for non-batch mode
            for email in emails:
                try:
                    # Get full message details including body
                    self.client._track_api_call(is_text_call=True)
                    message = self.client.service.users().messages().get(
                        userId='me',
                        id=email.message_id,
                        format='full'
                    ).execute()
                    
                    # Extract text content
                    email.text_content = self._extract_email_text(message)
                    
                except Exception as error:
                    email.text_content = f"Error retrieving text: {error}"
        else:
            # Parallel processing for batch mode with rate limiting
            from concurrent.futures import ThreadPoolExecutor, as_completed
            import time
            
            def fetch_email_text(email_obj):
                """Fetch text content for a single email with retry logic."""
                max_retries = 2  # Reduced retries
                base_delay = 2.0  # Increased base delay
                
                for attempt in range(max_retries):
                    try:
                        # Add small delay between requests to prevent overwhelming
                        if attempt > 0:
                            time.sleep(0.5)
                        
                        # Get full message details including body
                        self.client._track_api_call(is_text_call=True)
                        message = self.client.service.users().messages().get(
                            userId='me',
                            id=email_obj.message_id,
                            format='full'
                        ).execute()
                        
                        # Extract text content
                        email_obj.text_content = self._extract_email_text(message)
                        return email_obj
                        
                    except Exception as error:
                        if attempt < max_retries - 1:
                            # Exponential backoff for rate limiting
                            delay = base_delay * (2 ** attempt)
                            time.sleep(delay)
                            continue
                        else:
                            email_obj.text_content = f"Error retrieving text: {error}"
                            return email_obj
            
            # Use ThreadPoolExecutor with very limited workers to prevent kernel crashes
            max_workers = min(3, len(emails))  # Limit to 3 concurrent requests
            
            with EmailProgressTracker(
                total=len(emails),
                description="Fetching email text"
            ) as progress:
                with ThreadPoolExecutor(max_workers=max_workers) as executor:
                    # Submit all tasks
                    future_to_email = {
                        executor.submit(fetch_email_text, email): email 
                        for email in emails
                    }
                    
                    # Process completed tasks
                    for future in as_completed(future_to_email):
                        try:
                            future.result()  # This will raise any exceptions
                            progress.update(1)
                        except Exception as error:
                            # Handle any unexpected errors
                            email = future_to_email[future]
                            email.text_content = f"Error retrieving text: {error}"
                            progress.update(1)
        
        return emails
    
    @staticmethod
    def _extract_email_text(message: dict) -> str:
        """
        Extract text content from Gmail message.
        
        Args:
            message (dict): Gmail message object.
            
        Returns:
            str: Extracted text content.
        """
        import base64
        
        def decode_data(data):
            """Decode base64 data."""
            try:
                return base64.urlsafe_b64decode(data).decode('utf-8')
            except Exception:
                return ""
        
        def extract_text_from_part(part):
            """Extract text from message part."""
            if part.get('mimeType') == 'text/plain':
                data = part.get('body', {}).get('data')
                if data:
                    return decode_data(data)
            elif part.get('mimeType') == 'text/html':
                # For HTML, we could strip tags, but for now just return as is
                data = part.get('body', {}).get('data')
                if data:
                    return decode_data(data)
            elif 'parts' in part:
                # Recursively extract from multipart
                texts = []
                for subpart in part['parts']:
                    text = extract_text_from_part(subpart)
                    if text:
                        texts.append(text)
                return '\n'.join(texts)
            return ""
        
        payload = message.get('payload', {})
        
        # Try to extract text content
        if 'parts' in payload:
            return extract_text_from_part(payload)
        else:
            return extract_text_from_part(payload)
    
    def _emails_to_dataframe(self, emails: List, include_text: bool = False) -> pd.DataFrame:
        """
        Convert email objects to pandas DataFrame.
        
        Args:
            emails (List): List of email message objects.
            include_text (bool): Whether to include text content.
            
        Returns:
            pd.DataFrame: DataFrame containing email data.
        """
        data = []
        for email in emails:
            row = email.to_dict(include_text=include_text)
            row['in_folder'] = self._determine_folder(email)
            data.append(row)
        
        from .email_dataframe import EmailDataFrame
        df = EmailDataFrame(data=data, gmail_instance=self)
        return df
    
    def _determine_folder(self, email) -> str:
        """
        Determine which folder an email is in based on its labels.
        
        Args:
            email: EmailMessage object with labels.
            
        Returns:
            str: The folder name ('inbox', 'sent', 'drafts', 'spam', 'trash', 'archive').
        """
        labels = email.labels if email.labels else []
        
        # Check for specific folders
        if 'SENT' in labels:
            return 'sent'
        elif 'DRAFT' in labels:
            return 'drafts'
        elif 'SPAM' in labels:
            return 'spam'
        elif 'TRASH' in labels:
            return 'trash'
        elif 'INBOX' in labels:
            return 'inbox'
        else:
            # If not in inbox but not in other folders, likely archived
            return 'archive'
    
    # ============================================================================
    # EMAIL MODIFICATION METHODS (Convenience wrappers around client methods)
    # ============================================================================
    
    def modify_email_labels(
        self,
        message_id: str,
        add_labels: Optional[List[str]] = None,
        remove_labels: Optional[List[str]] = None
    ) -> bool:
        """
        Modify labels for a single email message.
        
        Args:
            message_id (str): The ID of the email message to modify.
            add_labels (Optional[List[str]]): Labels to add to the message.
            remove_labels (Optional[List[str]]): Labels to remove from the message.
            
        Returns:
            bool: True if modification was successful, False otherwise.
        """
        return self.client.modify_email_labels(message_id=message_id, add_labels=add_labels, remove_labels=remove_labels)
    
    def mark_as_read(self, message_id: Union[str, List[str]], show_progress: bool = True) -> Union[bool, Dict[str, bool]]:
        """Mark email(s) as read."""
        if isinstance(message_id, str):
            return self.client.mark_as_read(message_id)
        else:
            return self.client.batch_mark_as_read(message_ids=message_id, show_progress=show_progress)
    
    def mark_as_unread(self, message_id: str) -> bool:
        """Mark an email as unread."""
        return self.client.mark_as_unread(message_id)
    
    def star_email(self, message_id: Union[str, List[str]], show_progress: bool = True) -> Union[bool, Dict[str, bool]]:
        """Star email(s)."""
        if isinstance(message_id, str):
            return self.client.star_email(message_id)
        else:
            return self.client.batch_star_emails(message_ids=message_id, show_progress=show_progress)
    
    def unstar_email(self, message_id: str) -> bool:
        """Remove star from an email."""
        return self.client.unstar_email(message_id)
    
    def move_to_trash(self, message_id: Union[str, List[str]], show_progress: bool = True) -> Union[bool, Dict[str, bool]]:
        """Move email(s) to trash."""
        if isinstance(message_id, str):
            return self.client.move_to_trash(message_id)
        else:
            return self.client.batch_move_to_trash(message_ids=message_id, show_progress=show_progress)
    
    def move_to_inbox(self, message_id: str) -> bool:
        """Move an email to inbox."""
        return self.client.move_to_inbox(message_id)
    
    def archive_email(self, message_id: str) -> bool:
        """Archive an email."""
        return self.client.archive_email(message_id)
    
    def move_to_archive(self, message_ids: Union[str, List[str]], show_progress: bool = True) -> Union[bool, Dict[str, bool]]:
        """
        Move emails to archive (remove INBOX and TRASH labels).
        
        Args:
            message_ids: Single message ID or list of message IDs
            show_progress: Whether to show progress bar
            
        Returns:
            bool or Dict[str, bool]: Success status
        """
        if isinstance(message_ids, str):
            message_ids = [message_ids]
        return self.modify_labels(
            message_ids=message_ids,
            remove_labels=['INBOX', 'TRASH'],
            show_progress=show_progress
        )
    
    def add_label(self, message_ids: Union[str, List[str]], label: Union[str, List[str]], show_progress: bool = True) -> Union[bool, Dict[str, bool]]:
        """
        Add label(s) to emails.
        
        Args:
            message_ids: Single message ID or list of message IDs
            label: Single label name or list of label names
            show_progress: Whether to show progress bar
            
        Returns:
            bool or Dict[str, bool]: Success status
        """
        if isinstance(message_ids, str):
            message_ids = [message_ids]
        return self.modify_labels(
            message_ids=message_ids,
            add_labels=label,
            show_progress=show_progress
        )
    
    def remove_label(self, message_ids: Union[str, List[str]], label: Union[str, List[str]], show_progress: bool = True) -> Union[bool, Dict[str, bool]]:
        """
        Remove label(s) from emails.
        
        Args:
            message_ids: Single message ID or list of message IDs
            label: Single label name or list of label names
            show_progress: Whether to show progress bar
            
        Returns:
            bool or Dict[str, bool]: Success status
        """
        if isinstance(message_ids, str):
            message_ids = [message_ids]
        return self.modify_labels(
            message_ids=message_ids,
            remove_labels=label,
            show_progress=show_progress
        )
    
    def modify_labels(
        self,
        message_ids: List[str],
        add_labels: Optional[Union[List[str], str]] = None,
        remove_labels: Optional[Union[List[str], str]] = None,
        show_progress: bool = True
    ) -> Dict[str, bool]:
        """Modify labels for multiple email messages in batch."""
        if isinstance(add_labels, str):
            add_labels = [add_labels]
        if isinstance(remove_labels, str):
            remove_labels = [remove_labels]
        
        # Convert label names to IDs if needed
        processed_add_labels = self._process_labels_for_api(add_labels) if add_labels else None
        processed_remove_labels = self._process_labels_for_api(remove_labels) if remove_labels else None
        
        result = self.client.batch_modify_labels(
            message_ids=message_ids,
            add_labels=processed_add_labels,
            remove_labels=processed_remove_labels,
            show_progress=show_progress
        )
        
        # Invalidate cache after label modifications to ensure fresh data
        if self.cache_manager:
            self.cache_manager.invalidate_cache()
        
        return result
    


    def _process_labels_for_api(self, labels: List[str]) -> List[str]:
        """
        Process labels for Gmail API - convert names to IDs for custom labels.
        
        Args:
            labels: List of label names or IDs
            
        Returns:
            List of processed labels (names for system labels, IDs for custom labels)
        """
        if not labels:
            return []
        
        processed_labels = []
        for label in labels:
            # System labels (INBOX, SENT, etc.) use names
            if label.upper() in ['INBOX', 'SENT', 'DRAFT', 'SPAM', 'TRASH', 'STARRED', 'UNREAD', 'IMPORTANT']:
                processed_labels.append(label)
            else:
                # Custom labels need ID conversion
                label_id = self.get_label_id(label)
                if label_id:
                    processed_labels.append(label_id)
                else:
                    # If label doesn't exist, try to create it
                    label_id = self.create_label(label)
                    if label_id:
                        processed_labels.append(label_id)
                    else:
                        print(f"Warning: Could not find or create label: {label}")
        
        return processed_labels
    
    def get_labels(self) -> List[Dict[str, Any]]:
        """Get all available labels in the Gmail account."""
        return self.client.get_labels()
    
    def create_label(self, name: str, label_list_visibility: str = 'labelShow') -> Optional[str]:
        """Create a new custom label."""
        return self.client.create_label(name, label_list_visibility)
    
    def delete_label(self, label_id: str) -> bool:
        """Delete a custom label."""
        return self.client.delete_label(label_id)
    
    def get_label_id(self, label_name: str) -> Optional[str]:
        """
        Get the ID of a label by name.
        
        Args:
            label_name (str): Name of the label to find
            
        Returns:
            Optional[str]: Label ID if found, None otherwise
            
        Example:
            >>> gmail.get_label_id('INBOX')
            'INBOX'
            >>> gmail.get_label_id('wiz_trash')
            'Label_123456789'
        """
        labels = self.get_labels()
        for label in labels:
            if label.get('name') == label_name:
                return label.get('id')
        return None
    
    def has_label(self, label_name: str) -> bool:
        """
        Check if a label exists in the Gmail account.
        
        Args:
            label_name (str): Name of the label to check
            
        Returns:
            bool: True if label exists, False otherwise
            
        Example:
            >>> gmail.has_label('INBOX')
            True
            >>> gmail.has_label('wiz_trash')
            False
        """
        return self.get_label_id(label_name) is not None
    
    def get_label_id_or_create(self, label_name: str, label_list_visibility: str = 'labelShow') -> Optional[str]:
        """
        Get the ID of a label by name, creating it if it doesn't exist.
        
        Args:
            label_name (str): Name of the label to find or create
            label_list_visibility (str): Label list visibility setting for new labels
            
        Returns:
            Optional[str]: Label ID if found or created successfully, None if failed
            
        Example:
            >>> gmail.get_label_id_or_create('wiz_trash')
            'Label_123456789'
            >>> gmail.get_label_id_or_create('INBOX')
            'INBOX'
        """
        # First try to get existing label ID
        label_id = self.get_label_id(label_name)
        if label_id:
            return label_id
        
        # If label doesn't exist, create it
        return self.create_label(label_name, label_list_visibility)
    
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
            days (int): Number of days to look back (default: 365)
            max_emails (Optional[int]): Maximum number of emails to retrieve
            include_text (bool): Include email body text content
            include_metrics (bool): Include content analysis metrics
            use_batch (bool): Use Gmail API batch requests for better performance
            parallelize_text_fetch (bool): Parallelize text content fetching
            
        Returns:
            pd.DataFrame: DataFrame containing trash emails
            
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
            days (int): Number of days to look back (default: 365)
            max_emails (Optional[int]): Maximum number of emails to retrieve
            include_text (bool): Include email body text content
            include_metrics (bool): Include content analysis metrics
            use_batch (bool): Use Gmail API batch requests for better performance
            parallelize_text_fetch (bool): Parallelize text content fetching
            
        Returns:
            pd.DataFrame: DataFrame containing archived emails
            
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
            days (int): Number of days to look back (default: 30)
            max_emails (Optional[int]): Maximum number of emails to retrieve
            include_text (bool): Include email body text content
            include_metrics (bool): Include content analysis metrics
            use_batch (bool): Use Gmail API batch requests for better performance
            parallelize_text_fetch (bool): Parallelize text content fetching
            
        Returns:
            pd.DataFrame: DataFrame containing inbox emails
            
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
    
    def get_inbox_size(
        self, *,
        days: int = 365,
        from_sender: Optional[Union[str, List[str]]] = None,
        subject_contains: Optional[str] = None,
        subject_does_not_contain: Optional[str] = None,
        has_attachment: Optional[bool] = None,
        is_unread: Optional[bool] = None,
        is_important: Optional[bool] = None,
        is_starred: Optional[bool] = None
    ) -> int:
        """
        Get the count of emails in the inbox.
        
        Args:
            days (int): Number of days to look back (default: 365)
            from_sender: Filter by sender email address(es)
            subject_contains: Filter by text in subject line
            subject_does_not_contain: Filter by text not in subject line
            has_attachment: Filter by attachment presence
            is_unread: Filter by read/unread status
            is_important: Filter by importance
            is_starred: Filter by starred status
            
        Returns:
            int: Number of emails in inbox
            
        Example:
            >>> count = gmail.get_inbox_size(days=30, is_unread=True)
            >>> print(f"Inbox has {count} unread emails")
        """
        return self.count_emails(
            days=days,
            in_folder='inbox',
            from_sender=from_sender,
            subject_contains=subject_contains,
            subject_does_not_contain=subject_does_not_contain,
            has_attachment=has_attachment,
            is_unread=is_unread,
            is_important=is_important,
            is_starred=is_starred
        )
    
    def get_trash_size(
        self, *,
        days: int = 365,
        from_sender: Optional[Union[str, List[str]]] = None,
        subject_contains: Optional[str] = None,
        subject_does_not_contain: Optional[str] = None,
        has_attachment: Optional[bool] = None,
        is_unread: Optional[bool] = None,
        is_important: Optional[bool] = None,
        is_starred: Optional[bool] = None
    ) -> int:
        """
        Get the count of emails in the trash.
        
        Args:
            days (int): Number of days to look back (default: 365)
            from_sender: Filter by sender email address(es)
            subject_contains: Filter by text in subject line
            subject_does_not_contain: Filter by text not in subject line
            has_attachment: Filter by attachment presence
            is_unread: Filter by read/unread status
            is_important: Filter by importance
            is_starred: Filter by starred status
            
        Returns:
            int: Number of emails in trash
            
        Example:
            >>> count = gmail.get_trash_size(days=30, has_attachment=True)
            >>> print(f"Trash has {count} emails with attachments")
        """
        return self.count_emails(
            days=days,
            in_folder='trash',
            from_sender=from_sender,
            subject_contains=subject_contains,
            subject_does_not_contain=subject_does_not_contain,
            has_attachment=has_attachment,
            is_unread=is_unread,
            is_important=is_important,
            is_starred=is_starred
        )
    
    def get_archive_size(
        self, *,
        days: int = 365,
        from_sender: Optional[Union[str, List[str]]] = None,
        subject_contains: Optional[str] = None,
        subject_does_not_contain: Optional[str] = None,
        has_attachment: Optional[bool] = None,
        is_unread: Optional[bool] = None,
        is_important: Optional[bool] = None,
        is_starred: Optional[bool] = None
    ) -> int:
        """
        Get the count of emails in the archive (not in inbox).
        
        Args:
            days (int): Number of days to look back (default: 365)
            from_sender: Filter by sender email address(es)
            subject_contains: Filter by text in subject line
            subject_does_not_contain: Filter by text not in subject line
            has_attachment: Filter by attachment presence
            is_unread: Filter by read/unread status
            is_important: Filter by importance
            is_starred: Filter by starred status
            
        Returns:
            int: Number of emails in archive
            
        Example:
            >>> count = gmail.get_archive_size(days=30, from_sender='example@gmail.com')
            >>> print(f"Archive has {count} emails from example@gmail.com")
        """
        return self.count_emails(
            days=days,
            in_folder='archive',
            from_sender=from_sender,
            subject_contains=subject_contains,
            subject_does_not_contain=subject_does_not_contain,
            has_attachment=has_attachment,
            is_unread=is_unread,
            is_important=is_important,
            is_starred=is_starred
        )
    
    def count_emails(
        self, *,
        days: int = 365,
        from_sender: Optional[Union[str, List[str]]] = None,
        subject_contains: Optional[str] = None,
        subject_does_not_contain: Optional[str] = None,
        has_attachment: Optional[bool] = None,
        is_unread: Optional[bool] = None,
        is_important: Optional[bool] = None,
        in_folder: Optional[Literal['inbox', 'archive', 'spam', 'trash', 'drafts', 'sent']] = None,
        is_starred: Optional[bool] = None
    ) -> int:
        """
        Count emails based on specified filters.
        
        Args:
            days (int): Number of days to look back (default: 365)
            from_sender: Filter by sender email address(es)
            subject_contains: Filter by text in subject line
            subject_does_not_contain: Filter by text not in subject line
            has_attachment: Filter by attachment presence
            is_unread: Filter by read/unread status
            is_important: Filter by importance
            in_folder: Filter by folder
            is_starred: Filter by starred status
            
        Returns:
            int: Number of emails matching the filters
            
        Example:
            >>> count = gmail.count_emails(days=30, from_sender='example@gmail.com')
            >>> print(f"Found {count} emails from example@gmail.com")
        """
        return len(self.get_emails(
            days=days,
            max_emails=None,
            from_sender=from_sender,
            subject_contains=subject_contains,
            subject_does_not_contain=subject_does_not_contain,
            has_attachment=has_attachment,
            is_unread=is_unread,
            is_important=is_important,
            in_folder=in_folder,
            is_starred=is_starred,
            include_text=False,
            include_metrics=False,
            use_batch=True
        ))
    
    # ============================================================================
    # CACHE MANAGEMENT METHODS
    # ============================================================================
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive cache statistics.
        
        Returns:
            Dictionary with cache statistics.
        """
        if not self.cache_manager:
            return {"error": "Cache not enabled"}
        return self.cache_manager.get_cache_stats()
    
    def cleanup_cache(self, max_age_days: Optional[int] = -1) -> int:
        """
        Clean up old cached emails by deleting emails older than specified days.
        
        This method removes cached email files that are older than the specified
        number of days, helping to manage disk space and keep cache fresh.
        
        Args:
            max_age_days: Maximum age in days before emails are deleted.
                         If None, uses the default from cache configuration.
                         
                         Examples:
                         - max_age_days=7: Delete emails older than 1 week
                         - max_age_days=30: Delete emails older than 1 month
                         - max_age_days=90: Delete emails older than 3 months
            
        Returns:
            Number of emails deleted from cache.
            
        Example:
            >>> gmail.cleanup_cache(max_age_days=30)
            15  # Deleted 15 emails older than 30 days
        """
        if not self.cache_manager:
            return 0
        return self.cache_manager.cleanup_cache(max_age_days)
    
    def invalidate_cache(self) -> bool:
        """
        Invalidate entire cache (delete all cached data).
        
        Returns:
            True if successful, False otherwise.
        """
        if not self.cache_manager:
            return False
        return self.cache_manager.invalidate_cache()
    
    def rebuild_cache_indexes(self) -> bool:
        """
        Rebuild cache indexes.
        
        Returns:
            True if successful, False otherwise.
        """
        if not self.cache_manager:
            return False
        return self.cache_manager.index_manager.build_indexes()
