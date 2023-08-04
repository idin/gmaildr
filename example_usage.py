#!/usr/bin/env python3
"""
Example usage of GmailWiz package.

This script demonstrates how to use the GmailWiz package
to analyze your Gmail inbox programmatically.
"""

import os
from datetime import datetime, timedelta
from gmailwiz import GmailClient, EmailAnalyzer
from gmailwiz.config import ConfigManager, setup_logging


def main():
    """
    Example of using GmailWiz to analyze email data.
    
    This function demonstrates the basic workflow:
    1. Set up configuration
    2. Authenticate with Gmail
    3. Analyze emails from a date range
    4. Display and export results
    """
    # Initialize configuration
    config_manager = ConfigManager()
    config = config_manager.get_config()
    setup_logging(config)
    
    print("GmailWiz Example Usage")
    print("=" * 40)
    
    # Check if credentials file exists
    if not os.path.exists(config.credentials_file):
        print(f"Error: Credentials file not found: {config.credentials_file}")
        print("\nTo get your credentials file:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Create a new project or select an existing one")
        print("3. Enable the Gmail API")
        print("4. Create OAuth2 credentials (Desktop application)")
        print("5. Download the credentials JSON file")
        print(f"6. Save it as '{config.credentials_file}'")
        return
    
    try:
        # Initialize Gmail client
        print(f"\n1. Initializing Gmail client...")
        gmail_client = GmailClient(
            credentials_file=config.credentials_file,
            token_file=config.token_file
        )
        
        # Authenticate
        print("2. Authenticating with Gmail...")
        if not gmail_client.authenticate():
            print("Authentication failed!")
            return
        
        # Get user profile
        profile = gmail_client.get_user_profile()
        if profile:
            print(f"   Connected to: {profile.get('emailAddress')}")
            print(f"   Total messages: {profile.get('messagesTotal', 'Unknown')}")
        
        # Initialize analyzer
        print("\n3. Initializing email analyzer...")
        analyzer = EmailAnalyzer(gmail_client)
        
        # Define analysis period (last 7 days for example)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        print(f"4. Analyzing emails from {start_date.date()} to {end_date.date()}...")
        
        # Run analysis
        report = analyzer.analyze_emails_from_date_range(
            start_date=start_date,
            end_date=end_date,
            max_emails=100,  # Limit for example
            batch_size=50
        )
        
        # Display results
        print(f"\n5. Analysis Results:")
        print(f"   Total emails analyzed: {report.total_emails_analyzed:,}")
        print(f"   Unique senders: {len(report.sender_statistics)}")
        print(f"   Total storage: {report.total_storage_used_bytes / (1024**2):.1f} MB")
        
        # Top senders by count
        print(f"\n   Top 5 Senders by Email Count:")
        for i, sender in enumerate(report.get_top_senders_by_count(5), 1):
            print(f"   {i}. {sender.sender_email}: {sender.total_emails} emails")
        
        # Top senders by storage
        print(f"\n   Top 5 Senders by Storage Usage:")
        for i, sender in enumerate(report.get_top_senders_by_size(5), 1):
            storage_mb = sender.total_size_bytes / (1024**2)
            print(f"   {i}. {sender.sender_email}: {storage_mb:.1f} MB")
        
        # Get additional analysis
        print(f"\n6. Additional Analysis:")
        
        # Storage analysis
        storage_analysis = analyzer.get_storage_analysis()
        if storage_analysis:
            print(f"   Average email size: {storage_analysis.get('average_size_kb', 0):.1f} KB")
            if 'largest_emails' in storage_analysis:
                largest = storage_analysis['largest_emails'][0] if storage_analysis['largest_emails'] else None
                if largest:
                    largest_mb = largest['size_mb']
                    print(f"   Largest email: {largest_mb:.1f} MB from {largest['sender']}")
        
        # Temporal analysis
        temporal_analysis = analyzer.get_temporal_analysis()
        if temporal_analysis:
            busiest_hour = temporal_analysis.get('busiest_hour')
            if busiest_hour is not None:
                print(f"   Busiest hour: {busiest_hour}:00")
            
            busiest_day = temporal_analysis.get('busiest_day_of_week')
            if busiest_day:
                print(f"   Busiest day of week: {busiest_day}")
        
        # Export to DataFrame
        print(f"\n7. Exporting data...")
        df = analyzer.export_to_dataframe()
        if not df.empty:
            print(f"   Exported {len(df)} emails to DataFrame")
            print(f"   Columns: {', '.join(df.columns[:5])}...")
        
        # Save results
        output_file = config_manager.get_output_path("example_analysis.json")
        report.save_to_json(output_file)
        print(f"   Results saved to: {output_file}")
        
        print(f"\n✓ Analysis completed successfully!")
        
    except Exception as error:
        print(f"\nError during analysis: {error}")
        raise


if __name__ == "__main__":
    main()
