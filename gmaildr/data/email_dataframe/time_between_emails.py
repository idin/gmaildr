"""
Add time between emails features to EmailDataFrame.

This module contains the add_time_between_emails_features function that adds
time-based features between emails from the same sender.
"""

import pandas as pd
from typing import Optional
from .email_dataframe import EmailDataFrame


def add_time_between_emails_features(email_df: EmailDataFrame, in_place: bool = False) -> EmailDataFrame | None:
    """
    Add time-based features between emails from the same sender.
    
    This function adds features like time between emails from the same sender.
    It sorts the emails by sender_local_timestamp and then adds features like time between emails from same sender.
    
    Features added:
    - time_to_next_email_days: Time difference between consecutive emails from same sender in days
    - time_since_previous_email_days: Time difference between consecutive emails from same sender in days
    - time_since_first_email_days: Days since the first email from this sender
    - time_to_last_email_days: Days since the last email from this sender
    
    Args:
        email_df: EmailDataFrame to add time between emails features to
        in_place: Whether to modify the DataFrame in place or return a copy
        
    Returns:
        EmailDataFrame with time between emails features added, or None if in_place=True
    """
    if not in_place:
        email_df = email_df.copy()
    
    if 'sender_local_timestamp' not in email_df.columns:
        if not in_place:
            return email_df
        else:
            return None
    
    # Sort by sender and timestamp
    email_df.sort_values(['sender_email', 'sender_local_timestamp'], inplace=True)
    
    # Calculate time since previous email from same sender (0 for first email)
    email_df['time_since_previous_email_days'] = (email_df.groupby('sender_email')['sender_local_timestamp'].diff().dt.total_seconds() / (3600 * 24)).fillna(0)
    
    # Calculate time to next email from same sender (0 for last email)
    email_df['time_to_next_email_days'] = (-email_df.groupby('sender_email')['sender_local_timestamp'].diff(-1).dt.total_seconds() / (3600 * 24)).fillna(0)
    
    # Calculate time since first email from this sender
    first_emails = email_df.groupby('sender_email')['sender_local_timestamp'].transform('min')
    email_df['time_since_first_email_days'] = (email_df['sender_local_timestamp'] - first_emails).dt.total_seconds() / (3600 * 24)
    
    # Calculate time to last email from this sender
    last_emails = email_df.groupby('sender_email')['sender_local_timestamp'].transform('max')
    email_df['time_to_last_email_days'] = (last_emails - email_df['sender_local_timestamp']).dt.total_seconds() / (3600 * 24)
    
    if not in_place:
        return email_df
