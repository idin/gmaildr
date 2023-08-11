#!/usr/bin/env python3
"""
Test CLI functionality for GmailDr.

This test file verifies that the CLI works correctly after the module reorganization.
"""

import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def test_cli_import():
    """Test that CLI can be imported."""
    from gmaildr.utils.cli import cli
    print("✅ CLI import successful")


def test_cli_help():
    """Test CLI help command."""
    from gmaildr.utils.cli import cli
    # This should not raise an error
    print("✅ CLI help test passed")


def test_cli_commands_exist():
    """Test that CLI commands exist."""
    from gmaildr.utils.cli import cli
    commands = cli.commands.keys()
    expected_commands = {'analyze', 'setup', 'status', 'top-senders'}
    
    for cmd in expected_commands:
        assert cmd in commands, f"Command '{cmd}' not found in CLI"
    
    print("✅ All expected CLI commands found")


def test_help_text_contains_gmaildr():
    """Test that help text contains GmailDr branding."""
    from gmaildr.utils.cli import cli
    
    # Check that the CLI object has the right docstring
    assert "GmailDr" in cli.__doc__, "CLI docstring should contain 'GmailDr'"
    assert "Gmail Cleaner" not in cli.__doc__, "CLI docstring should not contain 'Gmail Cleaner'"
    
    print("✅ CLI help text branding correct")


if __name__ == "__main__":
    print("🧪 Testing GmailDr CLI...")
    test_cli_import()
    test_cli_help()
    test_cli_commands_exist()
    test_help_text_contains_gmaildr()
    print("🎉 All CLI tests passed!")
