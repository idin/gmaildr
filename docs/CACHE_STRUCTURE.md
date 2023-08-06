# GmailWiz Cache System Documentation

## Overview

The GmailWiz cache system provides intelligent caching of email data to improve performance and reduce API calls. The cache stores emails on disk in an organized, indexed structure that supports schema versioning and intelligent merging.

## Cache Directory Structure

```
cache/
├── emails/                    # Individual email files organized by date
│   ├── 2024-01-15/           # Date-based subdirectories (YYYY-MM-DD)
│   │   ├── message_id_1.json # Individual email cache files
│   │   ├── message_id_2.json
│   │   └── ...
│   ├── 2024-01-16/
│   │   ├── message_id_3.json
│   │   └── ...
│   └── ...
└── metadata/                  # Cache metadata and indexes
    ├── message_index.json     # Quick lookup by message ID
    ├── date_index.json        # Messages organized by date
    └── schema_version.json    # Current schema version info
```

## File Formats

### Email Cache Files (`emails/YYYY-MM-DD/message_id.json`)

Each email is stored as a JSON file containing:

```json
{
  "message_id": "18c1234567890abc",
  "sender_email": "sender@example.com",
  "sender_name": "Sender Name",
  "subject": "Email Subject",
  "date_received": "2024-01-15T10:30:00+00:00",
  "size_bytes": 2048,
  "labels": ["INBOX", "IMPORTANT"],
  "thread_id": "18c1234567890abc",
  "snippet": "Email snippet text...",
  "has_attachments": false,
  "is_read": true,
  "is_important": false,
  "text_content": "Full email body text...",  // Optional, only if include_text=True
  "metadata": {
    "cached_at": "2024-01-15T15:45:30.123456",
    "file_path": "/path/to/cache/emails/2024-01-15/18c1234567890abc.json",
    "schema_version": "1.0"
  }
}
```

### Message Index (`metadata/message_index.json`)

Quick lookup index for finding cached emails:

```json
{
  "18c1234567890abc": {
    "date": "2024-01-15",
    "file_path": "emails/2024-01-15/18c1234567890abc.json"
  },
  "18c1234567890def": {
    "date": "2024-01-15", 
    "file_path": "emails/2024-01-15/18c1234567890def.json"
  }
}
```

### Date Index (`metadata/date_index.json`)

Messages organized by date for efficient date range queries:

```json
{
  "2024-01-15": [
    "18c1234567890abc",
    "18c1234567890def"
  ],
  "2024-01-16": [
    "18c1234567890ghi"
  ]
}
```

### Schema Version (`metadata/schema_version.json`)

Tracks the current schema version for cache validation:

```json
{
  "schema_version": "1.0",
  "last_updated": "2024-01-15T15:45:30.123456"
}
```

## Cache Components

### 1. EmailCacheManager

**Location**: `gmailwiz/cache/cache_manager.py`

**Purpose**: Main orchestrator for all cache operations.

**Key Methods**:
- `get_emails_with_cache()`: Main method for retrieving emails with caching
- `get_cache_stats()`: Get comprehensive cache statistics
- `get_cache_access_stats()`: Get cache hit/miss statistics
- `cleanup_cache()`: Remove old cached emails
- `invalidate_cache()`: Clear entire cache

**Access Counters**:
- `cache_hits`: Number of successful cache retrievals
- `cache_misses`: Number of cache misses requiring API calls
- `cache_writes`: Number of new emails written to cache
- `cache_updates`: Number of cache updates
- `hit_rate_percent`: Cache hit rate percentage

### 2. EmailFileStorage

**Location**: `gmailwiz/cache/file_storage.py`

**Purpose**: Handles individual file operations for cached emails.

**Key Methods**:
- `save_email()`: Save email data to cache file
- `load_email()`: Load email data from cache file
- `delete_email()`: Remove email from cache
- `get_cache_stats()`: Get file storage statistics

### 3. EmailIndexManager

**Location**: `gmailwiz/cache/index_manager.py`

**Purpose**: Manages quick lookup indexes for efficient cache operations.

**Key Methods**:
- `build_indexes()`: Rebuild all indexes from cache files
- `add_message_to_index()`: Add message to indexes
- `remove_message_from_index()`: Remove message from indexes
- `get_cached_message_ids()`: Get message IDs in date range
- `get_message_info()`: Get message metadata from index

### 4. EmailSchemaManager

**Location**: `gmailwiz/cache/schema_manager.py`

**Purpose**: Handles schema versioning and intelligent merging of cached data.

**Key Methods**:
- `is_schema_valid()`: Check if cached data matches current schema
- `upgrade_schema()`: Upgrade cached data to current schema
- `merge_emails()`: Intelligently merge cached and fresh data

### 5. CacheConfig

**Location**: `gmailwiz/cache/cache_config.py`

**Purpose**: Manages cache configuration and directory paths.

**Key Settings**:
- `cache_dir`: Root cache directory
- `max_cache_age_days`: Maximum age of cached emails (default: 30)
- `schema_version`: Current schema version (default: "1.0")
- `enable_cache`: Whether caching is enabled (default: True)

## Cache Workflow

### 1. Email Retrieval with Caching

```python
# When get_emails() is called with caching enabled:
gmail = Gmail(enable_cache=True)
df = gmail.get_emails(days=30, include_text=True)
```

**Process**:
1. **Date Range Query**: Calculate date range and get cached message IDs
2. **Fresh Data Query**: Get fresh message IDs from Gmail API
3. **Cache Hit/Miss Analysis**: Determine which emails need fresh fetching
4. **Load Cached Emails**: Load existing emails from cache (track cache hits)
5. **Fetch New Emails**: Get new emails from API (track cache misses)
6. **Cache New Emails**: Save new emails to cache (track cache writes)
7. **Merge Results**: Combine cached and fresh data
8. **Return DataFrame**: Return unified email data

### 2. Cache Statistics

```python
# Get comprehensive cache statistics
cache_stats = gmail.get_cache_stats()
# Returns: file counts, directory info, index sizes, etc.

# Get cache access statistics  
access_stats = gmail.get_cache_access_stats()
# Returns: hits, misses, writes, hit rate, etc.

# Get API usage statistics
api_stats = gmail.get_api_stats()
# Returns: total calls, text calls, general calls, last call time
```

### 3. Cache Management

```python
# Clean up old emails (older than 30 days by default)
deleted_count = gmail.cleanup_cache(max_age_days=30)

# Invalidate entire cache
success = gmail.invalidate_cache()

# Rebuild indexes
success = gmail.rebuild_cache_indexes()
```

## Performance Benefits

### 1. Reduced API Calls
- **First Run**: All emails fetched from Gmail API
- **Subsequent Runs**: Only new emails fetched, cached emails loaded from disk
- **Text Content**: Email body text cached separately to avoid re-fetching

### 2. Faster Retrieval
- **Cached Emails**: Load from disk (much faster than API calls)
- **Indexed Lookups**: Quick message ID and date range queries
- **Batch Operations**: Efficient bulk loading of cached data

### 3. Intelligent Merging
- **Schema Versioning**: Automatic upgrade of old cache formats
- **Partial Updates**: Only fetch missing or changed data
- **Conflict Resolution**: Smart merging of cached and fresh data

## Configuration Options

### Cache Settings

```python
# Disable caching entirely
gmail = Gmail(enable_cache=False)

# Custom cache directory
from gmailwiz.cache import CacheConfig
config = CacheConfig(
    cache_dir="/custom/cache/path",
    max_cache_age_days=60,
    schema_version="1.1"
)
```

### Cache Behavior

```python
# Get emails with different caching scenarios
df = gmail.get_emails(
    days=30,
    include_text=True,      # Cache includes text content
    include_metrics=True,   # Cache includes analysis metrics
    use_batch=True         # Use batch API calls for new emails
)
```

## Monitoring and Debugging

### Cache Statistics

```python
# Monitor cache performance
access_stats = gmail.get_cache_access_stats()
print(f"Cache hit rate: {access_stats['hit_rate_percent']}%")
print(f"Total requests: {access_stats['total_requests']}")
print(f"Cache hits: {access_stats['cache_hits']}")
print(f"Cache misses: {access_stats['cache_misses']}")

# Monitor API usage
api_stats = gmail.get_api_stats()
print(f"Total API calls: {api_stats['total_api_calls']}")
print(f"Text API calls: {api_stats['text_api_calls']}")
print(f"General API calls: {api_stats['general_api_calls']}")
```

### Cache Directory Inspection

```bash
# Check cache directory structure
ls -la cache/
ls -la cache/emails/
ls -la cache/metadata/

# Check cache file sizes
du -sh cache/
find cache/ -name "*.json" | wc -l
```

## Best Practices

### 1. Cache Management
- **Regular Cleanup**: Run `cleanup_cache()` periodically to remove old emails
- **Monitor Size**: Check cache directory size to prevent disk space issues
- **Schema Updates**: Cache automatically handles schema version changes

### 2. Performance Optimization
- **Text Content**: Only enable `include_text=True` when needed (increases cache size)
- **Batch Operations**: Use `use_batch=True` for better API performance
- **Date Ranges**: Use specific date ranges to limit cache scope

### 3. Troubleshooting
- **Cache Corruption**: Use `invalidate_cache()` to clear and rebuild
- **Index Issues**: Use `rebuild_cache_indexes()` to fix index problems
- **Schema Issues**: Cache automatically upgrades old schemas

## Limitations and Considerations

### 1. Disk Space
- **Text Content**: Can significantly increase cache size
- **Long Date Ranges**: More emails = more disk usage
- **Cleanup**: Regular cleanup prevents unlimited growth

### 2. API Limits
- **Rate Limiting**: Cache reduces but doesn't eliminate API calls
- **Quota Management**: Monitor API usage with `get_api_stats()`
- **Fresh Data**: New emails still require API calls

### 3. Data Consistency
- **Real-time Updates**: Cache may not reflect recent email changes
- **Label Changes**: Email labels may be outdated in cache
- **Manual Refresh**: Use `invalidate_cache()` for fresh data

## Future Enhancements

### Planned Features
- **Compression**: Gzip compression for cache files
- **Incremental Updates**: Smart detection of changed emails
- **Background Sync**: Automatic cache updates in background
- **Cache Sharing**: Shared cache across multiple instances
- **Cloud Storage**: Support for cloud-based cache storage
