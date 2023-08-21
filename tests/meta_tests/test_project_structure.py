"""
Meta-tests to ensure proper project structure and file organization.

These tests verify that files are located in their appropriate directories
and that the project follows proper organizational conventions.
"""

import os
import re
from pathlib import Path


def test_no_test_files_outside_tests_directory():
    """
    Test that no test files exist outside the tests/ directory.
    
    This ensures that all test files are properly organized in the tests/
    directory and its subdirectories.
    """
    project_root = Path(__file__).parent.parent.parent
    test_files_found = []
    
        # Patterns that indicate test files
    test_patterns = [
        r'^test_.*\.py$',  # Files starting with test_
        r'^.*_test\.py$',  # Files ending with _test.py
        r'^test_.*\.pyx$',  # Cython test files
    ]
    
    # Directories to exclude from search
    exclude_dirs = {
        'tests',  # The tests directory itself
        '.git',   # Git directory
        '__pycache__',  # Python cache
        '.pytest_cache',  # Pytest cache
        'gmaildr.egg-info',  # Package build info
        '.ipynb_checkpoints',  # Jupyter checkpoints
        '.vscode',  # VS Code settings
    }
    
    for root, dirs, files in os.walk(project_root):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            file_path = Path(root) / file
            relative_path = file_path.relative_to(project_root)
            
            # Check if this looks like a test file
            for pattern in test_patterns:
                if re.match(pattern, file):
                    # If it's a test file but not in tests/ directory
                    if not str(relative_path).startswith('tests/'):
                        test_files_found.append(str(relative_path))
                    break
    
    assert not test_files_found, (
        f"Found test files outside tests/ directory:\n" +
        "\n".join(f"  - {file}" for file in test_files_found)
    )


def test_no_cache_files_outside_cache_directory():
    """
    Test that no cache files exist outside the cache/ directory.
    
    Cache files should be contained within the cache/ directory or ignored.
    """
    project_root = Path(__file__).parent.parent.parent
    cache_files_found = []
    
    # Cache file patterns
    cache_patterns = [
        r'^.*\.cache$',
        r'^.*\.pyc$',
        r'^.*\.pyo$',
        r'^.*\.pyd$',
        r'^__pycache__$',
        r'^\.pytest_cache$',
        r'^\.coverage$',
        r'^.*\.log$',
        r'^.*\.tmp$',
        r'^.*\.temp$',
    ]
    
    # Directories where cache files are allowed
    allowed_dirs = {
        'cache',  # Main cache directory
        'logs',   # Log files directory
        '__pycache__',  # Python cache
        '.pytest_cache',  # Pytest cache
        '.ipynb_checkpoints',  # Jupyter checkpoints
    }
    
    for root, dirs, files in os.walk(project_root):
        # Skip __pycache__ directories entirely
        dirs[:] = [d for d in dirs if d != '__pycache__']
        
        for file in files:
            file_path = Path(root) / file
            relative_path = file_path.relative_to(project_root)
            parent_dir = str(relative_path.parent)
            
            # Check if this looks like a cache file
            for pattern in cache_patterns:
                if re.match(pattern, file):
                    # If it's not in an allowed directory
                    if parent_dir not in allowed_dirs and not parent_dir.startswith('cache/'):
                        cache_files_found.append(str(relative_path))
                    break
    
    assert not cache_files_found, (
        f"Found cache files outside cache/ directory:\n" +
        "\n".join(f"  - {file}" for file in cache_files_found)
    )


def test_no_config_files_in_wrong_locations():
    """
    Test that configuration files are in appropriate locations.
    
    Config files should be in the root directory or specific config directories.
    """
    project_root = Path(__file__).parent.parent.parent
    misplaced_config_files = []
    
    # Config file patterns
    config_patterns = [
        r'^\.env$',
        r'^\.env\..*$',
        r'^config\.py$',
        r'^settings\.py$',
        r'^\.pytest\.ini$',
        r'^pyproject\.toml$',
        r'^setup\.cfg$',
        r'^tox\.ini$',
        r'^\.flake8$',
        r'^\.pylintrc$',
        r'^\.mypy\.ini$',
    ]
    
    # Directories where config files are allowed
    allowed_dirs = {
        '',  # Root directory
        'tests',  # Test configs
        'docs',   # Documentation configs
        'gmaildr/core',  # Application configs
    }
    
    for root, dirs, files in os.walk(project_root):
        for file in files:
            file_path = Path(root) / file
            relative_path = file_path.relative_to(project_root)
            parent_dir = str(relative_path.parent)
            
            # Check if this looks like a config file
            for pattern in config_patterns:
                if re.match(pattern, file):
                    # If it's not in an allowed directory
                    if parent_dir not in allowed_dirs:
                        misplaced_config_files.append(str(relative_path))
                    break
    
    assert not misplaced_config_files, (
        f"Found config files in inappropriate locations:\n" +
        "\n".join(f"  - {file}" for file in misplaced_config_files)
    )


def test_no_credentials_in_code_directories():
    """
    Test that no credential files exist in code directories.
    
    Credential files should be in secure locations or ignored.
    """
    project_root = Path(__file__).parent.parent.parent
    credential_files_found = []
    
    # Credential file patterns
    credential_patterns = [
        r'^.*\.key$',
        r'^.*\.pem$',
        r'^.*\.p12$',
        r'^.*\.pfx$',
        r'^.*\.crt$',
        r'^.*\.cer$',
        r'^.*\.der$',
        r'^.*\.p8$',
        r'^.*\.pem$',
        r'^token\.json$',
        r'^token\.pickle$',
        r'^credentials\.json$',
        r'^service_account\.json$',
        r'^\.env$',
        r'^\.env\..*$',
    ]
    
    # Directories where credentials might be allowed
    allowed_dirs = {'credentials'}  # Root directory and credentials directory
    
    for root, dirs, files in os.walk(project_root):
        for file in files:
            file_path = Path(root) / file
            relative_path = file_path.relative_to(project_root)
            parent_dir = str(relative_path.parent)
            
            # Check if this looks like a credential file
            for pattern in credential_patterns:
                if re.match(pattern, file):
                    # If it's not in an allowed directory
                    if parent_dir not in allowed_dirs:
                        credential_files_found.append(str(relative_path))
                    break
    
    assert not credential_files_found, (
        f"Found credential files in inappropriate locations:\n" +
        "\n".join(f"  - {file}" for file in credential_files_found)
    )


def test_no_duplicate_test_files():
    """
    Test that no duplicate test files exist with the same name.
    
    This prevents confusion and ensures proper test organization.
    """
    project_root = Path(__file__).parent.parent.parent
    test_files = {}
    duplicates = []
    
    for root, dirs, files in os.walk(project_root):
        for file in files:
            if file.startswith('test_') and file.endswith('.py'):
                file_path = Path(root) / file
                relative_path = file_path.relative_to(project_root)
                
                if file in test_files:
                    duplicates.append((file, test_files[file], str(relative_path)))
                else:
                    test_files[file] = str(relative_path)
    
    assert not duplicates, (
        f"Found duplicate test files:\n" +
        "\n".join(f"  - {file}: {path1} and {path2}" 
                 for file, path1, path2 in duplicates)
    )


def test_no_orphaned_directories():
    """
    Test that no empty or orphaned directories exist.
    
    This ensures the project structure is clean and organized.
    """
    project_root = Path(__file__).parent.parent.parent
    orphaned_dirs = []
    
    # Directories that are allowed to be empty
    allowed_empty_dirs = {
        'cache', 'output', 'email_lists', 'misc/examples',
        '__pycache__', '.pytest_cache', '.ipynb_checkpoints'
    }
    
    for root, dirs, files in os.walk(project_root):
        dir_path = Path(root)
        relative_path = dir_path.relative_to(project_root)
        
        # Skip if this is an allowed empty directory
        if str(relative_path) in allowed_empty_dirs:
            continue
            
        # Check if directory is empty (no files and no subdirectories with files)
        has_files = len(files) > 0
        has_subdirs_with_files = False
        
        for subdir in dirs:
            subdir_path = dir_path / subdir
            if any(subdir_path.rglob('*')):
                has_subdirs_with_files = True
                break
        
        if not has_files and not has_subdirs_with_files:
            orphaned_dirs.append(str(relative_path))
    
    assert not orphaned_dirs, (
        f"Found orphaned/empty directories:\n" +
        "\n".join(f"  - {dir_path}" for dir_path in orphaned_dirs)
    )
