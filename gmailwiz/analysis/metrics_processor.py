"""
Email metrics processor for applying content analysis to email DataFrames.

This module provides functions to apply email content metrics to pandas DataFrames
containing email data.
"""

import pandas as pd
import re
from typing import Optional
from tqdm.auto import tqdm

from .email_metrics import analyze_email_text


def add_content_metrics_to_dataframe(
    df: pd.DataFrame, *,
    text_column: str = 'text_content',
    subject_column: str = 'subject',
    show_progress: bool = True
) -> pd.DataFrame:
    """
    Add email content metrics to a DataFrame containing email data using vectorized operations.
    
    Args:
        df (pd.DataFrame): DataFrame with email data.
        text_column (str): Name of column containing email text content.
        subject_column (str): Name of column containing email subjects.
        show_progress (bool): Whether to show progress bar.
        
    Returns:
        pd.DataFrame: DataFrame with added metric columns.
    """
    from .email_metrics import EmailContentAnalyzer
    
    if show_progress:
        print("🔍 Analyzing email content with vectorized operations...")
    
    df_copy = df.copy()
    analyzer = EmailContentAnalyzer()
    
    # Get text and subject columns, fill NaN with empty strings
    text_series = df_copy[text_column].fillna('') if text_column in df_copy.columns else pd.Series([''] * len(df_copy))
    subject_series = df_copy[subject_column].fillna('') if subject_column in df_copy.columns else pd.Series([''] * len(df_copy))
    
    # Combine text and subject for analysis
    combined_text = subject_series + ' ' + text_series
    
    # Vectorized pattern matching
    if show_progress:
        print("  📝 Extracting text patterns...")
    
    # Flags using vectorized string operations
    df_copy['has_unsubscribe_link'] = combined_text.str.contains(
        '|'.join(analyzer.UNSUBSCRIBE_PATTERNS), case=False, regex=True, na=False
    )
    
    df_copy['has_marketing_language'] = combined_text.str.contains(
        '|'.join(analyzer.MARKETING_PATTERNS), case=False, regex=True, na=False
    )
    
    df_copy['has_legal_disclaimer'] = combined_text.str.contains(
        '|'.join(analyzer.LEGAL_PATTERNS), case=False, regex=True, na=False
    )
    
    df_copy['has_bulk_email_indicators'] = combined_text.str.contains(
        '|'.join(analyzer.BULK_EMAIL_INDICATORS), case=False, regex=True, na=False
    )
    
    # Promotional content (at least 2 promotional words)
    promotional_pattern = r'\b(' + '|'.join(analyzer.PROMOTIONAL_WORDS) + r')\b'
    promo_counts = combined_text.str.count(promotional_pattern, flags=re.IGNORECASE)
    df_copy['has_promotional_content'] = promo_counts >= 2
    
    if show_progress:
        print("  🔢 Calculating counts and ratios...")
    
    # Counts using vectorized operations
    df_copy['exclamation_count'] = combined_text.str.count('!')
    df_copy['caps_word_count'] = combined_text.str.count(r'\b[A-Z]{2,}\b')
    
    # Calculate ratios
    total_words = combined_text.str.count(r'\b\w+\b')
    total_words = total_words.replace(0, 1)  # Avoid division by zero
    
    df_copy['caps_ratio'] = (df_copy['caps_word_count'] / total_words).fillna(0)
    df_copy['promotional_word_ratio'] = (promo_counts / total_words).fillna(0)
    
    # HTML-based metrics (if HTML content available)
    # For now, set defaults - can be enhanced if HTML column is available
    df_copy['has_tracking_pixels'] = False
    df_copy['external_link_count'] = 0
    df_copy['image_count'] = 0
    df_copy['html_to_text_ratio'] = 0.0
    df_copy['link_to_text_ratio'] = 0.0
    
    if show_progress:
        print("  ✅ Content analysis complete!")
    
    return df_copy


def calculate_automated_email_score(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate an automated email score based on multiple metrics.
    
    Args:
        df (pd.DataFrame): DataFrame with content metrics already added.
        
    Returns:
        pd.DataFrame: DataFrame with added 'automated_email_score' column.
    """
    df_copy = df.copy()
    
    # Define weights for different indicators
    weights = {
        # Flags (strong indicators)
        'has_unsubscribe_link': 0.25,
        'has_marketing_language': 0.15,
        'has_legal_disclaimer': 0.10,
        'has_promotional_content': 0.15,
        'has_tracking_pixels': 0.20,
        'has_bulk_email_indicators': 0.30,
        
        # Ratios (scaled indicators)
        'link_to_text_ratio': 0.10,  # High link density
        'caps_ratio': 0.05,  # Excessive caps
        'promotional_word_ratio': 0.10,  # High promotional content
    }
    
    # Calculate weighted score
    score = 0.0
    
    # Add flag contributions
    for flag, weight in weights.items():
        if flag.startswith('has_') and flag in df_copy.columns:
            score += df_copy[flag].astype(float) * weight
    
    # Add ratio contributions (scaled)
    if 'link_to_text_ratio' in df_copy.columns:
        score += (df_copy['link_to_text_ratio'] * weights['link_to_text_ratio'])
    
    if 'caps_ratio' in df_copy.columns:
        score += (df_copy['caps_ratio'] * weights['caps_ratio'])
    
    if 'promotional_word_ratio' in df_copy.columns:
        score += (df_copy['promotional_word_ratio'] * weights['promotional_word_ratio'])
    
    # Normalize score to 0-1 range
    df_copy['automated_email_score'] = score.clip(0, 1)
    
    return df_copy


def classify_email_types(df: pd.DataFrame, *, score_threshold: float = 0.3) -> pd.DataFrame:
    """
    Classify emails as 'personal', 'automated', or 'mixed' based on automated score.
    
    Args:
        df (pd.DataFrame): DataFrame with automated_email_score column.
        score_threshold (float): Threshold for classifying as automated.
        
    Returns:
        pd.DataFrame: DataFrame with added 'email_type' column.
    """
    df_copy = df.copy()
    
    def classify_email(score):
        if score >= score_threshold:
            return 'automated'
        elif score >= score_threshold * 0.5:
            return 'mixed'
        else:
            return 'personal'
    
    df_copy['email_type'] = df_copy['automated_email_score'].apply(classify_email)
    
    return df_copy


def get_content_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Get summary statistics of content metrics.
    
    Args:
        df (pd.DataFrame): DataFrame with content metrics.
        
    Returns:
        pd.DataFrame: Summary statistics.
    """
    metric_columns = [col for col in df.columns if any(col.startswith(prefix) for prefix in ['has_', 'external_', 'image_', 'exclamation_', 'caps_', 'html_', 'link_', 'promotional_'])]
    
    if not metric_columns:
        return pd.DataFrame()
    
    summary = df[metric_columns].describe()
    
    # Add percentage for boolean columns
    for col in metric_columns:
        if col.startswith('has_'):
            summary.loc['percentage', col] = f"{(df[col].sum() / len(df) * 100):.1f}%"
    
    return summary


# Convenience function for full analysis
def analyze_email_dataframe(
    df: pd.DataFrame, *,
    text_column: str = 'text_content',
    subject_column: str = 'subject',
    score_threshold: float = 0.3,
    show_progress: bool = True
) -> pd.DataFrame:
    """
    Perform complete content analysis on email DataFrame.
    
    Args:
        df (pd.DataFrame): DataFrame with email data.
        text_column (str): Name of column containing email text.
        subject_column (str): Name of column containing subjects.
        score_threshold (float): Threshold for automated classification.
        show_progress (bool): Whether to show progress bars.
        
    Returns:
        pd.DataFrame: DataFrame with all metrics and classifications added.
    """
    print("📊 Starting email content analysis...")
    
    # Add content metrics
    df_with_metrics = add_content_metrics_to_dataframe(
        df, text_column, subject_column, show_progress
    )
    
    # Calculate automated email score
    df_with_score = calculate_automated_email_score(df_with_metrics)
    
    # Classify email types
    df_classified = classify_email_types(df_with_score, score_threshold)
    
    # Print summary
    if show_progress:
        print(f"\n✅ Analysis complete!")
        print(f"📧 Total emails analyzed: {len(df_classified)}")
        print(f"🤖 Automated emails: {(df_classified['email_type'] == 'automated').sum()}")
        print(f"👤 Personal emails: {(df_classified['email_type'] == 'personal').sum()}")
        print(f"🔀 Mixed emails: {(df_classified['email_type'] == 'mixed').sum()}")
    
    return df_classified
