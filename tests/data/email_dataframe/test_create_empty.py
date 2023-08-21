"""
Test create_empty method for EmailDataFrame.

This module tests that the create_empty method works correctly and returns
the proper EmailDataFrame instance.
"""

import pytest
from gmaildr import Gmail
from gmaildr.data.email_dataframe import EmailDataFrame, Email_ML_DataFrame


def test_email_dataframe_create_empty():
    """Test EmailDataFrame.create_empty() creates empty EmailDataFrame."""
    gmail = Gmail()
    empty_df = EmailDataFrame.create_empty(gmail=gmail)
    
    assert isinstance(empty_df, EmailDataFrame)
    assert len(empty_df) == 0
    assert empty_df._gmail_instance is gmail


def test_email_dataframe_create_empty_without_gmail():
    """Test EmailDataFrame.create_empty() works without gmail instance."""
    empty_df = EmailDataFrame.create_empty()
    
    assert isinstance(empty_df, EmailDataFrame)
    assert len(empty_df) == 0


def test_email_ml_dataframe_create_empty():
    """Test Email_ML_DataFrame.create_empty() creates empty Email_ML_DataFrame."""
    gmail = Gmail()
    empty_df = Email_ML_DataFrame.create_empty(gmail=gmail)
    
    assert isinstance(empty_df, Email_ML_DataFrame)
    assert len(empty_df) == 0
    assert empty_df._gmail_instance is gmail


def test_email_ml_dataframe_create_empty_without_gmail():
    """Test Email_ML_DataFrame.create_empty() works without gmail instance."""
    empty_df = Email_ML_DataFrame.create_empty()
    
    assert isinstance(empty_df, Email_ML_DataFrame)
    assert len(empty_df) == 0
