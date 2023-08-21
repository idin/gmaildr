"""
Tests for cluster function in_place behavior.
"""

import pandas as pd
import numpy as np
import pytest

from gmaildr.datascience.clustering.cluster import cluster
from gmaildr.data.email_dataframe.email_ml_dataframe import Email_ML_DataFrame
from gmaildr.data.sender_dataframe.sender_ml_dataframe import Sender_ML_DataFrame
from gmaildr.core.gmail import Gmail
from tests.core.gmail.test_get_emails import get_emails


def create_test_regular_dataframe():
    """Create a test regular pandas DataFrame with numeric columns."""
    return pd.DataFrame({
        'feature1': [1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
        'feature2': [0.1, 0.2, 0.3, 0.4, 0.5, 0.6],
        'feature3': [10, 20, 30, 40, 50, 60],
        'text_col': ['a', 'b', 'c', 'd', 'e', 'f']  # Non-numeric column
    })


def create_test_email_ml_dataframe():
    """Create a test Email_ML_DataFrame."""
    gmail = Gmail()
    emails_df = get_emails(gmail=gmail, n=100)
    # we return email_df because the clustering methods should accept email df too
    return emails_df


def create_test_sender_ml_dataframe():
    """Create a test Sender_ML_DataFrame."""
    gmail = Gmail()
    emails = get_emails(gmail=gmail, n=100)
    from gmaildr.data.sender_dataframe.sender_dataframe import SenderDataFrame
    sender_df = SenderDataFrame(emails)
    # we return sender_df because the clustering methods should accept sender df too
    return sender_df

def test_cluster_in_place_true():
    regular_df = create_test_regular_dataframe()
    regular_df_copy = regular_df.copy()
    assert regular_df is not regular_df_copy
    clustered_df = cluster(regular_df, k=2, in_place=True)
    # the copy should not change
    # clustered_df should be the same as regular_df
    assert clustered_df is regular_df
    assert clustered_df is not regular_df_copy
    assert 'cluster' in clustered_df.columns
    assert clustered_df['cluster'].nunique() == 2
    assert len(clustered_df) == 6

    gmail = Gmail()
    emails_df = get_emails(gmail=gmail, n=100)
    emails_ml_df = emails_df.ml_dataframe
    emails_ml_df_copy = emails_ml_df.copy()
    assert emails_ml_df is not emails_ml_df_copy
    clustered_emails_ml_df = cluster(emails_ml_df, k=2, in_place=True)
    assert clustered_emails_ml_df is emails_ml_df
    assert clustered_emails_ml_df is not emails_ml_df_copy
    assert 'cluster' in clustered_emails_ml_df.columns
    assert clustered_emails_ml_df['cluster'].nunique() == 2
    assert len(clustered_emails_ml_df) == 100

    senders_df = emails_df.get_senders()
    senders_ml_df = senders_df.ml_dataframe
    senders_ml_df_copy = senders_ml_df.copy()
    assert senders_ml_df is not senders_ml_df_copy
    clustered_senders_ml_df = cluster(senders_ml_df, k=2, in_place=True)
    assert clustered_senders_ml_df is senders_ml_df
    assert clustered_senders_ml_df is not senders_ml_df_copy
    assert 'cluster' in clustered_senders_ml_df.columns
    assert clustered_senders_ml_df['cluster'].nunique() == 2
    assert len(clustered_senders_ml_df) == 100

def test_cluster_in_place_false():
    regular_df = create_test_regular_dataframe()
    regular_df_copy = regular_df.copy()
    assert regular_df is not regular_df_copy
    clustered_df = cluster(regular_df, k=2, in_place=False)
    assert clustered_df is not regular_df
    assert clustered_df is not regular_df_copy
    assert 'cluster' in clustered_df.columns
    assert clustered_df['cluster'].nunique() == 2
    assert len(clustered_df) == 6

    emails_df = create_test_email_ml_dataframe()
    emails_ml_df = emails_df.ml_dataframe
    emails_ml_df_copy = emails_ml_df.copy()
    assert emails_ml_df is not emails_ml_df_copy
    clustered_emails_ml_df = cluster(emails_ml_df, k=2, in_place=False)
    assert clustered_emails_ml_df is not emails_ml_df
    assert clustered_emails_ml_df is not emails_ml_df_copy
    assert 'cluster' in clustered_emails_ml_df.columns
    assert clustered_emails_ml_df['cluster'].nunique() == 2
    assert len(clustered_emails_ml_df) == 100

    senders_df = emails_df.senders_dataframe
    senders_ml_df = senders_df.ml_dataframe
    senders_ml_df_copy = senders_ml_df.copy()
    assert senders_ml_df is not senders_ml_df_copy
    clustered_senders_ml_df = cluster(senders_ml_df, k=2, in_place=False)
    assert clustered_senders_ml_df is not senders_ml_df
    assert clustered_senders_ml_df is not senders_ml_df_copy
    assert 'cluster' in clustered_senders_ml_df.columns
    assert clustered_senders_ml_df['cluster'].nunique() == 2
    assert len(clustered_senders_ml_df) == 100

def test_cluster_in_place_false_with_include_columns():
    regular_df = create_test_regular_dataframe()
    original_df = regular_df.copy()
    assert regular_df is not original_df
    
