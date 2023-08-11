"""
Debug test to understand why image detection is failing.
"""

import re
from gmaildr import Gmail


def test_debug_image_detection():
    """Debug why image detection is returning all zeros."""
    
    gmail = Gmail()
    
    # Get emails with text content
    df = gmail.get_emails(
        days=1, 
        use_batch=True, 
        include_text=True, 
        include_metrics=False
    )
    
    if df.empty:
        print("⚠️  No emails found")
        return
    
    print(f"📧 Found {len(df)} emails")
    
    # Check first few emails for image content
    for i in range(min(3, len(df))):
        email = df.iloc[i]
        text_content = email.get('text_content', '')
        subject = email.get('subject', '')
        
        print(f"\n📬 Email {i+1}: {subject}")
        print(f"   Text length: {len(text_content)}")
        
        # Look for image patterns manually
        img_patterns = [
            r'<img[^>]*>',
            r'background.*image.*url',
            r'background.*url',
            r'<svg[^>]*>',
            r'<canvas[^>]*>',
            r'data.*image',
            r'base64.*image'
        ]
        
        found_images = []
        for pattern in img_patterns:
            matches = re.findall(pattern, text_content, re.IGNORECASE)
            if matches:
                found_images.append(f"{pattern}: {len(matches)} matches")
                print(f"   Found: {pattern}")
                print(f"   Matches: {matches[:2]}...")  # Show first 2 matches
        
        if not found_images:
            print("   No image patterns found")
            
        # Show first 200 chars of content
        print(f"   Content preview: {text_content[:200]}...")


def test_debug_unsubscribe_detection():
    """Debug why unsubscribe detection is failing."""
    
    gmail = Gmail()
    
    df = gmail.get_emails(
        days=1, 
        use_batch=True, 
        include_text=True, 
        include_metrics=False
    )
    
    if df.empty:
        print("⚠️  No emails found")
        return
    
    print(f"📧 Found {len(df)} emails")
    
    # Check for unsubscribe patterns
    unsubscribe_patterns = [
        r'unsubscribe',
        r'opt.?out',
        r'remove.*list',
        r'stop.*email',
        r'manage.*subscription',
        r'email.*preference'
    ]
    
    for i in range(min(3, len(df))):
        email = df.iloc[i]
        text_content = email.get('text_content', '')
        subject = email.get('subject', '')
        
        print(f"\n📬 Email {i+1}: {subject}")
        
        found_unsubscribe = []
        for pattern in unsubscribe_patterns:
            matches = re.findall(pattern, text_content, re.IGNORECASE)
            if matches:
                found_unsubscribe.append(f"{pattern}: {len(matches)} matches")
        
        if found_unsubscribe:
            print(f"   Found unsubscribe patterns: {found_unsubscribe}")
        else:
            print("   No unsubscribe patterns found")
            
        # Show first 200 chars of content
        print(f"   Content preview: {text_content[:200]}...")


def test_debug_message_structure():
    """Debug the actual message structure to understand why text_content is empty."""
    
    gmail = Gmail()
    
    # Get emails without text first to see the basic structure
    df = gmail.get_emails(
        days=1, 
        use_batch=True, 
        include_text=False, 
        include_metrics=False
    )
    
    if df.empty:
        print("⚠️  No emails found")
        return
    
    print(f"📧 Found {len(df)} emails")
    
    # Check first email structure
    first_email_id = df.iloc[0]['message_id']
    print(f"\n🔍 Examining email: {first_email_id}")
    
    # Get the raw message to see its structure
    try:
        message = gmail.client.service.users().messages().get(
            userId='me',
            id=first_email_id,
            format='full'
        ).execute()
        
        print(f"   Message size: {message.get('sizeEstimate', 'unknown')}")
        print(f"   Has payload: {'payload' in message}")
        
        payload = message.get('payload', {})
        print(f"   MIME type: {payload.get('mimeType', 'unknown')}")
        print(f"   Has parts: {'parts' in payload}")
        
        if 'parts' in payload:
            print(f"   Number of parts: {len(payload['parts'])}")
            for i, part in enumerate(payload['parts']):
                print(f"     Part {i}: {part.get('mimeType', 'unknown')}")
                if part.get('body', {}).get('data'):
                    print(f"       Has data: Yes")
                else:
                    print(f"       Has data: No")
        
        # Try to extract text manually
        from gmaildr.core.gmail import Gmail as GmailClass
        extracted_text = GmailClass._extract_email_text(message)
        print(f"   Extracted text length: {len(extracted_text)}")
        print(f"   Text preview: {extracted_text[:200]}...")
        
    except Exception as e:
        print(f"   Error examining message: {e}")


def test_debug_text_content_addition():
    """Debug whether text content is being properly added to email objects."""
    
    gmail = Gmail()
    
    # Get emails with text content
    df = gmail.get_emails(
        days=1, 
        use_batch=True, 
        include_text=True, 
        include_metrics=False
    )
    
    if df.empty:
        print("⚠️  No emails found")
        return
    
    print(f"📧 Found {len(df)} emails")
    
    # Check if text_content column exists
    if 'text_content' not in df.columns:
        print("❌ text_content column not found in DataFrame")
        return
    
    print(f"✅ text_content column found")
    
    # Check first few emails
    for i in range(min(3, len(df))):
        email = df.iloc[i]
        text_content = email.get('text_content', '')
        subject = email.get('subject', '')
        
        print(f"\n📬 Email {i+1}: {subject}")
        print(f"   Text content length: {len(text_content)}")
        print(f"   Text content type: {type(text_content)}")
        
        if text_content:
            print(f"   Text preview: {text_content[:200]}...")
            
            # Check for image patterns in the actual text
            img_patterns = [
                r'<img[^>]*>',
                r'background.*image.*url',
                r'background.*url',
                r'<svg[^>]*>',
                r'<canvas[^>]*>',
                r'data.*image',
                r'base64.*image'
            ]
            
            found_images = []
            for pattern in img_patterns:
                matches = re.findall(pattern, text_content, re.IGNORECASE)
                if matches:
                    found_images.append(f"{pattern}: {len(matches)} matches")
            
            if found_images:
                print(f"   Found image patterns: {found_images}")
            else:
                print("   No image patterns found in text content")
        else:
            print("   Text content is empty")


def test_debug_dataframe_columns():
    """Debug what columns are in the DataFrame and why text_content is missing."""
    
    gmail = Gmail()
    
    # Get emails with text content
    df = gmail.get_emails(
        days=1, 
        use_batch=True, 
        include_text=True, 
        include_metrics=False
    )
    
    if df.empty:
        print("⚠️  No emails found")
        return
    
    print(f"📧 Found {len(df)} emails")
    print(f"📊 DataFrame columns: {list(df.columns)}")
    
    # Check if text_content is in the columns
    if 'text_content' in df.columns:
        print("✅ text_content column found")
        text_lengths = df['text_content'].str.len()
        print(f"   Text content lengths: min={text_lengths.min()}, max={text_lengths.max()}")
    else:
        print("❌ text_content column not found")
        
        # Check if there are any other text-related columns
        text_columns = [col for col in df.columns if 'text' in col.lower()]
        if text_columns:
            print(f"   Other text columns found: {text_columns}")
        else:
            print("   No text-related columns found")
    
    # Show first few rows to see what's actually there
    print(f"\n📋 First row data:")
    first_row = df.iloc[0]
    for col in df.columns[:10]:  # Show first 10 columns
        value = first_row[col]
        if isinstance(value, str) and len(value) > 50:
            value = value[:50] + "..."
        print(f"   {col}: {value}")


if __name__ == "__main__":
    print("🔍 Debugging image and unsubscribe detection...")
    test_debug_image_detection()
    test_debug_unsubscribe_detection()
    print("🎉 Debug tests completed!")
