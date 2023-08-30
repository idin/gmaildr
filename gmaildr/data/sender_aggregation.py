"""
Sender aggregation functions for transforming email data into sender-level features.

This module provides functions to aggregate EmailDataFrame data by sender_email
for clustering and analysis purposes. Returns standard pandas DataFrames.
"""

import pandas as pd
from typing import Optional

from ..utils import has_all_columns, has_none_of_columns

# Current sender aggregation columns (organized logically)
SENDER_DATA_COLUMNS = [
    # Identity
    'domain', 'is_personal_domain',
    
    # Volume metrics
    'total_emails', 'unique_messages', 'unique_subjects', 'unique_threads',
    
    # Temporal metrics
    'first_email_timestamp', 'last_email_timestamp', 'date_range_days', 'emails_per_day',
    'most_active_day', 'most_active_hour', 'weekend_ratio', 'business_hours_ratio',
    
    # Size metrics
    'total_size_bytes', 'mean_email_size_bytes', 'min_email_size_bytes',
    'max_email_size_bytes', 'std_email_size_bytes', 'mean_email_size_kb',
    
    # Engagement metrics
    'read_ratio', 'important_ratio', 'starred_ratio', 'attachment_ratio',
    
    # Folder distribution
    'inbox_count', 'archive_count', 'trash_count',
    'inbox_ratio', 'archive_ratio', 'trash_ratio',
    
    # Behavioral metrics
    'is_role_based_sender', 'forwarded_ratio',
    
    # Subject analysis
    'subject_primary_language', 'mean_subject_language_confidence', 'subject_language_diversity',
    'english_subject_ratio', 'mean_subject_length_chars', 'std_subject_length_chars',
    'subject_length_variation_coef', 'unique_subject_ratio',
    
    # Recipient analysis
    'unique_recipients', 'recipient_diversity', 'most_common_recipient', 'recipient_consistency_ratio',
    
    # Sender name analysis
    'unique_sender_names', 'sender_name_diversity', 'most_common_sender_name', 'sender_name_consistency_ratio'
]

# GROUP 0: Pre-aggregation columns (create helper columns before aggregation)
PRE_AGG_COLUMNS = {
    # Create helper columns for ratios
    'is_weekend': "df['day_of_week'].isin(['Saturday', 'Sunday'])",
    'is_business_hours': "df['hour'].between(9, 17)",
    'is_english_subject': "df['subject_language'] == 'en'",
    'is_inbox': "df['in_folder'] == 'inbox'",
    'is_archive': "df['in_folder'] == 'archive'",
    'is_trash': "df['in_folder'] == 'trash'",
    
    # Handle missing values for mode calculations
    'day_of_week_clean': "df['day_of_week'].fillna('unknown')",
    'hour_clean': "df['hour'].fillna(-1)",
    'subject_language_clean': "df['subject_language'].fillna('unknown')",
    'recipient_email_clean': "df['recipient_email'].fillna('unknown')",
    'sender_name_clean': "df['sender_name'].fillna('unknown')",
    
    # Create length columns
    'subject_length': "df['subject'].str.len()",
}

# Text pre-aggregation columns (when include_text_features=True)
TEXT_PRE_AGG_COLUMNS = {
    # Handle missing text language
    'text_language_clean': "df['text_language'].fillna('unknown')",
    'is_english_text': "df['text_language_clean'] == 'en'",
    
    # Create text length columns
    'text_length': "df['text_content'].str.len()",
}

# GROUP 1: Groupby columns
GROUPBY_COLUMNS = ['sender_email']

# GROUP 2: Aggregation columns (direct aggregation from email data)
AGG_COLUMNS = {
    # Volume metrics
    'total_emails': {'message_id': 'count'},
    'unique_messages': {'message_id': 'nunique'},
    'unique_subjects': {'subject': 'nunique'},
    'unique_threads': {'thread_id': 'nunique'},
    
    # Temporal metrics  
    'first_email_timestamp': {'timestamp': 'min'},
    'last_email_timestamp': {'timestamp': 'max'},
    'most_active_day': {'day_of_week_clean': lambda x: x.mode().iloc[0] if not x.mode().empty else 'unknown'},
    'most_active_hour': {'hour_clean': lambda x: x.mode().iloc[0] if not x.mode().empty else -1},
    'weekend_ratio': {'is_weekend': 'mean'},
    'business_hours_ratio': {'is_business_hours': 'mean'},
    
    # Size metrics
    'total_size_bytes': {'size_bytes': 'sum'},
    'mean_email_size_bytes': {'size_bytes': 'mean'},
    'min_email_size_bytes': {'size_bytes': 'min'},
    'max_email_size_bytes': {'size_bytes': 'max'},
    'std_email_size_bytes': {'size_bytes': 'std'},
    'mean_email_size_kb': {'size_kb': 'mean'},
    
    # Engagement ratios
    'read_ratio': {'is_read': 'mean'},
    'important_ratio': {'is_important': 'mean'},
    'starred_ratio': {'is_starred': 'mean'},
    'attachment_ratio': {'has_attachments': 'mean'},
    
    # Folder counts
    'inbox_count': {'is_inbox': 'sum'},
    'archive_count': {'is_archive': 'sum'},
    'trash_count': {'is_trash': 'sum'},
    
    # Behavioral
    'is_role_based_sender': {'has_role_based_email': 'first'},
    'forwarded_ratio': {'is_forwarded': 'mean'},
    
    # Subject analysis
    'subject_primary_language': {'subject_language_clean': lambda x: x.mode().iloc[0] if not x.mode().empty else 'unknown'},
    'mean_subject_language_confidence': {'subject_language_confidence': 'mean'},
    'subject_language_diversity': {'subject_language_clean': 'nunique'},
    'english_subject_ratio': {'is_english_subject': 'mean'},
    'mean_subject_length_chars': {'subject_length': 'mean'},
    'std_subject_length_chars': {'subject_length': 'std'},
    
    # Recipients
    'unique_recipients': {'recipient_email': 'nunique'},
    'most_common_recipient': {'recipient_email_clean': lambda x: x.mode().iloc[0] if not x.mode().empty else 'unknown'},
    
    # Sender names
    'unique_sender_names': {'sender_name': 'nunique'},
    'most_common_sender_name': {'sender_name_clean': lambda x: x.mode().iloc[0] if not x.mode().empty else 'unknown'},
}

# Text aggregation columns (when include_text_features=True)
TEXT_AGG_COLUMNS = {
    # Text language analysis
    'text_primary_language': {'text_language_clean': lambda x: x.mode().iloc[0] if not x.mode().empty else 'unknown'},
    'mean_text_language_confidence': {'text_language_confidence': 'mean'},
    'text_language_diversity': {'text_language_clean': 'nunique'},
    'english_text_ratio': {'is_english_text': 'mean'},
    
    # Text length analysis
    'mean_text_length_chars': {'text_length': 'mean'},
    'std_text_length_chars': {'text_length': 'std'},
}

# GROUP 3: Derived columns (calculated from aggregated results)
DERIVED_FROM_AGG_COLUMNS = {
    # Identity
    'domain': "df['sender_email'].str.split('@').str[1]",
    'is_personal_domain': "df['domain'].isin(['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com'])",
    
    # Temporal derived
    'date_range_days': "(df['last_email_timestamp'] - df['first_email_timestamp']).dt.days",
    'emails_per_day': "df['total_emails'] / (df['date_range_days'] + 1)",
    
    # Folder ratios
    'inbox_ratio': "df['inbox_count'] / df['total_emails']",
    'archive_ratio': "df['archive_count'] / df['total_emails']",
    'trash_ratio': "df['trash_count'] / df['total_emails']",
    
    # Subject derived
    'subject_length_variation_coef': "df['std_subject_length_chars'] / df['mean_subject_length_chars']",
    'unique_subject_ratio': "df['unique_subjects'] / df['total_emails']",
    
    # Recipient derived
    'recipient_diversity': "df['unique_recipients'] / df['total_emails']",
    'recipient_consistency_ratio': "(df['recipient_email_mode_count'] / df['total_emails']) if 'recipient_email_mode_count' in df.columns else 0",
    
    # Sender name derived
    'sender_name_diversity': "df['unique_sender_names'] / df['total_emails']",
    'sender_name_consistency_ratio': "(df['sender_name_mode_count'] / df['total_emails']) if 'sender_name_mode_count' in df.columns else 0",
}

# Text derived columns (when include_text_features=True)
TEXT_DERIVED_FROM_AGG_COLUMNS = {
    # Text length derived
    'text_length_variation_coef': "df['std_text_length_chars'] / df['mean_text_length_chars']",
}

# Advanced columns requiring additional processing (future implementation)
SENDER_DATA_ADVANCED_COLUMNS = [
    # Currently empty - all feasible columns moved to main list
]

# COLUMN LISTS (for reference and testing)
# Additional text-related columns (when include_text_features=True)
SENDER_DATA_TEXT_COLUMNS = [
    'text_primary_language', 'text_language_diversity', 'english_text_ratio',
    'mean_text_language_confidence', 'mean_text_length_chars', 'std_text_length_chars',
    'text_length_variation_coef'
]

# Complete sender data columns (all possible columns)
SENDER_DATA_ALL_COLUMNS = SENDER_DATA_COLUMNS + SENDER_DATA_TEXT_COLUMNS + SENDER_DATA_ADVANCED_COLUMNS


def aggregate_emails_by_sender(email_df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate emails by sender_email into sender-level features.
    
    Automatically detects whether text features are available and includes them
    if all required text columns are present.
    
    Args:
        email_df: pandas DataFrame with email data
        
    Returns:
        pandas DataFrame with sender-level aggregated features
    """
    if email_df.empty:
        return pd.DataFrame()

    # Validate text column consistency
    required_text_columns = ['text_content', 'text_language', 'text_language_confidence']
    
    has_all_text_cols = has_all_columns(email_df, required_text_columns)
    has_no_text_cols = has_none_of_columns(email_df, required_text_columns)
    
    if not has_all_text_cols and not has_no_text_cols:
        # Something in between - this is an error state
        from ..utils import get_missing_columns, get_existing_columns
        missing = get_missing_columns(email_df, required_text_columns)
        existing = get_existing_columns(email_df, required_text_columns)
        raise ValueError(
            f"Inconsistent text columns state. "
            f"Missing: {missing}, Present: {existing}. "
            f"DataFrame must have either all text columns or none of them."
        )
    
    # Automatically determine if we should process text features
    process_text_features = has_all_text_cols

    # Step 0: Create pre-aggregation columns
    df = email_df.copy()
    
    # Determine which pre-aggregation columns to use
    pre_agg_columns_to_use = PRE_AGG_COLUMNS.copy()
    if process_text_features:
        pre_agg_columns_to_use.update(TEXT_PRE_AGG_COLUMNS)
    
    # Create helper columns
    for col_name, formula in pre_agg_columns_to_use.items():
        try:
            df[col_name] = eval(formula)
        except Exception:
            # Skip if column doesn't exist
            pass

    # Step 1: Perform aggregation using AGG_COLUMNS
    # Determine which aggregation columns to use
    columns_to_aggregate = AGG_COLUMNS.copy()
    if process_text_features:
        columns_to_aggregate.update(TEXT_AGG_COLUMNS)
    
    # Build agg_dict - use pandas named aggregation format
    agg_dict = {}
    column_mapping = {}  # To track output column names
    
    for output_col, input_spec in columns_to_aggregate.items():
        for input_col, agg_func in input_spec.items():
            # Use pandas named aggregation format
            agg_dict[output_col] = pd.NamedAgg(column=input_col, aggfunc=agg_func)
            column_mapping[output_col] = input_col
    
    # Perform the groupby aggregation
    result = df.groupby(GROUPBY_COLUMNS[0], as_index=False).agg(**agg_dict)
    
    # Step 2: Calculate derived columns using DERIVED_FROM_AGG_COLUMNS
    df = result  # For eval context
    
    # Determine which derived columns to calculate
    derived_columns_to_calculate = DERIVED_FROM_AGG_COLUMNS.copy()
    if process_text_features:
        derived_columns_to_calculate.update(TEXT_DERIVED_FROM_AGG_COLUMNS)
    
    for output_col, formula in derived_columns_to_calculate.items():
        try:
            result[output_col] = eval(formula)
        except Exception as e:
            # Handle missing columns gracefully
            result[output_col] = None
    
    return result
        