


"""
Aggregate emails by sender to create comprehensive sender aggregations.

This function takes an EmailDataFrame and aggregates it by sender_email to create
a SenderDataFrame with one row per sender containing all aggregated metrics.
"""

import pandas as pd
from typing import Union, List, Dict, Any
from ..email_dataframe.email_dataframe import EmailDataFrame
from ..email_dataframe.temporal_features import add_temporal_features
from ..email_dataframe.text_features import add_text_features
from ..email_dataframe.time_between_emails import add_time_between_emails_features

AGGREGATE_FEATURES = [
    # Basic metrics
    'total_emails',
    'unique_subjects',
    'first_email_timestamp',
    'last_email_timestamp',
    'date_range_days',
    'emails_per_day',
    
    # Size metrics
    'total_size_bytes',
    'mean_email_size_bytes',
    'max_email_size_bytes',
    'min_email_size_bytes',
    'std_email_size_bytes',
    
    # Status ratios
    'read_ratio',
    'important_ratio',
    'starred_ratio',
    
    # Language metrics
    'subject_primary_language',
    'subject_language_diversity',
    'english_subject_ratio',
    'mean_subject_language_confidence',
    'text_primary_language',
    'text_language_diversity',
    'english_text_ratio',
    'mean_text_language_confidence',
    
    # Role-based metrics
    'is_role_based_sender',
    
    # Temporal metrics
    'most_active_day',
    'weekend_ratio',
    'most_active_hour',
    'business_hours_ratio',
    
    # Text metrics
    'mean_subject_length_chars',
    
    # Additional metrics from sender_dataframe.py
    'unique_threads',
    'inbox_count',
    'archive_count',
    'trash_count',
    'role_based_emails_count',
    'role_based_emails_ratio',
    'unique_recipients',
    'recipient_diversity',
    'most_common_recipient',
    'forwarded_emails_count',
    'forwarded_emails_ratio',
    'std_subject_length_chars',
    'subject_length_variation_coef',
    'mean_text_length_chars',
    'std_text_length_chars',
    'text_length_variation_coef',
    'domain',
    'is_personal_domain',
    'name_consistency',
    'display_name',
    'name_variations',
    'unique_subject_ratio',
]


def aggregate_emails_by_sender(
    df: Union[EmailDataFrame, pd.DataFrame, List[Dict[str, Any]], List[Any]]
) -> pd.DataFrame:

    # Ensure we have an EmailDataFrame
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be an EmailDataFrame or a pandas DataFrame")
    
    # Just work with the pandas DataFrame directly
    df = df.copy()
    
    # Add basic temporal features that the aggregation needs
    if 'timestamp' in df.columns:
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['hour_of_day'] = df['timestamp'].dt.hour
        df['is_weekend'] = df['day_of_week'].isin([5, 6])  # Saturday, Sunday
        df['is_business_hour'] = (df['hour_of_day'] >= 9) & (df['hour_of_day'] <= 17)
    else:
        raise KeyError("timestamp column not found in df")
    
    # Add basic text features
    if 'subject' in df.columns:
        df['subject_length_chars'] = df['subject'].str.len()
    else:
        raise KeyError("subject column not found in df")

    if 'text_content' in df.columns:
        df['text_length_chars'] = df['text_content'].str.len()

    
    # aggregate by sender using comprehensive aggregations
    pandas_df = df
    if not isinstance(pandas_df, pd.DataFrame):
        raise TypeError("pandas_df must be a pd.DataFrame")
    
    # Calculate comprehensive sender aggregations
    sender_aggregation = (
        pandas_df.groupby('sender_email', as_index=False) 
        .agg(
            # Basic metrics
            total_emails=('message_id', 'count'),
            unique_subjects=('subject', 'nunique'),
            first_email_timestamp=('timestamp', 'min'),
            last_email_timestamp=('timestamp', 'max'),
            
            # Size metrics
            total_size_bytes=('size_bytes', 'sum'),
            mean_email_size_bytes=('size_bytes', 'mean'),
            max_email_size_bytes=('size_bytes', 'max'),
            min_email_size_bytes=('size_bytes', 'min'),
            std_email_size_bytes=('size_bytes', 'std'),
            
            # Status ratios
            read_ratio=('is_read', 'mean'),
            important_ratio=('is_important', 'mean'),
            starred_ratio=('is_starred', 'mean'),
            
            # Language metrics
            subject_primary_language=('subject_language', lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else None),
            subject_language_diversity=('subject_language', 'nunique'),
            english_subject_ratio=('subject_language', lambda x: (x == 'en').mean()),
            mean_subject_language_confidence=('subject_language_confidence', 'mean'),
            text_primary_language=('text_language', lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else None),
            text_language_diversity=('text_language', 'nunique'),
            english_text_ratio=('text_language', lambda x: (x == 'en').mean()),
            mean_text_language_confidence=('text_language_confidence', 'mean'),
            
            # Role-based metrics
            is_role_based_sender=('has_role_based_email', 'first'),
            role_based_emails_count=('has_role_based_email', 'sum'),
            role_based_emails_ratio=('has_role_based_email', 'mean'),
            
            # Temporal metrics
            most_active_day=('day_of_week', lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else None),
            weekend_ratio=('is_weekend', 'mean'),
            most_active_hour=('hour_of_day', lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else None),
            business_hours_ratio=('is_business_hour', 'mean'),
            
            # Text metrics
            mean_subject_length_chars=('subject_length_chars', 'mean'),
            std_subject_length_chars=('subject_length_chars', 'std'),
            mean_text_length_chars=('text_length_chars', 'mean'),
            std_text_length_chars=('text_length_chars', 'std'),
            
            # Thread metrics
            unique_threads=('thread_id', 'nunique'),
            
            # Recipient metrics
            unique_recipients=('recipient_email', 'nunique'),
            most_common_recipient=('recipient_email', lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else None),
            
            # Forwarding metrics
            forwarded_emails_count=('is_forwarded', 'sum'),
            forwarded_emails_ratio=('is_forwarded', 'mean'),
            
            # Name metrics
            name_consistency=('sender_name', lambda x: x.nunique() == 1),
            display_name=('sender_name', lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else None),
            name_variations=('sender_name', 'nunique'),
            
            # Folder-based metrics (using in_folder column)
            inbox_count=('in_folder', lambda x: (x == 'inbox').sum()),
            archive_count=('in_folder', lambda x: (x == 'archive').sum()),
            trash_count=('in_folder', lambda x: (x == 'trash').sum()),
        )
    )
    if not isinstance(sender_aggregation, pd.DataFrame):
        raise TypeError("sender_aggregation must be a pd.DataFrame")
        
    sender_aggregation['date_range_days'] = (
        sender_aggregation['last_email_timestamp'] - sender_aggregation['first_email_timestamp']
    ).dt.days
    # Derived calculations
    sender_aggregation['emails_per_day'] = sender_aggregation['total_emails'] / sender_aggregation['date_range_days'].replace(0, 1)
    
    # Recipient diversity ratio
    sender_aggregation['recipient_diversity'] = sender_aggregation['unique_recipients'] / sender_aggregation['total_emails']
    
    # Subject length variation coefficient
    sender_aggregation['subject_length_variation_coef'] = (
        sender_aggregation['std_subject_length_chars'] / sender_aggregation['mean_subject_length_chars'].replace(0, 1)
    )
    
    # Text length variation coefficient
    sender_aggregation['text_length_variation_coef'] = (
        sender_aggregation['std_text_length_chars'] / sender_aggregation['mean_text_length_chars'].replace(0, 1)
    )
    
    # Domain extraction from sender_email
    sender_aggregation['domain'] = sender_aggregation['sender_email'].str.split('@').str[1]
    sender_aggregation['is_personal_domain'] = sender_aggregation['domain'].isin(['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com'])
    
    # Subject pattern analysis
    sender_aggregation['unique_subject_ratio'] = sender_aggregation['unique_subjects'] / sender_aggregation['total_emails']
    
    # TODO: Missing features that require more complex analysis:
    # - inbox_count, archive_count, trash_count (labels aggregation - requires labels column)
    # - subject_length_entropy, text_length_entropy (requires entropy calculation function)
    # - repeated_subject_count (requires subject pattern analysis)
    # - subject_variation_coefficient (requires subject length variation analysis)
    # - subject_keywords (requires keyword extraction from subjects)

    missing_features = set(AGGREGATE_FEATURES) - set(sender_aggregation.columns)
    if missing_features:
        raise RuntimeError(f"Missing features: {missing_features}")
    
    # Create SenderDataFrame
    from .sender_dataframe import SenderDataFrame
    gmail_instance = df._gmail_instance if hasattr(df, '_gmail_instance') else None
    return SenderDataFrame(sender_aggregation, gmail=gmail_instance)