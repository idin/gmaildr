"""
EmailDataFrame - Enhanced DataFrame with direct email operations.

This module provides an EmailDataFrame class that extends pandas DataFrame
with methods for direct email operations like move_to_archive, mark_as_read, etc.
"""

import pandas as pd
from typing import Union, List, Optional, Any, Dict
from ..core.gmail import Gmail


class EmailSeries(pd.Series):
    """Custom Series class for email-specific operations on message_id columns."""
    
    def __init__(self, data=None, index=None, dtype=None, name=None, copy=False):
        """Initialize EmailSeries."""
        super().__init__(data=data, index=index, dtype=dtype, name=name, copy=copy)
    

    
    def get_message_ids(self) -> List[str]:
        """Get message IDs as a list."""
        return self.tolist()
    
    def count_emails(self) -> int:
        """Count the number of emails in this series."""
        return len(self)
    
    def is_empty(self) -> bool:
        """Check if this series is empty."""
        return len(self) == 0


class EmailDataFrame(pd.DataFrame):
    """
    Enhanced DataFrame for email operations.
    
    Extends pandas DataFrame with direct email operation methods
    that work on the email data without requiring manual ID extraction.
    """
    
    def __init__(self, data=None, gmail_instance: Optional[Gmail] = None, *args, **kwargs):
        """
        Initialize EmailDataFrame.
        
        Args:
            data: DataFrame data
            gmail_instance: Gmail instance for operations
            *args, **kwargs: Additional arguments for pandas DataFrame
        """
        super().__init__(data, *args, **kwargs)
        self._gmail_instance = gmail_instance
        
        # Only check for message_id column if DataFrame is not empty, has columns, and has string/object columns
        # This allows numeric-only DataFrames (like from select_dtypes) to be created
        if len(self) > 0:
            # THERE IS NO OTHER SITUATION. AN EMAIL DATAFRAME SHOULD HAVE THIS COLUMN REGARDLESS
            # IT DOES NOT MATTER IF THERE ARE ONLY NUMERIC COLUMNS OR WHATEVER. 
            # THIS COLUMN IS A MUST FOR THIS CLASS. WE SHOULD NOT CHANGE THIS IF STATEMENT.
            if 'message_id' not in self.columns:
                raise KeyError("DataFrame must contain 'message_id' column")

    @property
    def _constructor(self):
        """Return the class to use for DataFrame operations."""
        return EmailDataFrame
    
    def _constructor_from_mgr(self, mgr, axes):
        """Return the class to use for DataFrame operations from manager."""
        # Create a regular DataFrame first
        df = pd.DataFrame._from_mgr(mgr, axes=axes)
        # Only create EmailDataFrame if it has a message_id column (can perform email operations)
        # Otherwise return regular DataFrame
        gmail_instance = getattr(self, '_gmail_instance', None)
        if 'message_id' in df.columns:
            return EmailDataFrame(data=df, gmail_instance=gmail_instance)
        else:
            return df
    
    @property
    def _constructor_sliced(self):
        """Return the class to use for Series operations."""
        # Let pandas handle Series creation normally
        return pd.Series
    
    def _constructor_sliced_from_mgr(self, mgr, axes):
        """Return the class to use for Series operations from manager."""
        # Create a Series instance directly instead of returning the class
        return pd.Series._from_mgr(mgr, axes=axes)
    
    def iterrows(self):
        """Override iterrows to avoid the __finalize__ issue."""
        columns = self.columns
        for k, v in zip(self.index, self.values):
            s = pd.Series(v, index=columns, name=k)
            yield k, s
    
    def __getitem__(self, key):
        """Override __getitem__ to return EmailSeries for message_id column."""
        result = super().__getitem__(key)
        
        # If we're accessing a single column and it's message_id, return EmailSeries
        if isinstance(key, str) and key == 'message_id' and isinstance(result, pd.Series):
            # Convert the Series to EmailSeries
            email_series = EmailSeries(result.values, index=result.index, name=result.name)
            return email_series
        
        return result
    
    def _box_col_values(self, values, loc):
        """Provide boxed values for a column."""
        # Use the proper pandas API to avoid deprecation warning
        name = self.columns[loc]
        # Convert BlockManager to proper array using pandas internal API
        if hasattr(values, 'array'):
            # Use the array property which is the modern way
            obj = pd.Series(values.array, index=self.index, name=name)
        else:
            # Fallback to direct conversion
            obj = pd.Series(values, index=self.index, name=name)
        return obj
    
    # Remove dtypes override as it's causing issues with pandas internals
    
    # Removed __finalize__ method as it was causing issues with pandas internals
    # Metadata propagation is handled by _constructor_from_mgr instead
    
    def set_gmail_instance(self, gmail_instance: Gmail) -> 'EmailDataFrame':
        """Set the Gmail instance for this DataFrame."""
        self._gmail_instance = gmail_instance
        return self
    
    def _get_message_ids(self) -> List[str]:
        """Get message IDs from the DataFrame."""
        if 'message_id' not in self.columns:
            raise ValueError("DataFrame must contain 'message_id' column")
        return self['message_id'].tolist()
    
    def _check_gmail_instance(self):
        """Check if Gmail instance is available."""
        if self._gmail_instance is None:
            raise ValueError("Gmail instance not set. Use set_gmail_instance() first.")
        return self._gmail_instance
    
    def move_to_archive(self, show_progress: bool = True) -> Union[bool, Dict[str, bool]]:
        """
        Move all emails in this DataFrame to archive.
        
        Args:
            show_progress: Whether to show progress bar
            
        Returns:
            bool or Dict[str, bool]: Success status
        """
        gmail_instance = self._check_gmail_instance()
        message_ids = self._get_message_ids()
        if not message_ids:
            return True
        
        return gmail_instance.move_to_archive(
            message_ids=message_ids, 
            show_progress=show_progress
        )
    
    def move_to_trash(self, show_progress: bool = True) -> Union[bool, Dict[str, bool]]:
        """
        Move all emails in this DataFrame to trash.
        
        Args:
            show_progress: Whether to show progress bar
            
        Returns:
            bool or Dict[str, bool]: Success status
        """
        gmail_instance = self._check_gmail_instance()
        message_ids = self._get_message_ids()
        if not message_ids:
            return True
        
        return gmail_instance.move_to_trash(
            message_ids=message_ids, 
            show_progress=show_progress
        )
    
    def move_to_inbox(self, show_progress: bool = True) -> Union[bool, Dict[str, bool]]:
        """
        Move all emails in this DataFrame to inbox.
        
        Args:
            show_progress: Whether to show progress bar
            
        Returns:
            bool or Dict[str, bool]: Success status
        """
        gmail_instance = self._check_gmail_instance()
        message_ids = self._get_message_ids()
        if not message_ids:
            return True
        
        return gmail_instance.move_to_inbox(
            message_ids=message_ids,
            show_progress=show_progress
        )
    
    def mark_as_read(self, show_progress: bool = True) -> Union[bool, Dict[str, bool]]:
        """
        Mark all emails in this DataFrame as read.
        
        Args:
            show_progress: Whether to show progress bar
            
        Returns:
            bool or Dict[str, bool]: Success status
        """
        gmail_instance = self._check_gmail_instance()
        message_ids = self._get_message_ids()
        if not message_ids:
            return True
        
        return gmail_instance.mark_as_read(
            message_id=message_ids, 
            show_progress=show_progress
        )
    
    def mark_as_unread(self, show_progress: bool = True) -> Union[bool, Dict[str, bool]]:
        """
        Mark all emails in this DataFrame as unread.
        
        Args:
            show_progress: Whether to show progress bar
            
        Returns:
            bool or Dict[str, bool]: Success status
        """
        gmail_instance = self._check_gmail_instance()
        message_ids = self._get_message_ids()
        if not message_ids:
            return True
        
        # Note: mark_as_unread only accepts single message_id, so we need to handle multiple
        if len(message_ids) == 1:
            return gmail_instance.mark_as_unread(message_id=message_ids[0])
        else:
            # For multiple emails, we need to use modify_labels
            return gmail_instance.modify_labels(
                message_ids=message_ids,
                add_labels=['UNREAD'],
                show_progress=show_progress
            )
    
    def star(self, show_progress: bool = True) -> Union[bool, Dict[str, bool]]:
        """
        Star all emails in this DataFrame.
        
        Args:
            show_progress: Whether to show progress bar
            
        Returns:
            bool or Dict[str, bool]: Success status
        """
        gmail_instance = self._check_gmail_instance()
        message_ids = self._get_message_ids()
        if not message_ids:
            return True
        
        return gmail_instance.star_email(
            message_id=message_ids, 
            show_progress=show_progress
        )
    
    def unstar(self, show_progress: bool = True) -> Union[bool, Dict[str, bool]]:
        """
        Remove star from all emails in this DataFrame.
        
        Args:
            show_progress: Whether to show progress bar
            
        Returns:
            bool or Dict[str, bool]: Success status
        """
        gmail_instance = self._check_gmail_instance()
        message_ids = self._get_message_ids()
        if not message_ids:
            return True
        
        # Note: unstar_email only accepts single message_id, so we need to handle multiple
        if len(message_ids) == 1:
            return gmail_instance.unstar_email(message_id=message_ids[0])
        else:
            # For multiple emails, we need to use modify_labels
            return gmail_instance.modify_labels(
                message_ids=message_ids,
                remove_labels=['STARRED'],
                show_progress=show_progress
            )
    
    def add_label(self, label: Union[str, List[str]], show_progress: bool = True) -> Union[bool, Dict[str, bool]]:
        """
        Add label(s) to all emails in this DataFrame.
        
        Args:
            label: Label name(s) to add
            show_progress: Whether to show progress bar
            
        Returns:
            bool or Dict[str, bool]: Success status
        """
        gmail_instance = self._check_gmail_instance()
        message_ids = self._get_message_ids()
        if not message_ids:
            return True
        
        return gmail_instance.add_label(
            message_ids=message_ids,
            label=label,
            show_progress=show_progress
        )
    
    def remove_label(self, label: Union[str, List[str]], show_progress: bool = True) -> Union[bool, Dict[str, bool]]:
        """
        Remove label(s) from all emails in this DataFrame.
        
        Args:
            label: Label name(s) to remove
            show_progress: Whether to show progress bar
            
        Returns:
            bool or Dict[str, bool]: Success status
        """
        gmail_instance = self._check_gmail_instance()
        message_ids = self._get_message_ids()
        if not message_ids:
            return True
        
        return gmail_instance.remove_label(
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
                    # Use basic boolean indexing
                    mask = pd.Series([v in value for v in filtered_df[column]], index=filtered_df.index)
                    filtered_df = filtered_df[mask]
                else:
                    # Use basic equality comparison
                    mask = filtered_df[column] == value
                    filtered_df = filtered_df[mask]
        
        return filtered_df
    
    def count(self) -> int:
        """Get the number of emails in this DataFrame."""
        return len(self)
    
    def is_empty(self) -> bool:
        """Check if this DataFrame is empty."""
        return len(self) == 0
    
    def groupby(self, *args, **kwargs):
        """Override groupby to ensure proper Series creation."""
        # Call the parent groupby method
        result = super().groupby(*args, **kwargs)
        return result
