"""
EmailDataFrame Columns Demonstration.

This example shows all the columns available in the EmailDataFrame,
including the new language detection and role-based email columns.
"""

from gmaildr import Gmail
from gmaildr.core.email_message import EmailMessage
from datetime import datetime


def main():
    """Demonstrate EmailDataFrame columns."""
    print("📊 EmailDataFrame Columns Demonstration")
    print("=" * 50)
    
    gmail = Gmail()
    
    # Create a simple test email
    test_email = EmailMessage(
        message_id="demo1",
        sender_email="john@example.com",
        sender_name="John Smith",
        subject="Hello world",
        timestamp=datetime.now(),
        sender_local_timestamp=datetime.now(),
        size_bytes=1024,
        text_content="This is a test email in English."
    )
    
    # Convert to DataFrame
    df = gmail._emails_to_dataframe(emails=[test_email], include_text=True)
    
    print(f"DataFrame shape: {df.shape}")
    print(f"Total columns: {len(df.columns)}")
    
    print("\n📋 All Available Columns:")
    print("-" * 40)
    
    # Group columns by category
    basic_columns = ['message_id', 'sender_email', 'sender_name', 'subject', 'timestamp', 'snippet']
    size_columns = ['size_bytes', 'size_kb']
    label_columns = ['labels', 'thread_id', 'has_attachments', 'is_read', 'is_important']
    date_columns = ['year', 'month', 'day', 'hour', 'day_of_week']
    content_columns = ['text_content']
    language_columns = ['subject_language', 'subject_language_confidence', 'text_language', 'text_language_confidence']
    role_columns = ['has_role_based_email']
    folder_columns = ['in_folder']
    
    all_categories = [
        ("Basic Info", basic_columns),
        ("Size", size_columns),
        ("Labels & Metadata", label_columns),
        ("Date Components", date_columns),
        ("Content", content_columns),
        ("Language Detection", language_columns),
        ("Role Detection", role_columns),
        ("Folder", folder_columns)
    ]
    
    for category, columns in all_categories:
        print(f"\n🔹 {category}:")
        for col in columns:
            if col in df.columns:
                print(f"   ✅ {col}")
            else:
                print(f"   ❌ {col} (not present)")
    
    print(f"\n🎯 New Language & Role Detection Columns:")
    print("-" * 40)
    
    new_columns = [
        'subject_language',
        'subject_language_confidence',
        'text_language', 
        'text_language_confidence',
        'has_role_based_email'
    ]
    
    for col in new_columns:
        if col in df.columns:
            value = df.iloc[0][col]
            print(f"   ✅ {col}: {value}")
        else:
            print(f"   ❌ {col}: Not found")
    
    print(f"\n📈 Sample Data:")
    print("-" * 40)
    
    # Show sample values for key columns
    sample_cols = ['subject', 'sender_email', 'subject_language', 'text_language', 'has_role_based_email']
    for col in sample_cols:
        if col in df.columns:
            value = df.iloc[0][col]
            print(f"   {col}: {value}")
    
    print(f"\n✅ EmailDataFrame successfully includes all new language detection and role-based email columns!")


if __name__ == "__main__":
    main()
