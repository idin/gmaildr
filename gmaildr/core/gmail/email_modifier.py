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
    
    def mark_as_read(self, message_id: Union[str, List[str]], show_progress: bool = True) -> Union[bool, Dict[str, bool]]:
        """
        Mark email(s) as read.
        
        Args:
            message_id: Single message ID or list of message IDs
            show_progress: Whether to show progress bar for batch operations
            
        Returns:
            Success status for single or multiple emails
        """
        if isinstance(message_id, str):
            return self.client.mark_as_read(message_id)
        else:
            return self.client.batch_mark_as_read(message_ids=message_id, show_progress=show_progress)
    
    def mark_as_unread(self, message_id: str) -> bool:
        """
        Mark an email as unread.
        
        Args:
            message_id: The ID of the email message to mark as unread
            
        Returns:
            True if successful, False otherwise
        """
        return self.client.mark_as_unread(message_id)
    
    def star_email(self, message_id: Union[str, List[str]], show_progress: bool = True) -> Union[bool, Dict[str, bool]]:
        """
        Star email(s).
        
        Args:
            message_id: Single message ID or list of message IDs
            show_progress: Whether to show progress bar for batch operations
            
        Returns:
            Success status for single or multiple emails
        """
        if isinstance(message_id, str):
            return self.client.star_email(message_id)
        else:
            return self.client.batch_star_emails(message_ids=message_id, show_progress=show_progress)
    
    def unstar_email(self, message_id: str) -> bool:
        """
        Remove star from an email.
        
        Args:
            message_id: The ID of the email message to unstar
            
        Returns:
            True if successful, False otherwise
        """
        return self.client.unstar_email(message_id)
    
    def archive_email(self, message_id: str) -> bool:
        """
        Archive an email.
        
        Args:
            message_id: The ID of the email message to archive
            
        Returns:
            True if successful, False otherwise
        """
        return self.client.archive_email(message_id)