"""
Count capitalized words in text.

This module provides functions to count words that are all uppercase
in email text content.
"""


def email_count_caps_words(text: str) -> int:
    """
    Count words that are all uppercase.
    
    Args:
        text: Text content to analyze
        
    Returns:
        int: Number of all-caps words found
    """
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
