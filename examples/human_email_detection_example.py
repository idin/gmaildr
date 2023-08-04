"""
Example: Human Email Detection

This example demonstrates how to use the human email detection system
to identify email addresses that belong to real humans.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gmailwiz import Gmail
from gmailwiz.analysis.human_email_detector import detect_human_emails, get_human_sender_summary


def main():
    """Demonstrate human email detection capabilities."""
    
    print("🔍 Human Email Detection Example")
    print("=" * 50)
    
    # Initialize Gmail connection
    print("📧 Connecting to Gmail...")
    gmail = Gmail()
    
    # Get emails from the last 30 days with text content
    print("📥 Retrieving emails from the last 30 days...")
    emails_df = gmail.get_emails(
        days=30,
        include_text=True,
        include_metrics=True,
        use_batch=True
    )
    
    if emails_df.empty:
        print("❌ No emails found in the specified time range.")
        return
    
    print(f"✅ Retrieved {len(emails_df)} emails from {emails_df['sender_email'].nunique()} senders")
    
    # Detect human emails
    print("\n🔍 Analyzing emails for human senders...")
    human_emails_df = detect_human_emails(
        emails_df=emails_df,
        human_threshold=0.6,  # Adjust this threshold as needed
        show_progress=True
    )
    
    # Get summary statistics
    print("\n📊 Human vs Automated Sender Summary:")
    summary_df = get_human_sender_summary(human_emails_df)
    print(summary_df.to_string(index=False))
    
    # Show top human senders
    print("\n👥 Top Human Senders:")
    human_senders = human_emails_df[human_emails_df['is_human_sender'] == True]
    if not human_senders.empty:
        top_human_senders = human_senders.groupby('sender_email').agg({
            'human_score': 'mean',
            'sender_name': 'first',
            'subject': 'count'
        }).reset_index().rename(columns={'subject': 'email_count'}).sort_values('human_score', ascending=False)
        
        print(top_human_senders.head(10).to_string())
    
    # Show top automated senders
    print("\n🤖 Top Automated Senders:")
    automated_senders = human_emails_df[human_emails_df['is_human_sender'] == False]
    if not automated_senders.empty:
        top_automated_senders = automated_senders.groupby('sender_email').agg({
            'human_score': 'mean',
            'sender_name': 'first',
            'subject': 'count'
        }).reset_index().rename(columns={'subject': 'email_count'}).sort_values('human_score', ascending=True)
        
        print(top_automated_senders.head(10).to_string())
    
    # Show detailed analysis for a specific sender
    print("\n🔍 Detailed Analysis Example:")
    if not human_emails_df.empty:
        # Get a sender with multiple emails for detailed analysis
        sender_counts = human_emails_df['sender_email'].value_counts()
        if len(sender_counts) > 0:
            sample_sender = sender_counts.index[0]
            sender_emails = human_emails_df[human_emails_df['sender_email'] == sample_sender]
            
            print(f"📧 Analyzing sender: {sample_sender}")
            print(f"   Human Score: {sender_emails['human_score'].iloc[0]:.3f}")
            print(f"   Content Score: {sender_emails['content_score'].iloc[0]:.3f}")
            print(f"   Sender Score: {sender_emails['sender_score'].iloc[0]:.3f}")
            print(f"   Is Human: {sender_emails['is_human_sender'].iloc[0]}")
            print(f"   Email Count: {len(sender_emails)}")
            
            # Show human indicators
            human_indicators = [col for col in sender_emails.columns if col.startswith('human_')]
            print("   Human Indicators:")
            for indicator in human_indicators:
                if sender_emails[indicator].iloc[0]:
                    indicator_name = indicator.replace('human_', '').replace('_', ' ').title()
                    print(f"     ✅ {indicator_name}")
    
    # Export results
    print("\n💾 Exporting results...")
    output_file = "human_email_detection_results.csv"
    human_emails_df.to_csv(output_file, index=False)
    print(f"✅ Results saved to: {output_file}")
    
    # Show usage recommendations
    print("\n💡 Usage Recommendations:")
    print("   • Adjust human_threshold (0.6 default) based on your needs")
    print("   • Higher threshold = more strict human detection")
    print("   • Lower threshold = more lenient human detection")
    print("   • Use results to filter out automated emails")
    print("   • Combine with other filters for targeted email management")


if __name__ == "__main__":
    main()
