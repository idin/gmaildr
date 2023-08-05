"""
Test to verify the correct environment is being used.

This test ensures that we're running in the right conda environment
with all the required dependencies.
"""

import unittest
import sys
import os


class TestEnvironment(unittest.TestCase):
    """Test that the correct environment is being used."""
    
    def test_python_version(self):
        """Test that we're using the correct Python version."""
        # Should be Python 3.11.x for the gmail environment
        self.assertEqual(sys.version_info.major, 3)
        self.assertEqual(sys.version_info.minor, 11)
        print(f"✅ Python version: {sys.version}")
    
    def test_conda_environment(self):
        """Test that we're in the correct conda environment."""
        conda_env = os.environ.get('CONDA_DEFAULT_ENV')
        self.assertEqual(conda_env, 'gmail')
        print(f"✅ Conda environment: {conda_env}")
    
    def test_required_packages(self):
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
        
        self.assertEqual(len(missing_packages), 0, f"Missing packages: {missing_packages}")
    
    def test_gmailwiz_imports(self):
        """Test that gmailwiz modules can be imported."""
        try:
            from gmailwiz import Gmail
            from gmailwiz.analysis import HumanEmailDetector
            from gmailwiz.core import GmailClient
            print("✅ All gmailwiz modules import successfully")
        except ImportError as e:
            self.fail(f"Failed to import gmailwiz modules: {e}")


if __name__ == '__main__':
    unittest.main()
