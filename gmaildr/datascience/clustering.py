"""
Email clustering functionality for GmailDr.

This module provides clustering analysis for email data to identify
patterns and group similar emails together.
"""

import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any, Optional
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
from ..core.email_dataframe import EmailDataFrame


def find_optimal_clusters(
    email_dataframe: EmailDataFrame,
    max_clusters: int = 10,
    random_state: int = 42
) -> Tuple[int, Dict[str, Any]]:
    """
    Find the optimal number of clusters for email data.
    
    This function uses the elbow method and silhouette analysis to determine
    the best number of clusters for the given email data.
    
    Args:
        email_dataframe: EmailDataFrame containing email data
        max_clusters: Maximum number of clusters to test (default: 10)
        random_state: Random state for reproducibility (default: 42)
        
    Returns:
        Tuple containing:
        - optimal_k: The optimal number of clusters
        - metrics: Dictionary containing clustering metrics for each k
    """
    # Prepare features for clustering
    features = _prepare_clustering_features(email_dataframe)
    
    if len(features) < 2:
        raise ValueError("Need at least 2 emails for clustering")
    
    # Standardize features
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)
    
    # Test different numbers of clusters
    k_range = range(2, min(max_clusters + 1, len(features) + 1))
    metrics = {
        'k_values': [],
        'inertia': [],
        'silhouette_scores': []
    }
    
    for k in k_range:
        kmeans = KMeans(n_clusters=k, random_state=random_state, n_init=10)
        cluster_labels = kmeans.fit_predict(features_scaled)
        
        metrics['k_values'].append(k)
        metrics['inertia'].append(kmeans.inertia_)
        
        # Calculate silhouette score
        if k > 1:
            silhouette_avg = silhouette_score(features_scaled, cluster_labels)
            metrics['silhouette_scores'].append(silhouette_avg)
        else:
            metrics['silhouette_scores'].append(0)
    
    # Find optimal k using elbow method and silhouette analysis
    optimal_k = _find_optimal_k(metrics)
    
    return optimal_k, metrics


def cluster_emails(
    email_dataframe: EmailDataFrame,
    n_clusters: Optional[int] = None,
    random_state: int = 42
) -> Tuple[EmailDataFrame, Dict[str, Any]]:
    """
    Cluster emails using K-means clustering.
    
    Args:
        email_dataframe: EmailDataFrame containing email data
        n_clusters: Number of clusters (if None, will find optimal)
        random_state: Random state for reproducibility (default: 42)
        
    Returns:
        Tuple containing:
        - clustered_df: EmailDataFrame with cluster labels added
        - cluster_info: Dictionary containing clustering information
    """
    # Find optimal clusters if not specified
    if n_clusters is None:
        n_clusters, _ = find_optimal_clusters(email_dataframe, random_state=random_state)
    
    # Prepare features
    features = _prepare_clustering_features(email_dataframe)
    
    if len(features) < n_clusters:
        raise ValueError(f"Need at least {n_clusters} emails for {n_clusters} clusters")
    
    # Standardize features
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)
    
    # Perform clustering
    kmeans = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
    cluster_labels = kmeans.fit_predict(features_scaled)
    
    # Add cluster labels to DataFrame
    clustered_df = email_dataframe.copy()
    clustered_df['cluster'] = cluster_labels
    
    # Get cluster information
    cluster_info = _analyze_clusters(clustered_df, features_scaled, kmeans)
    
    return clustered_df, cluster_info


def _prepare_clustering_features(email_dataframe: EmailDataFrame) -> EmailDataFrame:
    """
    Prepare features for clustering from email data using vectorized operations.
    
    Args:
        email_dataframe: EmailDataFrame containing email data
        
    Returns:
        Feature matrix for clustering
    """
    df = email_dataframe.copy()
    features_list = []
    
    # Subject length (vectorized)
    if 'subject_length' not in df.columns:
        df['subject_length'] = df['subject'].fillna('').astype(str).str.len()

    features_list.append(df['subject_length'])
    
    # Sender domain encoding (vectorized)
    if 'sender_domain' not in df.columns:
        df['sender_domain'] = df['sender_email'].fillna('').astype(str).str.split('@').str[-1]
        df['sender_domain'] = df['sender_domain'].where(df['sender_domain'] != '', 'unknown')
        df['sender_domain'] = df['sender_domain'].apply(lambda x: hash(x) % 1000)

    features_list.append(domain_encoded)
    
    # Has attachment (vectorized)
    if 'has_attachment' in df.columns:
        has_attachment = df['has_attachment'].fillna(False).astype(int)
    else:
        has_attachment = pd.Series(0, index=df.index)
    features_list.append(has_attachment)
    
    # Is unread (vectorized)
    if 'is_unread' in df.columns:
        is_unread = df['is_unread'].fillna(False).astype(int)
    else:
        is_unread = pd.Series(0, index=df.index)
    features_list.append(is_unread)
    
    # Date features (vectorized)
    if 'timestamp' not in df.columns:
        raise KeyError("timestamp column is required for clustering")
    
    if 'date' in df.columns:
        try:
            dates = pd.to_datetime(df['date'], errors='coerce')
            hour_of_day = dates.dt.hour.fillna(0)
            day_of_week = dates.dt.weekday.fillna(0)
            day_of_month = dates.dt.day.fillna(0)
        except:
            hour_of_day = pd.Series(0, index=df.index)
            day_of_week = pd.Series(0, index=df.index)
            day_of_month = pd.Series(0, index=df.index)
    else:
        hour_of_day = pd.Series(0, index=df.index)
        day_of_week = pd.Series(0, index=df.index)
        day_of_month = pd.Series(0, index=df.index)
    
    features_list.extend([hour_of_day, day_of_week, day_of_month])
    
    # Combine all features into a single array
    features_array = np.column_stack(features_list)
    
    return features_array


def _find_optimal_k(metrics: Dict[str, Any]) -> int:
    """
    Find optimal number of clusters using elbow method and silhouette analysis.
    
    Args:
        metrics: Dictionary containing clustering metrics
        
    Returns:
        Optimal number of clusters
    """
    k_values = metrics['k_values']
    inertia = metrics['inertia']
    silhouette_scores = metrics['silhouette_scores']
    
    # Elbow method: find the point where inertia starts decreasing more slowly
    inertia_diff = np.diff(inertia)
    inertia_diff_ratio = np.abs(inertia_diff[1:] / inertia_diff[:-1])
    elbow_k = k_values[np.argmin(inertia_diff_ratio) + 1]
    
    # Silhouette method: find k with highest silhouette score
    silhouette_k = k_values[np.argmax(silhouette_scores)]
    
    # Combine both methods (prefer silhouette if it's reasonable)
    if silhouette_k <= elbow_k + 2:  # Silhouette k is not too far from elbow
        optimal_k = silhouette_k
    else:
        optimal_k = elbow_k
    
    return optimal_k


def _analyze_clusters(
    clustered_df: EmailDataFrame,
    features_scaled: np.ndarray,
    kmeans: KMeans
) -> Dict[str, Any]:
    """
    Analyze clustering results and provide insights.
    
    Args:
        clustered_df: EmailDataFrame with cluster labels
        features_scaled: Scaled feature matrix
        kmeans: Fitted KMeans model
        
    Returns:
        Dictionary containing cluster analysis information
    """
    cluster_info = {
        'n_clusters': kmeans.n_clusters,
        'cluster_sizes': {},
        'cluster_centers': kmeans.cluster_centers_.tolist(),
        'inertia': kmeans.inertia_,
        'silhouette_score': silhouette_score(features_scaled, clustered_df['cluster']),
        'cluster_characteristics': {}
    }
    
    # Analyze each cluster
    for cluster_id in range(kmeans.n_clusters):
        cluster_emails = clustered_df[clustered_df['cluster'] == cluster_id]
        cluster_info['cluster_sizes'][cluster_id] = len(cluster_emails)
        
        # Cluster characteristics
        characteristics = {}
        
        if 'subject' in cluster_emails.columns:
            avg_subject_length = cluster_emails['subject'].str.len().mean()
            characteristics['avg_subject_length'] = avg_subject_length
        
        if 'has_attachment' in cluster_emails.columns:
            attachment_rate = cluster_emails['has_attachment'].mean()
            characteristics['attachment_rate'] = attachment_rate
        
        if 'is_unread' in cluster_emails.columns:
            unread_rate = cluster_emails['is_unread'].mean()
            characteristics['unread_rate'] = unread_rate
        
        if 'sender_email' in cluster_emails.columns:
            unique_senders = cluster_emails['sender_email'].nunique()
            characteristics['unique_senders'] = unique_senders
        
        cluster_info['cluster_characteristics'][cluster_id] = characteristics
    
    return cluster_info


def plot_clustering_analysis(
    metrics: Dict[str, Any],
    save_path: Optional[str] = None
) -> None:
    """
    Plot clustering analysis results.
    
    Args:
        metrics: Metrics from find_optimal_clusters
        save_path: Optional path to save the plot
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Elbow plot
    ax1.plot(metrics['k_values'], metrics['inertia'], 'bo-')
    ax1.set_xlabel('Number of Clusters (k)')
    ax1.set_ylabel('Inertia')
    ax1.set_title('Elbow Method')
    ax1.grid(True)
    
    # Silhouette plot
    ax2.plot(metrics['k_values'], metrics['silhouette_scores'], 'ro-')
    ax2.set_xlabel('Number of Clusters (k)')
    ax2.set_ylabel('Silhouette Score')
    ax2.set_title('Silhouette Analysis')
    ax2.grid(True)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    else:
        plt.show()
