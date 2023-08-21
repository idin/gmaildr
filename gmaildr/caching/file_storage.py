"""
File storage operations for email caching.

Handles saving, loading, and managing individual email cache files.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)

class EmailFileStorage:
    """
    Handles file operations for cached email data.
    
    Manages saving, loading, and deleting individual email cache files.
    """
    
    def __init__(self, cache_config):
        """
        Initialize file storage.
        
        Args:
            cache_config: CacheConfig instance.
        """
        self.config = cache_config
    
    def save_email(self, email_data: Dict[str, Any], message_id: str, date_str: str) -> bool:
        """
        Save email data to cache file.
        
        Args:
            email_data: Email data to save.
            message_id: Email message ID.
            date_str: Date string in YYYY-MM-DD format.
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            file_path = self.config.get_email_file_path(message_id, date_str)
            
            # Ensure email data has required fields
            if 'message_id' not in email_data:
                email_data['message_id'] = message_id
            
            # Add cache metadata
            if 'metadata' not in email_data:
                email_data['metadata'] = {}
            
            email_data['metadata']['cached_at'] = datetime.now().isoformat()
            email_data['metadata']['file_path'] = str(file_path)
            
            # Save to file
            with open(file_path, mode='w', encoding='utf-8') as f:
                json.dump(email_data, f, indent=2, ensure_ascii=False, default=str)
            
            logger.debug(f"Saved email {message_id} to cache: {file_path}")
            return True
            
        except Exception as error:
            logger.error(f"Failed to save email {message_id} to cache: {error}")
            return False
    
    def load_email(self, message_id: str, date_str: str) -> Optional[Dict[str, Any]]:
        """
        Load email data from cache file.
        
        Args:
            message_id: Email message ID.
            date_str: Date string in YYYY-MM-DD format.
            
        Returns:
            Email data if found, None otherwise.
        """
        try:
            file_path = self.config.get_email_file_path(message_id, date_str)
            
            if not file_path.exists():
                return None
            
            with open(file_path, mode='r', encoding='utf-8') as f:
                email_data = json.load(f)
            
            logger.debug(f"Loaded email {message_id} from cache: {file_path}")
            return email_data
            
        except Exception as error:
            logger.error(f"Failed to load email {message_id} from cache: {error}")
            return None
    
    def delete_email(self, message_id: str, date_str: str) -> bool:
        """
        Delete email cache file.
        
        Args:
            message_id: Email message ID.
            date_str: Date string in YYYY-MM-DD format.
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            file_path = self.config.get_email_file_path(message_id, date_str)
            
            if file_path.exists():
                file_path.unlink()
                logger.debug(f"Deleted email {message_id} from cache: {file_path}")
            
            return True
            
        except Exception as error:
            logger.error(f"Failed to delete email {message_id} from cache: {error}")
            return False
    
    def delete_email_by_id(self, message_id: str) -> bool:
        """
        Delete email cache file by message ID (searches all dates).
        
        Args:
            message_id: Email message ID.
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            # Search for the email across all date directories
            for date_dir in self.config.emails_dir.iterdir():
                if date_dir.is_dir():
                    file_path = date_dir / f"{message_id}.json"
                    if file_path.exists():
                        file_path.unlink()
                        logger.debug(f"Deleted email {message_id} from cache: {file_path}")
                        return True
            
            return False
            
        except Exception as error:
            logger.error(f"Failed to delete email {message_id} from cache: {error}")
            return False
    
    def email_exists(self, message_id: str, date_str: str) -> bool:
        """
        Check if email cache file exists.
        
        Args:
            message_id: Email message ID.
            date_str: Date string in YYYY-MM-DD format.
            
        Returns:
            True if cache file exists, False otherwise.
        """
        file_path = self.config.get_email_file_path(message_id, date_str)
        return file_path.exists()
    
    def list_cached_emails(self, date_str: Optional[str] = None) -> List[str]:
        """
        List all cached email message IDs.
        
        Args:
            date_str: Optional date string to filter by.
            
        Returns:
            List of cached message IDs.
        """
        cached_emails = []
        
        try:
            if date_str:
                # List emails for specific date
                date_dir = self.config.emails_dir / date_str
                if date_dir.exists():
                    for file_path in date_dir.glob("*.json"):
                        message_id = file_path.stem
                        cached_emails.append(message_id)
            else:
                # List all cached emails
                for date_dir in self.config.emails_dir.iterdir():
                    if date_dir.is_dir():
                        for file_path in date_dir.glob("*.json"):
                            message_id = file_path.stem
                            cached_emails.append(message_id)
            
            return cached_emails
            
        except Exception as error:
            logger.error(f"Failed to list cached emails: {error}")
            return []
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get statistics about cached emails.
        
        Returns:
            Dictionary with cache statistics.
        """
        try:
            total_emails = 0
            date_counts = {}
            total_size = 0
            
            for date_dir in self.config.emails_dir.iterdir():
                if date_dir.is_dir():
                    date_str = date_dir.name
                    email_count = len(list(date_dir.glob("*.json")))
                    date_counts[date_str] = email_count
                    total_emails += email_count
                    
                    # Calculate total size
                    for file_path in date_dir.glob("*.json"):
                        total_size += file_path.stat().st_size
            
            return {
                "total_emails": total_emails,
                "date_counts": date_counts,
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2)
            }
            
        except Exception as error:
            logger.error(f"Failed to get cache stats: {error}")
            return {"total_emails": 0, "date_counts": {}, "total_size_bytes": 0, "total_size_mb": 0}
    
    def cleanup_old_emails(self, max_age_days: int) -> int:
        """
        Clean up emails older than specified days.
        
        Args:
            max_age_days: Maximum age in days.
            
        Returns:
            Number of emails deleted.
        """
        try:
            from datetime import datetime, timedelta
            
            cutoff_date = datetime.now() - timedelta(days=max_age_days)
            deleted_count = 0
            
            for date_dir in self.config.emails_dir.iterdir():
                if not date_dir.is_dir():
                    continue
                
                try:
                    date_obj = datetime.strptime(date_dir.name, "%Y-%m-%d")
                    if date_obj < cutoff_date:
                        # Delete entire date directory
                        for file_path in date_dir.glob("*.json"):
                            file_path.unlink()
                            deleted_count += 1
                        
                        # Remove empty directory
                        if not any(date_dir.iterdir()):
                            date_dir.rmdir()
                            
                except ValueError:
                    # Skip directories that don't match date format
                    continue
            
            logger.info(f"Cleaned up {deleted_count} old cached emails")
            return deleted_count
            
        except Exception as error:
            logger.error(f"Failed to cleanup old emails: {error}")
            return 0
