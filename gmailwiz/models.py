"""
Data models for Gmail Cleaner package.

This module contains dataclasses and models used throughout the package
for representing emails, statistics, and analysis results.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional, Any
import json


@dataclass
class EmailMessage:
    """
    Represents a single email message with relevant metadata.
    
    This class encapsulates all the important information about an email
    that we need for analysis purposes.
    """
    
    message_id: str
    sender_email: str
    sender_name: Optional[str]
    subject: str
    date_received: datetime
    size_bytes: int
    labels: List[str] = field(default_factory=list)
    thread_id: Optional[str] = None
    snippet: Optional[str] = None
    has_attachments: bool = False
    is_read: bool = False
    is_important: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the email message to a dictionary representation.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the email message.
        """
        return {
            "message_id": self.message_id,
            "sender_email": self.sender_email,
            "sender_name": self.sender_name,
            "subject": self.subject,
            "date_received": self.date_received.isoformat(),
            "size_bytes": self.size_bytes,
            "labels": self.labels,
            "thread_id": self.thread_id,
            "snippet": self.snippet,
            "has_attachments": self.has_attachments,
            "is_read": self.is_read,
            "is_important": self.is_important,
        }


@dataclass
class SenderStatistics:
    """
    Statistics for a specific email sender.
    
    Contains aggregated information about emails received from a particular sender.
    """
    
    sender_email: str
    sender_name: Optional[str]
    total_emails: int
    total_size_bytes: int
    first_email_date: datetime
    last_email_date: datetime
    average_size_bytes: float
    read_count: int
    unread_count: int
    important_count: int
    labels_distribution: Dict[str, int] = field(default_factory=dict)
    
    @property
    def read_percentage(self) -> float:
        """Calculate the percentage of read emails from this sender."""
        if self.total_emails == 0:
            return 0.0
        return (self.read_count / self.total_emails) * 100
    
    @property
    def important_percentage(self) -> float:
        """Calculate the percentage of important emails from this sender."""
        if self.total_emails == 0:
            return 0.0
        return (self.important_count / self.total_emails) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the sender statistics to a dictionary representation.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the sender statistics.
        """
        return {
            "sender_email": self.sender_email,
            "sender_name": self.sender_name,
            "total_emails": self.total_emails,
            "total_size_bytes": self.total_size_bytes,
            "first_email_date": self.first_email_date.isoformat(),
            "last_email_date": self.last_email_date.isoformat(),
            "average_size_bytes": self.average_size_bytes,
            "read_count": self.read_count,
            "unread_count": self.unread_count,
            "important_count": self.important_count,
            "read_percentage": self.read_percentage,
            "important_percentage": self.important_percentage,
            "labels_distribution": self.labels_distribution,
        }


@dataclass
class AnalysisReport:
    """
    Complete analysis report containing all statistics and insights.
    
    This class aggregates all analysis results and provides methods
    for exporting and displaying the findings.
    """
    
    total_emails_analyzed: int
    analysis_date: datetime
    date_range_start: datetime
    date_range_end: datetime
    sender_statistics: List[SenderStatistics]
    top_senders_by_count: List[SenderStatistics] = field(default_factory=list)
    top_senders_by_size: List[SenderStatistics] = field(default_factory=list)
    total_storage_used_bytes: int = 0
    
    def __post_init__(self):
        """Post-initialization to calculate derived statistics."""
        self._calculate_derived_statistics()
    
    def _calculate_derived_statistics(self):
        """Calculate derived statistics from sender data."""
        # Sort senders by email count
        self.top_senders_by_count = sorted(
            self.sender_statistics,
            key=lambda sender: sender.total_emails,
            reverse=True
        )
        
        # Sort senders by total size
        self.top_senders_by_size = sorted(
            self.sender_statistics,
            key=lambda sender: sender.total_size_bytes,
            reverse=True
        )
        
        # Calculate total storage used
        self.total_storage_used_bytes = sum(
            sender.total_size_bytes for sender in self.sender_statistics
        )
    
    def get_top_senders_by_count(self, limit: int = 10) -> List[SenderStatistics]:
        """
        Get the top senders by email count.
        
        Args:
            limit (int): Maximum number of senders to return.
            
        Returns:
            List[SenderStatistics]: List of top senders by email count.
        """
        return self.top_senders_by_count[:limit]
    
    def get_top_senders_by_size(self, limit: int = 10) -> List[SenderStatistics]:
        """
        Get the top senders by total email size.
        
        Args:
            limit (int): Maximum number of senders to return.
            
        Returns:
            List[SenderStatistics]: List of top senders by total size.
        """
        return self.top_senders_by_size[:limit]
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the analysis report to a dictionary representation.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the analysis report.
        """
        return {
            "total_emails_analyzed": self.total_emails_analyzed,
            "analysis_date": self.analysis_date.isoformat(),
            "date_range_start": self.date_range_start.isoformat(),
            "date_range_end": self.date_range_end.isoformat(),
            "total_storage_used_bytes": self.total_storage_used_bytes,
            "sender_statistics": [sender.to_dict() for sender in self.sender_statistics],
            "top_senders_by_count": [sender.to_dict() for sender in self.top_senders_by_count],
            "top_senders_by_size": [sender.to_dict() for sender in self.top_senders_by_size],
        }
    
    def save_to_json(self, file_path: str) -> None:
        """
        Save the analysis report to a JSON file.
        
        Args:
            file_path (str): Path where to save the JSON file.
        """
        with open(file_path, 'w', encoding='utf-8') as file_handle:
            json.dump(self.to_dict(), file_handle, indent=2, ensure_ascii=False)
