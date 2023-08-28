"""
Newsletter Email Classifier.

Simple function to classify emails as newsletters based on various indicators.
"""

import re
from typing import Optional

import pandas as pd


def is_newsletter_email(
        df: pd.DataFrame, *,
        subject_col: str = 'subject',
        sender_email_col: str = 'sender_email',
        sender_name_col: str = 'sender_name',
        snippet_col: Optional[str] = 'snippet'
) -> pd.DataFrame:
    """
    Classify emails as newsletters by adding an 'is_newsletter' boolean column.
    
    Args:
        df: Input DataFrame with email data.
        subject_col: Name of the subject column.
        sender_email_col: Name of the sender email column.
        sender_name_col: Name of the sender name column.
        snippet_col: Name of the snippet column (optional).
        
    Returns:
        New DataFrame with 'is_newsletter' column added.
    """
    if df.empty:
        return df.copy()
    
    # Create a copy to avoid modifying the original
    result_df = df.copy()
    
    # Newsletter email indicators
    newsletter_indicators = []
    
    # Check sender email patterns
    if sender_email_col in df.columns:
        newsletter_domain_patterns = [
            r'@(newsletter|news|updates|digest|weekly|monthly)\.',
            r'@[a-z]+\.(com|org|net)$',  # Generic newsletter domains
        ]
        
        for pattern in newsletter_domain_patterns:
            newsletter_indicators.append(
                df[sender_email_col].str.contains(pattern, case=False, na=False)
            )
    
    # Check sender name patterns
    if sender_name_col in df.columns:
        newsletter_name_patterns = [
            r'\b(newsletter|news|updates|digest|weekly|monthly)\b',
            r'\b(team|department|group|staff)\b',
            r'\b(no-reply|noreply|donotreply|donot-reply)\b',
        ]
        
        for pattern in newsletter_name_patterns:
            newsletter_indicators.append(
                df[sender_name_col].str.contains(pattern, case=False, na=False)
            )
    
    # Check subject patterns (newsletter keywords)
    if subject_col in df.columns:
        newsletter_subject_patterns = [
            # Newsletter indicators
            r'\b(newsletter|news|updates|digest|weekly|monthly)\b',
            r'\b(this week|this month|latest|recent|new)\b',
            r'\b(roundup|summary|highlights|top stories)\b',
            
            # Date patterns
            r'\b(week of|month of|january|february|march|april|may|june)\b',
            r'\b(july|august|september|october|november|december)\b',
            r'\b(\d{1,2}/\d{1,2}|\d{1,2}-\d{1,2})\b',  # Date formats
            
            # Issue numbers
            r'\b(issue|edition|volume|number)\b',
            r'\b(#\d+|\d+th|\d+st|\d+nd|\d+rd)\b',
            
            # Content indicators
            r'\b(articles|stories|posts|content|features)\b',
            r'\b(read|learn|discover|explore|find out)\b',
        ]
        
        for pattern in newsletter_subject_patterns:
            newsletter_indicators.append(
                df[subject_col].str.contains(pattern, case=False, na=False)
            )
    
    # Check snippet/content patterns
    if snippet_col and snippet_col in df.columns:
        newsletter_content_patterns = [
            r'\b(newsletter|news|updates|digest)\b',
            r'\b(this week|this month|latest|recent)\b',
            r'\b(roundup|summary|highlights)\b',
            r'\b(articles|stories|posts|content)\b',
            r'\b(read|learn|discover|explore)\b',
        ]
        
        for pattern in newsletter_content_patterns:
            newsletter_indicators.append(
                df[snippet_col].str.contains(pattern, case=False, na=False)
            )
    
    # Combine all indicators
    if newsletter_indicators:
        # Email is newsletter if it matches multiple indicators
        combined_score = sum(newsletter_indicators)
        result_df['is_newsletter'] = combined_score >= 2
    else:
        result_df['is_newsletter'] = False
    
    return result_df
