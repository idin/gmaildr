# GmailDr

A powerful Gmail analysis, management, and automation wizard. Connect to Gmail and run comprehensive analysis on your email data. Generate detailed statistics about email senders, storage usage, and email patterns to better understand and manage your Gmail inbox.

## Features

- 🔐 **Secure Gmail API Integration** - OAuth2 authentication with read-only access
- 📊 **Comprehensive Email Analysis** - Detailed sender statistics and email patterns
- 💾 **Storage Analysis** - Identify which senders use the most storage space
- 📈 **Temporal Analysis** - Understand email patterns over time
- 🖥️ **User-Friendly CLI** - Easy-to-use command-line interface
- 📁 **Multiple Export Formats** - JSON, CSV, and Excel output options
- ⚡ **Batch Processing** - Efficient handling of large email volumes
- 🎨 **Rich Console Output** - Beautiful terminal output with tables and progress bars

## Quick Examples

### 📅 Date Range Queries
```python
from gmaildr import Gmail
from datetime import datetime, timedelta

gmail = Gmail()

# Get emails from last 7 days
emails = gmail.get_emails(days=7)

# Get emails from specific date range
start_date = datetime(2024, 1, 1)
end_date = '2024-01-05' # it can be an iso date
emails = gmail.get_emails(start_date=start_date, end_date=end_date)

# Get emails from a start date for 30 days
start_date = '2024-01-01'
emails = gmail.get_emails(start_date=start_date, days=30)

# Get emails ending at a specific date, going back 7 days
end_date = datetime(2024, 1, 31)
emails = gmail.get_emails(end_date=end_date, days=7)
```

### 🗑️ Trash Management
```python
# Move all emails in trash from past year to archive
from datetime import datetime, timedelta

gmail = Gmail()
end_date = datetime.now()

# Get all emails in trash from past year
trash_emails = gmail.get_emails(
    start_date=start_date,
    end_date=end_date,
    in_folder='trash',
    days=365
)

# Move them to archive
message_ids = trash_emails['message_id'].tolist()
gmail.modify_labels(message_ids=message_ids, remove_labels='TRASH')
```

### 📧 Email Analysis with Filters
```python
# Get unread emails from specific sender in last month
emails = gmail.get_emails(
    days=30,
    from_sender="noreply@example.com",
    is_unread=True
)

# Get important emails with attachments
emails = gmail.get_emails(
    days=7,
    is_important=True,
    has_attachment=True
)

# Get emails from multiple senders
emails = gmail.get_emails(
    days=14,
    from_sender=["support@company.com", "billing@company.com"]
)
```

### 🏷️ Label Management
```python
# Create a custom label
label_id = gmail.get_label_id_or_create("Important_Work")

# Apply label to emails from specific sender
work_emails = gmail.get_emails(
    days=30,
    from_sender="boss@company.com"
)
gmail.modify_labels(
    message_ids=work_emails['message_id'].tolist(),
    add_labels=label_id
)

# Check if label exists
if gmail.has_label("Project_Alpha"):
    print("Project_Alpha label exists")
```

### 📊 Batch Operations
```python
# Mark multiple emails as read
emails = gmail.get_emails(days=1, is_unread=True)
gmail.mark_as_read(emails['message_id'].tolist())

# Star important emails
important_emails = gmail.get_emails(days=7, is_important=True)
gmail.star_email(important_emails['message_id'].tolist())

# Move emails to trash
old_emails = gmail.get_emails(days=365, is_unread=True)
gmail.move_to_trash(old_emails['message_id'].tolist())
```

## Installation

### From Source

```bash
git clone https://github.com/idin/gmailcleaner.git
cd gmailcleaner
pip install -e .
```

### Using pip (when published)

```bash
pip install gmaildr
```

## Quick Start

### 1. Set Up Google API Credentials

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Gmail API
4. Create OAuth2 credentials (Desktop application type)
5. Download the credentials JSON file and save it as `credentials.json`

### 2. Configure Gmail Cleaner

```bash
gmaildr setup --credentials-file credentials.json
```

### 3. Analyze Your Gmail

```bash
# Analyze last 30 days
gmaildr analyze

# Analyze last 7 days with max 500 emails
gmaildr analyze --days 7 --max-emails 500

# Export to Excel format
gmaildr analyze --format excel --output my_gmail_analysis.xlsx
```

## Usage

### Command Line Interface

#### Setup and Configuration

```bash
# Initial setup
gmaildr setup

# Check status
gmaildr status

# Use custom configuration file
gmaildr --config-file my_config.json analyze
```

#### Email Analysis

```bash
# Basic analysis (last 30 days)
gmaildr analyze

# Analyze specific time period
gmaildr analyze --days 90

# Limit number of emails
gmaildr analyze --max-emails 1000

# Save to specific file
gmaildr analyze --output analysis.json --format json

# Disable caching
gmaildr analyze --no-cache
```

#### Quick Insights

```bash
# Show top senders
gmaildr top-senders --limit 10

# Filter by specific sender
gmaildr top-senders --sender example@domain.com
```

### Python API

```python
from gmaildr import GmailClient, EmailAnalyzer
from datetime import datetime, timedelta

# Initialize client
gmail_client = GmailClient(credentials_file="credentials.json")
gmail_client.authenticate()

# Create analyzer
analyzer = EmailAnalyzer(gmail_client)

# Analyze last 30 days
end_date = datetime.now()
start_date = end_date - timedelta(days=30)

report = analyzer.analyze_emails_from_date_range(
    start_date=start_date,
    end_date=end_date,
    max_emails=1000
)

# Get top senders by email count
top_senders = report.get_top_senders_by_count(limit=10)
for sender in top_senders:
    print(f"{sender.sender_email}: {sender.total_emails} emails")

# Get storage analysis
storage_analysis = analyzer.get_storage_analysis()
print(f"Total storage: {storage_analysis['total_size_gb']:.2f} GB")

# Export to DataFrame for custom analysis
df = analyzer.export_to_dataframe()
print(df.head())
```

## Configuration

Gmail Cleaner can be configured through:

1. **Configuration file** (`gmail_cleaner_config.json`)
2. **Environment variables**
3. **Command-line options**

### Configuration File Example

```json
{
  "credentials_file": "credentials.json",
  "token_file": "token.pickle",
  "default_max_emails": 1000,
  "default_batch_size": 100,
  "output_directory": "output",
  "export_format": "json",
  "log_level": "INFO",
  "enable_cache": true,
  "cache_directory": "cache",
  "cache_expiry_hours": 24
}
```

### Environment Variables

```bash
export GMAIL_CREDENTIALS_FILE="path/to/credentials.json"
export GMAIL_TOKEN_FILE="path/to/token.pickle"
export GMAIL_MAX_EMAILS=1000
export GMAIL_BATCH_SIZE=100
export GMAIL_OUTPUT_DIR="output"
export GMAIL_EXPORT_FORMAT="json"
export GMAIL_LOG_LEVEL="INFO"
export GMAIL_ENABLE_CACHE=true
export GMAIL_CACHE_DIR="cache"
export GMAIL_CACHE_EXPIRY_HOURS=24
```

## Analysis Features

### Sender Statistics

- Total emails per sender
- Total storage usage per sender
- Average email size
- Read/unread ratios
- Important email counts
- First and last email dates
- Label distribution

### Storage Analysis

- Total storage usage
- Storage distribution by sender
- Largest emails identification
- Storage percentiles
- Storage efficiency metrics

### Temporal Analysis

- Daily email patterns
- Weekly email patterns
- Monthly trends
- Hourly distribution
- Day-of-week patterns
- Peak usage identification

## Output Formats

### JSON Output
Complete analysis data with all metadata and statistics.

### CSV Output
Tabular data suitable for spreadsheet analysis.

### Excel Output
Formatted Excel file with multiple sheets for different analysis aspects.

## Security and Privacy

- **Read-only access**: Gmail Cleaner only requests read-only permissions
- **Local processing**: All analysis is performed locally on your machine
- **No data transmission**: Your email data never leaves your computer
- **Secure authentication**: Uses Google's OAuth2 for secure authentication
- **Credential management**: Securely stores and manages API credentials

## Development

### Setting Up Development Environment

```bash
git clone https://github.com/idin/gmailcleaner.git
cd gmailcleaner
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
pytest --cov=gmail_cleaner
```

### Code Quality

```bash
# Format code
black gmail_cleaner/

# Lint code
flake8 gmail_cleaner/

# Type checking
mypy gmail_cleaner/
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Google Gmail API for providing access to email data
- Rich library for beautiful terminal output
- Click library for command-line interface
- Pandas for data analysis capabilities

## Support

If you encounter any issues or have questions:

1. Check the [documentation](https://github.com/idin/gmailcleaner)
2. Search [existing issues](https://github.com/idin/gmailcleaner/issues)
3. Create a [new issue](https://github.com/idin/gmailcleaner/issues/new)

## Roadmap

- [ ] Web dashboard interface
- [ ] Email categorization and clustering
- [ ] Advanced filtering options
- [ ] Email cleanup recommendations
- [ ] Integration with other email providers
- [ ] Machine learning insights
- [ ] Automated reporting schedules
