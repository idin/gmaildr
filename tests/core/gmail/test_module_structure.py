#!/usr/bin/env python3
"""
Test module structure for GmailDr.

This test file verifies that the module structure is organized correctly after reorganization.
"""

import sys
import importlib

# Add the project root to the path
from gmaildr.utils.paths import get_project_root, get_core_dir, get_analysis_dir, get_utils_dir, get_caching_dir
sys.path.insert(0, str(get_project_root()))


def test_core_module_structure():
    """Test core module structure."""
    try:
        core_module = importlib.import_module('gmaildr.core')
        
        # Check that core module has expected attributes
        expected_attrs = ['Gmail']
        for attr in expected_attrs:
            assert hasattr(core_module, attr), f"Core module missing {attr}"
        
        # Check that GmailClient is available from client module
        from gmaildr.core.client import GmailClient
        assert GmailClient is not None, "GmailClient should be available from client module"
        
        # Check that ConfigManager is available from config module
        from gmaildr.core.config import ConfigManager
        assert ConfigManager is not None, "ConfigManager should be available from config module"
        
        print("✅ Core module structure correct")
    except ImportError as e:
        assert False, f"Core module import failed: {e}"


def test_analysis_module_structure():
    """Test analysis module structure."""
    try:
        analysis_module = importlib.import_module('gmaildr.analysis')
        
        # Check that analysis module has expected attributes
        expected_attrs = [
            'analyze_email_content', 'detect_language_safe',
            'is_english', 'get_language_name'
        ]
        for attr in expected_attrs:
            assert hasattr(analysis_module, attr), f"Analysis module missing {attr}"
        
        print("✅ Analysis module structure correct")
    except ImportError as e:
        assert False, f"Analysis module import failed: {e}"


def test_utils_module_structure():
    """Test utils module structure."""
    try:
        utils_module = importlib.import_module('gmaildr.utils')
        
        # Check that utils module has expected attributes
        expected_attrs = ['EmailProgressTracker']
        for attr in expected_attrs:
            assert hasattr(utils_module, attr), f"Utils module missing {attr}"
        
        print("✅ Utils module structure correct")
    except ImportError as e:
        assert False, f"Utils module import failed: {e}"


def test_cache_module_structure():
    """Test cache module structure."""
    try:
        cache_module = importlib.import_module('gmaildr.caching')
        
        # Check that cache module has expected attributes
        expected_attrs = ['EmailCacheManager', 'CacheConfig']
        for attr in expected_attrs:
            assert hasattr(cache_module, attr), f"Cache module missing {attr}"
        
        print("✅ Cache module structure correct")
    except ImportError as e:
        assert False, f"Cache module import failed: {e}"


def test_main_package_structure():
    """Test main package structure."""
    try:
        main_module = importlib.import_module('gmaildr')
        
        # Check that main package has expected attributes
        expected_attrs = [
            'Gmail', 'GmailClient', 'ConfigManager', 'setup_logging',
            'EmailMessage', 'Sender',
            'analyze_email_content', 'detect_language_safe',
            'is_english', 'get_language_name'
        ]
        for attr in expected_attrs:
            assert hasattr(main_module, attr), f"Main package missing {attr}"
        
        print("✅ Main package structure correct")
    except ImportError as e:
        assert False, f"Main package import failed: {e}"


def test_core_files_exist():
    """Test that core files exist in the right place."""
    core_dir = get_core_dir()
    
    # Check core directory exists
    assert core_dir.exists(), "Core directory missing"
    
    # Check that client directory exists and contains gmail_client.py
    client_dir = core_dir / 'client'
    assert client_dir.exists(), "client directory missing in core"
    assert (client_dir / 'gmail_client.py').exists(), "client/gmail_client.py file missing"
    
    # Check that config directory exists and contains config.py
    config_dir = core_dir / 'config'
    assert config_dir.exists(), "config directory missing in core"
    assert (config_dir / 'config.py').exists(), "config/config.py file missing"
    
    # Check that models directory exists and contains email_message.py
    models_dir = core_dir / 'models'
    assert models_dir.exists(), "models directory missing in core"
    assert (models_dir / 'email_message.py').exists(), "models/email_message.py file missing"
    
    # Check that email_dataframe exists in data directory
    data_dir = get_project_root() / 'gmaildr' / 'data' / 'email_dataframe'
    assert data_dir.exists(), "email_dataframe directory missing in data"
    assert (data_dir / 'email_dataframe.py').exists(), "data/email_dataframe/email_dataframe.py file missing"
    
    print("✅ Core files organized correctly")


def test_analysis_files_exist():
    """Test that analysis files exist in the right place."""
    analysis_dir = get_analysis_dir()
    expected_files = ['__init__.py', 'analyze_email_content.py', 'language_detector.py', 'unsubscribe_links.py', 'marketing_language.py', 'legal_disclaimers.py', 'bulk_email_indicators.py', 'tracking_pixels.py', 'count_external_links.py', 'count_images.py', 'count_exclamations.py', 'count_caps_words.py', 'calculate_text_ratios.py']
    
    for file in expected_files:
        file_path = analysis_dir / file
        assert file_path.exists(), f"Analysis file missing: {file}"
    
    print("✅ Analysis files organized correctly")


def test_utils_files_exist():
    """Test that utils files exist in the right place."""
    utils_dir = get_utils_dir()
    expected_files = ['__init__.py', 'progress.py', 'cli.py']
    
    for file in expected_files:
        file_path = utils_dir / file
        assert file_path.exists(), f"Utils file missing: {file}"
    
    print("✅ Utils files organized correctly")


def test_cache_files_exist():
    """Test that cache files exist in the right place."""
    cache_dir = get_caching_dir()
    expected_files = [
        '__init__.py', 'cache_config.py', 'cache_manager.py', 
        'file_storage.py', 'index_manager.py', 'schema_manager.py'
    ]
    
    for file in expected_files:
        file_path = cache_dir / file
        assert file_path.exists(), f"Cache file missing: {file}"
    
    print("✅ Cache files organized correctly")



