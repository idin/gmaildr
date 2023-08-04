"""
Analysis module for GmailWiz.

This module contains email analysis and metrics functionality.
"""

from .email_analyzer import EmailAnalyzer
from .email_metrics import EmailMetrics, EmailContentAnalyzer, analyze_email_text
from .metrics_processor import (
    add_content_metrics_to_dataframe,
    add_content_metrics_to_dataframe_parallel,
    calculate_automated_email_score,
    classify_email_types,
    analyze_email_dataframe
)
from .human_email_detector import (
    HumanEmailDetector,
    HumanEmailScore,
    detect_human_emails,
    get_human_sender_summary
)

__all__ = [
    'EmailAnalyzer', 
    'EmailMetrics', 
    'EmailContentAnalyzer',
    'analyze_email_text',
    'add_content_metrics_to_dataframe',
    'add_content_metrics_to_dataframe_parallel',
    'calculate_automated_email_score',
    'classify_email_types',
    'analyze_email_dataframe',
    'HumanEmailDetector',
    'HumanEmailScore',
    'detect_human_emails',
    'get_human_sender_summary'
]
