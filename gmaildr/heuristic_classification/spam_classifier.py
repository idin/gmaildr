"""
Spam Email Classifier.

Simple function to classify emails as spam based on various indicators.
"""

import re
from typing import Optional

import pandas as pd


def is_spam_email(
        df: pd.DataFrame, *,
        subject_col: str = 'subject',
        sender_email_col: str = 'sender_email',
        sender_name_col: str = 'sender_name',
        snippet_col: Optional[str] = 'snippet'
) -> pd.DataFrame:
    """
    Classify emails as spam by adding an 'is_spam' boolean column.
    
    Args:
        df: Input DataFrame with email data.
        subject_col: Name of the subject column.
        sender_email_col: Name of the sender email column.
        sender_name_col: Name of the sender name column.
        snippet_col: Name of the snippet column (optional).
        
    Returns:
        New DataFrame with 'is_spam' column added.
    """
    if df.empty:
        return df.copy()
    
    # Create a copy to avoid modifying the original
    result_df = df.copy()
    
    # Spam email indicators
    spam_indicators = []
    
    # Check sender email patterns
    if sender_email_col in df.columns:
        spam_domain_patterns = [
            r'@[a-f0-9]{8,}\.',  # Random hex domains
            r'@[a-z]{1,3}\.[a-z]{1,3}$',  # Very short domains
            r'@[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$',  # IP addresses
            r'@[a-z]+[0-9]+[a-z]+\.',  # Random alphanumeric domains
        ]
        
        for pattern in spam_domain_patterns:
            spam_indicators.append(
                df[sender_email_col].str.contains(pattern, case=False, na=False)
            )
    
    # Check sender name patterns
    if sender_name_col in df.columns:
        spam_name_patterns = [
            r'^[A-Z0-9]{5,}$',  # All caps with numbers
            r'^[a-z0-9]{8,}$',  # All lowercase with numbers
            r'[0-9]{4,}',  # Many numbers
            r'[A-Z]{5,}',  # Many consecutive caps
        ]
        
        for pattern in spam_name_patterns:
            spam_indicators.append(
                df[sender_name_col].str.contains(pattern, case=False, na=False)
            )
    
    # Check subject patterns (spam keywords)
    if subject_col in df.columns:
        spam_subject_patterns = [
            # Urgent/emergency scams
            r'\b(urgent|emergency|immediate|critical|important)\b',
            r'\b(account suspended|security alert|verify account|confirm details)\b',
            r'\b(unauthorized access|suspicious activity|login attempt)\b',
            
            # Money scams
            r'\b(million|billion|inheritance|lottery|prize|winner)\b',
            r'\b(urgent business|investment opportunity|quick money)\b',
            r'\b(claim your|claim now|claim prize|claim reward)\b',
            
            # Pharmaceutical/health scams
            r'\b(viagra|cialis|weight loss|diet pill|enlargement)\b',
            r'\b(cheap|discount|generic|prescription|medication)\b',
            
            # Adult content
            r'\b(adult|porn|sex|dating|hookup|escort)\b',
            r'\b(single|lonely|meet|chat|video)\b',
            
            # Suspicious offers
            r'\b(free|100% free|no cost|no obligation|guaranteed)\b',
            r'\b(limited time|act now|don\'t miss|last chance)\b',
            r'\b(click here|visit now|respond now|reply now)\b',
            
            # Technical scams
            r'\b(computer|virus|malware|security|update)\b',
            r'\b(microsoft|apple|google|amazon|paypal)\b',
            r'\b(account|password|login|verify|confirm)\b',
        ]
        
        for pattern in spam_subject_patterns:
            spam_indicators.append(
                df[subject_col].str.contains(pattern, case=False, na=False)
            )
    
    # Check snippet/content patterns
    if snippet_col and snippet_col in df.columns:
        spam_content_patterns = [
            r'\b(urgent|emergency|immediate)\b',
            r'\b(million|billion|inheritance|lottery)\b',
            r'\b(viagra|cialis|weight loss)\b',
            r'\b(free|100% free|no cost)\b',
            r'\b(click here|visit now|respond now)\b',
            r'\b(account|password|verify|confirm)\b',
        ]
        
        for pattern in spam_content_patterns:
            spam_indicators.append(
                df[snippet_col].str.contains(pattern, case=False, na=False)
            )
    
    # Additional spam indicators
    if subject_col in df.columns:
        # Excessive punctuation
        spam_indicators.append(
            df[subject_col].str.count(r'[!?]{2,}') > 0
        )
        
        # Excessive caps
        spam_indicators.append(
            df[subject_col].str.count(r'[A-Z]') / df[subject_col].str.len() > 0.7
        )
        
        # Suspicious characters
        spam_indicators.append(
            df[subject_col].str.contains(r'[^\w\s!?.,\-]', na=False)
        )
    
    # Combine all indicators
    if spam_indicators:
        # Email is spam if it matches multiple indicators
        combined_score = sum(spam_indicators)
        result_df['is_spam'] = combined_score >= 3  # Higher threshold for spam
    else:
        result_df['is_spam'] = False
    
    return result_df
