# 📧 DataFrame Email Operations - Quick Guide

## ✅ **THE MOST IMPORTANT METHODS** - Now Accept DataFrames Directly!

### 🗑️ **Move to Trash**
```python
from gmaildr import Gmail

gmail = Gmail()

# Get emails as DataFrame
emails = gmail.get_emails(days=7)

# Filter emails you want to trash
old_emails = emails[emails['timestamp'] < some_date]

# Move directly with DataFrame - NO need to extract message_ids!
gmail.move_to_trash(old_emails)
```

### 📥 **Move to Inbox** 
```python
# Get trash emails
trash_emails = gmail.get_emails(in_folder='trash', days=30)

# Filter what you want to restore
important_emails = trash_emails[trash_emails['is_important'] == True]

# Move directly with DataFrame
gmail.move_to_inbox(important_emails)
```

### 📦 **Move to Archive**
```python
# Get inbox emails
inbox_emails = gmail.get_emails(in_folder='inbox', days=90)

# Filter old read emails
old_read = inbox_emails[
    (inbox_emails['is_read'] == True) & 
    (inbox_emails['timestamp'] < thirty_days_ago)
]

# Archive directly with DataFrame
gmail.move_to_archive(old_read)
```

## 🔥 **Complete Workflow Example**

```python
from gmaildr import Gmail
import pandas as pd
from datetime import datetime, timedelta

def clean_email_folders():
    gmail = Gmail()
    
    # 1. Get emails from different folders
    inbox = gmail.get_emails(in_folder='inbox', days=180)
    trash = gmail.get_emails(in_folder='trash', days=90)
    
    print(f"📥 Inbox: {len(inbox)} emails")
    print(f"🗑️ Trash: {len(trash)} emails")
    
    # 2. Define time thresholds
    thirty_days_ago = datetime.now() - timedelta(days=30)
    seven_days_ago = datetime.now() - timedelta(days=7)
    
    # 3. TRASH: Old newsletters and promotions
    newsletters = inbox[
        inbox['subject'].str.contains('newsletter|unsubscribe|promotion', case=False, na=False)
    ]
    old_newsletters = newsletters[newsletters['timestamp'] < thirty_days_ago]
    
    if not old_newsletters.empty:
        gmail.move_to_trash(old_newsletters)  # DataFrame directly!
        print(f"🗑️ Trashed {len(old_newsletters)} old newsletters")
    
    # 4. ARCHIVE: Old read emails
    old_read = inbox[
        (inbox['is_read'] == True) & 
        (inbox['timestamp'] < thirty_days_ago)
    ]
    
    if not old_read.empty:
        gmail.move_to_archive(old_read)  # DataFrame directly!
        print(f"📦 Archived {len(old_read)} old read emails")
    
    # 5. RESTORE: Important emails from trash
    important_trash = trash[
        (trash['is_important'] == True) |
        (trash['sender_email'].str.contains('boss|manager|client', case=False, na=False))
    ]
    
    if not important_trash.empty:
        gmail.move_to_inbox(important_trash)  # DataFrame directly!
        print(f"📥 Restored {len(important_trash)} important emails from trash")
    
    print("✅ Email cleanup complete!")

# Run it
clean_email_folders()
```

## 🎯 **Key Benefits**

1. **No more manual message_id extraction** - Pass DataFrames directly
2. **Powerful pandas filtering** - Use any DataFrame operation to select emails  
3. **Bulk operations** - Move hundreds of emails with one command
4. **Type safety** - Automatic validation that DataFrame has 'message_id' column

## ⚡ **Before vs After**

### ❌ **Old Way (Tedious)**
```python
emails = gmail.get_emails(days=30)
old_emails = emails[emails['timestamp'] < some_date]
message_ids = old_emails['message_id'].tolist()  # Manual extraction
gmail.move_to_trash(message_ids)
```

### ✅ **New Way (Simple)**
```python
emails = gmail.get_emails(days=30)
old_emails = emails[emails['timestamp'] < some_date]
gmail.move_to_trash(old_emails)  # Direct DataFrame support!
```

## 🚀 **ALL Email Modification Methods Support DataFrames**

### 📁 **Folder Operations**
- `gmail.move_to_trash(dataframe)`
- `gmail.move_to_inbox(dataframe)` 
- `gmail.move_to_archive(dataframe)`

### 🏷️ **Label Operations**
- `gmail.add_label(dataframe, "Important")`
- `gmail.remove_label(dataframe, "Spam")`

### ⭐ **Status Operations**
- `gmail.mark_as_read(dataframe)`
- `gmail.mark_as_unread(dataframe)`
- `gmail.star_email(dataframe)`
- `gmail.unstar_email(dataframe)`
- `gmail.archive_email(dataframe)`

### 🔄 **Complete Example**
```python
# Get emails
emails = gmail.get_emails(days=30)

# Filter different types
important = emails[emails['is_important'] == True]
spam = emails[emails['subject'].str.contains('spam', case=False)]
unread = emails[emails['is_read'] == False]

# Apply operations directly to DataFrames
gmail.star_email(important)           # Star important emails
gmail.add_label(spam, "Junk")         # Label spam emails  
gmail.mark_as_read(unread)            # Mark unread as read
gmail.move_to_trash(spam)             # Move spam to trash
```

**Still work with message IDs too:**
- `gmail.move_to_trash("message_id")`
- `gmail.move_to_trash(["id1", "id2", "id3"])`
