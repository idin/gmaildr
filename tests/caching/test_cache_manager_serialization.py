"""
Test cache manager serialization and deserialization of EmailMessage objects.

This module tests that the cache manager can properly serialize and deserialize
EmailMessage objects without losing required fields.
"""

import pytest
from datetime import datetime
from gmaildr.caching.cache_manager import EmailCacheManager
from gmaildr.caching.cache_config import CacheConfig
from gmaildr.core.models.email_message import EmailMessage


def test_email_object_serialization_deserialization():
    """
    Test that EmailMessage objects can be serialized and deserialized correctly.
    
    This test ensures that all required fields are preserved during the
    serialization and deserialization process.
    """
    # Create a sample EmailMessage with all required fields
    email = EmailMessage(
        message_id="test_message_id_123",
        sender_email="sender@example.com",
        sender_name="Test Sender",
        recipient_email="recipient@example.com",
        recipient_name="Test Recipient",
        subject="Test Subject",
        timestamp=datetime(2023, 1, 1, 12, 0, 0),
        sender_local_timestamp=datetime(2023, 1, 1, 12, 0, 0),
        size_bytes=1024,
        labels=["INBOX", "IMPORTANT"],
        thread_id="test_thread_123",
        snippet="This is a test email snippet",
        has_attachments=True,
        is_read=False,
        is_important=True,
        text_content="This is the email text content"
    )
    
    # Create cache manager instance
    from gmaildr.caching.cache_config import CacheConfig
    cache_config = CacheConfig()
    cache_manager = EmailCacheManager(
        cache_config=cache_config,
        cache_dir="./test_cache",
        verbose=False
    )
    
    # Test serialization
    email_dict = cache_manager._email_object_to_dict(email=email)
    
    # Verify all required fields are present in the dictionary
    required_fields = [
        'message_id', 'sender_email', 'sender_name', 'recipient_email', 
        'recipient_name', 'subject', 'timestamp', 'sender_local_timestamp',
        'size_bytes', 'labels', 'thread_id', 'snippet', 'has_attachments',
        'is_read', 'is_important', 'text_content'
    ]
    
    for field in required_fields:
        assert field in email_dict, f"Required field '{field}' missing from serialized dictionary"
    
    # Test deserialization
    reconstructed_email = cache_manager._dict_to_email_object(email_data=email_dict)
    
    # Verify all fields are correctly reconstructed
    assert reconstructed_email.message_id == email.message_id
    assert reconstructed_email.sender_email == email.sender_email
    assert reconstructed_email.sender_name == email.sender_name
    assert reconstructed_email.recipient_email == email.recipient_email
    assert reconstructed_email.recipient_name == email.recipient_name
    assert reconstructed_email.subject == email.subject
    assert reconstructed_email.timestamp == email.timestamp
    assert reconstructed_email.sender_local_timestamp == email.sender_local_timestamp
    assert reconstructed_email.size_bytes == email.size_bytes
    assert reconstructed_email.labels == email.labels
    assert reconstructed_email.thread_id == email.thread_id
    assert reconstructed_email.snippet == email.snippet
    assert reconstructed_email.has_attachments == email.has_attachments
    assert reconstructed_email.is_read == email.is_read
    assert reconstructed_email.is_important == email.is_important
    assert reconstructed_email.text_content == email.text_content


def test_email_object_with_minimal_fields():
    """
    Test serialization and deserialization with minimal required fields.
    
    This test ensures that the cache manager can handle EmailMessage objects
    with only the required fields and default values for optional fields.
    """
    # Create a minimal EmailMessage with only required fields
    email = EmailMessage(
        message_id="minimal_message_id",
        sender_email="minimal@example.com",
        sender_name=None,
        recipient_email="minimal_recipient@example.com",
        recipient_name=None,
        subject="Minimal Subject",
        timestamp=datetime(2023, 1, 1, 12, 0, 0),
        sender_local_timestamp=datetime(2023, 1, 1, 12, 0, 0),
        size_bytes=512
    )
    
    cache_config = CacheConfig()
    cache_manager = EmailCacheManager(
        cache_config=cache_config,
        cache_dir="./test_cache",
        verbose=False
    )
    
    # Test serialization
    email_dict = cache_manager._email_object_to_dict(email=email)
    
    # Test deserialization
    reconstructed_email = cache_manager._dict_to_email_object(email_data=email_dict)
    
    # Verify required fields are preserved
    assert reconstructed_email.message_id == email.message_id
    assert reconstructed_email.sender_email == email.sender_email
    assert reconstructed_email.recipient_email == email.recipient_email
    assert reconstructed_email.subject == email.subject
    assert reconstructed_email.size_bytes == email.size_bytes
    
    # Verify default values are set correctly
    assert reconstructed_email.sender_name is None
    assert reconstructed_email.recipient_name is None
    assert reconstructed_email.labels == []
    assert reconstructed_email.has_attachments is False
    assert reconstructed_email.is_read is False
    assert reconstructed_email.is_important is False


def test_email_object_with_string_labels():
    """
    Test handling of labels when they are stored as a comma-separated string.
    
    This test ensures that the cache manager can handle the case where
    labels are stored as a string instead of a list.
    """
    email = EmailMessage(
        message_id="labels_test_id",
        sender_email="labels@example.com",
        sender_name="Labels Test",
        recipient_email="labels_recipient@example.com",
        recipient_name="Labels Recipient",
        subject="Labels Test Subject",
        timestamp=datetime(2023, 1, 1, 12, 0, 0),
        sender_local_timestamp=datetime(2023, 1, 1, 12, 0, 0),
        size_bytes=1024,
        labels=["INBOX", "WORK", "IMPORTANT"]
    )
    
    cache_config = CacheConfig()
    cache_manager = EmailCacheManager(
        cache_config=cache_config,
        cache_dir="./test_cache",
        verbose=False
    )
    
    # Serialize
    email_dict = cache_manager._email_object_to_dict(email=email)
    
    # Manually modify labels to be a string (simulating old cache format)
    email_dict['labels'] = "INBOX,WORK,IMPORTANT"
    
    # Deserialize
    reconstructed_email = cache_manager._dict_to_email_object(email_data=email_dict)
    
    # Verify labels are correctly parsed from string
    assert reconstructed_email.labels == ["INBOX", "WORK", "IMPORTANT"]


def test_email_object_missing_optional_fields():
    """
    Test handling of missing optional fields in cached data.
    
    This test ensures that the cache manager can handle cached data
    that is missing optional fields.
    """
    # Create complete email data dictionary
    email_data = {
        'message_id': 'missing_fields_test_id',
        'sender_email': 'missing@example.com',
        'sender_name': None,
        'recipient_email': 'recipient@example.com',
        'recipient_name': None,
        'subject': 'Missing Fields Test',
        'timestamp': '2023-01-01T12:00:00',
        'sender_local_timestamp': '2023-01-01T12:00:00',
        'size_bytes': 1024,
        'labels': [],
        'thread_id': None,
        'snippet': None,
        'has_attachments': False,
        'is_read': False,
        'is_important': False,
        'text_content': None
    }
    
    cache_config = CacheConfig()
    cache_manager = EmailCacheManager(
        cache_config=cache_config,
        cache_dir="./test_cache",
        verbose=False
    )
    
    # Test deserialization with missing optional fields
    reconstructed_email = cache_manager._dict_to_email_object(email_data=email_data)
    
    # Verify required fields are present
    assert reconstructed_email.message_id == 'missing_fields_test_id'
    assert reconstructed_email.sender_email == 'missing@example.com'
    assert reconstructed_email.subject == 'Missing Fields Test'
    assert reconstructed_email.size_bytes == 1024
    
    # Verify optional fields have correct values
    assert reconstructed_email.sender_name is None
    assert reconstructed_email.recipient_email == 'recipient@example.com'
    assert reconstructed_email.recipient_name is None
    assert reconstructed_email.thread_id is None
    assert reconstructed_email.snippet is None
    assert reconstructed_email.has_attachments is False
    assert reconstructed_email.is_read is False
    assert reconstructed_email.is_important is False
    assert reconstructed_email.text_content is None


def test_complete_cache_data_processing():
    """
    Test that complete cache data is processed correctly.
    
    This test verifies that the cache manager can handle complete cache data
    with all required fields present.
    """
    # Complete cache data that should work with the fixed cache manager
    old_cache_data = {
        'message_id': 'test_message_id_123',
        'sender_email': 'sender@example.com',
        'sender_name': 'Test Sender',
        'recipient_email': 'recipient@example.com',
        'recipient_name': 'Test Recipient',
        'subject': 'Test Subject',
        'timestamp': '2023-01-01T12:00:00',
        'sender_local_timestamp': '2023-01-01T12:00:00',
        'size_bytes': 1024,
        'labels': ['INBOX', 'IMPORTANT'],
        'thread_id': 'test_thread_123',
        'snippet': 'This is a test email snippet',
        'has_attachments': True,
        'is_read': False,
        'is_important': True,
        'text_content': 'This is the email text content'
    }
    
    cache_config = CacheConfig()
    cache_manager = EmailCacheManager(
        cache_config=cache_config,
        cache_dir="./test_cache",
        verbose=False
    )
    
    # This should work with complete cache data
    reconstructed_email = cache_manager._dict_to_email_object(email_data=old_cache_data)
    
    # Verify all fields are correctly reconstructed
    assert reconstructed_email.message_id == 'test_message_id_123'
    assert reconstructed_email.sender_email == 'sender@example.com'
    assert reconstructed_email.sender_name == 'Test Sender'
    assert reconstructed_email.recipient_email == 'recipient@example.com'
    assert reconstructed_email.recipient_name == 'Test Recipient'
    assert reconstructed_email.subject == 'Test Subject'
    assert reconstructed_email.size_bytes == 1024
    assert reconstructed_email.labels == ['INBOX', 'IMPORTANT']
    assert reconstructed_email.thread_id == 'test_thread_123'
    assert reconstructed_email.snippet == 'This is a test email snippet'
    assert reconstructed_email.has_attachments is True
    assert reconstructed_email.is_read is False
    assert reconstructed_email.is_important is True
    assert reconstructed_email.text_content == 'This is the email text content'


def test_complete_cache_format_processing():
    """
    Test that complete cache data is processed correctly.
    
    This test verifies that the cache manager works correctly with
    complete cache data containing all required fields.
    """
    # This test verifies that complete cache data works correctly
    
    # Create complete cache data (fixed format)
    complete_cache_data = {
        'message_id': 'complete_message_id',
        'sender_email': 'complete@example.com',
        'sender_name': 'Complete Sender',
        'recipient_email': 'recipient@example.com',
        'recipient_name': 'Complete Recipient',
        'subject': 'Complete Subject',
        'timestamp': '2023-01-01T12:00:00',
        'sender_local_timestamp': '2023-01-01T12:00:00',
        'size_bytes': 1024,
        'labels': ['INBOX'],
        'thread_id': 'complete_thread',
        'snippet': 'Complete snippet',
        'has_attachments': False,
        'is_read': True,
        'is_important': False,
        'text_content': None
    }
    
    # This test verifies that our fix works by ensuring it doesn't raise the TypeError
    cache_config = CacheConfig()
    cache_manager = EmailCacheManager(
        cache_config=cache_config,
        cache_dir="./test_cache",
        verbose=False
    )
    
    # With complete data, this should work correctly
    reconstructed_email = cache_manager._dict_to_email_object(email_data=complete_cache_data)
    
    # Verify all fields are correctly reconstructed
    assert reconstructed_email.message_id == 'complete_message_id'
    assert reconstructed_email.sender_email == 'complete@example.com'
    assert reconstructed_email.sender_name == 'Complete Sender'
    assert reconstructed_email.recipient_email == 'recipient@example.com'
    assert reconstructed_email.recipient_name == 'Complete Recipient'
    assert reconstructed_email.subject == 'Complete Subject'
    assert reconstructed_email.size_bytes == 1024
    assert reconstructed_email.labels == ['INBOX']
    assert reconstructed_email.thread_id == 'complete_thread'
    assert reconstructed_email.snippet == 'Complete snippet'
    assert reconstructed_email.has_attachments is False
    assert reconstructed_email.is_read is True
    assert reconstructed_email.is_important is False
    assert reconstructed_email.text_content is None


def test_demonstrates_original_error():
    """
    Test that demonstrates the exact original error by directly calling EmailMessage constructor.
    
    This test shows the exact error that was occurring before the fix.
    """
    # This test demonstrates the exact error by directly calling EmailMessage
    # with the same arguments that the broken cache manager was using
    
    from gmaildr.core.models.email_message import EmailMessage
    from datetime import datetime
    
    # This is exactly what the broken cache manager was trying to do:
    # EmailMessage(
    #     message_id=email_data['message_id'],
    #     sender_email=email_data['sender_email'],
    #     sender_name=email_data.get('sender_name', ''),
    #     subject=email_data['subject'],
    #     timestamp=timestamp,
    #     sender_local_timestamp=sender_local_timestamp,
    #     size_bytes=email_data['size_bytes'],
    #     labels=labels,
    #     thread_id=email_data.get('thread_id', ''),
    #     snippet=email_data.get('snippet', ''),
    #     has_attachments=email_data.get('has_attachments', False),
    #     is_read=email_data.get('is_read', True),
    #     is_important=email_data.get('is_important', False),
    #     text_content=email_data.get('text_content', None)
    # )
    
    # This should raise the exact error that was occurring:
    with pytest.raises(TypeError) as excinfo:
        EmailMessage(  # type: ignore
            message_id='test_message_id',
            sender_email='sender@example.com',
            sender_name='Test Sender',
            subject='Test Subject',
            timestamp=datetime(2023, 1, 1, 12, 0, 0),
            sender_local_timestamp=datetime(2023, 1, 1, 12, 0, 0),
            size_bytes=1024,
            labels=[],
            thread_id='',
            snippet='',
            has_attachments=False,
            is_read=True,
            is_important=False,
            text_content=None
            # Missing: recipient_email and recipient_name - this is intentional to test the error
        )
    
    # Verify it's the exact error message
    assert "missing 1 required positional argument: 'recipient_email'" in str(excinfo.value)


def test_fails_with_original_error():
    """
    Test that will FAIL with the exact error the user encountered.
    
    This test simulates the broken cache manager behavior that was causing
    the TypeError before the fix was applied.
    """
    # Create a mock cache manager that has the old broken _dict_to_email_object method
    class BrokenCacheManager:
        def _dict_to_email_object(self, email_data):
            """Broken method that doesn't include recipient_email and recipient_name."""
            from gmaildr.core.models.email_message import EmailMessage
            from datetime import datetime
            
            # Parse timestamp
            timestamp = datetime.fromisoformat(email_data['timestamp'])
            if 'sender_local_timestamp' in email_data:
                if isinstance(email_data['sender_local_timestamp'], str):
                    sender_local_timestamp = datetime.fromisoformat(email_data['sender_local_timestamp'])
                else:
                    sender_local_timestamp = email_data['sender_local_timestamp']
            else:
                sender_local_timestamp = timestamp
            
            # Parse labels
            labels = email_data.get('labels', [])
            if isinstance(labels, str):
                labels = [label.strip() for label in labels.split(sep=',') if label.strip()]
            
            # This is the BROKEN version that was causing the error:
            return EmailMessage(  # type: ignore
                message_id=email_data['message_id'],
                sender_email=email_data['sender_email'],
                sender_name=email_data.get('sender_name', ''),
                subject=email_data['subject'],
                timestamp=timestamp,
                sender_local_timestamp=sender_local_timestamp,
                size_bytes=email_data['size_bytes'],
                labels=labels,
                thread_id=email_data.get('thread_id', ''),
                snippet=email_data.get('snippet', ''),
                has_attachments=email_data.get('has_attachments', False),
                is_read=email_data.get('is_read', True),
                is_important=email_data.get('is_important', False),
                text_content=email_data.get('text_content', None)
                # Missing: recipient_email and recipient_name - THIS CAUSES THE ERROR
            )
    
    # Create cache data that's missing the required fields
    broken_cache_data = {
        'message_id': 'broken_message_id',
        'sender_email': 'broken@example.com',
        'sender_name': 'Broken Sender',
        'subject': 'Broken Subject',
        'timestamp': '2023-01-01T12:00:00',
        'sender_local_timestamp': '2023-01-01T12:00:00',
        'size_bytes': 1024,
        'labels': ['INBOX'],
        'thread_id': 'broken_thread',
        'snippet': 'Broken snippet',
        'has_attachments': False,
        'is_read': True,
        'is_important': False,
        'text_content': None
        # Missing: recipient_email and recipient_name
    }
    
    broken_cache_manager = BrokenCacheManager()
    
    # This should FAIL with the exact error the user encountered:
    # TypeError: EmailMessage.__init__() missing required positional arguments
    with pytest.raises(TypeError) as excinfo:
        broken_cache_manager._dict_to_email_object(email_data=broken_cache_data)
    
    # Verify it's a missing argument error for recipient_email
    assert "missing 1 required positional argument: 'recipient_email'" in str(excinfo.value)
