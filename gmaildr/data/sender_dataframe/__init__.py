"""
Sender DataFrame Module.

This module provides SenderDataFrame and related functionality for analyzing
sender patterns and statistics from email data.
"""

from .sender_dataframe import SenderDataFrame
from .transform_features_for_ml import transform_sender_features_for_ml
from .aggregate_emails_by_sender import aggregate_emails_by_sender
from .content_analysis import calculate_entropy, extract_common_keywords
from .additional_features import add_additional_features
from .sender_ml_dataframe import Sender_ML_DataFrame

__all__ = [
    'SenderDataFrame', 
    'Sender_ML_DataFrame',
    'transform_sender_features_for_ml',
    'aggregate_emails_by_sender',
    'calculate_entropy',
    'extract_common_keywords',
    'add_additional_features',
]
