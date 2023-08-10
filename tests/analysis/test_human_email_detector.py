"""
Tests for human email detection functionality.

This module contains tests for the human email detector to ensure
accurate identification of human vs automated email senders.
"""

import pandas as pd
from datetime import datetime

from gmailwiz.analysis.human_email_detector import (
    HumanEmailDetector,
    HumanEmailScore,
    detect_human_emails,
    get_human_sender_summary
)


def test_analyze_single_email_human():
    """Test analysis of a human email."""
    detector = HumanEmailDetector()
    
    # Sample human email content
    human_email_content = """
    Hi there,
    
    I hope you're doing well. I wanted to check in about our meeting next week.
    Do you think we could reschedule it for Tuesday afternoon? I have a conflict
    with my daughter's soccer game on Wednesday.
    
    Let me know what works for you!
    
    Thanks,
    John Smith
    """
    
    score = detector.analyze_single_email(
        text_content=human_email_content,
        subject="Meeting reschedule",
        sender_email="john.smith@gmail.com",
        sender_name="John Smith",
        has_attachments=False
    )
    
    # Should have high human indicators
    assert score.has_personal_greeting
    assert score.has_conversational_tone
    assert score.has_questions
    assert score.has_personal_details
    assert score.has_signature
    assert score.has_real_name
    assert score.has_personal_domain
    assert score.has_consistent_sender_name
    
    # Should have low automated indicators
    assert not score.has_unsubscribe_link
    assert not score.has_marketing_language
    assert not score.has_legal_disclaimer
    assert not score.has_bulk_email_indicators
    
    # Should have high overall score
    assert score.human_score > 0.5
    assert score.content_score > 0.4
    assert score.sender_score > 0.8


def test_analyze_single_email_automated():
    """Test analysis of an automated email."""
    detector = HumanEmailDetector()
    
    # Sample automated email content
    automated_email_content = """
    LIMITED TIME OFFER!
    
    Save 50% on all products this week only!
    Click here to shop now!
    
    Don't miss out on these amazing deals!
    
    Unsubscribe: Click here to unsubscribe
    Privacy Policy: See our privacy policy
    """
    
    score = detector.analyze_single_email(
        text_content=automated_email_content,
        subject="LIMITED TIME OFFER - Save 50%!",
        sender_email="noreply@company.com",
        sender_name="Company Newsletter",
        has_attachments=False
    )
    
    # Should have low human indicators
    assert not score.has_personal_greeting
    assert not score.has_conversational_tone
    assert not score.has_questions
    assert not score.has_personal_details
    assert not score.has_signature
    
    # Should have high automated indicators
    assert score.has_unsubscribe_link
    assert score.has_marketing_language
    assert score.has_legal_disclaimer
    assert score.has_promotional_content
    
    # Should have low overall score
    assert score.human_score < 0.3
    assert score.content_score < 0.2


def test_analyze_single_email_with_attachments():
    """Test analysis of email with attachments."""
    detector = HumanEmailDetector()
    
    score = detector.analyze_single_email(
        text_content="Here's the document you requested.",
        subject="Document attached",
        sender_email="colleague@company.com",
        sender_name="Jane Doe",
        has_attachments=True
    )
    
    assert score.has_attachments
    assert score.behavioural_score > 0.0


def test_analyze_single_email_empty_content():
    """Test analysis of email with empty content."""
    detector = HumanEmailDetector()
    
    score = detector.analyze_single_email(
        text_content="",
        subject="",
        sender_email="test@example.com"
    )
    
    # Should return default scores
    assert score.human_score == 0.0
    assert score.content_score == 0.0
    assert score.sender_score == 0.0


def test_calculate_content_score():
    """Test content score calculation."""
    detector = HumanEmailDetector()
    score = HumanEmailScore()
    
    # Test with positive indicators
    score.has_personal_greeting = True
    score.has_conversational_tone = True
    score.has_questions = True
    
    content_score = detector._calculate_content_score(score)
    assert content_score > 0.0
    
    # Test with negative indicators
    score.has_unsubscribe_link = True
    score.has_marketing_language = True
    
    content_score_with_negatives = detector._calculate_content_score(score)
    assert content_score_with_negatives < content_score


def test_calculate_sender_score():
    """Test sender score calculation."""
    detector = HumanEmailDetector()
    score = HumanEmailScore()
    
    # Test with all positive indicators
    score.has_real_name = True
    score.has_personal_domain = True
    score.has_consistent_sender_name = True
    
    sender_score = detector._calculate_sender_score(score)
    assert sender_score == 1.0
    
    # Test with partial indicators
    score.has_consistent_sender_name = False
    sender_score_partial = detector._calculate_sender_score(score)
    assert sender_score_partial == 2.0 / 3.0


def test_calculate_overall_score():
    """Test overall score calculation."""
    detector = HumanEmailDetector()
    score = HumanEmailScore()
    score.content_score = 0.8
    score.sender_score = 0.9
    score.behavioural_score = 0.5
    score.conversation_score = 0.7
    
    overall_score = detector._calculate_overall_score(score)
    
    # Should be weighted average
    expected_score = 0.8 * 0.4 + 0.9 * 0.2 + 0.5 * 0.2 + 0.7 * 0.2
    assert abs(overall_score - expected_score) < 0.001


def test_combine_text():
    """Test text combination functionality."""
    detector = HumanEmailDetector()
    
    combined = detector._combine_text(
        text_content="Hello world",
        subject="Test subject",
        html_content="<p>HTML content</p>"
    )
    
    assert "Test subject" in combined
    assert "Hello world" in combined
    assert "HTML content" in combined


def test_detect_human_emails():
    """Test human email detection function."""
    # Create sample DataFrame
    sample_emails = pd.DataFrame({
        'sender_email': ['human1@gmail.com', 'human1@gmail.com', 'bot@company.com'],
        'sender_name': ['John Smith', 'John Smith', 'Company Bot'],
        'subject': ['Hi there', 'Meeting tomorrow', 'Special offer'],
        'text_content': [
            'Hi, how are you? Let me know when you\'re free.',
            'Can we meet tomorrow? I have some questions.',
            'LIMITED TIME OFFER! Click here to save 50%!'
        ],
        'has_attachments': [True, False, False],
        'thread_id': ['thread1', 'thread1', 'thread2'],
        'size_bytes': [1024, 512, 256],
        'is_read': [True, False, True]
    })
    
    result_df = detect_human_emails(
        emails_df=sample_emails,
        human_threshold=0.6,
        show_progress=False
    )
    
    # Should have new columns
    assert 'human_score' in result_df.columns
    assert 'is_human_sender' in result_df.columns
    assert 'content_score' in result_df.columns
    assert 'sender_score' in result_df.columns
    
    # Should have human indicators
    assert 'human_has_personal_greeting' in result_df.columns
    assert 'human_has_conversational_tone' in result_df.columns
    
    # Human sender should have higher scores
    human_emails = result_df[result_df['sender_email'] == 'human1@gmail.com']
    bot_emails = result_df[result_df['sender_email'] == 'bot@company.com']
    
    assert human_emails['human_score'].mean() > bot_emails['human_score'].mean()


def test_get_human_sender_summary():
    """Test human sender summary function."""
    # Create sample DataFrame
    sample_emails = pd.DataFrame({
        'sender_email': ['human1@gmail.com', 'human1@gmail.com', 'bot@company.com'],
        'sender_name': ['John Smith', 'John Smith', 'Company Bot'],
        'subject': ['Hi there', 'Meeting tomorrow', 'Special offer'],
        'text_content': [
            'Hi, how are you? Let me know when you\'re free.',
            'Can we meet tomorrow? I have some questions.',
            'LIMITED TIME OFFER! Click here to save 50%!'
        ],
        'has_attachments': [True, False, False],
        'thread_id': ['thread1', 'thread1', 'thread2'],
        'size_bytes': [1024, 512, 256],
        'is_read': [True, False, True]
    })
    
    # First run detection
    emails_with_scores = detect_human_emails(
        emails_df=sample_emails,
        show_progress=False
    )
    
    # Then get summary
    summary_df = get_human_sender_summary(emails_with_scores)
    
    # Should have summary data
    assert len(summary_df) > 0
    assert 'sender_type' in summary_df.columns
    assert 'sender_count' in summary_df.columns
    assert 'email_count' in summary_df.columns
    assert 'avg_human_score' in summary_df.columns


def test_get_human_sender_summary_no_detection():
    """Test summary function without running detection first."""
    # Create sample DataFrame without detection columns
    sample_emails = pd.DataFrame({
        'sender_email': ['human1@gmail.com', 'bot@company.com'],
        'sender_name': ['John Smith', 'Company Bot'],
        'subject': ['Hi there', 'Special offer'],
        'text_content': ['Hello', 'LIMITED TIME OFFER!']
    })
    
    try:
        get_human_sender_summary(sample_emails)
        assert False, "Expected ValueError but no exception was raised"
    except ValueError:
        # Expected behavior
        pass


def test_detect_human_emails_empty_dataframe():
    """Test detection with empty DataFrame."""
    empty_df = pd.DataFrame()
    result_df = detect_human_emails(empty_df, show_progress=False)
    
    assert result_df.empty


def test_detect_human_emails_custom_threshold():
    """Test detection with custom threshold."""
    # Create sample DataFrame
    sample_emails = pd.DataFrame({
        'sender_email': ['human1@gmail.com', 'human1@gmail.com', 'bot@company.com'],
        'sender_name': ['John Smith', 'John Smith', 'Company Bot'],
        'subject': ['Hi there', 'Meeting tomorrow', 'Special offer'],
        'text_content': [
            'Hi, how are you? Let me know when you\'re free.',
            'Can we meet tomorrow? I have some questions.',
            'LIMITED TIME OFFER! Click here to save 50%!'
        ],
        'has_attachments': [True, False, False],
        'thread_id': ['thread1', 'thread1', 'thread2'],
        'size_bytes': [1024, 512, 256],
        'is_read': [True, False, True]
    })
    
    result_df = detect_human_emails(
        emails_df=sample_emails,
        human_threshold=0.9,  # Very strict threshold
        show_progress=False
    )
    
    # With strict threshold, fewer should be classified as human
    strict_human_count = result_df['is_human_sender'].sum()
    
    result_df_relaxed = detect_human_emails(
        emails_df=sample_emails,
        human_threshold=0.3,  # Relaxed threshold
        show_progress=False
    )
    
    relaxed_human_count = result_df_relaxed['is_human_sender'].sum()
    
    # Relaxed threshold should classify more as human
    assert relaxed_human_count >= strict_human_count


def test_human_email_score_defaults():
    """Test HumanEmailScore default values."""
    score = HumanEmailScore()
    
    assert score.human_score == 0.0
    assert score.content_score == 0.0
    assert score.sender_score == 0.0
    assert score.behavioural_score == 0.0
    assert score.conversation_score == 0.0
    
    # Boolean flags should be False by default
    assert not score.has_personal_greeting
    assert not score.has_conversational_tone
    assert not score.has_questions
    assert not score.has_unsubscribe_link
    assert not score.has_marketing_language


def test_human_email_score_custom_values():
    """Test HumanEmailScore with custom values."""
    score = HumanEmailScore(
        human_score=0.8,
        content_score=0.7,
        sender_score=0.9,
        has_personal_greeting=True,
        has_conversational_tone=True
    )
    
    assert score.human_score == 0.8
    assert score.content_score == 0.7
    assert score.sender_score == 0.9
    assert score.has_personal_greeting
    assert score.has_conversational_tone
    assert not score.has_questions  # Should still be default


if __name__ == '__main__':
    print("🧪 Testing Human Email Detector...")
    
    # Run all tests
    test_analyze_single_email_human()
    test_analyze_single_email_automated()
    test_analyze_single_email_with_attachments()
    test_analyze_single_email_empty_content()
    test_calculate_content_score()
    test_calculate_sender_score()
    test_calculate_overall_score()
    test_combine_text()
    test_detect_human_emails()
    test_get_human_sender_summary()
    test_get_human_sender_summary_no_detection()
    test_detect_human_emails_empty_dataframe()
    test_detect_human_emails_custom_threshold()
    test_human_email_score_defaults()
    test_human_email_score_custom_values()
    
    print("🎉 All Human Email Detector tests passed!")
