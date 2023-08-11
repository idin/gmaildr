"""
Progress bar utilities for Gmail cleaner.

This module provides colorful, cross-platform progress bars that work
consistently in both terminal and Jupyter notebook environments.
"""

from typing import Iterator, TypeVar, Callable, Optional
from tqdm.auto import tqdm

T = TypeVar('T')


class EmailProgressTracker:
    """
    A wrapper class for tracking email processing progress with colorful progress bars.
    
    This class provides a consistent progress bar interface that works in both
    terminal and Jupyter notebook environments using tqdm.
    """
    
    def __init__(
        self, *,
        total: int,
        description: str = "Processing emails",
        use_batch_mode: bool = False
    ):
        """
        Initialize the progress tracker.
        
        Args:
            total (int): Total number of items to process.
            description (str): Description text for the progress bar.
            use_batch_mode (bool): Whether this is batch mode processing.
        """
        self.total = total
        self.description = description
        self.use_batch_mode = use_batch_mode
        
        # Create the progress bar with nice styling
        emoji = "⚡" if use_batch_mode else "📧"
        mode_text = " (batch mode)" if use_batch_mode else ""
        full_desc = f"{emoji} {description}{mode_text}"
        
        # Create a custom bar format with percentage inside the bar
        percentage_format = "{percentage:3.0f}%"
        self.progress_bar = tqdm(
            total=total,
            desc=full_desc,
            unit="email",
            colour="green",
            bar_format="{bar}| {n_fmt}/{total_fmt} emails [{elapsed}<{remaining}] {postfix}"
        )
    
    def update(self, count: int = 1) -> None:
        """
        Update the progress bar by the specified count.
        
        Args:
            count (int): Number of items processed in this update.
        """
        self.progress_bar.update(count)
    
    def set_description(self, description: str) -> None:
        """
        Update the progress bar description.
        
        Args:
            description (str): New description text.
        """
        emoji = "⚡" if self.use_batch_mode else "📧"
        mode_text = " (batch mode)" if self.use_batch_mode else ""
        full_desc = f"{emoji} {description}{mode_text}"
        self.progress_bar.set_description(full_desc)
    
    def set_postfix(self, message: str) -> None:
        """
        Set a postfix message that appears after the progress bar.
        
        Args:
            message (str): Message to display after the progress bar.
        """
        self.progress_bar.set_postfix_str(message)
    
    def close(self) -> None:
        """Close the progress bar."""
        self.progress_bar.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


def track_email_processing(
    iterable: Iterator[T], *,
    total: int,
    description: str = "Processing emails",
    use_batch_mode: bool = False,
    update_callback: Optional[Callable[[T], int]] = None
) -> Iterator[T]:
    """
    Track progress while iterating over email processing tasks.
    
    Args:
        iterable: The iterator to track progress for.
        total: Total number of items expected.
        description: Description text for the progress bar.
        use_batch_mode: Whether this is batch mode processing.
        update_callback: Optional function to determine how many items each iteration represents.
        
    Yields:
        Items from the iterable with progress tracking.
    """
    with EmailProgressTracker(total=total, description=description, use_batch_mode=use_batch_mode) as tracker:
        for item in iterable:
            yield item
            # Determine how many items this iteration represents
            count = update_callback(item) if update_callback else 1
            tracker.update(count)
