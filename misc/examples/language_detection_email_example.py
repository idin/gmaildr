"""
Language Detection in Email Processing Example.

This example demonstrates how language detection is automatically
added to emails during the processing pipeline.
"""

from gmaildr import Gmail
from gmaildr.core.email_message import EmailMessage
from datetime import datetime


def main():
    """Demonstrate language detection in email processing."""
    print("🌍 Language Detection in Email Processing")
    print("=" * 50)
    
    gmail = Gmail()
    
    # Create test emails in different languages and types
    test_emails = [
        EmailMessage(
            message_id="test1",
            sender_email="john@example.com",
            sender_name="John Smith",
            subject="Meeting tomorrow at 2 PM",
            timestamp=datetime.now(),
            sender_local_timestamp=datetime.now(),
            size_bytes=1024,
            text_content="Hi team, I wanted to remind everyone about our meeting tomorrow at 2 PM. Please bring your project updates."
        ),
        EmailMessage(
            message_id="test2",
            sender_email="maria@example.com",
            sender_name="María García",
            subject="Reunión mañana a las 2 PM",
            timestamp=datetime.now(),
            sender_local_timestamp=datetime.now(),
            size_bytes=1024,
            text_content="Hola equipo, quería recordarles sobre nuestra reunión mañana a las 2 PM. Por favor traigan sus actualizaciones del proyecto."
        ),
        EmailMessage(
            message_id="test3",
            sender_email="pierre@example.com",
            sender_name="Pierre Dubois",
            subject="Réunion demain à 14h",
            timestamp=datetime.now(),
            sender_local_timestamp=datetime.now(),
            size_bytes=1024,
            text_content="Bonjour équipe, je voulais vous rappeler notre réunion demain à 14h. Veuillez apporter vos mises à jour du projet."
        ),
        EmailMessage(
            message_id="test4",
            sender_email="support@company.com",
            sender_name="Support Team",
            subject="Ticket #12345 - Issue Resolved",
            timestamp=datetime.now(),
            sender_local_timestamp=datetime.now(),
            size_bytes=1024,
            text_content="Your support ticket has been resolved. Thank you for contacting us."
        ),
        EmailMessage(
            message_id="test5",
            sender_email="newsletter@marketing.com",
            sender_name="Marketing Newsletter",
            subject="Weekly Newsletter - Special Offers",
            timestamp=datetime.now(),
            sender_local_timestamp=datetime.now(),
            size_bytes=1024,
            text_content="Check out our latest offers and promotions. Limited time deals available!"
        )
    ]
    
    print("📧 Processing emails with language detection...")
    print("-" * 40)
    
    # Process emails with language detection
    processed_emails = gmail._add_language_detection(emails=test_emails, include_text=True)
    
    # Display results
    for i, email in enumerate(processed_emails, 1):
        role_indicator = "🤖 ROLE-BASED" if email.has_role_based_email else "👤 PERSONAL"
        print(f"\n📬 Email {i}: {email.subject}")
        print(f"   From: {email.sender_name} <{email.sender_email}>")
        print(f"   Type: {role_indicator}")
        print(f"   Subject Language: {email.subject_language} (confidence: {email.subject_language_confidence:.2f})")
        print(f"   Text Language: {email.text_language} (confidence: {email.text_language_confidence:.2f})")
        print(f"   Text Preview: {email.text_content[:50]}...")
    
    print("\n" + "=" * 50)
    print("📊 Converting to DataFrame...")
    print("-" * 40)
    
    # Convert to DataFrame to see the language columns
    df = gmail._emails_to_dataframe(emails=processed_emails, include_text=True)
    
    print(f"DataFrame shape: {df.shape}")
    print(f"Language columns: {[col for col in df.columns if 'language' in col]}")
    
    # Show language detection summary
    print("\n📈 Language Detection Summary:")
    print("-" * 40)
    
    subject_languages = df['subject_language'].value_counts()
    text_languages = df['text_language'].value_counts()
    
    print("Subject Languages:")
    for lang, count in subject_languages.items():
        print(f"  {lang}: {count} emails")
    
    print("\nText Languages:")
    for lang, count in text_languages.items():
        print(f"  {lang}: {count} emails")
    
    # Show role-based email summary
    print("\n🤖 Role-Based Email Summary:")
    print("-" * 40)
    
    role_based_count = df['has_role_based_email'].sum()
    personal_count = len(df) - role_based_count
    
    print(f"Role-based emails: {role_based_count}")
    print(f"Personal emails: {personal_count}")
    print(f"Role-based percentage: {(role_based_count/len(df)*100):.1f}%")
    
    # Show average confidence scores
    print(f"\nAverage Subject Confidence: {df['subject_language_confidence'].mean():.2f}")
    print(f"Average Text Confidence: {df['text_language_confidence'].mean():.2f}")


if __name__ == "__main__":
    main()
