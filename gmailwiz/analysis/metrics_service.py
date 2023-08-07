"""
Centralized metrics processing service.

This module provides a single point of entry for all email metrics processing,
eliminating code duplication across different parts of the application.
"""

import pandas as pd
from typing import Optional
from .metrics_processor import (
    add_content_metrics_to_dataframe_parallel,
    calculate_automated_email_score,
    classify_email_types
)


class MetricsService:
    """
    Centralized service for processing email metrics.
    
    This service handles all metrics processing in one place, ensuring
    consistency and eliminating code duplication.
    """
    
    @staticmethod
    def process_metrics(
        df: pd.DataFrame,
        *,
        include_metrics: bool = False,
        include_text: bool = False,
        show_progress: bool = True
    ) -> pd.DataFrame:
        """
        Process metrics for a DataFrame of emails.
        
        Args:
            df: DataFrame containing email data.
            include_metrics: Whether to include content analysis metrics.
            include_text: Whether text content is available.
            show_progress: Whether to show progress indicators.
            
        Returns:
            DataFrame with processed metrics.
        """
        if not include_metrics or not include_text:
            return df
        
        # Use fast vectorized operations instead of slow parallel processing
        df = MetricsService._add_metrics_vectorized(df=df, show_progress=show_progress)
        
        # Calculate automated email scores
        df = calculate_automated_email_score(df=df)
        
        # Classify email types
        df = classify_email_types(df=df)
        
        return df
    
    @staticmethod
    def _add_metrics_vectorized(df: pd.DataFrame, show_progress: bool = True) -> pd.DataFrame:
        """
        Add metrics using fast vectorized operations only.
        
        Args:
            df: DataFrame with email data.
            show_progress: Whether to show progress.
            
        Returns:
            DataFrame with metrics added.
        """
        if show_progress:
            print("🔍 Analyzing email content with fast functions...")
        
        df_copy = df.copy()
        
        # Get text and subject columns, fill NaN with empty strings
        text_series = df_copy['text_content'].fillna('') if 'text_content' in df_copy.columns else pd.Series([''] * len(df_copy))
        subject_series = df_copy['subject'].fillna('') if 'subject' in df_copy.columns else pd.Series([''] * len(df_copy))
        
        # Combine text and subject for analysis
        combined_text = subject_series + ' ' + text_series
        
        if show_progress:
            print("  📝 Extracting text patterns...")
        
        # Apply fast functions to each text
        df_copy['has_unsubscribe_link'] = combined_text.apply(MetricsService._has_unsubscribe_link)
        df_copy['has_marketing_language'] = combined_text.apply(MetricsService._has_marketing_language)
        df_copy['has_legal_disclaimer'] = combined_text.apply(MetricsService._has_legal_disclaimer)
        df_copy['has_bulk_email_indicators'] = combined_text.apply(MetricsService._has_bulk_email_indicators)
        df_copy['has_tracking_pixels'] = combined_text.apply(MetricsService._has_tracking_pixels)
        
        # Promotional content
        promo_counts = combined_text.apply(MetricsService._count_promotional_words)
        df_copy['has_promotional_content'] = promo_counts >= 2
        
        if show_progress:
            print("  🔢 Calculating counts and ratios...")
        
        # Counts using fast functions
        df_copy['exclamation_count'] = combined_text.apply(MetricsService._count_exclamations)
        df_copy['caps_word_count'] = combined_text.apply(MetricsService._count_caps_words)
        df_copy['external_link_count'] = combined_text.apply(MetricsService._count_external_links)
        df_copy['image_count'] = combined_text.apply(MetricsService._count_images)
        
        # Word count using space splitting (much faster than regex)
        word_counts = combined_text.str.split().str.len()
        
        # Calculate ratios
        df_copy['caps_ratio'] = df_copy['caps_word_count'] / word_counts.replace(0, 1)
        df_copy['promotional_word_ratio'] = promo_counts / word_counts.replace(0, 1)
        
        # HTML to text ratio using simple counting
        html_tags = combined_text.apply(MetricsService._count_html_tags)
        df_copy['html_to_text_ratio'] = html_tags / (word_counts + html_tags).replace(0, 1)
        
        # Link to text ratio
        df_copy['link_to_text_ratio'] = df_copy['external_link_count'] / word_counts.replace(0, 1)
        
        if show_progress:
            print("  ✅ Fast content analysis complete!")
        
        return df_copy
    
    @staticmethod
    def _has_unsubscribe_link(text: str) -> bool:
        """Fast check for unsubscribe links using sets and early breaking."""
        text_lower = text.lower()
        unsubscribe_terms = {'unsubscribe', 'opt out', 'remove from list', 'stop receiving'}
        return any(term in text_lower for term in unsubscribe_terms)
    
    @staticmethod
    def _has_marketing_language(text: str) -> bool:
        """Fast check for marketing language using sets and early breaking."""
        text_lower = text.lower()
        marketing_terms = {'special offer', 'limited time', 'act now', 'don\'t miss'}
        return any(term in text_lower for term in marketing_terms)
    
    @staticmethod
    def _has_legal_disclaimer(text: str) -> bool:
        """Fast check for legal disclaimers using sets and early breaking."""
        text_lower = text.lower()
        legal_terms = {'privacy policy', 'terms of service', 'legal notice', 'disclaimer'}
        return any(term in text_lower for term in legal_terms)
    
    @staticmethod
    def _has_bulk_email_indicators(text: str) -> bool:
        """Fast check for bulk email indicators using sets and early breaking."""
        text_lower = text.lower()
        bulk_terms = {'bulk', 'mass email', 'newsletter'}
        return any(term in text_lower for term in bulk_terms)
    
    @staticmethod
    def _has_tracking_pixels(text: str) -> bool:
        """Fast check for tracking pixels using sets and early breaking."""
        text_lower = text.lower()
        tracking_terms = {'utm_', 'tracking', 'pixel'}
        return any(term in text_lower for term in tracking_terms)
    
    @staticmethod
    def _count_promotional_words(text: str) -> int:
        """Fast count of promotional words."""
        text_lower = text.lower()
        promo_words = {'offer', 'sale', 'discount', 'free', 'limited', 'special', 'deal', 'save'}
        return sum(1 for word in promo_words if word in text_lower)
    
    @staticmethod
    def _count_exclamations(text: str) -> int:
        """Fast count of exclamation marks."""
        return text.count('!')
    
    @staticmethod
    def _count_caps_words(text: str) -> int:
        """Fast count of common caps words."""
        return text.count('HTTP') + text.count('HTTPS') + text.count('WWW')
    
    @staticmethod
    def _count_external_links(text: str) -> int:
        """Fast count of external links."""
        return text.count('http://') + text.count('https://')
    
    @staticmethod
    def _count_images(text: str) -> int:
        """Fast count of images."""
        return text.count('<img') + text.count('.jpg') + text.count('.png')
    
    @staticmethod
    def _count_html_tags(text: str) -> int:
        """Fast count of HTML tags."""
        return text.count('<')
