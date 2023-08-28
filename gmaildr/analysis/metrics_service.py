"""
Metrics processing for GmailDr.

This module provides functions for processing email metrics.
"""

import logging
from typing import Optional

import pandas as pd

from .analyze_email_content import analyze_email_content

logger = logging.getLogger(__name__)


def process_metrics(
    df: pd.DataFrame,
    include_metrics: bool = True,
    include_text: bool = True,
    show_progress: bool = True
) -> pd.DataFrame:
    """
    Process metrics for email DataFrame.
    
    Args:
        df: Email DataFrame to process
        include_metrics: Whether to include metrics processing
        include_text: Whether text content is available
        show_progress: Whether to show progress
        
    Returns:
        DataFrame with metrics added
    """
    if not include_metrics or not include_text:
        return df
    
    if df.empty:
        return df
    
    # Check if text_content column exists
    if 'text_content' not in df.columns:
        return df
    
    # Create a copy to avoid modifying the original
    result_df = df.copy()
    
    # Process metrics for each email
    metrics_list = []
    
    if show_progress:
        logger.info(f"Processing metrics for {len(df)} emails...")
    
    for idx, row in df.iterrows():
        text_content = row.get('text_content')
        subject = row.get('subject', '')
        
        # Analyze email content
        metrics = analyze_email_content(
            text_content=text_content,
            subject=subject
        )
        
        metrics_list.append(metrics)
    
    # Convert metrics to DataFrame
    metrics_df = pd.DataFrame(metrics_list)
    
    # Add metrics columns to result DataFrame
    for col in metrics_df.columns:
        result_df[col] = metrics_df[col]
    
    if show_progress:
        logger.info(f"Added {len(metrics_df.columns)} metric columns")
    
    return result_df
