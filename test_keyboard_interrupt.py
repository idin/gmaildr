#!/usr/bin/env python3
"""
Test script to demonstrate keyboard interrupt handling in email retrieval.
"""

from gmaildr.core.gmail import Gmail

def test_keyboard_interrupt():
    """Test that keyboard interrupts are handled gracefully."""
    print("Testing keyboard interrupt handling...")
    print("This will retrieve emails and you can interrupt with Ctrl+C")
    print("The system should return partial results instead of crashing.")
    print()
    
    gmail = Gmail()
    
    try:
        # Try to get a large number of emails to give time for interruption
        print("Starting email retrieval (try Ctrl+C to interrupt)...")
        df = gmail.get_emails(
            days=365,  # Large date range
            max_emails=1000,  # Large number of emails
            include_text=True,  # Include text to make it slower
            use_batch=True
        )
        
        print(f"✅ Successfully retrieved {len(df)} emails")
        print("No interruption occurred.")
        
    except KeyboardInterrupt:
        print("\n❌ KeyboardInterrupt was not caught - this means the handling isn't working")
        raise
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        raise

if __name__ == "__main__":
    test_keyboard_interrupt()
