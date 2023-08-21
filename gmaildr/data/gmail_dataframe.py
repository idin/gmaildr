"""
Base GmailDataFrame class for all Gmail-related DataFrames.

This module provides a base class that contains common functionality
shared by all Gmail DataFrame classes (EmailDataFrame, SenderDataFrame, etc.).
"""

import pandas as pd
from typing import Union, List, Dict, Any, Optional, Set, TYPE_CHECKING
from abc import ABC, abstractmethod

if TYPE_CHECKING:
    from ..core.gmail import Gmail


class GmailDataFrame(pd.DataFrame, ABC):
    """
    Base class for all Gmail-related DataFrames.
    
    This class provides common functionality shared by all Gmail DataFrame classes:
    - Gmail instance management
    - Constructor methods for pandas operations
    - Common validation and utility methods
    """

    NECESSARY_COLUMNS = []

    def is_acceptable_dataframe(self, data: pd.DataFrame) -> bool:
        if isinstance(data, self.__class__):
            return True
        
        return all(col in data.columns for col in self.NECESSARY_COLUMNS)

    def _get_dataframe_for_constructor(self, data):
        """Get the appropriate DataFrame for the constructor."""
        # Only check if it's an acceptable DataFrame if data has a columns attribute
        if hasattr(data, 'columns') and self.is_acceptable_dataframe(data):
            return self.__class__(data, gmail=self._gmail_instance)
        else:
            return data

    @classmethod
    def create_empty(cls, *, gmail: Optional[Any] = None) -> 'GmailDataFrame':
        """
        Create an empty DataFrame of the correct class.
        
        Args:
            gmail: Gmail instance for operations
            
        Returns:
            Empty DataFrame of the correct class
        """
        if gmail is None:
            # For empty DataFrames, we need to create a dummy gmail instance
            # This is a temporary solution - in practice, callers should provide a real gmail instance
            from gmaildr import Gmail
            gmail = Gmail()
        return cls(data=pd.DataFrame(), gmail=gmail)

    def __init__(self, data=None, *, gmail, **kwargs):
        """
        Initialize GmailDataFrame.
        
        Args:
            data: DataFrame data
            gmail: Gmail instance for operations
            **kwargs: Additional arguments for pandas DataFrame
        """
        super().__init__(data, **kwargs)
        self._gmail_instance = gmail

    @property
    def gmail(self) -> 'Gmail':
        """
        Get the Gmail instance associated with this DataFrame.
        """
        if self._gmail_instance is None:
            raise ValueError("Gmail instance is not set")
        return self._gmail_instance

    @property
    def dataframe(self) -> pd.DataFrame:
        """
        Get a regular pandas DataFrame representation.
        
        Returns:
            Regular pandas DataFrame
        """
        return pd.DataFrame(self)

    def is_empty(self) -> bool:
        """
        Check if this DataFrame is empty.
        
        Returns:
            True if the DataFrame is empty, False otherwise
        """
        return len(self) == 0

    @property
    def _constructor_sliced(self):
        """Return the class to use for Series operations."""
        return pd.Series

    def _constructor_expanddim(self, data, axis=0):
        """Return the class to use for DataFrame operations from expanded dimension data."""
        return self._get_dataframe_for_constructor(data)

    def _constructor_reduce_dim(self, data, axis=0):
        """Return the class to use for DataFrame operations from reduced dimension data."""
        return self._get_dataframe_for_constructor(data)

    def _constructor_from_axes(self, data, axes):
        """Return the class to use for DataFrame operations from axes."""
        return self._get_dataframe_for_constructor(data)

    def _constructor_from_series(self, data, axes):
        """Return the class to use for DataFrame operations from series."""
        return self._get_dataframe_for_constructor(data)

    def _constructor_from_dict(self, data, axes):
        """Return the class to use for DataFrame operations from dict."""
        return self._get_dataframe_for_constructor(data)

    def _constructor_from_list(self, data, axes):
        """Return the class to use for DataFrame operations from list."""
        return self._get_dataframe_for_constructor(data)

    def _constructor_from_ndarray(self, data, axes):
        """Return the class to use for DataFrame operations from ndarray."""
        return self._get_dataframe_for_constructor(data)

    def _constructor_from_records(self, data, axes):
        """Return the class to use for DataFrame operations from records."""
        return self._get_dataframe_for_constructor(data)

    def _constructor_from_mgr(self, mgr, axes):
        """Return the class to use for DataFrame operations from manager."""
        # Create a pandas DataFrame first
        data = pd.DataFrame._from_mgr(mgr, axes=axes)
        # Create a new instance of this class with the gmail instance
        return self.__class__(data, gmail=self._gmail_instance)

    def set_gmail_instance(self, gmail_instance: 'Gmail') -> 'GmailDataFrame':
        """
        Set the Gmail instance for this DataFrame.
        
        Args:
            gmail_instance: Gmail instance to use for operations
            
        Returns:
            Self for method chaining
        """
        self._gmail_instance = gmail_instance
        return self

    def copy(self, deep: bool = True) -> 'GmailDataFrame':
        """
        Create a copy of this DataFrame.
        
        Args:
            deep: Whether to perform a deep copy
            
        Returns:
            Copy of this DataFrame
        """
        result = super().copy(deep=deep)
        result._gmail_instance = self._gmail_instance
        return result

    def _check_gmail_instance(self):
        """Check if Gmail instance is available."""
        if self._gmail_instance is None:
            raise ValueError("Gmail instance not set. Use set_gmail_instance() first.")
        return self._gmail_instance

    def _get_message_ids(self) -> List[str]:
        """Get message IDs from the DataFrame. To be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement _get_message_ids()")