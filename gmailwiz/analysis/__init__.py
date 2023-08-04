"""
GmailWiz analysis functionality.

This module contains email analysis, metrics processing, and content analysis tools.
"""

from .email_analyzer import EmailAnalyzer
from .email_metrics import EmailContentAnalyzer, analyze_email_text
from .metrics_processor import (
    add_content_metrics_to_dataframe,
    calculate_automated_email_score,
    classify_email_types,
    analyze_email_dataframe
)

__all__ = [
    "EmailAnalyzer",
    "EmailContentAnalyzer",
    "analyze_email_text",
    "add_content_metrics_to_dataframe",
    "calculate_automated_email_score",
    "classify_email_types",
    "analyze_email_dataframe"
]
