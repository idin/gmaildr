"""
Text features for EmailDataFrame.

This module contains functions that add text-based features to EmailDataFrame.
"""

import pandas as pd
from .email_dataframe import EmailDataFrame


def add_text_features(email_df: EmailDataFrame, in_place: bool = False) -> EmailDataFrame | None:
    """
    Add text features to the email dataframe.
    
    Args:
        email_df: EmailDataFrame to add text features to
        in_place: Whether to modify the DataFrame in place or return a copy
        
    Returns:
        EmailDataFrame with text features added, or None if in_place=True
    """
    if in_place:
        # Modify in place
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
        
        return None
    else:
        # Return a copy
        result = email_df.copy()
        if 'subject_length_chars' not in result.columns and 'subject' in result.columns:
            result['subject_length_chars'] = result['subject'].str.len()
        if 'text_length_chars' not in result.columns and 'text_content' in result.columns:
            # Handle NaN values properly to avoid downcasting warnings
            text_lengths = result['text_content'].str.len()
            result['text_length_chars'] = text_lengths.where(text_lengths.notna(), 0).astype('int64')
        if 'subject_length_words' not in result.columns and 'subject' in result.columns:
            # Handle NaN values properly to avoid downcasting warnings
            subject_word_lengths = result['subject'].str.split().str.len()
            result['subject_length_words'] = subject_word_lengths.where(subject_word_lengths.notna(), 0).astype('int64')
        if 'text_length_words' not in result.columns and 'text_content' in result.columns:
            # Handle NaN values properly to avoid downcasting warnings
            text_word_lengths = result['text_content'].str.split().str.len()
            result['text_length_words'] = text_word_lengths.where(text_word_lengths.notna(), 0).astype('int64')

        return result
