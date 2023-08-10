"""
Tests for the fixed pattern matching function.
"""

from gmailwiz.utils import count_patterns


def test_count_pattern_simple():
    """Test simple pattern matching without wildcards."""
    assert count_patterns("hello world", "hello") == 1
    assert count_patterns("hello world hello", "hello") == 2
    assert count_patterns("hello world", "world") == 1
    assert count_patterns("hello world", "goodbye") == 0
    assert count_patterns("", "hello") == 0
    assert count_patterns("hello", "") == 0


def test_count_pattern_wildcard():
    """Test pattern matching with * wildcards."""
    assert count_patterns("hello world", "hello*") == 1
    assert count_patterns("hello world", "*world") == 1
    assert count_patterns("hello world", "hello*world") == 1
    assert count_patterns("hello beautiful world", "hello*world") == 1
    assert count_patterns("hello world", "hello*universe") == 0

def test_count_pattern_repeated_with_wildcard():
    assert count_patterns("hello world hello", "hello*") == 2
    assert count_patterns("hello world hello", "*hello") == 2
    assert count_patterns("hello xxx world hello", "*hello*") == 2
    assert count_patterns("hello xxxx world hello", "*hello*world") == 1
    assert count_patterns("hello world hello", "*hello*world*") == 1
    assert count_patterns("hello world hello", "*hello*world*hello") == 1
    assert count_patterns("hello world hello", "*hello*world*hello*") == 1
    assert count_patterns("helloAAA world hello BBBworld", "*hello*world*hello*hello") == 1
    assert count_patterns("hello world world", "*hello*world*") == 2


def test_count_pattern_multiple_wildcards():
    """Test pattern matching with multiple * wildcards."""
    assert count_patterns("hello beautiful world", "hello*world") == 1
    assert count_patterns("hello beautiful amazing world", "hello*amazing*world") == 1
    assert count_patterns("hello world", "hello*amazing*world") == 0


def test_count_pattern_case_insensitive():
    """Test that pattern matching is case insensitive."""
    assert count_patterns("Hello World", "hello") == 1
    assert count_patterns("HELLO WORLD", "hello") == 1
    assert count_patterns("hello world", "HELLO") == 1


def test_count_patterns():
    """Test count_patterns function."""
    patterns = ["hello", "world", "goodbye"]
    assert count_patterns("hello world", patterns) == 2
    assert count_patterns("goodbye", patterns) == 1
    assert count_patterns("farewell", patterns) == 0


def test_count_patterns_single():
    """Test count_patterns with single pattern."""
    assert count_patterns("hello world", "hello") == 1
    assert count_patterns("hello world", "goodbye") == 0


if __name__ == '__main__':
    print("🧪 Testing Fixed Pattern Matching...")
    
    # Run all tests
    test_count_pattern_simple()
    test_count_pattern_wildcard()
    test_count_pattern_repeated_with_wildcard()
    test_count_pattern_multiple_wildcards()
    test_count_pattern_case_insensitive()
    test_count_patterns()
    test_count_patterns_single()
    
    print("🎉 All Pattern Matching tests passed!")
