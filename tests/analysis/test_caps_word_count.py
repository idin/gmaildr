"""
Test for caps_word_count functionality.

This test verifies that caps_word_count correctly identifies and counts
words that are entirely in uppercase (2+ characters).
"""

from gmailwiz.analysis.email_metrics import EmailContentAnalyzer


def test_caps_word_count_basic():
    """Test basic caps word counting functionality."""
    analyzer = EmailContentAnalyzer()
    
    # Test text with various capitalization patterns
    test_text = "Hello WORLD this is a TEST message with SOME CAPS words"
    
    caps_count = analyzer._count_caps_words(test_text)
    
    # Should count: WORLD, TEST, SOME, CAPS (4 words)
    expected_count = 4
    assert caps_count == expected_count, f"Expected {expected_count} caps words, got {caps_count}"


def test_caps_word_count_edge_cases():
    """Test edge cases for caps word counting."""
    analyzer = EmailContentAnalyzer()
    
    # Test cases
    test_cases = [
        ("A B C", 0),  # Single letters don't count
        ("HELLO WORLD", 2),  # Two caps words
        ("Hello World", 0),  # Mixed case doesn't count
        ("HELLO", 1),  # Single caps word
        ("hello world", 0),  # No caps
        ("", 0),  # Empty string
        ("HELLO! WORLD?", 2),  # Punctuation doesn't affect
        ("HELLO123 WORLD", 1),  # Numbers make it not pure caps
    ]
    
    for text, expected in test_cases:
        caps_count = analyzer._count_caps_words(text)
        assert caps_count == expected, f"Text '{text}': expected {expected}, got {caps_count}"


def test_caps_word_count_realistic_email():
    """Test caps word count with realistic email content."""
    analyzer = EmailContentAnalyzer()
    
    # Realistic email content
    email_text = """
    Hello there,
    
    This is a normal email with some URGENT information.
    Please note that this is IMPORTANT and requires IMMEDIATE attention.
    
    Best regards,
    The Team
    """
    
    caps_count = analyzer._count_caps_words(email_text)
    
    # Should count: URGENT, IMPORTANT, IMMEDIATE (3 words)
    expected_count = 3
    assert caps_count == expected_count, f"Expected {expected_count} caps words, got {caps_count}"


def test_caps_word_count_zero_case():
    """Test that normal emails can have zero caps words."""
    analyzer = EmailContentAnalyzer()
    
    # Normal email with no ALL-CAPS words
    normal_email = """
    Hello there,
    
    This is a normal email with regular capitalization.
    Nothing urgent or important here.
    
    Best regards,
    The Team
    """
    
    caps_count = analyzer._count_caps_words(normal_email)
    
    # Should be 0 for normal emails
    assert caps_count == 0, f"Normal email should have 0 caps words, got {caps_count}"
