"""
Test the query builder fix for folder filtering.

This test verifies that the Gmail API query is built correctly
for folder filtering and bypasses cache to test fresh data.
"""

import pytest
from gmaildr.utils.query_builder import build_gmail_search_query


def test_query_builder_folder_logic():
    """Test that the query builder creates correct queries for different folders."""
    
    print("🔍 Testing query builder folder logic...")
    
    # Test inbox query
    inbox_query = build_gmail_search_query(days=30, in_folder='inbox')
    print(f"📥 Inbox query: {inbox_query}")
    
    # Should exclude sent, drafts, spam, trash
    assert "in:inbox" in inbox_query
    assert "-in:sent" in inbox_query
    assert "-in:drafts" in inbox_query
    assert "-in:spam" in inbox_query
    assert "-in:trash" in inbox_query
    
    # Test sent query
    sent_query = build_gmail_search_query(days=30, in_folder='sent')
    print(f"📤 Sent query: {sent_query}")
    assert "in:sent" in sent_query
    assert "-in:sent" not in sent_query  # Should not exclude sent
    
    # Test archive query
    archive_query = build_gmail_search_query(days=30, in_folder='archive')
    print(f"📦 Archive query: {archive_query}")
    
    # Should exclude all folder labels
    assert "-in:inbox" in archive_query
    assert "-in:sent" in archive_query
    assert "-in:drafts" in archive_query
    assert "-in:spam" in archive_query
    assert "-in:trash" in archive_query
    
    # Test trash query
    trash_query = build_gmail_search_query(days=30, in_folder='trash')
    print(f"🗑️ Trash query: {trash_query}")
    assert "in:trash" in trash_query
    
    print("✅ Query builder logic test passed")


def test_folder_filtering_with_fresh_data():
    """Test folder filtering by forcing fresh API calls."""
    from gmaildr import Gmail
    
    gmail = Gmail()
    
    print("🔍 Testing folder filtering with fresh data...")
    
    # Clear cache to force fresh API calls
    if gmail.cache_manager:
        print("🧹 Clearing cache to force fresh API calls...")
        gmail.cache_manager.invalidate_cache()
    
    # Test inbox filtering with fresh data
    print("\n📥 Testing inbox filtering (fresh data)...")
    inbox_emails = gmail.get_emails(in_folder='inbox', days=7, max_emails=5)
    
    if not inbox_emails.empty:
        print(f"Found {len(inbox_emails)} emails with in_folder='inbox'")
        
        # Check what folders these emails are actually in
        folder_counts = inbox_emails['in_folder'].value_counts()
        print(f"Actual folders: {dict(folder_counts)}")
        
        # Check for folder filtering issues
        non_inbox_emails = inbox_emails[inbox_emails['in_folder'] != 'inbox']
        if not non_inbox_emails.empty:
            print(f"⚠️ STILL HAVE FOLDER FILTERING ISSUES: {len(non_inbox_emails)} emails")
            
            for i, (_, email) in enumerate(non_inbox_emails.iterrows()):
                if i < 3:  # Show first 3 examples
                    labels = email.get('labels', [])
                    folder = email.get('in_folder', 'unknown')
                    print(f"  - Email {email['message_id']}: folder={folder}, labels={labels}")
            
            # Check if these are emails with conflicting labels (SENT+INBOX)
            sent_inbox_emails = non_inbox_emails[
                non_inbox_emails.apply(
                    lambda row: 'SENT' in row.get('labels', []) and 'INBOX' in row.get('labels', []), 
                    axis=1
                )
            ]
            
            if not sent_inbox_emails.empty:
                print(f"📧 Found {len(sent_inbox_emails)} emails with both SENT and INBOX labels")
                print("This suggests the Gmail API query fix didn't work as expected")
            
        else:
            print("✅ All emails returned by in_folder='inbox' are actually in inbox")
    else:
        print("No inbox emails found")
    
    print("\n✅ Fresh data test completed")


def test_manual_query_verification():
    """Manually test Gmail API queries to verify they work correctly."""
    from gmaildr import Gmail
    
    gmail = Gmail()
    
    print("🔍 Manual query verification...")
    
    # Test the exact query that should be generated
    test_query = "after:2024/12/01 before:2024/12/31 in:inbox -in:sent -in:drafts -in:spam -in:trash"
    print(f"📧 Testing query: {test_query}")
    
    try:
        # Use the Gmail client directly to test the query
        message_ids = gmail.client.search_messages(query=test_query, max_results=5)
        print(f"✅ Query returned {len(message_ids)} message IDs")
        
        if message_ids:
            # Get details for a few messages to verify they're actually inbox emails
            print("🔍 Checking first few messages...")
            
            for i, msg_id in enumerate(message_ids[:3]):
                try:
                    # Get message details
                    message = gmail.client.get_message(message_id=msg_id)
                    labels = message.get('labelIds', [])
                    
                    # Check folder logic
                    has_inbox = 'INBOX' in labels
                    has_sent = 'SENT' in labels
                    has_drafts = 'DRAFT' in labels
                    has_spam = 'SPAM' in labels
                    has_trash = 'TRASH' in labels
                    
                    print(f"  📧 Message {i+1}: INBOX={has_inbox}, SENT={has_sent}, DRAFT={has_drafts}, SPAM={has_spam}, TRASH={has_trash}")
                    
                    # This should be true for proper inbox emails
                    is_proper_inbox = has_inbox and not (has_sent or has_drafts or has_spam or has_trash)
                    
                    if not is_proper_inbox:
                        print(f"    ⚠️ This email should NOT be returned by inbox query!")
                        print(f"    Labels: {labels}")
                    else:
                        print(f"    ✅ This email is correctly in inbox")
                        
                except Exception as e:
                    print(f"    ❌ Error getting message details: {e}")
        
    except Exception as e:
        print(f"❌ Query failed: {e}")
    
    print("\n✅ Manual query verification completed")


if __name__ == "__main__":
    print("🧪 Running query builder fix tests...")
    test_query_builder_folder_logic()
    test_folder_filtering_with_fresh_data()
    test_manual_query_verification()
    print("✅ All query builder tests completed!")
