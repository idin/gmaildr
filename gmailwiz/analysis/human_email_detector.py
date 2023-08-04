"""
Human Email Detection Module.

This module provides advanced analysis capabilities to identify email addresses
that belong to real humans based on email patterns, content analysis, and
sender behaviour.
"""

import re
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import pandas as pd
import numpy as np

from .email_metrics import EmailContentAnalyzer

logger = logging.getLogger(__name__)


@dataclass
class HumanEmailScore:
    """Container for human email detection scores and indicators."""
    
    # Overall score (0.0 to 1.0, higher = more likely human)
    human_score: float = 0.0
    
    # Individual component scores
    content_score: float = 0.0
    sender_score: float = 0.0
    behavioural_score: float = 0.0
    conversation_score: float = 0.0
    
    # Detailed indicators
    has_personal_greeting: bool = False
    has_conversational_tone: bool = False
    has_questions: bool = False
    has_personal_details: bool = False
    has_emotional_content: bool = False
    has_typos_or_informal_language: bool = False
    has_attachments: bool = False
    has_signature: bool = False
    
    # Sender characteristics
    has_real_name: bool = False
    has_personal_domain: bool = False
    has_consistent_sender_name: bool = False
    
    # Behavioural patterns
    sends_replies: bool = False
    receives_replies: bool = False
    has_conversation_threads: bool = False
    sends_at_irregular_times: bool = False
    has_variable_subject_length: bool = False
    
    # Negative indicators (reduce human score)
    has_unsubscribe_link: bool = False
    has_marketing_language: bool = False
    has_legal_disclaimer: bool = False
    has_bulk_email_indicators: bool = False
    has_tracking_pixels: bool = False
    has_promotional_content: bool = False


class HumanEmailDetector:
    """
    Advanced detector for identifying human email addresses.
    
    This class analyzes multiple aspects of emails to determine if they
    were sent by real humans rather than automated systems.
    """
    
    # Patterns indicating human communication
    PERSONAL_GREETING_PATTERNS = [
        r'\b(hi|hello|hey|dear|good morning|good afternoon|good evening)\b',
        r'\b(thanks|thank you|cheers|best regards|sincerely)\b',
        r'\b(how are you|hope you\'re well|hope this finds you well)\b'
    ]
    
    CONVERSATIONAL_PATTERNS = [
        r'\b(i think|i believe|i feel|in my opinion)\b',
        r'\b(by the way|btw|also|additionally)\b',
        r'\b(let me know|please let me know|get back to me)\b',
        r'\b(sounds good|that works|perfect|great)\b'
    ]
    
    QUESTION_PATTERNS = [
        r'\?',  # Question marks
        r'\b(what|when|where|who|why|how)\b',
        r'\b(can you|could you|would you|will you)\b',
        r'\b(do you|does it|is it|are you)\b'
    ]
    
    PERSONAL_DETAILS_PATTERNS = [
        r'\b(my|mine|i\'m|i am|i\'ve|i have)\b',
        r'\b(family|kids|children|wife|husband|partner)\b',
        r'\b(weekend|vacation|holiday|birthday|anniversary)\b',
        r'\b(work|job|office|meeting|project)\b'
    ]
    
    EMOTIONAL_CONTENT_PATTERNS = [
        r'\b(happy|excited|thrilled|delighted|pleased)\b',
        r'\b(sorry|apologize|regret|disappointed|frustrated)\b',
        r'\b(worried|concerned|anxious|nervous|stressed)\b',
        r'\b(love|hate|like|dislike|enjoy)\b'
    ]
    
    INFORMAL_LANGUAGE_PATTERNS = [
        r'\b(yeah|yep|nope|gonna|wanna|gotta)\b',
        r'\b(awesome|cool|great|nice|sweet|amazing)\b',
        r'\b(btw|fyi|imo|tbh|omg|lol)\b',
        r'\b(ok|okay|sure|fine|whatever)\b'
    ]
    
    SIGNATURE_PATTERNS = [
        r'\b(best regards|sincerely|yours truly|cheers)\b',
        r'\b(thanks|thank you|regards|best)\b',
        r'--\s*\n',  # Signature separator
        r'phone:|mobile:|cell:|fax:',
        r'www\.|http://|https://'  # Website links
    ]
    
    PERSONAL_DOMAIN_PATTERNS = [
        r'@gmail\.com$',
        r'@yahoo\.com$',
        r'@hotmail\.com$',
        r'@outlook\.com$',
        r'@icloud\.com$',
        r'@aol\.com$'
    ]
    
    def __init__(self):
        """Initialize the human email detector with compiled patterns."""
        self.content_analyzer = EmailContentAnalyzer()
        
        # Compile regex patterns
        self.personal_greeting_regex = re.compile('|'.join(self.PERSONAL_GREETING_PATTERNS), re.IGNORECASE)
        self.conversational_regex = re.compile('|'.join(self.CONVERSATIONAL_PATTERNS), re.IGNORECASE)
        self.question_regex = re.compile('|'.join(self.QUESTION_PATTERNS), re.IGNORECASE)
        self.personal_details_regex = re.compile('|'.join(self.PERSONAL_DETAILS_PATTERNS), re.IGNORECASE)
        self.emotional_regex = re.compile('|'.join(self.EMOTIONAL_CONTENT_PATTERNS), re.IGNORECASE)
        self.informal_regex = re.compile('|'.join(self.INFORMAL_LANGUAGE_PATTERNS), re.IGNORECASE)
        self.signature_regex = re.compile('|'.join(self.SIGNATURE_PATTERNS), re.IGNORECASE)
        self.personal_domain_regex = re.compile('|'.join(self.PERSONAL_DOMAIN_PATTERNS), re.IGNORECASE)
    
    def analyze_single_email(
        self,
        *,
        text_content: Optional[str] = None,
        html_content: Optional[str] = None,
        subject: Optional[str] = None,
        sender_email: Optional[str] = None,
        sender_name: Optional[str] = None,
        has_attachments: bool = False,
        thread_id: Optional[str] = None
    ) -> HumanEmailScore:
        """
        Analyze a single email to determine if it's from a human.
        
        Args:
            text_content: Plain text content of the email.
            html_content: HTML content of the email.
            subject: Email subject line.
            sender_email: Sender's email address.
            sender_name: Sender's display name.
            has_attachments: Whether the email has attachments.
            thread_id: Gmail thread ID for conversation analysis.
            
        Returns:
            HumanEmailScore: Comprehensive human email detection score.
        """
        score = HumanEmailScore()
        
        # Combine all available text for analysis
        combined_text = self._combine_text(
            text_content=text_content,
            html_content=html_content,
            subject=subject
        )
        
        if not combined_text:
            return score
        
        # Analyze content indicators
        score.has_personal_greeting = bool(self.personal_greeting_regex.search(combined_text))
        score.has_conversational_tone = bool(self.conversational_regex.search(combined_text))
        score.has_questions = bool(self.question_regex.search(combined_text))
        score.has_personal_details = bool(self.personal_details_regex.search(combined_text))
        score.has_emotional_content = bool(self.emotional_regex.search(combined_text))
        score.has_typos_or_informal_language = bool(self.informal_regex.search(combined_text))
        score.has_signature = bool(self.signature_regex.search(combined_text))
        score.has_attachments = has_attachments
        
        # Analyze sender characteristics
        score.has_real_name = bool(sender_name and len(sender_name.strip()) > 0)
        score.has_personal_domain = bool(sender_email and self.personal_domain_regex.search(sender_email))
        score.has_consistent_sender_name = bool(sender_name and ' ' in sender_name)
        
        # Get automated email indicators (negative factors)
        automated_metrics = self.content_analyzer.analyze_email_content(
            text_content=text_content,
            html_content=html_content,
            subject=subject
        )
        
        score.has_unsubscribe_link = automated_metrics.has_unsubscribe_link
        score.has_marketing_language = automated_metrics.has_marketing_language
        score.has_legal_disclaimer = automated_metrics.has_legal_disclaimer
        score.has_bulk_email_indicators = automated_metrics.has_bulk_email_indicators
        score.has_tracking_pixels = automated_metrics.has_tracking_pixels
        score.has_promotional_content = automated_metrics.has_promotional_content
        
        # Calculate component scores
        score.content_score = self._calculate_content_score(score)
        score.sender_score = self._calculate_sender_score(score)
        score.behavioural_score = self._calculate_behavioural_score(score)
        score.conversation_score = self._calculate_conversation_score(score, thread_id)
        
        # Calculate overall human score
        score.human_score = self._calculate_overall_score(score)
        
        return score
    
    def analyze_sender_emails(
        self,
        emails_df: pd.DataFrame,
        *,
        sender_email: str,
        text_column: str = 'text_content',
        subject_column: str = 'subject',
        sender_name_column: str = 'sender_name',
        thread_id_column: str = 'thread_id'
    ) -> HumanEmailScore:
        """
        Analyze all emails from a specific sender to determine if they're human.
        
        Args:
            emails_df: DataFrame containing email data.
            sender_email: Email address of the sender to analyze.
            text_column: Name of column containing email text.
            subject_column: Name of column containing subjects.
            sender_name_column: Name of column containing sender names.
            thread_id_column: Name of column containing thread IDs.
            
        Returns:
            HumanEmailScore: Aggregated human email detection score.
        """
        # Filter emails from this sender
        sender_emails = emails_df[emails_df['sender_email'] == sender_email].copy()
        
        if sender_emails.empty:
            return HumanEmailScore()
        
        # Analyze each email
        individual_scores = []
        for _, email in sender_emails.iterrows():
            score = self.analyze_single_email(
                text_content=email.get(text_column),
                subject=email.get(subject_column),
                sender_email=email.get('sender_email'),
                sender_name=email.get(sender_name_column),
                has_attachments=email.get('has_attachments', False),
                thread_id=email.get(thread_id_column)
            )
            individual_scores.append(score)
        
        # Aggregate scores
        return self._aggregate_sender_scores(individual_scores, sender_emails)
    
    def _combine_text(
        self,
        *,
        text_content: Optional[str] = None,
        html_content: Optional[str] = None,
        subject: Optional[str] = None
    ) -> str:
        """Combine all available text for analysis."""
        parts = []
        
        if subject:
            parts.append(subject)
        
        if text_content:
            parts.append(text_content)
        
        if html_content:
            # Extract text from HTML
            import re
            html_text = re.sub(r'<[^>]+>', ' ', html_content)
            parts.append(html_text)
        
        return ' '.join(parts)
    
    def _calculate_content_score(self, score: HumanEmailScore) -> float:
        """Calculate content-based human score."""
        positive_indicators = sum([
            score.has_personal_greeting,
            score.has_conversational_tone,
            score.has_questions,
            score.has_personal_details,
            score.has_emotional_content,
            score.has_typos_or_informal_language,
            score.has_signature
        ])
        
        negative_indicators = sum([
            score.has_unsubscribe_link,
            score.has_marketing_language,
            score.has_legal_disclaimer,
            score.has_bulk_email_indicators,
            score.has_tracking_pixels,
            score.has_promotional_content
        ])
        
        # Normalize to 0-1 range
        total_indicators = 7  # Number of positive indicators
        content_score = (positive_indicators - negative_indicators) / total_indicators
        return max(0.0, min(1.0, content_score))
    
    def _calculate_sender_score(self, score: HumanEmailScore) -> float:
        """Calculate sender-based human score."""
        positive_indicators = sum([
            score.has_real_name,
            score.has_personal_domain,
            score.has_consistent_sender_name
        ])
        
        return positive_indicators / 3.0
    
    def _calculate_behavioural_score(self, score: HumanEmailScore) -> float:
        """Calculate behavioural-based human score."""
        # This would be enhanced with actual behavioural data
        # For now, use attachment presence as a behavioural indicator
        return 0.5 if score.has_attachments else 0.0
    
    def _calculate_conversation_score(self, score: HumanEmailScore, thread_id: Optional[str]) -> float:
        """Calculate conversation-based human score."""
        # This would be enhanced with thread analysis
        # For now, use basic indicators
        return 0.5 if score.has_questions or score.has_conversational_tone else 0.0
    
    def _calculate_overall_score(self, score: HumanEmailScore) -> float:
        """Calculate overall human email score."""
        # Weighted combination of component scores
        weights = {
            'content': 0.4,
            'sender': 0.2,
            'behavioural': 0.2,
            'conversation': 0.2
        }
        
        overall_score = (
            score.content_score * weights['content'] +
            score.sender_score * weights['sender'] +
            score.behavioural_score * weights['behavioural'] +
            score.conversation_score * weights['conversation']
        )
        
        return max(0.0, min(1.0, overall_score))
    
    def _aggregate_sender_scores(
        self,
        individual_scores: List[HumanEmailScore],
        sender_emails: pd.DataFrame
    ) -> HumanEmailScore:
        """Aggregate individual email scores into a sender-level score."""
        if not individual_scores:
            return HumanEmailScore()
        
        # Calculate average scores
        avg_human_score = np.mean([s.human_score for s in individual_scores])
        avg_content_score = np.mean([s.content_score for s in individual_scores])
        avg_sender_score = np.mean([s.sender_score for s in individual_scores])
        avg_behavioural_score = np.mean([s.behavioural_score for s in individual_scores])
        avg_conversation_score = np.mean([s.conversation_score for s in individual_scores])
        
        # Create aggregated score
        aggregated = HumanEmailScore(
            human_score=avg_human_score,
            content_score=avg_content_score,
            sender_score=avg_sender_score,
            behavioural_score=avg_behavioural_score,
            conversation_score=avg_conversation_score
        )
        
        # Set boolean indicators based on majority
        total_emails = len(individual_scores)
        threshold = total_emails / 2
        
        aggregated.has_personal_greeting = sum(s.has_personal_greeting for s in individual_scores) > threshold
        aggregated.has_conversational_tone = sum(s.has_conversational_tone for s in individual_scores) > threshold
        aggregated.has_questions = sum(s.has_questions for s in individual_scores) > threshold
        aggregated.has_personal_details = sum(s.has_personal_details for s in individual_scores) > threshold
        aggregated.has_emotional_content = sum(s.has_emotional_content for s in individual_scores) > threshold
        aggregated.has_typos_or_informal_language = sum(s.has_typos_or_informal_language for s in individual_scores) > threshold
        aggregated.has_signature = sum(s.has_signature for s in individual_scores) > threshold
        aggregated.has_attachments = sum(s.has_attachments for s in individual_scores) > threshold
        
        # Sender characteristics (should be consistent)
        first_score = individual_scores[0]
        aggregated.has_real_name = first_score.has_real_name
        aggregated.has_personal_domain = first_score.has_personal_domain
        aggregated.has_consistent_sender_name = first_score.has_consistent_sender_name
        
        # Negative indicators (any presence is concerning)
        aggregated.has_unsubscribe_link = any(s.has_unsubscribe_link for s in individual_scores)
        aggregated.has_marketing_language = any(s.has_marketing_language for s in individual_scores)
        aggregated.has_legal_disclaimer = any(s.has_legal_disclaimer for s in individual_scores)
        aggregated.has_bulk_email_indicators = any(s.has_bulk_email_indicators for s in individual_scores)
        aggregated.has_tracking_pixels = any(s.has_tracking_pixels for s in individual_scores)
        aggregated.has_promotional_content = any(s.has_promotional_content for s in individual_scores)
        
        return aggregated


def detect_human_emails(
    emails_df: pd.DataFrame,
    *,
    text_column: str = 'text_content',
    subject_column: str = 'subject',
    sender_name_column: str = 'sender_name',
    thread_id_column: str = 'thread_id',
    human_threshold: float = 0.6,
    show_progress: bool = True
) -> pd.DataFrame:
    """
    Detect human email addresses from a DataFrame of emails.
    
    Args:
        emails_df: DataFrame containing email data.
        text_column: Name of column containing email text.
        subject_column: Name of column containing subjects.
        sender_name_column: Name of column containing sender names.
        thread_id_column: Name of column containing thread IDs.
        human_threshold: Minimum score to classify as human.
        show_progress: Whether to show progress bar.
        
    Returns:
        pd.DataFrame: DataFrame with human email detection results.
    """
    detector = HumanEmailDetector()
    
    if show_progress:
        print("🔍 Analyzing emails for human senders...")
    
    # Handle empty DataFrame
    if emails_df.empty:
        return emails_df.copy()
    
    # Check if required column exists
    if 'sender_email' not in emails_df.columns:
        raise ValueError("DataFrame must contain 'sender_email' column")
    
    # Get unique senders
    unique_senders = emails_df['sender_email'].unique()
    
    # Analyze each sender
    sender_scores = {}
    for sender_email in unique_senders:
        score = detector.analyze_sender_emails(
            emails_df=emails_df,
            sender_email=sender_email,
            text_column=text_column,
            subject_column=subject_column,
            sender_name_column=sender_name_column,
            thread_id_column=thread_id_column
        )
        sender_scores[sender_email] = score
    
    # Add human detection results to DataFrame
    result_df = emails_df.copy()
    
    # Add human score columns
    result_df['human_score'] = result_df['sender_email'].map(
        lambda x: sender_scores.get(x, HumanEmailScore()).human_score
    )
    result_df['is_human_sender'] = result_df['human_score'] >= human_threshold
    result_df['content_score'] = result_df['sender_email'].map(
        lambda x: sender_scores.get(x, HumanEmailScore()).content_score
    )
    result_df['sender_score'] = result_df['sender_email'].map(
        lambda x: sender_scores.get(x, HumanEmailScore()).sender_score
    )
    
    # Add detailed indicators
    for indicator in ['has_personal_greeting', 'has_conversational_tone', 'has_questions',
                     'has_personal_details', 'has_emotional_content', 'has_signature']:
        result_df[f'human_{indicator}'] = result_df['sender_email'].map(
            lambda x: getattr(sender_scores.get(x, HumanEmailScore()), indicator, False)
        )
    
    if show_progress:
        human_count = result_df['is_human_sender'].sum()
        total_senders = len(unique_senders)
        print(f"✅ Found {human_count} human senders out of {total_senders} total senders")
    
    return result_df


def get_human_sender_summary(
    emails_df: pd.DataFrame,
    *,
    human_threshold: float = 0.6
) -> pd.DataFrame:
    """
    Get a summary of human vs automated senders.
    
    Args:
        emails_df: DataFrame with human detection results.
        human_threshold: Threshold used for human classification.
        
    Returns:
        pd.DataFrame: Summary statistics for human and automated senders.
    """
    if 'is_human_sender' not in emails_df.columns:
        raise ValueError("DataFrame must have human detection results. Run detect_human_emails() first.")
    
    # Group by sender type
    human_senders = emails_df[emails_df['is_human_sender'] == True]
    automated_senders = emails_df[emails_df['is_human_sender'] == False]
    
    # Calculate summary statistics
    summary_data = []
    
    # Human senders summary
    if not human_senders.empty:
        human_summary = {
            'sender_type': 'human',
            'sender_count': human_senders['sender_email'].nunique(),
            'email_count': len(human_senders),
            'avg_human_score': human_senders['human_score'].mean(),
            'avg_content_score': human_senders['content_score'].mean(),
            'avg_sender_score': human_senders['sender_score'].mean(),
            'total_size_bytes': human_senders['size_bytes'].sum(),
            'avg_email_size': human_senders['size_bytes'].mean(),
            'read_percentage': (human_senders['is_read'].sum() / len(human_senders)) * 100
        }
        summary_data.append(human_summary)
    
    # Automated senders summary
    if not automated_senders.empty:
        automated_summary = {
            'sender_type': 'automated',
            'sender_count': automated_senders['sender_email'].nunique(),
            'email_count': len(automated_senders),
            'avg_human_score': automated_senders['human_score'].mean(),
            'avg_content_score': automated_senders['content_score'].mean(),
            'avg_sender_score': automated_senders['sender_score'].mean(),
            'total_size_bytes': automated_senders['size_bytes'].sum(),
            'avg_email_size': automated_senders['size_bytes'].mean(),
            'read_percentage': (automated_senders['is_read'].sum() / len(automated_senders)) * 100
        }
        summary_data.append(automated_summary)
    
    return pd.DataFrame(summary_data)
