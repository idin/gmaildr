#!/usr/bin/env python3
"""
Simple test script to demonstrate logging without printing to console.
"""

import logging
import os
from pathlib import Path

def test_logging_to_file():
    """
    Test that logging works correctly when writing to file only.
    """
    # Create logs directory if it doesn't exist
    logs_dir = Path(__file__).parent.parent.parent / 'logs'
    logs_dir.mkdir(exist_ok=True)
    
    log_file = logs_dir / 'test.log'
    
    # Set up logging to ONLY write to file, not console
    # Create a new logger to avoid conflicts with pytest's logging
    logger = logging.getLogger('test_file_logger')
    logger.setLevel(logging.INFO)
    
    # Remove any existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create file handler
    file_handler = logging.FileHandler(str(log_file), mode='w')
    file_handler.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(file_handler)

    # These messages will ONLY go to the log file, not console
    logger.info("This message goes to log file only")
    logger.info("Another message to log file only")
    logger.warning("Warning message to log file only")

    # Verify the log file was created and contains the expected content
    assert log_file.exists(), "Log file should be created"
    
    with open(log_file, 'r') as f:
        content = f.read()
        assert "This message goes to log file only" in content
        assert "Another message to log file only" in content
        assert "Warning message to log file only" in content
    
    # Clean up - remove the log file after test
    log_file.unlink()
    
    print("✅ Logging test completed successfully - log file created and cleaned up")

if __name__ == "__main__":
    test_logging_to_file()
