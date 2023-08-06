#!/usr/bin/env python3
"""
Example usage of EmailListManager for managing email lists.

This example demonstrates how to use the EmailListManager to create and manage
blacklists, whitelists, friend lists, and other email categorizations.
"""

from gmailwiz.utils import EmailListManager


def main():
    """Demonstrate EmailListManager functionality."""
    
    # Initialize the email list manager
    # This will create an 'email_lists' directory in your project root
    list_manager = EmailListManager()
    
    print("📧 Email List Manager Example")
    print("=" * 50)
    
    # Create different types of lists
    print("\n1. Creating email lists...")
    list_manager.create_list("blacklist")
    list_manager.create_list("whitelist") 
    list_manager.create_list("friends")
    list_manager.create_list("family")
    list_manager.create_list("work")
    
    print(f"✅ Created lists: {list_manager.get_all_lists()}")
    
    # Add emails to different lists
    print("\n2. Adding emails to lists...")
    
    # Blacklist some spam emails
    spam_emails = [
        "spam@spammer.com",
        "noreply@marketing.com", 
        "newsletter@unwanted.org"
    ]
    for email in spam_emails:
        list_manager.add_email_to_list(email, "blacklist")
    
    # Whitelist important emails
    important_emails = [
        "support@bank.com",
        "security@paypal.com",
        "noreply@amazon.com"
    ]
    for email in important_emails:
        list_manager.add_email_to_list(email, "whitelist")
    
    # Add friends
    friend_emails = [
        "john.doe@gmail.com",
        "jane.smith@yahoo.com",
        "bob.wilson@hotmail.com"
    ]
    for email in friend_emails:
        list_manager.add_email_to_list(email, "friends")
    
    # Add family (some overlap with friends)
    family_emails = [
        "mom@family.com",
        "dad@family.com", 
        "john.doe@gmail.com"  # John is both friend and family
    ]
    for email in family_emails:
        list_manager.add_email_to_list(email, "family")
    
    # Add work contacts
    work_emails = [
        "boss@company.com",
        "hr@company.com",
        "colleague@company.com"
    ]
    for email in work_emails:
        list_manager.add_email_to_list(email, "work")
    
    print("✅ Added emails to various lists")
    
    # Demonstrate list operations
    print("\n3. List operations...")
    
    # Check if an email is in a specific list
    test_email = "john.doe@gmail.com"
    print(f"📧 Checking {test_email}:")
    print(f"   In friends list: {list_manager.is_email_in_list(test_email, 'friends')}")
    print(f"   In family list: {list_manager.is_email_in_list(test_email, 'family')}")
    print(f"   In blacklist: {list_manager.is_email_in_list(test_email, 'blacklist')}")
    
    # Get all lists for an email
    lists_for_email = list_manager.get_lists_for_email(test_email)
    print(f"   Lists containing this email: {lists_for_email}")
    
    # Get all emails in a list
    friends = list_manager.get_emails_in_list("friends")
    print(f"\n👥 Friends list ({len(friends)} emails): {sorted(friends)}")
    
    # Search for emails
    print("\n4. Email search...")
    gmail_friends = list_manager.search_emails("*@gmail.com", "friends")
    print(f"🔍 Gmail friends: {gmail_friends}")
    
    all_company_emails = list_manager.search_emails("*@company.com")
    print(f"🏢 All company emails: {all_company_emails}")
    
    # Get statistics
    print("\n5. Statistics...")
    stats = list_manager.get_all_stats()
    for list_name, list_stats in stats.items():
        print(f"📊 {list_name}: {list_stats['email_count']} emails")
    
    print(f"\n📈 Total unique emails: {list_manager.get_total_email_count()}")
    print(f"📋 Total lists: {list_manager.get_total_list_count()}")
    
    # Demonstrate bulk operations
    print("\n6. Bulk operations...")
    
    # Add multiple emails at once
    new_friends = ["friend1@example.com", "friend2@example.com", "friend3@example.com"]
    results = list_manager.add_emails_to_list(new_friends, "friends")
    print(f"✅ Added {sum(results.values())}/{len(new_friends)} new friends")
    
    # Remove multiple emails
    remove_friends = ["friend1@example.com", "friend2@example.com"]
    results = list_manager.remove_emails_from_list(remove_friends, "friends")
    print(f"❌ Removed {sum(results.values())}/{len(remove_friends)} friends")
    
    # Export a list
    print("\n7. Export functionality...")
    export_path = list_manager.export_list("friends", format="json")
    if export_path:
        print(f"📤 Exported friends list to: {export_path}")
    
    # Clear a list
    print("\n8. List management...")
    list_manager.clear_list("work")
    print(f"🧹 Cleared work list. Emails remaining: {len(list_manager.get_emails_in_list('work'))}")
    
    # Final statistics
    print("\n9. Final statistics...")
    final_stats = list_manager.get_all_stats()
    for list_name, list_stats in final_stats.items():
        print(f"📊 {list_name}: {list_stats['email_count']} emails")
    
    print(f"\n🎉 Email List Manager example completed!")
    print(f"💾 Data saved to: {list_manager.storage_dir}")


if __name__ == "__main__":
    main()
