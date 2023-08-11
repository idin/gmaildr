#!/usr/bin/env python3
"""
Test imports for GmailDr package.

This test file verifies that all imports work correctly after the module reorganization.
"""

import sys
import unittest
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestImports(unittest.TestCase):
    """Test that all GmailDr imports work correctly."""
    
    def test_main_imports(self):
        """Test main package imports."""
        try:
            from gmaildr import Gmail, GmailClient, EmailAnalyzer
            print("✅ Main imports successful")
        except ImportError as e:
            self.fail(f"Main imports failed: {e}")
    
    def test_core_imports(self):
        """Test core module imports."""
        try:
            from gmaildr.core import Gmail, GmailClient, ConfigManager, setup_logging
            print("✅ Core imports successful")
        except ImportError as e:
            self.fail(f"Core imports failed: {e}")
    
    def test_analysis_imports(self):
        """Test analysis module imports."""
        try:
            from gmaildr.analysis import (
                EmailAnalyzer,
                EmailContentAnalyzer,
                analyze_email_text,
                add_content_metrics_to_dataframe,
                calculate_automated_email_score,
                classify_email_types
            )
            print("✅ Analysis imports successful")
        except ImportError as e:
            self.fail(f"Analysis imports failed: {e}")
    
    def test_utils_imports(self):
        """Test utils module imports."""
        try:
            from gmaildr.utils import EmailProgressTracker
            print("✅ Utils imports successful")
        except ImportError as e:
            self.fail(f"Utils imports failed: {e}")
    
    def test_models_imports(self):
        """Test models imports."""
        try:
            from gmaildr.models import EmailMessage, SenderStatistics, AnalysisReport
            print("✅ Models imports successful")
        except ImportError as e:
            self.fail(f"Models imports failed: {e}")
    
    def test_cache_imports(self):
        """Test cache module imports."""
        try:
            from gmaildr.caching import EmailCacheManager, CacheConfig
            print("✅ Cache imports successful")
        except ImportError as e:
            self.fail(f"Cache imports failed: {e}")


if __name__ == "__main__":
    print("🧪 Testing GmailDr imports...")
    unittest.main(verbosity=2)
