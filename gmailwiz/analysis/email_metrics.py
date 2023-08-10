"""
Email content analysis metrics for identifying automated/commercial emails.

This module provides functions to analyze email text content and extract
metrics that help distinguish between personal and automated emails.
"""

import re
from typing import Dict, Any, Optional
from dataclasses import dataclass
from gmailwiz.utils import match_patterns


@dataclass
class EmailMetrics:
    """Container for all email content metrics."""
    
    # Flags (boolean)
    has_unsubscribe_link: bool = False
    has_marketing_language: bool = False
    has_legal_disclaimer: bool = False
    has_promotional_content: bool = False
    has_tracking_pixels: bool = False
    has_bulk_email_indicators: bool = False
    
    # Counts (numerical)
    external_link_count: int = 0
    image_count: int = 0
    exclamation_count: int = 0
    caps_word_count: int = 0
    
    # Ratios (0.0 to 1.0)
    html_to_text_ratio: float = 0.0
    link_to_text_ratio: float = 0.0
    caps_ratio: float = 0.0
    promotional_word_ratio: float = 0.0
    proper_capitalization_ratio: float = 0.0


class EmailContentAnalyzer:
    """
    Analyzes email content to extract metrics for automated email detection.
    """
    
    # Patterns for different types of indicators
    UNSUBSCRIBE_PATTERNS = [
        r'unsubscribe',
        r'opt.?out',
        r'remove.*list',
        r'stop.*email',
        r'manage.*subscription',
        r'email.*preference',
        r'click.*unsubscribe',
        r'unsubscribe.*here',
        r'to.*unsubscribe',
        r'if.*unsubscribe',
        r'opt.?out.*email',
        r'remove.*email',
        r'stop.*receiving',
        r'no.*longer.*want',
        r'preference.*center',
        r'email.*settings'
    ]
    
    MARKETING_PATTERNS = [
        r'limited.*time',
        r'act.*now',
        r'don\'t.*miss',
        r'exclusive.*offer',
        r'sale.*end',
        r'hurry.*up',
        r'click.*here',
        r'call.*action'
    ]
    
    LEGAL_PATTERNS = [
        r'terms.*condition',
        r'privacy.*policy',
        r'disclaimer',
        r'confidential',
        r'copyright',
        r'all.*rights.*reserved',
        r'this.*email.*intended'
    ]
    
    PROMOTIONAL_WORDS = [
        'sale', 'discount', 'offer', 'deal', 'free', 'save', 'percent', '%',
        'buy', 'shop', 'purchase', 'order', 'promo', 'special', 'limited',
        'exclusive', 'bonus', 'gift', 'win', 'prize', 'contest', 'coupon'
    ]
    
    BULK_EMAIL_INDICATORS = [
        r'this.*automated.*message',
        r'do.*not.*reply',
        r'automatically.*generated',
        r'system.*notification',
        r'noreply',
        r'no.reply',
        r'bulk.*mail'
    ]
    
    def __init__(self):
        """Initialize the analyzer with compiled regex patterns."""
        self.unsubscribe_regex = re.compile('|'.join(self.UNSUBSCRIBE_PATTERNS), re.IGNORECASE)
        self.marketing_regex = re.compile('|'.join(self.MARKETING_PATTERNS), re.IGNORECASE)
        self.legal_regex = re.compile('|'.join(self.LEGAL_PATTERNS), re.IGNORECASE)
        self.bulk_regex = re.compile('|'.join(self.BULK_EMAIL_INDICATORS), re.IGNORECASE)
        
    def analyze_email_content(
        self, *,
        text_content: Optional[str] = None,
        html_content: Optional[str] = None,
        subject: Optional[str] = None
    ) -> EmailMetrics:
        """
        Analyze email content and return comprehensive metrics.
        
        Args:
            text_content (Optional[str]): Plain text content of email.
            html_content (Optional[str]): HTML content of email.
            subject (Optional[str]): Email subject line.
            
        Returns:
            EmailMetrics: Container with all calculated metrics.
        """
        metrics = EmailMetrics()
        
        # Combine all available text for analysis
        combined_text = self._combine_text(
            text_content=text_content,
            html_content=html_content,
            subject=subject
        )
        
        if not combined_text:
            return metrics
            
        # Calculate flags
        metrics.has_unsubscribe_link = self._has_unsubscribe_indicators(
            text=combined_text,
            html_content=html_content
        )
        metrics.has_marketing_language = bool(self.marketing_regex.search(combined_text))
        metrics.has_legal_disclaimer = bool(self.legal_regex.search(combined_text))
        metrics.has_promotional_content = self._has_promotional_content(combined_text)
        metrics.has_tracking_pixels = self._has_tracking_pixels(html_content)
        metrics.has_bulk_email_indicators = bool(self.bulk_regex.search(combined_text))
        
        # Calculate counts
        metrics.external_link_count = self._count_external_links(html_content)
        metrics.image_count = self._count_images(html_content)
        metrics.exclamation_count = combined_text.count('!')
        metrics.caps_word_count = self._count_caps_words(combined_text)
        
        # Calculate ratios
        metrics.html_to_text_ratio = self._calculate_html_ratio(text_content, html_content)
        metrics.link_to_text_ratio = self._calculate_link_ratio(combined_text, html_content)
        metrics.caps_ratio = self._calculate_caps_ratio(text=combined_text)
        metrics.promotional_word_ratio = self._calculate_promotional_ratio(text=combined_text)
        metrics.proper_capitalization_ratio = self._calculate_proper_capitalization_ratio(text=combined_text)
        
        return metrics
    
    def _combine_text(
        self, *,
        text_content: Optional[str], 
        html_content: Optional[str], 
        subject: Optional[str]
    ) -> str:
        """Combine all available text content for analysis."""
        parts = []
        
        if subject:
            parts.append(subject)
        if text_content:
            parts.append(text_content)
        if html_content:
            # Extract text from HTML (simple approach)
            clean_html = re.sub(r'<[^>]+>', ' ', html_content)
            parts.append(clean_html)
            
        return ' '.join(parts)
    
    def _has_unsubscribe_indicators(
        self, *,
        text: str, 
        html_content: Optional[str]
    ) -> bool:
        """Check for unsubscribe links or text.

        Uses lightweight wildcard pattern matching. Note: The legacy
        regex-like entries in `UNSUBSCRIBE_PATTERNS` contain dots and
        question-marks with regex semantics; here we map to simpler
        phrases suitable for string wildcard matching.
        """
        simplified_patterns = [
            "unsubscribe",
            "opt out",
            "opt-out",
            "remove list",
            "stop email",
            "manage subscription",
            "email preference",
            "click unsubscribe",
            "unsubscribe here",
            "to unsubscribe",
            "remove email",
            "stop receiving",
            "no longer want",
            "preference center",
            "email settings",
        ]

        if match_patterns(text, simplified_patterns):
            return True

        if html_content and match_patterns(html_content, "unsubscribe"):
            return True

        return False
    
    def _has_promotional_content(self, text: str) -> bool:
        """Check if text contains promotional language."""
        word_pattern = r'\b(' + '|'.join(self.PROMOTIONAL_WORDS) + r')\b'
        matches = re.findall(word_pattern, text, re.IGNORECASE)
        return len(matches) >= 2  # At least 2 promotional words
    
    def _has_tracking_pixels(self, html_content: Optional[str]) -> bool:
        """Check for tracking pixels in HTML."""
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
    
    def _count_external_links(self, html_content: Optional[str]) -> int:
        """Count external links in HTML content."""
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
    
    def _count_images(self, html_content: Optional[str]) -> int:
        """Count images in HTML content."""
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
    
    def _count_caps_words(self, text: str) -> int:
        """Count words that are all uppercase."""
        if not text:
            return 0
        
        # Split text into words and count those that are all uppercase
        words = text.split()
        caps_count = 0
        
        for word in words:
            # Remove punctuation from the word for checking
            clean_word = ''.join(char for char in word if char.isalnum())
            
            # Check if the clean word is all uppercase and has 2+ characters
            if (len(clean_word) >= 2 and 
                clean_word.isupper() and 
                clean_word.isalpha()):  # Only letters, no numbers
                caps_count += 1
        
        return caps_count
    
    def _calculate_html_ratio(
        self, 
        text_content: Optional[str], 
        html_content: Optional[str]
    ) -> float:
        """Calculate ratio of HTML to text content."""
        if not html_content:
            return 0.0
            
        html_len = len(html_content)
        text_len = len(text_content) if text_content else 0
        
        if text_len == 0:
            return 1.0
            
        return min(html_len / text_len, 10.0)  # Cap at 10.0
    
    def _calculate_link_ratio(
        self, 
        text: str, 
        html_content: Optional[str]
    ) -> float:
        """Calculate ratio of links to total text."""
        link_count = self._count_external_links(html_content)
        word_count = len(text.split())
        
        if word_count == 0:
            return 0.0
            
        return min(link_count / word_count, 1.0)  # Cap at 1.0
    
    def _calculate_caps_ratio(self, text: str) -> float:
        """Calculate ratio of uppercase words to total words."""
        caps_count = self._count_caps_words(text)
        total_words = len(text.split())
        
        if total_words == 0:
            return 0.0
            
        return caps_count / total_words
    
    def _calculate_promotional_ratio(self, text: str) -> float:
        """Calculate ratio of promotional words to total words."""
        word_pattern = r'\b(' + '|'.join(self.PROMOTIONAL_WORDS) + r')\b'
        promo_count = len(re.findall(word_pattern, text, re.IGNORECASE))
        total_words = len(re.findall(r'\b\w+\b', text))
        
        if total_words == 0:
            return 0.0
            
        return promo_count / total_words
    
    def _calculate_proper_capitalization_ratio(self, text: str) -> float:
        """Calculate ratio of properly capitalized sentence-starting words."""
        if not text:
            return 0.0
        
        # Replace all sentence endings with periods
        normalized_text = text.replace('!', '.').replace('?', '.').replace('\n', '.')
        
        # Split by periods to get sentences
        sentences = normalized_text.split('.')
        
        properly_capitalized = 0
        total_sentences = 0
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # Get first character that's a letter
            for char in sentence:
                if char.isalpha():
                    total_sentences += 1
                    if char.isupper():
                        properly_capitalized += 1
                    break
        
        if total_sentences == 0:
            return 0.0
            
        return properly_capitalized / total_sentences


# Global analyzer instance
analyzer = EmailContentAnalyzer()


def analyze_email_text(
    text_content: Optional[str] = None,
    html_content: Optional[str] = None,
    subject: Optional[str] = None
) -> Dict[str, Any]:
    """
    Convenience function to analyze email content and return metrics as dictionary.
    
    Args:
        text_content (Optional[str]): Plain text content.
        html_content (Optional[str]): HTML content.
        subject (Optional[str]): Email subject.
        
    Returns:
        Dict[str, Any]: Dictionary of all metrics.
    """
    metrics = analyzer.analyze_email_content(
        text_content=text_content,
        html_content=html_content,
        subject=subject
    )
    
    return {
        # Flags
        'has_unsubscribe_link': metrics.has_unsubscribe_link,
        'has_marketing_language': metrics.has_marketing_language,
        'has_legal_disclaimer': metrics.has_legal_disclaimer,
        'has_promotional_content': metrics.has_promotional_content,
        'has_tracking_pixels': metrics.has_tracking_pixels,
        'has_bulk_email_indicators': metrics.has_bulk_email_indicators,
        
        # Counts
        'external_link_count': metrics.external_link_count,
        'image_count': metrics.image_count,
        'exclamation_count': metrics.exclamation_count,
        'caps_word_count': metrics.caps_word_count,
        
        # Ratios
        'html_to_text_ratio': round(metrics.html_to_text_ratio, 3),
        'link_to_text_ratio': round(metrics.link_to_text_ratio, 3),
        'caps_ratio': round(metrics.caps_ratio, 3),
        'promotional_word_ratio': round(metrics.promotional_word_ratio, 3),
        'proper_capitalization_ratio': round(metrics.proper_capitalization_ratio, 3),
    }
