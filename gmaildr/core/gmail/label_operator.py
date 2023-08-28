from typing import Any, Dict, List, Optional

from .email_modifier import EmailModifier


class LabelOperator(EmailModifier):
    """
    Label management operations that inherit from EmailModifier.
    
    This class handles all label-related operations including getting,
    creating, deleting, and managing labels in Gmail.
    """
    
    def get_labels(self) -> List[Dict[str, Any]]:
        """
        Get all available labels in the Gmail account.
        
        Returns:
            List of label dictionaries with label information.
        """
        return self.client.get_labels()
    
    def create_label(self, name: str, label_list_visibility: str = 'labelShow') -> Optional[str]:
        """
        Create a new custom label.
        
        Args:
            name: Name of the label to create
            label_list_visibility: Label list visibility setting
            
        Returns:
            Label ID if created successfully, None otherwise
        """
        return self.client.create_label(name, label_list_visibility)
    
    def delete_label(self, label_id: str) -> bool:
        """
        Delete a custom label.
        
        Args:
            label_id: ID of the label to delete
            
        Returns:
            True if deleted successfully, False otherwise
        """
        return self.client.delete_label(label_id)
    
    def get_label_id(self, label_name: str) -> Optional[str]:
        """
        Get the ID of a label by name.
        
        Args:
            label_name: Name of the label to find
            
        Returns:
            Label ID if found, None otherwise
            
        Example:
            >>> label_operator.get_label_id('INBOX')
            'INBOX'
            >>> label_operator.get_label_id('wiz_trash')
            'Label_123456789'
        """
        labels = self.get_labels()
        for label in labels:
            if label.get('name') == label_name:
                return label.get('id')
        return None
    
    def has_label(self, label_name: str) -> bool:
        """
        Check if a label exists in the Gmail account.
        
        Args:
            label_name: Name of the label to check
            
        Returns:
            True if label exists, False otherwise
            
        Example:
            >>> label_operator.has_label('INBOX')
            True
            >>> label_operator.has_label('wiz_trash')
            False
        """
        return self.get_label_id(label_name) is not None
    
    def get_label_id_or_create(self, label_name: str, label_list_visibility: str = 'labelShow') -> Optional[str]:
        """
        Get the ID of a label by name, creating it if it doesn't exist.
        
        Args:
            label_name: Name of the label to find or create
            label_list_visibility: Label list visibility setting for new labels
            
        Returns:
            Label ID if found or created successfully, None if failed
            
        Example:
            >>> label_operator.get_label_id_or_create('wiz_trash')
            'Label_123456789'
            >>> label_operator.get_label_id_or_create('INBOX')
            'INBOX'
        """
        # First try to get existing label ID
        label_id = self.get_label_id(label_name)
        if label_id:
            return label_id
        
        # If label doesn't exist, create it
        return self.create_label(label_name, label_list_visibility)
    
    def get_label_name(self, label_id: str) -> Optional[str]:
        """
        Get the name of a label by ID.
        
        Args:
            label_id: ID of the label to find
            
        Returns:
            Label name if found, None otherwise
            
        Example:
            >>> label_operator.get_label_name('INBOX')
            'INBOX'
            >>> label_operator.get_label_name('Label_123456789')
            'wiz_trash'
        """
        labels = self.get_labels()
        for label in labels:
            if label.get('id') == label_id:
                return label.get('name')
        return None
    
    def get_label_names_from_ids(self, label_ids: List[str]) -> List[str]:
        """
        Get label names from a list of label IDs.
        
        Args:
            label_ids: List of label IDs to convert to names
            
        Returns:
            List of label names (IDs for system labels, names for custom labels)
            
        Example:
            >>> label_operator.get_label_names_from_ids(['INBOX', 'Label_123456789'])
            ['INBOX', 'wiz_trash']
        """
        label_names = []
        for label_id in label_ids:
            # System labels use their IDs as names
            if label_id in ['INBOX', 'SENT', 'DRAFT', 'SPAM', 'TRASH', 'STARRED', 'UNREAD', 'IMPORTANT']:
                label_names.append(label_id)
            else:
                # For custom labels, get the name
                label_name = self.get_label_name(label_id)
                if label_name:
                    label_names.append(label_name)
                else:
                    # If we can't find the name, use the ID
                    label_names.append(label_id)
        return label_names