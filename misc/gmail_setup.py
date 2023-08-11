# ==========================================
# CELL 1: Setup and Import
# ==========================================

import os
from datetime import datetime, timedelta
from gmail_cleaner import GmailClient, EmailAnalyzer
from gmail_cleaner.config import ConfigManager, setup_logging

print("📦 Gmail Cleaner Setup Notebook")
print("=" * 40)

# Initialize configuration
config_manager = ConfigManager()
config = config_manager.get_config()
setup_logging(config)

print(f"✅ Configuration loaded")
print(f"📁 Working directory: {os.getcwd()}")


# ==========================================
# CELL 2: Check Requirements
# ==========================================

print("\n🔍 Checking requirements...")

# Check credentials file
credentials_exists = os.path.exists(config.credentials_file)
print(f"🔐 Credentials file: {'✅' if credentials_exists else '❌'} {config.credentials_file}")

# Check token file (created after first auth)
token_exists = os.path.exists(config.token_file)
print(f"🎫 Auth token: {'✅' if token_exists else '⚠️  Will be created on first auth'}")

# Check output directory
output_exists = os.path.exists(config.output_directory)
print(f"📁 Output directory: {'✅' if output_exists else '⚠️  Will be created'}")

if not credentials_exists:
    print("""
    ❌ Missing credentials.json file!
    
    To fix this:
    1. Go to Google Cloud Console
    2. Enable Gmail API
    3. Create OAuth2 credentials (Desktop app)
    4. Download as 'credentials.json'
    5. Place in this directory
    """)
else:
    print("✅ All requirements met!")


# ==========================================
# CELL 3: Initialize Gmail Client
# ==========================================

print("\n🔑 Initializing Gmail client...")

try:
    # Initialize Gmail client
    gmail_client = GmailClient(
        credentials_file=config.credentials_file,
        token_file=config.token_file
    )
    
    print("✅ Gmail client initialized")
    
    # Test authentication
    print("🔐 Testing authentication...")
    
    if gmail_client.authenticate():
        print("✅ Authentication successful!")
        
        # Get user profile
        profile = gmail_client.get_user_profile()
        if profile:
            email = profile.get('emailAddress', 'Unknown')
            total_messages = profile.get('messagesTotal', 'Unknown')
            print(f"📧 Connected to: {email}")
            print(f"📊 Total messages in account: {total_messages:,}" if isinstance(total_messages, int) else f"📊 Total messages: {total_messages}")
        
        # Test basic search
        print("\n🔍 Testing email search...")
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        message_ids = gmail_client.get_emails_from_date_range(
            start_date=start_date,
            end_date=end_date,
            max_results=10
        )
        
        print(f"✅ Found {len(message_ids)} emails in last 30 days")
        
        if message_ids:
            # Test getting email details
            first_email = gmail_client.get_message_details(message_ids[0])
            if first_email:
                print(f"✅ Email details retrieval working")
                print(f"   Sample: {first_email.sender_email} - {first_email.subject[:50]}...")
            else:
                print("⚠️  Could not retrieve email details")
        else:
            print("ℹ️  No recent emails found (this might be normal)")
        
    else:
        print("❌ Authentication failed!")
        gmail_client = None

except Exception as error:
    print(f"❌ Error: {error}")
    gmail_client = None


# ==========================================
# CELL 4: Initialize Email Analyzer
# ==========================================

if gmail_client:
    print("\n📊 Initializing Email Analyzer...")
    
    try:
        # Create analyzer
        analyzer = EmailAnalyzer(gmail_client)
        print("✅ Email analyzer ready!")
        
        # Set up some common date ranges for analysis
        today = datetime.now()
        date_ranges = {
            "last_week": (today - timedelta(days=7), today),
            "last_month": (today - timedelta(days=30), today),
            "last_3_months": (today - timedelta(days=90), today),
            "last_6_months": (today - timedelta(days=180), today),
            "last_year": (today - timedelta(days=365), today),
        }
        
        print("\n📅 Available date ranges for analysis:")
        for name, (start, end) in date_ranges.items():
            print(f"   {name}: {start.date()} to {end.date()}")
        
    except Exception as error:
        print(f"❌ Analyzer initialization error: {error}")
        analyzer = None
else:
    analyzer = None
    print("\n❌ Cannot initialize analyzer without Gmail client")


# ==========================================
# CELL 5: Quick Analysis Function
# ==========================================

def quick_analysis(days=30, max_emails=500):
    """
    Run a quick Gmail analysis.
    
    Args:
        days (int): Number of days to analyze
        max_emails (int): Maximum emails to process
    """
    if not analyzer:
        print("❌ Analyzer not available. Please fix authentication first.")
        return None
    
    print(f"\n🚀 Running quick analysis...")
    print(f"📅 Date range: Last {days} days")
    print(f"📧 Max emails: {max_emails}")
    
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Run analysis
        report = analyzer.analyze_emails_from_date_range(
            start_date=start_date,
            end_date=end_date,
            max_emails=max_emails,
            batch_size=50
        )
        
        # Display quick summary
        print(f"\n✅ Analysis complete!")
        print(f"📊 Emails analyzed: {report.total_emails_analyzed:,}")
        print(f"👥 Unique senders: {len(report.sender_statistics)}")
        print(f"💾 Total storage: {report.total_storage_used_bytes / (1024**2):.1f} MB")
        
        if report.sender_statistics:
            print(f"\n🏆 Top 3 senders by email count:")
            for i, sender in enumerate(report.get_top_senders_by_count(3), 1):
                print(f"   {i}. {sender.sender_email}: {sender.total_emails} emails")
        
        return report
        
    except Exception as error:
        print(f"❌ Analysis failed: {error}")
        return None

# Example usage
print(f"\n💡 To run a quick analysis, use:")
print(f"   report = quick_analysis(days=30, max_emails=200)")


# ==========================================
# CELL 6: Ready for Your Tasks!
# ==========================================

print(f"\n🎉 Gmail Cleaner Setup Complete!")
print(f"=" * 40)

if gmail_client and analyzer:
    print(f"✅ Gmail client: Ready")
    print(f"✅ Email analyzer: Ready")
    print(f"✅ Configuration: Loaded")
    
    print(f"\n🚀 Available tools:")
    print(f"   • gmail_client - for direct Gmail API access")
    print(f"   • analyzer - for email analysis")
    print(f"   • quick_analysis() - for fast analysis")
    print(f"   • config_manager - for settings")
    
    print(f"\n📖 Example commands:")
    print(f"   # Quick analysis")
    print(f"   report = quick_analysis(days=90, max_emails=1000)")
    print(f"   ")
    print(f"   # Export to DataFrame")
    print(f"   df = analyzer.export_to_dataframe()")
    print(f"   ")
    print(f"   # Get storage analysis")
    print(f"   storage = analyzer.get_storage_analysis()")
    print(f"   ")
    print(f"   # Get temporal analysis")
    print(f"   temporal = analyzer.get_temporal_analysis()")
    
    print(f"\n🎯 Ready for your Gmail analysis tasks!")
    
else:
    print(f"❌ Setup incomplete. Please fix the issues above.")
    if not gmail_client:
        print(f"   • Gmail authentication failed")
    if not analyzer:
        print(f"   • Email analyzer not available")
    
    print(f"\n🔧 Next steps:")
    print(f"   1. Enable Gmail API in Google Cloud Console")
    print(f"   2. Ensure credentials.json is valid")
    print(f"   3. Add yourself as test user in OAuth consent screen")
    print(f"   4. Re-run this notebook")


print(f"\n" + "="*50)
print(f"📝 Gmail Cleaner Setup Notebook Complete")
print(f"🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"="*50)
