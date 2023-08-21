"""
Detect tracking pixels in HTML content.

This module provides functions to identify tracking pixels and
related tracking mechanisms in HTML email content.
"""

import re
from typing import Optional


def email_has_tracking_pixels(html_content: Optional[str]) -> bool:
    """
    Check for tracking pixels in HTML.
    
    Args:
        html_content: HTML content to analyze
        
    Returns:
        bool: True if tracking pixels are detected
    """
    if not html_content:
        return False
        
    # Look for 1x1 images or tracking domains
    tracking_patterns = [
        r'<img[^>]*(?:width=["\']1["\']|height=["\']1["\'])',
        r'<img[^>]*src=["\'][^"\']*(?:tracking|pixel|beacon|analytics|stats)',
        r'<img[^>]*src=["\'][^"\']*\.gif\?',
        r'<img[^>]*src=["\'][^"\']*\.png\?',
        r'<img[^>]*src=["\'][^"\']*\.jpg\?',
        r'<img[^>]*src=["\'][^"\']*\.jpeg\?',
        r'<img[^>]*src=["\'][^"\']*utm_',
        r'<img[^>]*src=["\'][^"\']*campaign',
        r'<img[^>]*src=["\'][^"\']*email.*track',
        r'<img[^>]*src=["\'][^"\']*open.*track',
        r'<img[^>]*src=["\'][^"\']*click.*track'
    ]
    
    for pattern in tracking_patterns:
        if re.search(pattern, html_content, re.IGNORECASE):
            return True
            
    return False
