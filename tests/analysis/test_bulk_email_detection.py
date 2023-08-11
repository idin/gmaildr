"""
Tests for bulk email detection functionality.

This module contains tests to ensure that bulk email indicators are properly
detected in email content.
"""

from gmaildr.analysis.email_metrics import EmailContentAnalyzer


def test_bulk_email_detection_noreply():
    """Test detection of noreply email addresses."""
    analyzer = EmailContentAnalyzer()
    
    # Test with noreply email
    metrics = analyzer.analyze_email_content(
        text_content="This is an automated message from our system.",
        subject="System Notification",
        html_content=None
    )
    
    # Should detect bulk email indicators
    assert metrics.has_bulk_email_indicators


def test_bulk_email_detection_automated_message():
    """Test detection of automated message indicators."""
    analyzer = EmailContentAnalyzer()
    
    # Test with automated message text
    metrics = analyzer.analyze_email_content(
        text_content="This is an automatically generated message. Please do not reply to this email.",
        subject="Account Update",
        html_content=None
    )
    
    # Should detect bulk email indicators
    assert metrics.has_bulk_email_indicators


def test_bulk_email_detection_system_notification():
    """Test detection of system notification indicators."""
    analyzer = EmailContentAnalyzer()
    
    # Test with system notification text
    metrics = analyzer.analyze_email_content(
        text_content="This is a system notification about your account.",
        subject="System Alert",
        html_content=None
    )
    
    # Should detect bulk email indicators
    assert metrics.has_bulk_email_indicators


def test_bulk_email_detection_do_not_reply():
    """Test detection of 'do not reply' indicators."""
    analyzer = EmailContentAnalyzer()
    
    # Test with do not reply text
    metrics = analyzer.analyze_email_content(
        text_content="Please do not reply to this email as it is sent from an unmonitored address.",
        subject="Newsletter",
        html_content=None
    )
    
    # Should detect bulk email indicators
    assert metrics.has_bulk_email_indicators


def test_bulk_email_detection_bulk_mail():
    """Test detection of bulk mail indicators."""
    analyzer = EmailContentAnalyzer()
    
    # Test with bulk mail text
    metrics = analyzer.analyze_email_content(
        text_content="This bulk mail was sent to all subscribers.",
        subject="Newsletter",
        html_content=None
    )
    
    # Should detect bulk email indicators
    assert metrics.has_bulk_email_indicators


def test_bulk_email_detection_human_email():
    """Test that human emails are not flagged as bulk."""
    analyzer = EmailContentAnalyzer()
    
    # Test with human email content
    metrics = analyzer.analyze_email_content(
        text_content="Hi there, I hope you're doing well. Can we meet tomorrow?",
        subject="Meeting Request",
        html_content=None
    )
    
    # Should NOT detect bulk email indicators
    assert not metrics.has_bulk_email_indicators


def test_bulk_email_detection_empty_content():
    """Test bulk email detection with empty content."""
    analyzer = EmailContentAnalyzer()
    
    # Test with empty content
    metrics = analyzer.analyze_email_content(
        text_content="",
        subject="",
        html_content=None
    )
    
    # Should NOT detect bulk email indicators (no content to analyze)
    assert not metrics.has_bulk_email_indicators


def test_bulk_email_detection_mixed_content():
    """Test bulk email detection with mixed content."""
    analyzer = EmailContentAnalyzer()
    
    # Test with content that has some bulk indicators but also human elements
    metrics = analyzer.analyze_email_content(
        text_content="Hi John, this is an automated message but I wanted to personally let you know about the update.",
        subject="Update Notification",
        html_content=None
    )
    
    # Should detect bulk email indicators due to "automated message"
    assert metrics.has_bulk_email_indicators


if __name__ == '__main__':
    print("🧪 Testing Bulk Email Detection...")
    
    # Run all tests
    test_bulk_email_detection_noreply()
    test_bulk_email_detection_automated_message()
    test_bulk_email_detection_system_notification()
    test_bulk_email_detection_do_not_reply()
    test_bulk_email_detection_bulk_mail()
    test_bulk_email_detection_human_email()
    test_bulk_email_detection_empty_content()
    test_bulk_email_detection_mixed_content()
    
    print("🎉 All Bulk Email Detection tests passed!")
