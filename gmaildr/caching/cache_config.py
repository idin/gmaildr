"""
Cache configuration and settings for email caching.
"""

import os
from pathlib import Path
from typing import Optional, Union


class CacheConfig:
    """
    Configuration for email caching system.
    
    Manages cache directory paths, settings, and configuration options.
    """
    
    def __init__(
        self, *,
        cache_dir: Optional[Union[str, Path]] = None,
        max_cache_age_days: int = 30,
        schema_version: str = "1.0",
        enable_cache: bool = True
    ):
        """
        Initialize cache configuration.
        
        Args:
            cache_dir: Directory for cache storage. Defaults to 'cache' in project root.
            max_cache_age_days: Maximum age of cached emails in days.
            schema_version: Current schema version for cache validation.
            enable_cache: Whether caching is enabled.
        """
        self.max_cache_age_days = max_cache_age_days
        self.schema_version = schema_version
        self.enable_cache = enable_cache
        
        # Set up cache directory structure
        if cache_dir is None:
            # Default to 'cache' directory relative to current working directory
            cache_dir = "cache"
        
        self.cache_dir = Path(cache_dir)
        self.emails_dir = self.cache_dir / "emails"
        self.metadata_dir = self.cache_dir / "metadata"
        
        # Create cache directories if they don't exist
        self._ensure_cache_directories()
    
    def _ensure_cache_directories(self) -> None:
        """Create cache directories if they don't exist."""
        self.emails_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_dir.mkdir(parents=True, exist_ok=True)
    
    def get_email_file_path(self, message_id: str, date_str: str) -> Path:
        """
        Get the file path for a cached email.
        
        Args:
            message_id: The email message ID.
            date_str: Date string in YYYY-MM-DD format.
            
        Returns:
            Path to the email cache file.
        """
        date_dir = self.emails_dir / date_str
        date_dir.mkdir(exist_ok=True)
        return date_dir / f"{message_id}.json"
    
    def get_index_file_path(self, index_name: str) -> Path:
        """
        Get the file path for an index file.
        
        Args:
            index_name: Name of the index file.
            
        Returns:
            Path to the index file.
        """
        return self.metadata_dir / f"{index_name}.json"
    
    def get_cache_info(self) -> dict:
        """
        Get information about the cache configuration.
        
        Returns:
            Dictionary with cache configuration details.
        """
        return {
            "cache_dir": str(self.cache_dir),
            "emails_dir": str(self.emails_dir),
            "metadata_dir": str(self.metadata_dir),
            "max_cache_age_days": self.max_cache_age_days,
            "schema_version": self.schema_version,
            "enable_cache": self.enable_cache
        }
