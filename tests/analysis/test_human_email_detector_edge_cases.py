"""
Test human email detector edge cases and error handling.

This test verifies that the human email detector handles edge cases properly
and doesn't crash on invalid inputs.
"""

import unittest
import pandas as pd
from gmaildr.analysis.human_email_detector import detect_human_emails, HumanEmailDetector


class TestHumanEmailDetectorEdgeCases(unittest.TestCase):
    """Test edge cases and error handling for human email detector."""
    
    def test_empty_dataframe_handling(self):
        """Test that empty DataFrame handling works correctly."""
        empty_df = pd.DataFrame()
        result = detect_human_emails(empty_df, show_progress=False)
        
        # Should return empty DataFrame without error
        self.assertTrue(result.empty)
    
    def test_missing_sender_email_column(self):
        """Test that missing sender_email column raises proper error."""
        df_without_sender = pd.DataFrame({'subject': ['test'], 'text_content': ['test']})
        
        with self.assertRaises(ValueError, msg="DataFrame must contain 'sender_email' column"):
            detect_human_emails(df_without_sender, show_progress=False)
    
    def test_human_email_score_threshold(self):
        """Test that human email score is reasonable."""
        detector = HumanEmailDetector()
        
        # Test with human-like email content
        score = detector.analyze_single_email(
            text_content="Hi there, how are you? I hope you're doing well.",
            subject="Meeting tomorrow",
            sender_email="john.smith@gmail.com",
            sender_name="John Smith"
        )
        
        # Should have reasonable score (not too high, not too low)
        self.assertGreater(score.human_score, 0.3)
        self.assertLess(score.human_score, 0.9)


if __name__ == '__main__':
    unittest.main()
