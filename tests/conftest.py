"""
Pytest configuration for gmaildr test suite.

Provides test timing, performance monitoring, and other test utilities.
"""

import time
import pytest
from typing import Dict, List, Tuple


class TestTimingPlugin:
    """Plugin to track and display test execution times."""
    
    def __init__(self):
        self.test_times: Dict[str, float] = {}
        self.file_times: Dict[str, List[float]] = {}
        self.start_times: Dict[str, float] = {}
    
    def pytest_runtest_setup(self, item):
        """Record test start time."""
        self.start_times[item.nodeid] = time.time()
    
    def pytest_runtest_teardown(self, item):
        """Record test end time and calculate duration."""
        if item.nodeid in self.start_times:
            duration = time.time() - self.start_times[item.nodeid]
            self.test_times[item.nodeid] = duration
            
            # Group by file
            file_path = item.fspath.basename
            if file_path not in self.file_times:
                self.file_times[file_path] = []
            self.file_times[file_path].append(duration)
    
    def pytest_terminal_summary(self, terminalreporter, exitstatus, config):
        """Display timing summary at the end of test run."""
        if not self.test_times:
            return
        
        terminalreporter.write_sep("=", "TEST TIMING SUMMARY")
        
        # Sort tests by duration (slowest first)
        sorted_tests = sorted(self.test_times.items(), key=lambda x: x[1], reverse=True)
        
        # Show top 10 slowest individual tests
        terminalreporter.write_line("\n🐌 SLOWEST INDIVIDUAL TESTS:")
        terminalreporter.write_line("─" * 80)
        for i, (test_name, duration) in enumerate(sorted_tests[:10], 1):
            # Clean up test name for display
            clean_name = test_name.split("::")[-1] if "::" in test_name else test_name
            file_name = test_name.split("::")[0].replace("tests/", "") if "::" in test_name else "unknown"
            terminalreporter.write_line(f"{i:2d}. {duration:6.2f}s  {file_name}::{clean_name}")
        
        # Calculate and show file-level timing
        file_totals = {}
        for file_path, durations in self.file_times.items():
            file_totals[file_path] = {
                'total': sum(durations),
                'count': len(durations),
                'avg': sum(durations) / len(durations),
                'max': max(durations)
            }
        
        # Sort files by total time
        sorted_files = sorted(file_totals.items(), key=lambda x: x[1]['total'], reverse=True)
        
        terminalreporter.write_line("\n📁 SLOWEST TEST FILES:")
        terminalreporter.write_line("─" * 80)
        terminalreporter.write_line(f"{'RANK':<4} {'TOTAL':<8} {'COUNT':<5} {'AVG':<6} {'MAX':<6} {'FILE'}")
        terminalreporter.write_line("─" * 80)
        
        for i, (file_path, stats) in enumerate(sorted_files[:15], 1):
            clean_file = file_path.replace("test_", "").replace(".py", "")
            terminalreporter.write_line(
                f"{i:2d}.  {stats['total']:6.2f}s  "
                f"{stats['count']:3d}   {stats['avg']:5.2f}s {stats['max']:5.2f}s  "
                f"{clean_file}"
            )
        
        # Show overall statistics
        total_time = sum(self.test_times.values())
        total_tests = len(self.test_times)
        avg_time = total_time / total_tests if total_tests > 0 else 0
        
        terminalreporter.write_line("\n📊 OVERALL STATISTICS:")
        terminalreporter.write_line("─" * 40)
        terminalreporter.write_line(f"Total test time:     {total_time:6.2f}s")
        terminalreporter.write_line(f"Total tests:         {total_tests:6d}")
        terminalreporter.write_line(f"Average per test:    {avg_time:6.2f}s")
        terminalreporter.write_line(f"Slowest test:        {max(self.test_times.values()):6.2f}s")
        
        # Performance categories
        slow_tests = [t for t in self.test_times.values() if t > 10.0]
        medium_tests = [t for t in self.test_times.values() if 3.0 <= t <= 10.0]
        fast_tests = [t for t in self.test_times.values() if t < 3.0]
        
        terminalreporter.write_line(f"\n⚡ PERFORMANCE BREAKDOWN:")
        terminalreporter.write_line("─" * 40)
        terminalreporter.write_line(f"Fast tests (<3s):    {len(fast_tests):6d} ({len(fast_tests)/total_tests*100:4.1f}%)")
        terminalreporter.write_line(f"Medium tests (3-10s): {len(medium_tests):6d} ({len(medium_tests)/total_tests*100:4.1f}%)")
        terminalreporter.write_line(f"Slow tests (>10s):   {len(slow_tests):6d} ({len(slow_tests)/total_tests*100:4.1f}%)")
        
        if slow_tests:
            terminalreporter.write_line(f"\n⚠️  {len(slow_tests)} tests are taking >10s - consider optimization")


def pytest_configure(config):
    """Register the timing plugin."""
    if not hasattr(config, '_timing_plugin'):
        config._timing_plugin = TestTimingPlugin()
        config.pluginmanager.register(config._timing_plugin, 'timing')


def pytest_unconfigure(config):
    """Unregister the timing plugin."""
    if hasattr(config, '_timing_plugin'):
        config.pluginmanager.unregister(config._timing_plugin, 'timing')


# Additional pytest configuration  
def pytest_collection_modifyitems(config, items):
    """Configure test items for timing analysis."""
    # Tests are automatically tracked by the timing plugin
    pass


# Test data utilities for consistent test performance
@pytest.fixture(scope="session")
def small_email_sample():
    """Provide a small, consistent email sample for fast tests."""
    return {
        'days': 2,
        'max_emails': 5,
        'description': 'Small sample for fast tests'
    }


@pytest.fixture(scope="session") 
def medium_email_sample():
    """Provide a medium email sample for thorough tests."""
    return {
        'days': 7,
        'max_emails': 20,
        'description': 'Medium sample for thorough tests'
    }


@pytest.fixture(scope="session")
def large_email_sample():
    """Provide a large email sample for comprehensive tests."""
    return {
        'days': 30,
        'max_emails': 100,
        'description': 'Large sample for comprehensive tests'
    }
