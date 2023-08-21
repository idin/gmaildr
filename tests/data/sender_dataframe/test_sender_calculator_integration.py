"""
Integration tests for sender statistics calculator.
"""

import pytest
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

from gmaildr.data.sender_dataframe import SenderDataFrame
from gmaildr.data.sender_dataframe import aggregate_emails_by_sender
from gmaildr.data.email_dataframe.email_dataframe import EmailDataFrame
from gmaildr.core.models.email_message import EmailMessage
from gmaildr import Gmail
from tests.core.test_data_factory import create_basic_email_dict, create_test_scenarios, create_multiple_emails


def create_comprehensive_test_data():
    """Create comprehensive test data with multiple senders."""
    # Use factory to create realistic email data with multiple senders
    now = datetime.now()
    
    emails = [
        # Sender 1: John Doe (personal contact)
        create_basic_email_dict(
            message_id='msg1',
            sender_email='john.doe@gmail.com',
            sender_name='John Doe',
            subject='Hello from John',
            timestamp=now - timedelta(days=5),
            sender_local_timestamp=now - timedelta(days=5, hours=2),
            size_bytes=2048,
            labels=['inbox'],
            thread_id='thread1',
            snippet='Hi there!',
            has_attachments=False,
            is_read=True,
            is_important=True,
            text_content='Hello! How are you doing?',
            subject_language='en',
            subject_language_confidence=0.95,
            text_language='en',
            text_language_confidence=0.90,
            has_role_based_email=False,
            is_forwarded=False,
        ),
        create_basic_email_dict(
            message_id='msg2',
            sender_email='john.doe@gmail.com',
            sender_name='John Doe',
            subject='Follow up',
            timestamp=now - timedelta(days=3),
            sender_local_timestamp=now - timedelta(days=3, hours=1),
            size_bytes=1536,
            labels=['inbox'],
            thread_id='thread1',
            snippet='Just checking in',
            has_attachments=False,
            is_read=False,
            is_important=False,
            text_content='Just wanted to follow up on our conversation.',
            subject_language='en',
            subject_language_confidence=0.92,
            text_language='en',
            text_language_confidence=0.88,
            has_role_based_email=False,
            is_forwarded=False,
        ),
        
        # Sender 2: Support Team (role-based)
        create_basic_email_dict(
            message_id='msg3',
            sender_email='support@company.com',
            sender_name='Support Team',
            subject='Your ticket #12345',
            timestamp=now - timedelta(days=2),
            sender_local_timestamp=now - timedelta(days=2, hours=3),
            size_bytes=4096,
            labels=['inbox'],
            thread_id='thread2',
            snippet='We have received your support request',
            has_attachments=True,
            is_read=True,
            is_important=False,
            text_content='Thank you for contacting support. We have received your ticket and will get back to you soon.',
            subject_language='en',
            subject_language_confidence=0.89,
            text_language='en',
            text_language_confidence=0.85,
            has_role_based_email=True,
            is_forwarded=False,
        ),
        create_basic_email_dict(
            message_id='msg4',
            sender_email='support@company.com',
            sender_name='Support Team',
            recipient_email='user@gmail.com',
            recipient_name='User',
            subject='Re: Your ticket #12345',
            timestamp=datetime.now() - timedelta(hours=12),
            sender_local_timestamp=datetime.now() - timedelta(hours=15),
            size_bytes=3072,
            labels=['inbox'],
            thread_id='thread2',
            snippet='Here is the solution to your problem',
            has_attachments=False,
            is_read=False,
            is_important=True,
            text_content='We have resolved your issue. Please try the following steps...',
            subject_language='en',
            subject_language_confidence=0.91,
            text_language='en',
            text_language_confidence=0.87,
            has_role_based_email=True,
            is_forwarded=False,
        ),
        
        # Sender 3: Newsletter (forwarded)
        create_basic_email_dict(
            message_id='msg5',
            sender_email='newsletter@tech.com',
            sender_name='Tech Newsletter',
            subject='Weekly Tech Update',
            timestamp=now - timedelta(hours=6),
            sender_local_timestamp=now - timedelta(hours=9),
            size_bytes=8192,
            labels=['inbox'],
            thread_id='thread3',
            snippet='Latest technology news and updates',
            has_attachments=False,
            is_read=False,
            is_important=False,
            text_content='Here are the latest technology updates for this week...',
            subject_language='en',
            subject_language_confidence=0.94,
            text_language='en',
            text_language_confidence=0.92,
            has_role_based_email=False,
            is_forwarded=True,
        ),
        
        # Sender 4: International contact
        create_basic_email_dict(
            message_id='msg6',
            sender_email='maria@example.es',
            sender_name='María García',
            subject='Hola desde España',
            timestamp=now - timedelta(hours=3),
            sender_local_timestamp=now - timedelta(hours=6),
            size_bytes=1024,
            labels=['inbox'],
            thread_id='thread4',
            snippet='Saludos desde Madrid',
            has_attachments=False,
            is_read=True,
            is_important=False,
            text_content='¡Hola! ¿Cómo estás? Espero que todo esté bien.',
            subject_language='es',
            subject_language_confidence=0.98,
            text_language='es',
            text_language_confidence=0.96,
            has_role_based_email=False,
            is_forwarded=False,
        ),
    ]
    
    # Convert to EmailDataFrame - EmailDataFrame now accepts EmailMessage objects directly
    gmail = Gmail()
    return EmailDataFrame(emails, gmail=gmail)


def test_full_workflow():
    """Test the complete sender statistics workflow."""
    email_df = create_comprehensive_test_data()
    
    # Calculate sender statistics
    sender_stats = aggregate_emails_by_sender(email_df)
    
    # Verify basic structure
    assert isinstance(sender_stats, SenderDataFrame)
    assert len(sender_stats) == 4  # Four unique senders
    assert 'sender_email' in sender_stats.columns
    
        # Verify all expected columns are present
    expected_columns = [
        'sender_email', 'total_emails', 'unique_subjects', 'total_size_bytes', 'mean_email_size_bytes',
        'date_range_days', 'most_active_day', 'most_active_hour', 'weekend_ratio', 'business_hours_ratio',
        'is_role_based_sender', 'forwarded_emails_count', 'forwarded_emails_ratio',
        'unique_recipients', 'recipient_diversity', 'most_common_recipient',
        'mean_subject_length_chars', 'std_subject_length_chars', 'subject_length_variation_coef',
        'unique_subject_ratio', 'domain', 'is_personal_domain', 'name_consistency', 'display_name',
        'name_variations'
    ]
    
    for col in expected_columns:
        assert col in sender_stats.columns, f"Missing column: {col}"


def test_john_doe_statistics():
    """Test statistics for John Doe (personal contact)."""
    email_df = create_comprehensive_test_data()
    sender_stats = aggregate_emails_by_sender(email_df)
    john_stats = sender_stats[sender_stats['sender_email'] == 'john.doe@gmail.com'].iloc[0]
    
    # Basic counts
    assert john_stats['total_emails'] == 2
    assert john_stats['unique_subjects'] == 2
    assert john_stats['total_size_bytes'] == 3584  # 2048 + 1536
    assert john_stats['mean_email_size_bytes'] == 1792  # (2048 + 1536) / 2
    
    # Temporal analysis
    assert john_stats['date_range_days'] >= 1  # At least 1 day difference
    assert john_stats['is_role_based_sender'] == False
    assert john_stats['forwarded_emails_count'] == 0
    assert john_stats['forwarded_emails_ratio'] == 0.0
    
    # Recipient analysis
    assert john_stats['unique_recipients'] == 1
    assert john_stats['most_common_recipient'] == 'user@gmail.com'
    
    # Domain analysis
    assert john_stats['domain'] == 'gmail.com'
    assert john_stats['is_personal_domain'] == True  # Gmail is personal
    
    # Name consistency
    assert john_stats['name_consistency'] == True
    assert john_stats['display_name'] == 'John Doe'
    assert john_stats['name_variations'] == 1


def test_support_team_statistics():
    """Test statistics for Support Team (role-based)."""
    email_df = create_comprehensive_test_data()
    sender_stats = aggregate_emails_by_sender(email_df)
    support_stats = sender_stats[sender_stats['sender_email'] == 'support@company.com'].iloc[0]
    
    # Basic counts
    assert support_stats['total_emails'] == 2
    assert support_stats['unique_subjects'] == 2  # Different subjects
    assert support_stats['is_role_based_sender'] == True
    
    # Content analysis
    assert support_stats['mean_subject_length_chars'] > 0
    assert support_stats['std_subject_length_chars'] >= 0
    assert support_stats['subject_length_cv'] >= 0
    
    # Domain analysis
    assert support_stats['domain'] == 'company.com'
    assert support_stats['is_personal_domain'] == False
    
    # Name consistency
    assert support_stats['name_consistency'] == True
    assert support_stats['display_name'] == 'Support Team'
    assert support_stats['name_variations'] == 1


def test_newsletter_statistics():
    """Test statistics for Newsletter (forwarded)."""
    email_df = create_comprehensive_test_data()
    sender_stats = aggregate_emails_by_sender(email_df)
    newsletter_stats = sender_stats[sender_stats['sender_email'] == 'newsletter@tech.com'].iloc[0]
    
    # Forwarding analysis
    assert newsletter_stats['forwarded_emails_count'] == 1
    assert newsletter_stats['forwarded_emails_ratio'] == 1.0  # All emails forwarded
    
    # Size analysis (newsletter is largest)
    assert newsletter_stats['total_size_bytes'] == 8192
    assert newsletter_stats['mean_email_size_bytes'] == 8192


def test_international_contact_statistics():
    """Test statistics for international contact (Spanish)."""
    email_df = create_comprehensive_test_data()
    sender_stats = aggregate_emails_by_sender(email_df)
    maria_stats = sender_stats[sender_stats['sender_email'] == 'maria@example.es'].iloc[0]
    
    # Language analysis (if implemented)
    if 'subject_primary_language' in sender_stats.columns:
        assert maria_stats['subject_primary_language'] == 'es'
        assert maria_stats['english_subject_ratio'] == 0.0  # No English subjects
    
    # Domain analysis
    assert maria_stats['domain'] == 'example.es'
    assert maria_stats['is_personal_domain'] == False  # example.es is not personal
    
    # Name analysis
    assert maria_stats['name_consistency'] == True
    assert maria_stats['display_name'] == 'María García'


def test_statistical_measures():
    """Test that statistical measures are calculated correctly."""
    email_df = create_comprehensive_test_data()
    sender_stats = aggregate_emails_by_sender(email_df)
    
    # Check that entropy values are reasonable
    for _, row in sender_stats.iterrows():
        if row['total_emails'] > 1:
            # Entropy should be >= 0
            assert row['day_of_week_entropy'] >= 0
            assert row['hour_of_day_entropy'] >= 0
            assert row['subject_length_entropy'] >= 0
            
            # CV should be >= 0
            assert row['subject_length_cv'] >= 0
    
    # Check ratios are between 0 and 1
    for _, row in sender_stats.iterrows():
        assert 0 <= row['weekend_ratio'] <= 1
        assert 0 <= row['business_hours_ratio'] <= 1
        assert 0 <= row['forwarded_emails_ratio'] <= 1
        assert 0 <= row['unique_subject_ratio'] <= 1
        assert 0 <= row['recipient_diversity'] <= 1


def test_keyword_extraction():
    """Test that keywords are extracted correctly."""
    email_df = create_comprehensive_test_data()
    sender_stats = aggregate_emails_by_sender(email_df)
    
    for _, row in sender_stats.iterrows():
        assert isinstance(row['subject_keywords'], list)
        assert len(row['subject_keywords']) <= 5  # Max 5 keywords


def test_dataframe_operations():
    """Test that SenderDataFrame supports standard pandas operations."""
    email_df = create_comprehensive_test_data()
    sender_stats = aggregate_emails_by_sender(email_df)
    
    # Test filtering
    role_based = sender_stats[sender_stats['is_role_based_sender'] == True]
    assert len(role_based) == 1
    assert 'support@company.com' in role_based['sender_email'].tolist()
    
    # Test sorting
    sorted_by_emails = sender_stats.sort_values('total_emails', ascending=False)
    assert len(sorted_by_emails) == 4
    
    # Test grouping
    by_domain = sender_stats.groupby('domain').size()
    assert len(by_domain) >= 1
    
    # Test aggregation
    total_emails = sender_stats['total_emails'].sum()
    assert total_emails == 6  # Total emails across all senders


def test_performance_with_large_dataset():
    """Test performance with larger dataset."""
    # Create larger dataset using factory
    large_emails = []
    for i in range(100):
        email = create_basic_email_dict(
            message_id=f'msg{i}',
            sender_email=f'sender{i % 10}@example.com',  # 10 unique senders
            sender_name=f'Sender {i % 10}',
            subject=f'Email {i}',
            timestamp=datetime.now() - timedelta(days=i),
            sender_local_timestamp=datetime.now() - timedelta(days=i, hours=i % 24),
            size_bytes=1024 + (i * 100),
            labels=['inbox'],
            has_attachments=False,
            is_read=i % 2 == 0,
            is_important=i % 3 == 0,
            text_content=f'This is email number {i}',
            subject_language='en',
            subject_language_confidence=0.9,
            text_language='en',
            text_language_confidence=0.85,
            has_role_based_email=False,
            is_forwarded=False,
        )
        large_emails.append(email)
    
    gmail = Gmail()
    large_df = EmailDataFrame(large_emails, gmail=gmail)
    
    # Should complete without errors
    sender_stats = aggregate_emails_by_sender(large_df)
    assert isinstance(sender_stats, SenderDataFrame)
    assert len(sender_stats) == 10  # 10 unique senders
