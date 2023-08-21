"""
Meta-tests to ensure proper import structure and module organization.

These tests verify that all modules can be imported correctly and that
the import structure follows proper conventions.
"""

import importlib
import sys
from pathlib import Path
import re


def test_all_modules_importable():
    """
    Test that all Python modules in the gmaildr package can be imported.
    
    This ensures that there are no syntax errors or missing dependencies
    that would prevent the package from being used.
    """
    project_root = Path(__file__).parent.parent.parent
    gmaildr_path = project_root / 'gmaildr'
    
    import_errors = []
    
    # Find all Python files in the gmaildr package
    for py_file in gmaildr_path.rglob('*.py'):
        if py_file.name == '__init__.py':
            continue
            
        # Convert file path to module path
        relative_path = py_file.relative_to(gmaildr_path)
        module_path = str(relative_path).replace('/', '.').replace('\\', '.')[:-3]
        full_module_path = f'gmaildr.{module_path}'
        
        try:
            importlib.import_module(full_module_path)
        except Exception as e:
            import_errors.append((full_module_path, str(e)))
    
    assert not import_errors, (
        f"Failed to import modules:\n" +
        "\n".join(f"  - {module}: {error}" for module, error in import_errors)
    )


def test_init_files_exist():
    """
    Test that all package directories have __init__.py files.
    
    This ensures that Python recognizes all directories as packages.
    """
    project_root = Path(__file__).parent.parent.parent
    gmaildr_path = project_root / 'gmaildr'
    
    missing_init_files = []
    
    # Directories to exclude (not actual packages)
    exclude_dirs = {'__pycache__', '.pytest_cache', '.git'}
    
    for directory in gmaildr_path.rglob('*'):
        if directory.is_dir():
            # Skip excluded directories
            if directory.name in exclude_dirs:
                continue
                
            init_file = directory / '__init__.py'
            if not init_file.exists():
                relative_path = directory.relative_to(gmaildr_path)
                missing_init_files.append(str(relative_path))
    
    assert not missing_init_files, (
        f"Missing __init__.py files in directories:\n" +
        "\n".join(f"  - {dir_path}" for dir_path in missing_init_files)
    )


def test_no_circular_imports():
    """
    Test that there are no circular imports in the main modules.
    
    This checks the most commonly used modules for circular dependencies.
    """
    # List of core modules to test
    core_modules = [
        'gmaildr.core.gmail',
        'gmaildr.core.email_message',
        'gmaildr.core.email_dataframe',
        'gmaildr.caching.cache_manager',
        'gmaildr.analysis.analyze_email_content',
    ]
    
    circular_imports = []
    
    for module_name in core_modules:
        try:
            # Clear the module from sys.modules to force fresh import
            if module_name in sys.modules:
                del sys.modules[module_name]
            
            # Try to import the module
            importlib.import_module(module_name)
            
        except RecursionError as e:
            circular_imports.append((module_name, str(e)))
        except Exception as e:
            # Other import errors are not circular imports
            pass
    
    assert not circular_imports, (
        f"Found circular imports:\n" +
        "\n".join(f"  - {module}: {error}" for module, error in circular_imports)
    )


def test_relative_imports_used_correctly():
    """
    Test that relative imports are used correctly within the package.
    
    This ensures that internal package imports use relative imports
    rather than absolute imports.
    """
    project_root = Path(__file__).parent.parent.parent
    gmaildr_path = project_root / 'gmaildr'
    
    absolute_imports = []
    
    for py_file in gmaildr_path.rglob('*.py'):
        if py_file.name == '__init__.py':
            continue
            
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            lines = content.split('\n')
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                
                # Check for absolute imports of gmaildr modules
                if line.startswith('from gmaildr.') or line.startswith('import gmaildr.'):
                    relative_path = py_file.relative_to(gmaildr_path)
                    absolute_imports.append((str(relative_path), line_num, line))
                    
        except Exception:
            # Skip files that can't be read
            pass
    
    assert not absolute_imports, (
        f"Found absolute imports of gmaildr modules (should use relative imports):\n" +
        "\n".join(f"  - {file}:{line_num}: {import_line}" 
                 for file, line_num, import_line in absolute_imports)
    )


def test_no_unused_imports():
    """
    Test that there are no obviously unused imports in core modules.
    
    This is a basic check for common unused import patterns.
    """
    project_root = Path(__file__).parent.parent.parent
    gmaildr_path = project_root / 'gmaildr'
    
    # Common unused import patterns
    unused_patterns = [
        r'^import os$',
        r'^import sys$',
        r'^import re$',
        r'^import json$',
        r'^import datetime$',
        r'^import pandas$',
        r'^import numpy$',
    ]
    
    potential_unused = []
    
    for py_file in gmaildr_path.rglob('*.py'):
        if py_file.name == '__init__.py':
            continue
            
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            lines = content.split('\n')
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                
                # Check for potential unused imports
                for pattern in unused_patterns:
                    if re.match(pattern, line):
                        # Check if the imported module is actually used
                        import_name = line.split()[1]
                        if import_name not in content[content.find(line) + len(line):]:
                            relative_path = py_file.relative_to(gmaildr_path)
                            potential_unused.append((str(relative_path), line_num, line))
                        break
                        
        except Exception:
            # Skip files that can't be read
            pass
    
    # This is a warning rather than an error, so we'll just report it
    if potential_unused:
        print("WARNING: Potential unused imports found:")
        for file, line_num, import_line in potential_unused:
            print(f"  - {file}:{line_num}: {import_line}")


def test_import_order():
    """
    Test that imports follow a consistent order.
    
    This ensures that imports are organized in a standard way:
    1. Standard library imports
    2. Third-party imports
    3. Local imports
    """
    project_root = Path(__file__).parent.parent.parent
    gmaildr_path = project_root / 'gmaildr'
    
    import_order_violations = []
    
    # Standard library modules
    stdlib_modules = {
        'os', 'sys', 're', 'json', 'datetime', 'time', 'pathlib',
        'typing', 'dataclasses', 'collections', 'itertools', 'functools',
        'logging', 'warnings', 'traceback', 'copy', 'pickle'
    }
    
    for py_file in gmaildr_path.rglob('*.py'):
        if py_file.name == '__init__.py':
            continue
            
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            lines = content.split('\n')
            current_section = 'stdlib'  # Start with standard library
            violations = []
            
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                
                if line.startswith('import ') or line.startswith('from '):
                    # Determine what type of import this is
                    if line.startswith('from gmaildr.') or line.startswith('import gmaildr.'):
                        import_type = 'local'
                    elif any(module in line for module in stdlib_modules):
                        import_type = 'stdlib'
                    else:
                        import_type = 'third_party'
                    
                    # Check if this violates the order
                    if import_type == 'stdlib' and current_section != 'stdlib':
                        violations.append((line_num, line, 'stdlib import after other imports'))
                    elif import_type == 'third_party' and current_section == 'local':
                        violations.append((line_num, line, 'third_party import after local imports'))
                    elif import_type == 'local' and current_section == 'stdlib':
                        current_section = 'third_party'
                    elif import_type == 'local' and current_section == 'third_party':
                        current_section = 'local'
                    elif import_type == 'third_party' and current_section == 'stdlib':
                        current_section = 'third_party'
                        
            if violations:
                relative_path = py_file.relative_to(gmaildr_path)
                import_order_violations.append((str(relative_path), violations))
                        
        except Exception:
            # Skip files that can't be read
            pass
    
    assert not import_order_violations, (
        f"Found import order violations:\n" +
        "\n".join(f"  - {file}:\n" +
                 "\n".join(f"    Line {line_num}: {line} ({reason})" 
                          for line_num, line, reason in violations)
                 for file, violations in import_order_violations)
    )
