"""
Feature summary functions for email analysis.

This module provides functions to summarize and analyze features in dataframes.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any


def get_feature_summary(analysis_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Get a summary of features in the analysis dataframe.
    
    Args:
        analysis_df: Analysis-ready dataframe
        
    Returns:
        Dictionary with feature summary information
    """
    if analysis_df.empty:
        return {}
    
    summary = {
        'total_features': len(analysis_df.columns),
        'total_samples': len(analysis_df),
        'feature_types': {},
        'missing_values': {},
        'numeric_features': [],
        'categorical_features': [],
        'periodic_features': []
    }
    
    for col in analysis_df.columns:
        dtype = analysis_df[col].dtype
        
        if np.issubdtype(dtype, np.number):
            summary['numeric_features'].append(col)
            summary['feature_types'][col] = 'numeric'
        else:
            summary['categorical_features'].append(col)
            summary['feature_types'][col] = 'categorical'
        
        # Check for periodic features
        if any(periodic in col for periodic in ['_sin', '_cos']):
            summary['periodic_features'].append(col)
        
        # Missing values
        missing_count = analysis_df[col].isna().sum()
        if missing_count > 0:
            summary['missing_values'][col] = {
                'count': missing_count,
                'percentage': (missing_count / len(analysis_df)) * 100
            }
    
    summary['numeric_count'] = len(summary['numeric_features'])
    summary['categorical_count'] = len(summary['categorical_features'])
    summary['periodic_count'] = len(summary['periodic_features'])
    
    return summary
