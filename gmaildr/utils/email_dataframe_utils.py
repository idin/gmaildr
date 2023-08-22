"""
Email DataFrame Utilities

This module provides utility functions that were previously methods on EmailDataFrame.
These functions work with regular pandas DataFrames and a Gmail instance.
"""

import pandas as pd
from typing import Union, List, Optional, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.gmail import Gmail


def filter_emails(df: pd.DataFrame, **kwargs) -> pd.DataFrame:
    """
    Filter emails in a DataFrame.
    
    Args:
        df: pandas DataFrame containing email data
        **kwargs: Filter conditions (e.g., is_unread=True, has_attachment=True)
        
    Returns:
        pd.DataFrame: Filtered DataFrame
    """
    # Start with all rows
    mask = pd.Series([True] * len(df), index=df.index)
    
    # Apply each filter condition (AND logic)
    for column, value in kwargs.items():
        if column in df.columns:
            if isinstance(value, (list, tuple)):
                # Use basic boolean indexing
                column_mask = df[column].isin(value)
            else:
                # Use basic equality comparison
                column_mask = df[column] == value
            # Combine with existing mask (AND logic)
            mask = mask & column_mask
    
    # Apply the combined mask and return
    filtered_df = df[mask]
    # Ensure we have a DataFrame, not a Series
    if isinstance(filtered_df, pd.Series):
        filtered_df = filtered_df.to_frame()
    return filtered_df


def get_message_ids(df: pd.DataFrame) -> List[str]:
    """Get message IDs from the DataFrame."""
    if 'message_id' not in df.columns:
        raise ValueError("DataFrame must contain 'message_id' column")
    return df['message_id'].tolist()


def move_to_archive(df: pd.DataFrame, gmail: 'Gmail', show_progress: bool = True) -> Union[bool, Dict[str, bool]]:
    """
    Move all emails in this DataFrame to archive.
    
    Args:
        df: pandas DataFrame containing email data
        gmail: Gmail instance
        show_progress: Whether to show progress bar
        
    Returns:
        bool or Dict[str, bool]: Success status
    """
    message_ids = get_message_ids(df)
    if not message_ids:
        return True
    
    return gmail.move_to_archive(
        message_ids=message_ids, 
        show_progress=show_progress
    )


def move_to_trash(df: pd.DataFrame, gmail: 'Gmail', show_progress: bool = True) -> Union[bool, Dict[str, bool]]:
    """
    Move all emails in this DataFrame to trash.
    
    Args:
        df: pandas DataFrame containing email data
        gmail: Gmail instance
        show_progress: Whether to show progress bar
        
    Returns:
        bool or Dict[str, bool]: Success status
    """
    message_ids = get_message_ids(df)
    if not message_ids:
        return True
    
    return gmail.move_to_trash(
        message_ids=message_ids, 
        show_progress=show_progress
    )


def move_to_inbox(df: pd.DataFrame, gmail: 'Gmail', show_progress: bool = True) -> Union[bool, Dict[str, bool]]:
    """
    Move all emails in this DataFrame to inbox.
    
    Args:
        df: pandas DataFrame containing email data
        gmail: Gmail instance
        show_progress: Whether to show progress bar
        
    Returns:
        bool or Dict[str, bool]: Success status
    """
    message_ids = get_message_ids(df)
    if not message_ids:
        return True
    
    return gmail.move_to_inbox(
        message_ids=message_ids,
        show_progress=show_progress
    )


def mark_as_read(df: pd.DataFrame, gmail: 'Gmail', show_progress: bool = True) -> Union[bool, Dict[str, bool]]:
    """
    Mark all emails in this DataFrame as read.
    
    Args:
        df: pandas DataFrame containing email data
        gmail: Gmail instance
        show_progress: Whether to show progress bar
        
    Returns:
        bool or Dict[str, bool]: Success status
    """
    message_ids = get_message_ids(df)
    if not message_ids:
        return True
    
    return gmail.mark_as_read(
        message_id=message_ids, 
        show_progress=show_progress
    )


def mark_as_unread(df: pd.DataFrame, gmail: 'Gmail', show_progress: bool = True) -> Union[bool, Dict[str, bool]]:
    """
    Mark all emails in this DataFrame as unread.
    
    Args:
        df: pandas DataFrame containing email data
        gmail: Gmail instance
        show_progress: Whether to show progress bar
        
    Returns:
        bool or Dict[str, bool]: Success status
    """
    message_ids = get_message_ids(df)
    if not message_ids:
        return True
    
    # Note: mark_as_unread only accepts single message_id, so we need to handle multiple
    if len(message_ids) == 1:
        return gmail.mark_as_unread(message_id=message_ids[0])
    else:
        # For multiple emails, we need to use modify_labels
        return gmail.modify_labels(
            message_ids=message_ids,
            add_labels=['UNREAD'],
            show_progress=show_progress
        )


def star_emails(df: pd.DataFrame, gmail: 'Gmail', show_progress: bool = True) -> Union[bool, Dict[str, bool]]:
    """
    Star all emails in this DataFrame.
    
    Args:
        df: pandas DataFrame containing email data
        gmail: Gmail instance
        show_progress: Whether to show progress bar
        
    Returns:
        bool or Dict[str, bool]: Success status
    """
    message_ids = get_message_ids(df)
    if not message_ids:
        return True
    
    return gmail.star_email(
        message_id=message_ids, 
        show_progress=show_progress
    )


def unstar_emails(df: pd.DataFrame, gmail: 'Gmail', show_progress: bool = True) -> Union[bool, Dict[str, bool]]:
    """
    Remove star from all emails in this DataFrame.
    
    Args:
        df: pandas DataFrame containing email data
        gmail: Gmail instance
        show_progress: Whether to show progress bar
        
    Returns:
        bool or Dict[str, bool]: Success status
    """
    message_ids = get_message_ids(df)
    if not message_ids:
        return True
    
    # Note: unstar_email only accepts single message_id, so we need to handle multiple
    if len(message_ids) == 1:
        return gmail.unstar_email(message_id=message_ids[0])
    else:
        # For multiple emails, we need to use modify_labels
        return gmail.modify_labels(
            message_ids=message_ids,
            remove_labels=['STARRED'],
            show_progress=show_progress
        )


def add_label(df: pd.DataFrame, gmail: 'Gmail', label: Union[str, List[str]], show_progress: bool = True) -> Union[bool, Dict[str, bool]]:
    """
    Add label(s) to all emails in this DataFrame.
    
    Args:
        df: pandas DataFrame containing email data
        gmail: Gmail instance
        label: Label name(s) to add
        show_progress: Whether to show progress bar
        
    Returns:
        bool or Dict[str, bool]: Success status
    """
    message_ids = get_message_ids(df)
    if not message_ids:
        return True
    
    return gmail.add_label(
        message_ids=message_ids,
        label=label,
        show_progress=show_progress
    )


def remove_label(df: pd.DataFrame, gmail: 'Gmail', label: Union[str, List[str]], show_progress: bool = True) -> Union[bool, Dict[str, bool]]:
    """
    Remove label(s) from all emails in this DataFrame.
    
    Args:
        df: pandas DataFrame containing email data
        gmail: Gmail instance
        label: Label name(s) to remove
        show_progress: Whether to show progress bar
        
    Returns:
        bool or Dict[str, bool]: Success status
    """
    message_ids = get_message_ids(df)
    if not message_ids:
        return True
    
    return gmail.remove_label(
        message_ids=message_ids,
        label=label,
        show_progress=show_progress
    )


def get_label_names(df: pd.DataFrame, gmail: 'Gmail') -> List[str]:
    """
    Get all unique label names from emails in this DataFrame.
    
    Args:
        df: pandas DataFrame containing email data
        gmail: Gmail instance
        
    Returns:
        List[str]: List of unique label names
    """
    all_label_ids = set()
    for labels in df['labels']:
        if labels:
            all_label_ids.update(labels)
    # Convert label IDs to names using the new method
    return gmail.get_label_names_from_ids(list(all_label_ids))


def has_label(df: pd.DataFrame, gmail: 'Gmail', label_name: str) -> pd.DataFrame:
    """
    Filter emails that have a specific label.
    
    Args:
        df: pandas DataFrame containing email data
        gmail: Gmail instance
        label_name: Name of the label to filter by
        
    Returns:
        pd.DataFrame: Filtered DataFrame containing only emails with the specified label
    """
    # Get the label ID for the given name
    label_id = gmail.get_label_id(label_name)
    if not label_id:
        # If label doesn't exist, return empty DataFrame
        return pd.DataFrame()
    
    # Filter emails that have this label ID
    mask = df['labels'].apply(lambda labels: label_id in labels if labels else False)
    return df[mask]


def has_any_label(df: pd.DataFrame, gmail: 'Gmail', label_names: List[str]) -> pd.DataFrame:
    """
    Filter emails that have any of the specified labels.
    
    Args:
        df: pandas DataFrame containing email data
        gmail: Gmail instance
        label_names: List of label names to filter by
        
    Returns:
        pd.DataFrame: Filtered DataFrame containing emails with any of the specified labels
    """
    # Get label IDs for all given names
    label_ids = []
    for label_name in label_names:
        label_id = gmail.get_label_id(label_name)
        if label_id:
            label_ids.append(label_id)
    
    if not label_ids:
        # If no labels exist, return empty DataFrame
        return pd.DataFrame()
    
    # Filter emails that have any of these label IDs
    mask = df['labels'].apply(lambda labels: any(label_id in labels for label_id in label_ids) if labels else False)
    return df[mask]


def has_all_labels(df: pd.DataFrame, gmail: 'Gmail', label_names: List[str]) -> pd.DataFrame:
    """
    Filter emails that have all of the specified labels.
    
    Args:
        df: pandas DataFrame containing email data
        gmail: Gmail instance
        label_names: List of label names to filter by
        
    Returns:
        pd.DataFrame: Filtered DataFrame containing emails with all of the specified labels
    """
    # Get label IDs for all given names
    label_ids = []
    for label_name in label_names:
        label_id = gmail.get_label_id(label_name)
        if label_id:
            label_ids.append(label_id)
    
    if not label_ids:
        # If no labels exist, return empty DataFrame
        return pd.DataFrame()
    
    # Filter emails that have all of these label IDs
    mask = df['labels'].apply(lambda labels: all(label_id in labels for label_id in label_ids) if labels else False)
    return df[mask]


def count_by_label(df: pd.DataFrame, gmail: 'Gmail', label_name: str) -> int:
    """
    Count emails that have a specific label.
    
    Args:
        df: pandas DataFrame containing email data
        gmail: Gmail instance
        label_name: Name of the label to count
        
    Returns:
        int: Number of emails with the specified label
    """
    return len(has_label(df, gmail, label_name))


def get_emails_with_label(df: pd.DataFrame, gmail: 'Gmail', label_name: str) -> pd.DataFrame:
    """
    Get all emails that have a specific label.
    
    Args:
        df: pandas DataFrame containing email data
        gmail: Gmail instance
        label_name: Name of the label to filter by
        
    Returns:
        pd.DataFrame: Filtered DataFrame containing only emails with the specified label
    """
    return has_label(df, gmail, label_name)
