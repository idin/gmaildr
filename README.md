# Gmail Doctor 🩻

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
# Get all emails in trash from past year
gmail = Gmail()
trash_emails = gmail.get_trash_emails(days=365)

# Move them to archive using EmailDataFrame methods
trash_emails.move_to_archive()

# Or move them back to inbox
trash_emails.move_to_inbox()
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

# Add label using EmailDataFrame methods
work_emails.add_label(label_id)

# Or add multiple labels
work_emails.add_label(['WORK', 'URGENT'])

# Remove labels
work_emails.remove_label('SPAM')

# Check if label exists
if gmail.has_label("Project_Alpha"):
    print("Project_Alpha label exists")
```

### 📊 Batch Operations
```python
# Mark multiple emails as read
emails = gmail.get_emails(days=1, is_unread=True)
emails.mark_as_read()

# Star important emails
important_emails = gmail.get_emails(days=7, is_important=True)
important_emails.star()

# Move emails to trash
old_emails = gmail.get_emails(days=365, is_unread=True)
old_emails.move_to_trash()
```

## Installation

### From Source

```bash
git clone https://github.com/idin/gmaildr.git
cd gmaildr
pip install -e .
```

### Using pip (when published)

```bash
pip install gmaildr
```

## Quick Start

### 🚀 First-Time Setup

GmailWiz requires Google OAuth2 credentials to access your Gmail account. We've made this process as simple as possible!

#### Option 1: Automatic Setup (Recommended)

Run our setup script to get guided through the entire process:

```bash
python misc/gmail_setup.py
```

This script will:
- ✅ Create the necessary directories
- 📋 Guide you through Google Cloud Console setup
- 🔐 Test your authentication
- 🎉 Confirm everything is working

#### Option 2: Credentials Template Creator (For Beginners)

If you're new to OAuth2 setup, start with our template creator:

```bash
python misc/create_credentials_template.py
```

This tool will:
- 📝 Create a credentials file template
- 📋 Show step-by-step setup instructions
- 🔧 Help you get started with the right file structure

#### Option 3: Diagnostic Tool (If You're Having Issues)

If you're experiencing authentication problems, run our diagnostic tool:

```bash
python misc/gmail_diagnostic.py
```

This tool will:
- 🔍 Check your credentials file validity
- 📦 Verify all dependencies are installed
- 🌐 Test network connectivity
- 📧 Test Gmail API access
- 💡 Provide specific recommendations for any issues found

#### Option 2: Manual Setup

If you prefer to set up manually:

1. **Go to Google Cloud Console**
   - Visit [https://console.cloud.google.com/](https://console.cloud.google.com/)
   - Create a new project or select an existing one

2. **Enable Gmail API**
   - Go to "APIs & Services" > "Library"
   - Search for "Gmail API"
   - Click on it and press "Enable"

3. **Create OAuth2 Credentials**
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth 2.0 Client IDs"
   - Choose "Desktop application" as the application type
   - Give it a name (e.g., "GmailWiz")
   - Click "Create"

4. **Download Credentials**
   - Click the download button (⬇️) next to your new OAuth2 client
   - Save the JSON file as `credentials.json`

5. **Place Credentials File**
   - Create a `credentials` folder in your project root
   - Move `credentials.json` to `credentials/credentials.json`

### 🔐 First Authentication

Once you have your credentials file in place:

```python
from gmaildr.core.gmail.main import Gmail

# This will open a browser window for authentication
gmail = Gmail()

# Test that it works
emails = gmail.get_emails(days=7)
print(f"Found {len(emails)} emails in the last 7 days")
```

**Note:** The first time you run this, a browser window will open asking you to authorize GmailWiz. After authorization, your credentials will be saved and you won't need to authenticate again.

### 🔧 Troubleshooting

If you encounter authentication issues:

1. **Run the diagnostic tool:**
   ```bash
   python misc/gmail_diagnostic.py
   ```

2. **Common solutions:**
   - Delete token files: `rm credentials/token.*`
   - Re-run setup: `python misc/gmail_setup.py`
   - Check Gmail API is enabled in Google Cloud Console
   - Verify your credentials.json file is valid

3. **Still having issues?**
   - Check the error messages for specific guidance
   - Ensure you're using the correct Google account
   - Try creating a new OAuth2 client in Google Cloud Console

### 📊 Quick Analysis Examples

```bash
# Analyze last 30 days
gmaildr analyze

# Analyze last 7 days with max 500 emails
gmaildr analyze --days 7 --max-emails 500

# Export to Excel format
gmaildr analyze --format excel --output my_gmail_analysis.xlsx
```

### 📧 Email Operations with EmailDataFrame
```python
# Get emails and perform operations directly
emails = gmail.get_emails(days=7)

# Mark emails as read
emails.mark_as_read()

# Star important emails
emails.star()

# Move to different folders
emails.move_to_trash()
emails.move_to_archive()
emails.move_to_inbox()

# Filter and operate on subsets
unread_emails = emails[emails['is_unread'] == True]
unread_emails.mark_as_read()

# Chain operations
emails.filter(is_unread=True).mark_as_read().add_label('PROCESSED')
```

### 📁 Folder-Specific Methods
```python
# Get emails from specific folders
trash_emails = gmail.get_trash_emails(days=30)
archive_emails = gmail.get_archive_emails(days=90)

# Work with trash emails
trash_emails.move_to_inbox()  # Restore from trash
trash_emails.move_to_archive()  # Move to archive instead

# Work with archived emails
archive_emails.move_to_inbox()  # Move back to inbox
archive_emails.move_to_trash()  # Move to trash
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

### Analysis DataFrames for Machine Learning

GmailDr provides analysis-ready DataFrames optimized for clustering and machine learning tasks. These DataFrames automatically include all available features with proper encoding for ML algorithms.

#### EmailDataFrame Analysis

```python
from gmaildr import Gmail

gmail = Gmail()

# Get emails with text content and metrics
emails = gmail.get_emails(
    days=30,
    include_text=True,
    include_metrics=True
)

# Get analysis-ready DataFrame (auto-detects features)
analysis_df = emails.analysis_dataframe
print(f"Analysis DataFrame shape: {analysis_df.shape}")
print(f"Features: {list(analysis_df.columns)}")

# Get feature summary
summary = emails.get_feature_summary()
print(f"Total features: {summary['total_features']}")
print(f"Numeric features: {summary['numeric_count']}")
print(f"Periodic features: {summary['periodic_count']}")

# Prepare for clustering (scales features)
clustering_df = emails.prepare_for_clustering(scale_features=True)
```

**Features automatically included:**
- **Temporal features**: Hour, day of week, month (with sin/cos encoding for cyclical patterns)
- **Text features**: Word count, sentence count, capitalization ratio (when text content available)
- **Analysis metrics**: Unsubscribe links, marketing language, external links, etc. (when text content available)
- **Boolean features**: Has attachments, is read, is important
- **Categorical features**: In folder (one-hot encoded)

#### SenderDataFrame Analysis

```python
from gmaildr.sender_statistics import SenderDataFrame

# Create sender statistics
sender_df = SenderDataFrame(emails)

# Get analysis-ready DataFrame
sender_analysis_df = sender_df.analysis_dataframe
print(f"Sender Analysis DataFrame shape: {sender_analysis_df.shape}")

# Get feature summary
sender_summary = sender_df.get_feature_summary()
print(f"Sender features: {sender_summary['total_features']}")

# Prepare for clustering
sender_clustering_df = sender_df.prepare_for_clustering(scale_features=True)
```

**Features automatically included:**
- **Volume metrics**: Total emails, emails per day, unique subjects
- **Temporal patterns**: Time between emails, day/hour distributions
- **Content analysis**: Subject/text lengths, language diversity
- **Engagement metrics**: Read ratios, importance ratios, starred ratios
- **Domain analysis**: Corporate vs personal domains, role-based detection

#### Advanced Usage

```python
# Manual control over analysis parameters
analysis_df = emails.create_analysis_dataframe(drop_na_threshold=0.3)

# Custom clustering preparation
clustering_df = emails.prepare_for_clustering(
    scale_features=True,
    remove_outliers=True,
    outlier_threshold=2.5
)

# Use with scikit-learn
from sklearn.cluster import KMeans

# Cluster emails
kmeans = KMeans(n_clusters=5, random_state=42)
clusters = kmeans.fit_predict(clustering_df)

# Add cluster assignments back to original DataFrame
emails['cluster'] = clusters
```

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
git clone https://github.com/idin/gmaildr.git
cd gmaildr
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

1. Check the [documentation](https://github.com/idin/gmaildr)
2. Search [existing issues](https://github.com/idin/gmaildr/issues)
3. Create a [new issue](https://github.com/idin/gmaildr/issues/new)

## Roadmap

- [ ] Web dashboard interface
- [ ] Email categorization and clustering
- [ ] Advanced filtering options
- [ ] Email cleanup recommendations
- [ ] Integration with other email providers
- [ ] Machine learning insights
- [ ] Automated reporting schedules
