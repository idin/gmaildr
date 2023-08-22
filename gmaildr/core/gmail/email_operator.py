from datetime import datetime, timedelta
from typing import Optional, List, Union, Literal, Dict, Any
import pandas as pd
import time
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import base64

from .cached_gmail import CachedGmail
from ...analysis.language_detector import detect_language_safe
from ...utils.query_builder import build_gmail_search_query
from ...utils.progress import EmailProgressTracker
from ..config.config import ROLE_WORDS

logger = logging.getLogger(__name__)

class EmailOperator(CachedGmail):
    """
    Complex email operations that inherit from CachedGmail.
    
    This class handles complex email operations including email retrieval,
    text processing, language detection, and advanced label operations.
    """
    
    # Folder labels that are mutually exclusive
    FOLDER_LABELS = {'INBOX', 'SPAM', 'TRASH'}
    
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
            days: Number of days to retrieve emails from (default: 30, handled by query builder).
                SHOULD BE NONE if start_date and end_date are provided otherwise raises ValueError
            start_date: Start date for email search
            end_date: End date for email search
            max_emails: Maximum number of emails to retrieve
            from_sender: Filter by sender email address(es)
            subject_contains: Filter by text in subject line.
                Example: subject_contains = "Amazon & (order | tracking)"
            subject_does_not_contain: Filter by text not in subject line.
                Example: subject_does_not_contain = "Amazon & (order | tracking)"
            has_attachment: Filter by attachment presence
            is_unread: Filter by read/unread status
            is_important: Filter by importance
            in_folder: Filter by folder.
                Options: 'inbox', 'archive', 'spam', 'trash', 'drafts', 'sent'
            is_starred: Filter by starred status
            include_text: Include email body text content
            include_metrics: Include content analysis metrics (requires include_text=True)
            use_batch: Use Gmail API batch requests for better performance
            parallelize_text_fetch: Parallelize text content fetching
            
        Returns:
            DataFrame containing filtered email data
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
            return pd.DataFrame()  # Return empty pandas DataFrame instead of EmailDataFrame
        
        # Use cache manager if available, otherwise fall back to direct API calls
        if self.cache_manager:
            df = self.cache_manager.get_emails_with_cache(
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
            # Return the DataFrame directly (it's already a pandas DataFrame)
            return df
        else:
            # Fall back to direct API calls (original implementation)
            # Get detailed email information
            emails = []
            try:
                for batch in self.client.get_messages_batch(message_ids=message_ids, batch_size=25, use_api_batch=use_batch):
                    emails.extend(batch)
            except KeyboardInterrupt:
                logger.warning("Email retrieval interrupted by user. Returning partial results...")
                if not emails:
                    return pd.DataFrame()  # Return empty pandas DataFrame
            
            # Validate include_metrics requires include_text
            if include_metrics and not include_text:
                raise ValueError("include_metrics=True requires include_text=True")
            
            # Add email text content if requested (separate process)
            if include_text:
                emails = self._add_email_text(emails=emails, parallelize=parallelize_text_fetch)
            
            # Convert to DataFrame (main progress bar should complete here)
            df = self._emails_to_dataframe(emails=emails, include_text=include_text)
            
            # Return the pandas DataFrame directly
            return df
    
    def _add_email_text(self, emails: List, parallelize: bool = False) -> List:
        """
        Add email body text content to email objects.
        
        Args:
            emails (List): List of email message objects.
            parallelize (bool): Whether to use parallel processing for batch mode.
            
        Returns:
            List: List of emails with text content added.
        """
        if not parallelize:
            # Sequential processing for non-batch mode
            try:
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
            except KeyboardInterrupt:
                logger.warning("Text content retrieval interrupted by user. Returning emails with partial text content...")
                # Mark remaining emails as having no text content
                for email in emails:
                    if not hasattr(email, 'text_content') or email.text_content is None:
                        email.text_content = "Text retrieval interrupted"
        else:
            # Parallel processing for batch mode with rate limiting
            def fetch_email_text(email_obj):
                """
                Fetch text content for a single email with improved retry logic.
                
                Args:
                    email_obj: Email object to fetch text for
                    
                Returns:
                    Email object with text content populated
                """
                max_retries = 3  # Increased retries for better reliability
                base_delay = 1.0  # Reduced base delay for faster recovery
                
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
                        error_str = str(error).lower()
                        
                        # Check for specific error types
                        if 'quota' in error_str or 'rate' in error_str:
                            # Rate limiting - use exponential backoff
                            if attempt < max_retries - 1:
                                delay = base_delay * (2 ** attempt)
                                time.sleep(delay)
                                continue
                        elif 'not found' in error_str or '404' in error_str:
                            # Message not found - don't retry
                            email_obj.text_content = "Message not found or deleted"
                            return email_obj
                        elif 'forbidden' in error_str or '403' in error_str:
                            # Permission denied - don't retry
                            email_obj.text_content = "Access denied to message"
                            return email_obj
                        elif 'timeout' in error_str or 'deadline' in error_str:
                            # Timeout - retry with backoff
                            if attempt < max_retries - 1:
                                delay = base_delay * (2 ** attempt)
                                time.sleep(delay)
                                continue
                        else:
                            # Other errors - retry with backoff
                            if attempt < max_retries - 1:
                                delay = base_delay * (2 ** attempt)
                                time.sleep(delay)
                                continue
                        
                        # Final attempt failed
                        email_obj.text_content = f"Error retrieving text: {error}"
                        return email_obj
            
            # Use ThreadPoolExecutor with very limited workers to prevent kernel crashes
            # Reduce workers further for large datasets to prevent memory issues
            if len(emails) > 100:
                max_workers = 1  # Single worker for large datasets
            elif len(emails) > 50:
                max_workers = 2  # Two workers for medium datasets
            else:
                max_workers = min(3, len(emails))  # Up to 3 for small datasets
            
            try:
                with EmailProgressTracker(
                    total=len(emails),
                    description="Fetching email text"
                ) as progress:
                    with ThreadPoolExecutor(max_workers=max_workers) as executor:
                        # Process emails in smaller chunks to reduce memory usage
                        chunk_size = 25 if len(emails) > 100 else len(emails)
                        
                        for chunk_start in range(0, len(emails), chunk_size):
                            chunk_end = min(chunk_start + chunk_size, len(emails))
                            chunk_emails = emails[chunk_start:chunk_end]
                            
                            # Submit tasks for this chunk
                            future_to_email = {
                                executor.submit(fetch_email_text, email): email 
                                for email in chunk_emails
                            }
                            
                            # Process completed tasks for this chunk
                            for future in as_completed(future_to_email):
                                try:
                                    future.result()  # This will raise any exceptions
                                    progress.update(1)
                                except Exception as error:
                                    # Handle any unexpected errors
                                    email = future_to_email[future]
                                    email.text_content = f"Error retrieving text: {error}"
                                    progress.update(1)
                            
                            # Small delay between chunks to prevent overwhelming the system
                            if chunk_end < len(emails):
                                time.sleep(0.1)
            except KeyboardInterrupt:
                logger.warning("Parallel text content retrieval interrupted by user. Returning emails with partial text content...")
                # Mark remaining emails as having no text content
                for email in emails:
                    if not hasattr(email, 'text_content') or email.text_content is None:
                        email.text_content = "Text retrieval interrupted"
        
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
        def decode_data(data):
            """
            Decode base64 data.
            
            Args:
                data: Base64 encoded data string
                
            Returns:
                Decoded string
            """
            try:
                return base64.urlsafe_b64decode(data).decode('utf-8')
            except Exception:
                return ""
        
        def extract_text_from_part(part):
            """
            Extract text from message part.
            
            Args:
                part: Message part dictionary
                
            Returns:
                Extracted text content
            """
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
        Convert email objects to EmailDataFrame.
        
        🚨 CRITICAL: THIS MUST REMAIN A CLASS METHOD - DO NOT CHANGE TO INSTANCE METHOD
        REASONS:
        1. IT DOES NOT NEED INSTANCE STATE - ALL DEPENDENCIES ARE CLASS METHODS OR STATIC METHODS
        2. IT CALLS `cls._add_language_detection()` (CLASS METHOD) AND `cls._determine_folder()` (STATIC METHOD)
        3. IT CAN BE CALLED AS `self._emails_to_dataframe()` FROM INSTANCE METHODS (CLASS METHODS CAN BE CALLED ON INSTANCES)
        4. IT CAN BE CALLED AS `ClassName._emails_to_dataframe()` FOR UTILITY PURPOSES
        5. KEEPING IT AS CLASS METHOD ALLOWS FLEXIBLE USAGE WITHOUT REQUIRING INSTANCE CONTEXT
        
        THIS MUST RETURN PANDAS DATAFRAME BECAUSE:
        1. THE METHOD SHOULD BE FLEXIBLE AND NOT TIED TO A SPECIFIC DATAFRAME TYPE
        2. CALLING CODE CAN CONVERT TO EMAILDATAFRAME IF NEEDED: `EmailDataFrame(df)`
        3. THIS ALLOWS THE METHOD TO BE USED IN DIFFERENT CONTEXTS WITHOUT FORCING EMAILDATAFRAME DEPENDENCY
        4. IT FOLLOWS THE PRINCIPLE OF SEPARATION OF CONCERNS - DATA CONVERSION VS TYPE-SPECIFIC FUNCTIONALITY

        Args:
            emails (List): List of email message objects.
            include_text (bool): Whether to include text content.

        Returns:
            pd.DataFrame: DataFrame containing email data.
        """
        # Add language detection to emails
        emails = cls._add_language_detection(emails=emails, include_text=include_text)

        data = []
        for email in emails:
            row = email.to_dict(include_text=include_text)
            row['in_folder'] = cls._determine_folder(email)
            data.append(row)
        
        return pd.DataFrame(data)
    
    @classmethod
    def _add_language_detection(cls, emails: List, include_text: bool = False) -> List:
        """
        Add language detection and role-based email detection to email objects.
        
        🚨 CRITICAL: THIS MUST REMAIN A CLASS METHOD - DO NOT CHANGE TO INSTANCE METHOD
        REASONS:
        1. IT DOES NOT NEED INSTANCE STATE - IT ONLY PROCESSES EMAIL OBJECTS
        2. IT CALLS `cls._is_role_based_email()` (STATIC METHOD) - NO INSTANCE DEPENDENCIES
        3. IT CAN BE CALLED FROM CLASS METHODS LIKE `_emails_to_dataframe`
        4. IT CAN BE CALLED AS `self._add_language_detection()` FROM INSTANCE METHODS (CLASS METHODS CAN BE CALLED ON INSTANCES)
        5. KEEPING IT AS CLASS METHOD ALLOWS FLEXIBLE USAGE WITHOUT REQUIRING INSTANCE CONTEXT
        
        Args:
            emails (List): List of email message objects.
            include_text (bool): Whether text content is available.
            
        Returns:
            List: List of email message objects with language detection and role detection added.
        """
        for email in emails:
            # Detect language for subject
            if email.subject and email.subject.strip():
                subject_lang, subject_conf = detect_language_safe(email.subject)
                email.subject_language = subject_lang
                email.subject_language_confidence = subject_conf
            
            # Detect language for text content if available
            if include_text and email.text_content and email.text_content.strip():
                text_lang, text_conf = detect_language_safe(email.text_content)
                email.text_language = text_lang
                email.text_language_confidence = text_conf
            
            # Check for role-based email addresses
            email.has_role_based_email = cls._is_role_based_email(email.sender_email)
        
        return emails
    
    @staticmethod
    def _is_role_based_email(email_address: str) -> bool:
        """
        Check if an email address is role-based (likely automated/non-human).
        
        🚨 CRITICAL: THIS MUST REMAIN A STATIC METHOD - DO NOT CHANGE TO INSTANCE OR CLASS METHOD
        REASONS:
        1. IT IS A PURE FUNCTION - ONLY USES GLOBAL `ROLE_WORDS` CONSTANT
        2. IT DOES NOT NEED INSTANCE OR CLASS STATE
        3. IT CAN BE CALLED FROM CLASS METHODS AS `cls._is_role_based_email()`
        4. IT CAN BE CALLED FROM INSTANCE METHODS AS `self._is_role_based_email()`
        5. IT CAN BE CALLED DIRECTLY AS `ClassName._is_role_based_email()`
        
        Args:
            email_address (str): The email address to check.
            
        Returns:
            bool: True if the email is role-based, False otherwise.
        """
        if not email_address or '@' not in email_address:
            return False
        
        # Extract the local part (before @)
        local_part = email_address.split('@')[0].lower()
        
        # Check if the local part contains any role words
        return local_part in ROLE_WORDS
    
    @staticmethod   
    def _determine_folder(email) -> str:
        """
        Determine which folder an email is in based on its labels.
        
        🚨 CRITICAL: THIS MUST REMAIN A STATIC METHOD - DO NOT CHANGE TO INSTANCE OR CLASS METHOD
        REASONS:
        1. IT IS A PURE FUNCTION - ONLY PROCESSES EMAIL LABELS
        2. IT DOES NOT NEED INSTANCE OR CLASS STATE
        3. IT CAN BE CALLED FROM CLASS METHODS AS `cls._determine_folder()`
        4. IT CAN BE CALLED FROM INSTANCE METHODS AS `self._determine_folder()`
        5. IT CAN BE CALLED DIRECTLY AS `ClassName._determine_folder()`
        
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
    
    def modify_labels(
        self,
        message_ids: List[str],
        add_labels: Optional[Union[List[str], str]] = None,
        remove_labels: Optional[Union[List[str], str]] = None,
        show_progress: bool = True
    ) -> Dict[str, bool]:
        """
        Modify labels for multiple email messages in batch.
        
        Args:
            message_ids: List of message IDs to modify
            add_labels: Labels to add
            remove_labels: Labels to remove
            show_progress: Whether to show progress bar
            
        Returns:
            Results of label modification operations
        """
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
        
        # Invalidate cache for modified emails only
        if self.cache_manager:
            self.cache_manager.invalidate_cache(message_ids=message_ids)
        
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
                        logger.warning(f"Could not find or create label: {label}")
        
        return processed_labels
