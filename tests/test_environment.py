"""
Test to verify the correct environment is being used.

This test ensures that we're running in the right conda environment
with all the required dependencies.
"""

import sys
import os


def test_python_version():
    """Test that we're using the correct Python version."""
    # Should be Python 3.11.x for the gmail environment
    assert sys.version_info.major == 3
    assert sys.version_info.minor == 11
    print(f"✅ Python version: {sys.version}")


def test_conda_environment():
    """Test that we're in the correct conda environment."""
    conda_env = os.environ.get('CONDA_DEFAULT_ENV')
    assert conda_env == 'gmail'
    print(f"✅ Conda environment: {conda_env}")


def test_required_packages():
    """Test that required packages are available."""
    required_packages = [
        'pandas',
        'numpy', 
        'google',
        'google_auth_oauthlib',
        'google_auth_httplib2',
        'googleapiclient',
        'tqdm'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} is available")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} is missing")
    
    assert len(missing_packages) == 0, f"Missing packages: {missing_packages}"


def test_gmaildr_imports():
    """Test that gmaildr modules can be imported."""
    try:
        from gmaildr import Gmail
        from gmaildr.analysis import HumanEmailDetector
        from gmaildr.core import GmailClient
        print("✅ All gmaildr modules import successfully")
    except ImportError as e:
        assert False, f"Failed to import gmaildr modules: {e}"
