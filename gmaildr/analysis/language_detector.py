"""
Language detection module for email content analysis.

This module provides a simple interface for detecting the language of email text,
with the ability to easily swap out the underlying language detection library.
"""

import logging
from typing import Optional, Tuple

# Import langid at module level
try:
    import langid
    LANGID_AVAILABLE = True
except ImportError:
    langid = None
    LANGID_AVAILABLE = False

logger = logging.getLogger(__name__)


def detect_language(text: str) -> Tuple[str, float]:
    """
    Detect the most probable language of the given text.
    
    Args:
        text: The text to analyze for language detection
        
    Returns:
        A tuple containing:
            - language_code: ISO 639-1 language code (e.g., 'en', 'es', 'fr')
            - confidence: Confidence score between 0.0 and 1.0
            
    Raises:
        ValueError: If text is empty or contains no detectable content
        RuntimeError: If language detection fails for any reason
    """
    if not text or not text.strip():
        raise ValueError("Text cannot be empty for language detection")
    
    try:
        # Use langid for language detection if available
        if not LANGID_AVAILABLE or langid is None:
            raise RuntimeError("langid library is not available. Please install it with: pip install langid")
        
        # langid returns (language_code, log_probability)
        # Higher (less negative) values indicate higher confidence
        language_code, log_probability = langid.classify(text)
        
        # Convert log probability to confidence score (0.0 to 1.0)
        # langid log probabilities are typically between -200 and 0
        # We normalize this to 0.0-1.0 range
        # Higher (less negative) log probability = higher confidence
        if log_probability >= 0:
            confidence = 1.0
        elif log_probability <= -200:
            confidence = 0.0
        else:
            # Normalize: -200 -> 0.0, 0 -> 1.0
            confidence = (log_probability + 200) / 200
        
        return (language_code, confidence)
            
    except Exception as e:
        logger.error(f"Language detection failed: {e}")
        raise RuntimeError(f"Language detection failed: {e}")


def detect_language_safe(text: str) -> Tuple[str, float]:
    """
    Safe version of detect_language that returns default values on failure.
    
    Args:
        text: The text to analyze for language detection
        
    Returns:
        A tuple containing:
            - language_code: ISO 639-1 language code or 'unknown'
            - confidence: Confidence score between 0.0 and 1.0
    """
    try:
        return detect_language(text)
    except (ValueError, RuntimeError) as e:
        logger.warning(f"Language detection failed, returning default: {e}")
        return ('unknown', 0.0)


def is_english(text: str, confidence_threshold: float = 0.5) -> bool:
    """
    Check if the text is likely to be English.
    
    Args:
        text: The text to analyze
        confidence_threshold: Minimum confidence threshold
        
    Returns:
        True if text is likely English, False otherwise
    """
    try:
        language_code, confidence = detect_language(text)
        return language_code == 'en' and confidence >= confidence_threshold
    except (ValueError, RuntimeError):
        return False


def get_supported_languages() -> list:
    """
    Get a list of supported language codes.
    
    Returns:
        list: List of ISO 639-1 language codes supported by the detector.
    """
    # langid supports 97+ languages, here are the most common ones
    return [
        'en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'ja', 'ko', 'zh', 'ar', 'hi', 'th',
        'vi', 'tr', 'pl', 'nl', 'sv', 'da', 'no', 'fi', 'cs', 'sk', 'hu', 'ro', 'bg',
        'hr', 'sr', 'sl', 'et', 'lv', 'lt', 'mt', 'ga', 'cy', 'eu', 'ca', 'gl', 'is',
        'fo', 'sq', 'mk', 'bs', 'me', 'ms', 'id', 'tl', 'my', 'km', 'lo', 'ne', 'si',
        'bn', 'ur', 'fa', 'he', 'am', 'ti', 'om', 'so', 'sw', 'zu', 'af', 'st', 'tn',
        'ts', 'ss', 'rw', 'ak', 'yo', 'ig', 'ha', 'mg', 'ml', 'ta', 'te', 'kn', 'gu',
        'pa', 'or', 'as', 'mr', 'sa', 'dv', 'ps', 'ku', 'ckb', 'ug', 'bo', 'dz', 'mn',
        'ka', 'hy', 'az', 'kk', 'ky', 'uz', 'tk', 'tg', 'mn', 'ka', 'hy', 'az', 'kk',
        'ky', 'uz', 'tk', 'tg'
    ]


# Language code to name mapping for better readability
LANGUAGE_NAMES = {
    'en': 'English',
    'es': 'Spanish', 
    'fr': 'French',
    'de': 'German',
    'it': 'Italian',
    'pt': 'Portuguese',
    'ru': 'Russian',
    'ja': 'Japanese',
    'ko': 'Korean',
    'zh': 'Chinese',
    'ar': 'Arabic',
    'hi': 'Hindi',
    'th': 'Thai',
    'vi': 'Vietnamese',
    'tr': 'Turkish',
    'pl': 'Polish',
    'nl': 'Dutch',
    'sv': 'Swedish',
    'da': 'Danish',
    'no': 'Norwegian',
    'fi': 'Finnish',
    'cs': 'Czech',
    'sk': 'Slovak',
    'hu': 'Hungarian',
    'ro': 'Romanian',
    'bg': 'Bulgarian',
    'hr': 'Croatian',
    'sr': 'Serbian',
    'sl': 'Slovenian',
    'et': 'Estonian',
    'lv': 'Latvian',
    'lt': 'Lithuanian',
    'mt': 'Maltese',
    'ga': 'Irish',
    'cy': 'Welsh',
    'eu': 'Basque',
    'ca': 'Catalan',
    'gl': 'Galician',
    'is': 'Icelandic',
    'fo': 'Faroese',
    'sq': 'Albanian',
    'mk': 'Macedonian',
    'bs': 'Bosnian',
    'me': 'Montenegrin',
    'ms': 'Malay',
    'id': 'Indonesian',
    'tl': 'Tagalog',
    'my': 'Burmese',
    'km': 'Khmer',
    'lo': 'Lao',
    'ne': 'Nepali',
    'si': 'Sinhala',
    'bn': 'Bengali',
    'ur': 'Urdu',
    'fa': 'Persian',
    'he': 'Hebrew',
    'am': 'Amharic',
    'ti': 'Tigrinya',
    'om': 'Oromo',
    'so': 'Somali',
    'sw': 'Swahili',
    'zu': 'Zulu',
    'af': 'Afrikaans',
    'st': 'Southern Sotho',
    'tn': 'Tswana',
    'ts': 'Tsonga',
    'ss': 'Swati',
    'rw': 'Kinyarwanda',
    'ak': 'Akan',
    'yo': 'Yoruba',
    'ig': 'Igbo',
    'ha': 'Hausa',
    'mg': 'Malagasy',
    'ml': 'Malayalam',
    'ta': 'Tamil',
    'te': 'Telugu',
    'kn': 'Kannada',
    'gu': 'Gujarati',
    'pa': 'Punjabi',
    'or': 'Odia',
    'as': 'Assamese',
    'mr': 'Marathi',
    'sa': 'Sanskrit',
    'dv': 'Divehi',
    'ps': 'Pashto',
    'ku': 'Kurdish',
    'ckb': 'Central Kurdish',
    'ug': 'Uyghur',
    'bo': 'Tibetan',
    'dz': 'Dzongkha',
    'mn': 'Mongolian',
    'ka': 'Georgian',
    'hy': 'Armenian',
    'az': 'Azerbaijani',
    'kk': 'Kazakh',
    'ky': 'Kyrgyz',
    'uz': 'Uzbek',
    'tk': 'Turkmen',
    'tg': 'Tajik',
    'unknown': 'Unknown'
}


def get_language_name(language_code: str) -> str:
    """
    Get the human-readable name for a language code.
    
    Args:
        language_code: ISO 639-1 language code
        
    Returns:
        Human-readable language name
    """
    return LANGUAGE_NAMES.get(language_code, f'Unknown ({language_code})')
