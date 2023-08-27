#!/usr/bin/env python3
"""
Simple commit reminder script.
Checks if there are uncommitted changes and reminds to commit.
"""

import subprocess
import sys
from datetime import datetime

def check_git_status():
    """Check if there are uncommitted changes."""
    try:
        # Check for staged changes
        staged = subprocess.run(['git', 'diff', '--cached', '--quiet'], 
                              capture_output=True)
        
        # Check for unstaged changes  
        unstaged = subprocess.run(['git', 'diff', '--quiet'], 
                                capture_output=True)
        
        # Check for untracked files
        untracked = subprocess.run(['git', 'ls-files', '--others', '--exclude-standard'], 
                                 capture_output=True, text=True)
        
        has_staged = staged.returncode != 0
        has_unstaged = unstaged.returncode != 0
        has_untracked = bool(untracked.stdout.strip())
        
        return has_staged, has_unstaged, has_untracked
        
    except subprocess.CalledProcessError:
        print("❌ Not in a git repository")
        return False, False, False

def main():
    """Main commit reminder function."""
    print("🔍 Checking git status...")
    
    has_staged, has_unstaged, has_untracked = check_git_status()
    
    if not (has_staged or has_unstaged or has_untracked):
        print("✅ No uncommitted changes - you're good!")
        return
    
    print("\n⚠️  UNCOMMITTED CHANGES DETECTED:")
    
    if has_staged:
        print("   📦 Staged changes ready to commit")
    
    if has_unstaged:
        print("   📝 Modified files not staged")
        
    if has_untracked:
        print("   ❓ Untracked files")
    
    print("\n💡 RECOMMENDATIONS:")
    print("   • For experimental work: icommit -m 'wip: [description]'")
    print("   • For stable work: icommit -m '[proper commit message]'")
    print("   • For risky experiments: create a branch first")
    
    # Show brief status
    print("\n📊 Current status:")
    subprocess.run(['git', 'status', '--short'])

if __name__ == "__main__":
    main()
