"""
Tests for API and cache access counters.

Tests the tracking of Gmail API calls and cache access statistics.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from gmailwiz.core.gmail_client import GmailClient
from gmailwiz.core.gmail import Gmail


class TestApiCounters:
    """Test API call counters in GmailClient."""
    
    def test_initial_api_stats(self):
        """Test initial API statistics are zero."""
        client = GmailClient()
        stats = client.get_api_stats()
        
        assert stats['total_api_calls'] == 0
        assert stats['text_api_calls'] == 0
        assert stats['general_api_calls'] == 0
        assert stats['last_api_call'] is None
    
    def test_track_general_api_call(self):
        """Test tracking of general API calls."""
        client = GmailClient()
        
        # Track a general API call
        client._track_api_call(is_text_call=False)
        
        stats = client.get_api_stats()
        assert stats['total_api_calls'] == 1
        assert stats['text_api_calls'] == 0
        assert stats['general_api_calls'] == 1
        assert stats['last_api_call'] is not None
    
    def test_track_text_api_call(self):
        """Test tracking of text API calls."""
        client = GmailClient()
        
        # Track a text API call
        client._track_api_call(is_text_call=True)
        
        stats = client.get_api_stats()
        assert stats['total_api_calls'] == 1
        assert stats['text_api_calls'] == 1
        assert stats['general_api_calls'] == 0
        assert stats['last_api_call'] is not None
    
    def test_multiple_api_calls(self):
        """Test tracking of multiple API calls."""
        client = GmailClient()
        
        # Track multiple calls
        client._track_api_call(is_text_call=False)  # General call
        client._track_api_call(is_text_call=True)   # Text call
        client._track_api_call(is_text_call=False)  # General call
        
        stats = client.get_api_stats()
        assert stats['total_api_calls'] == 3
        assert stats['text_api_calls'] == 1
        assert stats['general_api_calls'] == 2
        assert stats['last_api_call'] is not None


class TestCacheCounters:
    """Test cache access counters in EmailCacheManager."""
    
    @pytest.fixture
    def temp_cache_dir(self):
        """Create a temporary cache directory for testing."""
        import tempfile
        import shutil
        from pathlib import Path
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def cache_manager(self, temp_cache_dir):
        """Create a cache manager instance for testing."""
        from gmailwiz.cache import EmailCacheManager
        return EmailCacheManager(cache_dir=temp_cache_dir)
    
    def test_initial_cache_stats(self, cache_manager):
        """Test initial cache statistics are zero."""
        stats = cache_manager.get_cache_access_stats()
        
        assert stats['cache_hits'] == 0
        assert stats['cache_misses'] == 0
        assert stats['cache_writes'] == 0
        assert stats['cache_updates'] == 0
        assert stats['total_requests'] == 0
        assert stats['hit_rate_percent'] == 0.0
        assert stats['cache_enabled'] is True
    
    def test_track_cache_hit(self, cache_manager):
        """Test tracking of cache hits."""
        cache_manager._track_cache_hit()
        cache_manager._track_cache_hit()
        
        stats = cache_manager.get_cache_access_stats()
        assert stats['cache_hits'] == 2
        assert stats['cache_misses'] == 0
        assert stats['total_requests'] == 2
        assert stats['hit_rate_percent'] == 100.0
    
    def test_track_cache_miss(self, cache_manager):
        """Test tracking of cache misses."""
        cache_manager._track_cache_miss()
        cache_manager._track_cache_miss()
        
        stats = cache_manager.get_cache_access_stats()
        assert stats['cache_hits'] == 0
        assert stats['cache_misses'] == 2
        assert stats['total_requests'] == 2
        assert stats['hit_rate_percent'] == 0.0
    
    def test_track_cache_write(self, cache_manager):
        """Test tracking of cache writes."""
        cache_manager._track_cache_write()
        cache_manager._track_cache_write()
        cache_manager._track_cache_write()
        
        stats = cache_manager.get_cache_access_stats()
        assert stats['cache_writes'] == 3
    
    def test_track_cache_update(self, cache_manager):
        """Test tracking of cache updates."""
        cache_manager._track_cache_update()
        
        stats = cache_manager.get_cache_access_stats()
        assert stats['cache_updates'] == 1
    
    def test_mixed_cache_operations(self, cache_manager):
        """Test mixed cache operations."""
        cache_manager._track_cache_hit()
        cache_manager._track_cache_hit()
        cache_manager._track_cache_miss()
        cache_manager._track_cache_write()
        
        stats = cache_manager.get_cache_access_stats()
        assert stats['cache_hits'] == 2
        assert stats['cache_misses'] == 1
        assert stats['cache_writes'] == 1
        assert stats['total_requests'] == 3
        assert stats['hit_rate_percent'] == 66.67  # 2/3 * 100


class TestGmailClassCounters:
    """Test counter integration in Gmail class."""
    
    @pytest.fixture
    def gmail_instance(self):
        """Create a Gmail instance for testing."""
        return Gmail()
    
    def test_gmail_api_stats(self, gmail_instance):
        """Test Gmail class exposes API stats."""
        stats = gmail_instance.get_api_stats()
        
        assert isinstance(stats, dict)
        assert 'total_api_calls' in stats
        assert 'text_api_calls' in stats
        assert 'general_api_calls' in stats
        assert 'last_api_call' in stats
    
    def test_gmail_cache_stats(self, gmail_instance):
        """Test Gmail class exposes cache stats."""
        stats = gmail_instance.get_cache_access_stats()
        
        assert isinstance(stats, dict)
        assert 'cache_hits' in stats
        assert 'cache_misses' in stats
        assert 'cache_writes' in stats
        assert 'cache_updates' in stats
        assert 'total_requests' in stats
        assert 'hit_rate_percent' in stats
        assert 'cache_enabled' in stats
    
    def test_cache_disabled_stats(self):
        """Test cache stats when cache is disabled."""
        gmail = Gmail(enable_cache=False)
        stats = gmail.get_cache_access_stats()
        
        assert stats['cache_enabled'] is False
        assert stats['cache_hits'] == 0
        assert stats['cache_misses'] == 0
        assert stats['total_requests'] == 0
        assert stats['hit_rate_percent'] == 0.0


def test_api_counters_import():
    """Test that API counters can be imported and used."""
    from gmailwiz.core.gmail_client import GmailClient
    from gmailwiz.core.gmail import Gmail
    
    client = GmailClient()
    gmail = Gmail()
    
    # Test that methods exist and are callable
    assert hasattr(client, 'get_api_stats')
    assert hasattr(client, '_track_api_call')
    assert hasattr(gmail, 'get_api_stats')
    assert hasattr(gmail, 'get_cache_access_stats')
    
    # Test that methods return dictionaries
    assert isinstance(client.get_api_stats(), dict)
    assert isinstance(gmail.get_api_stats(), dict)
    assert isinstance(gmail.get_cache_access_stats(), dict)
