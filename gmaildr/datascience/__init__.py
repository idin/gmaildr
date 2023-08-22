"""
DataScience module for GmailDr.

This module contains data science and analytics functionality for email analysis,
including statistical analysis, machine learning features, and advanced data processing.
"""

__version__ = "1.1.0"
__author__ = "idin"

# Import main functions
from .clustering import find_optimal_k
from .clustering import cluster
from . import feature_engineering

__all__ = [
    "find_optimal_k",
    "cluster",
    "feature_engineering",
]
