#!/usr/bin/env python3
"""
Test EmailProgressTracker functionality.
"""

import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def test_progress_import():
    """Test that EmailProgressTracker can be imported."""
    from gmaildr.utils.progress import EmailProgressTracker
    print("✅ EmailProgressTracker import successful")


def test_progress_initialization():
    """Test EmailProgressTracker initialization."""
    from gmaildr.utils.progress import EmailProgressTracker
    
    tracker = EmailProgressTracker(total=10, description="Test progress")
    assert tracker is not None
    print("✅ EmailProgressTracker initialization successful")


def test_progress_context_manager():
    """Test EmailProgressTracker as context manager."""
    from gmaildr.utils.progress import EmailProgressTracker
    
    with EmailProgressTracker(total=5, description="Test context") as progress:
        assert progress is not None
        progress.update(1)
    
    print("✅ EmailProgressTracker context manager successful")


if __name__ == "__main__":
    print("🧪 Testing EmailProgressTracker...")
    test_progress_import()
    test_progress_initialization()
    test_progress_context_manager()
    print("🎉 All progress tests passed!")
