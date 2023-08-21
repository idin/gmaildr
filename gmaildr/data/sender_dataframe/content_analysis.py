"""
Content analysis functions for sender statistics.

This module contains functions for analyzing email content patterns.
"""

import numpy as np
from collections import Counter


def calculate_entropy(series: np.ndarray) -> float:
    """
    Calculate entropy of a series of values.
    
    Args:
        series: Series of values to calculate entropy for
        
    Returns:
        Entropy value
    """
    if len(series) == 0:
        return 0.0
    
    # Count occurrences of each value
    value_counts = Counter(series)
    total_count = len(series)
    
    # Calculate entropy
    entropy = 0.0
    for count in value_counts.values():
        if count > 0:
            probability = count / total_count
            entropy -= probability * np.log2(probability)
    
    return entropy


def extract_common_keywords(subjects: list) -> list:
    """
    Extract common keywords from a list of email subjects.
    
    Args:
        subjects: List of email subjects
        
    Returns:
        List of most common keywords (up to 5)
    """
    all_words = []
    
    for subject in subjects:
        if subject and isinstance(subject, str):
            words = subject.lower().split()
            all_words.extend([word for word in words if len(word) > 2])
    
    if not all_words:
        return []
    
    word_counts = Counter(all_words)
    return [word for word, count in word_counts.most_common(5)]
