"""
Personal Email Classifier.

Simple function to classify emails as personal based on various indicators.
"""

import re
import pandas as pd
from typing import Optional


def is_personal_email(
        df: pd.DataFrame, *,
        subject_col: str = 'subject',
        sender_email_col: str = 'sender_email',
        sender_name_col: str = 'sender_name',
        snippet_col: Optional[str] = 'snippet'
) -> pd.DataFrame:
    """
    Classify emails as personal by adding an 'is_personal' column (True/False/None).
    
    Conservative approach: Only classifies as True/False when confident.
    Returns None when unsure.
    
    Args:
        df: Input DataFrame with email data.
        subject_col: Name of the subject column.
        sender_email_col: Name of the sender email column.
        sender_name_col: Name of the sender name column.
        snippet_col: Name of the snippet column (optional).
        
    Returns:
        New DataFrame with 'is_personal' column added (True/False/None).
    """
    if df.empty:
        return df.copy()
    
    # Create a copy to avoid modifying the original
    result_df = df.copy()
    
    # Initialize all emails as unsure (None) - conservative approach
    result_df['is_personal'] = None
    
    # ============================================================================
    # STRONG PERSONAL INDICATORS (High confidence it IS personal)
    # ============================================================================
    strong_personal_indicators = []
    
    # Personal email domains - Very strong indicator of personal emails
    # Examples: john@gmail.com, sarah@yahoo.com, mike@icloud.com
    if sender_email_col in df.columns:
        personal_domains = [
            r'@gmail\.com$', r'@yahoo\.com$', r'@hotmail\.com$', r'@outlook\.com$',
            r'@icloud\.com$', r'@me\.com$', r'@mac\.com$', r'@live\.com$'
        ]
        
        for domain_pattern in personal_domains:
            strong_personal_indicators.append(
                df[sender_email_col].str.contains(domain_pattern, case=False, na=False)
            )
    
    # Real person names - Strong indicator of personal emails
    # Examples: "John Smith", "Sarah Johnson", "Mike Wilson"
    # Excludes: "Dr. Smith", "John Smith Inc", "JOHN SMITH"
    if sender_name_col in df.columns:
        real_name_pattern = r'^[A-Z][a-z]+ [A-Z][a-z]+$'
        strong_personal_indicators.append(
            df[sender_name_col].str.match(real_name_pattern, na=False)
        )
    
    # Family/friend specific content in subject lines
    # Examples: "Hi mom", "Dinner with family", "Friend's birthday party"
    if subject_col in df.columns:
        family_patterns = [
            r'\b(mom|dad|wife|husband|son|daughter|brother|sister)\b',
            r'\b(family|friend|friends)\b',
        ]
        
        for pattern in family_patterns:
            strong_personal_indicators.append(
                df[subject_col].str.contains(pattern, case=False, na=False)
            )
    
    # Personal emotional content in email body/snippet
    # Examples: "Love you", "Miss you", "See you soon", "Personal matter"
    if snippet_col and snippet_col in df.columns:
        family_content_patterns = [
            r'\b(love you|miss you|see you soon)\b',
            r'\b(family|friend|personal)\b',
        ]
        
        for pattern in family_content_patterns:
            strong_personal_indicators.append(
                df[snippet_col].str.contains(pattern, case=False, na=False)
            )
    
    # ============================================================================
    # STRONG NON-PERSONAL INDICATORS (High confidence it's NOT personal)
    # ============================================================================
    strong_non_personal_indicators = []
    
    # Company/business domains - Strong indicator of business emails
    # Examples: john@company.com, sarah@corp.com, mike@business.com
    if sender_email_col in df.columns:
        company_domains = [
            r'@(company|corp|inc|llc|ltd|business|enterprise)\.',
            r'@[a-z]+\.(edu|gov|mil)$',  # Educational/government domains
        ]
        
        for domain_pattern in company_domains:
            strong_non_personal_indicators.append(
                df[sender_email_col].str.contains(domain_pattern, case=False, na=False)
            )
    
    # Company names in sender field - Strong indicator of business emails
    # Examples: "John Smith Inc", "ACME CORPORATION", "Tech Solutions Co"
    if sender_name_col in df.columns:
        company_name_patterns = [
            r'\b(inc|corp|llc|ltd|company|co)\b',
            r'[A-Z]{4,}',  # All caps words (likely company names)
        ]
        
        for pattern in company_name_patterns:
            strong_non_personal_indicators.append(
                df[sender_name_col].str.contains(pattern, case=False, na=False)
            )
    
    # Business-specific content in subject lines
    # Examples: "Meeting tomorrow", "Project deadline", "Client presentation"
    if subject_col in df.columns:
        business_patterns = [
            r'\b(meeting|conference|presentation|project|deadline)\b',
            r'\b(client|customer|vendor|partner|stakeholder)\b',
        ]
        
        for pattern in business_patterns:
            strong_non_personal_indicators.append(
                df[subject_col].str.contains(pattern, case=False, na=False)
            )
    
    # ============================================================================
    # CLASSIFICATION LOGIC - Conservative approach
    # ============================================================================
    # Only classify as True/False when we have strong confidence indicators
    # Requires at least 2 strong indicators to make a confident classification
    for idx in df.index:
        # Count how many strong personal indicators this email matches
        personal_score = sum(1 for indicator in strong_personal_indicators if indicator.iloc[idx])
        # Count how many strong non-personal indicators this email matches
        non_personal_score = sum(1 for indicator in strong_non_personal_indicators if indicator.iloc[idx])
        
        # Classification rules:
        # - True: 2+ strong personal indicators (definitely personal)
        # - False: 2+ strong non-personal indicators (definitely not personal)
        # - None: Less than 2 strong indicators of either type (unsure)
        if personal_score >= 2:
            result_df.loc[idx, 'is_personal'] = True
        elif non_personal_score >= 2:
            result_df.loc[idx, 'is_personal'] = False
        # Otherwise remains None (unsure) - conservative approach
    
    return result_df
