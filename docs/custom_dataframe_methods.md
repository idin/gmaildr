# Custom DataFrame Methods Documentation

This document lists all the methods that existed on the custom `EmailDataFrame` and `SenderDataFrame` classes before they were removed in favor of regular pandas DataFrames.

## 📧 EmailDataFrame Class Methods

### Constructor and Properties

#### `_constructor` Property
```python
@property
def _constructor(self):
    """Return the class to use for DataFrame operations."""
    return EmailDataFrame
```

#### `senders_dataframe` Property
```python
@property
def senders_dataframe(self):
    """
    Get a SenderDataFrame representation.
    
    Returns:
        SenderDataFrame
    """
    from ..sender_dataframe.sender_dataframe import SenderDataFrame
    return SenderDataFrame(self, gmail=self._gmail_instance)
```

#### `ml_dataframe` Property
```python
@property
def ml_dataframe(self):
    """
    Transform features for machine learning.
    
    This creates a new Email_ML_DataFrame with transformed features suitable for ML.
    
    Returns:
        Email_ML_DataFrame with transformed features
    """
    from .transform_features_for_ml import transform_email_features_for_ml
    from .email_ml_dataframe import Email_ML_DataFrame
    
    # Transform the features - function returns pandas DataFrame with ML features
    ml_features_df = transform_email_features_for_ml(email_df=self)
    
    # Validate that ML DataFrame contains required columns and excludes non-ML columns
    if 'message_id' not in ml_features_df.columns:
        raise KeyError("ML DataFrame must contain 'message_id' column")
    
    # Check for non-ML columns that should not be present
    non_ml_columns = [
        'sender_email', 'timestamp', 'sender_local_timestamp', 'subject', 
        'text_content', 'thread_id', 'recipient_email', 'labels'
    ]
    found_non_ml_columns = [col for col in non_ml_columns if col in ml_features_df.columns]
    if found_non_ml_columns:
        raise KeyError(f"ML DataFrame must not contain non-ML columns: {found_non_ml_columns}")
    
    return Email_ML_DataFrame(ml_features_df, gmail=self._gmail_instance)
```

### Internal Helper Methods

#### `_get_message_ids()` Method
```python
def _get_message_ids(self) -> List[str]:
    """Get message IDs from the DataFrame."""
    if 'message_id' not in self.columns:
        raise ValueError("DataFrame must contain 'message_id' column")
    return self['message_id'].tolist()
```

#### `_check_gmail_instance()` Method
```python
def _check_gmail_instance(self):
    """Check if gmail instance is available."""
    if not self._gmail_instance:
        raise ValueError("Gmail instance is required for this operation")
    return self._gmail_instance
```

### Email Operations Methods

#### `move_to_archive()` Method
```python
def move_to_archive(self, show_progress: bool = True) -> Union[bool, Dict[str, bool]]:
    """
    Move all emails in this DataFrame to archive.
    
    Args:
        show_progress: Whether to show progress bar
        
    Returns:
        bool or Dict[str, bool]: Success status
    """
    gmail_instance = self._check_gmail_instance()
    message_ids = self._get_message_ids()
    if not message_ids:
        return True
    
    return gmail_instance.move_to_archive(
        message_ids=message_ids, 
        show_progress=show_progress
    )
```

#### `move_to_trash()` Method
```python
def move_to_trash(self, show_progress: bool = True) -> Union[bool, Dict[str, bool]]:
    """
    Move all emails in this DataFrame to trash.
    
    Args:
        show_progress: Whether to show progress bar
        
    Returns:
        bool or Dict[str, bool]: Success status
    """
    gmail_instance = self._check_gmail_instance()
    message_ids = self._get_message_ids()
    if not message_ids:
        return True
    
    return gmail_instance.move_to_trash(
        message_ids=message_ids, 
        show_progress=show_progress
    )
```

#### `move_to_inbox()` Method
```python
def move_to_inbox(self, show_progress: bool = True) -> Union[bool, Dict[str, bool]]:
    """
    Move all emails in this DataFrame to inbox.
    
    Args:
        show_progress: Whether to show progress bar
        
    Returns:
        bool or Dict[str, bool]: Success status
    """
    gmail_instance = self._check_gmail_instance()
    message_ids = self._get_message_ids()
    if not message_ids:
        return True
    
    return gmail_instance.move_to_inbox(
        message_ids=message_ids,
        show_progress=show_progress
    )
```

#### `mark_as_read()` Method
```python
def mark_as_read(self, show_progress: bool = True) -> Union[bool, Dict[str, bool]]:
    """
    Mark all emails in this DataFrame as read.
    
    Args:
        show_progress: Whether to show progress bar
        
    Returns:
        bool or Dict[str, bool]: Success status
    """
    gmail_instance = self._check_gmail_instance()
    message_ids = self._get_message_ids()
    if not message_ids:
        return True
    
    return gmail_instance.mark_as_read(
        message_id=message_ids, 
        show_progress=show_progress
    )
```

#### `mark_as_unread()` Method
```python
def mark_as_unread(self, show_progress: bool = True) -> Union[bool, Dict[str, bool]]:
    """
    Mark all emails in this DataFrame as unread.
    
    Args:
        show_progress: Whether to show progress bar
        
    Returns:
        bool or Dict[str, bool]: Success status
    """
    gmail_instance = self._check_gmail_instance()
    message_ids = self._get_message_ids()
    if not message_ids:
        return True
    
    # Note: mark_as_unread only accepts single message_id, so we need to handle multiple
    if len(message_ids) == 1:
        return gmail_instance.mark_as_unread(message_id=message_ids[0])
    else:
        # For multiple emails, we need to use modify_labels
        return gmail_instance.modify_labels(
            message_ids=message_ids,
            add_labels=['UNREAD'],
            show_progress=show_progress
        )
```

#### `star()` Method
```python
def star(self, show_progress: bool = True) -> Union[bool, Dict[str, bool]]:
    """
    Star all emails in this DataFrame.
    
    Args:
        show_progress: Whether to show progress bar
        
    Returns:
        bool or Dict[str, bool]: Success status
    """
    gmail_instance = self._check_gmail_instance()
    message_ids = self._get_message_ids()
    if not message_ids:
        return True
    
    return gmail_instance.star_email(
        message_id=message_ids, 
        show_progress=show_progress
    )
```

#### `unstar()` Method
```python
def unstar(self, show_progress: bool = True) -> Union[bool, Dict[str, bool]]:
    """
    Remove star from all emails in this DataFrame.
    
    Args:
        show_progress: Whether to show progress bar
        
    Returns:
        bool or Dict[str, bool]: Success status
    """
    gmail_instance = self._check_gmail_instance()
    message_ids = self._get_message_ids()
    if not message_ids:
        return True
    
    # Note: unstar_email only accepts single message_id, so we need to handle multiple
    if len(message_ids) == 1:
        return gmail_instance.unstar_email(message_id=message_ids[0])
    else:
        # For multiple emails, we need to use modify_labels
        return gmail_instance.modify_labels(
            message_ids=message_ids,
            remove_labels=['STARRED'],
            show_progress=show_progress
        )
```

### Label Operations Methods

#### `add_label()` Method
```python
def add_label(self, label: Union[str, List[str]], show_progress: bool = True) -> Union[bool, Dict[str, bool]]:
    """
    Add label(s) to all emails in this DataFrame.
    
    Args:
        label: Label name(s) to add
        show_progress: Whether to show progress bar
        
    Returns:
        bool or Dict[str, bool]: Success status
    """
    gmail_instance = self._check_gmail_instance()
    message_ids = self._get_message_ids()
    if not message_ids:
        return True
    
    return gmail_instance.add_label(
        message_ids=message_ids,
        label=label,
        show_progress=show_progress
    )
```

#### `remove_label()` Method
```python
def remove_label(self, label: Union[str, List[str]], show_progress: bool = True) -> Union[bool, Dict[str, bool]]:
    """
    Remove label(s) from all emails in this DataFrame.
    
    Args:
        label: Label name(s) to remove
        show_progress: Whether to show progress bar
        
    Returns:
        bool or Dict[str, bool]: Success status
    """
    gmail_instance = self._check_gmail_instance()
    message_ids = self._get_message_ids()
    if not message_ids:
        return True
    
    return gmail_instance.remove_label(
        message_ids=message_ids,
        label=label,
        show_progress=show_progress
    )
```

#### `get_label_names()` Method
```python
def get_label_names(self) -> List[str]:
    """
    Get all unique label names from emails in this DataFrame.
    
    Returns:
        List[str]: List of unique label names
    """
    gmail_instance = self._check_gmail_instance()
    all_label_ids = set()
    for labels in self['labels']:
        if labels:
            all_label_ids.update(labels)
    # Convert label IDs to names using the new method
    return gmail_instance.get_label_names_from_ids(list(all_label_ids))
```

#### `has_label()` Method
```python
def has_label(self, label_name: str) -> 'EmailDataFrame':
    """
    Filter emails that have a specific label.
    
    Args:
        label_name: Name of the label to filter by
        
    Returns:
        EmailDataFrame: Filtered DataFrame containing only emails with the specified label
    """
    gmail_instance = self._check_gmail_instance()
    
    # Get the label ID for the given name
    label_id = gmail_instance.get_label_id(label_name)
    if not label_id:
        # If label doesn't exist, return empty DataFrame
        return EmailDataFrame(pd.DataFrame(), gmail=gmail_instance)
    
    # Filter emails that have this label ID
    mask = self['labels'].apply(lambda labels: label_id in labels if labels else False)
    return EmailDataFrame(self[mask], gmail=gmail_instance)
```

#### `has_any_label()` Method
```python
def has_any_label(self, label_names: List[str]) -> 'EmailDataFrame':
    """
    Filter emails that have any of the specified labels.
    
    Args:
        label_names: List of label names to filter by
        
    Returns:
        EmailDataFrame: Filtered DataFrame containing emails with any of the specified labels
    """
    gmail_instance = self._check_gmail_instance()
    
    # Get label IDs for all given names
    label_ids = []
    for label_name in label_names:
        label_id = gmail_instance.get_label_id(label_name)
        if label_id:
            label_ids.append(label_id)
    
    if not label_ids:
        # If no labels exist, return empty DataFrame
        return EmailDataFrame(pd.DataFrame(), gmail=gmail_instance)
    
    # Filter emails that have any of these label IDs
    mask = self['labels'].apply(lambda labels: any(label_id in labels for label_id in label_ids) if labels else False)
    return EmailDataFrame(self[mask], gmail=gmail_instance)
```

#### `has_all_labels()` Method
```python
def has_all_labels(self, label_names: List[str]) -> 'EmailDataFrame':
    """
    Filter emails that have all of the specified labels.
    
    Args:
        label_names: List of label names to filter by
        
    Returns:
        EmailDataFrame: Filtered DataFrame containing emails with all of the specified labels
    """
    gmail_instance = self._check_gmail_instance()
    
    # Get label IDs for all given names
    label_ids = []
    for label_name in label_names:
        label_id = gmail_instance.get_label_id(label_name)
        if label_id:
            label_ids.append(label_id)
    
    if not label_ids:
        # If no labels exist, return empty DataFrame
        return EmailDataFrame(pd.DataFrame(), gmail=gmail_instance)
    
    # Filter emails that have all of these label IDs
    mask = self['labels'].apply(lambda labels: all(label_id in labels for label_id in label_ids) if labels else False)
    return EmailDataFrame(self[mask], gmail=gmail_instance)
```

#### `count_by_label()` Method
```python
def count_by_label(self, label_name: str) -> int:
    """
    Count emails that have a specific label.
    
    Args:
        label_name: Name of the label to count
        
    Returns:
        int: Number of emails with the specified label
    """
    return len(self.has_label(label_name))
```

#### `get_emails_with_label()` Method
```python
def get_emails_with_label(self, label_name: str) -> 'EmailDataFrame':
    """
    Get all emails that have a specific label.
    
    Args:
        label_name: Name of the label to filter by
        
    Returns:
        EmailDataFrame: Filtered DataFrame containing only emails with the specified label
    """
    return self.has_label(label_name)
```

### Filtering Methods

#### `filter()` Method
```python
def filter(self, **kwargs) -> 'EmailDataFrame':
    """
    Filter emails in this DataFrame.
    
    Args:
        **kwargs: Filter conditions (e.g., is_unread=True, has_attachment=True)
        
    Returns:
        EmailDataFrame: Filtered DataFrame
    """
    # Start with all rows
    mask = pd.Series([True] * len(self), index=self.index)
    
    # Apply each filter condition (AND logic)
    for column, value in kwargs.items():
        if column in self.columns:
            if isinstance(value, (list, tuple)):
                # Use basic boolean indexing
                column_mask = self[column].isin(value)  # type: ignore
            else:
                # Use basic equality comparison
                column_mask = self[column] == value
            # Combine with existing mask (AND logic)
            mask = mask & column_mask
    
    # Apply the combined mask and return as EmailDataFrame
    filtered_df = self[mask]
    # Ensure we have a DataFrame, not a Series
    if isinstance(filtered_df, pd.Series):
        filtered_df = filtered_df.to_frame()
    return EmailDataFrame(filtered_df, gmail=self._gmail_instance)
```

## 👥 SenderDataFrame Class Methods

### Constructor and Properties

#### `_constructor` Property
```python
@property
def _constructor(self):
    """Return the class to use for DataFrame operations."""
    return SenderDataFrame
```

#### `senders` Property
```python
@property
def senders(self) -> Set[str]:
    """
    Get the set of sender emails in the SenderDataFrame.
    """
    return set(self['sender_email'])
```

#### `ml_dataframe` Property
```python
@property
def ml_dataframe(self) -> pd.DataFrame:
    """
    Transform features for machine learning.
    """
    from .sender_ml_dataframe import Sender_ML_DataFrame
    from .transform_features_for_ml import transform_sender_features_for_ml
    
    data = transform_sender_features_for_ml(self.dataframe)
    return Sender_ML_DataFrame(data, gmail=self.gmail)
```

### Internal Helper Methods

#### `_get_message_ids()` Method
```python
def _get_message_ids(self) -> List[str]:
    """Get message IDs from the DataFrame."""
    raise NotImplementedError("SenderDataFrame does not have message IDs")
```

### Sender Operations Methods

#### `get_emails()` Method
```python
def get_emails(
    self, *,
    days: Optional[int] = None,
    start_date: Optional[Union[datetime, str]] = None,
    end_date: Optional[Union[datetime, str]] = None,
    max_emails: Optional[int] = None,
    subject_contains: Optional[str] = None,
    subject_does_not_contain: Optional[str] = None,
    has_attachment: Optional[bool] = None,
    is_unread: Optional[bool] = None,
    is_important: Optional[bool] = None,
    in_folder: Optional[Literal['inbox', 'archive', 'spam', 'trash', 'drafts', 'sent']] = None,
    is_starred: Optional[bool] = None,
    include_text: bool = False,
    include_metrics: bool = False,
    use_batch: bool = True,
    parallelize_text_fetch: bool = False
) -> EmailDataFrame:
    return self.gmail.get_emails(
        from_sender=list(self.senders),
        days=days,
        start_date=start_date,
        end_date=end_date,
        max_emails=max_emails,
        subject_contains=subject_contains,
        subject_does_not_contain=subject_does_not_contain,
        has_attachment=has_attachment,
        is_unread=is_unread,
        is_important=is_important,
        in_folder=in_folder,
        is_starred=is_starred,
        include_text=include_text,
        include_metrics=include_metrics,
        use_batch=use_batch,
        parallelize_text_fetch=parallelize_text_fetch
    )
```

## 📋 Summary of Removed Methods

### EmailDataFrame Methods (15 total)
1. **Properties**: `_constructor`, `senders_dataframe`, `ml_dataframe`
2. **Internal**: `_get_message_ids`, `_check_gmail_instance`
3. **Email Operations**: `move_to_archive`, `move_to_trash`, `move_to_inbox`, `mark_as_read`, `mark_as_unread`, `star`, `unstar`
4. **Label Operations**: `add_label`, `remove_label`, `get_label_names`, `has_label`, `has_any_label`, `has_all_labels`, `count_by_label`, `get_emails_with_label`
5. **Filtering**: `filter`

### SenderDataFrame Methods (4 total)
1. **Properties**: `_constructor`, `senders`, `ml_dataframe`
2. **Internal**: `_get_message_ids`
3. **Sender Operations**: `get_emails`

## 🎯 Why These Methods Were Removed

The custom DataFrame classes were removed to:
1. **Eliminate pandas compatibility issues** - Custom DataFrame subclasses often conflict with pandas operations
2. **Simplify the codebase** - Regular pandas DataFrames are easier to work with
3. **Improve performance** - No overhead from custom DataFrame methods
4. **Reduce maintenance burden** - Standard pandas patterns are more maintainable

## 📚 Related Documentation

- [Email DataFrame Schema](email_dataframe_schema.md)
- [API Improvements](api_improvements.md)
- [Status](status.md)
