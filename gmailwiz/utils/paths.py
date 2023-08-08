"""
Path utilities for GmailWiz package.

This module provides utility functions to get package directories and paths
that can be used by tests and other modules.
"""

from pathlib import Path
import os


def get_package_root() -> Path:
    """
    Get the root directory of the GmailWiz package.
    
    Returns:
        Path: Path to the gmailwiz package root directory.
    """
    # Get the directory containing this file
    current_file = Path(__file__)
    # Go up to utils, then up to gmailwiz root
    return current_file.parent.parent


def get_core_dir() -> Path:
    """
    Get the core module directory.
    
    Returns:
        Path: Path to the gmailwiz/core directory.
    """
    return get_package_root() / 'core'


def get_analysis_dir() -> Path:
    """
    Get the analysis module directory.
    
    Returns:
        Path: Path to the gmailwiz/analysis directory.
    """
    return get_package_root() / 'analysis'


def get_utils_dir() -> Path:
    """
    Get the utils module directory.
    
    Returns:
        Path: Path to the gmailwiz/utils directory.
    """
    return get_package_root() / 'utils'


def get_caching_dir() -> Path:
    """
    Get the caching module directory.
    
    Returns:
        Path: Path to the gmailwiz/caching directory.
    """
    return get_package_root() / 'caching'


def get_project_root() -> Path:
    """
    Get the project root directory (parent of gmailwiz package).
    
    Returns:
        Path: Path to the project root directory.
    """
    return get_package_root().parent


def get_tests_dir() -> Path:
    """
    Get the tests directory.
    
    Returns:
        Path: Path to the tests directory.
    """
    return get_project_root() / 'tests'


def verify_package_structure() -> dict:
    """
    Verify that all required package directories and files exist.
    
    Returns:
        dict: Dictionary with verification results for each module.
    """
    results = {}
    
    # Check core module
    core_dir = get_core_dir()
    core_files = ['__init__.py', 'gmail.py', 'gmail_client.py', 'config.py']
    results['core'] = {
        'dir_exists': core_dir.exists(),
        'files_exist': all((core_dir / file).exists() for file in core_files),
        'missing_files': [file for file in core_files if not (core_dir / file).exists()]
    }
    
    # Check analysis module
    analysis_dir = get_analysis_dir()
    analysis_files = ['__init__.py', 'email_analyzer.py', 'email_metrics.py', 'metrics_processor.py']
    results['analysis'] = {
        'dir_exists': analysis_dir.exists(),
        'files_exist': all((analysis_dir / file).exists() for file in analysis_files),
        'missing_files': [file for file in analysis_files if not (analysis_dir / file).exists()]
    }
    
    # Check utils module
    utils_dir = get_utils_dir()
    utils_files = ['__init__.py', 'progress.py', 'cli.py', 'email_lists.py', 'query_builder.py']
    results['utils'] = {
        'dir_exists': utils_dir.exists(),
        'files_exist': all((utils_dir / file).exists() for file in utils_files),
        'missing_files': [file for file in utils_files if not (utils_dir / file).exists()]
    }
    
    # Check caching module
    caching_dir = get_caching_dir()
    caching_files = ['__init__.py', 'cache_config.py', 'cache_manager.py', 'file_storage.py', 'index_manager.py', 'schema_manager.py']
    results['caching'] = {
        'dir_exists': caching_dir.exists(),
        'files_exist': all((caching_dir / file).exists() for file in caching_files),
        'missing_files': [file for file in caching_files if not (caching_dir / file).exists()]
    }
    
    return results
