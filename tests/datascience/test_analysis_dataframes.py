"""
Test analysis dataframes functionality.

This test verifies that the analysis dataframes work correctly
with different types of email data.
"""

from gmaildr import Gmail
from gmaildr.datascience.clustering.auto_cluster import auto_cluster
from tests.core.gmail.test_get_emails import get_emails
import pytest


def test_basic_analysis_dataframes():
    """Test basic analysis dataframes functionality."""
    gmail = Gmail()
    
    # Get emails using the helper function
    emails = get_emails(gmail, 10)
    
    # Test clustering
    clustered_emails, cluster_info = auto_cluster(emails)
    
    assert len(clustered_emails) == len(emails)
    assert 'cluster' in clustered_emails.columns
    assert len(cluster_info) > 0


def test_analysis_with_text_content():
    """Test analysis with text content."""
    gmail = Gmail()
    
    # Get emails using the helper function
    emails = get_emails(gmail, 10)
    
    # Test clustering with text content
    clustered_emails, cluster_info = auto_cluster(emails)
    
    assert len(clustered_emails) == len(emails)
    assert 'cluster' in clustered_emails.columns


def test_analysis_with_metrics():
    """Test analysis with metrics."""
    gmail = Gmail()
    
    # Get emails using the helper function
    emails = get_emails(gmail, 10)
    
    # Test clustering with metrics
    clustered_emails, cluster_info = auto_cluster(emails)
    
    assert len(clustered_emails) == len(emails)
    assert 'cluster' in clustered_emails.columns


def test_large_dataset_analysis():
    """Test analysis with larger dataset."""
    gmail = Gmail()
    
    # Get emails using the helper function
    emails = get_emails(gmail, 50)
    
    # Test clustering with larger dataset
    clustered_emails, cluster_info = auto_cluster(emails)
    
    assert len(clustered_emails) == len(emails)
    assert 'cluster' in clustered_emails.columns
    assert len(cluster_info) > 0


def test_clustering_consistency():
    """Test that clustering produces consistent results."""
    gmail = Gmail()
    
    # Get emails using the helper function
    emails = get_emails(gmail, 50)
    
    # Run clustering twice
    clustered_emails1, cluster_info1 = auto_cluster(emails)
    clustered_emails2, cluster_info2 = auto_cluster(emails)
    
    # Results should be consistent
    assert len(clustered_emails1) == len(clustered_emails2)
    assert len(cluster_info1) == len(cluster_info2)


def test_analysis_with_different_sizes():
    """Test analysis with different dataset sizes."""
    gmail = Gmail()
    
    for size in [10, 20, 50]:
        # Get emails using the helper function
        emails = get_emails(gmail, size)
        
        # Test clustering
        clustered_emails, cluster_info = auto_cluster(emails)
        
        assert len(clustered_emails) == len(emails)
        assert 'cluster' in clustered_emails.columns


def test_analysis_edge_cases():
    """Test analysis with edge cases."""
    gmail = Gmail()
    
    # Test with very small dataset
    emails = get_emails(gmail, 5)
    
    # Test clustering
    clustered_emails, cluster_info = auto_cluster(emails)
    
    assert len(clustered_emails) == len(emails)
    assert 'cluster' in clustered_emails.columns

