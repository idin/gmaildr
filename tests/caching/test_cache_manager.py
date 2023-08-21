"""
Tests for the cache manager functionality.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta

from gmaildr.caching import EmailCacheManager, CacheConfig
from gmaildr.core.models.email_message import EmailMessage


def test_cache_manager_initialization():
    """Test cache manager initialization."""
    temp_dir = tempfile.mkdtemp()
    try:
        config = CacheConfig(cache_dir=temp_dir)
        cache_manager = EmailCacheManager(cache_config=config, cache_dir=temp_dir, verbose=False)
        
        assert str(cache_manager.config.cache_dir) == temp_dir
        assert cache_manager.config.enable_cache is True
        assert cache_manager.file_storage is not None
        assert cache_manager.schema_manager is not None
        assert cache_manager.index_manager is not None
    finally:
        shutil.rmtree(temp_dir)


def test_cache_stats_empty():
    """Test cache statistics when cache is empty."""
    temp_dir = tempfile.mkdtemp()
    try:
        config = CacheConfig(cache_dir=temp_dir)
        cache_manager = EmailCacheManager(cache_config=config, cache_dir=temp_dir, verbose=False)
        
        stats = cache_manager.get_cache_stats()
        
        assert isinstance(stats, dict)
        assert 'total_cached_messages' in stats
        assert stats['total_cached_messages'] == 0
    finally:
        shutil.rmtree(temp_dir)


def test_cache_cleanup_empty():
    """Test cache cleanup on empty cache."""
    temp_dir = tempfile.mkdtemp()
    try:
        config = CacheConfig(cache_dir=temp_dir)
        cache_manager = EmailCacheManager(cache_config=config, cache_dir=temp_dir, verbose=False)
        
        result = cache_manager.cleanup_cache()
        assert result == 0  # Returns number of deleted emails
    finally:
        shutil.rmtree(temp_dir)


def test_cache_invalidation():
    """Test cache invalidation."""
    temp_dir = tempfile.mkdtemp()
    try:
        config = CacheConfig(cache_dir=temp_dir)
        cache_manager = EmailCacheManager(cache_config=config, cache_dir=temp_dir, verbose=False)
        
        result = cache_manager.invalidate_cache()
        assert result is True
        
        # Check that cache directories are recreated but empty
        assert cache_manager.config.emails_dir.exists()
        assert cache_manager.config.metadata_dir.exists()
        email_files = list(cache_manager.config.emails_dir.glob('**/*.json'))
        assert len(email_files) == 0
    finally:
        shutil.rmtree(temp_dir)


def test_file_storage_operations():
    """Test file storage operations."""
    temp_dir = tempfile.mkdtemp()
    try:
        config = CacheConfig(cache_dir=temp_dir)
        cache_manager = EmailCacheManager(cache_config=config, cache_dir=temp_dir, verbose=False)
        
        # Test save and load operations
        test_email_data = {
            'message_id': 'test123',
            'sender_email': 'test@example.com',
            'sender_name': 'Test User',
            'subject': 'Test Email',
            'timestamp': datetime.now().isoformat(),
            'size_bytes': 1024,
            'labels': ['INBOX'],
            'thread_id': 'thread123',
            'snippet': 'Test snippet',
            'has_attachments': False,
            'is_read': True,
            'is_important': False
        }
        
        # Test saving
        success = cache_manager.file_storage.save_email(
            email_data=test_email_data,
            message_id='test123',
            date_str='2024-01-01'
        )
        assert success is True
        
        # Test loading
        loaded_data = cache_manager.file_storage.load_email(
            message_id='test123',
            date_str='2024-01-01'
        )
        assert loaded_data is not None
        assert loaded_data['message_id'] == 'test123'
    finally:
        shutil.rmtree(temp_dir)


def test_email_caching_workflow():
    """Test the complete email caching workflow."""
    temp_dir = tempfile.mkdtemp()
    try:
        config = CacheConfig(cache_dir=temp_dir)
        cache_manager = EmailCacheManager(cache_config=config, cache_dir=temp_dir, verbose=False)
        
        # Create sample email
        now = datetime.now()
        sample_email = EmailMessage(
            message_id="test_message_123",
            sender_email="test@example.com",
            sender_name="Test User",
            recipient_email="user@gmail.com",
            recipient_name="User",
            subject="Test Email",
            timestamp=now,
            sender_local_timestamp=now,
            size_bytes=1024,
            labels=["INBOX", "UNREAD"],
            thread_id="test_thread_123",
            snippet="This is a test email snippet",
            has_attachments=False,
            is_read=False,
            is_important=False
        )
        
        # Convert email to dict
        email_dict = {
            'message_id': sample_email.message_id,
            'sender_email': sample_email.sender_email,
            'sender_name': sample_email.sender_name,
            'subject': sample_email.subject,
            'timestamp': sample_email.timestamp.isoformat(),
            'size_bytes': sample_email.size_bytes,
            'labels': sample_email.labels,
            'thread_id': sample_email.thread_id,
            'snippet': sample_email.snippet,
            'has_attachments': sample_email.has_attachments,
            'is_read': sample_email.is_read,
            'is_important': sample_email.is_important
        }
        
        # Test email storage
        date_str = sample_email.timestamp.strftime('%Y-%m-%d')
        success = cache_manager.file_storage.save_email(
            email_data=email_dict,
            message_id=sample_email.message_id,
            date_str=date_str
        )
        assert success is True
        
        # Test email retrieval
        loaded_data = cache_manager.file_storage.load_email(
            message_id=sample_email.message_id,
            date_str=date_str
        )
        assert loaded_data is not None
        assert loaded_data['message_id'] == sample_email.message_id
        
        # Test index addition
        success = cache_manager.index_manager.add_message_to_index(
            message_id=sample_email.message_id,
            date_str=date_str,
            file_path=str(cache_manager.config.get_email_file_path(sample_email.message_id, date_str))
        )
        assert success is True
        
        # Test cache statistics
        stats = cache_manager.get_cache_stats()
        assert stats['total_cached_messages'] == 1
        
        # Test index statistics
        index_stats = cache_manager.index_manager.get_index_stats()
        assert index_stats['total_cached_messages'] == 1
    finally:
        shutil.rmtree(temp_dir)


def test_cache_with_multiple_emails():
    """Test caching multiple emails."""
    temp_dir = tempfile.mkdtemp()
    try:
        config = CacheConfig(cache_dir=temp_dir)
        cache_manager = EmailCacheManager(cache_config=config, cache_dir=temp_dir, verbose=False)
        
        # Create multiple test emails
        emails = []
        for i in range(3):
            now = datetime.now() - timedelta(days=i)
            email = EmailMessage(
                message_id=f"test_message_{i}",
                sender_email=f"test{i}@example.com",
                sender_name=f"Test User {i}",
                recipient_email="user@gmail.com",
                recipient_name="User",
                subject=f"Test Email {i}",
                timestamp=now,
                sender_local_timestamp=now,
                size_bytes=1024 * (i + 1),
                labels=["INBOX"],
                thread_id=f"test_thread_{i}",
                snippet=f"Test snippet {i}",
                has_attachments=False,
                is_read=False,
                is_important=False
            )
            emails.append(email)
        
        # Cache all emails
        for email in emails:
            email_dict = {
                'message_id': email.message_id,
                'sender_email': email.sender_email,
                'sender_name': email.sender_name,
                'subject': email.subject,
                'timestamp': email.timestamp.isoformat(),
                'size_bytes': email.size_bytes,
                'labels': email.labels,
                'thread_id': email.thread_id,
                'snippet': email.snippet,
                'has_attachments': email.has_attachments,
                'is_read': email.is_read,
                'is_important': email.is_important
            }
            
            date_str = email.timestamp.strftime('%Y-%m-%d')
            success = cache_manager.file_storage.save_email(
                email_data=email_dict,
                message_id=email.message_id,
                date_str=date_str
            )
            assert success is True
            
            cache_manager.index_manager.add_message_to_index(
                message_id=email.message_id,
                date_str=date_str,
                file_path=str(cache_manager.config.get_email_file_path(email.message_id, date_str))
            )
        
        # Verify cache statistics
        stats = cache_manager.get_cache_stats()
        assert stats['total_cached_messages'] == 3
        
        # Verify index statistics
        index_stats = cache_manager.index_manager.get_index_stats()
        assert index_stats['total_cached_messages'] == 3
        
        # Test retrieving cached message IDs
        end_date = datetime.now()
        start_date = end_date - timedelta(days=5)
        cached_ids = cache_manager.index_manager.get_cached_message_ids(
            start_date=start_date,
            end_date=end_date
        )
        assert len(cached_ids) == 3
        assert all(f"test_message_{i}" in cached_ids for i in range(3))
    finally:
        shutil.rmtree(temp_dir)
