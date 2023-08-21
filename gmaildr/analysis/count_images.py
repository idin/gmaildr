"""
Count images in HTML content.

This module provides functions to count images and
related image metrics in HTML email content.
"""

import re
from typing import Optional


def email_count_images(html_content: Optional[str]) -> int:
    """
    Count images in HTML content.
    
    Args:
        html_content: HTML content to analyze
        
    Returns:
        int: Number of images found
    """
    if not html_content:
        return 0
        
    # Look for various image patterns
    img_patterns = [
        r'<img[^>]*>',  # Standard img tags
        r'background.*image.*url',  # CSS background images
        r'background.*url',  # CSS background images
        r'<svg[^>]*>',  # SVG images
        r'<canvas[^>]*>',  # Canvas elements (might contain images)
        r'data.*image',  # Data URLs with images
        r'base64.*image'  # Base64 encoded images
    ]
    
    total_images = 0
    for pattern in img_patterns:
        matches = re.findall(pattern, html_content, re.IGNORECASE)
        total_images += len(matches)
        
    return total_images
