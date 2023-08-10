"""
Tests for the match_patterns function.
"""

from gmailwiz.utils import match_patterns


def test_match_pattern_simple():
    """Test simple pattern matching without wildcards."""
    assert match_patterns("hello world", "hello")
    assert match_patterns("hello world", "world")
    assert not match_patterns("hello world", "goodbye")
    assert not match_patterns("", "hello")
    assert not match_patterns("hello", "")


def test_match_pattern_wildcard():
    """Test pattern matching with * wildcards."""
    assert match_patterns("hello world", "hello*")
    assert match_patterns("hello world", "*world")
    assert match_patterns("hello world", "hello*world")
    assert match_patterns("hello beautiful world", "hello*world")
    assert not match_patterns("hello world", "hello*universe")


def test_match_pattern_question_mark():
    """Test pattern matching with ? wildcards."""
    assert match_patterns("hello world", "hello?world")
    assert match_patterns("hello world", "h?llo")
    assert not match_patterns("hello world", "h?llx")


def test_match_patterns_single():
    """Test match_patterns with single pattern."""
    assert match_patterns("hello world", "hello")
    assert match_patterns("hello world", "world")
    assert not match_patterns("hello world", "goodbye")


def test_match_patterns_list():
    """Test match_patterns with list of patterns."""
    patterns = ["hello", "world", "goodbye"]
    assert match_patterns("hello world", patterns)
    assert match_patterns("goodbye", patterns)
    assert not match_patterns("farewell", patterns)


def test_match_patterns_wildcards():
    """Test match_patterns with wildcard patterns."""
    patterns = ["hello*", "*world", "goodbye*"]
    assert match_patterns("hello world", patterns)
    assert match_patterns("goodbye", patterns)
    assert not match_patterns("farewell", patterns)


def test_match_patterns_case_insensitive():
    """Test that match_patterns is case insensitive."""
    assert match_patterns("Hello World", "hello")
    assert match_patterns("HELLO WORLD", "hello")
    assert match_patterns("hello world", "HELLO")


def test_match_patterns_edge_cases():
    """Test edge cases for match_patterns."""
    # Empty strings
    assert not match_patterns("", "hello")
    assert not match_patterns("hello", "")
    assert not match_patterns("", "")
    
    # Multiple wildcards
    assert match_patterns("hello world", "hello**world")
    assert match_patterns("hello world", "**hello**")


if __name__ == '__main__':
    print("🧪 Testing match_patterns...")
    
    # Run all tests
    test_match_pattern_simple()
    test_match_pattern_wildcard()
    test_match_pattern_question_mark()
    test_match_patterns_single()
    test_match_patterns_list()
    test_match_patterns_wildcards()
    test_match_patterns_case_insensitive()
    test_match_patterns_edge_cases()
    
    print("🎉 All match_patterns tests passed!")
