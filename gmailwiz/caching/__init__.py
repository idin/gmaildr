"""
Cache module for GmailWiz.

This module contains caching functionality for email data.
"""

from .cache_manager import EmailCacheManager
from .cache_config import CacheConfig
from .file_storage import EmailFileStorage
from .index_manager import EmailIndexManager
from .schema_manager import EmailSchemaManager

__all__ = ['EmailCacheManager', 'CacheConfig', 'EmailFileStorage', 'EmailIndexManager', 'EmailSchemaManager']
