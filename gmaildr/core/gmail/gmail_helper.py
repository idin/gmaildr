from typing import Dict, Any
from .label_operator import LabelOperator

class GmailHelper(LabelOperator):
    """
    Gmail helper methods that inherit from LabelOperator.
    
    This class provides helper methods and properties that are useful
    for getting information about the Gmail account and basic operations.
    """
    
    @property
    def email(self) -> str:
        """
        Get the connected Gmail email address.
        
        Returns:
            str: The email address of the authenticated user.
        """
        profile = self.client.get_user_profile()
        return profile.get('emailAddress', 'Unknown') if profile else 'Unknown'
    
    @property
    def total_messages(self) -> int:
        """
        Get total number of messages in the Gmail account.
        
        Returns:
            int: Total number of messages in the account.
        """
        profile = self.client.get_user_profile()
        return profile.get('messagesTotal', 0) if profile else 0
    
    def get_cache_access_stats(self) -> Dict[str, Any]:
        """
        Get cache access statistics.
        
        This method provides a default implementation that returns
        cache statistics indicating cache is not enabled. Subclasses
        can override this to provide actual cache statistics.
        
        Returns:
            Dictionary with cache access statistics.
        """
        return {
            'cache_hits': 0,
            'cache_misses': 0,
            'cache_writes': 0,
            'cache_updates': 0,
            'total_requests': 0,
            'hit_rate_percent': 0.0,
            'cache_enabled': False
        }
