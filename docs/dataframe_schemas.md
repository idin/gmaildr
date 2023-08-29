# DataFrame Schemas 📊

Quick reference for all dataframe columns in gmaildr.

## 📧 EmailDataFrame Columns

### 🚀 Fast Version (without text) - 27 columns
```python
emails = gmail.get_emails(include_text=False)  # Default
```

|  # | Column                        | Type       | Description                     |
|----|-------------------------------|------------|---------------------------------|
|  1 | `message_id`                  | str        | Unique Gmail message ID         |
|  2 | `sender_email`                | str        | Sender's email address          |
|  3 | `sender_name`                 | str/None   | Sender's display name           |
|  4 | `recipient_email`             | str        | Recipient's email address       |
|  5 | `recipient_name`              | str/None   | Recipient's display name        |
|  6 | `subject`                     | str        | Email subject line              |
|  7 | `timestamp`                   | datetime   | Email received date/time (UTC)  |
|  8 | `sender_local_timestamp`      | datetime   | Sender's local timestamp        |
|  9 | `size_bytes`                  | int        | Email size in bytes             |
| 10 | `size_kb`                     | float      | Email size in kilobytes         |
| 11 | `labels`                      | List[str]  | Gmail labels                    |
| 12 | `thread_id`                   | str        | Gmail thread ID                 |
| 13 | `snippet`                     | str        | Email preview snippet           |
| 14 | `has_attachments`             | bool       | Has attachments                 |
| 15 | `is_read`                     | bool       | Email has been read             |
| 16 | `is_important`                | bool       | Gmail marked as important       |
| 17 | `year`                        | int        | Year email was received         |
| 18 | `month`                       | int        | Month email was received        |
| 19 | `day`                         | int        | Day of month                    |
| 20 | `hour`                        | int        | Hour email was received         |
| 21 | `day_of_week`                 | str        | Day of week                     |
| 22 | `subject_language`            | str/None   | Detected subject language       |
| 23 | `subject_language_confidence` | float/None | Subject language confidence     |
| 24 | `has_role_based_email`        | bool       | Sender is role-based/automated  |
| 25 | `is_forwarded`                | bool       | Email is forwarded              |
| 26 | `is_starred`                  | bool       | Email is starred                |
| 27 | `in_folder`                   | str        | Current folder location         |

### 🐌 Slow Version (with text) - 30 columns
```python
emails = gmail.get_emails(include_text=True)
```

**All above columns PLUS:**

|  # | Column                        | Type       | Description                     |
|----|-------------------------------|------------|---------------------------------|
| 28 | `text_content`                | str        | Full email body text            |
| 29 | `text_language`               | str/None   | Detected text language          |
| 30 | `text_language_confidence`    | float/None | Text language confidence        |

### 📊 With Metrics (additional columns)
```python
emails = gmail.get_emails(include_text=True, include_metrics=True)
```

**Additional analysis columns added:**
- Content metrics: `word_count`, `sentence_count`, `capitalization_ratio`
- Sentiment: `sentiment_score`, `formality_score`, `readability_score`
- Human detection: `human_score`, `is_human_sender`, `content_score`
- Communication: `question_count`, `exclamation_count`, `url_count`

## 👤 Sender Analysis (Manual Aggregation)

**Note**: There is no built-in `SenderDataFrame` class. For sender clustering, you'll need to manually aggregate email data by `sender_email`.

### Suggested Aggregation Features
```python
# Manual sender aggregation example
sender_stats = emails.groupby('sender_email').agg({
    'message_id': 'count',           # total_emails
    'subject': 'nunique',            # unique_subjects  
    'size_kb': ['mean', 'sum'],      # avg/total size
    'is_read': 'mean',               # read_ratio
    'is_important': 'mean',          # importance_ratio
    'has_attachments': 'mean',       # attachment_ratio
    'timestamp': ['min', 'max'],     # first/last email
    'day_of_week': lambda x: x.mode()[0],  # most_active_day
    'hour': lambda x: x.mode()[0],         # most_active_hour
}).round(3)
```

**Key features to create for sender clustering:**
- **Volume**: email count, frequency, date range
- **Temporal**: most active day/hour, sending patterns  
- **Content**: average size, attachment ratio, subject diversity
- **Engagement**: read ratio, importance ratio, star ratio
- **Behavior**: role-based detection, language patterns

## 🎯 For Clustering

### Email Clustering
**Fast clustering (metadata only):**
```python
# Use columns: sender_email, subject, size_kb, labels, 
# day_of_week, hour, has_attachments, is_important
```

**Slow clustering (with content):**
```python
# Add: text_content, text_language for semantic analysis
```

### Sender Clustering
**Manual aggregation needed - no built-in SenderDataFrame:**
```python
# Create features by grouping emails by sender_email
# Volume: message count, unique subjects, date range
# Temporal: most active day/hour, sending frequency
# Content: average size, attachment ratio
# Engagement: read ratio, importance ratio
# Behavior: role-based email detection
```

## 📝 Quick Usage

```python
from gmaildr import Gmail

gmail = Gmail()

# Fast email data (27 cols)
emails_fast = gmail.get_emails(days=30)

# Slow email data (30 cols) 
emails_slow = gmail.get_emails(days=30, include_text=True)

# With metrics (50+ cols)
emails_metrics = gmail.get_emails(days=30, include_text=True, include_metrics=True)

# Manual sender aggregation
senders = emails_fast.groupby('sender_email').agg({
    'message_id': 'count',
    'subject': 'nunique', 
    'size_kb': 'mean'
})

print(f"Email columns: {len(emails_fast.columns)}")
print(f"Unique senders: {len(senders)}")
```
