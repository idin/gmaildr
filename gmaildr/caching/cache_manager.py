"""
Main cache manager for email caching system.

Orchestrates all cache operations and provides the main interface for
cached email retrieval and storage.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Literal, Optional, Set
import shutil  
import pandas as pd

from ..analysis import process_metrics
from ..core.gmail import Gmail
from ..utils.progress import EmailProgressTracker
from .cache_config import CacheConfig
from .file_storage import EmailFileStorage
from .index_manager import EmailIndexManager
from .schema_manager import EmailSchemaManager

logger = logging.getLogger(__name__)



class EmailCacheManager:
    """
    Main cache management interface for email operations.
    
    Orchestrates caching, retrieval, and updates of email data with
    intelligent merging and schema management.
    """
    
    def __init__(
        self, *, 
        cache_config: CacheConfig,
        cache_dir: str,
        verbose: bool
    ):
        """
        Initialize cache manager.
        
        Args:
            cache_config: Cache configuration.
            cache_dir: Cache directory path.
            verbose: Whether to show detailed cache and processing messages.
        """
        self.config = cache_config
        self.cache_dir = cache_dir
        
        self.verbose = verbose
        
        self.file_storage = EmailFileStorage(cache_config=self.config)
        self.schema_manager = EmailSchemaManager(schema_version=self.config.schema_version)
        self.index_manager = EmailIndexManager(cache_config=self.config, verbose=verbose)
        
        # Build indexes on initialization
        if self.config.enable_cache:
            self.index_manager.build_indexes()
        
        # Cache access counters
        self.cache_hits = 0
        self.cache_misses = 0
        self.cache_writes = 0
        self.cache_updates = 0
    
    def _log_with_verbosity(self, message: str, level: str = "info") -> None:
        """
        Log a message to file and optionally print to console if verbose.
        
        Args:
            message: Message to log.
            level: Log level ('info', 'warning', 'error', 'debug').
        """
        # Log the message to file only
        log_method = getattr(logger, level.lower(), logger.info)
        log_method(message)
        
        # Log if verbose
        if self.verbose:
            logger.info(message)
    
    def get_emails_with_cache(
        self, *,
        gmail_client,
        gmail_instance,
        days,
        start_date,
        end_date,
        max_emails,
        from_sender,
        subject_contains,
        subject_does_not_contain,
        has_attachment,
        is_unread,
        is_important,
        in_folder,
        is_starred,
        include_text,
        include_metrics,
        use_batch,
        parallelize_text_fetch
    ) -> pd.DataFrame:
        """
        Get emails with intelligent caching.
        
        Args:
            gmail_client: GmailClient instance
            gmail_instance: Gmail instance for operations
            days: Number of days to retrieve
            start_date: Start date for search range
            end_date: End date for search range
            max_emails: Maximum number of emails to retrieve
            from_sender: Filter by sender email address(es)
            subject_contains: Filter by text in subject line
            subject_does_not_contain: Filter by text not in subject line
            has_attachment: Filter by attachment presence
            is_unread: Filter by read/unread status
            is_important: Filter by importance
            in_folder: Filter by folder
            is_starred: Filter by starred status
            include_text: Whether to include email text content
            include_metrics: Whether to include content analysis metrics
            use_batch: Whether to use batch processing
            parallelize_text_fetch: Whether to parallelize text extraction
            
        Returns:
            DataFrame with email data
        """
        if not self.config.enable_cache:
            # Fall back to direct API calls
            return self._get_emails_direct(
                gmail_client=gmail_client,
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
        
        # Calculate date range
        if start_date is not None and end_date is not None:
            # Use provided start_date and end_date
            pass
        elif days is not None:
            # Calculate from days
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
        else:
            # Default to 30 days if nothing provided
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
        
        # Build query for fresh message IDs using shared utility
        from ..utils.query_builder import build_gmail_search_query
        query = build_gmail_search_query(
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
        
        # Get fresh message IDs from Gmail
        self._log_with_verbosity("Searching Gmail API for emails...")
        fresh_message_ids = gmail_client.search_messages(
            query=query, max_results=max_emails
        )
        self._log_with_verbosity(f"Found {len(fresh_message_ids)} fresh emails from Gmail")
        
        # Get cached message IDs in date range
        self._log_with_verbosity("Checking cache for existing emails...")
        cached_message_ids = self.index_manager.get_cached_message_ids(start_date=start_date, end_date=end_date)
        self._log_with_verbosity(f"Found {len(cached_message_ids)} cached emails in date range")
        
        # Determine which emails to fetch
        new_message_ids = set(fresh_message_ids) - cached_message_ids
        self._log_with_verbosity(f"Need to fetch {len(new_message_ids)} new emails")
        
        cache_result = self._load_cached_emails(
            message_ids=cached_message_ids, 
            include_text=include_text
        )
        
        # Combine new emails and cached emails that need fresh data
        emails_to_fetch = new_message_ids | cache_result["skipped_message_ids"]
        
        # Fetch fresh emails
        fresh_emails = []
        if emails_to_fetch:
            self._log_with_verbosity(f"Starting to fetch {len(emails_to_fetch)} new emails...")
            # Track cache misses
            self._track_cache_miss()
            fresh_emails = self._fetch_new_emails(
                gmail_client=gmail_client, 
                message_ids=list(emails_to_fetch), 
                include_text=include_text, 
                use_batch=use_batch, 
                parallelize_text_fetch=parallelize_text_fetch
            )
        else:
            self._log_with_verbosity("No new emails to fetch - all data available in cache")
        
        # Merge cached and fresh emails
        all_emails = cache_result["cached_emails"] + fresh_emails
        self._log_with_verbosity(f"Total emails processed: {len(all_emails)} ({len(cache_result['cached_emails'])} from cache, {len(fresh_emails)} fresh)")
        
        # Convert to DataFrame
        if gmail_instance is None:
            from ..core.gmail import Gmail
            gmail_instance = Gmail()
        df = gmail_instance._emails_to_dataframe(emails=all_emails, include_text=include_text)
        
        # CRITICAL FIX: Apply folder filter to cached results
        # The cache returns emails based on date range, but doesn't know about folder moves
        # This post-filter ensures cached emails match the requested folder
        if in_folder is not None and not df.empty:
            original_count = len(df)
            df = df[df['in_folder'] == in_folder]
            filtered_count = len(df)
            if original_count != filtered_count:
                self._log_with_verbosity(f"Folder filter: removed {original_count - filtered_count} cached emails not in '{in_folder}' folder")
        
        # Apply max_emails limit to final result if specified
        if max_emails is not None and len(df) > max_emails:
            df = df.head(max_emails)
            self._log_with_verbosity(f"Limited final result to {len(df)} emails to respect max_emails={max_emails}")
        
        # Add metrics if requested
        if include_metrics and include_text:
            
            df = process_metrics(
                df=df, 
                include_metrics=include_metrics, 
                include_text=include_text, 
                show_progress=True
            )
        
        return df
    
    def _load_cached_emails(
        self, message_ids: Set[str], include_text: bool) -> Dict[Literal["cached_emails", "skipped_message_ids"], Any]:
        """
        Load cached emails from storage.
        
        Args:
            message_ids: Set of message IDs to load.
            include_text: Whether text content is required.
            
        Returns:
            Tuple of (list of email objects, set of message IDs that need fresh data).
        """
        cached_emails = []
        skipped_message_ids = set()
        
        with EmailProgressTracker(
            total=len(message_ids),
            description="Loading cached emails",
            unit="cached emails"
        ) as progress:
            for message_id in message_ids:
                message_info = self.index_manager.get_message_info(message_id=message_id)
                if message_info:
                    date_str = message_info["date"]
                    email_data = self.file_storage.load_email(message_id=message_id, date_str=date_str)
                    
                    if email_data:
                        # Validate and upgrade schema if needed
                        if not self.schema_manager.is_schema_valid(email_data=email_data):
                            email_data = self.schema_manager.upgrade_schema(email_data=email_data)
                        
                        # Check if all required fields are available
                        required_fields = ['message_id', 'sender_email', 'subject', 'timestamp', 'labels', 'size_bytes']
                        if include_text:
                            required_fields.append('text_content')
                        
                        missing_fields = [field for field in required_fields if field not in email_data or email_data[field] is None]
                        
                        if missing_fields:
                            # Skip this cached email - we'll fetch it fresh
                            logger.debug(f"Email {message_id} missing fields: {missing_fields}, will fetch fresh")
                            skipped_message_ids.add(message_id)
                            continue
                        
                        # Convert to email object
                        email_obj = self._dict_to_email_object(email_data=email_data)
                        cached_emails.append(email_obj)
                else:
                    # No message info found, need to fetch fresh
                    skipped_message_ids.add(message_id)
                
                progress.update(1)
        
        self._log_with_verbosity(f"Loaded {len(cached_emails)} cached emails, {len(skipped_message_ids)} need fresh data")
        
        # Track cache hits
        if len(cached_emails) > 0:
            self._track_cache_hit()
        
        return {"cached_emails": cached_emails, "skipped_message_ids": skipped_message_ids}
    
    def _fetch_new_emails(
        self, *,
        gmail_client,
        message_ids: List[str],
        include_text: bool,
        use_batch: bool,
        parallelize_text_fetch: bool
    ) -> List[Any]:
        """
        Fetch new emails from Gmail API.
        
        Args:
            gmail_client: GmailClient instance.
            message_ids: List of message IDs to fetch.
            include_text: Whether to include text content.
            use_batch: Whether to use batch processing.
            parallelize_text_fetch: Whether to parallelize text extraction.
            
        Returns:
            List of email objects.
        """
        # Fetch emails from Gmail
        emails = []
        for batch in gmail_client.get_messages_batch(
            message_ids=message_ids, 
            batch_size=25, 
            use_api_batch=use_batch
        ):
            emails.extend(batch)
        
        # Add text content if requested
        if include_text:
            # Create Gmail instance with existing client
            gmail_instance = Gmail()
            gmail_instance.client = gmail_client
            emails = gmail_instance._add_email_text(emails=emails, parallelize=parallelize_text_fetch)
        
        # Cache the new emails
        self._cache_emails(emails=emails)
        
        return emails
    
    def _cache_emails(self, emails: List[Any]) -> None:
        """
        Cache email objects to storage.
        
        Args:
            emails: List of email objects to cache.
        """
        if not self.config.enable_cache:
            return
        
        with EmailProgressTracker(
            total=len(emails),
            description="Caching emails",
            unit="emails to cache"
        ) as progress:
            for email in emails:
                # Convert to dictionary
                email_data = self._email_object_to_dict(email=email)
                
                # Add schema metadata
                email_data = self.schema_manager._add_cache_metadata(email_data=email_data)
                
                # Save to file
                date_str = email.timestamp.strftime(format="%Y-%m-%d")
                success = self.file_storage.save_email(email_data=email_data, message_id=email.message_id, date_str=date_str)
                
                if success:
                    # Update index
                    file_path = self.config.get_email_file_path(message_id=email.message_id, date_str=date_str)
                    self.index_manager.add_message_to_index(
                        message_id=email.message_id, date_str=date_str, file_path=str(file_path)
                    )
                    # Track cache write
                    self._track_cache_write()
                
                progress.update(1)
    
    def _dict_to_email_object(self, email_data: Dict[str, Any]) -> Any:
        """
        Convert dictionary to EmailMessage object.
        
        Args:
            email_data: Email data dictionary.
            
        Returns:
            EmailMessage object.
        """
        from ..core.models.email_message import EmailMessage

        # Parse timestamp
        if isinstance(email_data['timestamp'], str):
            timestamp = datetime.fromisoformat(email_data['timestamp'].replace('Z', '+00:00'))
        else:
            timestamp = email_data['timestamp']
        
        # Parse sender_local_timestamp
        if 'sender_local_timestamp' in email_data:
            if isinstance(email_data['sender_local_timestamp'], str):
                sender_local_timestamp = datetime.fromisoformat(email_data['sender_local_timestamp'].replace('Z', '+00:00'))
            else:
                sender_local_timestamp = email_data['sender_local_timestamp']
        else:
            # Fallback for old cached data that doesn't have sender_local_timestamp
            sender_local_timestamp = timestamp
        
        # Parse labels
        labels = email_data.get('labels', [])
        if isinstance(labels, str):
            labels = [label.strip() for label in labels.split(sep=',') if label.strip()]
        
        return EmailMessage(
            message_id=email_data['message_id'],
            sender_email=email_data['sender_email'],
            recipient_email=email_data['recipient_email'],
            subject=email_data['subject'],
            timestamp=timestamp,
            sender_local_timestamp=sender_local_timestamp,
            size_bytes=email_data['size_bytes'],
            sender_name=email_data['sender_name'],
            recipient_name=email_data['recipient_name'],
            labels=labels,
            thread_id=email_data['thread_id'],
            snippet=email_data['snippet'],
            has_attachments=email_data['has_attachments'],
            is_read=email_data['is_read'],
            is_important=email_data['is_important'],
            text_content=email_data['text_content']
        )
    
    def _email_object_to_dict(self, email: Any) -> Dict[str, Any]:
        """
        Convert EmailMessage object to dictionary.
        
        Args:
            email: EmailMessage object.
            
        Returns:
            Email data dictionary.
        """
        return {
            'message_id': email.message_id,
            'sender_email': email.sender_email,
            'sender_name': email.sender_name,
            'recipient_email': email.recipient_email,
            'recipient_name': email.recipient_name,
            'subject': email.subject,
            'timestamp': email.timestamp.isoformat(),
            'sender_local_timestamp': email.sender_local_timestamp.isoformat(),
            'size_bytes': email.size_bytes,
            'labels': email.labels,
            'thread_id': email.thread_id,
            'snippet': email.snippet,
            'has_attachments': email.has_attachments,
            'is_read': email.is_read,
            'is_important': email.is_important,
            'text_content': getattr(email, 'text_content', None)
        }
    
    def _get_emails_direct(
        self, *,
        gmail_client,
        days: int,
        max_emails: Optional[int],
        include_text: bool,
        include_metrics: bool,
        use_batch: bool,
        parallelize_text_fetch: bool,
        **filters
    ) -> pd.DataFrame:
        """
        Get emails directly from Gmail API (no caching).
        
        Args:
            gmail_client: GmailClient instance.
            days: Number of days to retrieve.
            max_emails: Maximum number of emails to retrieve.
            include_text: Whether to include email text content.
            include_metrics: Whether to include content analysis metrics.
            use_batch: Whether to use batch processing.
            parallelize_text_fetch: Whether to parallelize text extraction.
            **filters: Additional email filters.
            
        Returns:
            DataFrame with email data.
        """
        # Get message IDs
        message_ids = gmail_client.search_messages(
            days=days, max_results=max_emails, **filters
        )
        
        # Fetch emails
        emails = []
        for batch in gmail_client.get_messages_batch(message_ids, batch_size=25, use_api_batch=use_batch):
            emails.extend(batch)
        
        # Add text content if requested
        if include_text:
            # Create Gmail instance with existing client
            gmail_instance = Gmail()
            gmail_instance.client = gmail_client
            emails = gmail_instance._add_email_text(emails=emails, parallelize=parallelize_text_fetch)
        
        # Convert to DataFrame
        gmail_instance = Gmail()
        df = gmail_instance._emails_to_dataframe(emails=emails, include_text=include_text)
        
        # Add metrics if requested
        if include_metrics and include_text:
            df = process_metrics(
                df=df, 
                include_metrics=include_metrics, 
                include_text=include_text, 
                show_progress=True
            )
        
        return df
    

    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive cache statistics.
        
        Returns:
            Dictionary with cache statistics.
        """
        file_stats = self.file_storage.get_cache_stats()
        index_stats = self.index_manager.get_index_stats()
        config_info = self.config.get_cache_info()
        
        return {
            **file_stats,
            **index_stats,
            **config_info
        }
    
    def _track_cache_hit(self) -> None:
        """Track a cache hit."""
        self.cache_hits += 1
    
    def _track_cache_miss(self) -> None:
        """Track a cache miss."""
        self.cache_misses += 1
    
    def _track_cache_write(self) -> None:
        """Track a cache write."""
        self.cache_writes += 1
    
    def _track_cache_update(self) -> None:
        """Track a cache update."""
        self.cache_updates += 1
    
    def get_cache_access_stats(self) -> Dict[str, Any]:
        """
        Get cache access statistics.
        
        Returns:
            Dictionary with cache access statistics.
        """
        total_requests = self.cache_hits + self.cache_misses
        hit_rate = (self.cache_hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'cache_writes': self.cache_writes,
            'cache_updates': self.cache_updates,
            'total_requests': total_requests,
            'hit_rate_percent': round(hit_rate, 2),
            'cache_enabled': self.config.enable_cache
        }
    
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
            >>> cache_manager.cleanup_cache(max_age_days=30)
            15  # Deleted 15 emails older than 30 days
        """
        if max_age_days is None:
            max_age_days = self.config.max_cache_age_days
        
        deleted_count = self.file_storage.cleanup_old_emails(max_age_days=max_age_days)
        
        # Rebuild indexes after cleanup
        if deleted_count > 0:
            self.index_manager.build_indexes()
        
        return deleted_count
    
    def invalidate_cache(self, message_ids: Optional[List[str]] = None) -> bool:
        """
        Invalidate cache - either entire cache or specific message IDs.
        
        Args:
            message_ids: List of specific message IDs to invalidate.
                        If None, invalidates entire cache.
        
        Returns:
            True if successful, False otherwise.
        """
        try:
            if message_ids is None:
                # Invalidate entire cache
                

                # Remove cache directory
                if self.config.cache_dir.exists():
                    shutil.rmtree(self.config.cache_dir)
                
                # Recreate directories
                self.config._ensure_cache_directories()
                
                self._log_with_verbosity("Cache invalidated successfully")
            else:
                # Invalidate specific message IDs
                invalidated_count = 0
                for message_id in message_ids:
                    if self.file_storage.delete_email_by_id(message_id=message_id):
                        invalidated_count += 1
                
                # Rebuild indexes after selective invalidation
                if invalidated_count > 0:
                    self.index_manager.build_indexes()
                
                self._log_with_verbosity(f"Invalidated {invalidated_count} specific emails from cache")
            
            return True
            
        except Exception as error:
            logger.error(f"Failed to invalidate cache: {error}")
            return False
