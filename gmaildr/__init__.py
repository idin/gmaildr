"""
GmailDr - A powerful Gmail analysis, management, and automation wizard.

This package provides tools to connect to Gmail, analyze email data,
generate statistics about email senders and usage patterns, and automate
email management tasks.
"""

__version__ = "1.1.0"
__author__ = "idin"

from .core import Gmail, GmailClient, ConfigManager, setup_logging
from .analysis import (
    EmailAnalyzer,
    EmailContentAnalyzer,
    analyze_email_text,
    add_content_metrics_to_dataframe,
    calculate_automated_email_score,
    classify_email_types,
    analyze_email_dataframe
)
from .models import EmailMessage, SenderStatistics, AnalysisReport

__all__ = [
    "Gmail",
    "GmailClient",
    "ConfigManager",
    "setup_logging",
    "EmailAnalyzer",
    "EmailMessage",
    "SenderStatistics",
    "AnalysisReport",
    "EmailContentAnalyzer",
    "analyze_email_text",
    "add_content_metrics_to_dataframe",
    "calculate_automated_email_score",
    "classify_email_types",
    "analyze_email_dataframe",
]
