"""
Utility functions for the gmaildr package.
"""

from .progress import EmailProgressTracker
from .email_lists import EmailListManager
from .query_builder import build_gmail_search_query
from .paths import (
    get_package_root, get_core_dir, get_analysis_dir, get_utils_dir, 
    get_caching_dir, get_project_root, get_tests_dir, verify_package_structure
)
from .pattern_matching import count_patterns, match_patterns

__all__ = [
    'EmailProgressTracker', 'EmailListManager', 'build_gmail_search_query',
    'get_package_root', 'get_core_dir', 'get_analysis_dir', 'get_utils_dir',
    'get_caching_dir', 'get_project_root', 'get_tests_dir', 'verify_package_structure',
    'count_patterns',
    'match_patterns',   
]
