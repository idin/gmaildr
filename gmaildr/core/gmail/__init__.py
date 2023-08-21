"""
Gmail submodule for organized Gmail functionality.

This submodule contains:
- GmailBase: Basic authentication and client access
- EmailModifier: Basic email modification operations
- LabelOperator: Label management operations
- GmailHelper: Helper methods and properties
- CachedGmail: Cache operations and management
- EmailOperator: Complex email operations
"""

from .main import Gmail

# other classes do not need to be exposed outside of this module
__all__ = ['Gmail']
