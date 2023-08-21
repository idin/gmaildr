"""
Additional features for sender analysis.

This module contains functions that add features needed for sender statistics calculation.
"""

from ..email_dataframe import EmailDataFrame


def add_additional_features(email_df: EmailDataFrame) -> EmailDataFrame:
    """
    Add additional features to the email dataframe.
    
    Args:
        email_df: EmailDataFrame to add features to
        
    Returns:
        EmailDataFrame with additional features added
    """
    if 'subject_length_chars' not in email_df.columns and 'subject' in email_df.columns:
        email_df['subject_length_chars'] = email_df['subject'].str.len()
    if 'text_length_chars' not in email_df.columns and 'text_content' in email_df.columns:
        # Handle NaN values properly to avoid downcasting warnings
        text_lengths = email_df['text_content'].str.len()
        email_df['text_length_chars'] = text_lengths.where(text_lengths.notna(), 0).astype('int64')
    if 'subject_length_words' not in email_df.columns and 'subject' in email_df.columns:
        # Handle NaN values properly to avoid downcasting warnings
        subject_word_lengths = email_df['subject'].str.split().str.len()
        email_df['subject_length_words'] = subject_word_lengths.where(subject_word_lengths.notna(), 0).astype('int64')
    if 'text_length_words' not in email_df.columns and 'text_content' in email_df.columns:
        # Handle NaN values properly to avoid downcasting warnings
        text_word_lengths = email_df['text_content'].str.split().str.len()
        email_df['text_length_words'] = text_word_lengths.where(text_word_lengths.notna(), 0).astype('int64')

    # temporal features
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
        email_df['is_business_hour'] = (email_df['hour_of_day'] >= 9) & (email_df['hour_of_day'] <= 17)

    return email_df
