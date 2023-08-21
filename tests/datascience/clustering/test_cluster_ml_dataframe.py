"""
Tests for auto_cluster functions.
"""

import pandas as pd
import numpy as np
import pytest

from gmaildr.datascience.clustering.auto_cluster import (
    auto_cluster,
    analyze_clusters
)
from gmaildr.data.email_dataframe.email_ml_dataframe import Email_ML_DataFrame
from gmaildr.data.sender_dataframe.sender_ml_dataframe import Sender_ML_DataFrame
from gmaildr.core.gmail import Gmail
from tests.core.gmail.test_get_emails import get_emails


def create_test_email_ml_dataframe():
    """Create a test Email_ML_DataFrame using the get_emails helper."""
    gmail = Gmail()
    emails = get_emails(gmail=gmail, n=6)
    return emails.ml_dataframe


def create_test_sender_ml_dataframe():
    """Create a test Sender_ML_DataFrame using the get_emails helper."""
    gmail = Gmail()
    emails = get_emails(gmail=gmail, n=10)
    # Create sender dataframe from emails
    from gmaildr.data.sender_dataframe.sender_dataframe import SenderDataFrame
    sender_df = SenderDataFrame(emails, gmail=gmail)
    return sender_df.ml_dataframe


def test_cluster_email_ml_dataframe_basic():
    """Test basic clustering of Email_ML_DataFrame."""
    ml_df = create_test_email_ml_dataframe()
    
    # Test with fixed k
    clustered_df, info = auto_cluster(
        ml_df,
        k=2,
        auto_select_k=False,
        random_state=42,
        in_place=False
    )
    
    assert isinstance(clustered_df, Email_ML_DataFrame)
    assert clustered_df is not ml_df
    assert 'cluster' in clustered_df.columns
    assert info['k'] == 2
    assert info['auto_selected'] is False
    assert clustered_df['cluster'].nunique() == 2
    assert len(clustered_df) == len(ml_df)


def test_cluster_email_ml_dataframe_auto_k():
    """Test clustering with automatic k selection."""
    ml_df = create_test_email_ml_dataframe()
    
    # Test with auto k selection
    clustered_df, info = auto_cluster(
        ml_df,
        auto_select_k=True,
        max_k=5,
        method="silhouette",
        random_state=42,
        in_place=False
    )
    
    assert isinstance(clustered_df, Email_ML_DataFrame)
    assert clustered_df is not ml_df
    assert 'cluster' in clustered_df.columns
    assert info['auto_selected'] is True
    assert 'diagnostics' in info
    assert clustered_df['cluster'].nunique() > 0
    assert len(clustered_df) == len(ml_df)


def test_cluster_sender_ml_dataframe_basic():
    """Test basic clustering of Sender_ML_DataFrame."""
    ml_df = create_test_sender_ml_dataframe()
    
    # Test with fixed k
    clustered_df, info = auto_cluster(
        ml_df,
        k=2,
        auto_select_k=False,
        random_state=42
    )
    
    assert isinstance(clustered_df, Sender_ML_DataFrame)
    assert clustered_df is not ml_df
    assert 'cluster' in clustered_df.columns
    assert info['k'] == 2
    assert info['auto_selected'] is False
    assert clustered_df['cluster'].nunique() == 2
    assert len(clustered_df) == len(ml_df)


def test_cluster_sender_ml_dataframe_auto_k():
    """Test clustering with automatic k selection."""
    ml_df = create_test_sender_ml_dataframe()
    
    # Test with auto k selection
    clustered_df, info = auto_cluster(
        ml_df,
        auto_select_k=True,
        max_k=3,
        method="silhouette",
        random_state=42
    )
    
    assert isinstance(clustered_df, Sender_ML_DataFrame)
    assert clustered_df is not ml_df
    assert 'cluster' in clustered_df.columns
    assert info['auto_selected'] is True
    assert 'diagnostics' in info
    assert clustered_df['cluster'].nunique() > 0
    assert len(clustered_df) == len(ml_df)


def test_cluster_email_ml_dataframe_empty():
    """Test clustering with empty Email_ML_DataFrame."""
    empty_df = Email_ML_DataFrame.create_empty()

    # it should raise an error
    with pytest.raises(ValueError, match="df is empty"):
        auto_cluster(
            empty_df,
            k=2,
            auto_select_k=False
        )


def test_cluster_sender_ml_dataframe_empty():
    """Test clustering with empty Sender_ML_DataFrame."""
    empty_df = Sender_ML_DataFrame.create_empty()
    
    # it should raise an error
    with pytest.raises(ValueError, match="df is empty"):
        auto_cluster(
            empty_df,
            k=2,
            auto_select_k=False
        )


def test_analyze_clusters():
    """Test cluster analysis function."""
    # Create a test DataFrame with clusters
    test_data = {
        'feature1': [1, 2, 3, 10, 11, 12],
        'feature2': [1, 2, 3, 10, 11, 12],
        'cluster': [0, 0, 0, 1, 1, 1]
    }
    df = pd.DataFrame(test_data)
    
    analysis = analyze_clusters(df, cluster_col='cluster')
    
    assert 'total_clusters' in analysis
    assert 'total_samples' in analysis
    assert 'cluster_distribution' in analysis
    assert analysis['total_clusters'] == 2
    assert analysis['total_samples'] == 6
    
    # Check cluster statistics
    cluster_0 = analysis['cluster_distribution']['cluster_0']
    cluster_1 = analysis['cluster_distribution']['cluster_1']
    
    assert cluster_0['size'] == 3
    assert cluster_1['size'] == 3
    assert cluster_0['percentage'] == 50.0
    assert cluster_1['percentage'] == 50.0
    
    # Check feature statistics
    assert 'feature1' in cluster_0['features']
    assert 'feature2' in cluster_0['features']
    assert cluster_0['features']['feature1']['mean'] == 2.0
    assert cluster_1['features']['feature1']['mean'] == 11.0


def test_analyze_clusters_with_specific_features():
    """Test cluster analysis with specific feature columns."""
    test_data = {
        'feature1': [1, 2, 3, 10, 11, 12],
        'feature2': [1, 2, 3, 10, 11, 12],
        'cluster': [0, 0, 0, 1, 1, 1],
        'ignore_me': ['a', 'b', 'c', 'd', 'e', 'f']
    }
    df = pd.DataFrame(test_data)
    
    analysis = analyze_clusters(df, cluster_col='cluster', feature_cols=['feature1'])
    
    cluster_0 = analysis['cluster_distribution']['cluster_0']
    assert 'feature1' in cluster_0['features']
    assert 'feature2' not in cluster_0['features']
    assert 'ignore_me' not in cluster_0['features']


def test_analyze_clusters_invalid_column():
    """Test cluster analysis with invalid cluster column."""
    test_data = {
        'feature1': [1, 2, 3],
        'feature2': [1, 2, 3]
    }
    df = pd.DataFrame(test_data)
    
    with pytest.raises(ValueError, match="Cluster column 'nonexistent' not found"):
        analyze_clusters(df, cluster_col='nonexistent')
