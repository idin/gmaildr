"""
EmailDataFrame - Enhanced DataFrame with direct email operations.

This module provides an EmailDataFrame class that extends pandas DataFrame
with methods for direct email operations like move_to_archive, mark_as_read, etc.
"""

import pandas as pd
from typing import Union, List, Optional, Any, Dict, TYPE_CHECKING
from ..gmail_dataframe import GmailDataFrame

if TYPE_CHECKING:
    from ...core.gmail import Gmail

# Import EmailMessage for runtime use
from ...core.models.email_message import EmailMessage

from ..gmail_dataframe import GmailDataFrame

class EmailDataFrame(GmailDataFrame):
    """
    Enhanced DataFrame for email operations.
    
    Extends pandas DataFrame with direct email operation methods
    that work on the email data without requiring manual ID extraction.
    """

    NECESSARY_COLUMNS = [
        'message_id', 'sender_email', 'subject', 'timestamp', 'sender_local_timestamp'
    ]
    
    @property
    def _constructor(self):
        """Return the class to use for DataFrame operations."""
        return EmailDataFrame
    

    
    @property
    def senders_dataframe(self):
        """
        Get a SenderDataFrame representation.
        
        Returns:
            SenderDataFrame
        """
        from ..sender_dataframe.sender_dataframe import SenderDataFrame
        return SenderDataFrame(self, gmail=self._gmail_instance)

    def _get_message_ids(self) -> List[str]:
        """Get message IDs from the DataFrame."""
        if 'message_id' not in self.columns:
            raise ValueError("DataFrame must contain 'message_id' column")
        return self['message_id'].tolist()
    
    def filter(self, **kwargs) -> 'EmailDataFrame':
        """
        Filter emails in this DataFrame.
        
        Args:
            **kwargs: Filter conditions (e.g., is_unread=True, has_attachment=True)
            
        Returns:
            EmailDataFrame: Filtered DataFrame
        """
        # Start with all rows
        mask = pd.Series([True] * len(self), index=self.index)
        
        # Apply each filter condition (AND logic)
        for column, value in kwargs.items():
            if column in self.columns:
                if isinstance(value, (list, tuple)):
                    # Use basic boolean indexing
                    column_mask = self[column].isin(value)  # type: ignore
                else:
                    # Use basic equality comparison
                    column_mask = self[column] == value
                # Combine with existing mask (AND logic)
                mask = mask & column_mask
        
        # Apply the combined mask and return as EmailDataFrame
        filtered_df = self[mask]
        # Ensure we have a DataFrame, not a Series
        if isinstance(filtered_df, pd.Series):
            filtered_df = filtered_df.to_frame()
        return EmailDataFrame(filtered_df, gmail=self._gmail_instance)

    @property
    def ml_dataframe(self):
        """
        Transform features for machine learning.
        
        This creates a new Email_ML_DataFrame with transformed features suitable for ML.
        
        Returns:
            Email_ML_DataFrame with transformed features
        """
        from .transform_features_for_ml import transform_email_features_for_ml
        from .email_ml_dataframe import Email_ML_DataFrame
        
        # Transform the features - function returns pandas DataFrame with ML features
        ml_features_df = transform_email_features_for_ml(email_df=self)
        
        # Validate that ML DataFrame contains required columns and excludes non-ML columns
        if 'message_id' not in ml_features_df.columns:
            raise KeyError("ML DataFrame must contain 'message_id' column")
        
        # Check for non-ML columns that should not be present
        non_ml_columns = [
            'sender_email', 'timestamp', 'sender_local_timestamp', 'subject', 
            'text_content', 'thread_id', 'recipient_email', 'labels'
        ] # TODO use the columns guide
        found_non_ml_columns = [col for col in non_ml_columns if col in ml_features_df.columns]
        if found_non_ml_columns:
            raise KeyError(f"ML DataFrame must not contain non-ML columns: {found_non_ml_columns}")
        
        return Email_ML_DataFrame(ml_features_df, gmail=self._gmail_instance)

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
    
    def get_label_names(self) -> List[str]:
        """
        Get all unique label names from emails in this DataFrame.
        
        Returns:
            List[str]: List of unique label names
        """
        gmail_instance = self._check_gmail_instance()
        all_label_ids = set()
        for labels in self['labels']:
            if labels:
                all_label_ids.update(labels)
        # Convert label IDs to names using the new method
        return gmail_instance.get_label_names_from_ids(list(all_label_ids))
    
    def has_label(self, label_name: str) -> 'EmailDataFrame':
        """
        Filter emails that have a specific label.
        
        Args:
            label_name: Name of the label to filter by
            
        Returns:
            EmailDataFrame: Filtered DataFrame containing only emails with the specified label
        """
        gmail_instance = self._check_gmail_instance()
        
        # Get the label ID for the given name
        label_id = gmail_instance.get_label_id(label_name)
        if not label_id:
            # If label doesn't exist, return empty DataFrame
            return EmailDataFrame(pd.DataFrame(), gmail=gmail_instance)
        
        # Filter emails that have this label ID
        mask = self['labels'].apply(lambda labels: label_id in labels if labels else False)
        return EmailDataFrame(self[mask], gmail=gmail_instance)
    
    def has_any_label(self, label_names: List[str]) -> 'EmailDataFrame':
        """
        Filter emails that have any of the specified labels.
        
        Args:
            label_names: List of label names to filter by
            
        Returns:
            EmailDataFrame: Filtered DataFrame containing emails with any of the specified labels
        """
        gmail_instance = self._check_gmail_instance()
        
        # Get label IDs for all given names
        label_ids = []
        for label_name in label_names:
            label_id = gmail_instance.get_label_id(label_name)
            if label_id:
                label_ids.append(label_id)
        
        if not label_ids:
            # If no labels exist, return empty DataFrame
            return EmailDataFrame(pd.DataFrame(), gmail=gmail_instance)
        
        # Filter emails that have any of these label IDs
        mask = self['labels'].apply(lambda labels: any(label_id in labels for label_id in label_ids) if labels else False)
        return EmailDataFrame(self[mask], gmail=gmail_instance)
    
    def has_all_labels(self, label_names: List[str]) -> 'EmailDataFrame':
        """
        Filter emails that have all of the specified labels.
        
        Args:
            label_names: List of label names to filter by
            
        Returns:
            EmailDataFrame: Filtered DataFrame containing emails with all of the specified labels
        """
        gmail_instance = self._check_gmail_instance()
        
        # Get label IDs for all given names
        label_ids = []
        for label_name in label_names:
            label_id = gmail_instance.get_label_id(label_name)
            if label_id:
                label_ids.append(label_id)
        
        if not label_ids:
            # If no labels exist, return empty DataFrame
            return EmailDataFrame(pd.DataFrame(), gmail=gmail_instance)
        
        # Filter emails that have all of these label IDs
        mask = self['labels'].apply(lambda labels: all(label_id in labels for label_id in label_ids) if labels else False)
        return EmailDataFrame(self[mask], gmail=gmail_instance)
    
    def count_by_label(self, label_name: str) -> int:
        """
        Count emails that have a specific label.
        
        Args:
            label_name: Name of the label to count
            
        Returns:
            int: Number of emails with the specified label
        """
        return len(self.has_label(label_name))
    
    def get_emails_with_label(self, label_name: str) -> 'EmailDataFrame':
        """
        Get all emails that have a specific label.
        
        Args:
            label_name: Name of the label to filter by
            
        Returns:
            EmailDataFrame: Filtered DataFrame containing only emails with the specified label
        """
        return self.has_label(label_name)
    

    

    

