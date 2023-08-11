"""
Test for proper_capitalization_ratio functionality.

This test verifies that proper_capitalization_ratio correctly calculates
the ratio of properly capitalized sentence-starting words.
"""

from gmaildr.analysis.email_metrics import EmailContentAnalyzer


def test_proper_capitalization_ratio_basic():
    """Test basic proper capitalization ratio functionality."""
    analyzer = EmailContentAnalyzer()
    
    # All sentences properly capitalized
    text = "Hello there. How are you? I am fine!"
    ratio = analyzer._calculate_proper_capitalization_ratio(text)
    assert ratio == 1.0, f"Expected 1.0 for properly capitalized text, got {ratio}"


def test_proper_capitalization_ratio_all_lowercase():
    """Test all lowercase sentences."""
    analyzer = EmailContentAnalyzer()
    
    # No sentences properly capitalized
    text = "hello there. how are you? i am fine!"
    ratio = analyzer._calculate_proper_capitalization_ratio(text)
    assert ratio == 0.0, f"Expected 0.0 for all lowercase text, got {ratio}"


def test_proper_capitalization_ratio_mixed():
    """Test mixed capitalization."""
    analyzer = EmailContentAnalyzer()
    
    # 2 out of 3 sentences properly capitalized
    text = "Hello there. how are you? I am fine!"
    ratio = analyzer._calculate_proper_capitalization_ratio(text)
    expected = 2/3  # 2 properly capitalized out of 3 sentences
    assert abs(ratio - expected) < 0.01, f"Expected {expected:.3f}, got {ratio:.3f}"


def test_proper_capitalization_ratio_newlines():
    """Test sentences separated by newlines."""
    analyzer = EmailContentAnalyzer()
    
    # Test with newlines as sentence separators
    text = "Hello\nhow are you\nI am fine"
    ratio = analyzer._calculate_proper_capitalization_ratio(text)
    expected = 2/3  # "Hello" and "I" are capitalized, "how" is not
    assert abs(ratio - expected) < 0.01, f"Expected {expected:.3f}, got {ratio:.3f}"


def test_proper_capitalization_ratio_empty():
    """Test empty and edge cases."""
    analyzer = EmailContentAnalyzer()
    
    # Empty string
    assert analyzer._calculate_proper_capitalization_ratio("") == 0.0
    
    # Only punctuation
    assert analyzer._calculate_proper_capitalization_ratio("...!!!") == 0.0
    
    # Single word
    assert analyzer._calculate_proper_capitalization_ratio("Hello") == 1.0
    assert analyzer._calculate_proper_capitalization_ratio("hello") == 0.0


def test_proper_capitalization_ratio_realistic_email():
    """Test with realistic email content."""
    analyzer = EmailContentAnalyzer()
    
    # Well-written email
    good_email = """
    Hello John,
    
    I hope this email finds you well. I wanted to follow up on our meeting yesterday.
    Could you please send me the report? Thank you for your time.
    
    Best regards,
    Sarah
    """
    
    ratio = analyzer._calculate_proper_capitalization_ratio(good_email)
    # Should be high (close to 1.0) for well-written email
    assert ratio > 0.8, f"Well-written email should have high ratio, got {ratio:.3f}"
    
    # Poorly written email (spam-like)
    bad_email = """
    hello there!!!
    
    amazing offer just for you. don't miss out on this incredible deal!
    click here now. hurry up before it's too late!
    
    buy now
    """
    
    ratio = analyzer._calculate_proper_capitalization_ratio(bad_email)
    # Should be low for poorly written email
    assert ratio < 0.5, f"Poorly written email should have low ratio, got {ratio:.3f}"


def test_proper_capitalization_ratio_integration():
    """Test integration with full email analysis."""
    analyzer = EmailContentAnalyzer()
    
    # Test with full email analysis
    metrics = analyzer.analyze_email_content(
        text_content="Hello there. how are you doing? I am fine!",
        subject="Test Email"
    )
    
    # Should have the proper_capitalization_ratio field
    assert hasattr(metrics, 'proper_capitalization_ratio')
    assert 0.0 <= metrics.proper_capitalization_ratio <= 1.0
    
    # Should be around 0.75 (3 out of 4 sentences properly capitalized)
    # "Test Email" (subject), "Hello there", "I am fine" are capitalized
    # "how are you doing" is not
    expected = 3/4
    assert abs(metrics.proper_capitalization_ratio - expected) < 0.1
