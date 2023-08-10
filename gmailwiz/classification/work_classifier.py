"""
Work Email Classifier.

Simple function to classify emails as work-related based on various indicators.
"""

import re
import pandas as pd
from typing import Optional


def is_work_email(
        df: pd.DataFrame, *,
        subject_col: str = 'subject',
        sender_email_col: str = 'sender_email',
        sender_name_col: str = 'sender_name',
        snippet_col: Optional[str] = 'snippet'
) -> pd.DataFrame:
    """
    Classify emails as work-related by adding an 'is_work' column (True/False/None).
    
    Conservative approach: Only classifies as True/False when confident.
    Returns None when unsure.
    
    Args:
        df: Input DataFrame with email data.
        subject_col: Name of the subject column.
        sender_email_col: Name of the sender email column.
        sender_name_col: Name of the sender name column.
        snippet_col: Name of the snippet column (optional).
        
    Returns:
        New DataFrame with 'is_work' column added (True/False/None).
    """
    if df.empty:
        return df.copy()
    
    # Create a copy to avoid modifying the original
    result_df = df.copy()
    
    # Initialize with None (unsure)
    result_df['is_work'] = None
    
    # Strong work indicators (high confidence)
    strong_work_indicators = []
    
    # Check for work domains (very strong indicator)
    if sender_email_col in df.columns:
        work_domain_patterns = [
            r'@(company|corp|inc|llc|ltd|business|enterprise)\.',
            r'@[a-z]+\.(edu|gov|mil)$',  # Educational/government domains
        ]
        
        for pattern in work_domain_patterns:
            strong_work_indicators.append(
                df[sender_email_col].str.contains(pattern, case=False, na=False)
            )
    
    # Check for professional titles (strong indicator)
    if sender_name_col in df.columns:
        professional_titles = [
            r'\b(ceo|cfo|cto|vp|director|manager|supervisor)\b',
            r'\b(engineer|developer|analyst|consultant|specialist)\b',
        ]
        
        for title in professional_titles:
            strong_work_indicators.append(
                df[sender_name_col].str.contains(title, case=False, na=False)
            )
        
        # Company name patterns
        company_patterns = [
            r'\b(inc|corp|llc|ltd|company|co)\b',
            r'[A-Z]{4,}',  # All caps words (likely company names)
        ]
        
        for pattern in company_patterns:
            strong_work_indicators.append(
                df[sender_name_col].str.contains(pattern, case=False, na=False)
            )
    
    # Strong work content indicators
    if subject_col in df.columns:
        work_content_patterns = [
            r'\b(meeting|conference|presentation|workshop)\b',
            r'\b(project|task|assignment|deliverable)\b',
            r'\b(client|customer|vendor|partner|stakeholder)\b',
            r'\b(agenda|minutes|action items|follow up)\b',
        ]
        
        for pattern in work_content_patterns:
            strong_work_indicators.append(
                df[subject_col].str.contains(pattern, case=False, na=False)
            )
    
    if snippet_col and snippet_col in df.columns:
        work_snippet_patterns = [
            r'\b(meeting|conference|presentation)\b',
            r'\b(project|task|assignment)\b',
            r'\b(client|customer|vendor|partner)\b',
            r'\b(agenda|minutes|action items)\b',
        ]
        
        for pattern in work_snippet_patterns:
            strong_work_indicators.append(
                df[snippet_col].str.contains(pattern, case=False, na=False)
            )
    
    # Strong non-work indicators (high confidence it's NOT work)
    strong_non_work_indicators = []
    
    # Personal domains
    if sender_email_col in df.columns:
        personal_domains = [
            r'@gmail\.com$', r'@yahoo\.com$', r'@hotmail\.com$', r'@outlook\.com$',
            r'@icloud\.com$', r'@me\.com$', r'@mac\.com$', r'@live\.com$'
        ]
        
        for domain_pattern in personal_domains:
            strong_non_work_indicators.append(
                df[sender_email_col].str.contains(domain_pattern, case=False, na=False)
            )
    
    # Personal content
    if subject_col in df.columns:
        personal_patterns = [
            r'\b(mom|dad|wife|husband|family|friend)\b',
            r'\b(birthday|anniversary|party|celebration)\b',
        ]
        
        for pattern in personal_patterns:
            strong_non_work_indicators.append(
                df[subject_col].str.contains(pattern, case=False, na=False)
            )
    
    # Apply classification logic
    for idx in df.index:
        work_score = sum(1 for indicator in strong_work_indicators if indicator.iloc[idx])
        non_work_score = sum(1 for indicator in strong_non_work_indicators if indicator.iloc[idx])
        
        # Only classify if we have strong indicators
        if work_score >= 2:
            result_df.loc[idx, 'is_work'] = True
        elif non_work_score >= 2:
            result_df.loc[idx, 'is_work'] = False
        # Otherwise remains None (unsure)
    
    return result_df
