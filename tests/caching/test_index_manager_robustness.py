#!/usr/bin/env python3
"""
Test script to reproduce and fix JSON parsing issues in index manager.
"""

import json
import tempfile
import threading
import time
from pathlib import Path
from gmaildr.caching.index_manager import EmailIndexManager
from gmaildr.caching.cache_config import CacheConfig

def create_corrupted_json_file(file_path: Path):
    """Create a corrupted JSON file for testing."""
    # Write valid JSON first
    data = {"test": "data", "numbers": [1, 2, 3]}
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    # Append extra data to corrupt it
    with open(file_path, 'a') as f:
        f.write("\n{\"extra\": \"data\"}")

def test_json_parsing_robustness():
    """Test robust JSON parsing with corrupted files."""
    print("Testing JSON parsing robustness...")
    
    # Create temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create cache config
        config = CacheConfig(cache_dir=temp_path)
        
        # Create index manager
        index_manager = EmailIndexManager(cache_config=config, verbose=False)
        
        # Test with corrupted files
        corrupted_file = temp_path / "corrupted.json"
        create_corrupted_json_file(corrupted_file)
        
        # Test loading corrupted file
        result = index_manager._load_index(corrupted_file)
        print(f"Loading corrupted file returned: {result}")
        
        # Test with valid file
        valid_file = temp_path / "valid.json"
        valid_data = {"test": "data"}
        with open(valid_file, 'w') as f:
            json.dump(valid_data, f)
        
        result = index_manager._load_index(valid_file)
        print(f"Loading valid file returned: {result}")

if __name__ == "__main__":
    test_json_parsing_robustness()
