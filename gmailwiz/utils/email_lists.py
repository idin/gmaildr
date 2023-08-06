"""
Email address list management system.

Provides efficient storage and retrieval of email addresses organized into lists
such as blacklists, whitelists, friend lists, etc. Supports disk persistence
and fast lookups.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Set, List, Optional, Union
from datetime import datetime
import hashlib

logger = logging.getLogger(__name__)


class EmailListManager:
    """
    Manages email address lists with efficient operations and disk persistence.
    
    Supports multiple lists (blacklist, whitelist, friends, etc.) where each
    email can belong to multiple lists. Provides fast lookups and efficient
    disk storage.
    """
    
    def __init__(self, *, storage_dir: Optional[str] = None):
        """
        Initialize email list manager.
        
        Args:
            storage_dir: Directory for storing list data. Defaults to 'email_lists' in project root.
        """
        # Set up storage directory
        if storage_dir is None:
            # Default to 'email_lists' directory in project root
            project_root = Path(__file__).parent.parent.parent
            storage_dir = project_root / "email_lists"
        
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # File paths
        self.lists_file = self.storage_dir / "lists.json"
        self.email_index_file = self.storage_dir / "email_index.json"
        
        # In-memory data structures for fast lookups
        self._lists: Dict[str, Set[str]] = {}  # list_name -> set of emails
        self._email_index: Dict[str, Set[str]] = {}  # email -> set of list names
        
        # Load existing data
        self._load_data()
    
    def _load_data(self) -> None:
        """Load list data from disk."""
        try:
            # Load lists
            if self.lists_file.exists():
                with open(self.lists_file, 'r', encoding='utf-8') as f:
                    lists_data = json.load(f)
                    self._lists = {name: set(emails) for name, emails in lists_data.items()}
            
            # Load email index
            if self.email_index_file.exists():
                with open(self.email_index_file, 'r', encoding='utf-8') as f:
                    index_data = json.load(f)
                    self._email_index = {email: set(lists) for email, lists in index_data.items()}
            
            # Rebuild email index if it's missing or inconsistent
            if not self._email_index:
                self._rebuild_email_index()
                
        except Exception as error:
            logger.error(f"Failed to load email list data: {error}")
            self._lists = {}
            self._email_index = {}
    
    def _save_data(self) -> None:
        """Save list data to disk."""
        try:
            # Save lists
            lists_data = {name: list(emails) for name, emails in self._lists.items()}
            with open(self.lists_file, 'w', encoding='utf-8') as f:
                json.dump(lists_data, f, indent=2, ensure_ascii=False)
            
            # Save email index
            index_data = {email: list(lists) for email, lists in self._email_index.items()}
            with open(self.email_index_file, 'w', encoding='utf-8') as f:
                json.dump(index_data, f, indent=2, ensure_ascii=False)
                
        except Exception as error:
            logger.error(f"Failed to save email list data: {error}")
    
    def _rebuild_email_index(self) -> None:
        """Rebuild email index from lists data."""
        self._email_index = {}
        for list_name, emails in self._lists.items():
            for email in emails:
                if email not in self._email_index:
                    self._email_index[email] = set()
                self._email_index[email].add(list_name)
    
    def create_list(self, list_name: str) -> bool:
        """
        Create a new email list.
        
        Args:
            list_name: Name of the list to create.
            
        Returns:
            True if created successfully, False if list already exists.
        """
        if list_name in self._lists:
            logger.warning(f"List '{list_name}' already exists")
            return False
        
        self._lists[list_name] = set()
        self._save_data()
        logger.info(f"Created email list: {list_name}")
        return True
    
    def delete_list(self, list_name: str) -> bool:
        """
        Delete an email list and remove all emails from it.
        
        Args:
            list_name: Name of the list to delete.
            
        Returns:
            True if deleted successfully, False if list doesn't exist.
        """
        if list_name not in self._lists:
            logger.warning(f"List '{list_name}' does not exist")
            return False
        
        # Remove list from email index
        emails_to_remove = self._lists[list_name]
        for email in emails_to_remove:
            if email in self._email_index:
                self._email_index[email].discard(list_name)
                # Remove email from index if it's not in any lists
                if not self._email_index[email]:
                    del self._email_index[email]
        
        # Remove list
        del self._lists[list_name]
        self._save_data()
        logger.info(f"Deleted email list: {list_name}")
        return True
    
    def add_email_to_list(self, email: str, list_name: str) -> bool:
        """
        Add an email to a list.
        
        Args:
            email: Email address to add.
            list_name: Name of the list to add to.
            
        Returns:
            True if added successfully, False if list doesn't exist.
        """
        if list_name not in self._lists:
            logger.warning(f"List '{list_name}' does not exist")
            return False
        
        # Normalize email (lowercase)
        email = email.lower().strip()
        
        # Add to list
        self._lists[list_name].add(email)
        
        # Update email index
        if email not in self._email_index:
            self._email_index[email] = set()
        self._email_index[email].add(list_name)
        
        self._save_data()
        logger.debug(f"Added {email} to list: {list_name}")
        return True
    
    def remove_email_from_list(self, email: str, list_name: str) -> bool:
        """
        Remove an email from a list.
        
        Args:
            email: Email address to remove.
            list_name: Name of the list to remove from.
            
        Returns:
            True if removed successfully, False if email not in list.
        """
        if list_name not in self._lists:
            logger.warning(f"List '{list_name}' does not exist")
            return False
        
        # Normalize email
        email = email.lower().strip()
        
        # Remove from list
        if email not in self._lists[list_name]:
            logger.warning(f"Email {email} not in list {list_name}")
            return False
        
        self._lists[list_name].discard(email)
        
        # Update email index
        if email in self._email_index:
            self._email_index[email].discard(list_name)
            # Remove email from index if it's not in any lists
            if not self._email_index[email]:
                del self._email_index[email]
        
        self._save_data()
        logger.debug(f"Removed {email} from list: {list_name}")
        return True
    
    def add_emails_to_list(self, emails: List[str], list_name: str) -> Dict[str, bool]:
        """
        Add multiple emails to a list.
        
        Args:
            emails: List of email addresses to add.
            list_name: Name of the list to add to.
            
        Returns:
            Dictionary mapping emails to success status.
        """
        results = {}
        for email in emails:
            results[email] = self.add_email_to_list(email, list_name)
        return results
    
    def remove_emails_from_list(self, emails: List[str], list_name: str) -> Dict[str, bool]:
        """
        Remove multiple emails from a list.
        
        Args:
            emails: List of email addresses to remove.
            list_name: Name of the list to remove from.
            
        Returns:
            Dictionary mapping emails to success status.
        """
        results = {}
        for email in emails:
            results[email] = self.remove_email_from_list(email, list_name)
        return results
    
    def is_email_in_list(self, email: str, list_name: str) -> bool:
        """
        Check if an email is in a specific list.
        
        Args:
            email: Email address to check.
            list_name: Name of the list to check.
            
        Returns:
            True if email is in the list, False otherwise.
        """
        email = email.lower().strip()
        return list_name in self._lists and email in self._lists[list_name]
    
    def get_lists_for_email(self, email: str) -> Set[str]:
        """
        Get all lists that contain an email.
        
        Args:
            email: Email address to check.
            
        Returns:
            Set of list names containing the email.
        """
        email = email.lower().strip()
        return self._email_index.get(email, set()).copy()
    
    def get_emails_in_list(self, list_name: str) -> Set[str]:
        """
        Get all emails in a specific list.
        
        Args:
            list_name: Name of the list.
            
        Returns:
            Set of email addresses in the list.
        """
        return self._lists.get(list_name, set()).copy()
    
    def get_all_lists(self) -> List[str]:
        """
        Get all list names.
        
        Returns:
            List of all list names.
        """
        return list(self._lists.keys())
    
    def get_list_stats(self, list_name: str) -> Optional[Dict[str, any]]:
        """
        Get statistics for a specific list.
        
        Args:
            list_name: Name of the list.
            
        Returns:
            Dictionary with list statistics or None if list doesn't exist.
        """
        if list_name not in self._lists:
            return None
        
        emails = self._lists[list_name]
        return {
            'list_name': list_name,
            'email_count': len(emails),
            'created_at': self._get_list_creation_time(list_name),
            'last_modified': self._get_list_modification_time(list_name)
        }
    
    def get_all_stats(self) -> Dict[str, Dict[str, any]]:
        """
        Get statistics for all lists.
        
        Returns:
            Dictionary mapping list names to their statistics.
        """
        stats = {}
        for list_name in self._lists:
            stats[list_name] = self.get_list_stats(list_name)
        return stats
    
    def search_emails(self, pattern: str, list_name: Optional[str] = None) -> List[str]:
        """
        Search for emails matching a pattern.
        
        Args:
            pattern: Search pattern (supports wildcards).
            list_name: Optional list name to search within.
            
        Returns:
            List of matching email addresses.
        """
        import re
        
        # Convert wildcard pattern to regex
        regex_pattern = pattern.replace('*', '.*').replace('?', '.')
        regex = re.compile(regex_pattern, re.IGNORECASE)
        
        matching_emails = []
        
        if list_name:
            # Search within specific list
            if list_name in self._lists:
                for email in self._lists[list_name]:
                    if regex.search(email):
                        matching_emails.append(email)
        else:
            # Search all emails
            for email in self._email_index:
                if regex.search(email):
                    matching_emails.append(email)
        
        return sorted(matching_emails)
    
    def export_list(self, list_name: str, format: str = 'json') -> Optional[str]:
        """
        Export a list to a file.
        
        Args:
            list_name: Name of the list to export.
            format: Export format ('json', 'txt', 'csv').
            
        Returns:
            Path to exported file or None if failed.
        """
        if list_name not in self._lists:
            return None
        
        emails = sorted(self._lists[list_name])
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if format == 'json':
            file_path = self.storage_dir / f"{list_name}_{timestamp}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'list_name': list_name,
                    'exported_at': datetime.now().isoformat(),
                    'email_count': len(emails),
                    'emails': emails
                }, f, indent=2, ensure_ascii=False)
        
        elif format == 'txt':
            file_path = self.storage_dir / f"{list_name}_{timestamp}.txt"
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"# Email List: {list_name}\n")
                f.write(f"# Exported: {datetime.now().isoformat()}\n")
                f.write(f"# Count: {len(emails)}\n\n")
                for email in emails:
                    f.write(f"{email}\n")
        
        elif format == 'csv':
            file_path = self.storage_dir / f"{list_name}_{timestamp}.csv"
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("email,list_name,exported_at\n")
                for email in emails:
                    f.write(f"{email},{list_name},{datetime.now().isoformat()}\n")
        
        else:
            logger.error(f"Unsupported export format: {format}")
            return None
        
        logger.info(f"Exported list '{list_name}' to {file_path}")
        return str(file_path)
    
    def import_list(self, file_path: str, list_name: Optional[str] = None) -> bool:
        """
        Import emails from a file into a list.
        
        Args:
            file_path: Path to the file to import from.
            list_name: Name of the list to import to (uses filename if None).
            
        Returns:
            True if import was successful.
        """
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                logger.error(f"Import file not found: {file_path}")
                return False
            
            # Determine list name
            if list_name is None:
                list_name = file_path.stem
            
            # Create list if it doesn't exist
            if list_name not in self._lists:
                self.create_list(list_name)
            
            emails = []
            
            if file_path.suffix.lower() == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict) and 'emails' in data:
                        emails = data['emails']
                    elif isinstance(data, list):
                        emails = data
            
            elif file_path.suffix.lower() in ['.txt', '.csv']:
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '@' in line:
                            emails.append(line)
            
            else:
                logger.error(f"Unsupported import format: {file_path.suffix}")
                return False
            
            # Add emails to list
            results = self.add_emails_to_list(emails, list_name)
            success_count = sum(1 for success in results.values() if success)
            
            logger.info(f"Imported {success_count}/{len(emails)} emails to list '{list_name}'")
            return success_count > 0
            
        except Exception as error:
            logger.error(f"Failed to import list: {error}")
            return False
    
    def _get_list_creation_time(self, list_name: str) -> Optional[str]:
        """Get creation time for a list (placeholder for future implementation)."""
        # This could be enhanced to store actual creation times
        return None
    
    def _get_list_modification_time(self, list_name: str) -> Optional[str]:
        """Get last modification time for a list (placeholder for future implementation)."""
        # This could be enhanced to store actual modification times
        return None
    
    def clear_list(self, list_name: str) -> bool:
        """
        Clear all emails from a list.
        
        Args:
            list_name: Name of the list to clear.
            
        Returns:
            True if cleared successfully.
        """
        if list_name not in self._lists:
            return False
        
        # Remove all emails from the list
        emails_to_remove = self._lists[list_name].copy()
        for email in emails_to_remove:
            self.remove_email_from_list(email, list_name)
        
        logger.info(f"Cleared list: {list_name}")
        return True
    
    def get_total_email_count(self) -> int:
        """
        Get total number of unique emails across all lists.
        
        Returns:
            Total number of unique emails.
        """
        return len(self._email_index)
    
    def get_total_list_count(self) -> int:
        """
        Get total number of lists.
        
        Returns:
            Total number of lists.
        """
        return len(self._lists)
