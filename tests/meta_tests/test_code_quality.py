"""
Meta-tests to ensure code quality and style consistency.

These tests verify that the code follows proper conventions for
docstrings, function length, naming conventions, and other quality metrics.
"""

import ast
import re
from pathlib import Path


def test_all_functions_have_docstrings():
    """
    Test that all functions and classes have docstrings.
    
    This ensures proper documentation of the codebase.
    """
    project_root = Path(__file__).parent.parent.parent
    gmaildr_path = project_root / 'gmaildr'
    
    missing_docstrings = []
    
    for py_file in gmaildr_path.rglob('*.py'):
        if py_file.name == '__init__.py':
            continue
            
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            relative_path = py_file.relative_to(gmaildr_path)
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    # Skip private methods (starting with _)
                    if node.name.startswith('_'):
                        continue
                        
                    # Check if the node has a docstring
                    if ast.get_docstring(node) is None:
                        missing_docstrings.append((str(relative_path), node.lineno, node.name, type(node).__name__))
                        
        except Exception:
            # Skip files that can't be parsed
            pass
    
    assert not missing_docstrings, (
        f"Found functions/classes without docstrings:\n" +
        "\n".join(f"  - {file}:{line}: {name} ({node_type})" 
                 for file, line, name, node_type in missing_docstrings)
    )


def test_docstring_format_and_completeness():
    """
    Test that all docstrings follow Google format and have complete argument documentation.
    
    This ensures proper documentation quality and consistency.
    """
    project_root = Path(__file__).parent.parent.parent
    gmaildr_path = project_root / 'gmaildr'
    
    docstring_issues = []
    
    for py_file in gmaildr_path.rglob('*.py'):
        if py_file.name == '__init__.py':
            continue
            
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            relative_path = py_file.relative_to(gmaildr_path)
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    # Skip private methods (starting with _)
                    if node.name.startswith('_'):
                        continue
                    
                    docstring = ast.get_docstring(node)
                    if docstring is None:
                        continue  # Already caught by test_all_functions_have_docstrings
                    
                    # Check for Google docstring format
                    issues = check_google_docstring_format(docstring, node)
                    if issues:
                        docstring_issues.append((str(relative_path), node.lineno, node.name, issues))
                        
        except Exception:
            # Skip files that can't be parsed
            pass
    
    assert not docstring_issues, (
        f"Found docstring format/completeness issues:\n" +
        "\n".join(f"  - {file}:{line}: {name} - {', '.join(issues)}" 
                 for file, line, name, issues in docstring_issues)
    )


def check_google_docstring_format(docstring: str, node) -> list:
    """
    Check if a docstring follows Google format and has complete argument documentation.
    
    Args:
        docstring: The docstring text to check
        node: The AST node (function or class)
        
    Returns:
        List of issues found, empty if docstring is correct
    """
    issues = []
    
    # Split docstring into lines
    lines = docstring.strip().split('\n')
    
    # Check for Args section in function docstrings
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        # Get function arguments
        args = []
        if node.args.args:
            args.extend([arg.arg for arg in node.args.args if arg.arg != 'self'])
        if node.args.kwonlyargs:
            args.extend([arg.arg for arg in node.args.kwonlyargs])
        if node.args.posonlyargs:
            args.extend([arg.arg for arg in node.args.posonlyargs])
        
        # Check if Args section exists
        has_args_section = any('Args:' in line or 'Arguments:' in line for line in lines)
        
        if args and not has_args_section:
            issues.append("missing Args section")
        elif has_args_section:
            # Check if all arguments are documented
            documented_args = set()
            in_args_section = False
            
            for line in lines:
                line = line.strip()
                if 'Args:' in line or 'Arguments:' in line:
                    in_args_section = True
                    continue
                elif in_args_section:
                    if line.startswith('Returns:') or line.startswith('Raises:') or line.startswith('Yields:'):
                        break
                    # Look for argument documentation (Google format: arg_name: type)
                    match = re.match(r'^\s*(\w+)\s*:', line)
                    if match:
                        documented_args.add(match.group(1))
            
            # Check for missing argument documentation
            missing_args = set(args) - documented_args
            if missing_args:
                issues.append(f"missing Args documentation for: {', '.join(missing_args)}")
    
    # Check for Returns section if function has return annotation
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.returns:
        has_returns_section = any('Returns:' in line for line in lines)
        if not has_returns_section:
            issues.append("missing Returns section")
    
    # Check for basic Google format structure
    # Should have a brief description followed by sections
    if len(lines) > 1:
        # Find the end of the brief description (first line that starts with a section header)
        brief_end = 0
        for i, line in enumerate(lines):
            line = line.strip()
            if line.startswith(('Args:', 'Arguments:', 'Returns:', 'Raises:', 'Yields:')):
                brief_end = i
                break
        else:
            # No sections found, brief description is the entire docstring
            return issues
        
        # Check if there's a blank line after the brief description
        if brief_end > 0 and lines[brief_end - 1].strip() != '':
            issues.append("missing blank line after brief description")
    
    return issues


def test_no_overly_long_functions():
    """
    Test that no functions are excessively long.
    
    This ensures code readability and maintainability.
    """
    project_root = Path(__file__).parent.parent.parent
    gmaildr_path = project_root / 'gmaildr'
    
    long_functions = []
    max_lines = 250  # Maximum lines for a function - allows complex operations like auth flows
    
    for py_file in gmaildr_path.rglob('*.py'):
        if py_file.name == '__init__.py':
            continue
            
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            relative_path = py_file.relative_to(gmaildr_path)
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    # Skip private methods
                    if node.name.startswith('_'):
                        continue
                        
                    # Calculate function length
                    function_lines = node.end_lineno - node.lineno + 1
                    if function_lines > max_lines:
                        long_functions.append((str(relative_path), node.lineno, node.name, function_lines))
                        
        except Exception:
            # Skip files that can't be parsed
            pass
    
    assert not long_functions, (
        f"Found functions longer than {max_lines} lines:\n" +
        "\n".join(f"  - {file}:{line}: {name} ({lines} lines)" 
                 for file, line, name, lines in long_functions)
    )


def test_consistent_naming_conventions():
    """
    Test that naming conventions are consistent throughout the codebase.
    
    This ensures that variables, functions, and classes follow Python conventions.
    """
    project_root = Path(__file__).parent.parent.parent
    gmaildr_path = project_root / 'gmaildr'
    
    naming_violations = []
    
    # Naming patterns
    patterns = {
        'function': r'^[a-z_][a-z0-9_]*$',  # snake_case for functions
        'class': r'^[A-Z][a-zA-Z0-9]*$',    # PascalCase for classes
        'constant': r'^[A-Z][A-Z0-9_]*$',   # UPPER_CASE for constants
        'variable': r'^[a-z_][a-z0-9_]*$',  # snake_case for variables
    }
    
    for py_file in gmaildr_path.rglob('*.py'):
        if py_file.name == '__init__.py':
            continue
            
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            relative_path = py_file.relative_to(gmaildr_path)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if not re.match(patterns['function'], node.name):
                        naming_violations.append((str(relative_path), node.lineno, node.name, 'function'))
                        
                elif isinstance(node, ast.ClassDef):
                    if not re.match(patterns['class'], node.name):
                        naming_violations.append((str(relative_path), node.lineno, node.name, 'class'))
                        
                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            # Check if it looks like a constant
                            if target.id.isupper():
                                if not re.match(patterns['constant'], target.id):
                                    naming_violations.append((str(relative_path), node.lineno, target.id, 'constant'))
                            else:
                                if not re.match(patterns['variable'], target.id):
                                    naming_violations.append((str(relative_path), node.lineno, target.id, 'variable'))
                        
        except Exception:
            # Skip files that can't be parsed
            pass
    
    assert not naming_violations, (
        f"Found naming convention violations:\n" +
        "\n".join(f"  - {file}:{line}: {name} (should follow {type_name} convention)" 
                 for file, line, name, type_name in naming_violations)
    )


def test_no_hardcoded_paths():
    """
    Test that no hardcoded file paths exist in the code.
    
    This ensures that the code is portable and doesn't rely on specific file system structures.
    """
    project_root = Path(__file__).parent.parent.parent
    gmaildr_path = project_root / 'gmaildr'
    
    hardcoded_paths = []
    
    # Patterns that indicate hardcoded paths
    path_patterns = [
        r'["\']/[a-zA-Z]',  # Absolute paths starting with /
        r'["\']C:\\',       # Windows absolute paths
        r'["\']D:\\',       # Windows drive paths
        r'["\']E:\\',       # Windows drive paths
        r'["\']F:\\',       # Windows drive paths
        r'["\']G:\\',       # Windows drive paths
        r'["\']H:\\',       # Windows drive paths
        r'["\']I:\\',       # Windows drive paths
        r'["\']J:\\',       # Windows drive paths
        r'["\']K:\\',       # Windows drive paths
        r'["\']L:\\',       # Windows drive paths
        r'["\']M:\\',       # Windows drive paths
        r'["\']N:\\',       # Windows drive paths
        r'["\']O:\\',       # Windows drive paths
        r'["\']P:\\',       # Windows drive paths
        r'["\']Q:\\',       # Windows drive paths
        r'["\']R:\\',       # Windows drive paths
        r'["\']S:\\',       # Windows drive paths
        r'["\']T:\\',       # Windows drive paths
        r'["\']U:\\',       # Windows drive paths
        r'["\']V:\\',       # Windows drive paths
        r'["\']W:\\',       # Windows drive paths
        r'["\']X:\\',       # Windows drive paths
        r'["\']Y:\\',       # Windows drive paths
        r'["\']Z:\\',       # Windows drive paths
    ]
    
    for py_file in gmaildr_path.rglob('*.py'):
        if py_file.name == '__init__.py':
            continue
            
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            relative_path = py_file.relative_to(gmaildr_path)
            
            for line_num, line in enumerate(lines, 1):
                for pattern in path_patterns:
                    if re.search(pattern, line):
                        hardcoded_paths.append((str(relative_path), line_num, line.strip()))
                        break
                        
        except Exception:
            # Skip files that can't be read
            pass
    
    assert not hardcoded_paths, (
        f"Found hardcoded file paths:\n" +
        "\n".join(f"  - {file}:{line_num}: {line}" 
                 for file, line_num, line in hardcoded_paths)
    )


def test_no_print_statements():
    """
    Test that no print statements exist in the code.
    
    This ensures that logging is used instead of print statements.
    """
    project_root = Path(__file__).parent.parent.parent
    gmaildr_path = project_root / 'gmaildr'
    
    print_statements = []
    
    for py_file in gmaildr_path.rglob('*.py'):
        if py_file.name == '__init__.py':
            continue
            
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            relative_path = py_file.relative_to(gmaildr_path)
            
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if line.startswith('print(') or line.startswith('print '):
                    print_statements.append((str(relative_path), line_num, line))
                        
        except Exception:
            # Skip files that can't be read
            pass
    
    assert not print_statements, (
        f"Found print statements (should use logging instead):\n" +
        "\n".join(f"  - {file}:{line_num}: {line}" 
                 for file, line_num, line in print_statements)
    )


def test_no_todo_comments():
    """
    Test that no TODO comments exist in the code.
    
    This ensures that the code is complete and production-ready.
    """
    project_root = Path(__file__).parent.parent.parent
    gmaildr_path = project_root / 'gmaildr'
    
    todo_comments = []
    
    for py_file in gmaildr_path.rglob('*.py'):
        if py_file.name == '__init__.py':
            continue
            
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            relative_path = py_file.relative_to(gmaildr_path)
            
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if 'TODO' in line.upper() or 'FIXME' in line.upper():
                    todo_comments.append((str(relative_path), line_num, line))
                        
        except Exception:
            # Skip files that can't be read
            pass
    
    assert not todo_comments, (
        f"Found TODO/FIXME comments:\n" +
        "\n".join(f"  - {file}:{line_num}: {line}" 
                 for file, line_num, line in todo_comments)
    )
