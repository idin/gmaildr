"""
Email Analyzer for GmailDr.

This module provides analysis functionality for email data.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Literal
import pandas as pd

from .email_processing import EmailProcessing


class EmailAnalyzer(EmailProcessing):
    """
    Analyzer class for email data analysis.
    
    This class provides methods for analyzing email patterns, sender statistics,
    and other email-related metrics.
    """
    
    def __init__(
        self, *, 
        credentials_file: str, 
        token_file: str,
        enable_cache: bool, 
        verbose: bool
    ):
        """
        Initialize the EmailAnalyzer.
        
        Args:
            credentials_file (str): Path to Google OAuth2 credentials file.
            enable_cache (bool): Whether to enable email caching.
            verbose (bool): Whether to show detailed cache and processing messages.
        """
        super().__init__(credentials_file=credentials_file, token_file=token_file, enable_cache=enable_cache, verbose=verbose)
    
    def analyze(
        self, *,
        days: int = 30, 
        max_emails: Optional[int] = None
    ):
        """
        Run comprehensive email analysis.
        
        Args:
            days: Number of days to analyze
            max_emails: Maximum number of emails to analyze
            
        Returns:
            Complete analysis report
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get emails for analysis
        emails_df = self.get_emails(
            days=days,
            max_emails=max_emails,
            include_text=False,
            include_metrics=False
        )
        
        # For now, return basic analysis
        return {
            'total_emails': len(emails_df),
            'date_range': {
                'start': start_date,
                'end': end_date
            },
            'emails_df': emails_df
        }
    
    def top_senders(
        self, *, 
        limit: int = 10, 
        days: int = 30, 
        by: Optional[List[str] | str] = None
    ) -> List[Dict[str, Any]]:
        """
        Top email senders over the last `days`, using the harmonic mean of
        per-metric percentile ranks (email_count, total_size_bytes, attachment_count).

        Args:
            limit: Number of top senders to return
            days: Number of days to analyze
            by: List of metrics to use for ranking.
                available metrics: 'email_count', 'total_size_bytes', 'attachment_count'
            
        Returns:
            List of top senders
        """
        all_metrics = ['email_count', 'total_size_bytes', 'attachment_count']

        if isinstance(by, str):
            by = [by]
        
        if by is None:
            by = all_metrics
        else:
            for m in by:
                if m not in all_metrics:
                    raise ValueError(f"Invalid metric: {m}")
        
        if len(by) == 0:
            raise ValueError("No metrics to rank by")

        emails_df = self.get_emails(days=days, include_text=False, include_metrics=False)
        if emails_df.empty:
            return []

        # Drop rows without a sender and normalise dtypes
        emails_df = emails_df.dropna(subset=['sender_email']).copy()
        emails_df['size_bytes'] = pd.to_numeric(emails_df.get('size_bytes', 0), errors='coerce').fillna(0).astype('int64')
        # Treat missing has_attachments as False; bool sum counts Trues
        emails_df['has_attachments'] = emails_df.get('has_attachments', False).fillna(False).astype(bool)

        # Aggregate per sender
        grouped = emails_df.groupby('sender_email', as_index=False).agg(
            email_count=('message_id', 'count'),
            total_size_bytes=('size_bytes', 'sum'),
            attachment_count=('has_attachments', 'sum'),
        )

        # Percentiles, higher value -> higher percentile
        pct_cols = []
        for m in by:
            c = f'{m}_percentile'
            grouped[c] = grouped[m].rank(pct=True)  # ascending=True by default
            pct_cols.append(c)

        # Harmonic mean of percentiles
        eps = 1e-12
        denom = (1.0 / grouped[pct_cols].clip(lower=eps)).sum(axis=1)
        grouped['hm_pct'] = len(by) / denom

        # Tie-breaker: maximise the worst percentile
        grouped['min_pct'] = grouped[pct_cols].min(axis=1)

        # Final ordering (best first)
        df_final = grouped.sort_values(['hm_pct', 'min_pct'], ascending=[False, False])

        # Prepare output
        out = df_final.head(limit).copy()
        out['total_size_mb'] = out['total_size_bytes'] / (1024 * 1024)

        # Return core stats plus scores for transparency
        cols = ['sender_email', 'email_count', 'total_size_mb', 'attachment_count']
        return out[cols].to_dict(orient='records')
    
    def storage_analysis(self, days: int = 30) -> Dict[str, Any]:
        """
        Get storage usage analysis.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Storage analysis results
        """
        emails_df = self.get_emails(
            days=days,
            include_text=False,
            include_metrics=False
        )
        
        if emails_df.empty:
            return {
                'total_emails': 0,
                'total_size_mb': 0,
                'average_size_mb': 0
            }
        
        total_size_bytes = emails_df['size_bytes'].sum()
        total_size_mb = total_size_bytes / (1024 * 1024)
        average_size_mb = total_size_mb / len(emails_df)
        
        return {
            'total_emails': len(emails_df),
            'total_size_mb': round(total_size_mb, 2),
            'average_size_mb': round(average_size_mb, 2)
        }
    
    def temporal_analysis(self, days: int = 30) -> Dict[str, Any]:
        """
        Get temporal email patterns.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Temporal analysis results
        """
        emails_df = self.get_emails(
            days=days,
            include_text=False,
            include_metrics=False
        )
        
        if emails_df.empty:
            return {
                'total_emails': 0,
                'emails_per_day': 0,
                'busiest_day': None,
                'quietest_day': None
            }
        
        # Convert timestamp to datetime if needed
        if 'timestamp' in emails_df.columns:
            emails_df['date'] = pd.to_datetime(emails_df['timestamp']).dt.date
        
        # Count emails per day
        daily_counts = emails_df.groupby('date').size().reset_index(name='count')
        daily_counts = daily_counts.sort_values('count', ascending=False)
        
        return {
            'total_emails': len(emails_df),
            'emails_per_day': round(len(emails_df) / days, 2),
            'busiest_day': {
                'date': str(daily_counts.iloc[0]['date']),
                'count': int(daily_counts.iloc[0]['count'])
            } if not daily_counts.empty else None,
            'quietest_day': {
                'date': str(daily_counts.iloc[-1]['date']),
                'count': int(daily_counts.iloc[-1]['count'])
            } if not daily_counts.empty else None
        }
