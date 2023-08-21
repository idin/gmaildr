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
    from gmaildr.caching.index_manager import EmailIndexManager
    from gmaildr.caching.cache_config import CacheConfig
    
    config = CacheConfig(cache_dir=Path('cache'))
    manager = EmailIndexManager(cache_config=config, verbose=False)
    print('Index manager loaded successfully')
    assert manager is not None

