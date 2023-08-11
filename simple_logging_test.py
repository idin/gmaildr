#!/usr/bin/env python3
"""
Simple test script to demonstrate logging without printing to console.
"""

import logging

# Set up logging to ONLY write to file, not console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='test.log',  # Only log to file
    filemode='w'
)

# Get a logger
logger = logging.getLogger('test')

# These messages will ONLY go to the log file, not console
logger.info("This message goes to log file only")
logger.info("Another message to log file only")
logger.warning("Warning message to log file only")

print("This print statement will show in console")
print("But the logger messages above will NOT show in console")

print("\nCheck the test.log file to see the logged messages.")
