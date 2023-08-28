from typing import Optional, List, Union, Dict
import pandas as pd
import logging
from .gmail_base import GmailBase

logger = logging.getLogger(__name__)

class EmailModifier(GmailBase):
    """
    Basic email modification operations that only depend on GmailBase.
    
    This class handles simple email operations like marking as read/unread,
    starring/unstarring, and basic label modifications that only require
    the Gmail client (no cache, analyzer, or other dependencies).
    """
    
    def modify_email_labels(
        self,
        message_id: str,
        add_labels: Optional[List[str]] = None,
        remove_labels: Optional[List[str]] = None
    ) -> bool:
        """
        Modify labels for a single email message.
        
        Args:
            message_id: The ID of the email message to modify
            add_labels: Labels to add to the message
            remove_labels: Labels to remove from the message
            
        Returns:
            True if modification was successful, False otherwise
        """
        return self.client.modify_email_labels(message_id=message_id, add_labels=add_labels, remove_labels=remove_labels)
    
    def get_message_ids(self, emails: Union[str, List[str], pd.DataFrame]) -> List[str]:
        """
        Get message IDs from emails.
        
        Args:
            emails: Single message ID, list of message IDs, or DataFrame with message_id column
            
        Returns:
            List of message IDs extracted from the input
        """
        if isinstance(emails, pd.DataFrame):
            if not 'message_id' in emails.columns:
                raise KeyError("DataFrame must have 'message_id' column")
            return emails['message_id'].tolist()
        elif isinstance(emails, str):
            return [emails]
        else:
            return emails
    
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
                # Custom labels need ID conversion - only available in subclasses with get_label_id
                if hasattr(self, 'get_label_id'):
                    label_id = self.get_label_id(label)
                    if label_id:
                        processed_labels.append(label_id)
                    elif hasattr(self, 'create_label'):
                        # If label doesn't exist, try to create it
                        label_id = self.create_label(label)
                        if label_id:
                            processed_labels.append(label_id)
                        else:
                            logger.warning(f"Could not find or create label: {label}")
                    else:
                        logger.warning(f"Could not find or create label: {label}")
                else:
                    # For base class, just use the label name as-is
                    processed_labels.append(label)
        
        return processed_labels
    
    def modify_labels(
        self,
        emails: Union[str, List[str], pd.DataFrame],
        add_labels: Optional[Union[List[str], str]] = None,
        remove_labels: Optional[Union[List[str], str]] = None,
        show_progress: bool = True
    ) -> Dict[str, bool]:
        """
        Modify labels for multiple email messages in batch.
        
        Args:
            emails: Single message ID, list of message IDs, or DataFrame with 'message_id' column
            add_labels: Labels to add
            remove_labels: Labels to remove
            show_progress: Whether to show progress bar
            
        Returns:
            Results of label modification operations
        """
        # Extract message IDs from DataFrame if needed
        message_ids = self.get_message_ids(emails)
        # If it's already a list, use as-is
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
        
        # Invalidate cache for modified emails if cache manager is available
        if hasattr(self, 'cache_manager') and self.cache_manager:
            self.cache_manager.invalidate_cache(message_ids=message_ids)
        
        return result
    
    def mark_as_read(self, emails: Union[str, List[str], pd.DataFrame], show_progress: bool = True) -> Union[bool, Dict[str, bool]]:
        """
        Mark email(s) as read.
        
        Args:
            emails: Single message ID, list of message IDs, or DataFrame with 'message_id' column
            show_progress: Whether to show progress bar for batch operations
            
        Returns:
            Success status for single or multiple emails
        """
        # Extract message IDs from DataFrame if needed
        if hasattr(emails, 'columns') and 'message_id' in emails.columns:  # DataFrame check
            message_ids = emails['message_id'].tolist()
        elif isinstance(emails, str):
            return self.client.mark_as_read(emails)
        else:
            message_ids = emails
            
        result = self.client.batch_mark_as_read(message_ids=message_ids, show_progress=show_progress)
        
        # Invalidate cache for modified emails if cache manager is available
        if hasattr(self, 'cache_manager') and self.cache_manager:
            self.cache_manager.invalidate_cache(message_ids=message_ids)
        
        return result
    
    def mark_as_unread(self, emails: Union[str, List[str], 'pd.DataFrame']) -> Union[bool, Dict[str, bool]]:
        """
        Mark email(s) as unread.
        
        Args:
            emails: Single message ID, list of message IDs, or DataFrame with 'message_id' column
            
        Returns:
            Success status for single or multiple emails
        """
        # Extract message IDs from DataFrame if needed
        if hasattr(emails, 'columns') and 'message_id' in emails.columns:  # DataFrame check
            message_ids = emails['message_id'].tolist()
            # Batch operation for multiple emails
            results = {}
            for msg_id in message_ids:
                results[msg_id] = self.client.mark_as_unread(msg_id)
        elif isinstance(emails, str):
            message_ids = [emails]
            results = self.client.mark_as_unread(emails)
        else:
            # List of message IDs
            message_ids = emails
            results = {}
            for msg_id in emails:
                results[msg_id] = self.client.mark_as_unread(msg_id)
        
        # Invalidate cache for modified emails if cache manager is available
        if hasattr(self, 'cache_manager') and self.cache_manager:
            self.cache_manager.invalidate_cache(message_ids=message_ids)
        
        return results
    
    def star_email(self, emails: Union[str, List[str], pd.DataFrame], show_progress: bool = True) -> Union[bool, Dict[str, bool]]:
        """
        Star email(s) by adding the STARRED label.
        
        Args:
            emails: Single message ID, list of message IDs, or DataFrame with 'message_id' column
            show_progress: Whether to show progress bar for batch operations
            
        Returns:
            Success status for single or multiple emails
        """
        return self.modify_labels(emails=emails, add_labels=['STARRED'], show_progress=show_progress)
    
    def unstar_email(self, emails: Union[str, List[str], pd.DataFrame], show_progress: bool = True) -> Union[bool, Dict[str, bool]]:
        """
        Remove star from email(s) by removing the STARRED label.
        
        Args:
            emails: Single message ID, list of message IDs, or DataFrame with 'message_id' column
            show_progress: Whether to show progress bar for batch operations
            
        Returns:
            Success status for single or multiple emails
        """
        return self.modify_labels(emails=emails, remove_labels=['STARRED'], show_progress=show_progress)
    
    def archive_email(self, emails: Union[str, List[str], 'pd.DataFrame']) -> Union[bool, Dict[str, bool]]:
        """
        Archive email(s).
        
        Args:
            emails: Single message ID, list of message IDs, or DataFrame with 'message_id' column
            
        Returns:
            Success status for single or multiple emails
        """
        # Extract message IDs from DataFrame if needed
        if hasattr(emails, 'columns') and 'message_id' in emails.columns:  # DataFrame check
            message_ids = emails['message_id'].tolist()
            # Batch operation for multiple emails
            results = {}
            for msg_id in message_ids:
                results[msg_id] = self.client.archive_email(msg_id)
        elif isinstance(emails, str):
            message_ids = [emails]
            results = self.client.archive_email(emails)
        else:
            # List of message IDs
            message_ids = emails
            results = {}
            for msg_id in emails:
                results[msg_id] = self.client.archive_email(msg_id)
        
        # Invalidate cache for modified emails if cache manager is available
        if hasattr(self, 'cache_manager') and self.cache_manager:
            self.cache_manager.invalidate_cache(message_ids=message_ids)
        
        return results