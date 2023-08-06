#!/usr/bin/env python3
"""
Test module structure for GmailWiz.

This test file verifies that the module structure is organized correctly after reorganization.
"""

import sys
import unittest
import importlib

# Add the project root to the path
from gmailwiz.utils.paths import get_project_root, get_core_dir, get_analysis_dir, get_utils_dir, get_cache_dir
sys.path.insert(0, str(get_project_root()))


class TestModuleStructure(unittest.TestCase):
    """Test that the module structure is organized correctly."""
    
    def test_core_module_structure(self):
        """Test core module structure."""
        try:
            core_module = importlib.import_module('gmailwiz.core')
            
            # Check that core module has expected attributes
            expected_attrs = ['Gmail', 'GmailClient', 'ConfigManager', 'setup_logging']
            for attr in expected_attrs:
                self.assertTrue(hasattr(core_module, attr), f"Core module missing {attr}")
            
            print("✅ Core module structure correct")
        except ImportError as e:
            self.fail(f"Core module import failed: {e}")
    
    def test_analysis_module_structure(self):
        """Test analysis module structure."""
        try:
            analysis_module = importlib.import_module('gmailwiz.analysis')
            
            # Check that analysis module has expected attributes
            expected_attrs = [
                'EmailAnalyzer', 'EmailContentAnalyzer', 'analyze_email_text',
                'add_content_metrics_to_dataframe', 'calculate_automated_email_score',
                'classify_email_types'
            ]
            for attr in expected_attrs:
                self.assertTrue(hasattr(analysis_module, attr), f"Analysis module missing {attr}")
            
            print("✅ Analysis module structure correct")
        except ImportError as e:
            self.fail(f"Analysis module import failed: {e}")
    
    def test_utils_module_structure(self):
        """Test utils module structure."""
        try:
            utils_module = importlib.import_module('gmailwiz.utils')
            
            # Check that utils module has expected attributes
            expected_attrs = ['EmailProgressTracker']
            for attr in expected_attrs:
                self.assertTrue(hasattr(utils_module, attr), f"Utils module missing {attr}")
            
            print("✅ Utils module structure correct")
        except ImportError as e:
            self.fail(f"Utils module import failed: {e}")
    
    def test_cache_module_structure(self):
        """Test cache module structure."""
        try:
            cache_module = importlib.import_module('gmailwiz.cache')
            
            # Check that cache module has expected attributes
            expected_attrs = ['EmailCacheManager', 'CacheConfig']
            for attr in expected_attrs:
                self.assertTrue(hasattr(cache_module, attr), f"Cache module missing {attr}")
            
            print("✅ Cache module structure correct")
        except ImportError as e:
            self.fail(f"Cache module import failed: {e}")
    
    def test_main_package_structure(self):
        """Test main package structure."""
        try:
            main_module = importlib.import_module('gmailwiz')
            
            # Check that main package has expected attributes
            expected_attrs = [
                'Gmail', 'GmailClient', 'ConfigManager', 'setup_logging',
                'EmailAnalyzer', 'EmailMessage', 'SenderStatistics', 'AnalysisReport',
                'EmailContentAnalyzer', 'analyze_email_text',
                'add_content_metrics_to_dataframe', 'calculate_automated_email_score',
                'classify_email_types'
            ]
            for attr in expected_attrs:
                self.assertTrue(hasattr(main_module, attr), f"Main package missing {attr}")
            
            print("✅ Main package structure correct")
        except ImportError as e:
            self.fail(f"Main package import failed: {e}")


class TestFileOrganization(unittest.TestCase):
    """Test that files are organized in the correct directories."""
    
    def test_core_files_exist(self):
        """Test that core files exist in the right place."""
        core_dir = get_core_dir()
        expected_files = ['__init__.py', 'gmail.py', 'gmail_client.py', 'config.py']
        
        for file in expected_files:
            file_path = core_dir / file
            self.assertTrue(file_path.exists(), f"Core file missing: {file}")
        
        print("✅ Core files organized correctly")
    
    def test_analysis_files_exist(self):
        """Test that analysis files exist in the right place."""
        analysis_dir = get_analysis_dir()
        expected_files = ['__init__.py', 'email_analyzer.py', 'email_metrics.py', 'metrics_processor.py']
        
        for file in expected_files:
            file_path = analysis_dir / file
            self.assertTrue(file_path.exists(), f"Analysis file missing: {file}")
        
        print("✅ Analysis files organized correctly")
    
    def test_utils_files_exist(self):
        """Test that utils files exist in the right place."""
        utils_dir = get_utils_dir()
        expected_files = ['__init__.py', 'progress.py', 'cli.py']
        
        for file in expected_files:
            file_path = utils_dir / file
            self.assertTrue(file_path.exists(), f"Utils file missing: {file}")
        
        print("✅ Utils files organized correctly")
    
    def test_cache_files_exist(self):
        """Test that cache files exist in the right place."""
        cache_dir = get_cache_dir()
        expected_files = [
            '__init__.py', 'cache_config.py', 'cache_manager.py', 
            'file_storage.py', 'index_manager.py', 'schema_manager.py'
        ]
        
        for file in expected_files:
            file_path = cache_dir / file
            self.assertTrue(file_path.exists(), f"Cache file missing: {file}")
        
        print("✅ Cache files organized correctly")


if __name__ == "__main__":
    print("🧪 Testing GmailWiz module structure...")
    unittest.main(verbosity=2)
