"""
Analysis module for GmailDr.

This module provides comprehensive email analysis capabilities including:
- Human email detection
- Content analysis
- Language detection
- Metrics processing
"""

from .analyze_email_content import analyze_email_content
from .language_detector import detect_language_safe, is_english, get_language_name
from .metrics_service import process_metrics

__all__ = [
    'analyze_email_content',
    'detect_language_safe',
    'is_english',
    'get_language_name',
    'process_metrics'
]
