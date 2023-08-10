"""
Marketing Email Classifier.

Simple function to classify emails as marketing based on various indicators.
"""

import re
import pandas as pd
from typing import Optional


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
        marketing_domain_patterns = [
            r'@(marketing|promo|sales|offers|deals|newsletter|updates)\.',
            r'@[a-z]+\.(com|org|net)$',  # Generic marketing domains
        ]
        
        for pattern in marketing_domain_patterns:
            marketing_indicators.append(
                df[sender_email_col].str.contains(pattern, case=False, na=False)
            )
    
    # Check sender name patterns
    if sender_name_col in df.columns:
        marketing_name_patterns = [
            r'\b(marketing|promo|sales|offers|deals|newsletter|updates)\b',
            r'\b(team|department|group|staff)\b',
            r'\b(no-reply|noreply|donotreply|donot-reply)\b',
        ]
        
        for pattern in marketing_name_patterns:
            marketing_indicators.append(
                df[sender_name_col].str.contains(pattern, case=False, na=False)
            )
    
    # Check subject patterns (marketing keywords)
    if subject_col in df.columns:
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
        
        for pattern in marketing_subject_patterns:
            marketing_indicators.append(
                df[subject_col].str.contains(pattern, case=False, na=False)
            )
    
    # Check snippet/content patterns
    if snippet_col and snippet_col in df.columns:
        marketing_content_patterns = [
            r'\b(sale|discount|offer|deal|promotion)\b',
            r'\b(save|buy now|order now|shop now)\b',
            r'\b(free|complimentary|bonus|gift)\b',
            r'\b(limited time|act now|don\'t miss)\b',
            r'\b(new|launch|introducing)\b',
            r'\b(click here|learn more|sign up)\b',
        ]
        
        for pattern in marketing_content_patterns:
            marketing_indicators.append(
                df[snippet_col].str.contains(pattern, case=False, na=False)
            )
    
    # Combine all indicators
    if marketing_indicators:
        # Email is marketing if it matches multiple indicators
        combined_score = sum(marketing_indicators)
        result_df['is_marketing'] = combined_score >= 2
    else:
        result_df['is_marketing'] = False
    
    return result_df
