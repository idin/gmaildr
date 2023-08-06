"""
Test script for email modification functionality.

This script tests the email modification features by:
1. Getting emails with their current labels
2. Modifying labels on selected emails
3. Retrieving the emails again to verify changes
"""

import time
from gmailwiz import Gmail
import pandas as pd

def test_email_modification():
    """Test email modification functionality."""
    
    start_time = time.time()
    
    # Initialize Gmail client
    print("🚀 Initializing Gmail client...")
    init_start = time.time()
    gmail = Gmail()
    init_time = time.time() - init_start
    print(f"   ⏱️  Gmail client initialization: {init_time:.2f}s")
    
    # Get some emails to work with
    print("📧 Retrieving emails...")
    retrieve_start = time.time()
    df = gmail.get_emails(days=1, use_batch=True, include_text=False, include_metrics=False)
    retrieve_time = time.time() - retrieve_start
    print(f"   ⏱️  Email retrieval: {retrieve_time:.2f}s")
    
    if df.empty:
        print("❌ No emails found in the last 10 days")
        return
    
    print(f"✅ Found {len(df)} emails")
    
    # Select a few emails for testing (avoid system emails)
    test_emails = df.head(1)  # Test with just 1 email for speed
    print(f"\n🧪 Testing with {len(test_emails)} email:")
    
    for idx, (_, email) in enumerate(test_emails.iterrows()):
        message_id = str(email['message_id'])
        sender = str(email['sender_email'])
        subject = str(email['subject'])
        subject_display = subject[:50] + "..." if len(subject) > 50 else subject
        
        print(f"\n📬 Email {idx + 1}: {sender} - {subject_display}")
        print(f"   Message ID: {message_id}")
        
        # Get current labels
        print("   📋 Current labels:", email['labels'])
        
        # Test 1: Mark as read/unread
        print("\n   🔄 Testing read/unread status...")
        read_start = time.time()
        original_is_read = bool(email['is_read'])
        
        if original_is_read:
            print("   → Marking as unread...")
            success = gmail.client.mark_as_unread(message_id)
            print(f"   ✅ Success: {success}")
        else:
            print("   → Marking as read...")
            success = gmail.client.mark_as_read(message_id)
            print(f"   ✅ Success: {success}")
        read_time = time.time() - read_start
        print(f"   ⏱️  Read/unread operation: {read_time:.2f}s")
        
        # Test 2: Star/unstar
        print("   ⭐ Testing star status...")
        star_start = time.time()
        success = gmail.client.star_email(message_id)
        star_time = time.time() - star_start
        print(f"   → Starred email: {success}")
        print(f"   ⏱️  Star operation: {star_time:.2f}s")
        
        # Retrieve the email again to see changes
        print("   🔍 Retrieving updated email...")
        verify_start = time.time()
        updated_df = gmail.get_emails(
            days=1, 
            use_batch=True,  # Use batch for speed
            include_text=False, 
            include_metrics=False
        )
        verify_time = time.time() - verify_start
        print(f"   ⏱️  Verification retrieval: {verify_time:.2f}s")
        
        # Find the updated email
        updated_email = updated_df[updated_df['message_id'] == message_id]
        
        if not updated_email.empty:
            updated_email = updated_email.iloc[0]
            print(f"   📋 Updated labels: {updated_email['labels']}")
            print(f"   📖 Is read: {updated_email['is_read']}")
            
            # Check if changes were applied
            if 'STARRED' in updated_email['labels']:
                print("   ✅ Star was successfully added")
            else:
                print("   ❌ Star was not added")
                
            if updated_email['is_read'] != original_is_read:
                print("   ✅ Read status was successfully changed")
            else:
                print("   ❌ Read status was not changed")
        else:
            print("   ❌ Could not retrieve updated email")
        
        # Test 3: Custom label modification
        print("   🏷️ Testing custom label modification...")
        label_start = time.time()
        success = gmail.client.modify_email_labels(
            message_id=message_id,
            add_labels=["IMPORTANT"],
            remove_labels=[]
        )
        label_time = time.time() - label_start
        print(f"   → Added IMPORTANT label: {success}")
        print(f"   ⏱️  Label modification: {label_time:.2f}s")
        
        # Retrieve again to verify label changes
        print("   🔍 Final verification...")
        final_verify_start = time.time()
        time.sleep(0.5)  # Reduced wait time
        updated_df2 = gmail.get_emails(
            days=1, 
            use_batch=True,
            include_text=False, 
            include_metrics=False
        )
        final_verify_time = time.time() - final_verify_start
        print(f"   ⏱️  Final verification: {final_verify_time:.2f}s")
        
        updated_email2 = updated_df2[updated_df2['message_id'] == message_id]
        if not updated_email2.empty:
            updated_email2 = updated_email2.iloc[0]
            print(f"   📋 Final labels: {updated_email2['labels']}")
            
            if 'IMPORTANT' in updated_email2['labels']:
                print("   ✅ IMPORTANT label was successfully added")
            else:
                print("   ❌ IMPORTANT label was not added")
        
        print("   " + "="*50)
    
    total_time = time.time() - start_time
    print(f"\n⏱️  Total test time: {total_time:.2f}s")
    print(f"   Breakdown:")
    print(f"   - Gmail client init: {init_time:.2f}s")
    print(f"   - Email retrieval: {retrieve_time:.2f}s")
    print(f"   - Read/unread operation: {read_time:.2f}s")
    print(f"   - Star operation: {star_time:.2f}s")
    print(f"   - Verification retrieval: {verify_time:.2f}s")
    print(f"   - Label modification: {label_time:.2f}s")
    print(f"   - Final verification: {final_verify_time:.2f}s")

def test_batch_modification():
    """Test batch email modification functionality."""
    
    print("\n" + "="*60)
    print("🧪 TESTING BATCH MODIFICATION")
    print("="*60)
    
    batch_start = time.time()
    
    gmail = Gmail()
    
    # Get emails for batch testing
    print("📧 Getting emails for batch testing...")
    batch_retrieve_start = time.time()
    df = gmail.get_emails(days=3, use_batch=True, include_text=False, include_metrics=False)
    batch_retrieve_time = time.time() - batch_retrieve_start
    print(f"   ⏱️  Batch email retrieval: {batch_retrieve_time:.2f}s")
    
    if len(df) < 2:
        print("❌ Need at least 2 emails for batch testing")
        return
    
    # Select emails for batch testing
    batch_emails = df.head(2)
    message_ids = batch_emails['message_id'].tolist()
    
    print(f"📧 Testing batch operations on {len(message_ids)} emails")
    
    # Test batch star
    print("\n⭐ Testing batch star...")
    batch_star_start = time.time()
    results = gmail.client.batch_star_emails(message_ids=message_ids)
    batch_star_time = time.time() - batch_star_start
    print(f"✅ Batch star results: {results}")
    print(f"   ⏱️  Batch star operation: {batch_star_time:.2f}s")
    
    # Test batch mark as read
    print("\n📖 Testing batch mark as read...")
    batch_read_start = time.time()
    results = gmail.client.batch_mark_as_read(message_ids=message_ids)
    batch_read_time = time.time() - batch_read_start
    print(f"✅ Batch mark as read results: {results}")
    print(f"   ⏱️  Batch read operation: {batch_read_time:.2f}s")
    
    # Retrieve and verify batch changes
    print("\n🔍 Verifying batch changes...")
    batch_verify_start = time.time()
    updated_df = gmail.get_emails(days=1, use_batch=True, include_text=False, include_metrics=False)
    batch_verify_time = time.time() - batch_verify_start
    print(f"   ⏱️  Batch verification: {batch_verify_time:.2f}s")
    
    for message_id in message_ids:
        email = updated_df[updated_df['message_id'] == message_id]
        if not email.empty:
            email = email.iloc[0]
            print(f"   📬 {email['sender_email']}: {email['labels']}")
    
    batch_total_time = time.time() - batch_start
    print(f"\n⏱️  Total batch test time: {batch_total_time:.2f}s")
    print(f"   Breakdown:")
    print(f"   - Batch email retrieval: {batch_retrieve_time:.2f}s")
    print(f"   - Batch star operation: {batch_star_time:.2f}s")
    print(f"   - Batch read operation: {batch_read_time:.2f}s")
    print(f"   - Batch verification: {batch_verify_time:.2f}s")

def test_label_management():
    """Test label creation and management."""
    
    print("\n" + "="*60)
    print("🏷️ TESTING LABEL MANAGEMENT")
    print("="*60)
    
    gmail = Gmail()
    
    # Get current labels
    print("📋 Current labels:")
    labels = gmail.client.get_labels()
    for label in labels[:5]:  # Show first 5 labels
        print(f"   - {label.get('name', 'Unknown')} (ID: {label.get('id', 'Unknown')})")
    
    # Create a test label
    test_label_name = "GmailCleaner_Test"
    print(f"\n➕ Creating test label: {test_label_name}")
    label_id = gmail.client.create_label(test_label_name)
    
    if label_id:
        print(f"✅ Created label with ID: {label_id}")
        
        # Get labels again to verify
        labels_after = gmail.client.get_labels()
        test_label = next((l for l in labels_after if l.get('id') == label_id), None)
        
        if test_label:
            print(f"✅ Label found in list: {test_label.get('name')}")
        else:
            print("❌ Label not found in list")
        
        # Clean up - delete the test label
        print(f"\n🗑️ Deleting test label: {test_label_name}")
        success = gmail.client.delete_label(label_id)
        print(f"✅ Deletion successful: {success}")
    else:
        print("❌ Failed to create test label")

if __name__ == "__main__":
    print("🚀 Starting Email Modification Tests")
    print("="*60)
    
    try:
        # Test individual email modifications
        test_email_modification()
        
        # Test batch modifications
        test_batch_modification()
        
        # Test label management
        test_label_management()
        
        print("\n" + "="*60)
        print("✅ All tests completed!")
        print("="*60)
        
    except Exception as error:
        print(f"\n❌ Test failed with error: {error}")
        import traceback
        traceback.print_exc()
