"""
Utilities module for GmailWiz.

This module contains utility functions and helper classes.
"""

from .progress import EmailProgressTracker
from .email_lists import EmailListManager
from .query_builder import build_gmail_search_query
from .paths import (
    get_package_root, get_core_dir, get_analysis_dir, get_utils_dir, 
    get_cache_dir, get_project_root, get_tests_dir, verify_package_structure
)

__all__ = [
    'EmailProgressTracker', 'EmailListManager', 'build_gmail_search_query',
    'get_package_root', 'get_core_dir', 'get_analysis_dir', 'get_utils_dir',
    'get_cache_dir', 'get_project_root', 'get_tests_dir', 'verify_package_structure'
]
