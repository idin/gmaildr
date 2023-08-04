"""
Email analysis module for sender statistics and insights.

This module provides comprehensive analysis capabilities for Gmail data,
including sender statistics, storage analysis, and trend identification.
"""

import logging
from collections import defaultdict
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Generator
import pandas as pd
import numpy as np

from ..models import EmailMessage, SenderStatistics, AnalysisReport
from ..core.gmail_client import GmailClient

logger = logging.getLogger(__name__)


class EmailAnalyzer:
    """
    Comprehensive email analysis engine.
    
    This class provides methods to analyze email data and generate
    detailed statistics about senders, storage usage, and email patterns.
    """
    
    def __init__(self, gmail_client: GmailClient):
        """
        Initialize the email analyzer.
        
        Args:
            gmail_client (GmailClient): Authenticated Gmail client instance.
        """
        self.gmail_client = gmail_client
        self.emails_cache: List[EmailMessage] = []
        
    def analyze_emails_from_date_range(
        self, *,
        start_date: datetime,
        end_date: Optional[datetime] = None,
        max_emails: Optional[int] = None,
        batch_size: int = 100
    ) -> AnalysisReport:
        """
        Analyze emails from a specific date range.
        
        Args:
            start_date (datetime): Start date for analysis.
            end_date (Optional[datetime]): End date for analysis. Defaults to now.
            max_emails (Optional[int]): Maximum number of emails to analyze.
            batch_size (int): Number of emails to process in each batch.
            
        Returns:
            AnalysisReport: Comprehensive analysis report.
        """
        if end_date is None:
            end_date = datetime.now()
            
        logger.info(f"Starting email analysis from {start_date} to {end_date}")
        
        # Get message IDs
        message_ids = self.gmail_client.get_emails_from_date_range(
            start_date=start_date,
            end_date=end_date,
            max_results=max_emails
        )
        
        if not message_ids:
            logger.warning("No emails found in the specified date range")
            return self._create_empty_report(start_date, end_date)
        
        logger.info(f"Found {len(message_ids)} emails to analyze")
        
        # Process emails in batches
        all_emails = []
        total_processed = 0
        
        for batch_emails in self.gmail_client.get_messages_batch(message_ids, batch_size):
            all_emails.extend(batch_emails)
            total_processed += len(batch_emails)
            logger.info(f"Processed {total_processed}/{len(message_ids)} emails")
        
        # Cache the emails for potential future analysis
        self.emails_cache = all_emails
        
        # Generate analysis report
        return self._generate_analysis_report(all_emails, start_date, end_date)
    
    def analyze_cached_emails(self) -> Optional[AnalysisReport]:
        """
        Analyze previously cached emails.
        
        Returns:
            Optional[AnalysisReport]: Analysis report or None if no cached emails.
        """
        if not self.emails_cache:
            logger.warning("No cached emails available for analysis")
            return None
        
        logger.info(f"Analyzing {len(self.emails_cache)} cached emails")
        
        # Determine date range from cached emails
        dates = [email.date_received for email in self.emails_cache]
        start_date = min(dates)
        end_date = max(dates)
        
        return self._generate_analysis_report(self.emails_cache, start_date, end_date)
    
    def get_sender_statistics(
        self,
        emails: Optional[List[EmailMessage]] = None
    ) -> List[SenderStatistics]:
        """
        Generate detailed statistics for each email sender.
        
        Args:
            emails (Optional[List[EmailMessage]]): List of emails to analyze.
                                                  Uses cached emails if None.
            
        Returns:
            List[SenderStatistics]: List of sender statistics.
        """
        if emails is None:
            emails = self.emails_cache
        
        if not emails:
            logger.warning("No emails provided for sender analysis")
            return []
        
        # Group emails by sender
        sender_groups = defaultdict(list)
        for email in emails:
            sender_groups[email.sender_email].append(email)
        
        sender_stats = []
        
        for sender_email, sender_emails in sender_groups.items():
            # Calculate basic statistics
            total_emails = len(sender_emails)
            total_size = sum(email.size_bytes for email in sender_emails)
            average_size = total_size / total_emails if total_emails > 0 else 0
            
            # Get sender name (use the most recent non-None name)
            sender_name = None
            for email in reversed(sender_emails):
                if email.sender_name:
                    sender_name = email.sender_name
                    break
            
            # Count read/unread/important emails
            read_count = sum(1 for email in sender_emails if email.is_read)
            unread_count = total_emails - read_count
            important_count = sum(1 for email in sender_emails if email.is_important)
            
            # Calculate label distribution
            labels_distribution = defaultdict(int)
            for email in sender_emails:
                for label in email.labels:
                    labels_distribution[label] += 1
            
            # Get date range
            dates = [email.date_received for email in sender_emails]
            first_email_date = min(dates)
            last_email_date = max(dates)
            
            # Create sender statistics object
            stats = SenderStatistics(
                sender_email=sender_email,
                sender_name=sender_name,
                total_emails=total_emails,
                total_size_bytes=total_size,
                first_email_date=first_email_date,
                last_email_date=last_email_date,
                average_size_bytes=average_size,
                read_count=read_count,
                unread_count=unread_count,
                important_count=important_count,
                labels_distribution=dict(labels_distribution)
            )
            
            sender_stats.append(stats)
        
        logger.info(f"Generated statistics for {len(sender_stats)} senders")
        return sender_stats
    
    def get_storage_analysis(
        self,
        emails: Optional[List[EmailMessage]] = None
    ) -> Dict[str, any]:
        """
        Analyze storage usage patterns.
        
        Args:
            emails (Optional[List[EmailMessage]]): List of emails to analyze.
                                                  Uses cached emails if None.
            
        Returns:
            Dict[str, any]: Storage analysis results.
        """
        if emails is None:
            emails = self.emails_cache
        
        if not emails:
            return {}
        
        total_size = sum(email.size_bytes for email in emails)
        total_emails = len(emails)
        average_size = total_size / total_emails if total_emails > 0 else 0
        
        # Size distribution analysis
        sizes = [email.size_bytes for email in emails]
        if sizes:
            size_percentiles = np.percentile(sizes, [25, 50, 75, 90, 95, 99])
        else:
            size_percentiles = [0, 0, 0, 0, 0, 0]
        
        # Find largest emails
        largest_emails = sorted(emails, key=lambda e: e.size_bytes, reverse=True)[:10]
        
        # Analyze size by sender
        sender_sizes = defaultdict(int)
        for email in emails:
            sender_sizes[email.sender_email] += email.size_bytes
        
        top_storage_senders = sorted(
            sender_sizes.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        return {
            'total_size_bytes': total_size,
            'total_size_mb': total_size / (1024 * 1024),
            'total_size_gb': total_size / (1024 * 1024 * 1024),
            'total_emails': total_emails,
            'average_size_bytes': average_size,
            'average_size_kb': average_size / 1024,
            'size_percentiles': {
                '25th': size_percentiles[0],
                '50th': size_percentiles[1],
                '75th': size_percentiles[2],
                '90th': size_percentiles[3],
                '95th': size_percentiles[4],
                '99th': size_percentiles[5],
            },
            'largest_emails': [
                {
                    'sender': email.sender_email,
                    'subject': email.subject,
                    'size_bytes': email.size_bytes,
                    'size_mb': email.size_bytes / (1024 * 1024),
                    'date': email.date_received.isoformat()
                }
                for email in largest_emails
            ],
            'top_storage_senders': [
                {
                    'sender': sender,
                    'total_size_bytes': size,
                    'total_size_mb': size / (1024 * 1024)
                }
                for sender, size in top_storage_senders
            ]
        }
    
    def get_temporal_analysis(
        self,
        emails: Optional[List[EmailMessage]] = None
    ) -> Dict[str, any]:
        """
        Analyze email patterns over time.
        
        Args:
            emails (Optional[List[EmailMessage]]): List of emails to analyze.
                                                  Uses cached emails if None.
            
        Returns:
            Dict[str, any]: Temporal analysis results.
        """
        if emails is None:
            emails = self.emails_cache
        
        if not emails:
            return {}
        
        # Convert to pandas DataFrame for easier analysis
        df = pd.DataFrame([
            {
                'date': email.date_received,
                'sender': email.sender_email,
                'size_bytes': email.size_bytes,
                'is_read': email.is_read,
                'is_important': email.is_important
            }
            for email in emails
        ])
        
        # Daily email counts
        df['date_only'] = df['date'].dt.date
        daily_counts = df.groupby('date_only').size()
        
        # Weekly email counts
        df['week'] = df['date'].dt.to_period('W')
        weekly_counts = df.groupby('week').size()
        
        # Monthly email counts
        df['month'] = df['date'].dt.to_period('M')
        monthly_counts = df.groupby('month').size()
        
        # Hourly patterns
        df['hour'] = df['date'].dt.hour
        hourly_patterns = df.groupby('hour').size()
        
        # Day of week patterns
        df['day_of_week'] = df['date'].dt.day_name()
        day_patterns = df.groupby('day_of_week').size()
        
        return {
            'daily_email_counts': daily_counts.to_dict(),
            'weekly_email_counts': {str(k): v for k, v in weekly_counts.to_dict().items()},
            'monthly_email_counts': {str(k): v for k, v in monthly_counts.to_dict().items()},
            'hourly_patterns': hourly_patterns.to_dict(),
            'day_of_week_patterns': day_patterns.to_dict(),
            'busiest_day': daily_counts.idxmax() if not daily_counts.empty else None,
            'busiest_hour': hourly_patterns.idxmax() if not hourly_patterns.empty else None,
            'busiest_day_of_week': day_patterns.idxmax() if not day_patterns.empty else None,
        }
    
    def export_to_dataframe(
        self,
        emails: Optional[List[EmailMessage]] = None
    ) -> pd.DataFrame:
        """
        Export email data to a pandas DataFrame for custom analysis.
        
        Args:
            emails (Optional[List[EmailMessage]]): List of emails to export.
                                                  Uses cached emails if None.
            
        Returns:
            pd.DataFrame: DataFrame containing email data.
        """
        if emails is None:
            emails = self.emails_cache
        
        if not emails:
            return pd.DataFrame()
        
        data = []
        for email in emails:
            data.append({
                'message_id': email.message_id,
                'sender_email': email.sender_email,
                'sender_name': email.sender_name,
                'subject': email.subject,
                'date_received': email.date_received,
                'size_bytes': email.size_bytes,
                'size_kb': email.size_bytes / 1024,
                'size_mb': email.size_bytes / (1024 * 1024),
                'labels': ','.join(email.labels),
                'thread_id': email.thread_id,
                'snippet': email.snippet,
                'has_attachments': email.has_attachments,
                'is_read': email.is_read,
                'is_important': email.is_important,
                'year': email.date_received.year,
                'month': email.date_received.month,
                'day': email.date_received.day,
                'hour': email.date_received.hour,
                'day_of_week': email.date_received.strftime('%A'),
            })
        
        return pd.DataFrame(data)
    
    def _generate_analysis_report(
        self, *,
        emails: List[EmailMessage],
        start_date: datetime,
        end_date: datetime
    ) -> AnalysisReport:
        """
        Generate a comprehensive analysis report.
        
        Args:
            emails (List[EmailMessage]): List of emails to analyze.
            start_date (datetime): Analysis start date.
            end_date (datetime): Analysis end date.
            
        Returns:
            AnalysisReport: Complete analysis report.
        """
        logger.info(f"Generating analysis report for {len(emails)} emails")
        
        # Generate sender statistics
        sender_statistics = self.get_sender_statistics(emails)
        
        # Create the analysis report
        report = AnalysisReport(
            total_emails_analyzed=len(emails),
            analysis_date=datetime.now(),
            date_range_start=start_date,
            date_range_end=end_date,
            sender_statistics=sender_statistics
        )
        
        logger.info(f"Analysis report generated with {len(sender_statistics)} senders")
        return report
    
    def _create_empty_report(
        self, *,
        start_date: datetime,
        end_date: datetime
    ) -> AnalysisReport:
        """
        Create an empty analysis report for when no emails are found.
        
        Args:
            start_date (datetime): Analysis start date.
            end_date (datetime): Analysis end date.
            
        Returns:
            AnalysisReport: Empty analysis report.
        """
        return AnalysisReport(
            total_emails_analyzed=0,
            analysis_date=datetime.now(),
            date_range_start=start_date,
            date_range_end=end_date,
            sender_statistics=[]
        )
