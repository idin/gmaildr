# SenderDataFrame Aggregate Features

## Overview
The SenderDataFrame aggregates EmailDataFrame data by sender_email to provide comprehensive sender analysis and statistics.

## Core Aggregation Features

### 📊 **Volume & Frequency Metrics**
- `total_emails` - Total number of emails from this sender
- `unique_subjects` - Number of unique subject lines
- `unique_threads` - Number of unique thread IDs
- `date_range_days` - Number of days between first and last email
- `emails_per_day` - Mean emails sent per day
- `first_email_date` - Date of first email from sender
- `last_email_date` - Date of most recent email from sender

### 📅 **Temporal Patterns** *(based on sender_local_timestamp)*
- `most_active_day` - Day of week with most emails (sender's timezone)
- `most_active_hour` - Hour of day with most emails (sender's timezone)
- `quiet_days` - Number of days with no emails
- `burst_days` - Number of days with >1 email (burst sending)
- `recent_activity_days` - Days since last email

**Time Between Emails:**
- `mean_time_between_emails_hours` - Mean time between consecutive emails (hours)
- `std_time_between_emails_hours` - Standard deviation of time between emails (hours)
- `min_time_between_emails_hours` - Minimum time between consecutive emails (hours)
- `max_time_between_emails_hours` - Maximum time between consecutive emails (hours)
- `time_between_emails_entropy` - Entropy of time intervals (measure of randomness)
- `time_between_emails_cv` - Coefficient of variation (std/mean) of time intervals

**Day of Week Patterns:**
- `day_of_week_distribution` - Distribution of emails across days (Mon-Sun, sender's timezone)
- `day_of_week_entropy` - Entropy of day distribution (measure of randomness)
- `day_of_week_concentration` - Concentration index (1 - entropy/max_entropy)
- `weekend_ratio` - Ratio of emails sent on weekends (0-1, sender's timezone)

**Hour of Day Patterns:**
- `hour_of_day_distribution` - Distribution of emails across hours (0-23, sender's timezone)
- `hour_of_day_entropy` - Entropy of hour distribution (measure of randomness)
- `hour_of_day_concentration` - Concentration index (1 - entropy/max_entropy)
- `business_hours_ratio` - Ratio of emails sent during business hours (9-17, sender's timezone) (0-1)
- `night_hours_ratio` - Ratio of emails sent during night hours (22-6, sender's timezone) (0-1)

### 📏 **Size & Content Metrics**
- `total_size_bytes` - Total size of all emails from sender
- `mean_email_size_bytes` - Mean email size
- `max_email_size_bytes` - Size of largest email
- `min_email_size_bytes` - Size of smallest email
- `emails_with_attachments` - Number of emails with attachments
- `attachment_ratio` - Ratio of emails with attachments (0-1)

### 🏷️ **Folder & Status Distribution**
- `inbox_count` - Number of emails in inbox
- `archive_count` - Number of emails in archive
- `trash_count` - Number of emails in trash
- `spam_count` - Number of emails in spam
- `read_count` - Number of read emails
- `unread_count` - Number of unread emails
- `important_count` - Number of important emails
- `starred_count` - Number of starred emails

### 🌍 **Language Analysis**
- `subject_primary_language` - Most common subject language
- `text_primary_language` - Most common text language
- `subject_languages` - List of all subject languages used
- `text_languages` - List of all text languages used
- `subject_language_diversity` - Number of different subject languages
- `text_language_diversity` - Number of different text languages
- `english_subject_ratio` - Ratio of English subjects (0-1)
- `english_text_ratio` - Ratio of English text content (0-1)
- `mean_subject_language_confidence` - Mean subject language confidence
- `mean_text_language_confidence` - Mean text language confidence

### 🤖 **Role & Type Analysis**
- `is_role_based_sender` - Whether sender uses role-based email address
- `role_type` - Type of role (admin, support, sales, etc.)
- `role_based_ratio` - Ratio of role-based emails (0-1)

### 📝 **Content Analysis**
- `mean_subject_length_chars` - Mean subject length in characters
- `std_subject_length_chars` - Standard deviation of subject length (characters)
- `min_subject_length_chars` - Shortest subject length (characters)
- `max_subject_length_chars` - Longest subject length (characters)
- `subject_length_cv` - Coefficient of variation of subject length
- `subject_length_entropy` - Entropy of subject length distribution

- `mean_text_length_chars` - Mean text length in characters
- `std_text_length_chars` - Standard deviation of text length (characters)
- `min_text_length_chars` - Shortest text length (characters)
- `max_text_length_chars` - Longest text length (characters)
- `text_length_cv` - Coefficient of variation of text length
- `text_length_entropy` - Entropy of text length distribution

- `mean_subject_length_words` - Mean subject length in words
- `std_subject_length_words` - Standard deviation of subject length (words)
- `min_subject_length_words` - Shortest subject length (words)
- `max_subject_length_words` - Longest subject length (words)
- `subject_word_count_cv` - Coefficient of variation of subject word count

- `mean_text_length_words` - Mean text length in words
- `std_text_length_words` - Standard deviation of text length (words)
- `min_text_length_words` - Shortest text length (words)
- `max_text_length_words` - Longest text length (words)
- `text_word_count_cv` - Coefficient of variation of text word count

- `html_content_ratio` - Ratio of emails with HTML content (0-1)

### 🔄 **Thread & Communication Analysis**
- `thread_count` - Number of unique threads participated in
- `mean_thread_length` - Mean emails per thread
- `max_thread_length` - Longest thread participated in
- `thread_initiator_count` - Number of threads started by sender
- `thread_joiner_count` - Number of threads joined by sender
- `thread_initiator_ratio` - Ratio of threads started vs joined (0-1)

### 🎯 **Human vs Automated Indicators**
- `human_likelihood_score` - Overall human detection score (0-1)
- `personal_greeting_ratio` - Ratio of emails with personal greetings (0-1)
- `conversational_tone_ratio` - Ratio with conversational tone (0-1)
- `question_ratio` - Ratio of emails containing questions (0-1)
- `emotional_content_ratio` - Ratio with emotional content (0-1)
- `informal_language_ratio` - Ratio with informal language (0-1)
- `signature_ratio` - Ratio with signatures (0-1)

### 📊 **Engagement & Quality Metrics**
- `read_ratio` - Ratio of emails that are read (0-1)
- `importance_ratio` - Ratio marked as important (0-1)
- `star_ratio` - Ratio starred (0-1)
- `archive_ratio` - Ratio archived (0-1)
- `delete_ratio` - Ratio deleted/trashed (0-1)

### 🔍 **Domain & Identity**
- `domain` - Email domain (gmail.com, company.com, etc.)
- `is_personal_domain` - Whether using personal email domain
- `is_corporate_domain` - Whether using corporate email domain
- `domain_type` - Classification of domain type
- `name_consistency` - Whether sender name is consistent across emails
- `display_name` - Most common display name used
- `name_variations` - Number of different names used

### 📋 **Subject Pattern Analysis**
- `unique_subject_ratio` - Ratio of unique subjects (0-1)
- `repeated_subject_count` - Number of repeated subject lines
- `subject_variation_coefficient` - Coefficient of variation in subject lengths
- `subject_keywords` - Most common keywords in subjects

## Derived Features

### 🏆 **Rankings**
- `volume_rank` - Rank by total_emails
- `read_rank` - Rank by read_ratio
- `importance_rank` - Rank by importance_ratio
- `activity_rank` - Rank by emails_per_day
- `recent_activity_rank` - Rank by recent_activity_days
- `thread_rank` - Rank by thread_count
- `human_likelihood_rank` - Rank by human_likelihood_score

### 📈 **Activity Patterns**
- `activity_trend` - Recent activity trend (increasing/decreasing/stable)
- `burst_pattern` - Whether sender exhibits burst sending behavior
- `regularity_score` - How regular vs irregular the sending pattern is

## Usage Examples

```python
# Create SenderDataFrame from EmailDataFrame
sender_df = SenderDataFrame.from_email_dataframe(email_df)

# Top senders by volume
top_senders = sender_df.sort_values('total_emails', ascending=False).head(10)

# Most engaged senders (high read ratio)
engaged_senders = sender_df[sender_df['read_ratio'] > 0.8]

# Role-based senders
role_senders = sender_df[sender_df['is_role_based_sender'] == True]

# Human vs automated analysis
human_senders = sender_df[sender_df['human_likelihood_score'] > 0.7]
automated_senders = sender_df[sender_df['human_likelihood_score'] < 0.3]

# Language analysis
multilingual_senders = sender_df[sender_df['subject_language_diversity'] > 1]
english_only_senders = sender_df[sender_df['english_subject_ratio'] == 1.0]

# High importance senders
important_senders = sender_df[sender_df['importance_ratio'] > 0.8]

# Recent activity
recent_senders = sender_df[sender_df['recent_activity_days'] < 7]

# Thread participants
conversational_senders = sender_df[sender_df['thread_count'] > 5]

# Regular senders (low entropy)
regular_senders = sender_df[sender_df['day_of_week_entropy'] < 1.5]
```

## Implementation Notes

- **Performance**: Use pandas groupby operations for efficient aggregation
- **Memory**: Consider chunking for large datasets
- **Flexibility**: Allow custom aggregation functions
- **Extensibility**: Easy to add new aggregate features
- **Caching**: Cache results for repeated analysis
