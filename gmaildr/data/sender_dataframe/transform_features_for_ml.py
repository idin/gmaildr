"""
Transform sender features for machine learning.

This module provides functions to transform raw sender features into
ML-ready numerical features suitable for machine learning algorithms.
"""

import pandas as pd
import numpy as np

from ..columns import SENDER_ML_DF_COLUMNS, SENDER_ML_SHOULD_NOT_HAVE_COLUMNS, SENDER_DF_COLUMNS    
from ...datascience.utils import df_must_have_columns, df_must_not_have_columns


def transform_sender_features_for_ml(
    sender_df: pd.DataFrame,
    drop_na_threshold: float = 0.5
) -> pd.DataFrame:
    """
    Transform sender features for machine learning.
    
    Converts raw sender features into proper numerical features suitable for ML algorithms.
    This includes:
    - Converting periodic features to sin/cos encoding
    - Encoding categorical variables
    - Scaling and normalizing features
    
    Args:
        sender_df: SenderDataFrame or pandas DataFrame with sender data to transform
        drop_na_threshold: Threshold for dropping columns with too many NaN values
        
    Returns:
        pandas DataFrame with transformed features ready for ML
    """
    if sender_df.empty:
        raise ValueError("Sender DataFrame is empty")
    
    # Validate input has required columns
    df_must_have_columns(sender_df, ['sender_email'])
    df_must_have_columns(sender_df, SENDER_DF_COLUMNS)
    
    # Start with a copy to avoid modifying original
    ml_dataframe = sender_df.copy()
    
    # Drop non-ML columns that should not be used by models
    columns_to_drop_early = ['first_email_timestamp', 'last_email_timestamp', 'display_name', 'most_common_recipient']
    columns_to_drop_early = [col for col in columns_to_drop_early if col in ml_dataframe.columns]
    if columns_to_drop_early:
        ml_dataframe = ml_dataframe.drop(columns=columns_to_drop_early)
    
    # 1. Basic numeric features (convert to float)
    numeric_features = [
        'total_emails', 'unique_subjects', 'date_range_days', 'emails_per_day',
        'total_size_bytes', 'mean_email_size_bytes', 'max_email_size_bytes',
        'min_email_size_bytes', 'std_email_size_bytes', 'read_ratio', 'important_ratio',
        'starred_ratio', 'subject_language_diversity', 'english_subject_ratio',
        'mean_subject_language_confidence', 'text_language_diversity', 'english_text_ratio',
        'mean_text_language_confidence', 'mean_subject_length_chars', 'std_subject_length_chars',
        'mean_text_length_chars', 'std_text_length_chars', 'inbox_count', 'archive_count',
        'trash_count', 'role_based_emails_count', 'role_based_emails_ratio',
        'unique_recipients', 'recipient_diversity', 'forwarded_emails_count',
        'forwarded_emails_ratio', 'subject_length_variation_coef', 'text_length_variation_coef',
        'name_variations', 'unique_subject_ratio'
    ]
    
    for col in numeric_features:
        if col in ml_dataframe.columns:
            ml_dataframe[col] = ml_dataframe[col].astype(float)
    
    # 2. Handle periodic features (sin/cos encoding for core features)
    periodic_features = ['total_emails', 'unique_subjects', 'mean_email_size_bytes']
    
    for col in periodic_features:
        if col in ml_dataframe.columns:
            # Normalize to 0-1 range for sin/cos encoding
            col_min = ml_dataframe[col].min()
            col_max = ml_dataframe[col].max()
            if col_max > col_min:
                normalized = (ml_dataframe[col] - col_min) / (col_max - col_min)
            else:
                normalized = ml_dataframe[col] * 0  # All zeros if no variation
            
            ml_dataframe[f'{col}_sin'] = np.sin(2 * np.pi * normalized)
            ml_dataframe[f'{col}_cos'] = np.cos(2 * np.pi * normalized)
            ml_dataframe = ml_dataframe.drop(columns=[col])
    
    # 3. Handle temporal entropy features (sin/cos encoding)
    entropy_features = ['day_of_week_entropy', 'hour_of_day_entropy']
    
    for col in entropy_features:
        if col in ml_dataframe.columns:
            # Normalize entropy values (typically 0 to log(n))
            col_min = ml_dataframe[col].min()
            col_max = ml_dataframe[col].max()
            if col_max > col_min:
                normalized = (ml_dataframe[col] - col_min) / (col_max - col_min)
            else:
                normalized = ml_dataframe[col] * 0
            
            ml_dataframe[f'{col}_sin'] = np.sin(2 * np.pi * normalized)
            ml_dataframe[f'{col}_cos'] = np.cos(2 * np.pi * normalized)
            ml_dataframe = ml_dataframe.drop(columns=[col])
    
    # 4. Handle ratio features (sin/cos encoding)
    ratio_features = ['weekend_ratio', 'business_hours_ratio', 'burst_days_ratio']
    
    for col in ratio_features:
        if col in ml_dataframe.columns:
            # Ratios are already 0-1, perfect for sin/cos encoding
            ml_dataframe[f'{col}_sin'] = np.sin(2 * np.pi * ml_dataframe[col])
            ml_dataframe[f'{col}_cos'] = np.cos(2 * np.pi * ml_dataframe[col])
            ml_dataframe = ml_dataframe.drop(columns=[col])
    
    # 5. Boolean features (convert to numeric)
    boolean_features = [
        'is_role_based_sender', 'is_personal_domain', 'name_consistency'
    ]
    
    for col in boolean_features:
        if col in ml_dataframe.columns:
            ml_dataframe[col] = ml_dataframe[col].astype(int)
    
    # 6. Categorical features (one-hot encoding)
    categorical_features = ['domain', 'most_active_day', 'subject_primary_language', 'text_primary_language']
    
    for col in categorical_features:
        if col in ml_dataframe.columns:
            dummies = pd.get_dummies(ml_dataframe[col], prefix=col, dummy_na=True)
            for dummy_col in dummies.columns:
                ml_dataframe[dummy_col] = dummies[dummy_col]
    
    # 7. Handle missing values
    # Drop columns with too many NaN values
    na_ratio = ml_dataframe.isna().sum() / len(ml_dataframe)
    columns_to_drop = na_ratio[na_ratio > drop_na_threshold].index
    ml_dataframe = ml_dataframe.drop(columns=columns_to_drop)
    
    # Fill remaining NaN values with median for numeric columns
    numeric_cols = ml_dataframe.select_dtypes(include=[np.number]).columns
    ml_dataframe[numeric_cols] = ml_dataframe[numeric_cols].fillna(
        ml_dataframe[numeric_cols].median()
    )

    # Drop remaining non-ML columns that should not be used by models
    columns_to_drop = [col for col in SENDER_ML_SHOULD_NOT_HAVE_COLUMNS if col in ml_dataframe.columns]
    if columns_to_drop:
        ml_dataframe = ml_dataframe.drop(columns=columns_to_drop)
    
    # 8. Validate the final ML DataFrame
    # Must have sender_email column
    df_must_have_columns(ml_dataframe, ['sender_email'])
    df_must_have_columns(ml_dataframe, SENDER_ML_DF_COLUMNS)
    
    # Must not have non-ML columns
    df_must_not_have_columns(ml_dataframe, SENDER_ML_SHOULD_NOT_HAVE_COLUMNS)
    
    # Return pandas DataFrame
    return ml_dataframe
