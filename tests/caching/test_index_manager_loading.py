#!/usr/bin/env python3
"""
Test index manager loading with existing cache files.
"""

import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def test_index_manager_loading():
    """Test that the index manager loads successfully with existing cache."""
    try:
        from gmaildr.caching.index_manager import EmailIndexManager
        from gmaildr.caching.cache_config import CacheConfig
        
        config = CacheConfig(cache_dir=Path('cache'))
        manager = EmailIndexManager(config)
        print('Index manager loaded successfully')
        return True
    except Exception as error:
        print(f'Failed to load index manager: {error}')
        return False

if __name__ == "__main__":
    # Run the test multiple times to check for consistency
    for i in range(3):
        print(f"Test run {i+1}:")
        success = test_index_manager_loading()
        if not success:
            sys.exit(1)
        print()
