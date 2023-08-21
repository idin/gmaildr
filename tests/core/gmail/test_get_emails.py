"""
Helper function to get emails with minimum count by intelligently increasing date range.
"""

from gmaildr import Gmail


def get_emails(gmail: Gmail, n: int, **kwargs):
    """
    Get at least N emails by intelligently increasing the date range.
    
    Args:
        gmail: Gmail instance
        n: Minimum number of emails to retrieve
        **kwargs: Additional filtering parameters (in_folder, from_sender, subject_contains, etc.)
        
    Returns:
        DataFrame containing at least N emails (or all available if less than N)
    """
    days = 1
    
    while days <= 365:
        # Get emails for this date range
        # Pass through all additional filters
        emails = gmail.get_emails(days=days, max_emails=n, **kwargs)
        
        if len(emails) >= n:
            return emails.head(n)
        
        # Double the days for next iteration (exponential growth)
        days *= 2

    # If we reach here, return whatever we have
    return emails
        

def test_get_emails():
    gmail = Gmail()

    for i in [1, 10, 100]:
        emails = get_emails(gmail, i)
        assert len(emails) == i