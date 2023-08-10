"""
EmailDataFrame - Enhanced DataFrame with direct email operations.

This module provides an EmailDataFrame class that extends pandas DataFrame
with methods for direct email operations like move_to_archive, mark_as_read, etc.
"""

import pandas as pd
from typing import Union, List, Optional, Any
from ..core.gmail import Gmail


class EmailDataFrame(pd.DataFrame):
    """
    Enhanced DataFrame for email operations.
    
    Extends pandas DataFrame with direct email operation methods
    that work on the email data without requiring manual ID extraction.
    """
    
    def __init__(self, data=None, gmail_client: Optional[Gmail] = None, *args, **kwargs):
        """
        Initialize EmailDataFrame.
        
        Args:
            data: DataFrame data
            gmail_client: Gmail client instance for operations
            *args, **kwargs: Additional arguments for pandas DataFrame
        """
        super().__init__(data, *args, **kwargs)
        self._gmail_client = gmail_client
    
    @property
    def _constructor(self):
        """Return the class to use for DataFrame operations."""
        return EmailDataFrame
    
    def _constructor_sliced(self, *args, **kwargs):
        """Return the class to use for Series operations."""
        return pd.Series
    
    def set_gmail_client(self, gmail_client: Gmail) -> 'EmailDataFrame':
        """Set the Gmail client for this DataFrame."""
        self._gmail_client = gmail_client
        return self
    
    def _get_message_ids(self) -> List[str]:
        """Get message IDs from the DataFrame."""
        if 'message_id' not in self.columns:
            raise ValueError("DataFrame must contain 'message_id' column")
        return self['message_id'].tolist()
    
    def _check_gmail_client(self):
        """Check if Gmail client is available."""
        if self._gmail_client is None:
            raise ValueError("Gmail client not set. Use set_gmail_client() first.")
    
    def move_to_archive(self, show_progress: bool = True) -> bool:
        """
        Move all emails in this DataFrame to archive.
        
        Args:
            show_progress: Whether to show progress bar
            
        Returns:
            bool: True if operation was successful
        """
        self._check_gmail_client()
        message_ids = self._get_message_ids()
        if not message_ids:
            return True
        
        return self._gmail_client.move_to_archive(
            message_ids=message_ids, 
            show_progress=show_progress
        )
    
    def move_to_trash(self, show_progress: bool = True) -> bool:
        """
        Move all emails in this DataFrame to trash.
        
        Args:
            show_progress: Whether to show progress bar
            
        Returns:
            bool: True if operation was successful
        """
        self._check_gmail_client()
        message_ids = self._get_message_ids()
        if not message_ids:
            return True
        
        return self._gmail_client.move_to_trash(
            message_ids=message_ids, 
            show_progress=show_progress
        )
    
    def move_to_inbox(self, show_progress: bool = True) -> bool:
        """
        Move all emails in this DataFrame to inbox.
        
        Args:
            show_progress: Whether to show progress bar
            
        Returns:
            bool: True if operation was successful
        """
        self._check_gmail_client()
        message_ids = self._get_message_ids()
        if not message_ids:
            return True
        
        return self._gmail_client.move_to_inbox(
            message_ids=message_ids, 
            show_progress=show_progress
        )
    
    def mark_as_read(self, show_progress: bool = True) -> bool:
        """
        Mark all emails in this DataFrame as read.
        
        Args:
            show_progress: Whether to show progress bar
            
        Returns:
            bool: True if operation was successful
        """
        self._check_gmail_client()
        message_ids = self._get_message_ids()
        if not message_ids:
            return True
        
        return self._gmail_client.mark_as_read(
            message_ids=message_ids, 
            show_progress=show_progress
        )
    
    def mark_as_unread(self, show_progress: bool = True) -> bool:
        """
        Mark all emails in this DataFrame as unread.
        
        Args:
            show_progress: Whether to show progress bar
            
        Returns:
            bool: True if operation was successful
        """
        self._check_gmail_client()
        message_ids = self._get_message_ids()
        if not message_ids:
            return True
        
        return self._gmail_client.mark_as_unread(
            message_ids=message_ids, 
            show_progress=show_progress
        )
    
    def star(self, show_progress: bool = True) -> bool:
        """
        Star all emails in this DataFrame.
        
        Args:
            show_progress: Whether to show progress bar
            
        Returns:
            bool: True if operation was successful
        """
        self._check_gmail_client()
        message_ids = self._get_message_ids()
        if not message_ids:
            return True
        
        return self._gmail_client.star_email(
            message_ids=message_ids, 
            show_progress=show_progress
        )
    
    def unstar(self, show_progress: bool = True) -> bool:
        """
        Remove star from all emails in this DataFrame.
        
        Args:
            show_progress: Whether to show progress bar
            
        Returns:
            bool: True if operation was successful
        """
        self._check_gmail_client()
        message_ids = self._get_message_ids()
        if not message_ids:
            return True
        
        return self._gmail_client.unstar_email(
            message_ids=message_ids, 
            show_progress=show_progress
        )
    
    def add_label(self, label: Union[str, List[str]], show_progress: bool = True) -> bool:
        """
        Add label(s) to all emails in this DataFrame.
        
        Args:
            label: Label name(s) to add
            show_progress: Whether to show progress bar
            
        Returns:
            bool: True if operation was successful
        """
        self._check_gmail_client()
        message_ids = self._get_message_ids()
        if not message_ids:
            return True
        
        return self._gmail_client.add_label(
            message_ids=message_ids,
            label=label,
            show_progress=show_progress
        )
    
    def remove_label(self, label: Union[str, List[str]], show_progress: bool = True) -> bool:
        """
        Remove label(s) from all emails in this DataFrame.
        
        Args:
            label: Label name(s) to remove
            show_progress: Whether to show progress bar
            
        Returns:
            bool: True if operation was successful
        """
        self._check_gmail_client()
        message_ids = self._get_message_ids()
        if not message_ids:
            return True
        
        return self._gmail_client.remove_label(
            message_ids=message_ids,
            label=label,
            show_progress=show_progress
        )
    
    def filter(self, **kwargs) -> 'EmailDataFrame':
        """
        Filter emails in this DataFrame.
        
        Args:
            **kwargs: Filter conditions (e.g., is_unread=True, has_attachment=True)
            
        Returns:
            EmailDataFrame: Filtered DataFrame
        """
        filtered_df = self.copy()
        
        for column, value in kwargs.items():
            if column in self.columns:
                if isinstance(value, (list, tuple)):
                    filtered_df = filtered_df[filtered_df[column].isin(value)]
                else:
                    filtered_df = filtered_df[filtered_df[column] == value]
        
        return filtered_df
    
    def count(self) -> int:
        """Get the number of emails in this DataFrame."""
        return len(self)
    
    def is_empty(self) -> bool:
        """Check if this DataFrame is empty."""
        return len(self) == 0
