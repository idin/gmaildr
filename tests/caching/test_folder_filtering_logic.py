"""
Test folder filtering logic to identify issues with in_folder parameter.

This test checks if the in_folder parameter correctly filters emails
and if there are any issues with the folder detection logic.
"""

import pytest
from gmaildr import Gmail
from gmaildr.test_utils import get_emails


def test_folder_filtering_accuracy():
    """Test that folder filtering returns emails from the correct folder."""
    gmail = Gmail()
    
    print("🔍 Testing folder filtering accuracy...")
    
    # Test inbox filtering
    print("\n📥 Testing inbox filtering...")
    inbox_emails = gmail.get_emails(in_folder='inbox', days=30, max_emails=10)
    
    if not inbox_emails.empty:
        print(f"Found {len(inbox_emails)} emails with in_folder='inbox'")
        
        # Check what folders these emails are actually in
        folder_counts = inbox_emails['in_folder'].value_counts()
        print(f"Actual folders of 'inbox' emails: {dict(folder_counts)}")
        
        # Check labels of emails that claim to be inbox but aren't
        non_inbox_emails = inbox_emails[inbox_emails['in_folder'] != 'inbox']
        if not non_inbox_emails.empty:
            print(f"⚠️ FOLDER FILTERING BUG: {len(non_inbox_emails)} emails returned by in_folder='inbox' are not actually in inbox!")
            
            for i, (_, email) in enumerate(non_inbox_emails.iterrows()):
                if i < 3:  # Show first 3 examples
                    labels = email.get('labels', [])
                    folder = email.get('in_folder', 'unknown')
                    print(f"  - Email {email['message_id']}: actual_folder={folder}, labels={labels}")
            
            # This is a bug in the folder filtering logic
            assert False, f"Folder filtering bug: {len(non_inbox_emails)} emails returned by in_folder='inbox' are not in inbox"
        else:
            print("✅ All emails returned by in_folder='inbox' are actually in inbox")
    else:
        print("No inbox emails found")
    
    # Test trash filtering
    print("\n🗑️ Testing trash filtering...")
    trash_emails = gmail.get_emails(in_folder='trash', days=30, max_emails=10)
    
    if not trash_emails.empty:
        print(f"Found {len(trash_emails)} emails with in_folder='trash'")
        
        folder_counts = trash_emails['in_folder'].value_counts()
        print(f"Actual folders of 'trash' emails: {dict(folder_counts)}")
        
        non_trash_emails = trash_emails[trash_emails['in_folder'] != 'trash']
        if not non_trash_emails.empty:
            print(f"⚠️ FOLDER FILTERING BUG: {len(non_trash_emails)} emails returned by in_folder='trash' are not actually in trash!")
            assert False, f"Folder filtering bug: {len(non_trash_emails)} emails returned by in_folder='trash' are not in trash"
        else:
            print("✅ All emails returned by in_folder='trash' are actually in trash")
    else:
        print("No trash emails found")
    
    # Test archive filtering
    print("\n📦 Testing archive filtering...")
    archive_emails = gmail.get_emails(in_folder='archive', days=30, max_emails=10)
    
    if not archive_emails.empty:
        print(f"Found {len(archive_emails)} emails with in_folder='archive'")
        
        folder_counts = archive_emails['in_folder'].value_counts()
        print(f"Actual folders of 'archive' emails: {dict(folder_counts)}")
        
        non_archive_emails = archive_emails[archive_emails['in_folder'] != 'archive']
        if not non_archive_emails.empty:
            print(f"⚠️ FOLDER FILTERING BUG: {len(non_archive_emails)} emails returned by in_folder='archive' are not actually in archive!")
            assert False, f"Folder filtering bug: {len(non_archive_emails)} emails returned by in_folder='archive' are not in archive"
        else:
            print("✅ All emails returned by in_folder='archive' are actually in archive")
    else:
        print("No archive emails found")
    
    print("\n✅ Folder filtering accuracy test completed")


def test_folder_detection_logic():
    """Test the folder detection logic by examining email labels."""
    gmail = Gmail()
    
    print("🔍 Testing folder detection logic...")
    
    # Get a sample of emails from different folders
    all_emails = gmail.get_emails(days=30, max_emails=50)
    
    if all_emails.empty:
        pytest.skip("No emails found for testing")
    
    print(f"📧 Analyzing {len(all_emails)} emails...")
    
    # Group emails by detected folder
    folder_counts = all_emails['in_folder'].value_counts()
    print(f"Folder distribution: {dict(folder_counts)}")
    
    # Check a few emails from each folder to verify logic
    for folder in folder_counts.index[:3]:  # Check top 3 folders
        print(f"\n📁 Checking {folder} folder logic...")
        folder_emails = all_emails[all_emails['in_folder'] == folder].head(3)
        
        for _, email in folder_emails.iterrows():
            labels = email.get('labels', [])
            detected_folder = email.get('in_folder')
            message_id = email.get('message_id', 'unknown')
            
            print(f"  📧 {message_id}: detected={detected_folder}, labels={labels}")
            
            # Verify folder detection logic
            if detected_folder == 'inbox':
                if 'INBOX' not in labels:
                    print(f"    ⚠️ LOGIC ERROR: Email detected as inbox but no INBOX label")
            elif detected_folder == 'trash':
                if 'TRASH' not in labels:
                    print(f"    ⚠️ LOGIC ERROR: Email detected as trash but no TRASH label")
            elif detected_folder == 'spam':
                if 'SPAM' not in labels:
                    print(f"    ⚠️ LOGIC ERROR: Email detected as spam but no SPAM label")
            elif detected_folder == 'archive':
                # Archive should have no folder labels
                folder_labels = [l for l in labels if l in ['INBOX', 'TRASH', 'SPAM']]
                if folder_labels:
                    print(f"    ⚠️ LOGIC ERROR: Email detected as archive but has folder labels: {folder_labels}")
    
    print("\n✅ Folder detection logic test completed")


def test_query_vs_postfilter_consistency():
    """Test if Gmail API query filtering matches post-processing filtering."""
    gmail = Gmail()
    
    print("🔍 Testing query vs post-filter consistency...")
    
    # Method 1: Use in_folder parameter (should use Gmail API query)
    print("\n📥 Method 1: Using in_folder='inbox' parameter...")
    method1_emails = gmail.get_emails(in_folder='inbox', days=30, max_emails=20)
    method1_ids = set(method1_emails['message_id'].tolist()) if not method1_emails.empty else set()
    print(f"Found {len(method1_ids)} emails using in_folder parameter")
    
    # Method 2: Get all emails and filter by in_folder column
    print("\n📧 Method 2: Getting all emails and filtering by in_folder column...")
    all_emails = gmail.get_emails(days=30, max_emails=100)
    method2_emails = all_emails[all_emails['in_folder'] == 'inbox'] if not all_emails.empty else all_emails
    method2_ids = set(method2_emails['message_id'].tolist()) if not method2_emails.empty else set()
    print(f"Found {len(method2_ids)} emails using post-filtering")
    
    # Compare the two methods
    if method1_ids and method2_ids:
        only_in_method1 = method1_ids - method2_ids
        only_in_method2 = method2_ids - method1_ids
        common = method1_ids & method2_ids
        
        print(f"\n📊 Comparison results:")
        print(f"  Common emails: {len(common)}")
        print(f"  Only in method 1 (in_folder param): {len(only_in_method1)}")
        print(f"  Only in method 2 (post-filter): {len(only_in_method2)}")
        
        if only_in_method1:
            print(f"  ⚠️ INCONSISTENCY: {len(only_in_method1)} emails only found by in_folder parameter")
            # Show a few examples
            for i, msg_id in enumerate(list(only_in_method1)[:3]):
                email = method1_emails[method1_emails['message_id'] == msg_id].iloc[0]
                labels = email.get('labels', [])
                folder = email.get('in_folder', 'unknown')
                print(f"    - {msg_id}: folder={folder}, labels={labels}")
        
        if only_in_method2:
            print(f"  ⚠️ INCONSISTENCY: {len(only_in_method2)} emails only found by post-filtering")
        
        if not only_in_method1 and not only_in_method2:
            print("  ✅ Both methods return the same emails")
    
    print("\n✅ Query vs post-filter consistency test completed")


if __name__ == "__main__":
    print("🧪 Running folder filtering tests...")
    test_folder_filtering_accuracy()
    test_folder_detection_logic()
    test_query_vs_postfilter_consistency()
    print("✅ All folder filtering tests completed!")
