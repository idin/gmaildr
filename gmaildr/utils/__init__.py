"""
Utility functions for the gmaildr package.
"""

from .email_lists import EmailListManager
from .paths import (
    get_analysis_dir,
    get_caching_dir,
    get_core_dir,
    get_package_root,
    get_project_root,
    get_tests_dir,
    get_utils_dir,
    verify_package_structure,
)
from .pattern_matching import count_patterns, match_patterns
from .progress import EmailProgressTracker
from .query_builder import build_gmail_search_query

__all__ = [
    'EmailProgressTracker', 'EmailListManager', 'build_gmail_search_query',
    'get_package_root', 'get_core_dir', 'get_analysis_dir', 'get_utils_dir',
    'get_caching_dir', 'get_project_root', 'get_tests_dir', 'verify_package_structure',
    'count_patterns',
    'match_patterns',   
]
