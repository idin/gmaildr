"""
Analysis-Ready DataFrames for Clustering and Machine Learning.

This module provides functions to create dataframes optimized for clustering and analysis
by extracting numeric features, handling periodic variables, and encoding categorical variables.
"""

import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Any, Tuple
from sklearn.preprocessing import OneHotEncoder
import warnings

from .email_dataframe import EmailDataFrame
from ..columns import EMAIL_ML_SHOULD_NOT_HAVE_COLUMNS, EMAIL_ML_DF_COLUMNS, EMAIL_ML_DF_CORE_COLUMNS
from ...datascience.utils import df_must_have_columns, df_must_not_have_columns


def transform_email_features_for_ml(
    email_df: EmailDataFrame,
    drop_na_threshold: float = 0.5
) -> pd.DataFrame:
    """
    Transform email features for machine learning.
    
    Converts raw email features into proper numerical features suitable for ML algorithms.
    This includes:
    - Converting periodic features (hour, day_of_week) to sin/cos encoding
    - Encoding categorical variables
    - Scaling and normalizing features
    
    Args:
        email_df: EmailDataFrame to transform
        drop_na_threshold: Threshold for dropping columns with too many NaN values
        
    Returns:
        pandas DataFrame with transformed features ready for ML
    """
    if email_df.empty:
        raise ValueError("EmailDataFrame is empty")
    
    # Validate input EmailDataFrame has required columns
    df_must_have_columns(email_df, ['message_id'])
    
    # Start with a copy to avoid modifying original
    ml_dataframe = email_df.copy()
    
    print(f"DEBUG: Starting transformation with {len(ml_dataframe)} rows")
    print(f"DEBUG: DataFrame columns: {ml_dataframe.columns.tolist()}")
    
    # Drop non-ML columns that should not be used by models (but keep what we need for transformation)
    # We need to keep some columns temporarily for the transformation process
    columns_to_drop_early = ['sender_email', 'subject', 'text_content', 'thread_id', 'recipient_email', 'labels']
    columns_to_drop_early = [col for col in columns_to_drop_early if col in ml_dataframe.columns]
    if columns_to_drop_early:
        print(f"DEBUG: Dropping non-ML columns early: {columns_to_drop_early}")
        ml_dataframe = ml_dataframe.drop(columns=columns_to_drop_early)
    
    # 1. Basic numeric features (always included) - convert to float
    numeric_features = [
        'size_bytes', 'size_kb', 'year', 'month', 'day', 'hour'
    ]
    
    for col in numeric_features:
        if col in ml_dataframe.columns:
            ml_dataframe[col] = ml_dataframe[col].astype(float)
    
    # 2. Handle periodic features (hour, month, day)
    if not 'hour' in ml_dataframe.columns:
        raise KeyError("Hour column not found in dataframe")
    ml_dataframe['hour_sin'] = np.sin(2 * np.pi * ml_dataframe['hour'] / 24)
    ml_dataframe['hour_cos'] = np.cos(2 * np.pi * ml_dataframe['hour'] / 24)
    ml_dataframe = ml_dataframe.drop(columns=['hour'])

    # Handle day_of_week - convert string day names to numeric (0=Monday, 6=Sunday)
    if 'day_of_week' not in ml_dataframe.columns:
        raise KeyError("Day of week column not found in dataframe")

    # if day_of_week is not numeric, convert it to numeric by mapping the day names to numbers
    if not ml_dataframe['day_of_week'].dtype == np.number:
        day_mapping = {
            'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
            'friday': 4, 'saturday': 5, 'sunday': 6
        }
        ml_dataframe['day_of_week'] = ml_dataframe['day_of_week'].str.lower().map(day_mapping)

    ml_dataframe['day_of_week_sin'] = np.sin(2 * np.pi * ml_dataframe['day_of_week'] / 7)
    ml_dataframe['day_of_week_cos'] = np.cos(2 * np.pi * ml_dataframe['day_of_week'] / 7)
    # drop day_of_week. We do not need it. 
    ml_dataframe = ml_dataframe.drop(columns=['day_of_week'])

    # Handle day_of_year if available
    if 'day_of_year' not in ml_dataframe.columns:
        # create day_of_year from timestamp
        if 'sender_local_timestamp' not in ml_dataframe.columns:
            raise KeyError("sender_local_timestamp column not found in dataframe")
        ml_dataframe['day_of_year'] = ml_dataframe['sender_local_timestamp'].dt.dayofyear
    else:
        ml_dataframe['day_of_year'] = ml_dataframe['day_of_year'].astype(int)

    ml_dataframe['day_of_year_sin'] = np.sin(2 * np.pi * ml_dataframe['day_of_year'] / 365)
    ml_dataframe['day_of_year_cos'] = np.cos(2 * np.pi * ml_dataframe['day_of_year'] / 365)
    ml_dataframe = ml_dataframe.drop(columns=['day_of_year'])

    # drop time columns that we've processed
    columns_to_drop = []
    if 'day' in ml_dataframe.columns:
        columns_to_drop.append('day')
    if 'month' in ml_dataframe.columns:
        columns_to_drop.append('month')
    
    ml_dataframe = ml_dataframe.drop(columns=columns_to_drop)
    
    # 3. Boolean features (convert to numeric)
    boolean_features = [
        'has_attachments', 'is_read', 'is_important'
    ]
    
    for col in boolean_features:
        if col in ml_dataframe.columns:
            ml_dataframe[col] = ml_dataframe[col].astype(int)
    
    # 4. Text features (auto-detected when available)
    if 'text_content' in ml_dataframe.columns and bool(ml_dataframe['text_content'].notna().any()):
        text_features = [
            'word_count', 'sentence_count', 'avg_sentence_length',
            'capitalization_ratio', 'question_count', 'exclamation_count',
            'url_count', 'email_count', 'phone_count'
        ]
        
        for col in text_features:
            if col in ml_dataframe.columns:
                ml_dataframe[col] = ml_dataframe[col].astype(float)
    
    # 5. Analysis metrics (auto-detected when text content is available)
    if 'text_content' in ml_dataframe.columns and bool(ml_dataframe['text_content'].notna().any()):
        # Include all available metric columns (actual implemented metrics)
        metric_features = [
            'has_unsubscribe_link', 'has_marketing_language', 'has_legal_disclaimer',
            'has_promotional_content', 'has_tracking_pixels', 'has_bulk_email_indicators',
            'external_link_count', 'image_count', 'exclamation_count', 'caps_word_count',
            'html_to_text_ratio', 'link_to_text_ratio', 'caps_ratio', 'promotional_word_ratio'
        ]
        
        for col in metric_features:
            if col in ml_dataframe.columns:
                ml_dataframe[col] = ml_dataframe[col].astype(float)
    
    # 6. Categorical features (one-hot encoding)
    # Create all expected categorical features by checking in_folder values
    if 'in_folder' in ml_dataframe.columns:
        ml_dataframe['in_folder_inbox'] = (ml_dataframe['in_folder'] == 'inbox').astype(int)
        ml_dataframe['in_folder_archive'] = (ml_dataframe['in_folder'] == 'archive').astype(int)
        ml_dataframe['in_folder_spam'] = (ml_dataframe['in_folder'] == 'spam').astype(int)
        ml_dataframe['in_folder_trash'] = (ml_dataframe['in_folder'] == 'trash').astype(int)
        ml_dataframe['in_folder_drafts'] = (ml_dataframe['in_folder'] == 'drafts').astype(int)
        ml_dataframe['in_folder_sent'] = (ml_dataframe['in_folder'] == 'sent').astype(int)
        ml_dataframe['in_folder_nan'] = ml_dataframe['in_folder'].isna().astype(int)
    else:
        raise KeyError("in_folder column not found in dataframe")
    # 7. Handle missing values
    # Drop columns with too many NaN values
    na_ratio = ml_dataframe.isna().sum() / len(ml_dataframe)
    columns_to_drop = na_ratio[na_ratio > drop_na_threshold].index
    ml_dataframe = ml_dataframe.drop(columns=columns_to_drop)
    
    print(f"DEBUG: After dropping NaN columns: {len(ml_dataframe)} rows and {len(ml_dataframe.columns)} columns")
    
    # Fill remaining NaN values with median for numeric columns
    numeric_cols = ml_dataframe.select_dtypes(include=[np.number]).columns
    ml_dataframe[numeric_cols] = ml_dataframe[numeric_cols].fillna(
        ml_dataframe[numeric_cols].median()
    )

    # Drop remaining non-ML columns that should not be used by models
    columns_to_drop = [col for col in EMAIL_ML_SHOULD_NOT_HAVE_COLUMNS if col in ml_dataframe.columns]
    if columns_to_drop:
        print(f"DEBUG: Dropping remaining non-ML columns: {columns_to_drop}")
        ml_dataframe = ml_dataframe.drop(columns=columns_to_drop)
    
    # 8. Validate the final ML DataFrame
    # Must have message_id column
    df_must_have_columns(ml_dataframe, ['message_id'])
    
    # Check for core ML columns (these should always be present)
    df_must_have_columns(ml_dataframe, EMAIL_ML_DF_CORE_COLUMNS)
    
    # Must not have non-ML columns
    df_must_not_have_columns(ml_dataframe, EMAIL_ML_SHOULD_NOT_HAVE_COLUMNS)
    
    # Return pandas DataFrame
    return ml_dataframe
