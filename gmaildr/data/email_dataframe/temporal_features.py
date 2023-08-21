"""
Temporal features for EmailDataFrame.

This module contains functions that add time-based features to EmailDataFrame.
"""

import pandas as pd
from .email_dataframe import EmailDataFrame


def add_temporal_features(email_df: EmailDataFrame, in_place: bool = False) -> EmailDataFrame | None:
    """
    Add temporal features to the email dataframe.
    
    Args:
        email_df: EmailDataFrame to add temporal features to
        in_place: Whether to modify the DataFrame in place or return a copy
        
    Returns:
        EmailDataFrame with temporal features added, or None if in_place=True
    """
    if in_place:
        # Modify in place
        if 'sender_local_timestamp' not in email_df.columns:
            email_df['sender_local_timestamp'] = email_df['timestamp']
        else:
            # Handle timestamp fillna without triggering downcasting warnings
            email_df['sender_local_timestamp'] = email_df['sender_local_timestamp'].where(
                email_df['sender_local_timestamp'].notna(), 
                email_df['timestamp']
            )

        if 'timestamp' in email_df.columns and 'sender_local_timestamp' in email_df.columns:
            email_df['sender_time_difference_hours'] = (email_df['timestamp'] - email_df['sender_local_timestamp']).dt.total_seconds() / 3600
        
        if 'sender_local_timestamp' in email_df.columns and 'day_of_week' not in email_df.columns:
            email_df['day_of_week'] = email_df['sender_local_timestamp'].dt.dayofweek
        if 'sender_local_timestamp' in email_df.columns and 'hour_of_day' not in email_df.columns:
            email_df['hour_of_day'] = email_df['sender_local_timestamp'].dt.hour
        if 'sender_local_timestamp' in email_df.columns and 'is_weekend' not in email_df.columns:
            email_df['is_weekend'] = email_df['day_of_week'].isin([5, 6])
        if 'sender_local_timestamp' in email_df.columns and 'is_business_hour' not in email_df.columns:
            email_df['is_business_hour'] = (email_df['hour_of_day'] >= 9) & (email_df['hour_of_day'] <= 17) & (~email_df['is_weekend'])
        
        return None
    else:
        # Return a copy
        result = email_df.copy()
        if 'sender_local_timestamp' not in result.columns:
            result['sender_local_timestamp'] = result['timestamp']
        else:
            # Handle timestamp fillna without triggering downcasting warnings
            result['sender_local_timestamp'] = result['sender_local_timestamp'].where(
                result['sender_local_timestamp'].notna(), 
                result['timestamp']
            )

        if 'timestamp' in result.columns and 'sender_local_timestamp' in result.columns:
            result['sender_time_difference_hours'] = (result['timestamp'] - result['sender_local_timestamp']).dt.total_seconds() / 3600
        
        if 'sender_local_timestamp' in result.columns and 'day_of_week' not in result.columns:
            result['day_of_week'] = result['sender_local_timestamp'].dt.dayofweek
        if 'sender_local_timestamp' in result.columns and 'hour_of_day' not in result.columns:
            result['hour_of_day'] = result['sender_local_timestamp'].dt.hour
        if 'sender_local_timestamp' in result.columns and 'is_weekend' not in result.columns:
            result['is_weekend'] = result['day_of_week'].isin([5, 6])
        if 'sender_local_timestamp' in result.columns and 'is_business_hour' not in result.columns:
            result['is_business_hour'] = (result['hour_of_day'] >= 9) & (result['hour_of_day'] <= 17) & (~result['is_weekend'])

        return result
