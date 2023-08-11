"""
Test that Gmail can be imported correctly from gmaildr package.
"""

import pytest


def test_gmail_import():
    """Test that Gmail can be imported from gmaildr."""
    try:
        from gmaildr import Gmail
        assert Gmail is not None
        print("✅ Gmail import successful")
    except ImportError as e:
        pytest.fail(f"Failed to import Gmail: {e}")


def test_gmail_instantiation():
    """Test that Gmail can be instantiated."""
    from gmaildr import Gmail
    
    gmail = Gmail()
    assert gmail is not None
    print("✅ Gmail instantiation successful")
