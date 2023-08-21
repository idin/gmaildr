"""
EmailMLFeaturesDataFrame - DataFrame for email machine learning features.

This module provides an EmailMLFeaturesDataFrame class that represents transformed email features
suitable for machine learning algorithms. This is different from EmailDataFrame because
it has dropped some features and transformed others.
"""

import pandas as pd
from typing import Dict, Any, Union, List, TYPE_CHECKING

from .email_dataframe import EmailDataFrame

class Email_ML_DataFrame(EmailDataFrame):
    """
    DataFrame for email machine learning features.
    
    This represents transformed email features suitable for ML algorithms.
    It IS an EmailDataFrame with transformed features for ML.
    """

    NECESSARY_COLUMNS = [
        'hour_sin', 'hour_cos', 'day_of_week_sin', 'day_of_week_cos', 
        'day_of_year_sin', 'day_of_year_cos'
    ]
    
    @property
    def _constructor(self):
        """Return the class to use for DataFrame operations."""
        return Email_ML_DataFrame

    @property
    def ml_dataframe(self) -> pd.DataFrame:
        return self