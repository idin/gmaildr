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
            from ..cache import EmailCacheManager
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
        days: int = 30,
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
            days (int): Number of days to retrieve emails from.
            max_emails (int): Maximum number of emails to retrieve.
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
        # Check if any filters are being used (including date range)
        has_filters = any([
            days is not None,  # Non-default date range
            from_sender, subject_contains, subject_does_not_contain, 
            has_attachment is not None, is_unread is not None, 
            is_important is not None, in_folder, is_starred is not None
        ])
        
        # Set default max_emails: no limit when using filters, 1000 when using defaults only
        if max_emails is None:
            max_emails = None if has_filters else 1000
        
        # Build search query using shared utility
        from ..utils.query_builder import build_gmail_search_query
        query = build_gmail_search_query(
            days=days,
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
            return pd.DataFrame()
        
        # Use cache manager if available, otherwise fall back to direct API calls
        if self.cache_manager:
            return self.cache_manager.get_emails_with_cache(
                gmail_client=self.client,
                days=days,
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
            for batch in self.client.get_messages_batch(message_ids, batch_size=25, use_api_batch=use_batch):
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
    
    @classmethod
    def _emails_to_dataframe(cls, emails: List, include_text: bool = False) -> pd.DataFrame:
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
            row = {
                'message_id': email.message_id,
                'sender_email': email.sender_email,
                'sender_name': email.sender_name,
                'subject': email.subject,
                'date_received': email.date_received,
                'size_bytes': email.size_bytes,
                'size_kb': email.size_bytes / 1024,
                'size_mb': email.size_bytes / (1024 * 1024),
                'labels': ','.join(email.labels),
                'thread_id': email.thread_id,
                'snippet': email.snippet,
                'has_attachments': email.has_attachments,
                'in_folder': cls._determine_folder(email),
                'is_read': email.is_read,
                'is_important': email.is_important,
                'year': email.date_received.year,
                'month': email.date_received.month,
                'day': email.date_received.day,
                'hour': email.date_received.hour,
                'day_of_week': email.date_received.strftime('%A'),
            }
            
            if include_text and hasattr(email, 'text_content'):
                row['text_content'] = email.text_content
            
            data.append(row)
        
        return pd.DataFrame(data)
    
    @staticmethod
    def _determine_folder(email) -> str:
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
        return self.client.modify_email_labels(message_id, add_labels, remove_labels)
    
    def mark_as_read(self, message_id: str) -> bool:
        """Mark an email as read."""
        return self.client.mark_as_read(message_id)
    
    def mark_as_unread(self, message_id: str) -> bool:
        """Mark an email as unread."""
        return self.client.mark_as_unread(message_id)
    
    def star_email(self, message_id: str) -> bool:
        """Star an email."""
        return self.client.star_email(message_id)
    
    def unstar_email(self, message_id: str) -> bool:
        """Remove star from an email."""
        return self.client.unstar_email(message_id)
    
    def move_to_trash(self, message_id: str) -> bool:
        """Move an email to trash."""
        return self.client.move_to_trash(message_id)
    
    def move_to_inbox(self, message_id: str) -> bool:
        """Move an email to inbox."""
        return self.client.move_to_inbox(message_id)
    
    def archive_email(self, message_id: str) -> bool:
        """Archive an email."""
        return self.client.archive_email(message_id)
    
    def batch_modify_labels(
        self,
        message_ids: List[str],
        add_labels: Optional[List[str]] = None,
        remove_labels: Optional[List[str]] = None,
        show_progress: bool = True
    ) -> Dict[str, bool]:
        """Modify labels for multiple email messages in batch."""
        return self.client.batch_modify_labels(message_ids, add_labels, remove_labels, show_progress)
    
    def batch_mark_as_read(self, message_ids: List[str], show_progress: bool = True) -> Dict[str, bool]:
        """Mark multiple emails as read."""
        return self.client.batch_mark_as_read(message_ids, show_progress)
    
    def batch_star_emails(self, message_ids: List[str], show_progress: bool = True) -> Dict[str, bool]:
        """Star multiple emails."""
        return self.client.batch_star_emails(message_ids, show_progress)
    
    def batch_move_to_trash(self, message_ids: List[str], show_progress: bool = True) -> Dict[str, bool]:
        """Move multiple emails to trash."""
        return self.client.batch_move_to_trash(message_ids, show_progress)
    
    def get_labels(self) -> List[Dict[str, Any]]:
        """Get all available labels in the Gmail account."""
        return self.client.get_labels()
    
    def create_label(self, name: str, label_list_visibility: str = 'labelShow') -> Optional[str]:
        """Create a new custom label."""
        return self.client.create_label(name, label_list_visibility)
    
    def delete_label(self, label_id: str) -> bool:
        """Delete a custom label."""
        return self.client.delete_label(label_id)
    
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
    
    def cleanup_cache(self, max_age_days: Optional[int] = None) -> int:
        """
        Clean up old cached emails.
        
        Args:
            max_age_days: Maximum age in days. Uses config default if None.
            
        Returns:
            Number of emails deleted.
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
