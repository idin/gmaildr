#!/usr/bin/env python3
"""
Test script to demonstrate the new label functionality.
"""

from gmaildr import Gmail

def test_label_functionality():
    """Test the new label functionality."""
    print("=== TESTING NEW LABEL FUNCTIONALITY ===")
    
    gmail = Gmail()
    
    # Get some emails
    print("1. Getting emails...")
    emails = gmail.get_emails(days=7, max_emails=10)
    
    if emails.empty:
        print("No emails found for testing")
        return
    
    print(f"   Found {len(emails)} emails")
    
    # Test 1: Get all label names from emails
    print("\n2. Getting all label names from emails...")
    label_names = emails.get_label_names()
    print(f"   Label names: {label_names}")
    
    # Test 2: Count emails by label
    print("\n3. Counting emails by label...")
    for label_name in label_names[:3]:  # Test first 3 labels
        count = emails.count_by_label(label_name)
        print(f"   Emails with '{label_name}': {count}")
    
    # Test 3: Filter emails by label
    print("\n4. Filtering emails by label...")
    if label_names:
        test_label = label_names[0]
        filtered_emails = emails.has_label(test_label)
        print(f"   Emails with '{test_label}': {len(filtered_emails)}")
    
    # Test 4: Add a new label
    print("\n5. Adding a new label...")
    test_label_name = "TEST_DEMO_LABEL"
    
    # Get first email
    first_email = emails.iloc[0]
    message_id = first_email['message_id']
    
    # Add label
    result = gmail.add_label(message_id, test_label_name)
    print(f"   Add result: {result}")
    
    # Verify the label was added
    if result is True or (isinstance(result, dict) and result.get(message_id, False)):
        print(f"   ✅ Label '{test_label_name}' added successfully")
        
        # Get the label ID
        label_id = gmail.get_label_id(test_label_name)
        print(f"   Label ID: {label_id}")
        
        # Test filtering by the new label
        updated_emails = gmail.get_emails(days=7, max_emails=50)
        filtered_emails = updated_emails.has_label(test_label_name)
        print(f"   Emails with new label: {len(filtered_emails)}")
        
        if len(filtered_emails) > 0:
            print(f"   ✅ Successfully found emails with the new label!")
        else:
            print(f"   ❌ Could not find emails with the new label")
    else:
        print(f"   ❌ Failed to add label '{test_label_name}'")
    
    # Test 5: Test multiple label filtering
    print("\n6. Testing multiple label filtering...")
    if len(label_names) >= 2:
        # Test has_any_label
        any_label_emails = emails.has_any_label(label_names[:2])
        print(f"   Emails with any of {label_names[:2]}: {len(any_label_emails)}")
        
        # Test has_all_labels (this might be empty if no email has both labels)
        all_label_emails = emails.has_all_labels(label_names[:2])
        print(f"   Emails with all of {label_names[:2]}: {len(all_label_emails)}")
    
    print("\n=== LABEL FUNCTIONALITY TEST COMPLETE ===")

if __name__ == "__main__":
    test_label_functionality()
