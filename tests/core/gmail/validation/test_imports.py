#!/usr/bin/env python3
"""
Test imports for GmailDr package.

This test file verifies that all imports work correctly after the module reorganization.
"""

import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_main_imports():
    """Test main package imports."""
    try:
        from gmaildr import Gmail
        print("✅ Main imports successful")
    except ImportError as e:
        assert False, f"Main imports failed: {e}"


def test_core_imports():
    """Test core module imports."""
    try:
        from gmaildr.core import Gmail
        print("✅ Core imports successful")
    except ImportError as e:
        assert False, f"Core imports failed: {e}"


def test_analysis_imports():
    """Test analysis module imports."""
    try:
        from gmaildr.analysis import (
            analyze_email_content,
            detect_language_safe,
            is_english,
            get_language_name
        )
        print("✅ Analysis imports successful")
    except ImportError as e:
        assert False, f"Analysis imports failed: {e}"


def test_utils_imports():
    """Test utils module imports."""
    try:
        from gmaildr.utils import EmailProgressTracker
        print("✅ Utils imports successful")
    except ImportError as e:
        assert False, f"Utils imports failed: {e}"


def test_models_imports():
    """Test models imports."""
    try:
        from gmaildr.core.models.email_message import EmailMessage
        from gmaildr.core.models.sender import Sender
        print("✅ Models imports successful")
    except ImportError as e:
        assert False, f"Models imports failed: {e}"


def test_cache_imports():
    """Test cache module imports."""
    try:
        from gmaildr.caching import EmailCacheManager, CacheConfig
        print("✅ Cache imports successful")
    except ImportError as e:
        assert False, f"Cache imports failed: {e}"



