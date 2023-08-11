# Human Email Detection System

## Overview

The Human Email Detection System is an advanced analysis tool that identifies email addresses belonging to real humans by analyzing email patterns, content, and sender behaviour. This system helps distinguish between personal emails from humans and automated emails from bots, newsletters, and marketing systems.

## Key Features

### 🔍 **Multi-Dimensional Analysis**
- **Content Analysis**: Examines email text for human communication patterns
- **Sender Analysis**: Evaluates sender characteristics and domain types
- **Behavioural Analysis**: Considers email sending patterns and attachments
- **Conversation Analysis**: Looks for conversational elements and questions

### 📊 **Comprehensive Scoring**
- **Human Score**: Overall likelihood the sender is human (0.0 to 1.0)
- **Component Scores**: Individual scores for content, sender, behavioural, and conversation aspects
- **Detailed Indicators**: Boolean flags for specific human/automated characteristics

### 🎯 **Flexible Thresholds**
- Adjustable human detection threshold (default: 0.6)
- Customizable scoring weights for different components
- Configurable pattern matching for different languages and styles

## How It Works

### 1. Content Analysis

The system analyzes email content for human communication patterns:

#### Positive Human Indicators
- **Personal Greetings**: "Hi", "Hello", "Dear", "Good morning"
- **Conversational Tone**: "I think", "By the way", "Let me know"
- **Questions**: Question marks, "What", "When", "How", "Can you"
- **Personal Details**: "My", "Family", "Work", "Weekend"
- **Emotional Content**: "Happy", "Sorry", "Worried", "Love"
- **Informal Language**: "Yeah", "Cool", "Awesome", "BTW"
- **Signatures**: "Best regards", "Thanks", Contact information

#### Negative Automated Indicators
- **Unsubscribe Links**: "Unsubscribe", "Opt out", "Remove from list"
- **Marketing Language**: "Limited time", "Act now", "Exclusive offer"
- **Legal Disclaimers**: "Terms and conditions", "Privacy policy"
- **Bulk Email Signs**: "Do not reply", "Automated message"
- **Tracking Elements**: Tracking pixels, excessive external links
- **Promotional Content**: "Sale", "Discount", "Free", "Save"

### 2. Sender Analysis

Evaluates sender characteristics:

- **Real Name**: Presence of a human-like display name
- **Personal Domain**: Gmail, Yahoo, Hotmail, Outlook, etc.
- **Consistent Naming**: Proper first/last name format

### 3. Behavioural Analysis

Considers email sending patterns:

- **Attachments**: Human emails often include files
- **Sending Times**: Irregular patterns vs. scheduled sending
- **Subject Variation**: Variable subject lengths vs. templates

### 4. Conversation Analysis

Looks for conversational elements:

- **Questions**: Asking for information or clarification
- **Conversational Flow**: Natural back-and-forth communication
- **Thread Participation**: Engaging in email conversations

## Usage Examples

### Basic Human Email Detection

```python
from gmaildr import Gmail
from gmaildr.analysis import detect_human_emails, get_human_sender_summary

# Initialize Gmail connection
gmail = Gmail()

# Get emails with text content
emails_df = gmail.get_emails(
    days=30,
    include_text=True,
    include_metrics=True
)

# Detect human emails
human_emails_df = detect_human_emails(
    emails_df=emails_df,
    human_threshold=0.6
)

# Get summary statistics
summary = get_human_sender_summary(human_emails_df)
print(summary)
```

### Advanced Analysis with Custom Threshold

```python
from gmaildr.analysis import HumanEmailDetector

# Create detector instance
detector = HumanEmailDetector()

# Analyze specific sender
sender_score = detector.analyze_sender_emails(
    emails_df=emails_df,
    sender_email="colleague@company.com"
)

print(f"Human Score: {sender_score.human_score:.3f}")
print(f"Content Score: {sender_score.content_score:.3f}")
print(f"Has Personal Greeting: {sender_score.has_personal_greeting}")
print(f"Has Questions: {sender_score.has_questions}")
```

### Filtering Human vs Automated Emails

```python
# Filter for human senders only
human_senders = human_emails_df[human_emails_df['is_human_sender'] == True]

# Filter for automated senders only
automated_senders = human_emails_df[human_emails_df['is_human_sender'] == False]

# Get top human senders
top_human = human_senders.groupby('sender_email').agg({
    'human_score': 'mean',
    'sender_name': 'first',
    'subject': 'count'
}).sort_values('human_score', ascending=False)
```

## Configuration Options

### Human Detection Threshold

```python
# Strict detection (fewer false positives)
strict_humans = detect_human_emails(emails_df, human_threshold=0.8)

# Relaxed detection (more inclusive)
relaxed_humans = detect_human_emails(emails_df, human_threshold=0.4)
```

### Custom Pattern Matching

```python
from gmaildr.analysis import HumanEmailDetector

detector = HumanEmailDetector()

# Add custom patterns (advanced usage)
detector.PERSONAL_GREETING_PATTERNS.append(r'\b(ciao|bonjour|hola)\b')
detector.CONVERSATIONAL_PATTERNS.append(r'\b(by the way|btw)\b')
```

## Scoring System

### Overall Human Score (0.0 to 1.0)

The overall score is a weighted combination of four component scores:

- **Content Score (40%)**: Based on text analysis and human indicators
- **Sender Score (20%)**: Based on sender characteristics
- **Behavioural Score (20%)**: Based on sending patterns
- **Conversation Score (20%)**: Based on conversational elements

### Component Scores

Each component score ranges from 0.0 to 1.0:

- **Content Score**: Positive indicators minus negative indicators
- **Sender Score**: Percentage of positive sender characteristics
- **Behavioural Score**: Based on attachment presence and sending patterns
- **Conversation Score**: Based on questions and conversational tone

### Classification Thresholds

- **Human**: Score ≥ 0.6 (default)
- **Mixed**: Score between 0.3 and 0.6
- **Automated**: Score < 0.3

## Performance Considerations

### Processing Speed

- **Small datasets** (< 1,000 emails): Real-time processing
- **Medium datasets** (1,000-10,000 emails): Several seconds
- **Large datasets** (> 10,000 emails): Use batch processing

### Memory Usage

- **Text content**: Requires significant memory for large datasets
- **Caching**: Results are cached for repeated analysis
- **Batch processing**: Recommended for large email collections

### Accuracy

- **High accuracy** for clear human vs automated emails
- **Medium accuracy** for mixed-content emails
- **Lower accuracy** for emails in languages other than English

## Best Practices

### 1. **Choose Appropriate Thresholds**

```python
# For strict filtering (fewer false positives)
human_threshold = 0.7

# For balanced detection
human_threshold = 0.6

# For inclusive filtering (fewer false negatives)
human_threshold = 0.4
```

### 2. **Combine with Other Filters**

```python
# Combine human detection with other filters
human_important = human_emails_df[
    (human_emails_df['is_human_sender'] == True) &
    (human_emails_df['is_important'] == True)
]
```

### 3. **Use for Email Management**

```python
# Move automated emails to archive
automated_emails = human_emails_df[human_emails_df['is_human_sender'] == False]
message_ids = automated_emails['message_id'].tolist()
gmail.batch_move_to_archive(message_ids)
```

### 4. **Monitor and Adjust**

```python
# Review classification results
summary = get_human_sender_summary(human_emails_df)
print(f"Human senders: {summary[summary['sender_type'] == 'human']['sender_count'].iloc[0]}")
print(f"Automated senders: {summary[summary['sender_type'] == 'automated']['sender_count'].iloc[0]}")
```

## Limitations and Considerations

### Language Support

- **Primary**: English language emails
- **Secondary**: Basic support for common phrases in other languages
- **Customization**: Can be extended with language-specific patterns

### False Positives/Negatives

- **False Positives**: Well-written automated emails may be classified as human
- **False Negatives**: Formal business emails may be classified as automated
- **Mitigation**: Adjust thresholds based on your specific use case

### Privacy Considerations

- **Text Analysis**: Analyzes email content for patterns
- **Data Storage**: Results can be exported and stored
- **Compliance**: Ensure compliance with privacy regulations

## Troubleshooting

### Common Issues

1. **Low Human Scores for Known Humans**
   - Check if emails have text content (`include_text=True`)
   - Lower the human threshold
   - Review sender characteristics

2. **High Human Scores for Automated Emails**
   - Increase the human threshold
   - Check for marketing language patterns
   - Review unsubscribe link detection

3. **Slow Processing**
   - Use batch processing for large datasets
   - Reduce the number of days analyzed
   - Disable progress bars for faster processing

### Debugging

```python
# Get detailed scores for debugging
detector = HumanEmailDetector()
score = detector.analyze_single_email(
    text_content="Your email content here",
    subject="Your subject here",
    sender_email="sender@example.com"
)

print(f"Content Score: {score.content_score}")
print(f"Has Personal Greeting: {score.has_personal_greeting}")
print(f"Has Marketing Language: {score.has_marketing_language}")
```

## Future Enhancements

### Planned Features

- **Multi-language Support**: Enhanced pattern matching for multiple languages
- **Machine Learning**: ML-based classification for improved accuracy
- **Behavioural Analysis**: More sophisticated sending pattern analysis
- **Thread Analysis**: Conversation flow and reply chain analysis
- **Custom Training**: User-specific training for improved accuracy

### Contributing

To contribute to the human email detection system:

1. **Add Patterns**: Extend pattern lists for better detection
2. **Improve Scoring**: Enhance scoring algorithms
3. **Add Tests**: Create test cases for edge cases
4. **Documentation**: Improve documentation and examples

## API Reference

### Classes

#### `HumanEmailDetector`

Main detector class for analyzing emails.

**Methods:**
- `analyze_single_email()`: Analyze a single email
- `analyze_sender_emails()`: Analyze all emails from a sender

#### `HumanEmailScore`

Container for human email detection scores and indicators.

**Attributes:**
- `human_score`: Overall human likelihood (0.0 to 1.0)
- `content_score`: Content-based score
- `sender_score`: Sender-based score
- `behavioural_score`: Behavioural-based score
- `conversation_score`: Conversation-based score

### Functions

#### `detect_human_emails()`

Detect human email addresses from a DataFrame.

**Parameters:**
- `emails_df`: DataFrame containing email data
- `human_threshold`: Minimum score to classify as human (default: 0.6)
- `show_progress`: Whether to show progress bar (default: True)

#### `get_human_sender_summary()`

Get summary statistics for human vs automated senders.

**Parameters:**
- `emails_df`: DataFrame with human detection results
- `human_threshold`: Threshold used for classification

For more detailed API documentation, see the source code and test files.
