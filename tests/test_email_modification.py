"""
Test script for email modification functionality.

This script tests the email modification features by:
1. Getting emails with their current labels
2. Modifying labels on selected emails
3. Retrieving the emails again to verify changes
"""

from gmailwiz import Gmail
import pandas as pd

def test_email_modification():
    """Test email modification functionality."""
    
    # Initialize Gmail client
    gmail = Gmail()
    
    # Get some emails to work with
    print("📧 Retrieving emails...")
    df = gmail.get_emails(days=10, use_batch=True, include_text=False, include_metrics=False)
    
    if df.empty:
        print("❌ No emails found in the last 10 days")
        return
    
    print(f"✅ Found {len(df)} emails")
    
    # Select a few emails for testing (avoid system emails)
    test_emails = df.head(3)  # Test with first 3 emails
    print(f"\n🧪 Testing with {len(test_emails)} emails:")
    
    for idx, email in test_emails.iterrows():
        message_id = email['message_id']
        sender = email['sender_email']
        subject = email['subject'][:50] + "..." if len(email['subject']) > 50 else email['subject']
        
        print(f"\n📬 Email {idx + 1}: {sender} - {subject}")
        print(f"   Message ID: {message_id}")
        
        # Get current labels
        print("   📋 Current labels:", email['labels'])
        
        # Test 1: Mark as read/unread
        print("\n   🔄 Testing read/unread status...")
        original_is_read = email['is_read']
        
        if original_is_read:
            print("   → Marking as unread...")
            success = gmail.client.mark_as_unread(message_id)
            print(f"   ✅ Success: {success}")
        else:
            print("   → Marking as read...")
            success = gmail.client.mark_as_read(message_id)
            print(f"   ✅ Success: {success}")
        
        # Test 2: Star/unstar
        print("   ⭐ Testing star status...")
        success = gmail.client.star_email(message_id)
        print(f"   → Starred email: {success}")
        
        # Wait a moment for changes to propagate
        import time
        time.sleep(1)
        
        # Retrieve the email again to see changes
        print("   🔍 Retrieving updated email...")
        updated_df = gmail.get_emails(
            days=10, 
            use_batch=False,  # Use sequential to get fresh data
            include_text=False, 
            include_metrics=False
        )
        
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
            success = gmail.client.modify_email_labels(
                message_id=message_id,
                add_labels=["IMPORTANT"],
                remove_labels=[]
            )
        print(f"   → Added IMPORTANT label: {success}")
        
        # Wait and retrieve again
        time.sleep(1)
        updated_df2 = gmail.get_emails(
            days=10, 
            use_batch=False,
            include_text=False, 
            include_metrics=False
        )
        
        updated_email2 = updated_df2[updated_df2['message_id'] == message_id]
        if not updated_email2.empty:
            updated_email2 = updated_email2.iloc[0]
            print(f"   📋 Final labels: {updated_email2['labels']}")
            
            if 'IMPORTANT' in updated_email2['labels']:
                print("   ✅ IMPORTANT label was successfully added")
            else:
                print("   ❌ IMPORTANT label was not added")
        
        print("   " + "="*50)

def test_batch_modification():
    """Test batch email modification functionality."""
    
    print("\n" + "="*60)
    print("🧪 TESTING BATCH MODIFICATION")
    print("="*60)
    
    gmail = Gmail()
    
    # Get emails for batch testing
    df = gmail.get_emails(days=10, use_batch=True, include_text=False, include_metrics=False)
    
    if len(df) < 2:
        print("❌ Need at least 2 emails for batch testing")
        return
    
    # Select emails for batch testing
    batch_emails = df.head(2)
    message_ids = batch_emails['message_id'].tolist()
    
    print(f"📧 Testing batch operations on {len(message_ids)} emails")
    
    # Test batch star
    print("\n⭐ Testing batch star...")
    results = gmail.client.batch_star_emails(message_ids=message_ids)
    print(f"✅ Batch star results: {results}")
    
    # Test batch mark as read
    print("\n📖 Testing batch mark as read...")
    results = gmail.client.batch_mark_as_read(message_ids=message_ids)
    print(f"✅ Batch mark as read results: {results}")
    
    # Wait for changes to propagate
    import time
    time.sleep(2)
    
    # Retrieve and verify batch changes
    print("\n🔍 Verifying batch changes...")
    updated_df = gmail.get_emails(days=10, use_batch=False, include_text=False, include_metrics=False)
    
    for message_id in message_ids:
        email = updated_df[updated_df['message_id'] == message_id]
        if not email.empty:
            email = email.iloc[0]
            print(f"   📬 {email['sender_email']}: {email['labels']}")

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
