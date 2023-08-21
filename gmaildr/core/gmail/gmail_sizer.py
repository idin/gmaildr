from typing import Optional, List, Union, Literal, Dict, Any
import pandas as pd

from .email_operator import EmailOperator

class GmailSizer(EmailOperator):
    """
    Gmail size and folder-specific operations that inherit from EmailOperator.
    
    This class handles size calculations and folder-specific email retrieval
    operations that build upon the core email operations.
    """
    
    def get_inbox_size(
        self, *,
        days: int = 365,
        from_sender: Optional[Union[str, List[str]]] = None,
        subject_contains: Optional[str] = None,
        subject_does_not_contain: Optional[str] = None,
        has_attachment: Optional[bool] = None,
        is_unread: Optional[bool] = None,
        is_important: Optional[bool] = None,
        is_starred: Optional[bool] = None
    ) -> int:
        """
        Get the count of emails in the inbox.
        
        Args:
            days: Number of days to look back
            from_sender: Filter by sender email address(es)
            subject_contains: Filter by text in subject line
            subject_does_not_contain: Filter by text not in subject line
            has_attachment: Filter by attachment presence
            is_unread: Filter by read/unread status
            is_important: Filter by importance
            is_starred: Filter by starred status
            
        Returns:
            Number of emails in inbox
            
        Example:
            >>> count = gmail_sizer.get_inbox_size(days=30, is_unread=True)
            >>> print(f"Inbox has {count} unread emails")
        """
        return self.count_emails(
            days=days,
            in_folder='inbox',
            from_sender=from_sender,
            subject_contains=subject_contains,
            subject_does_not_contain=subject_does_not_contain,
            has_attachment=has_attachment,
            is_unread=is_unread,
            is_important=is_important,
            is_starred=is_starred
        )
    
    def get_trash_size(
        self, *,
        days: int = 365,
        from_sender: Optional[Union[str, List[str]]] = None,
        subject_contains: Optional[str] = None,
        subject_does_not_contain: Optional[str] = None,
        has_attachment: Optional[bool] = None,
        is_unread: Optional[bool] = None,
        is_important: Optional[bool] = None,
        is_starred: Optional[bool] = None
    ) -> int:
        """
        Get the count of emails in the trash.
        
        Args:
            days: Number of days to look back
            from_sender: Filter by sender email address(es)
            subject_contains: Filter by text in subject line
            subject_does_not_contain: Filter by text not in subject line
            has_attachment: Filter by attachment presence
            is_unread: Filter by read/unread status
            is_important: Filter by importance
            is_starred: Filter by starred status
            
        Returns:
            Number of emails in trash
            
        Example:
            >>> count = gmail_sizer.get_trash_size(days=30, has_attachment=True)
            >>> print(f"Trash has {count} emails with attachments")
        """
        return self.count_emails(
            days=days,
            in_folder='trash',
            from_sender=from_sender,
            subject_contains=subject_contains,
            subject_does_not_contain=subject_does_not_contain,
            has_attachment=has_attachment,
            is_unread=is_unread,
            is_important=is_important,
            is_starred=is_starred
        )
    
    def get_archive_size(
        self, *,
        days: int = 365,
        from_sender: Optional[Union[str, List[str]]] = None,
        subject_contains: Optional[str] = None,
        subject_does_not_contain: Optional[str] = None,
        has_attachment: Optional[bool] = None,
        is_unread: Optional[bool] = None,
        is_important: Optional[bool] = None,
        is_starred: Optional[bool] = None
    ) -> int:
        """
        Get the count of emails in the archive (not in inbox).
        
        Args:
            days: Number of days to look back
            from_sender: Filter by sender email address(es)
            subject_contains: Filter by text in subject line
            subject_does_not_contain: Filter by text not in subject line
            has_attachment: Filter by attachment presence
            is_unread: Filter by read/unread status
            is_important: Filter by importance
            is_starred: Filter by starred status
            
        Returns:
            Number of emails in archive
            
        Example:
            >>> count = gmail_sizer.get_archive_size(days=30, from_sender='example@gmail.com')
            >>> print(f"Archive has {count} emails from example@gmail.com")
        """
        return self.count_emails(
            days=days,
            in_folder='archive',
            from_sender=from_sender,
            subject_contains=subject_contains,
            subject_does_not_contain=subject_does_not_contain,
            has_attachment=has_attachment,
            is_unread=is_unread,
            is_important=is_important,
            is_starred=is_starred
        )
    
    def count_emails(
        self, *,
        days: int = 365,
        from_sender: Optional[Union[str, List[str]]] = None,
        subject_contains: Optional[str] = None,
        subject_does_not_contain: Optional[str] = None,
        has_attachment: Optional[bool] = None,
        is_unread: Optional[bool] = None,
        is_important: Optional[bool] = None,
        in_folder: Optional[Literal['inbox', 'archive', 'spam', 'trash', 'drafts', 'sent']] = None,
        is_starred: Optional[bool] = None
    ) -> int:
        """
        Count emails based on specified filters.
        
        Args:
            days: Number of days to look back
            from_sender: Filter by sender email address(es)
            subject_contains: Filter by text in subject line
            subject_does_not_contain: Filter by text not in subject line
            has_attachment: Filter by attachment presence
            is_unread: Filter by read/unread status
            is_important: Filter by importance
            in_folder: Filter by folder
            is_starred: Filter by starred status
            
        Returns:
            Number of emails matching the filters
            
        Example:
            >>> count = gmail_sizer.count_emails(days=30, from_sender='example@gmail.com')
            >>> print(f"Found {count} emails from example@gmail.com")
        """
        return len(self.get_emails(
            days=days,
            max_emails=None,
            from_sender=from_sender,
            subject_contains=subject_contains,
            subject_does_not_contain=subject_does_not_contain,
            has_attachment=has_attachment,
            is_unread=is_unread,
            is_important=is_important,
            in_folder=in_folder,
            is_starred=is_starred,
            include_text=False,
            include_metrics=False,
            use_batch=True
        ))
    
    def get_trash_emails(
        self, *,
        days: int = 365,
        max_emails: Optional[int] = None,
        include_text: bool = False,
        include_metrics: bool = False,
        use_batch: bool = True,
        parallelize_text_fetch: bool = False
    ) -> pd.DataFrame:
        """
        Get emails from the trash folder.
        
        Args:
            days: Number of days to look back
            max_emails: Maximum number of emails to retrieve
            include_text: Include email body text content
            include_metrics: Include content analysis metrics
            use_batch: Use Gmail API batch requests for better performance
            parallelize_text_fetch: Parallelize text content fetching
            
        Returns:
            DataFrame containing trash emails
            
        Example:
            >>> df = gmail_sizer.get_trash_emails(days=30, max_emails=100)
            >>> print(f"Found {len(df)} emails in trash")
        """
        return self.get_emails(
            days=days,
            max_emails=max_emails,
            in_folder='trash',
            include_text=include_text,
            include_metrics=include_metrics,
            use_batch=use_batch,
            parallelize_text_fetch=parallelize_text_fetch
        )
    
    def get_archive_emails(
        self, *,
        days: int = 365,
        max_emails: Optional[int] = None,
        include_text: bool = False,
        include_metrics: bool = False,
        use_batch: bool = True,
        parallelize_text_fetch: bool = False
    ) -> pd.DataFrame:
        """
        Get emails from the archive (not in inbox).
        
        Args:
            days: Number of days to look back
            max_emails: Maximum number of emails to retrieve
            include_text: Include email body text content
            include_metrics: Include content analysis metrics
            use_batch: Use Gmail API batch requests for better performance
            parallelize_text_fetch: Parallelize text content fetching
            
        Returns:
            DataFrame containing archived emails
            
        Example:
            >>> df = gmail_sizer.get_archive_emails(days=30, max_emails=100)
            >>> print(f"Found {len(df)} archived emails")
        """
        return self.get_emails(
            days=days,
            max_emails=max_emails,
            in_folder='archive',
            include_text=include_text,
            include_metrics=include_metrics,
            use_batch=use_batch,
            parallelize_text_fetch=parallelize_text_fetch
        )
    
    def get_inbox_emails(
        self, *,
        days: int = 30,
        max_emails: Optional[int] = None,
        include_text: bool = False,
        include_metrics: bool = False,
        use_batch: bool = True,
        parallelize_text_fetch: bool = False
    ) -> pd.DataFrame:
        """
        Get emails from the inbox.
        
        Args:
            days: Number of days to look back
            max_emails: Maximum number of emails to retrieve
            include_text: Include email body text content
            include_metrics: Include content analysis metrics
            use_batch: Use Gmail API batch requests for better performance
            parallelize_text_fetch: Parallelize text content fetching
            
        Returns:
            DataFrame containing inbox emails
            
        Example:
            >>> df = gmail_sizer.get_inbox_emails(days=7, max_emails=50)
            >>> print(f"Found {len(df)} emails in inbox")
        """
        return self.get_emails(
            days=days,
            max_emails=max_emails,
            in_folder='inbox',
            include_text=include_text,
            include_metrics=include_metrics,
            use_batch=use_batch,
            parallelize_text_fetch=parallelize_text_fetch
        )
