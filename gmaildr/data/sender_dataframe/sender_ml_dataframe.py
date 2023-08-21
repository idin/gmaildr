"""
SenderMLDataFrame - DataFrame for sender machine learning features.

This module provides a SenderMLDataFrame class that represents transformed sender features
suitable for machine learning algorithms.
"""

import pandas as pd
from typing import Dict, Any, Union, List, TYPE_CHECKING, TYPE_CHECKING

from .sender_dataframe import SenderDataFrame
    
class Sender_ML_DataFrame(SenderDataFrame):
    """
    DataFrame for sender machine learning features.
    
    This represents transformed sender features suitable for ML algorithms.
    It is NOT a SenderDataFrame since it has dropped some features.
    """

    NECESSARY_COLUMNS = [
        'sender_email', 'total_emails', 'unique_subjects', 'mean_email_size_bytes',
        'total_emails_sin', 'total_emails_cos', 'unique_subjects_sin', 'unique_subjects_cos',
        'mean_email_size_sin', 'mean_email_size_cos', 'day_of_week_entropy_sin', 'day_of_week_entropy_cos',
        'hour_of_day_entropy_sin', 'hour_of_day_entropy_cos', 'weekend_ratio_sin', 'weekend_ratio_cos',
        'business_hours_ratio_sin', 'business_hours_ratio_cos', 'burst_days_ratio_sin', 'burst_days_ratio_cos'
    ]
    
    @property
    def _constructor(self):
        """Return the class to use for DataFrame operations."""
        return Sender_ML_DataFrame

    def _get_message_ids(self) -> List[str]:
        """Get message IDs from the DataFrame."""
        # For Sender_ML_DataFrame, we need to get emails from the senders
        if self._gmail_instance is None:
            raise ValueError("Gmail instance not set. Use set_gmail_instance() first.")
        
        # Get emails from all senders in this DataFrame
        emails = self._gmail_instance.get_emails(from_sender=self['sender_email'].tolist())
        return emails['message_id'].tolist()

    @property
    def ml_dataframe(self) -> pd.DataFrame:
        return self