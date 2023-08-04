#!/usr/bin/env python3
"""
Test module structure for GmailWiz.

This test file verifies that the module structure is organized correctly after reorganization.
"""

import sys
import importlib
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_core_module_structure():
    """Test core module structure."""
    core_module = importlib.import_module('gmailwiz.core')
    
    # Check that core module has expected attributes
    expected_attrs = ['Gmail', 'GmailClient', 'ConfigManager', 'setup_logging']
    for attr in expected_attrs:
        assert hasattr(core_module, attr), f"Core module missing {attr}"
    
    print("✅ Core module structure correct")


def test_analysis_module_structure():
    """Test analysis module structure."""
    analysis_module = importlib.import_module('gmailwiz.analysis')
    
    # Check that analysis module has expected attributes
    expected_attrs = [
        'EmailAnalyzer', 'EmailContentAnalyzer', 'analyze_email_text',
        'add_content_metrics_to_dataframe', 'calculate_automated_email_score',
        'classify_email_types'
    ]
    for attr in expected_attrs:
        assert hasattr(analysis_module, attr), f"Analysis module missing {attr}"
    
    print("✅ Analysis module structure correct")


def test_utils_module_structure():
    """Test utils module structure."""
    utils_module = importlib.import_module('gmailwiz.utils')
    
    # Check that utils module has expected attributes
    expected_attrs = ['EmailProgressTracker']
    for attr in expected_attrs:
        assert hasattr(utils_module, attr), f"Utils module missing {attr}"
    
    print("✅ Utils module structure correct")


def test_cache_module_structure():
    """Test cache module structure."""
    cache_module = importlib.import_module('gmailwiz.cache')
    
    # Check that cache module has expected attributes
    expected_attrs = ['EmailCacheManager', 'CacheConfig']
    for attr in expected_attrs:
        assert hasattr(cache_module, attr), f"Cache module missing {attr}"
    
    print("✅ Cache module structure correct")


def test_main_package_structure():
    """Test main package structure."""
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
        assert hasattr(main_module, attr), f"Main package missing {attr}"
    
    print("✅ Main package structure correct")


def test_core_files_exist():
    """Test that core files exist in the right place."""
    core_dir = project_root / 'gmailwiz' / 'core'
    expected_files = ['__init__.py', 'gmail.py', 'gmail_client.py', 'config.py']
    
    for file in expected_files:
        file_path = core_dir / file
        assert file_path.exists(), f"Core file missing: {file}"
    
    print("✅ Core files organized correctly")


def test_analysis_files_exist():
    """Test that analysis files exist in the right place."""
    analysis_dir = project_root / 'gmailwiz' / 'analysis'
    expected_files = ['__init__.py', 'email_analyzer.py', 'email_metrics.py', 'metrics_processor.py']
    
    for file in expected_files:
        file_path = analysis_dir / file
        assert file_path.exists(), f"Analysis file missing: {file}"
    
    print("✅ Analysis files organized correctly")


def test_utils_files_exist():
    """Test that utils files exist in the right place."""
    utils_dir = project_root / 'gmailwiz' / 'utils'
    expected_files = ['__init__.py', 'progress.py', 'cli.py']
    
    for file in expected_files:
        file_path = utils_dir / file
        assert file_path.exists(), f"Utils file missing: {file}"
    
    print("✅ Utils files organized correctly")


def test_cache_files_exist():
    """Test that cache files exist in the right place."""
    cache_dir = project_root / 'gmailwiz' / 'cache'
    expected_files = [
        '__init__.py', 'cache_config.py', 'cache_manager.py', 
        'file_storage.py', 'index_manager.py', 'schema_manager.py'
    ]
    
    for file in expected_files:
        file_path = cache_dir / file
        assert file_path.exists(), f"Cache file missing: {file}"
    
    print("✅ Cache files organized correctly")


if __name__ == "__main__":
    print("🧪 Testing GmailWiz module structure...")
    test_core_module_structure()
    test_analysis_module_structure()
    test_utils_module_structure()
    test_cache_module_structure()
    test_main_package_structure()
    test_core_files_exist()
    test_analysis_files_exist()
    test_utils_files_exist()
    test_cache_files_exist()
    print("🎉 All structure tests passed!")
