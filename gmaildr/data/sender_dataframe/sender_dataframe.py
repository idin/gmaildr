"""
SenderDataFrame - DataFrame for sender statistics.

This module provides a SenderDataFrame class that represents aggregated email data
with one row per sender and comprehensive statistics.
"""

import pandas as pd
from typing import Dict, List, Any, Optional, Union, Set, Literal, TYPE_CHECKING
from datetime import datetime
from .transform_features_for_ml import transform_sender_features_for_ml #SenderDataFrame needs this: transform_sender_features_for_ml and it is not a circular import, if it is circular there is another issue somwhere else 
from ..email_dataframe.email_dataframe import EmailDataFrame

if TYPE_CHECKING:
    from ...core.gmail import Gmail

from ..gmail_dataframe import GmailDataFrame

class SenderDataFrame(GmailDataFrame):
    """DataFrame for sender statistics with one row per sender."""

    NECESSARY_COLUMNS = [
        'sender_email', 'total_emails', 'unique_subjects', 'mean_email_size_bytes'
    ]

    @property
    def senders(self) -> Set[str]:
        """
        Get the set of sender emails in the SenderDataFrame.
        """
        return set(self['sender_email'])

    @property
    def _constructor(self):
        """Return the class to use for DataFrame operations."""
        return SenderDataFrame

    def _get_message_ids(self) -> List[str]:
        """Get message IDs from the DataFrame."""
        raise NotImplementedError("SenderDataFrame does not have message IDs")

    @property
    def ml_dataframe(self) -> pd.DataFrame:
        """
        Transform features for machine learning.
        """
        from .sender_ml_dataframe import Sender_ML_DataFrame
        from .transform_features_for_ml import transform_sender_features_for_ml
        
        data = transform_sender_features_for_ml(self.dataframe)
        return Sender_ML_DataFrame(data, gmail=self.gmail)

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




