# Email Operations with Standard Pandas DataFrames

This guide shows how to perform email operations using gmaildr's simplified architecture with standard pandas DataFrames.

## 📧 Basic Email Operations

### 1. Get Emails as Standard DataFrame

```python
from gmaildr import Gmail

gmail = Gmail()

# Get emails as standard pandas DataFrame
emails = gmail.get_emails(days=7, max_emails=50)
print(f"Type: {type(emails)}")  # <class 'pandas.core.frame.DataFrame'>
print(f"Shape: {emails.shape}")
print(f"Columns: {list(emails.columns)}")
```

### 2. Filter and Select Emails

```python
# Filter emails using standard pandas operations
inbox_emails = emails[emails['in_folder'] == 'inbox']
unread_emails = emails[emails['is_read'] == False]
important_emails = emails[emails['is_important'] == True]

# Get message IDs for operations
message_ids = inbox_emails['message_id'].tolist()
print(f"Found {len(message_ids)} inbox emails")
```

## 🏷️ Label Operations

### Add/Remove Labels

```python
# Add labels to emails
gmail.modify_labels(
    message_ids=message_ids,
    add_labels=['IMPORTANT', 'MyCustomLabel'],
    show_progress=True
)

# Remove labels from emails
gmail.modify_labels(
    message_ids=message_ids,
    remove_labels=['SPAM'],
    show_progress=True
)
```

### Create Custom Labels

```python
# Create a new label
label_id = gmail.create_label('ProjectAlpha')
print(f"Created label with ID: {label_id}")

# Get or create label (creates if doesn't exist)
label_id = gmail.get_label_id_or_create('ProjectBeta')
```

## 📁 Folder Operations (Moving Emails)

### Move to Different Folders

```python
# Move emails to trash
gmail.move_to_trash(message_ids, show_progress=True)

# Move emails to inbox
gmail.move_to_inbox(message_ids, show_progress=True)

# Archive emails (remove INBOX label)
for msg_id in message_ids:
    gmail.archive_email(msg_id)
```

### Custom Folder Movement

```python
# Move to custom folder by manipulating labels
def move_to_folder(gmail, message_ids, folder_label):
    """Move emails to a specific folder by managing labels."""
    # Remove all folder labels
    folder_labels = ['INBOX', 'SPAM', 'TRASH', 'SENT', 'DRAFT']
    
    gmail.modify_labels(
        message_ids=message_ids,
        add_labels=[folder_label],
        remove_labels=folder_labels,
        show_progress=True
    )

# Usage
move_to_folder(gmail, message_ids, 'ProjectAlpha')
```

## ⭐ Email Status Operations

### Mark as Read/Unread

```python
# Mark emails as read
gmail.mark_as_read(message_ids, show_progress=True)

# Mark single email as unread
gmail.mark_as_unread(message_ids[0])
```

### Star/Unstar Emails

```python
# Star emails
gmail.star_email(message_ids, show_progress=True)

# Unstar single email
gmail.unstar_email(message_ids[0])
```

## 🔍 Advanced DataFrame Operations

### Filter by Labels

```python
# Filter emails that have specific labels
def has_label_filter(labels_list, target_label):
    """Check if email has a specific label."""
    if isinstance(labels_list, list):
        return target_label in labels_list
    return False

# Apply filter
starred_emails = emails[emails['labels'].apply(
    lambda x: has_label_filter(x, 'STARRED')
)]

# Get message IDs for further operations
starred_message_ids = starred_emails['message_id'].tolist()
```

### Bulk Operations by Criteria

```python
# Example: Archive all marketing emails older than 30 days
import pandas as pd
from datetime import datetime, timedelta

# Filter criteria
thirty_days_ago = datetime.now() - timedelta(days=30)
marketing_emails = emails[
    (emails['timestamp'] < thirty_days_ago) &
    (emails['subject'].str.contains('unsubscribe', case=False, na=False))
]

# Get message IDs and archive
marketing_ids = marketing_emails['message_id'].tolist()
if marketing_ids:
    print(f"Archiving {len(marketing_ids)} marketing emails...")
    for msg_id in marketing_ids:
        gmail.archive_email(msg_id)
```

### Batch Label Management

```python
# Example: Organize emails by sender domain
def organize_by_domain(emails_df, gmail):
    """Organize emails by adding domain-based labels."""
    
    # Group by sender domain
    emails_df['domain'] = emails_df['sender_email'].str.split('@').str[1]
    
    for domain, group in emails_df.groupby('domain'):
        # Create domain label
        domain_label = f"Domain_{domain.replace('.', '_')}"
        gmail.get_label_id_or_create(domain_label)
        
        # Add label to all emails from this domain
        domain_message_ids = group['message_id'].tolist()
        gmail.modify_labels(
            message_ids=domain_message_ids,
            add_labels=[domain_label],
            show_progress=True
        )
        print(f"Labeled {len(domain_message_ids)} emails from {domain}")

# Usage
organize_by_domain(emails, gmail)
```

## 🔄 Complete Workflow Example

```python
from gmaildr import Gmail
import pandas as pd

def clean_inbox_workflow():
    """Complete workflow to clean and organize inbox."""
    
    gmail = Gmail()
    
    # 1. Get all inbox emails
    emails = gmail.get_emails(query='in:inbox', max_emails=1000)
    print(f"Found {len(emails)} inbox emails")
    
    if emails.empty:
        print("No emails to process")
        return
    
    # 2. Identify different types of emails
    newsletters = emails[
        emails['subject'].str.contains('newsletter|unsubscribe', case=False, na=False)
    ]
    
    notifications = emails[
        emails['sender_email'].str.contains('noreply|no-reply|notification', case=False, na=False)
    ]
    
    old_emails = emails[
        emails['timestamp'] < (pd.Timestamp.now() - pd.Timedelta(days=90))
    ]
    
    # 3. Create labels for organization
    gmail.get_label_id_or_create('Newsletters')
    gmail.get_label_id_or_create('Notifications')
    
    # 4. Apply labels and organize
    if not newsletters.empty:
        newsletter_ids = newsletters['message_id'].tolist()
        gmail.modify_labels(newsletter_ids, add_labels=['Newsletters'])
        print(f"Labeled {len(newsletter_ids)} newsletters")
    
    if not notifications.empty:
        notification_ids = notifications['message_id'].tolist()
        gmail.modify_labels(notification_ids, add_labels=['Notifications'])
        print(f"Labeled {len(notification_ids)} notifications")
    
    # 5. Archive old emails
    if not old_emails.empty:
        old_ids = old_emails['message_id'].tolist()
        for msg_id in old_ids:
            gmail.archive_email(msg_id)
        print(f"Archived {len(old_ids)} old emails")
    
    print("✅ Inbox cleanup complete!")

# Run the workflow
clean_inbox_workflow()
```

## 🎯 Key Benefits

1. **Standard pandas**: Use familiar DataFrame operations
2. **Batch operations**: Efficient bulk email modifications  
3. **Flexible filtering**: Powerful pandas filtering capabilities
4. **Label management**: Full control over Gmail labels
5. **Progress tracking**: Built-in progress bars for long operations

## 🔗 Integration with Ravenclaw

For advanced data science tasks, pass the standard DataFrame to Ravenclaw:

```python
# Get emails with gmaildr
emails = gmail.get_emails(days=30, include_text=True, include_metrics=True)

# Use Ravenclaw for advanced analysis
from ravenclaw import DataFrame as RavenclawDF

# Convert to Ravenclaw DataFrame for ML features
raven_emails = RavenclawDF(emails)
ml_features = raven_emails.encode_categorical_features_with_one_hot(
    columns=['in_folder', 'subject_language'],
    prefix='',
    suffix='',
    delete_original_columns=True
)

# Continue with ML pipeline...
```
