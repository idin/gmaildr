"""
Schema management for email caching.

Handles schema versioning, field updates, and intelligent merging of cached data.
"""

import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime

class EmailSchemaManager:
    """
    Manages email schema versioning and field updates.
    
    Handles schema changes, field additions/removals, and intelligent merging
    of cached email data with fresh API data.
    """
    
    def __init__(self, schema_version: str = "1.0"):
        """
        Initialize schema manager.
        
        Args:
            schema_version: Current schema version.
        """
        self.schema_version = schema_version
        self.required_fields = [
            'message_id', 'sender_email', 'subject', 'timestamp',
            'labels', 'size_bytes', 'has_attachments'
        ]
    
    def calculate_fields_hash(self, email_data: Dict[str, Any]) -> str:
        """
        Calculate hash of field names for change detection.
        
        Args:
            email_data: Email data dictionary.
            
        Returns:
            Hash string of field names.
        """
        field_names = sorted(email_data.keys())
        field_string = ','.join(field_names)
        return hashlib.md5(field_string.encode(encoding='utf-8')).hexdigest()
    
    def has_schema_changes(self, *, cached_email: Dict[str, Any], fresh_email: Dict[str, Any]) -> bool:
        """
        Check if there are schema changes between cached and fresh email.
        
        Args:
            cached_email: Cached email data.
            fresh_email: Fresh email data from API.
            
        Returns:
            True if schema has changed, False otherwise.
        """
        cached_hash = self.calculate_fields_hash(cached_email)
        fresh_hash = self.calculate_fields_hash(fresh_email)
        
        return cached_hash != fresh_hash
    
    def is_schema_valid(self, email_data: Dict[str, Any]) -> bool:
        """
        Check if email data has valid schema.
        
        Args:
            email_data: Email data to validate.
            
        Returns:
            True if schema is valid, False otherwise.
        """
        # Check for required fields
        for field in self.required_fields:
            if field not in email_data:
                return False
        
        # Check for metadata
        if 'metadata' not in email_data:
            return False
        
        return True
    
    def merge_emails(
        self, *,
        cached_email: Dict[str, Any], 
        fresh_email: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Intelligently merge cached email with fresh email data.
        
        Args:
            cached_email: Cached email data.
            fresh_email: Fresh email data from API.
            
        Returns:
            Merged email data.
        """
        # If schema has changed, use fresh data
        if self.has_schema_changes(cached_email=cached_email, fresh_email=fresh_email):
            return self._add_cache_metadata(email_data=fresh_email)
        
        # Start with cached data
        merged_email = cached_email.copy()
        
        # Update fields that might have changed
        updateable_fields = [
            'labels', 'is_read', 'is_important', 'has_attachments',
            'size_bytes', 'snippet'
        ]
        
        for field in updateable_fields:
            if field in fresh_email and field in cached_email:
                if cached_email[field] != fresh_email[field]:
                    merged_email[field] = fresh_email[field]
            elif field in fresh_email:
                # New field
                merged_email[field] = fresh_email[field]
        
        # Always update text content if available
        if 'text_content' in fresh_email:
            merged_email['text_content'] = fresh_email['text_content']
        
        # Update cache metadata
        merged_email['metadata']['last_updated'] = datetime.now().isoformat()
        merged_email['metadata']['schema_version'] = self.schema_version
        
        return merged_email
    
    def _add_cache_metadata(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add cache metadata to email data.
        
        Args:
            email_data: Email data to add metadata to.
            
        Returns:
            Email data with cache metadata.
        """
        email_data['metadata'] = {
            'cached_at': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat(),
            'schema_version': self.schema_version,
            'fields_hash': self.calculate_fields_hash(email_data)
        }
        
        return email_data
    
    def get_missing_fields(self, email_data: Dict[str, Any]) -> List[str]:
        """
        Get list of missing required fields.
        
        Args:
            email_data: Email data to check.
            
        Returns:
            List of missing required field names.
        """
        missing_fields = []
        for field in self.required_fields:
            if field not in email_data:
                missing_fields.append(field)
        
        return missing_fields
    
    def upgrade_schema(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Upgrade email data to current schema version.
        
        Args:
            email_data: Email data to upgrade.
            
        Returns:
            Upgraded email data.
        """
        # Add default values for missing fields
        defaults = {
            'sender_name': '',
            'thread_id': '',
            'snippet': '',
            'has_attachments': False,
            'is_read': True,
            'is_important': False
        }
        
        for field, default_value in defaults.items():
            if field not in email_data:
                email_data[field] = default_value
        
        # Ensure metadata exists
        if 'metadata' not in email_data:
            email_data['metadata'] = {}
        
        # Update metadata
        email_data['metadata']['schema_version'] = self.schema_version
        email_data['metadata']['upgraded_at'] = datetime.now().isoformat()
        
        return email_data
