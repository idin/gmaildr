#!/usr/bin/env python3
"""
Test EmailAnalyzer class functionality.
"""

import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def test_email_analyzer_import():
    """Test that EmailAnalyzer class can be imported."""
    from gmailwiz.analysis.email_analyzer import EmailAnalyzer
    print("✅ EmailAnalyzer class import successful")


def test_email_analyzer_initialization():
    """Test EmailAnalyzer class initialization."""
    from gmailwiz.analysis.email_analyzer import EmailAnalyzer
    from gmailwiz.core.gmail_client import GmailClient
    
    # Mock GmailClient for testing
    class MockGmailClient:
        pass
    
    client = MockGmailClient()
    analyzer = EmailAnalyzer(client)
    assert analyzer is not None
    print("✅ EmailAnalyzer initialization successful")


if __name__ == "__main__":
    print("🧪 Testing EmailAnalyzer class...")
    test_email_analyzer_import()
    test_email_analyzer_initialization()
    print("🎉 All EmailAnalyzer tests passed!")
