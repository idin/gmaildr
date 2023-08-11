# EmailDataFrame Schema Documentation 📊

## Overview

This document describes the complete schema of EmailDataFrame objects returned by `gmail.get_emails()`. EmailDataFrame extends pandas DataFrame with email-specific operations.

## Core Schema

### Required Columns

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `message_id` | `str` | Unique Gmail message ID | `"18c1234567890abc"` |
| `sender_email` | `str` | Sender's email address | `"sender@example.com"` |
| `sender_name` | `str` or `None` | Sender's display name | `"John Doe"` or `None` |
| `subject` | `str` | Email subject line | `"Meeting tomorrow"` |
| `date` | `datetime` | Email received date/time | `2024-01-15 10:30:00` |

### Size Information

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `size_bytes` | `int` | Email size in bytes | `2048` |
| `size_kb` | `float` | Email size in kilobytes | `2.0` |

### Email Status

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `has_attachments` | `bool` | Whether email has attachments | `True` |
| `is_read` | `bool` | Whether email has been read | `False` |
| `is_important` | `bool` | Whether Gmail marked as important | `True` |
| `in_folder` | `str` | Current folder location | `"inbox"` |

### Metadata

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `labels` | `List[str]` | Gmail labels applied to email | `["INBOX", "IMPORTANT"]` |
| `thread_id` | `str` | Gmail thread ID | `"18c1234567890abc"` |
| `snippet` | `str` | Email preview snippet | `"Hi, let's meet tomorrow..."` |

### Date Components (Auto-generated)

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `year` | `int` | Year email was received | `2024` |
| `month` | `int` | Month email was received | `1` |
| `day` | `int` | Day of month email was received | `15` |
| `hour` | `int` | Hour email was received | `10` |
| `day_of_week` | `str` | Day of week email was received | `"Monday"` |

### Optional Columns (Conditional)

| Column | Type | Description | When Available |
|--------|------|-------------|----------------|
| `text_content` | `str` | Full email body text | When `include_text=True` |
| `in_reply_to` | `str` | Message ID this email replies to | When available in headers |
| `cluster` | `int` | Cluster assignment | After running clustering |

## Extended Schema (with Metrics)

When `include_metrics=True` and `include_text=True`, additional columns are added:

### Content Analysis Metrics

| Column | Type | Description | Range |
|--------|------|-------------|-------|
| `word_count` | `int` | Number of words in email | `0+` |
| `sentence_count` | `int` | Number of sentences in email | `0+` |
| `avg_sentence_length` | `float` | Average words per sentence | `0+` |
| `capitalization_ratio` | `float` | Ratio of capitalized words | `0.0-1.0` |
| `question_count` | `int` | Number of questions in email | `0+` |
| `exclamation_count` | `int` | Number of exclamations in email | `0+` |
| `url_count` | `int` | Number of URLs in email | `0+` |
| `email_count` | `int` | Number of email addresses in email | `0+` |
| `phone_count` | `int` | Number of phone numbers in email | `0+` |

### Sentiment & Style Metrics

| Column | Type | Description | Range |
|--------|------|-------------|-------|
| `sentiment_score` | `float` | Sentiment analysis score | `-1.0 to 1.0` |
| `formality_score` | `float` | Formality level of email | `0.0-1.0` |
| `readability_score` | `float` | Flesch reading ease score | `0-100` |
| `complexity_score` | `float` | Text complexity measure | `0.0-1.0` |

### Human Detection Metrics

| Column | Type | Description | Range |
|--------|------|-------------|-------|
| `human_score` | `float` | Likelihood email is from human | `0.0-1.0` |
| `is_human_sender` | `bool` | Binary human/automated classification | `True/False` |
| `content_score` | `float` | Content-based human indicator | `0.0-1.0` |
| `sender_score` | `float` | Sender-based human indicator | `0.0-1.0` |
| `behavioural_score` | `float` | Behaviour-based human indicator | `0.0-1.0` |
| `conversation_score` | `float` | Conversation-based human indicator | `0.0-1.0` |

## Data Types Summary

### String Columns
- `message_id`, `sender_email`, `sender_name`, `subject`, `snippet`, `thread_id`, `day_of_week`, `in_folder`
- `text_content` (optional), `in_reply_to` (optional)

### Numeric Columns
- `size_bytes` (int), `size_kb` (float)
- `year`, `month`, `day`, `hour` (int)
- All metrics columns (float/int)

### Boolean Columns
- `has_attachments`, `is_read`, `is_important`
- `is_human_sender` (optional)

### List Columns
- `labels` (List[str])

### Datetime Columns
- `date` (datetime)

## Usage Examples

### Basic Email Retrieval
```python
from gmaildr import Gmail

gmail = Gmail()
emails = gmail.get_emails(days=30)

# Check available columns
print(emails.columns.tolist())

# Access basic email data
print(emails[['message_id', 'sender_email', 'subject', 'date']].head())
```

### With Text Content
```python
# Include full email text
emails_with_text = gmail.get_emails(days=7, include_text=True)
print(emails_with_text['text_content'].iloc[0])
```

### With Analysis Metrics
```python
# Include content analysis metrics
emails_with_metrics = gmail.get_emails(
    days=7, 
    include_text=True, 
    include_metrics=True
)

# Check human detection
human_emails = emails_with_metrics[emails_with_metrics['is_human_sender'] == True]
print(f"Found {len(human_emails)} human emails")
```

### After Clustering
```python
from gmaildr.datascience import cluster_emails

# Cluster emails
clustered_emails, cluster_info = cluster_emails(emails)

# Check cluster assignments
print(clustered_emails['cluster'].value_counts())
```

## Schema Validation

EmailDataFrame validates that:
1. `message_id` column is always present
2. All required columns have appropriate data types
3. Date columns are properly formatted as datetime
4. Boolean columns contain only True/False values

## Notes

- **Missing Values**: Some columns may contain `None` or `NaN` values
- **Date Handling**: All dates are in UTC timezone
- **Text Encoding**: Text content is UTF-8 encoded
- **Size Calculations**: Size columns are calculated from `size_bytes`
- **Label Format**: Labels are Gmail's internal label IDs (e.g., "INBOX", "IMPORTANT")
- **Thread ID**: Same as message_id for single emails, different for thread members
