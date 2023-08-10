"""
Gmail API client for authentication and email access.

This module provides the main interface for connecting to Gmail
and retrieving email data for analysis.
"""

import os
import pickle
import time
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Generator
import logging

from ..utils.progress import EmailProgressTracker

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import BatchHttpRequest

from ..models import EmailMessage

# Gmail API scopes - read and modify access to Gmail
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify'
]

logger = logging.getLogger(__name__)


class GmailClient:
    """
    Gmail API client for authenticating and retrieving email data.
    
    This class handles OAuth2 authentication with Gmail and provides
    methods to fetch emails with various filtering options.
    """
    
    def __init__(
        self, *,
        credentials_file: str = "credentials.json",
        token_file: str = "token.pickle"
    ):
        """
        Initialize the Gmail client.
        
        Args:
            credentials_file (str): Path to the Google OAuth2 credentials JSON file.
            token_file (str): Path to store the authentication token.
        """
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.service = None
        self.credentials = None
        
        # API access counters
        self.api_call_count = 0
        self.text_api_call_count = 0
        self.last_api_call_time = None
        
    def authenticate(self) -> bool:
        """
        Authenticate with Gmail using OAuth2.
        
        This method handles the complete OAuth2 flow, including refreshing
        existing tokens and prompting for new authorization if needed.
        
        Returns:
            bool: True if authentication was successful, False otherwise.
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
                    self.credentials.refresh(Request())
                else:
                    if not os.path.exists(self.credentials_file):
                        logger.error(f"Credentials file not found: {self.credentials_file}")
                        return False
                    
                    logger.info("Starting OAuth2 flow")
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_file, SCOPES
                    )
                    self.credentials = flow.run_local_server(port=0)
                
                # Save the credentials for the next run
                with open(self.token_file, 'wb') as token_file_handle:
                    pickle.dump(self.credentials, token_file_handle)
            
            # Build the service
            self.service = build('gmail', 'v1', credentials=self.credentials)
            # Suppress authentication success message for cleaner output
            pass  # logger.info("Gmail authentication successful")
            return True
            
        except Exception as error:
            logger.error(f"Authentication failed: {error}")
            return False
    
    def _track_api_call(self, is_text_call: bool = False) -> None:
        """
        Track API call for monitoring purposes.
        
        Args:
            is_text_call (bool): Whether this is a text content API call.
        """
        self.api_call_count += 1
        if is_text_call:
            self.text_api_call_count += 1
        self.last_api_call_time = datetime.now()
    
    def get_api_stats(self) -> Dict[str, Any]:
        """
        Get API usage statistics.
        
        Returns:
            Dictionary with API usage statistics.
        """
        return {
            'total_api_calls': self.api_call_count,
            'text_api_calls': self.text_api_call_count,
            'general_api_calls': self.api_call_count - self.text_api_call_count,
            'last_api_call': self.last_api_call_time.isoformat() if self.last_api_call_time else None
        }
    

    
    def get_user_profile(self) -> Optional[Dict[str, Any]]:
        """
        Get the authenticated user's Gmail profile information.
        
        Returns:
            Optional[Dict[str, Any]]: User profile information or None if failed.
        """
        if not self.service:
            logger.error("Not authenticated. Call authenticate() first.")
            return None
        
        try:
            profile = self.service.users().getProfile(userId='me').execute()
            return profile
        except HttpError as error:
            logger.error(f"Failed to get user profile: {error}")
            return None
    
    def search_messages(
        self, *,
        query: str = "",
        max_results: Optional[int] = None
    ) -> List[str]:
        """
        Search for Gmail messages using Gmail search syntax.
        
        Args:
            query (str): Gmail search query (e.g., "from:sender@example.com").
            max_results (Optional[int]): Maximum number of message IDs to return.
            
        Returns:
            List[str]: List of message IDs matching the search criteria.
        """
        if not self.service:
            logger.error("Not authenticated. Call authenticate() first.")
            return []
        
        try:
            message_ids = []
            page_token = None
            
            while True:
                # Execute search request
                request_params = {
                    'userId': 'me',
                    'q': query,
                    'maxResults': min(500, max_results) if max_results else 500,
                    'includeSpamTrash': True,  # Include emails from Spam and Trash folders
                }
                
                if page_token:
                    request_params['pageToken'] = page_token
                
                self._track_api_call()
                result = self.service.users().messages().list(**request_params).execute()
                
                # Extract message IDs
                messages = result.get('messages', [])
                for message in messages:
                    message_ids.append(message['id'])
                    
                    # Check if we've reached the maximum
                    if max_results and len(message_ids) >= max_results:
                        return message_ids[:max_results]
                
                # Check for next page
                page_token = result.get('nextPageToken')
                if not page_token:
                    break
            
            # Don't print found message here - we'll show it in the progress bar
            return message_ids
            
        except HttpError as error:
            logger.error(f"Failed to search messages: {error}")
            return []
    
    def get_message_details(self, message_id: str) -> Optional[EmailMessage]:
        """
        Get detailed information about a specific email message.
        
        Args:
            message_id (str): Gmail message ID.
            
        Returns:
            Optional[EmailMessage]: Email message object or None if failed.
        """
        if not self.service:
            logger.error("Not authenticated. Call authenticate() first.")
            return None
        
        try:
            # Get message details
            self._track_api_call()
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            # Extract headers
            headers = {}
            payload = message.get('payload', {})
            for header in payload.get('headers', []):
                headers[header['name'].lower()] = header['value']
            
            # Parse sender information
            sender_raw = headers.get('from', 'Unknown')
            sender_email, sender_name = self._parse_sender(sender_raw)
            
            # Parse date
            date_received = self._parse_date(headers.get('date'))
            
            # Get message size
            size_bytes = int(message.get('sizeEstimate', 0))
            
            # Get labels
            labels = message.get('labelIds', [])
            
            # Check for attachments
            has_attachments = self._has_attachments(payload)
            
            # Check read status and importance
            is_read = 'UNREAD' not in labels
            is_important = 'IMPORTANT' in labels
            
            return EmailMessage(
                message_id=message_id,
                sender_email=sender_email,
                sender_name=sender_name,
                subject=headers.get('subject', 'No Subject'),
                date_received=date_received,
                size_bytes=size_bytes,
                labels=labels,
                thread_id=message.get('threadId'),
                snippet=message.get('snippet'),
                has_attachments=has_attachments,
                is_read=is_read,
                is_important=is_important,
            )
            
        except HttpError as error:
            logger.error(f"Failed to get message details for {message_id}: {error}")
            return None
    
    def get_messages_batch(
        self, *,
        message_ids: List[str],
        batch_size: int = 100,
        use_api_batch: bool = False
    ) -> Generator[List[EmailMessage], None, None]:
        """
        Get details for multiple messages in batches.
        
        Args:
            message_ids (List[str]): List of Gmail message IDs.
            batch_size (int): Number of messages to process in each batch.
            use_api_batch (bool): Whether to use Gmail API batch requests for better performance.
            
        Yields:
            List[EmailMessage]: Batches of email message objects.
        """
        if use_api_batch:
            yield from self._get_messages_api_batch(
                message_ids=message_ids, 
                batch_size=batch_size
            )
        else:
            yield from self._get_messages_sequential(
                message_ids=message_ids, 
                batch_size=batch_size
            )
    
    def _get_messages_sequential(
        self, *,
        message_ids: List[str],
        batch_size: int = 100
    ) -> Generator[List[EmailMessage], None, None]:
        """
        Get message details using sequential API calls (original method).
        
        Args:
            message_ids (List[str]): List of Gmail message IDs.
            batch_size (int): Number of messages to process in each batch.
            
        Yields:
            List[EmailMessage]: Batches of email message objects.
        """
        total_messages = len(message_ids)
        
        # Suppress logging during progress display
        original_level = logger.getEffectiveLevel()
        logger.setLevel(logging.ERROR)
        
        try:
            with EmailProgressTracker(
                total=total_messages, 
                description="Processing emails", 
                use_batch_mode=False
            ) as tracker:
                for index in range(0, len(message_ids), batch_size):
                    batch_ids = message_ids[index:index + batch_size]
                    batch_messages = []
                    
                    for message_id in batch_ids:
                        message = self.get_message_details(message_id)
                        if message:
                            batch_messages.append(message)
                        tracker.update(1)
                    
                    yield batch_messages
        finally:
            # Restore original logging level
            logger.setLevel(original_level)

    def _get_messages_api_batch(
        self, *,
        message_ids: List[str],
        batch_size: int = 100
    ) -> Generator[List[EmailMessage], None, None]:
        """
        Get message details using Gmail API batch requests for better performance.
        
        Args:
            message_ids (List[str]): List of Gmail message IDs.
            batch_size (int): Number of messages to process in each batch.
            
        Yields:
            List[EmailMessage]: Batches of email message objects.
        """
        if not self.service:
            logger.error("Not authenticated. Call authenticate() first.")
            return
        
        # Reduce batch size to avoid rate limits
        safe_batch_size = min(batch_size, 25)  # Gmail API works better with smaller batches
        total_messages = len(message_ids)
        
        # Suppress logging during progress display
        original_level = logger.getEffectiveLevel()
        logger.setLevel(logging.ERROR)
        
        try:
            with EmailProgressTracker(
                total=total_messages, 
                description="Processing emails", 
                use_batch_mode=True
            ) as tracker:
                
                for index in range(0, len(message_ids), safe_batch_size):
                    batch_ids = message_ids[index:index + safe_batch_size]
                    batch_messages = []
                    
                    # Retry logic for rate limiting
                    max_retries = 3
                    retry_count = 0
                    
                    while retry_count < max_retries:
                        try:
                            # Create a batch request using the modern API-specific endpoint
                            batch_request = self.service.new_batch_http_request()
                            batch_responses = {}
                            rate_limited_messages = []
                            
                            def create_callback(message_id):
                                def callback(request_id, response, exception):
                                    if exception:
                                        if "rateLimitExceeded" in str(exception) or "Too many concurrent requests" in str(exception):
                                            rate_limited_messages.append(message_id)
                                        batch_responses[message_id] = None
                                    else:
                                        batch_responses[message_id] = response
                                return callback
                            
                            # Add all requests to the batch
                            for message_id in batch_ids:
                                request = self.service.users().messages().get(
                                    userId='me',
                                    id=message_id,
                                    format='full'
                                )
                                batch_request.add(request, callback=create_callback(message_id))
                            
                            # Execute the batch request
                            batch_request.execute()
                            
                            # If we have rate limited messages, retry them after a delay
                            if rate_limited_messages and retry_count < max_retries - 1:
                                retry_count += 1
                                wait_time = (2 ** retry_count) * 1.0  # Exponential backoff: 2, 4, 8 seconds
                                tracker.set_description(f"Rate limited, waiting {wait_time}s...")
                                time.sleep(wait_time)
                                tracker.set_description("Processing emails")
                                batch_ids = rate_limited_messages  # Only retry the rate-limited ones
                                continue
                            
                            # Process responses and convert to EmailMessage objects
                            for message_id in batch_ids:
                                response = batch_responses.get(message_id)
                                if response:
                                    email_message = self._convert_api_response_to_email_message(
                                        message_id=message_id, message=response
                                    )
                                    if email_message:
                                        batch_messages.append(email_message)
                            
                            # Update progress bar with attempted messages (to match total)
                            tracker.update(len(batch_ids))
                            break  # Success, exit retry loop
                            
                        except Exception as error:
                            retry_count += 1
                            if retry_count < max_retries:
                                wait_time = (2 ** retry_count) * 1.0  # Exponential backoff
                                tracker.set_description(f"Retrying batch ({retry_count}/{max_retries})...")
                                time.sleep(wait_time)
                                tracker.set_description("Processing emails")
                            else:
                                # Fall back to sequential processing for this batch
                                tracker.set_description("Fallback to sequential...")
                                fallback_count = 0
                                for message_id in batch_ids:
                                    message = self.get_message_details(message_id)
                                    if message:
                                        batch_messages.append(message)
                                        fallback_count += 1
                                
                                tracker.update(len(batch_ids))
                                tracker.set_description("Processing emails")
                                break
                    
                    yield batch_messages
                    
                    # Add a small delay between batches to be nice to the API
                    if index + safe_batch_size < len(message_ids):
                        time.sleep(0.1)  # 100ms delay between batches
        finally:
            # Restore original logging level
            logger.setLevel(original_level)

    def _convert_api_response_to_email_message(
        self, *,
        message_id: str,
        message: Dict[str, Any]
    ) -> Optional[EmailMessage]:
        """
        Convert Gmail API response to EmailMessage object.
        
        Args:
            message_id (str): Gmail message ID.
            message (Dict[str, Any]): Gmail API message response.
            
        Returns:
            Optional[EmailMessage]: Email message object or None if conversion failed.
        """
        try:
            # Extract headers
            headers = {}
            payload = message.get('payload', {})
            for header in payload.get('headers', []):
                headers[header['name'].lower()] = header['value']
            
            # Parse sender information
            sender_raw = headers.get('from', 'Unknown')
            sender_email, sender_name = self._parse_sender(sender_raw)
            
            # Parse date
            date_received = self._parse_date(headers.get('date'))
            
            # Get message size
            size_bytes = int(message.get('sizeEstimate', 0))
            
            # Get labels
            labels = message.get('labelIds', [])
            
            # Check for attachments
            has_attachments = self._has_attachments(payload)
            
            # Check read status and importance
            is_read = 'UNREAD' not in labels
            is_important = 'IMPORTANT' in labels
            
            return EmailMessage(
                message_id=message_id,
                sender_email=sender_email,
                sender_name=sender_name,
                subject=headers.get('subject', 'No Subject'),
                date_received=date_received,
                size_bytes=size_bytes,
                labels=labels,
                thread_id=message.get('threadId'),
                snippet=message.get('snippet'),
                has_attachments=has_attachments,
                is_read=is_read,
                is_important=is_important,
            )
            
        except Exception as error:
            logger.error(f"Failed to convert API response for {message_id}: {error}")
            return None
    
    def get_emails_from_date_range(
        self, *,
        start_date: datetime,
        end_date: Optional[datetime] = None,
        max_results: Optional[int] = None
    ) -> List[str]:
        """
        Get email message IDs from a specific date range.
        
        Args:
            start_date (datetime): Start date for the search.
            end_date (Optional[datetime]): End date for the search. Defaults to now.
            max_results (Optional[int]): Maximum number of messages to return.
            
        Returns:
            List[str]: List of message IDs in the date range.
        """
        if end_date is None:
            end_date = datetime.now()
        
        # Format dates for Gmail search
        start_str = start_date.strftime('%Y/%m/%d')
        end_str = end_date.strftime('%Y/%m/%d')
        
        query = f"after:{start_str} before:{end_str}"
        return self.search_messages(query=query, max_results=max_results)
    
    def _parse_sender(self, sender_raw: str) -> tuple[str, Optional[str]]:
        """
        Parse sender email and name from raw sender string.
        
        Args:
            sender_raw (str): Raw sender string from email header.
            
        Returns:
            tuple[str, Optional[str]]: Email address and display name.
        """
        import re
        
        # Pattern to match "Name <email@domain.com>" format
        match = re.match(r'^(.+?)\s*<(.+?)>$', sender_raw.strip())
        if match:
            name = match.group(1).strip(' "\'')
            email = match.group(2).strip()
            return email, name
        
        # If no name found, assume the whole string is the email
        email = sender_raw.strip(' <>"\'')
        return email, None
    
    def _parse_date(self, date_str: Optional[str]) -> datetime:
        """
        Parse date string from email header.
        
        Args:
            date_str (Optional[str]): Date string from email header.
            
        Returns:
            datetime: Parsed datetime object.
        """
        if not date_str:
            return datetime.now()
        
        try:
            from email.utils import parsedate_to_datetime
            return parsedate_to_datetime(date_str)
        except (ValueError, TypeError):
            logger.warning(f"Failed to parse date: {date_str}")
            return datetime.now()
    
    def _has_attachments(self, payload: Dict[str, Any]) -> bool:
        """
        Check if an email has attachments.
        
        Args:
            payload (Dict[str, Any]): Email payload from Gmail API.
            
        Returns:
            bool: True if the email has attachments, False otherwise.
        """
        def check_parts(parts):
            for part in parts:
                if part.get('filename'):
                    return True
                if 'parts' in part:
                    if check_parts(part['parts']):
                        return True
            return False
        
        if 'parts' in payload:
            return check_parts(payload['parts'])
        
        return bool(payload.get('filename'))
    
    # ============================================================================
    # EMAIL MODIFICATION METHODS
    # ============================================================================
    
    def modify_email_labels(
        self, *,
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
        try:
            body = {}
            if add_labels:
                body['addLabelIds'] = add_labels
            if remove_labels:
                body['removeLabelIds'] = remove_labels
            
            if not body:
                logger.warning("No labels to add or remove")
                return False
            
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body=body
            ).execute()
            
            logger.debug(f"Successfully modified labels for message {message_id}")
            return True
            
        except Exception as error:
            logger.error(f"Failed to modify labels for message {message_id}: {error}")
            return False
    
    def mark_as_read(self, message_id: str) -> bool:
        """
        Mark an email as read by removing the UNREAD label.
        
        Args:
            message_id (str): The ID of the email message to mark as read.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        return self.modify_email_labels(
            message_id=message_id, 
            remove_labels=['UNREAD']
        )
    
    def mark_as_unread(self, message_id: str) -> bool:
        """
        Mark an email as unread by adding the UNREAD label.
        
        Args:
            message_id (str): The ID of the email message to mark as unread.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        return self.modify_email_labels(
            message_id=message_id, 
            add_labels=['UNREAD']
        )
    
    def star_email(self, message_id: str) -> bool:
        """
        Star an email by adding the STARRED label.
        
        Args:
            message_id (str): The ID of the email message to star.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        return self.modify_email_labels(
            message_id=message_id, 
            add_labels=['STARRED']
        )
    
    def unstar_email(self, message_id: str) -> bool:
        """
        Remove star from an email by removing the STARRED label.
        
        Args:
            message_id (str): The ID of the email message to unstar.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        return self.modify_email_labels(
            message_id=message_id, 
            remove_labels=['STARRED']
        )
    
    def move_to_trash(self, message_id: str) -> bool:
        """
        Move an email to trash by adding the TRASH label.
        
        Args:
            message_id (str): The ID of the email message to move to trash.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        return self.modify_email_labels(message_id, add_labels=['TRASH'])
    
    def move_to_inbox(self, message_id: str) -> bool:
        """
        Move an email to inbox by adding the INBOX label and removing TRASH/SPAM.
        
        Args:
            message_id (str): The ID of the email message to move to inbox.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        return self.modify_email_labels(
            message_id, 
            add_labels=['INBOX'],
            remove_labels=['TRASH', 'SPAM']
        )
    
    def move_to_spam(self, message_id: str) -> bool:
        """
        Move an email to spam by adding the SPAM label.
        
        Args:
            message_id (str): The ID of the email message to move to spam.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        return self.modify_email_labels(message_id, add_labels=['SPAM'])
    
    def archive_email(self, message_id: str) -> bool:
        """
        Archive an email by removing the INBOX label.
        
        Args:
            message_id (str): The ID of the email message to archive.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        return self.modify_email_labels(message_id, remove_labels=['INBOX'])
    
    def batch_modify_labels(
        self, *,
        message_ids: List[str],
        add_labels: Optional[List[str]] = None,
        remove_labels: Optional[List[str]] = None,
        show_progress: bool = True
    ) -> Dict[str, bool]:
        """
        Modify labels for multiple email messages in batch.
        
        Args:
            message_ids (List[str]): List of message IDs to modify.
            add_labels (Optional[List[str]]): Labels to add to all messages.
            remove_labels (Optional[List[str]]): Labels to remove from all messages.
            show_progress (bool): Whether to show progress bar.
            
        Returns:
            Dict[str, bool]: Dictionary mapping message_id to success status.
        """
        if not message_ids:
            return {}
        
        results = {}
        body = {}
        if add_labels:
            body['addLabelIds'] = add_labels
        if remove_labels:
            body['removeLabelIds'] = remove_labels
        
        if not body:
            logger.warning("No labels to add or remove")
            return {msg_id: False for msg_id in message_ids}
        
        if show_progress:
            with EmailProgressTracker(
                total=len(message_ids),
                description="Modifying email labels"
            ) as progress:
                for message_id in message_ids:
                    try:
                        self.service.users().messages().modify(
                            userId='me',
                            id=message_id,
                            body=body
                        ).execute()
                        results[message_id] = True
                    except Exception as error:
                        logger.error(f"Failed to modify message {message_id}: {error}")
                        results[message_id] = False
                    progress.update(1)
        else:
            for message_id in message_ids:
                try:
                    self.service.users().messages().modify(
                        userId='me',
                        id=message_id,
                        body=body
                    ).execute()
                    results[message_id] = True
                except Exception as error:
                    logger.error(f"Failed to modify message {message_id}: {error}")
                    results[message_id] = False
        
        success_count = sum(results.values())
        logger.info(f"Batch modification completed: {success_count}/{len(message_ids)} successful")
        return results
    
    def batch_mark_as_read(self, *, message_ids: List[str], show_progress: bool = True) -> Dict[str, bool]:
        """
        Mark multiple emails as read.
        
        Args:
            message_ids (List[str]): List of message IDs to mark as read.
            show_progress (bool): Whether to show progress bar.
            
        Returns:
            Dict[str, bool]: Dictionary mapping message_id to success status.
        """
        return self.batch_modify_labels(message_ids, remove_labels=['UNREAD'], show_progress=show_progress)
    
    def batch_mark_as_unread(self, *, message_ids: List[str], show_progress: bool = True) -> Dict[str, bool]:
        """
        Mark multiple emails as unread.
        
        Args:
            message_ids (List[str]): List of message IDs to mark as unread.
            show_progress (bool): Whether to show progress bar.
            
        Returns:
            Dict[str, bool]: Dictionary mapping message_id to success status.
        """
        return self.batch_modify_labels(
            message_ids=message_ids, 
            add_labels=['UNREAD'], 
            show_progress=show_progress
        )
    
    def batch_star_emails(self, *, message_ids: List[str], show_progress: bool = True) -> Dict[str, bool]:
        """
        Star multiple emails.
        
        Args:
            message_ids (List[str]): List of message IDs to star.
            show_progress (bool): Whether to show progress bar.
            
        Returns:
            Dict[str, bool]: Dictionary mapping message_id to success status.
        """
        return self.batch_modify_labels(message_ids=message_ids, add_labels=['STARRED'], show_progress=show_progress)
    
    def batch_unstar_emails(self, *, message_ids: List[str], show_progress: bool = True) -> Dict[str, bool]:
        """
        Remove stars from multiple emails.
        
        Args:
            message_ids (List[str]): List of message IDs to unstar.
            show_progress (bool): Whether to show progress bar.
            
        Returns:
            Dict[str, bool]: Dictionary mapping message_id to success status.
        """
        return self.batch_modify_labels(message_ids=message_ids, remove_labels=['STARRED'], show_progress=show_progress)
    
    def batch_move_to_trash(self, *, message_ids: List[str], show_progress: bool = True) -> Dict[str, bool]:
        """
        Move multiple emails to trash.
        
        Args:
            message_ids (List[str]): List of message IDs to move to trash.
            show_progress (bool): Whether to show progress bar.
            
        Returns:
            Dict[str, bool]: Dictionary mapping message_id to success status.
        """
        return self.batch_modify_labels(message_ids=message_ids, add_labels=['TRASH'], show_progress=show_progress)
    
    def batch_move_to_inbox(self, *, message_ids: List[str], show_progress: bool = True) -> Dict[str, bool]:
        """
        Move multiple emails to inbox.
        
        Args:
            message_ids (List[str]): List of message IDs to move to inbox.
            show_progress (bool): Whether to show progress bar.
            
        Returns:
            Dict[str, bool]: Dictionary mapping message_id to success status.
        """
        return self.batch_modify_labels(
            message_ids=message_ids, 
            add_labels=['INBOX'],
            remove_labels=['TRASH', 'SPAM'],
            show_progress=show_progress
        )
    
    def batch_archive_emails(self, *, message_ids: List[str], show_progress: bool = True) -> Dict[str, bool]:
        """
        Archive multiple emails.
        
        Args:
            message_ids (List[str]): List of message IDs to archive.
            show_progress (bool): Whether to show progress bar.
            
        Returns:
            Dict[str, bool]: Dictionary mapping message_id to success status.
        """
        return self.batch_modify_labels(message_ids=message_ids, remove_labels=['INBOX'], show_progress=show_progress)
    
    def get_labels(self) -> List[Dict[str, Any]]:
        """
        Get all available labels in the Gmail account.
        
        Returns:
            List[Dict[str, Any]]: List of label objects with id, name, and type.
        """
        try:
            response = self.service.users().labels().list(userId='me').execute()
            return response.get('labels', [])
        except Exception as error:
            logger.error(f"Failed to get labels: {error}")
            return []
    
    def create_label(self, name: str, label_list_visibility: str = 'labelShow') -> Optional[str]:
        """
        Create a new custom label.
        
        Args:
            name (str): Name of the label to create.
            label_list_visibility (str): Visibility of the label ('labelShow' or 'labelHide').
            
        Returns:
            Optional[str]: The ID of the created label, or None if failed.
        """
        try:
            label_object = {
                'name': name,
                'labelListVisibility': label_list_visibility
            }
            
            response = self.service.users().labels().create(
                userId='me',
                body=label_object
            ).execute()
            
            label_id = response.get('id')
            logger.info(f"Created label '{name}' with ID: {label_id}")
            return label_id
            
        except Exception as error:
            logger.error(f"Failed to create label '{name}': {error}")
            return None
    
    def delete_label(self, label_id: str) -> bool:
        """
        Delete a custom label.
        
        Args:
            label_id (str): The ID of the label to delete.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            self.service.users().labels().delete(
                userId='me',
                id=label_id
            ).execute()
            
            logger.info(f"Deleted label with ID: {label_id}")
            return True
            
        except Exception as error:
            logger.error(f"Failed to delete label {label_id}: {error}")
            return False
