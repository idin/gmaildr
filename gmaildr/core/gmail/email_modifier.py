from typing import Optional, List, Union, Dict
from .gmail_base import GmailBase

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
    
    def mark_as_read(self, emails: Union[str, List[str], 'pd.DataFrame'], show_progress: bool = True) -> Union[bool, Dict[str, bool]]:
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
    
    def star_email(self, emails: Union[str, List[str], 'pd.DataFrame'], show_progress: bool = True) -> Union[bool, Dict[str, bool]]:
        """
        Star email(s).
        
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
            return self.client.star_email(emails)
        else:
            message_ids = emails
            
        result = self.client.batch_star_emails(message_ids=message_ids, show_progress=show_progress)
        
        # Invalidate cache for modified emails if cache manager is available
        if hasattr(self, 'cache_manager') and self.cache_manager:
            self.cache_manager.invalidate_cache(message_ids=message_ids)
        
        return result
    
    def unstar_email(self, emails: Union[str, List[str], 'pd.DataFrame']) -> Union[bool, Dict[str, bool]]:
        """
        Remove star from email(s).
        
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
                results[msg_id] = self.client.unstar_email(msg_id)
        elif isinstance(emails, str):
            message_ids = [emails]
            results = self.client.unstar_email(emails)
        else:
            # List of message IDs
            message_ids = emails
            results = {}
            for msg_id in emails:
                results[msg_id] = self.client.unstar_email(msg_id)
        
        # Invalidate cache for modified emails if cache manager is available
        if hasattr(self, 'cache_manager') and self.cache_manager:
            self.cache_manager.invalidate_cache(message_ids=message_ids)
        
        return results
    
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