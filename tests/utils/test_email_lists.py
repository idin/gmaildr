"""
Tests for EmailListManager functionality.

Tests the email list management system including list operations,
email additions/removals, and disk persistence.
"""

import pytest
import tempfile
import shutil
from pathlib import Path

from gmailwiz.utils import EmailListManager


class TestEmailListManager:
    """Test the EmailListManager class."""
    
    @pytest.fixture
    def temp_storage_dir(self):
        """Create a temporary storage directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def list_manager(self, temp_storage_dir):
        """Create an EmailListManager instance for testing."""
        return EmailListManager(storage_dir=str(temp_storage_dir))
    
    def test_initialization(self, temp_storage_dir):
        """Test EmailListManager initialization."""
        manager = EmailListManager(storage_dir=str(temp_storage_dir))
        
        assert manager.storage_dir == temp_storage_dir
        assert manager.lists_file == temp_storage_dir / "lists.json"
        assert manager.email_index_file == temp_storage_dir / "email_index.json"
        assert manager._lists == {}
        assert manager._email_index == {}
    
    def test_create_list(self, list_manager):
        """Test creating a new list."""
        # Create a new list
        success = list_manager.create_list("blacklist")
        assert success is True
        
        # Check that list exists
        assert "blacklist" in list_manager._lists
        assert list_manager._lists["blacklist"] == set()
        
        # Try to create same list again
        success = list_manager.create_list("blacklist")
        assert success is False  # Should fail
    
    def test_delete_list(self, list_manager):
        """Test deleting a list."""
        # Create and then delete a list
        list_manager.create_list("test_list")
        assert "test_list" in list_manager._lists
        
        success = list_manager.delete_list("test_list")
        assert success is True
        assert "test_list" not in list_manager._lists
        
        # Try to delete non-existent list
        success = list_manager.delete_list("non_existent")
        assert success is False
    
    def test_add_email_to_list(self, list_manager):
        """Test adding emails to lists."""
        # Create a list
        list_manager.create_list("friends")
        
        # Add email to list
        success = list_manager.add_email_to_list("friend@example.com", "friends")
        assert success is True
        
        # Check that email is in list
        assert "friend@example.com" in list_manager._lists["friends"]
        assert "friends" in list_manager._email_index["friend@example.com"]
        
        # Test email normalization (lowercase)
        assert list_manager.is_email_in_list("FRIEND@EXAMPLE.COM", "friends") is True
    
    def test_remove_email_from_list(self, list_manager):
        """Test removing emails from lists."""
        # Create list and add email
        list_manager.create_list("test_list")
        list_manager.add_email_to_list("test@example.com", "test_list")
        
        # Remove email
        success = list_manager.remove_email_from_list("test@example.com", "test_list")
        assert success is True
        
        # Check that email is removed
        assert "test@example.com" not in list_manager._lists["test_list"]
        assert "test@example.com" not in list_manager._email_index
    
    def test_multiple_lists_per_email(self, list_manager):
        """Test that an email can belong to multiple lists."""
        # Create multiple lists
        list_manager.create_list("friends")
        list_manager.create_list("family")
        list_manager.create_list("work")
        
        # Add same email to multiple lists
        email = "person@example.com"
        list_manager.add_email_to_list(email, "friends")
        list_manager.add_email_to_list(email, "family")
        list_manager.add_email_to_list(email, "work")
        
        # Check that email is in all lists
        assert list_manager.is_email_in_list(email, "friends") is True
        assert list_manager.is_email_in_list(email, "family") is True
        assert list_manager.is_email_in_list(email, "work") is True
        
        # Check that email index shows all lists
        lists_for_email = list_manager.get_lists_for_email(email)
        assert lists_for_email == {"friends", "family", "work"}
    
    def test_get_emails_in_list(self, list_manager):
        """Test getting all emails in a list."""
        # Create list and add emails
        list_manager.create_list("test_list")
        emails = ["email1@example.com", "email2@example.com", "email3@example.com"]
        
        for email in emails:
            list_manager.add_email_to_list(email, "test_list")
        
        # Get emails in list
        list_emails = list_manager.get_emails_in_list("test_list")
        assert list_emails == set(emails)
    
    def test_get_all_lists(self, list_manager):
        """Test getting all list names."""
        # Create multiple lists
        list_names = ["blacklist", "whitelist", "friends", "family"]
        for name in list_names:
            list_manager.create_list(name)
        
        # Get all lists
        all_lists = list_manager.get_all_lists()
        assert set(all_lists) == set(list_names)
    
    def test_search_emails(self, list_manager):
        """Test email search functionality."""
        # Create list and add emails
        list_manager.create_list("test_list")
        emails = [
            "john.doe@example.com",
            "jane.smith@example.com", 
            "bob.wilson@test.org",
            "alice@company.com"
        ]
        
        for email in emails:
            list_manager.add_email_to_list(email, "test_list")
        
        # Search with wildcard
        results = list_manager.search_emails("*@example.com", "test_list")
        assert len(results) == 2
        assert "john.doe@example.com" in results
        assert "jane.smith@example.com" in results
        
        # Search all emails
        results = list_manager.search_emails("*@*.com")
        assert len(results) == 3  # All .com emails
    
    def test_clear_list(self, list_manager):
        """Test clearing all emails from a list."""
        # Create list and add emails
        list_manager.create_list("test_list")
        emails = ["email1@example.com", "email2@example.com"]
        
        for email in emails:
            list_manager.add_email_to_list(email, "test_list")
        
        # Clear list
        success = list_manager.clear_list("test_list")
        assert success is True
        
        # Check that list is empty
        assert list_manager.get_emails_in_list("test_list") == set()
    
    def test_get_stats(self, list_manager):
        """Test getting list statistics."""
        # Create list and add emails
        list_manager.create_list("test_list")
        emails = ["email1@example.com", "email2@example.com"]
        
        for email in emails:
            list_manager.add_email_to_list(email, "test_list")
        
        # Get list stats
        stats = list_manager.get_list_stats("test_list")
        assert stats is not None
        assert stats["list_name"] == "test_list"
        assert stats["email_count"] == 2
        
        # Get all stats
        all_stats = list_manager.get_all_stats()
        assert "test_list" in all_stats
        assert all_stats["test_list"]["email_count"] == 2
    
    def test_total_counts(self, list_manager):
        """Test total email and list counts."""
        # Create multiple lists with overlapping emails
        list_manager.create_list("list1")
        list_manager.create_list("list2")
        
        list_manager.add_email_to_list("email1@example.com", "list1")
        list_manager.add_email_to_list("email2@example.com", "list1")
        list_manager.add_email_to_list("email2@example.com", "list2")  # Overlap
        list_manager.add_email_to_list("email3@example.com", "list2")
        
        # Check counts
        assert list_manager.get_total_list_count() == 2
        assert list_manager.get_total_email_count() == 3  # Unique emails
    
    def test_persistence(self, temp_storage_dir):
        """Test that data persists across instances."""
        # Create first instance and add data
        manager1 = EmailListManager(storage_dir=str(temp_storage_dir))
        manager1.create_list("test_list")
        manager1.add_email_to_list("test@example.com", "test_list")
        
        # Create second instance and check data
        manager2 = EmailListManager(storage_dir=str(temp_storage_dir))
        assert "test_list" in manager2.get_all_lists()
        assert manager2.is_email_in_list("test@example.com", "test_list") is True


def test_email_list_manager_import():
    """Test that EmailListManager can be imported and used."""
    from gmailwiz.utils import EmailListManager
    
    # Test that class can be instantiated
    manager = EmailListManager()
    
    # Test that methods exist
    assert hasattr(manager, 'create_list')
    assert hasattr(manager, 'add_email_to_list')
    assert hasattr(manager, 'is_email_in_list')
    assert hasattr(manager, 'get_emails_in_list')
    assert hasattr(manager, 'get_lists_for_email')
