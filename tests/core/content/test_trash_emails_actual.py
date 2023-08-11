"""
Test to verify what emails are actually returned by trash search.

This test helps debug the issue where get_trash_emails() returns emails
that are not actually in the trash folder.
"""

from gmaildr import Gmail
import pandas as pd


def test_trash_emails_vs_manual_verification():
    """Test that emails returned by trash search are actually in trash."""
    gmail = Gmail(enable_cache=False)
    
    # Get emails using trash search
    print("Getting emails with trash search...")
    trash_df = gmail.get_trash_emails(days=30, max_emails=10, include_text=False, include_metrics=False)
    
    print(f"Found {len(trash_df)} emails with trash search")
    
    if len(trash_df) == 0:
        print("No emails found in trash search - this might be correct")
        return
    
    # Check the labels of each email to see if they're actually in trash
    print("\nChecking labels of returned emails:")
    for idx, email in trash_df.iterrows():
        labels = email.get('labels', [])
        label_names = email.get('label_names', [])
        
        print(f"Email {idx}: {email.get('subject', 'No subject')[:50]}...")
        print(f"  Labels: {labels}")
        print(f"  Label names: {label_names}")
        
        # Check if it has TRASH label (Gmail's system label for trash)
        has_trash_label = 'TRASH' in labels or 'Trash' in label_names
        print(f"  Has TRASH label: {has_trash_label}")
        print()


def test_manual_trash_verification():
    """Test manual verification of trash emails using label search."""
    gmail = Gmail(enable_cache=False)
    
    # Try to get emails with TRASH label directly
    print("Getting emails with TRASH label...")
    
    # Get all labels to find the trash label ID
    labels = gmail.get_labels()
    trash_label = None
    for label in labels:
        if label.get('name') == 'Trash' or label.get('id') == 'TRASH':
            trash_label = label
            break
    
    if trash_label:
        print(f"Found trash label: {trash_label}")
        
        # Try to get emails with this label
        # Note: This might not work as Gmail doesn't allow searching by system labels
        print("Attempting to search by trash label...")
    else:
        print("Could not find trash label in labels list")
        print("Available labels:")
        for label in labels[:10]:  # Show first 10
            print(f"  {label.get('name', 'NO_NAME')} (ID: {label.get('id', 'NO_ID')})")


def test_alternative_trash_detection():
    """Test alternative methods to detect trash emails."""
    gmail = Gmail(enable_cache=False)
    
    print("Testing alternative trash detection methods...")
    
    # Method 1: Get all emails and filter by TRASH label
    print("\nMethod 1: Get all emails and filter by TRASH label")
    all_emails = gmail.get_emails(days=30, max_emails=50, include_text=False, include_metrics=False)
    
    trash_emails = []
    for idx, email in all_emails.iterrows():
        labels = email.get('labels', [])
        if 'TRASH' in labels:
            trash_emails.append(email)
    
    print(f"Found {len(trash_emails)} emails with TRASH label out of {len(all_emails)} total emails")
    
    # Method 2: Check if emails are NOT in INBOX (archive + trash)
    print("\nMethod 2: Get emails not in inbox (archive + trash)")
    not_inbox = gmail.get_emails(days=30, max_emails=50, in_folder='archive', include_text=False, include_metrics=False)
    print(f"Found {len(not_inbox)} emails not in inbox")
    
    # Check which of these have TRASH label
    actual_trash = []
    for idx, email in not_inbox.iterrows():
        labels = email.get('labels', [])
        if 'TRASH' in labels:
            actual_trash.append(email)
    
    print(f"Found {len(actual_trash)} actual trash emails out of {len(not_inbox)} not-in-inbox emails")
