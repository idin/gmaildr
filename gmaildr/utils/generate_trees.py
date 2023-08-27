#!/usr/bin/env python3
"""
Generate tree structures for package and test directories to compare them.
"""

import os
from pathlib import Path

def generate_tree(directory, prefix="", is_last=True, max_depth=4, current_depth=0):
    """
    Generate a tree structure for a directory.
    
    Args:
        directory: Directory path to generate tree for
        prefix: Prefix string for tree formatting
        is_last: Whether this is the last item in the current level
        max_depth: Maximum depth to traverse
        current_depth: Current traversal depth
    """
    if current_depth > max_depth:
        return ""
    
    tree = []
    path = Path(directory)
    
    if not path.exists():
        return f"{prefix}📁 {path.name}/ (❌ MISSING)\n"
    
    # Get all items in directory
    items = []
    for item in path.iterdir():
        if item.name not in ['__pycache__', '.pytest_cache', '.git']:
            items.append(item)
    
    # Sort items: directories first, then files
    dirs = sorted([item for item in items if item.is_dir()])
    files = sorted([item for item in items if item.is_file() and item.suffix == '.py'])
    
    all_items = dirs + files
    
    for i, item in enumerate(all_items):
        is_last_item = i == len(all_items) - 1
        current_prefix = "└── " if is_last_item else "├── "
        
        if item.is_dir():
            tree.append(f"{prefix}{current_prefix}📁 {item.name}/")
            next_prefix = prefix + ("    " if is_last_item else "│   ")
            subtree = generate_tree(item, next_prefix, is_last_item, max_depth, current_depth + 1)
            tree.append(subtree)
        else:
            tree.append(f"{prefix}{current_prefix}📄 {item.name}")
    
    return "\n".join(tree)

def main():
    """Generate and display both trees."""
    print("🌳 PACKAGE TREE (gmaildr/)")
    print("=" * 50)
    package_tree = generate_tree("gmaildr")
    print(package_tree)
    
    print("\n" + "=" * 50)
    print("🧪 TEST TREE (tests/)")
    print("=" * 50)
    test_tree = generate_tree("tests")
    print(test_tree)
    
    print("\n" + "=" * 50)
    print("🔍 STRUCTURE COMPARISON")
    print("=" * 50)
    
    # Compare structures
    package_dirs = set()
    test_dirs = set()
    
    for root, dirs, files in os.walk("gmaildr"):
        if "__pycache__" not in root:
            rel_path = os.path.relpath(root, "gmaildr")
            if rel_path != ".":
                package_dirs.add(rel_path)
    
    for root, dirs, files in os.walk("tests"):
        if "__pycache__" not in root:
            rel_path = os.path.relpath(root, "tests")
            if rel_path != ".":
                test_dirs.add(rel_path)
    
    print("📦 Package directories:")
    for dir_path in sorted(package_dirs):
        print(f"  - {dir_path}")
    
    print("\n🧪 Test directories:")
    for dir_path in sorted(test_dirs):
        print(f"  - {dir_path}")
    
    # Find mismatches
    package_only = package_dirs - test_dirs
    test_only = test_dirs - package_dirs
    
    if package_only:
        print(f"\n❌ Package directories without tests:")
        for dir_path in sorted(package_only):
            print(f"  - {dir_path}")
    
    if test_only:
        print(f"\n❌ Test directories without package counterparts:")
        for dir_path in sorted(test_only):
            print(f"  - {dir_path}")
    
    if not package_only and not test_only:
        print("\n✅ All package directories have corresponding test directories!")

if __name__ == "__main__":
    main()
