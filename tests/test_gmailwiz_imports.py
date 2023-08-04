#!/usr/bin/env python3
"""
Test imports for GmailWiz package.

This test file verifies that all imports work correctly after the module reorganization.
"""

import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_main_imports():
    """Test main package imports."""
    from gmailwiz import Gmail, GmailClient, EmailAnalyzer
    print("✅ Main imports successful")


def test_core_imports():
    """Test core module imports."""
    from gmailwiz.core import Gmail, GmailClient, ConfigManager, setup_logging
    print("✅ Core imports successful")


def test_analysis_imports():
    """Test analysis module imports."""
    from gmailwiz.analysis import (
        EmailAnalyzer,
        EmailContentAnalyzer,
        analyze_email_text,
        add_content_metrics_to_dataframe,
        calculate_automated_email_score,
        classify_email_types
    )
    print("✅ Analysis imports successful")


def test_utils_imports():
    """Test utils module imports."""
    from gmailwiz.utils import EmailProgressTracker
    print("✅ Utils imports successful")


def test_models_imports():
    """Test models imports."""
    from gmailwiz.models import EmailMessage, SenderStatistics, AnalysisReport
    print("✅ Models imports successful")


def test_cache_imports():
    """Test cache module imports."""
    from gmailwiz.cache import EmailCacheManager, CacheConfig
    print("✅ Cache imports successful")


if __name__ == "__main__":
    print("🧪 Testing GmailWiz imports...")
    test_main_imports()
    test_core_imports()
    test_analysis_imports()
    test_utils_imports()
    test_models_imports()
    test_cache_imports()
    print("🎉 All import tests passed!")
