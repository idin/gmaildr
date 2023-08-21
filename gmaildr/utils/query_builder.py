"""
Query builder utility for Gmail search queries.

This module contains shared logic for building Gmail search queries
to ensure consistency between cached and non-cached email retrieval.
"""

from datetime import datetime, timedelta
from typing import Optional, Union, List, Literal
from .date_utils import parse_date_range


def build_gmail_search_query(
    *, 
    days: Optional[int] = None,
    start_date: Optional[Union[datetime, str]] = None,
    end_date: Optional[Union[datetime, str]] = None,
    from_sender: Optional[Union[str, List[str]]] = None,
    subject_contains: Optional[str] = None,
    subject_does_not_contain: Optional[str] = None,
    has_attachment: Optional[bool] = None,
    is_unread: Optional[bool] = None,
    is_important: Optional[bool] = None,
    in_folder: Optional[Literal['inbox', 'archive', 'spam', 'trash', 'drafts', 'sent']] = None,
    is_starred: Optional[bool] = None
) -> str:
    """
    Build Gmail search query from filter parameters.
    
    Args:
        days: Number of days to search back from
        start_date: Start date for search range
        end_date: End date for search range
        from_sender: Filter by sender email address(es)
        subject_contains: Filter by text in subject line
        subject_does_not_contain: Filter by text not in subject line
        has_attachment: Filter by attachment presence
        is_unread: Filter by read/unread status
        is_important: Filter by importance
        in_folder: Filter by folder
        is_starred: Filter by starred status
        
    Returns:
        str: Gmail search query string.
    """
    # Parse date range using utility function
    date_range = parse_date_range(
        days=days,
        start_date=start_date,
        end_date=end_date
    )
    query_start_date = date_range['start_date']
    query_end_date = date_range['end_date']
    
    # Build Gmail search query
    query_parts = []
    # Use Gmail's native date format - after: and before: are exclusive
    query_parts.append(f"after:{query_start_date.strftime('%Y/%m/%d')}")  # type: ignore
    query_parts.append(f"before:{query_end_date.strftime('%Y/%m/%d')}")  # type: ignore
    
    if from_sender:
        if isinstance(from_sender, str):
            query_parts.append(f"from:{from_sender}")
        elif isinstance(from_sender, list):
            # Gmail doesn't support OR with |, so we need to use OR syntax
            sender_queries = [f"from:{sender}" for sender in from_sender]
            query_parts.append(f"({' OR '.join(sender_queries)})")
    
    if subject_contains:
        # Convert & and | to Gmail's AND and OR syntax
        gmail_subject = subject_contains.replace('&', ' AND ').replace('|', ' OR ')
        query_parts.append(f"subject:({gmail_subject})")
    
    if subject_does_not_contain:
        # Convert & and | to Gmail's AND and OR syntax, then use NOT
        gmail_subject = subject_does_not_contain.replace('&', ' AND ').replace('|', ' OR ')
        query_parts.append(f"subject:(NOT ({gmail_subject}))")
    
    if has_attachment is True:
        query_parts.append("has:attachment")
    elif has_attachment is False:
        query_parts.append("-has:attachment")
    
    if is_unread is True:
        query_parts.append("is:unread")
    elif is_unread is False:
        query_parts.append("-is:unread")
    
    if is_important is True:
        query_parts.append("is:important")
    elif is_important is False:
        query_parts.append("-is:important")
    
    # Folder filter
    if in_folder:
        if in_folder == 'archive':
            query_parts.append("-in:inbox")  # Archive means not in inbox
        else:
            query_parts.append(f"in:{in_folder}")
    
    # Starred filter
    if is_starred is True:
        query_parts.append("is:starred")
    elif is_starred is False:
        query_parts.append("-is:starred")
    
    return " ".join(query_parts)
