#!/usr/bin/env python3
"""
Test Gmail class functionality.
"""

import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def test_gmail_import():
    """Test that Gmail class can be imported."""
    from gmaildr.core.gmail.main import Gmail
    print("✅ Gmail class import successful")


def test_gmail_initialization():
    """Test Gmail class initialization."""
    from gmaildr.core.gmail.main import Gmail
    
    # Test with default parameters
    gmail = Gmail()
    assert gmail is not None
    print("✅ Gmail initialization successful")


def test_gmail_with_cache():
    """Test Gmail class with cache enabled."""
    from gmaildr.core.gmail.main import Gmail
    
    gmail = Gmail(enable_cache=True)
    assert gmail.cache_manager is not None
    print("✅ Gmail with cache initialization successful")


if __name__ == "__main__":
    print("🧪 Testing Gmail class...")
    test_gmail_import()
    test_gmail_initialization()
    test_gmail_with_cache()
    print("🎉 All Gmail tests passed!")
