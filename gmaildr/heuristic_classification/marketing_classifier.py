"""
Marketing Email Classifier.

Simple function to classify emails as marketing based on various indicators.
"""

import re
from typing import List, Optional

import pandas as pd


def _check_marketing_domain_patterns(df: pd.DataFrame, sender_email_col: str) -> List[pd.Series]:
    """Check for marketing domain patterns in sender emails.
    
    Args:
        df: Input DataFrame with email data.
        sender_email_col: Name of the sender email column.
        
    Returns:
        List of boolean series indicating marketing domain matches.
    """
    marketing_domain_patterns = [
        r'@(marketing|promo|sales|offers|deals|newsletter|updates)\.',
        r'@[a-z]+\.(com|org|net)$',  # Generic marketing domains
    ]
    
    indicators = []
    for pattern in marketing_domain_patterns:
        indicators.append(
            df[sender_email_col].str.contains(pattern, case=False, na=False)
        )
    return indicators


def _check_marketing_name_patterns(df: pd.DataFrame, sender_name_col: str) -> List[pd.Series]:
    """Check for marketing name patterns in sender names.
    
    Args:
        df: Input DataFrame with email data.
        sender_name_col: Name of the sender name column.
        
    Returns:
        List of boolean series indicating marketing name matches.
    """
    marketing_name_patterns = [
        r'\b(marketing|promo|sales|offers|deals|newsletter|updates)\b',
        r'\b(team|department|group|staff)\b',
        r'\b(no-reply|noreply|donotreply|donot-reply)\b',
    ]
    
    indicators = []
    for pattern in marketing_name_patterns:
        indicators.append(
            df[sender_name_col].str.contains(pattern, case=False, na=False)
        )
    return indicators


def _check_marketing_subject_patterns(df: pd.DataFrame, subject_col: str) -> List[pd.Series]:
    """Check for marketing subject patterns.
    
    Args:
        df: Input DataFrame with email data.
        subject_col: Name of the subject column.
        
    Returns:
        List of boolean series indicating marketing subject matches.
    """
    marketing_subject_patterns = [
        # Promotional language
        r'\b(sale|discount|offer|deal|promotion|special|limited|exclusive)\b',
        r'\b(save|save up to|up to \d+% off|buy now|order now)\b',
        r'\b(free|complimentary|bonus|gift|reward|bonus)\b',
        
        # Urgency and scarcity
        r'\b(limited time|act now|don\'t miss|last chance|expires|ending soon)\b',
        r'\b(only \d+ left|while supplies last|limited quantity)\b',
        
        # Product promotion
        r'\b(new|launch|introducing|announcing|preview|sneak peek)\b',
        r'\b(upgrade|premium|pro|plus|exclusive|vip)\b',
        
        # Call to action
        r'\b(click here|learn more|find out|discover|explore|shop now)\b',
        r'\b(register|sign up|subscribe|join|become a member)\b',
        
        # Marketing events
        r'\b(black friday|cyber monday|holiday|seasonal|clearance)\b',
        r'\b(flash sale|daily deal|deal of the day|weekend sale)\b',
    ]
    
    indicators = []
    for pattern in marketing_subject_patterns:
        indicators.append(
            df[subject_col].str.contains(pattern, case=False, na=False)
        )
    return indicators


def _check_marketing_content_patterns(df: pd.DataFrame, snippet_col: str) -> List[pd.Series]:
    """Check for marketing content patterns in snippets.
    
    Args:
        df: Input DataFrame with email data.
        snippet_col: Name of the snippet column.
        
    Returns:
        List of boolean series indicating marketing content matches.
    """
    marketing_content_patterns = [
        r'\b(sale|discount|offer|deal|promotion)\b',
        r'\b(save|buy now|order now|shop now)\b',
        r'\b(free|complimentary|bonus|gift)\b',
        r'\b(limited time|act now|don\'t miss)\b',
        r'\b(new|launch|introducing)\b',
        r'\b(click here|learn more|sign up)\b',
    ]
    
    indicators = []
    for pattern in marketing_content_patterns:
        indicators.append(
            df[snippet_col].str.contains(pattern, case=False, na=False)
        )
    return indicators


def is_marketing_email(
        df: pd.DataFrame, *,
        subject_col: str = 'subject',
        sender_email_col: str = 'sender_email',
        sender_name_col: str = 'sender_name',
        snippet_col: Optional[str] = 'snippet'
) -> pd.DataFrame:
    """
    Classify emails as marketing by adding an 'is_marketing' boolean column.
    
    Args:
        df: Input DataFrame with email data.
        subject_col: Name of the subject column.
        sender_email_col: Name of the sender email column.
        sender_name_col: Name of the sender name column.
        snippet_col: Name of the snippet column (optional).
        
    Returns:
        New DataFrame with 'is_marketing' column added.
    """
    if df.empty:
        return df.copy()
    
    # Create a copy to avoid modifying the original
    result_df = df.copy()
    
    # Marketing email indicators
    marketing_indicators = []
    
    # Check sender email patterns
    if sender_email_col in df.columns:
        marketing_indicators.extend(_check_marketing_domain_patterns(df, sender_email_col))
    
    # Check sender name patterns
    if sender_name_col in df.columns:
        marketing_indicators.extend(_check_marketing_name_patterns(df, sender_name_col))
    
    # Check subject patterns (marketing keywords)
    if subject_col in df.columns:
        marketing_indicators.extend(_check_marketing_subject_patterns(df, subject_col))
    
    # Check snippet/content patterns
    if snippet_col and snippet_col in df.columns:
        marketing_indicators.extend(_check_marketing_content_patterns(df, snippet_col))
    
    # Combine all indicators
    if marketing_indicators:
        # Email is marketing if it matches multiple indicators
        combined_score = sum(marketing_indicators)
        result_df['is_marketing'] = combined_score >= 2
    else:
        result_df['is_marketing'] = False
    
    return result_df
