"""
Temporal statistics functions for sender analysis.

This module contains functions for calculating temporal patterns in sender behavior.
"""

import pandas as pd
from pandas.core import groupby


def calculate_temporal_statistics_groupby(grouped: groupby.DataFrameGroupBy) -> pd.DataFrame:
    """
    Calculate temporal statistics using groupby operations.
    
    Args:
        grouped: Grouped DataFrame by sender_email
        
    Returns:
        DataFrame with temporal statistics for each sender
    """
    temporal_stats = pd.DataFrame()
    
    # Time difference between sender and receiver timestamps
    if 'sender_time_difference_hours' in grouped.obj.columns:
        temporal_stats['mean_sender_time_difference_hours'] = grouped['sender_time_difference_hours'].mean()
        temporal_stats['std_sender_time_difference_hours'] = grouped['sender_time_difference_hours'].std()
        temporal_stats['min_sender_time_difference_hours'] = grouped['sender_time_difference_hours'].min()
        temporal_stats['max_sender_time_difference_hours'] = grouped['sender_time_difference_hours'].max()

    # Most active day and hour
    temporal_stats['most_active_day'] = grouped['day_of_week'].agg(lambda x: x.mode()[0] if len(x.mode()) > 0 else None)
    temporal_stats['most_active_hour'] = grouped['hour_of_day'].agg(lambda x: x.mode()[0] if len(x.mode()) > 0 else None)
    
    # Day of week patterns
    if 'day_of_week' in grouped.obj.columns:
        temporal_stats['day_of_week_entropy'] = grouped['day_of_week'].apply(calculate_day_entropy, include_groups=False)
        temporal_stats['day_of_week_concentration'] = grouped['day_of_week'].apply(calculate_day_concentration, include_groups=False)
        temporal_stats['weekend_ratio'] = grouped['day_of_week'].apply(lambda x: (x.isin([5, 6])).mean(), include_groups=False)
    
    # Hour of day patterns
    if 'hour_of_day' in grouped.obj.columns:
        temporal_stats['hour_of_day_entropy'] = grouped['hour_of_day'].apply(calculate_hour_entropy, include_groups=False)
        temporal_stats['hour_of_day_concentration'] = grouped['hour_of_day'].apply(calculate_hour_concentration, include_groups=False)
        temporal_stats['business_hours_ratio'] = grouped['hour_of_day'].apply(lambda x: ((x >= 9) & (x <= 17)).mean(), include_groups=False)
        temporal_stats['night_hours_ratio'] = grouped['hour_of_day'].apply(lambda x: ((x >= 22) | (x <= 6)).mean(), include_groups=False)
    
    # Time between emails patterns
    if 'sender_local_timestamp' in grouped.obj.columns:
        time_between_stats = calculate_time_between_emails_stats(grouped)
        temporal_stats = pd.concat([temporal_stats, time_between_stats], axis=1)
    
    return temporal_stats


def calculate_day_entropy(series: pd.Series) -> float:
    """Calculate entropy of day of week distribution."""
    from .content_analysis import calculate_entropy
    return calculate_entropy(series.values)


def calculate_day_concentration(series: pd.Series) -> float:
    """Calculate concentration of emails on most common day."""
    if len(series) == 0:
        return 0.0
    most_common_count = series.value_counts().max()
    return most_common_count / len(series)


def calculate_hour_entropy(series: pd.Series) -> float:
    """Calculate entropy of hour of day distribution."""
    from .content_analysis import calculate_entropy
    return calculate_entropy(series.values)


def calculate_hour_concentration(series: pd.Series) -> float:
    """Calculate concentration of emails on most common hour."""
    if len(series) == 0:
        return 0.0
    most_common_count = series.value_counts().max()
    return most_common_count / len(series)


def calculate_time_between_emails_stats(grouped: groupby.DataFrameGroupBy) -> pd.DataFrame:
    """Calculate time between emails statistics."""
    stats = pd.DataFrame()
    
    # Sort each group by timestamp
    sorted_groups = grouped.apply(lambda x: x.sort_values('sender_local_timestamp'))
    
    # Calculate time differences between consecutive emails
    time_diffs = []
    for sender, group in sorted_groups:
        if len(group) > 1:
            timestamps = group['sender_local_timestamp']
            diffs = timestamps.diff().dropna().dt.total_seconds() / 3600  # Convert to hours
            time_diffs.extend(diffs.tolist())
    
    if time_diffs:
        time_diffs_series = pd.Series(time_diffs)
        stats['mean_time_between_emails_hours'] = time_diffs_series.mean()
        stats['std_time_between_emails_hours'] = time_diffs_series.std()
        stats['min_time_between_emails_hours'] = time_diffs_series.min()
        stats['max_time_between_emails_hours'] = time_diffs_series.max()
        stats['time_between_emails_entropy'] = calculate_time_entropy(time_diffs_series)
        stats['time_between_emails_cv'] = time_diffs_series.std() / time_diffs_series.mean() if time_diffs_series.mean() > 0 else 0
    else:
        stats['mean_time_between_emails_hours'] = 0
        stats['std_time_between_emails_hours'] = 0
        stats['min_time_between_emails_hours'] = 0
        stats['max_time_between_emails_hours'] = 0
        stats['time_between_emails_entropy'] = 0
        stats['time_between_emails_cv'] = 0
    
    return stats


def calculate_time_entropy(series: pd.Series) -> float:
    """Calculate entropy of time between emails distribution."""
    from .content_analysis import calculate_entropy
    return calculate_entropy(series.values)
