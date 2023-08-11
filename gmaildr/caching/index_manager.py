"""
Index management for email caching.

Handles quick lookup indexes for efficient cache operations.
"""

import json
import logging
import fcntl
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)



class EmailIndexManager:
    """
    Manages indexes for quick email lookups.
    
    Maintains indexes for message_id to file path mapping and date-based lookups.
    """
    
    def __init__(self, *, cache_config, verbose: bool):
        """
        Initialize index manager.
        
        Args:
            cache_config: CacheConfig instance.
            verbose: Whether to show detailed cache and processing messages.
        """
        self.config = cache_config
        self.verbose = verbose
        self.message_index_file = self.config.get_index_file_path("message_index")
        self.date_index_file = self.config.get_index_file_path("date_index")
        self._file_locks = {}
    
    def _log_with_verbosity(self, message: str, level: str = "info") -> None:
        """
        Log a message to file and optionally print to console if verbose.
        
        Args:
            message: Message to log.
            level: Log level ('info', 'warning', 'error', 'debug').
        """
        # Log the message to file only
        log_method = getattr(logger, level.lower(), logger.info)
        log_method(message)
        
        # Print to console if verbose
        if self.verbose:
            print(message)
    
    def _get_file_lock(self, file_path: Path):
        """
        Get or create a file lock for the given file.
        
        Args:
            file_path: Path to the file to lock.
            
        Returns:
            File lock object.
        """
        lock_key = str(file_path)
        if lock_key not in self._file_locks:
            self._file_locks[lock_key] = {}
        return self._file_locks[lock_key]
    
    def build_indexes(self) -> bool:
        """
        Build or rebuild all indexes from cache files.
        
        Returns:
            True if successful, False otherwise.
        """
        try:
            self._log_with_verbosity("Building email cache indexes...")
            
            # Clean up any existing lock files first
            self._cleanup_lock_files()
            
            message_index = {}
            date_index = {}
            
            # Scan all cache files
            for date_dir in self.config.emails_dir.iterdir():
                if not date_dir.is_dir():
                    continue
                
                date_str = date_dir.name
                date_index[date_str] = []
                
                for file_path in date_dir.glob("*.json"):
                    message_id = file_path.stem
                    message_index[message_id] = {
                        "file_path": str(file_path),
                        "date": date_str,
                        "last_updated": datetime.now().isoformat()
                    }
                    date_index[date_str].append(message_id)
            
            # Save indexes
            self._save_index(index_file=self.message_index_file, index_data=message_index)
            self._save_index(index_file=self.date_index_file, index_data=date_index)
            
            self._log_with_verbosity(f"Built indexes: {len(message_index)} messages across {len(date_index)} dates")
            return True
            
        except Exception as error:
            self._log_with_verbosity(f"Failed to build indexes: {error}", level="error")
            return False
    
    def _cleanup_lock_files(self) -> None:
        """
        Clean up any existing lock files that might be left over.
        """
        try:
            for lock_file in self.config.metadata_dir.glob("*.lock"):
                try:
                    lock_file.unlink()
                except Exception:
                    pass
        except Exception:
            pass
    
    def get_cached_message_ids(self, start_date: datetime, end_date: datetime) -> Set[str]:
        """
        Get cached message IDs within a date range.
        
        Args:
            start_date: Start date for range.
            end_date: End date for range.
            
        Returns:
            Set of cached message IDs in the date range.
        """
        try:
            date_index = self._load_index(self.date_index_file)
            if not date_index:
                return set()
            
            cached_ids = set()
            current_date = start_date
            
            while current_date <= end_date:
                date_str = current_date.strftime("%Y-%m-%d")
                if date_str in date_index:
                    cached_ids.update(date_index[date_str])
                current_date += timedelta(days=1)
            
            return cached_ids
            
        except Exception as error:
            logger.error(f"Failed to get cached message IDs: {error}")
            return set()
    
    def is_message_cached(self, message_id: str) -> bool:
        """
        Check if a message is cached.
        
        Args:
            message_id: Message ID to check.
            
        Returns:
            True if message is cached, False otherwise.
        """
        try:
            message_index = self._load_index(self.message_index_file)
            if message_index is None:
                return False
            return message_id in message_index
            
        except Exception as error:
            logger.error(f"Failed to check if message {message_id} is cached: {error}")
            return False
    
    def get_message_info(self, message_id: str) -> Optional[Dict[str, Any]]:
        """
        Get cached message information.
        
        Args:
            message_id: Message ID to look up.
            
        Returns:
            Message info if cached, None otherwise.
        """
        try:
            message_index = self._load_index(self.message_index_file)
            if message_index is None:
                return None
            return message_index.get(message_id)
            
        except Exception as error:
            logger.error(f"Failed to get message info for {message_id}: {error}")
            return None
    
    def add_message_to_index(self, message_id: str, date_str: str, file_path: str) -> bool:
        """
        Add a message to the indexes.
        
        Args:
            message_id: Message ID.
            date_str: Date string.
            file_path: Path to cache file.
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            # Update message index
            message_index = self._load_index(self.message_index_file) or {}
            message_index[message_id] = {
                "file_path": file_path,
                "date": date_str,
                "last_updated": datetime.now().isoformat()
            }
            self._save_index(
                index_file=self.message_index_file, 
                index_data=message_index
            )
            
            # Update date index
            date_index = self._load_index(self.date_index_file) or {}
            if date_str not in date_index:
                date_index[date_str] = []
            if message_id not in date_index[date_str]:
                date_index[date_str].append(message_id)
            self._save_index(
                index_file=self.date_index_file, 
                index_data=date_index
            )
            
            return True
            
        except Exception as error:
            logger.error(f"Failed to add message {message_id} to index: {error}")
            return False
    
    def remove_message_from_index(self, message_id: str) -> bool:
        """
        Remove a message from the indexes.
        
        Args:
            message_id: Message ID to remove.
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            # Get message info first
            message_info = self.get_message_info(message_id)
            if not message_info:
                return True  # Already not in index
            
            # Remove from message index
            message_index = self._load_index(self.message_index_file) or {}
            if message_id in message_index:
                del message_index[message_id]
                self._save_index(
                    index_file=self.message_index_file, 
                    index_data=message_index
                )
            
            # Remove from date index
            date_index = self._load_index(self.date_index_file) or {}
            date_str = message_info.get("date")
            if date_str and date_str in date_index:
                if message_id in date_index[date_str]:
                    date_index[date_str].remove(message_id)
                # Remove empty date entries
                if not date_index[date_str]:
                    del date_index[date_str]
                self._save_index(
                    index_file=self.date_index_file, 
                    index_data=date_index
                )
            
            return True
            
        except Exception as error:
            logger.error(f"Failed to remove message {message_id} from index: {error}")
            return False
    
    def get_index_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the indexes.
        
        Returns:
            Dictionary with index statistics.
        """
        try:
            message_index = self._load_index(self.message_index_file) or {}
            date_index = self._load_index(self.date_index_file) or {}
            
            return {
                "total_cached_messages": len(message_index),
                "total_dates": len(date_index),
                "index_last_updated": datetime.now().isoformat(),
                "message_index_size": len(json.dumps(message_index)),
                "date_index_size": len(json.dumps(date_index))
            }
            
        except Exception as error:
            logger.error(f"Failed to get index stats: {error}")
            return {}
    
    def _load_index(self, index_file: Path) -> Optional[Dict[str, Any]]:
        """
        Load an index file with robust error handling.
        
        Args:
            index_file: Path to index file.
            
        Returns:
            Index data if file exists and is valid, None otherwise.
        """
        if not index_file.exists():
            return None
        
        # Use file locking to prevent concurrent access during read
        lock_file = index_file.with_suffix('.lock')
        
        try:
            # Try to acquire a shared lock for reading
            with open(lock_file, 'w') as lock_f:
                fcntl.flock(lock_f.fileno(), fcntl.LOCK_SH)
                
                try:
                    # Read the entire file content first
                    with open(index_file, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                    
                    # Skip empty files
                    if not content:
                        logger.warning(f"Index file {index_file} is empty")
                        return None
                    
                    # Try to parse JSON
                    try:
                        return json.loads(content)
                    except json.JSONDecodeError as json_error:
                        logger.error(f"JSON decode error in {index_file}: {json_error}")
                        
                        # Try to recover by reading only the first valid JSON object
                        try:
                            # Find the first complete JSON object
                            brace_count = 0
                            start_pos = content.find('{')
                            if start_pos == -1:
                                logger.error(f"No JSON object found in {index_file}")
                                return None
                            
                            for i, char in enumerate(content[start_pos:], start_pos):
                                if char == '{':
                                    brace_count += 1
                                elif char == '}':
                                    brace_count -= 1
                                    if brace_count == 0:
                                        # Found complete JSON object
                                        partial_content = content[start_pos:i+1]
                                        return json.loads(partial_content)
                            
                            logger.error(f"Could not find complete JSON object in {index_file}")
                            return None
                            
                        except Exception as recovery_error:
                            logger.error(f"Failed to recover JSON from {index_file}: {recovery_error}")
                            return None
                        
                finally:
                    # Release the lock
                    fcntl.flock(lock_f.fileno(), fcntl.LOCK_UN)
                    
        except Exception as error:
            logger.error(f"Failed to load index {index_file}: {error}")
            return None
        finally:
            # Clean up lock file
            if lock_file.exists():
                try:
                    lock_file.unlink()
                except Exception:
                    pass
    
    def _save_index(self, *, index_file: Path, index_data: Dict[str, Any]) -> bool:
        """
        Save an index file using atomic write to prevent corruption.
        
        Args:
            index_file: Path to index file.
            index_data: Index data to save.
            
        Returns:
            True if successful, False otherwise.
        """
        # Ensure the directory exists
        index_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Use file locking to prevent concurrent access
        lock_file = index_file.with_suffix('.lock')
        
        try:
            # Create lock file and acquire exclusive lock
            with open(lock_file, 'w') as lock_f:
                fcntl.flock(lock_f.fileno(), fcntl.LOCK_EX)
                
                try:
                    # Create temporary file in the same directory
                    temp_file = tempfile.NamedTemporaryFile(
                        mode='w',
                        dir=index_file.parent,
                        prefix=f"{index_file.stem}_",
                        suffix='.tmp',
                        delete=False,
                        encoding='utf-8'
                    )
                    
                    # Write data to temporary file
                    json.dump(index_data, temp_file, indent=2, ensure_ascii=False)
                    temp_file.close()
                    
                    # Atomically move the temporary file to the target location
                    shutil.move(temp_file.name, index_file)
                    
                    return True
                    
                finally:
                    # Release the lock
                    fcntl.flock(lock_f.fileno(), fcntl.LOCK_UN)
                    
        except Exception as error:
            logger.error(f"Failed to save index {index_file}: {error}")
            # Clean up temporary file if it exists
            temp_file_path = Path(temp_file.name) if 'temp_file' in locals() else None
            if temp_file_path and temp_file_path.exists():
                try:
                    temp_file_path.unlink()
                except Exception:
                    pass
            return False
        finally:
            # Clean up lock file
            if lock_file.exists():
                try:
                    lock_file.unlink()
                except Exception:
                    pass
