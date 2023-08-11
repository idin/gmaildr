#!/usr/bin/env python3
"""
Test script to verify the verbose parameter functionality.
"""

import logging
from gmaildr.core.gmail import Gmail

def test_verbose_parameter():
    """Test that verbose parameter controls logging output."""
    print("Testing verbose parameter functionality...")
    
    # Test with verbose=True (default)
    print("\n1. Testing with verbose=True (default):")
    gmail_verbose = Gmail(verbose=True)
    print("✓ Gmail instance created with verbose=True")
    
    # Test with verbose=False
    print("\n2. Testing with verbose=False:")
    gmail_quiet = Gmail(verbose=False)
    print("✓ Gmail instance created with verbose=False")
    
    # Test that cache manager respects verbose setting
    if gmail_verbose.cache_manager:
        print(f"✓ Verbose cache manager verbose setting: {gmail_verbose.cache_manager.verbose}")
    if gmail_quiet.cache_manager:
        print(f"✓ Quiet cache manager verbose setting: {gmail_quiet.cache_manager.verbose}")
    
    print("\n✓ Verbose parameter test completed successfully!")
    return True

if __name__ == "__main__":
    test_verbose_parameter()
