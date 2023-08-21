"""
Language Detection Example.

This example demonstrates how to use the language detection module
for analyzing email content in different languages.
"""

from gmaildr.analysis.language_detector import (
    detect_language,
    detect_language_safe,
    is_english,
    get_language_name
)


def main():
    """Demonstrate language detection functionality."""
    print("🌍 Language Detection Example")
    print("=" * 50)
    
    # Test texts in different languages
    test_texts = [
        "Hello, how are you today?",
        "Hola, ¿cómo estás hoy?",
        "Bonjour, comment allez-vous aujourd'hui?",
        "Hallo, wie geht es dir heute?",
        "Ciao, come stai oggi?",
        "Привет, как дела?",
        "こんにちは、お元気ですか？",
        "안녕하세요, 오늘 어떠세요?",
        "你好，今天怎么样？",
        "",  # Empty text
        "12345 @#$%^&*()",  # Special characters
    ]
    
    print("Testing language detection:")
    print("-" * 30)
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n{i}. Text: '{text[:30]}{'...' if len(text) > 30 else ''}'")
        
        # Use safe detection to handle empty text
        language_code, confidence = detect_language_safe(text)
        language_name = get_language_name(language_code)
        
        print(f"   Language: {language_name} ({language_code})")
        print(f"   Confidence: {confidence:.2f}")
        print(f"   Is English: {is_english(text)}")
    
    print("\n" + "=" * 50)
    print("Example with error handling:")
    print("-" * 30)
    
    # Demonstrate error handling
    try:
        language_code, confidence = detect_language("")
        print(f"Language: {language_code}, Confidence: {confidence}")
    except ValueError as e:
        print(f"Error caught: {e}")
    
    # Safe version handles errors gracefully
    language_code, confidence = detect_language_safe("")
    print(f"Safe detection result: {language_code}, {confidence}")


if __name__ == "__main__":
    main()
