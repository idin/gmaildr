# GmailWiz API Improvements

## Current Issues

### 1. Clumsy DataFrame Operations
```python
# Current (clumsy)
emails = gmail.get_emails(days=7)
message_ids = emails['message_id'].tolist()
gmail.modify_labels(message_ids=message_ids, remove_labels='TRASH')
```

### 2. Confusing Label vs Folder Semantics
```python
# Current (confusing)
gmail.modify_labels(message_ids=ids, remove_labels='TRASH')  # TRASH is treated as a label
gmail.get_emails(in_folder='trash')  # But also treated as a folder
```

### 3. Inconsistent Single vs List Parameters
```python
# Current (inconsistent)
gmail.modify_labels(message_ids=ids, add_labels='LABEL')     # Single string
gmail.modify_labels(message_ids=ids, add_labels=['LABEL1', 'LABEL2'])  # List
```

## Proposed Elegant API

### 1. Direct Email Operations
```python
# New (elegant)
emails = gmail.get_emails(days=7)
emails.move_to_archive()  # Direct operation on DataFrame
emails.mark_as_read()
emails.star()
emails.move_to_trash()
```

### 2. Folder-Specific Methods
```python
# New (clear semantics)
gmail.move_to_trash(message_ids)      # Clear folder operation
gmail.move_to_archive(message_ids)    # Clear folder operation
gmail.move_to_inbox(message_ids)      # Clear folder operation
gmail.add_label(message_ids, 'WORK')  # Clear label operation
gmail.remove_label(message_ids, 'SPAM')  # Clear label operation
```

### 3. Method Chaining
```python
# New (fluent API)
gmail.get_emails(days=7)\
    .filter(is_unread=True)\
    .mark_as_read()\
    .add_label('PROCESSED')
```

### 4. Simplified Parameters
```python
# New (consistent)
gmail.add_label(message_ids, 'WORK')           # Single label
gmail.add_labels(message_ids, ['WORK', 'URGENT'])  # Multiple labels
gmail.remove_label(message_ids, 'SPAM')        # Single label
gmail.remove_labels(message_ids, ['SPAM', 'PROMO'])  # Multiple labels
```

## Implementation Plan

### Phase 1: Add Direct DataFrame Methods
```python
class EmailDataFrame(pd.DataFrame):
    def move_to_archive(self):
        """Move all emails in this DataFrame to archive."""
        message_ids = self['message_id'].tolist()
        return self._gmail_client.move_to_archive(message_ids)
    
    def move_to_trash(self):
        """Move all emails in this DataFrame to trash."""
        message_ids = self['message_id'].tolist()
        return self._gmail_client.move_to_trash(message_ids)
    
    def mark_as_read(self):
        """Mark all emails in this DataFrame as read."""
        message_ids = self['message_id'].tolist()
        return self._gmail_client.mark_as_read(message_ids)
    
    def star(self):
        """Star all emails in this DataFrame."""
        message_ids = self['message_id'].tolist()
        return self._gmail_client.star_emails(message_ids)
```

### Phase 2: Add Folder-Specific Methods
```python
class Gmail:
    def move_to_trash(self, message_ids: Union[str, List[str]]) -> bool:
        """Move emails to trash (clear INBOX label, add TRASH label)."""
        return self.modify_labels(message_ids, remove_labels='INBOX', add_labels='TRASH')
    
    def move_to_archive(self, message_ids: Union[str, List[str]]) -> bool:
        """Move emails to archive (remove INBOX label)."""
        return self.modify_labels(message_ids, remove_labels='INBOX')
    
    def move_to_inbox(self, message_ids: Union[str, List[str]]) -> bool:
        """Move emails to inbox (add INBOX label, remove TRASH/SPAM)."""
        return self.modify_labels(message_ids, add_labels='INBOX', remove_labels=['TRASH', 'SPAM'])
```

### Phase 3: Add Method Chaining
```python
class EmailQuery:
    def __init__(self, gmail_client):
        self.gmail = gmail_client
        self.filters = {}
    
    def filter(self, **kwargs):
        """Add filters to the query."""
        self.filters.update(kwargs)
        return self
    
    def get(self):
        """Execute the query and return EmailDataFrame."""
        return self.gmail.get_emails(**self.filters)
    
    def mark_as_read(self):
        """Get emails and mark them as read."""
        emails = self.get()
        return emails.mark_as_read()
```

## Usage Examples

### Current vs New API

#### Moving Trash to Archive
```python
# Current
trash_emails = gmail.get_emails(days=365, in_folder='trash')
message_ids = trash_emails['message_id'].tolist()
gmail.modify_labels(message_ids=message_ids, remove_labels='TRASH')

# New
trash_emails = gmail.get_emails(days=365, in_folder='trash')
trash_emails.move_to_archive()

# Or even simpler
gmail.get_emails(days=365, in_folder='trash').move_to_archive()
```

#### Processing Unread Emails
```python
# Current
unread = gmail.get_emails(days=7, is_unread=True)
message_ids = unread['message_id'].tolist()
gmail.mark_as_read(message_ids)
gmail.modify_labels(message_ids=message_ids, add_labels='PROCESSED')

# New
gmail.get_emails(days=7, is_unread=True)\
    .mark_as_read()\
    .add_label('PROCESSED')
```

#### Label Management
```python
# Current
work_emails = gmail.get_emails(from_sender='boss@company.com')
message_ids = work_emails['message_id'].tolist()
gmail.modify_labels(message_ids=message_ids, add_labels=['WORK', 'IMPORTANT'])

# New
gmail.get_emails(from_sender='boss@company.com')\
    .add_labels(['WORK', 'IMPORTANT'])
```

## Benefits

1. **More Intuitive**: Operations feel natural and readable
2. **Less Code**: Fewer lines to accomplish the same tasks
3. **Clear Semantics**: Distinction between folders and labels
4. **Method Chaining**: Fluent API for complex operations
5. **Type Safety**: Better IDE support and error detection
6. **Consistency**: Uniform parameter handling

## Migration Strategy

1. **Backward Compatibility**: Keep existing methods working
2. **Gradual Migration**: Add new methods alongside old ones
3. **Deprecation Warnings**: Warn users about old methods
4. **Documentation**: Update examples to use new API
5. **Testing**: Comprehensive tests for new methods
