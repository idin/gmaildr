from typing import Dict, Any, Optional
from .gmail_helper import GmailHelper

class CachedGmail(GmailHelper):
    """
    Gmail cache operations that inherit from GmailHelper.
    
    This class handles all cache-related operations including cache manager
    initialization and cache management methods.
    """
    
    def __init__(
        self, *, 
        credentials_file: str, 
        token_file: str,
        enable_cache: bool, 
        verbose: bool
    ):
        """
        Initialize GmailCache with cache manager support.
        
        Args:
            credentials_file (str): Path to Google OAuth2 credentials file.
            enable_cache (bool): Whether to enable email caching.
            verbose (bool): Whether to show detailed cache and processing messages.
        """
        # Initialize base class (authentication and client)
        super().__init__(credentials_file=credentials_file, token_file=token_file, verbose=verbose)
        
        # Initialize cache manager if caching is enabled
        self.cache_manager = None
        if enable_cache:
            from ...caching import EmailCacheManager, CacheConfig
            cache_config = CacheConfig()
            self.cache_manager = EmailCacheManager(
                cache_config=cache_config,
                cache_dir="cache",
                verbose=verbose
            )
    
    def get_cache_access_stats(self) -> Dict[str, Any]:
        """
        Get cache access statistics.
        
        Overrides the GmailHelper method to provide actual cache statistics
        when cache manager is available.
        
        Returns:
            Dictionary with cache access statistics.
        """
        if self.cache_manager:
            return self.cache_manager.get_cache_access_stats()
        else:
            return super().get_cache_access_stats()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive cache statistics.
        
        Returns:
            Dictionary with cache statistics.
        """
        if not self.cache_manager:
            return {"error": "Cache not enabled"}
        return self.cache_manager.get_cache_stats()
    
    def cleanup_cache(self, max_age_days: Optional[int] = -1) -> int:
        """
        Clean up old cached emails by deleting emails older than specified days.
        
        This method removes cached email files that are older than the specified
        number of days, helping to manage disk space and keep cache fresh.
        
        Args:
            max_age_days: Maximum age in days before emails are deleted.
                         If None, uses the default from cache configuration.
                         
                         Examples:
                         - max_age_days=7: Delete emails older than 1 week
                         - max_age_days=30: Delete emails older than 1 month
                         - max_age_days=90: Delete emails older than 3 months
            
        Returns:
            Number of emails deleted from cache.
            
        Example:
            >>> gmail_cache.cleanup_cache(max_age_days=30)
            15  # Deleted 15 emails older than 30 days
        """
        if not self.cache_manager:
            return 0
        return self.cache_manager.cleanup_cache(max_age_days)
    
    def invalidate_cache(self) -> bool:
        """
        Invalidate entire cache (delete all cached data).
        
        Returns:
            True if successful, False otherwise.
        """
        if not self.cache_manager:
            return False
        return self.cache_manager.invalidate_cache()
    
    def rebuild_cache_indexes(self) -> bool:
        """
        Rebuild cache indexes.
        
        Returns:
            True if successful, False otherwise.
        """
        if not self.cache_manager:
            return False
        return self.cache_manager.index_manager.build_indexes()
