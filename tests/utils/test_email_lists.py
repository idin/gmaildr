"""
Tests for EmailListManager functionality.

Tests the email list management system including list operations,
email additions/removals, and disk persistence.
"""

import pytest
import tempfile
import shutil
from pathlib import Path

from gmaildr.utils import EmailListManager


def test_initialization():
    """Test EmailListManager initialization."""
    temp_dir = tempfile.mkdtemp()
    try:
        manager = EmailListManager(storage_dir=str(temp_dir))
        
        assert str(manager.storage_dir) == str(temp_dir)
        from pathlib import Path
        temp_path = Path(temp_dir)
        assert str(manager.lists_file) == str(temp_path / "lists.json")
        assert str(manager.email_index_file) == str(temp_path / "email_index.json")
        assert manager._lists == {}
        assert manager._email_index == {}
    finally:
        shutil.rmtree(temp_dir)


def test_create_list():
    """Test creating a new list."""
    temp_dir = tempfile.mkdtemp()
    try:
        manager = EmailListManager(storage_dir=str(temp_dir))
        
        # Create a new list
        success = manager.create_list("blacklist")
        assert success is True
        
        # Check that list exists
        assert "blacklist" in manager._lists
        assert manager._lists["blacklist"] == set()
        
        # Try to create same list again
        success = manager.create_list("blacklist")
        assert success is False  # Should fail
    finally:
        shutil.rmtree(temp_dir)


def test_delete_list():
    """Test deleting a list."""
    temp_dir = tempfile.mkdtemp()
    try:
        manager = EmailListManager(storage_dir=str(temp_dir))
        
        # Create and then delete a list
        manager.create_list("test_list")
        assert "test_list" in manager._lists
        
        success = manager.delete_list("test_list")
        assert success is True
        assert "test_list" not in manager._lists
        
        # Try to delete non-existent list
        success = manager.delete_list("non_existent")
        assert success is False
    finally:
        shutil.rmtree(temp_dir)


def test_add_email_to_list():
    """Test adding emails to lists."""
    temp_dir = tempfile.mkdtemp()
    try:
        manager = EmailListManager(storage_dir=str(temp_dir))
        
        # Create a list
        manager.create_list("friends")
        
        # Add email to list
        success = manager.add_email_to_list("friend@example.com", "friends")
        assert success is True
        
        # Check that email is in list
        assert "friend@example.com" in manager._lists["friends"]
        assert "friends" in manager._email_index["friend@example.com"]
        
        # Test email normalization (lowercase)
        assert manager.is_email_in_list("FRIEND@EXAMPLE.COM", "friends") is True
    finally:
        shutil.rmtree(temp_dir)


def test_remove_email_from_list():
    """Test removing emails from lists."""
    temp_dir = tempfile.mkdtemp()
    try:
        manager = EmailListManager(storage_dir=str(temp_dir))
        
        # Create list and add email
        manager.create_list("test_list")
        manager.add_email_to_list("test@example.com", "test_list")
        
        # Remove email
        success = manager.remove_email_from_list("test@example.com", "test_list")
        assert success is True
        
        # Check that email is removed
        assert "test@example.com" not in manager._lists["test_list"]
        assert "test@example.com" not in manager._email_index
    finally:
        shutil.rmtree(temp_dir)


def test_multiple_lists_per_email():
    """Test that an email can belong to multiple lists."""
    temp_dir = tempfile.mkdtemp()
    try:
        manager = EmailListManager(storage_dir=str(temp_dir))
        
        # Create multiple lists
        manager.create_list("friends")
        manager.create_list("family")
        manager.create_list("work")
        
        # Add same email to multiple lists
        email = "person@example.com"
        manager.add_email_to_list(email, "friends")
        manager.add_email_to_list(email, "family")
        manager.add_email_to_list(email, "work")
        
        # Check that email is in all lists
        assert manager.is_email_in_list(email, "friends") is True
        assert manager.is_email_in_list(email, "family") is True
        assert manager.is_email_in_list(email, "work") is True
        
        # Check that email index shows all lists
        lists_for_email = manager.get_lists_for_email(email)
        assert lists_for_email == {"friends", "family", "work"}
    finally:
        shutil.rmtree(temp_dir)


def test_get_emails_in_list():
    """Test getting all emails in a list."""
    temp_dir = tempfile.mkdtemp()
    try:
        manager = EmailListManager(storage_dir=str(temp_dir))
        
        # Create list and add emails
        manager.create_list("test_list")
        emails = ["email1@example.com", "email2@example.com", "email3@example.com"]
        
        for email in emails:
            manager.add_email_to_list(email, "test_list")
        
        # Get emails in list
        list_emails = manager.get_emails_in_list("test_list")
        assert list_emails == set(emails)
    finally:
        shutil.rmtree(temp_dir)


def test_get_all_lists():
    """Test getting all list names."""
    temp_dir = tempfile.mkdtemp()
    try:
        manager = EmailListManager(storage_dir=str(temp_dir))
        
        # Create multiple lists
        list_names = ["blacklist", "whitelist", "friends", "family"]
        for name in list_names:
            manager.create_list(name)
        
        # Get all lists
        all_lists = manager.get_all_lists()
        assert set(all_lists) == set(list_names)
    finally:
        shutil.rmtree(temp_dir)


def test_search_emails():
    """Test email search functionality."""
    temp_dir = tempfile.mkdtemp()
    try:
        manager = EmailListManager(storage_dir=str(temp_dir))
        
        # Create list and add emails
        manager.create_list("test_list")
        emails = [
            "john.doe@example.com",
            "jane.smith@example.com", 
            "bob.wilson@test.org",
            "alice@company.com"
        ]
        
        for email in emails:
            manager.add_email_to_list(email, "test_list")
        
        # Search with wildcard
        results = manager.search_emails("*@example.com", "test_list")
        assert len(results) == 2
        assert "john.doe@example.com" in results
        assert "jane.smith@example.com" in results
        
        # Search all emails
        results = manager.search_emails("*@*.com")
        assert len(results) == 3  # All .com emails
    finally:
        shutil.rmtree(temp_dir)


def test_clear_list():
    """Test clearing all emails from a list."""
    temp_dir = tempfile.mkdtemp()
    try:
        manager = EmailListManager(storage_dir=str(temp_dir))
        
        # Create list and add emails
        manager.create_list("test_list")
        emails = ["email1@example.com", "email2@example.com"]
        
        for email in emails:
            manager.add_email_to_list(email, "test_list")
        
        # Clear list
        success = manager.clear_list("test_list")
        assert success is True
        
        # Check that list is empty
        assert manager.get_emails_in_list("test_list") == set()
    finally:
        shutil.rmtree(temp_dir)


def test_get_stats():
    """Test getting list statistics."""
    temp_dir = tempfile.mkdtemp()
    try:
        manager = EmailListManager(storage_dir=str(temp_dir))
        
        # Create list and add emails
        manager.create_list("test_list")
        emails = ["email1@example.com", "email2@example.com"]
        
        for email in emails:
            manager.add_email_to_list(email, "test_list")
        
        # Get list stats
        stats = manager.get_list_stats("test_list")
        assert stats is not None
        assert stats["list_name"] == "test_list"
        assert stats["email_count"] == 2
        
        # Get all stats
        all_stats = manager.get_all_stats()
        assert "test_list" in all_stats
        assert all_stats["test_list"]["email_count"] == 2
    finally:
        shutil.rmtree(temp_dir)


def test_total_counts():
    """Test total email and list counts."""
    temp_dir = tempfile.mkdtemp()
    try:
        manager = EmailListManager(storage_dir=str(temp_dir))
        
        # Create multiple lists with overlapping emails
        manager.create_list("list1")
        manager.create_list("list2")
        
        manager.add_email_to_list("email1@example.com", "list1")
        manager.add_email_to_list("email2@example.com", "list1")
        manager.add_email_to_list("email2@example.com", "list2")  # Overlap
        manager.add_email_to_list("email3@example.com", "list2")
        
        # Check counts
        assert manager.get_total_list_count() == 2
        assert manager.get_total_email_count() == 3  # Unique emails
    finally:
        shutil.rmtree(temp_dir)


def test_persistence():
    """Test that data persists across instances."""
    temp_dir = tempfile.mkdtemp()
    try:
        # Create first instance and add data
        manager1 = EmailListManager(storage_dir=str(temp_dir))
        manager1.create_list("test_list")
        manager1.add_email_to_list("test@example.com", "test_list")
        
        # Create second instance and check data
        manager2 = EmailListManager(storage_dir=str(temp_dir))
        assert "test_list" in manager2.get_all_lists()
        assert manager2.is_email_in_list("test@example.com", "test_list") is True
    finally:
        shutil.rmtree(temp_dir)


def test_email_list_manager_import():
    """Test that EmailListManager can be imported and used."""
    from gmaildr.utils import EmailListManager
    
    # Test that class can be instantiated
    manager = EmailListManager()
    
    # Test that methods exist
    assert hasattr(manager, 'create_list')
    assert hasattr(manager, 'add_email_to_list')
    assert hasattr(manager, 'is_email_in_list')
    assert hasattr(manager, 'get_emails_in_list')
    assert hasattr(manager, 'get_lists_for_email')
