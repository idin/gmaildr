"""
Count external links in HTML content.

This module provides functions to count external links and
related link metrics in HTML email content.
"""

import re
from typing import Optional


def email_count_external_links(html_content: Optional[str]) -> int:
    """
    Count external links in HTML content.
    
    Args:
        html_content: HTML content to analyze
        
    Returns:
        int: Number of external links found
    """
    if not html_content:
        return 0
        
    # Find all href attributes
    href_pattern = r'href=["\']([^"\']+)["\']'
    links = re.findall(href_pattern, html_content, re.IGNORECASE)
    
    # Count external links (http/https)
    external_count = 0
    for link in links:
        if link.startswith(('http://', 'https://')):
            external_count += 1
            
    return external_count
