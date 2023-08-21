"""
Sender data model for GmailDr.

This module contains the Sender class which represents an email sender
with address, name, and domain information.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Sender:
    """
    Represents an email sender.
    """
    
    address: str
    name: Optional[str] = None
    domain: Optional[str] = None
    
    def __post_init__(self):
        """Validate address and extract domain if not provided."""
        if self.address.count('@') != 1:
            raise ValueError(f"Email address must contain exactly one @ symbol: {self.address}")
        
        if self.domain is None and '@' in self.address:
            self.domain = self.address.split('@')[-1]
