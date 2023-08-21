"""
Test cache manager serialization and deserialization of EmailMessage objects with None values.

This module tests that the cache manager can properly handle EmailMessage objects
that contain None values for optional fields like sender_name and recipient_name.
"""

from datetime import datetime
from gmaildr.caching.cache_manager import EmailCacheManager
from gmaildr.caching.cache_config import CacheConfig
from gmaildr.core.models.email_message import EmailMessage


def test_email_serialization_with_none_values():
    """
    Test that EmailMessage objects with None values can be serialized and deserialized correctly.
    
    This test ensures that None values for optional fields like sender_name and recipient_name
    are preserved during the serialization and deserialization process.
    """
    # Create a minimal EmailMessage with None values
    email = EmailMessage(
        message_id='minimal_message_id',
        sender_email='minimal@example.com',
        sender_name=None,
        recipient_email='minimal_recipient@example.com',
        recipient_name=None,
        subject='Minimal Subject',
        timestamp=datetime(2023, 1, 1, 12, 0, 0),
        sender_local_timestamp=datetime(2023, 1, 1, 12, 0, 0),
        size_bytes=512
    )

    cache_config = CacheConfig()
    cache_manager = EmailCacheManager(
        cache_config=cache_config,
        cache_dir='./test_cache',
        verbose=False
    )

    # Test serialization
    email_dict = cache_manager._email_object_to_dict(email=email)
    
    # Verify None values are preserved in serialization
    assert email_dict['sender_name'] is None
    assert email_dict['recipient_name'] is None
    assert email_dict['message_id'] == 'minimal_message_id'
    assert email_dict['sender_email'] == 'minimal@example.com'
    assert email_dict['recipient_email'] == 'minimal_recipient@example.com'
    assert email_dict['subject'] == 'Minimal Subject'
    assert email_dict['size_bytes'] == 512

    # Test deserialization
    reconstructed_email = cache_manager._dict_to_email_object(email_data=email_dict)
    
    # Verify None values are preserved in deserialization
    assert reconstructed_email.sender_name is None
    assert reconstructed_email.recipient_name is None
    assert reconstructed_email.message_id == 'minimal_message_id'
    assert reconstructed_email.sender_email == 'minimal@example.com'
    assert reconstructed_email.recipient_email == 'minimal_recipient@example.com'
    assert reconstructed_email.subject == 'Minimal Subject'
    assert reconstructed_email.size_bytes == 512


def test_email_serialization_with_empty_strings():
    """
    Test that EmailMessage objects with empty strings are handled correctly.
    
    This test ensures that empty strings for optional fields are preserved
    during the serialization and deserialization process.
    """
    # Create an EmailMessage with empty strings
    email = EmailMessage(
        message_id='empty_strings_message_id',
        sender_email='empty@example.com',
        sender_name='',
        recipient_email='empty_recipient@example.com',
        recipient_name='',
        subject='Empty Strings Subject',
        timestamp=datetime(2023, 1, 1, 12, 0, 0),
        sender_local_timestamp=datetime(2023, 1, 1, 12, 0, 0),
        size_bytes=256
    )

    cache_config = CacheConfig()
    cache_manager = EmailCacheManager(
        cache_config=cache_config,
        cache_dir='./test_cache',
        verbose=False
    )

    # Test serialization
    email_dict = cache_manager._email_object_to_dict(email=email)
    
    # Verify empty strings are preserved in serialization
    assert email_dict['sender_name'] == ''
    assert email_dict['recipient_name'] == ''
    assert email_dict['message_id'] == 'empty_strings_message_id'

    # Test deserialization
    reconstructed_email = cache_manager._dict_to_email_object(email_data=email_dict)
    
    # Verify empty strings are preserved in deserialization
    assert reconstructed_email.sender_name == ''
    assert reconstructed_email.recipient_name == ''
    assert reconstructed_email.message_id == 'empty_strings_message_id'


def test_email_serialization_with_mixed_values():
    """
    Test that EmailMessage objects with mixed None and string values are handled correctly.
    
    This test ensures that a mix of None values and actual strings for optional fields
    are preserved during the serialization and deserialization process.
    """
    # Create an EmailMessage with mixed None and string values
    email = EmailMessage(
        message_id='mixed_values_message_id',
        sender_email='mixed@example.com',
        sender_name='John Doe',  # Has a value
        recipient_email='mixed_recipient@example.com',
        recipient_name=None,  # Is None
        subject='Mixed Values Subject',
        timestamp=datetime(2023, 1, 1, 12, 0, 0),
        sender_local_timestamp=datetime(2023, 1, 1, 12, 0, 0),
        size_bytes=1024
    )

    cache_config = CacheConfig()
    cache_manager = EmailCacheManager(
        cache_config=cache_config,
        cache_dir='./test_cache',
        verbose=False
    )

    # Test serialization
    email_dict = cache_manager._email_object_to_dict(email=email)
    
    # Verify mixed values are preserved in serialization
    assert email_dict['sender_name'] == 'John Doe'
    assert email_dict['recipient_name'] is None
    assert email_dict['message_id'] == 'mixed_values_message_id'

    # Test deserialization
    reconstructed_email = cache_manager._dict_to_email_object(email_data=email_dict)
    
    # Verify mixed values are preserved in deserialization
    assert reconstructed_email.sender_name == 'John Doe'
    assert reconstructed_email.recipient_name is None
    assert reconstructed_email.message_id == 'mixed_values_message_id'