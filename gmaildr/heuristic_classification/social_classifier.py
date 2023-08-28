"""
Social Email Classifier.

Simple function to classify emails as social media related based on various indicators.
"""

import re
from typing import Optional

import pandas as pd


def is_social_email(
        df: pd.DataFrame, *,
        subject_col: str = 'subject',
        sender_email_col: str = 'sender_email',
        sender_name_col: str = 'sender_name',
        snippet_col: Optional[str] = 'snippet'
) -> pd.DataFrame:
    """
    Classify emails as social media related by adding an 'is_social' boolean column.
    
    Args:
        df: Input DataFrame with email data.
        subject_col: Name of the subject column.
        sender_email_col: Name of the sender email column.
        sender_name_col: Name of the sender name column.
        snippet_col: Name of the snippet column (optional).
        
    Returns:
        New DataFrame with 'is_social' column added.
    """
    if df.empty:
        return df.copy()
    
    # Create a copy to avoid modifying the original
    result_df = df.copy()
    
    # Social email indicators
    social_indicators = []
    
    # Check sender email patterns (social media domains)
    if sender_email_col in df.columns:
        social_domain_patterns = [
            r'@(facebook|twitter|instagram|linkedin|youtube|tiktok|snapchat)\.',
            r'@(reddit|pinterest|tumblr|discord|slack|telegram|whatsapp)\.',
            r'@(github|stackoverflow|medium|quora|producthunt)\.',
        ]
        
        for pattern in social_domain_patterns:
            social_indicators.append(
                df[sender_email_col].str.contains(pattern, case=False, na=False)
            )
    
    # Check sender name patterns
    if sender_name_col in df.columns:
        social_name_patterns = [
            r'\b(facebook|twitter|instagram|linkedin|youtube|tiktok)\b',
            r'\b(reddit|pinterest|tumblr|discord|slack|telegram)\b',
            r'\b(notifications|alerts|updates|team)\b',
        ]
        
        for pattern in social_name_patterns:
            social_indicators.append(
                df[sender_name_col].str.contains(pattern, case=False, na=False)
            )
    
    # Check subject patterns (social media keywords)
    if subject_col in df.columns:
        social_subject_patterns = [
            # Social media notifications
            r'\b(new follower|new connection|friend request|message request)\b',
            r'\b(like|comment|share|retweet|repost|mention)\b',
            r'\b(notification|alert|update|activity)\b',
            
            # Social interactions
            r'\b(profile|post|story|reel|video|photo|image)\b',
            r'\b(conversation|chat|message|dm|direct message)\b',
            r'\b(group|community|forum|discussion)\b',
            
            # Social events
            r'\b(event|meetup|hangout|party|celebration)\b',
            r'\b(live|stream|broadcast|webinar)\b',
            
            # Social features
            r'\b(trending|viral|popular|featured|highlighted)\b',
            r'\b(recommendation|suggestion|discovery)\b',
        ]
        
        for pattern in social_subject_patterns:
            social_indicators.append(
                df[subject_col].str.contains(pattern, case=False, na=False)
            )
    
    # Check snippet/content patterns
    if snippet_col and snippet_col in df.columns:
        social_content_patterns = [
            r'\b(new follower|new connection|friend request)\b',
            r'\b(like|comment|share|retweet|mention)\b',
            r'\b(notification|alert|update|activity)\b',
            r'\b(profile|post|story|reel|video)\b',
            r'\b(conversation|chat|message|dm)\b',
            r'\b(event|meetup|live|stream)\b',
        ]
        
        for pattern in social_content_patterns:
            social_indicators.append(
                df[snippet_col].str.contains(pattern, case=False, na=False)
            )
    
    # Combine all indicators
    if social_indicators:
        # Email is social if it matches multiple indicators
        combined_score = sum(social_indicators)
        result_df['is_social'] = combined_score >= 2
    else:
        result_df['is_social'] = False
    
    return result_df
